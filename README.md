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

✅ Autonomous Flight Ready

Pixhawk + Raspberry Pi architecture

Grid/spiral search patterns (future integration)

Failsafe logic via LoRa/LTE (planned)

✅ Complete Evidence Capture

Saves image when person is detected

Saves audio when human sound is detected

Stores logs with timestamp + latitude + longitude + altitude
