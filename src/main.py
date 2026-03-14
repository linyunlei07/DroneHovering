"""
KEEPS EVERYTHING RUNNING IN A CYCLE 

- 'cv2.VideoCapture' : connect to the two cameras
- 'cv2.imshow' : opens and external window to see what the camera "sees"
- 'cv2.waitKey' : waits for our commands (through keyboards) 

"""

import cv2
import time
from vision import DroneTracker
import drone_comm as drone  
from controller import PIDController

def main():

    # 1. Setup Video Capture for two cameras 
    cam_top = cv2.VideoCapture(0)       
    cam_side = cv2.VideoCapture(1)
    
    # # Target height is ~0.5m
    # # We map 0.5m to a pixel value in our cage coordinate system
    # height_pid = PIDController(kp=0.5, ki=0.1, kd=0.05, target=240) 
    
    # last_time = time.time()


    # 2. Initialize Connection
    # The drone_comm script connects to 192.168.4.1:8080 automatically on import
    print("Connecting to ESP32-S2...")
    drone.set_mode(2)  # Set to PID mod                                                                                                                                                                                                                                                             e for stable pitch/roll 
    drone.blue_LED(1)  # Turn on Blue LED to signify system is ready


    # Target values
    target_thrust = 150  # Starting baseline thrust (range 0-250)

    print("CONTROL: Press 'SPACE' for EMERGENCY STOP | 'Q' to Quit")

    try:
        while True:
            ret_t, frame_top = cam_top.read()
            ret_s, frame_side = cam_side.read()

            if not ret_t or not ret_s:
                print("Failed to grab frames")
                break

            # --- VISION PROCESSING ---
            # (Insert your logic here to find drone x, y, z) [cite: 15, 16]
            
            # --- FLIGHT LOGIC ---
            # To avoid high-bandwidth lag, only send updates periodically
            # Example: Maintain 0.5m height by adjusting manual_thrusts 
            drone.manual_thrusts(target_thrust, target_thrust, target_thrust, target_thrust)

            # Display feeds
            cv2.imshow('Top View', frame_top)
            cv2.imshow('Side View', frame_side)

            # --- INPUT HANDLING ---
            key = cv2.waitKey(1) & 0xFF
            
            # MANDATORY MANUAL EMERGENCY STOPS: 
            # "panic exit"
            if key == ord(' '):
                print("!!! MANUAL EMERGENCY STOP TRIGGERED !!!")
                drone.emergency_stop()
                break
            
            # "soft exit" 
            if key == ord('q'):
                drone.emergency_stop()
                break

    except Exception as e:
        print(f"Error occurred: {e}")
        drone.emergency_stop() # Safety first!

    finally:
        cam_top.release()
        cam_side.release()
        cv2.destroyAllWindows()