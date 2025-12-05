import sounddevice as sd
import tflite_runtime.interpreter as tflite
import soundfile as sf
import numpy as np
import csv
import time
import os
import requests
from datetime import datetime
from threading import Thread

# Optional Pixhawk integration
try:
    from pymavlink import mavutil
    PIXHAWK_AVAILABLE = True
except ImportError:
    PIXHAWK_AVAILABLE = False

# -------------------------
# Config
# -------------------------
MODEL_PATH = "/home/pi/yamnet_live/yamnet.tflite"
CLASS_MAP_PATH = "/home/pi/yamnet_live/yamnet_class_map.csv"
SAMPLE_RATE = 16000
RECORD_SECONDS = 3
NUM_SAMPLES = 15600        # YAMNet model input size
LOG_FILE = "/home/pi/human_detection_log.csv"
AUDIO_DIR = "/home/pi/human_audio"
SERVER_URL = "http://localhost:5000"
CONFIDENCE_THRESHOLD = 0.5  # Only save if score >= 0.5

# Default GPS
gps_data = {"lat": 0.0, "lon": 0.0, "alt": 0.0}

# -------------------------
# Create folder for saving audio
# -------------------------
os.makedirs(AUDIO_DIR, exist_ok=True)

# -------------------------
# Load class map
# -------------------------
class_map = []
with open(CLASS_MAP_PATH) as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        class_map.append(row[2])

# -------------------------
# Load TFLite model
# -------------------------
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# -------------------------
# CSV initialization
# -------------------------
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "label", "score", "audio_file", "lat", "lon", "alt"])

# -------------------------
# GPS Thread
# -------------------------
def gps_thread():
    global gps_data
    if not PIXHAWK_AVAILABLE:
        print("Pixhawk not available. GPS will remain 0 until connected.")
        return

    try:
        print("Connecting to Pixhawk...")
        master = mavutil.mavlink_connection('/dev/serial0', baud=57600)
        master.wait_heartbeat()
        print("Heartbeat received from Pixhawk!")

        while True:
            msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if msg:
                lat = msg.lat / 1e7
                lon = msg.lon / 1e7
                alt = msg.alt / 1000
                if lat != 0 and lon != 0:
                    gps_data = {"lat": lat, "lon": lon, "alt": alt}
            time.sleep(0.1)

    except Exception as e:
        print("Pixhawk connection failed:", e)
        print("GPS will remain at 0 until connected.")

# Start GPS thread
Thread(target=gps_thread, daemon=True).start()

# -------------------------
# Recording and prediction
# -------------------------
def record_audio():
    audio = sd.rec(RECORD_SECONDS * SAMPLE_RATE, samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    return audio

def predict(audio):
    input_audio = audio[:NUM_SAMPLES].flatten().astype(np.float32)
    interpreter.set_tensor(input_details[0]["index"], input_audio)
    interpreter.invoke()
    scores = interpreter.get_tensor(output_details[0]["index"])
    mean_scores = np.mean(scores, axis=0)
    top_idx = np.argmax(mean_scores)
    return class_map[top_idx], float(mean_scores[top_idx])

# -------------------------
# Keywords to detect human sounds
# -------------------------
HUMAN_KEYWORDS = ["Speech", "Scream", "Yell", "Human", "Cry", "Baby", "Shout"]

print("🔥 Starting Human Voice Detection Service...")

# -------------------------
# Main loop
# -------------------------
while True:
    audio = record_audio()
    label, score = predict(audio)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if any(word in label for word in HUMAN_KEYWORDS) and score >= CONFIDENCE_THRESHOLD:
        print("⚠ Human sound detected! Saving audio...")

        filename = f"{timestamp}_{label.replace(' ', '_')}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)
        sf.write(filepath, audio, SAMPLE_RATE)

        # Send to server
        try:
            requests.post(f"{SERVER_URL}/event", json={
                "filename": filename,
                "type": "voice",
                "timestamp": timestamp,
                "lat": gps_data["lat"],
                "lon": gps_data["lon"],
                "alt": gps_data["alt"]
            })
        except Exception as e:
            print("⚠ Could not send event to server (server may be offline)")

        # Save log
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, label, score, filename, gps_data["lat"], gps_data["lon"], gps_data["alt"]])

        print(f"Saved: {filepath} (Score={score:.2f}, GPS={gps_data})\n")
    else:
        print(f"{timestamp} — No human voice detected (Score={score:.3f})")
