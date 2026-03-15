# Vision-Stabilized PID Drone Controller

This project implements a real-time, 3D vision-based flight control system for a quadcopter. It uses two cameras (Front and Side) to track the drone's position via LED detection and stabilizes flight using a custom PID architecture integrated with the drone's onboard autopilot.

---

## Project Architecture

The system consists of three core modules designed to handle high-latency wireless communication while maintaining precise stabilization:

* **`main.py`**: The central control loop coordinating vision data, PID logic, and safety interlocks.
* **`vision.py`**: The "Eyes" of the system, using OpenCV to detect and smooth the $(x, y)$ coordinates of the drone's LEDs.
* **`drone_comm.py`**: The communication interface handling the TCP socket handshake and command formatting for the drone hardware.

---

## Key Features

### 1. 3D PID Stabilization
The controller utilizes three independent PID loops to maintain a stable hover:
* **X-Axis (Roll)**: Corrects left/right drift using the Front camera.
* **Y-Axis (Pitch)**: Corrects forward/backward drift using the Side camera.
* **Z-Axis (Thrust)**: Maintains vertical altitude relative to the center of the frame.



### 2. Intelligent Takeoff
Instead of a hardcoded thrust value, the system employs a dynamic ramp-up:
* It monitors the floor position (`initial_z`).
* It increments thrust gradually until vertical displacement is detected.
* Active flight mode triggers automatically once lift-off is confirmed.

### 3. Advanced Vision Processing
The `DroneTracker` uses **Color Excess filtering** to isolate LEDs:
* It identifies pixels where a specific color is significantly more dominant than others to reduce interference from ambient light.
* A **Signal Filter** (Low-Pass Filter) is applied to coordinates to prevent motor "jitter" caused by camera sensor noise.

### 4. Triple-Layer Safety
* **Watchdog Timer**: Kills motors if the vision stream hangs for more than 0.5 seconds.
* **Tilt-Limit Detection**: Monitors the onboard MPU6050; if the drone tilts beyond 25°, the system executes an emergency stop.
* **dt Normalization**: Caps time-delta calculations to 100ms to prevent power spikes during CPU lag.

---

## Installation & Setup

1. **Hardware Connection**: Ensure your computer is connected to the drone's Wi-Fi Access Point (Default: `192.168.4.1`).
2. **Camera Placement**: 
    * **Camera 0**: Positioned in front of the flight area (X/Z tracking).
    * **Camera 1**: Positioned to the side of the flight area (Y tracking).
3. **Dependencies**:
   ```bash
   pip install opencv-python numpy