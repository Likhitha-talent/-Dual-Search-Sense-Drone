from pymavlink import mavutil
import requests
from datetime import datetime
import time

SERVER_URL = "http://localhost:5000"

print("Connecting to Pixhawk...")
master = mavutil.mavlink_connection('/dev/serial0', baud=57600)
master.wait_heartbeat()
print("Heartbeat received from Pixhawk!")

# ---------------------------------------------------------
# WAIT FOR FIRST VALID GPS FIX
# ---------------------------------------------------------
print("Waiting for first valid GPS message...")

first_fix = False
while not first_fix:
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg:
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.alt / 1000

        # Check if GPS fix is valid
        if lat != 0 and lon != 0:
            first_fix = True
            print(f"GPS FIX ACQUIRED → Lat:{lat}, Lon:{lon}, Alt:{alt}")
        else:
            print("GPS not fixed yet... (lat/lon = 0)")
            time.sleep(1)

print("Starting continuous GPS streaming to central server...")
# ---------------------------------------------------------

# GPS Streaming Loop
while True:
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg:
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.alt / 1000
        ts = datetime.now().isoformat()

        # Send to central server
        try:
            requests.post(f"{SERVER_URL}/gps", json={
                "timestamp": ts,
                "lat": lat,
                "lon": lon,
                "alt": alt
            })
        except Exception as e:
            print("Error sending GPS:", e)

        print(f"GPS SENT → lat:{lat}, lon:{lon}, alt:{alt}")

    time.sleep(0.3)
