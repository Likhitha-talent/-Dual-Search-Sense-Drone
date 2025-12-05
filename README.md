# -Dual-Search-Sense-Drone

🔥 AeroRescue – Dual-Sense Human Detection Drone (Camera + Audio + GPS)
AI-Powered Search & Rescue System using YOLO, YAMNet, Pixhawk, and Raspberry Pi
Project Overview

AeroRescue is an AI-driven Search and Rescue (SAR) system that combines visual detection, acoustic detection, and real-time GPS mapping to locate victims in disaster environments.
Unlike traditional rescue drones that rely only on camera vision, AeroRescue detects:

Humans visible to the camera
Humans hidden under debris or low visibility (via sound)
GPS coordinates at the exact moment of detection
The system runs on Raspberry Pi, integrates with Pixhawk (PX4/Ardupilot) for autonomous flight, and communicates with a central ground station.

 Key Features
✅ Dual-Sense Human Detection
YOLOv8 vision-based person detection
YAMNet audio detection (speech, scream, cry, shout, human sounds)
Automatic logging of detected events
Instant synchronization with the ground station

✅ Real-Time GPS Integration
Reads GPS from Pixhawk via MAVLink
Continuous GPS streaming
Accurate location marking at detection instant

✅ Event Transmission to Ground Station
Sends camera events (/event)
Sends audio events (/event)
Sends GPS updates (/gps)

📸 1. Camera Detection Service (YOLOv8)
File: camera_detection.py
Captures frames using Picamera2
Runs YOLOv8 model
Saves images when a human is detected
Sends event JSON to server

🎤 2. Audio Detection Service (YAMNet)
File: voice_detection.py
Records audio using sounddevice
Runs YAMNet TFLite model
Detects keywords: Speech, Scream, Yell, Cry, Baby, etc.
Saves .wav file for positive detections
Sends event JSON (with GPS)

📡 3. GPS Reader (Pixhawk → MAVLink → Server)
File: gps_reader.py
Connects to Pixhawk via /dev/serial0
Waits for valid GPS fix
Streams GPS data to server every 0.3 sec
Provides live lat/long/alt

🌐 4. Ground Station Server (Flask)
Receives:
/event → human detection (image/audio)
/gps → location updates
Stores everything into:
CSV logs
Local folders
Dashboard-ready data
