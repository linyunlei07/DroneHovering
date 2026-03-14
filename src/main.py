"""
KEEPS EVERYTHING RUNNING IN A CYCLE 

- 'cv2.VideoCapture' : connect to the two cameras
- 'cv2.imshow' : opens and external window to see what the camera "sees"
- 'cv2.waitKey' : waits for our commands (through keyboards) 

"""

import cv2
import drone_comm as drone
from vision import DroneTracker
import time

def main():
    tracker = DroneTracker()
    cap = cv2.VideoCapture(1) # Using your working laptop camera
    
    # this controls up down 
    target_thrust = 80 
    
    print("Connecting to Drone...")


    drone.emergency_stop()
    drone.set_mode(2) # Enable stable mode to unlock motors

    drone.blue_LED(1) 
    drone.blue_LED(0)




    print("\n--- TEST MODE ACTIVE ---")
    print("W: Increase Thrust | S: Decrease Thrust")
    print("SPACEBAR: EMERGENCY STOP | Q: Quit")

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break

            # 1. Vision Processing (The 'Eyes')
            coords = tracker.get_drone_coords(frame, cam_id=1)
            
            if coords:
                cv2.circle(frame, coords, 15, (0, 255, 0), 2)
                cv2.putText(frame, f"Y-Pixel: {coords[1]}", (10, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # 2. Status Overlay
            cv2.putText(frame, f"Thrust: {target_thrust}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Flight Dashboard', frame)

            # 3. Send Thrust Command [cite: 1, 38]
            drone.manual_thrusts(target_thrust, target_thrust, target_thrust, target_thrust)

            # 4. Input Handling
            key = cv2.waitKey(1) & 0xFF
            
            # If spacebar doesn't work, try tapping 'Q' or 'ESC' (27)
            if key == ord(' ') or key == ord('q') or key == 27: 
                print("\n!!! EMERGENCY STOP TRIGGERED !!!")
                # Send kill command 3 times to ensure it clears the WiFi buffer [cite: 26]
                for _ in range(3):
                    # drone.msg("mode0") 
                    drone.emergency_stop()
                break
                
            elif key == ord('w') or key == ord('W'):
                # Cap thrust at 200 per firmware limits [cite: 1, 55]
                target_thrust = min(target_thrust + 5, 200) 
                print(f"Thrust: {target_thrust}")
                
            elif key == ord('s') or key == ord('S'):
                target_thrust = max(target_thrust - 5, 0)
                print(f"Thrust: {target_thrust}")

    except Exception as e:
        print(f"Error: {e}")
        drone.emergency_stop()
        # drone.msg("mode0")


    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()