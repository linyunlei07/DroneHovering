import cv2
import time
from vision import DroneTracker

def main():
    tracker = DroneTracker()
    cap = cv2.VideoCapture(0) # Your laptop webcam
    
    # Virtual Drone State
    virtual_thrust = 120  # Base hover starting point
    pitch_offset = 0      # Correction for the 0.5 deg/sec drift
    start_time = time.time()

    print("--- VIRTUAL FLIGHT TEST ---")
    print("1. Set your phone screen to SOLID BLUE.")
    print("2. Move it around in front of the webcam.")
    print("3. Watch the console for the 'sent' commands.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            h, w = frame.shape[:2]
            center_x, center_y = w // 2, h // 2

            # 1. SIMULATE GYRO DRIFT (0.5 deg per second)
            elapsed = time.time() - start_time
            simulated_drift = elapsed * 0.5

            # 2. VISION TRACKING
            coords = tracker.get_drone_coords(frame)
            
            thrust_cmd = "HOLD"
            roll_cmd = "CENTER"

            if coords:
                dx, dy = coords
                
                # --- VERTICAL LOGIC (Thrust) ---
                v_error = dy - center_y # Positive = Phone is too low
                if v_error > 25:
                    virtual_thrust += 1
                    thrust_cmd = "INCREASE ↑"
                elif v_error < -25:
                    virtual_thrust -= 1
                    thrust_cmd = "DECREASE ↓"

                # --- HORIZONTAL LOGIC (Roll/Lateral Drift) ---
                h_error = dx - center_x # Positive = Phone is too far right
                if h_error > 30:
                    roll_cmd = "TILT LEFT ←"
                elif h_error < -30:
                    roll_cmd = "TILT RIGHT →"

                # Visuals
                cv2.circle(frame, (dx, dy), 15, (255, 0, 0), 2) # Blue tracking circle
                cv2.line(frame, (center_x, center_y), (dx, dy), (0, 255, 0), 2) # Error vector

            # 3. CONSTRUCT THE "SENT" COMMANDS
            # Correcting for the simulated drift:
            # We tell the drone to aim for 'simulated_drift' to stay at 0 in reality
            final_pitch_target = 0 + simulated_drift 

            # 4. TELEMETRY OUTPUT
            # This mimics what would be sent to drone.manual_thrusts() and drone.set_pitch()
            print(f"\r[CMD SENT] Thrust: {virtual_thrust} ({thrust_cmd}) | Target Pitch: {final_pitch_target:.2f}° | Roll: {roll_cmd}    ", end="")

            # 5. DASHBOARD
            cv2.line(frame, (0, center_y), (w, center_y), (0, 0, 255), 1) # Target H
            cv2.line(frame, (center_x, 0), (center_x, h), (0, 0, 255), 1) # Target V
            cv2.putText(frame, f"Simulated Drift: {simulated_drift:.1f} deg", (10, 30), 1, 1, (255, 255, 255), 1)
            cv2.imshow('Drone Logic Simulator', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
