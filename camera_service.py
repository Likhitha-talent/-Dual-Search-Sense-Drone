from picamera2 import Picamera2
from ultralytics import YOLO
import time
import requests
from datetime import datetime
import os
import cv2  # for channel conversion
import numpy as np

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Initialize Picamera2
picam = Picamera2()
picam.start()

# Directory to save captured images
save_dir = "captures"
os.makedirs(save_dir, exist_ok=True)

# Central server URL
SERVER_URL = "http://localhost:5000"

print("Camera service started...")

while True:
    try:
        # Capture frame
        frame = picam.capture_array()
        print("Captured frame")

        # Convert 4-channel (XBGR) to 3-channel (BGR) if needed
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Run YOLO detection
        results = model(frame)
        print("YOLO processed frame")

        for r in results:
            # Convert tensors to numpy arrays
            boxes = r.boxes.xyxy.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy()

            for box, cls in zip(boxes, classes):
                cls = int(cls)
                print("Detected class:", cls)

                if cls == 0:  # person class
                    ts = datetime.now()
                    filename = f"{save_dir}/human_{ts.strftime('%Y%m%d_%H%M%S')}.jpg"
                    picam.capture_file(filename)

                    # Send event to central server
                    try:
                        resp = requests.post(f"{SERVER_URL}/event", json={
                            'filename': filename,
                            'type': 'human',
                            'timestamp': ts.isoformat()
                        })
                        print(f"Human detected & sent: {filename}, response: {resp.json()}")
                    except Exception as e:
                        print("Error sending event:", e)

        # Sleep to control FPS
        time.sleep(1)

    except KeyboardInterrupt:
        print("Camera service stopped.")
        break
    except Exception as e:
        print("Error in camera loop:", e)
        time.sleep(1)
