"""
KEEPS EVERYTHING RUNNING IN A CYCLE 

- 'cv2.VideoCapture' : connect to the two cameras
- 'cv2.imshow' : opens and external window to see what the camera "sees"
- 'cv2.waitKey' : waits for our commands (through keyboards) 

"""



import cv2
import drone_comm as drone
from vision import DroneTracker


def main():
    # 1. Initialize Components
    tracker = DroneTracker()
    cap = cv2.VideoCapture(1) # Your working laptop camera
    
    # 2. Starting baseline thrust (Equilibrium is usually around 140-160)
    target_thrust = 140 
    
    print("Connecting to Drone...")
    drone.set_mode(2) # Enable internal PID stabilization
    drone.blue_LED(1) # System Ready Signal

    print("\n--- MANUAL OVERRIDE ACTIVE ---")
    print("UP ARROW: Increase Thrust | DOWN ARROW: Decrease Thrust")
    print("SPACEBAR: EMERGENCY STOP | Q: Quit")

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break

            # 3. Vision Processing (The 'Eyes')
            #coords = tracker.get_drone_coords(frame, cam_id=1)
            
            # if coords:
            #     # Draw the tracking circle
            #     cv2.circle(frame, coords, 15, (0, 255, 0), 2)
            #     cv2.putText(frame, f"Y-Pixel: {coords[1]}", (10, 80), 
            #                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # # 4. Telemetry Overlay
            # cv2.putText(frame, f"Thrust: {target_thrust}", (10, 30), 
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            # cv2.imshow('Flight Dashboard', frame)

            # # 5. Continuous Command Sending (Must keep drone awake)
            # # Sends same thrust to all 4 motors A, B, C, D
            # drone.manual_thrusts(target_thrust, target_thrust, target_thrust, target_thrust)

            # # 6. Input Handling
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '): # Panic Button
                print("!!! EMERGENCY STOP !!!")
                drone.emergency_stop()
                break
            elif key == 'W': # Mac Up Arrow (Try 0 if this doesn't work)
                target_thrust += 2
            elif key == 'S': # Mac Down Arrow
                target_thrust -= 2
            elif key == ord('q'):
                drone.emergency_stop()
                break

    except Exception as e:
        print(f"Error: {e}")
        drone.emergency_stop()
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()