"""
DRONE_COMM.PY - Optimized Drone Interface
Controls connection, command formatting, and hardware safety.
"""

import time 
import socket

# --- CONNECTION SETUP ---
# Using a global socket to maintain the session
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0) # Prevent code from hanging forever if drone disconnects
    s.connect(("192.168.4.1", 8080))
except Exception as e:
    print(f"FAILED TO CONNECT TO DRONE: {e}")

def msg(tx):
    """Formats and sends ASCII commands, waits for single-line response."""
    try:
        s.sendall((tx + "\n").encode("ASCII"))
        rx = ""
        # Read byte by byte until newline is reached
        while not rx.endswith("\n"):
            char = s.recv(1).decode("ASCII")
            if not char: break
            rx += char
        return rx.strip()
    except Exception as e:
        return f"Error: {e}"

# --- SYSTEM MODES ---
def set_mode(m):
    """
    mode 0: STOP - Kill all motors
    mode 1: MANUAL - Direct motor control
    mode 2: AUTO - Internal PID stabilization (MPU6050 active)
    """
    return msg(f"mode{m}")

def emergency_stop():
    """Immediately kills motors and signals status via LEDs."""
    msg("mode0")
    green_LED(1) # Visual confirmation of stop
    print("!!! EMERGENCY STOP EXECUTED - MOTORS KILLED !!!")

# --- THRUST & MOVEMENT ---
def manual_thrusts(A, B, C, D):
    """Sets baseline thrust for motors A, B, C, and D (0-250)."""
    # Double newline is required by the drone's parser for manT
    return msg(f"manT\n{A},{B},{C},{D}\n")

def set_pitch(val):
    """Sets target pitch for Mode 2 autopilot (MPU6050 units)."""
    return msg(f"gx{val}")

def set_roll(val):
    """Sets target roll for Mode 2 autopilot (MPU6050 units)."""
    return msg(f"gy{val}")

def set_yaw(val):
    """Sets motor differential for rotation control."""
    return msg(f"yaw{val}")

# --- TELEMETRY (IMU DATA) ---
def get_pitch():
    """Returns current pitch angle. Scaled /16 to match degree-ish units."""
    resp = msg("angX")
    try: return float(resp) / 16
    except: return 0.0

def get_roll():
    """Returns current roll angle. Scaled /16 to match degree-ish units."""
    resp = msg("angY")
    try: return float(resp) / 16
    except: return 0.0

# --- HARDWARE UTILITIES ---
def reset_integral():
    """Resets the onboard PID integrators to prevent 'runaway' lift."""
    return msg("irst")

def red_LED(val):
    """1 = On, 0 = Off"""
    msg(f"lr{val}")

def green_LED(val):
    """1 = On, 0 = Off"""
    msg(f"lg{val}")

def blue_LED(val):
    """1 = On, 0 = Off"""
    msg(f"lb{val}")

# --- PID GAIN TUNING (USE WITH CAUTION) ---
def set_p_gain(p): msg(f"gainP{p}")
def set_i_gain(i): msg(f"gainI{i}")
def set_d_gain(d): msg(f"gainD{d}")