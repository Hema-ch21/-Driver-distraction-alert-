# Driver Distraction Alert 🚗💡

**Real-time driver monitoring system** that detects drowsiness and distraction to help prevent accidents.

---

## Overview
Driver Distraction Alert continuously monitors a driver’s face to detect:

- **Drowsiness:** Eyes closed for more than 5 seconds.
- **Distraction:** Looking left or right for more than 10 seconds.

When detected, the system plays an **audio buzzer alert** to notify the driver.

---

## Features
- **Drowsiness Detection:** Alerts when eyes remain closed >5 seconds.
- **Side Distraction Detection:** Alerts when looking left/right >10 seconds.
- **Real-Time Monitoring:** Works with your webcam for live tracking.
- **Audio Alerts:** Uses buzzer sound via Pygame for instant feedback.
- **Lightweight & Extensible:** Built using Python, OpenCV, MediaPipe, and Pygame.

---

## How It Works
1. Start the system – the camera tracks the driver’s face in real-time.
2. **Eye Closure Detection:** If eyes are closed >5 seconds → buzzer plays.
3. **Head/Side Distraction Detection:**  
   - Right side >10 seconds → buzzer plays.  
   - Left side >10 seconds → buzzer plays.
4. Continuous monitoring repeats alerts until driver attention returns.

---

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/DriverDistractionAlert.git

# Navigate to the project folder
cd C:\Users\venka\PycharmProjects\driver

# Install dependencies
pip install -r requirements.txt
