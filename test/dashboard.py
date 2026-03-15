# dashboard.py
import cv2
import drone_comm as drone
from vision import DroneTracker
import time

def main():
    # Initialize components
    tracker = DroneTracker()
    cap = cv2.VideoCapture(1) # Using your working laptop camera
    
    print("Connecting to drone telemetry...")
    drone.set_mode(2) # Keep drone in stable mode for sensor reading
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Get Vision Data (The 'Eyes')
        coords = tracker.get_drone_coords(frame)
        
        # 2. Get Telemetry Data (The 'Nervous System')
        pitch = drone.get_pitch()
        roll = drone.get_roll()
        mode = drone.get_mode()

        # --- DRAWING ON THE FEED ---
        if coords:
            # Draw a circle around the detected drone
            cv2.circle(frame, coords, 15, (0, 255, 0), 2)
            # Display the pixel coordinates
            cv2.putText(frame, f"Pixels: {coords}", (coords[0]+20, coords[1]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Display Telemetry Overlay
        cv2.rectangle(frame, (10, 10), (250, 100), (0, 0, 0), -1) # Background box
        cv2.putText(frame, f"Pitch: {pitch:.2f}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Roll: {roll:.2f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Mode: {mode}", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.imshow("Drone Live Dashboard", frame)

        # --- INPUT HANDLING ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '): # Panic Button [cite: 29]
            drone.emergency_stop()
            print("Emergency Stop Triggered!")
            break
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    