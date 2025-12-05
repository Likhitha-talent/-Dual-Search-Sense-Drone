from flask import Flask, request, jsonify
from collections import deque
from datetime import datetime
import csv
import os

app = Flask(__name__)

# Rolling GPS buffer (last 20 readings)
gps_buffer = deque(maxlen=20)
output_csv = 'integrated_events.csv'

# Ensure CSV exists
if not os.path.exists(output_csv):
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['event_file', 'event_type', 'timestamp', 'gps_lat', 'gps_lon', 'gps_alt'])

# Helper: find closest GPS reading to a timestamp
def closest_gps(event_time):
    closest = None
    min_diff = float('inf')
    for ts, gps in gps_buffer:
        diff = abs((event_time - ts).total_seconds())
        if diff < min_diff:
            min_diff = diff
            closest = gps
    return closest

@app.route('/gps', methods=['POST'])
def receive_gps():
    data = request.json
    # Expecting: {'timestamp': '2025-11-29T03:03:18', 'lat': .., 'lon': .., 'alt': ..}
    ts = datetime.fromisoformat(data['timestamp'])
    gps_buffer.append((ts, (data['lat'], data['lon'], data['alt'])))
    return jsonify({'status': 'ok'})

@app.route('/event', methods=['POST'])
def receive_event():
    data = request.json
    # Expecting: {'filename': 'captures/human.jpg', 'type': 'human', 'timestamp': '2025-11-29T03:03:18'}
    event_time = datetime.fromisoformat(data['timestamp'])
    gps = closest_gps(event_time)
    with open(output_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([data['filename'], data['type'], data['timestamp'],
                         gps[0] if gps else '', gps[1] if gps else '', gps[2] if gps else ''])
    return jsonify({'status': 'ok', 'gps_attached': gps})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
