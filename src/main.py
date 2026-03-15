import cv2
import time
import drone_comm as drone
from vision import DroneTracker

# ==========================================
# 1. TUNING & CONFIGURATION CONSTANTS
# ==========================================
# PID: P (Strength), I (Steady-state correction), D (Braking/Damping)
# Note: These PIDs calculate the *Target Angle* to send to the drone's Mode 2
PID_X = {'kp': 0.07, 'ki': 0.01, 'kd': 0.04} 
PID_Y = {'kp': 0.07, 'ki': 0.01, 'kd': 0.04} 
PID_Z = {'kp': 0.35, 'ki': 0.08, 'kd': 0.15} 

MAX_TILT = 25.0         # Degrees. If drone tilts past this, kill motors.
MAX_THRUST_LIMIT = 185  # 0-250 scale. Leaves headroom for PID to add power.
SMOOTHING_ALPHA = 0.7   # Low-pass filter weight (0.7 = 70% new data).
LIFT_OFF_THRESHOLD = 12 # Pixels moved from initial_z to trigger flight mode.
WATCHDOG_LIMIT = 0.5    # Seconds. Emergency stop if vision stream hangs.

# ==========================================
# 2. SIGNAL PROCESSING & CONTROL CLASSES
# ==========================================
class SignalFilter:
    """Smoothes raw camera coordinates to prevent motor 'jitter'."""
    def __init__(self, alpha):
        self.alpha = alpha
        self.val = None

    def filter(self, new_val):
        if self.val is None: self.val = new_val
        self.val = (self.alpha * new_val) + (1 - self.alpha) * self.val
        return self.val

class PIDController:
    """Calculates necessary motor adjustments based on position error."""
    def __init__(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.last_err = 0
        self.integral = 0

    def update(self, error, dt):
        # Accumulate integral and clamp to prevent 'windup'
        self.integral = max(min(self.integral + error * dt, 10), -10)
        # Derivative calculates speed of error change to damp oscillation
        deriv = (error - self.last_err) / dt if dt > 0 else 0
        self.last_err = error
        return (self.kp * error) + (self.ki * self.integral) + (self.kd * deriv)

# ==========================================
# 3. MAIN FLIGHT LOOP
# ==========================================
def main():
    tracker = DroneTracker()
    cap0, cap1 = cv2.VideoCapture(0), cv2.VideoCapture(1) # Cam0=Front, Cam1=Side
    
    # Initialize PIDs and Low-Pass Filters
    x_pid, y_pid, z_pid = PIDController(**PID_X), PIDController(**PID_Y), PIDController(**PID_Z)
    f_x, f_y, f_z = SignalFilter(SMOOTHING_ALPHA), SignalFilter(SMOOTHING_ALPHA), SignalFilter(SMOOTHING_ALPHA)

    target_thrust, active_flight = 0, False
    initial_z = None
    last_time = time.time()
    last_vision_time = time.time()

    try:
        # Initial Hardware Setup
        drone.set_mode(2)      # Enable onboard PID leveling
        drone.reset_integral() # Clear drone's internal PID history
        time.sleep(1)
        
        # Calibration: Establish baseline level from MPU6050
        base_p = drone.get_pitch() 
        base_r = drone.get_roll()
        print(f"Calibrated. BaseP: {base_p:.2f} BaseR: {base_r:.2f}")

        while True:
            # --- LOOP TIMING & PROTECTION ---
            now = time.time()
            dt = now - last_time
            dt = min(dt, 0.1)  # Protection: Cap dt at 100ms to prevent PID spikes
            last_time = now

            # Watchdog: Emergency stop if vision processing takes too long
            if now - last_vision_time > WATCHDOG_LIMIT:
                print("Safety Stop: Vision Connection Lost")
                break

            # --- DATA ACQUISITION ---
            ret0, frame0 = cap0.read()
            ret1, frame1 = cap1.read()
            if not (ret0 and ret1): break

            # Track drone in both views
            c0 = tracker.get_drone_coords(frame0) # (x, z)
            c1 = tracker.get_drone_coords(frame1) # (y, alt_z)

            t_p, t_r = base_p, base_r # Default to baseline tilt

            # --- POSITION PROCESSING ---
            if c0 and c1:
                last_vision_time = now
                
                # Apply smoothing filters to raw coordinates
                # dx/dy/dz represent distance from screen centers
                dx = f_x.filter(c0[0] - (frame0.shape[1] // 2))
                dz = f_z.filter(c0[1] - (frame0.shape[0] // 2))
                dy = f_y.filter(c1[0] - (frame1.shape[1] // 2))

                if initial_z is None: initial_z = c0[1]

                # Update target Roll/Pitch via external PID
                # Active from start to correct ground-sliding
                t_r -= x_pid.update(dx, dt)
                t_p += y_pid.update(dy, dt)

                # --- THRUST LOGIC ---
                if not active_flight:
                    # Slow ramp-up until vertical movement is detected
                    target_thrust += 0.2 
                    if initial_z - c0[1] > LIFT_OFF_THRESHOLD:
                        active_flight = True
                        print(f"Lift-off! Thrust: {round(target_thrust,1)}")
                else:
                    # Maintain height using vertical PID
                    target_thrust += z_pid.update(dz, dt)

            # --- CRITICAL SAFETY CHECKS ---
            # Tilt Check: Check actual MPU6050 values against calibration baseline
            if abs(drone.get_pitch() - base_p) > MAX_TILT or \
               abs(drone.get_roll() - base_r) > MAX_TILT:
                print("Safety Stop: Excessive Tilt Detected")
                break
            
            # --- COMMAND DISPATCH ---
            target_thrust = max(0, min(target_thrust, MAX_THRUST_LIMIT))
            
            drone.set_pitch(t_p)  # Send target pitch to Mode 2
            drone.set_roll(t_r)   # Send target roll to Mode 2
            
            # Broadcast thrust to all motors (Mode 2 uses this as baseline)
            t_val = int(target_thrust)
            drone.manual_thrusts(t_val, t_val, t_val, t_val)

            # Dashboard Feed
            cv2.imshow('Front Control View', frame0)
            if cv2.waitKey(1) & 0xFF in [ord('q'), ord(' ')]: break

    except Exception as e:
        print(f"System Error: {e}")
    finally:
        # Shutdown sequence
        drone.emergency_stop()
        cap0.release()
        cap1.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()