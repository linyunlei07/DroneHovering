# This script runs on the drone. Its main job is to listen for UDP packets 
# and translate them into motor speeds using a basic PID for leveling.



import cv2
import time
from vision import DroneTracker
from controller import PIDController

def main():
    # Initialize hardware
    cam_top = cv2.VideoCapture(0)
    tracker = DroneTracker()
    
    # Target height is ~0.5m
    # We map 0.5m to a pixel value in our cage coordinate system
    height_pid = PIDController(kp=0.5, ki=0.1, kd=0.05, target=240) 
    
    last_time = time.time()

    while True:
        ret, frame = cam_top.read()
        if not ret: break
        
        now = time.time()
        dt = now - last_time
        last_time = now

        coords = tracker.get_drone_coords(frame)
        if coords:
            # Adjust throttle based on vertical pixel error
            thrust_adj = height_pid.compute(coords[1], dt)
            # print(f"Sending thrust adjustment: {thrust_adj}")

        cv2.imshow("Drone Feed", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '): # MANDATORY EMERGENCY STOP
            print("!!! EMERGENCY STOP !!!")
            # custom_lib.kill_engines()
            break
        elif key == ord('q'):
            break

    cam_top.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()