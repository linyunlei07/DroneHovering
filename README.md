# DroneHovering

####
FIXME : Reformat the file, such that it does not look like it was copied from Gemini 
#####


Team [Your Name] - Vision-Based Autonomous HoverOverviewThis system enables an ESP32-S2-MINI drone to maintain a stable hover at 0.5m within a $1\text{m} \times 1\text{m} \times 1\text{m}$ flight cage. It utilizes two external USB cameras to triangulate position and sends real-time control commands via Python


System ArchitectureVision: Uses OpenCV to track the drone's built-in LED. By processing two feeds, we calculate $(x, y, z)$ coordinates.Estimation: Coordinates are filtered to reduce noise from camera latency.Control: A PID Controller (Proportional-Integral-Derivative) adjusts throttle, pitch, and roll to maintain the target zone.Safety: A dedicated Emergency Stop function is mapped to the SPACE key to immediately terminate flight.


How to Run
Activate the virtual environment: source drone_env/bin/activate.

Install dependencies: pip install -r requirements.txt.

Run the main script: python main.py.


2. Triangulation Logic (The Math)Since the cameras are fixed at known positions overlooking the cage, you can estimate the drone's 3D position by combining the 2D data from each camera.$$x_{pos} \approx \text{Camera 1 (Horizontal Pixel Value)}$$$$y_{pos} \approx \text{Camera 2 (Horizontal Pixel Value)}$$$$z_{pos} \approx \text{Average (Vertical Pixel Value from both)}$$



3. Handling the "Disturbance Test" (Bonus Points)
The rubric offers a 20% bonus for handling external disturbances. To prepare for this:

Increase your "D" (Derivative) gain: In a PID controller, the Derivative term helps resist sudden changes (like someone blowing air on the drone).


Sampling Rate: Ensure your Python loop is running fast enough (at least 30-60 FPS) so the cameras catch the disturbance immediately.