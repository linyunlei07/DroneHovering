# Interface for the TBD Drone Library

# initially called drone rc.py

"""
3. ESTABLISH CONNECTION WITH THE DRONE (Handshake)

- 'socket.connect' : Establishes the TCP link to 192.168.4.1 on port 8080
- 'msg()' : that converts Python strings (commands) into ASCII bytes the drone can read
- 'set_mode(2)' : 
    - mode 0 : done's motor = stoped
    - mode 1 : allows user to input to manually control each motor
    - mode 2: done's internal "autopilot" mode (this will be used to handle the "automatic" hovering)
        - drone: ORIENTATION
            - use its MPU6050 sensor (gyroscope and accelerometer), to calculate its orientation (aka tilt)
        - python LEVELING
            - correction of the drone when it leaves the 0.5m
- 'emergency_stop()' : makes the mode = 0, aka stoping the drones' motors



general advice:
do not have constant high-bandwidth communications with the drone,
because processing time doing wifi stuff is processing time not spent updating the gyroscope,
which will lead to increased drift

- this code handles the socket connection and command formatting
"""


import time 
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.4.1", 8080))            # IP adress

def msg(tx):
    s.sendall((tx + "\n").encode("ASCII"))
    rx = ""
    while not rx.endswith("\n"):
        rx += s.recv(1).decode("ASCII")
    return rx[:-1]


def emergency_stop():
    msg("mode0")
    
    green_LED(1)
    print("Blue LED ON")
    time.sleep(1)
    

def e():
    emergency_stop()

# mode 0: off
# mode 1: full manual motor control
# mode 2: PID control for pitch and roll
def set_mode(m):
    msg("mode" + str(m))

def get_mode():
    return msg("gMode")

# always between 0 and 250
# in mode 2 sets baseline value in PID results are added to
def manual_thrusts(A, B, C, D):
    msg("manT\n" + str(A) + "," + str(B) + "," + str(C) + "," + str(D) + "\n")

# same as prev function, but increments last value instead of overwriting
def increment_thrusts(A, B, C, D):
    msg("incT\n" + str(A) + "," + str(B) + "," + str(C) + "," + str(D) + "\n")

def get_pitch(): # unit close-ish to degrees, but not exact
    return float(msg("angX")) / 16

def get_roll(): # unit close-ish to degrees, but not exact
    return float(msg("angY")) / 16

def get_gyro_pitch(): # pitch rate in degree/sec
    return float(msg("gyroX"))

def get_gyro_roll(): # roll rate in degree/sec
    return float(msg("gyroY"))

# target pitch to aim for in mode 2
# same unit as get_pitch()
def set_pitch(r):
    msg("gx" + str(r))

# target roll to aim for in mode 2
# same unit as get_roll()
def set_roll(r):
    msg("gy" + str(r))

def set_p_gain(p): # approx 0 - 0.5
    msg("gainP" + str(p))

def set_i_gain(i): # below 0.00003
    msg("gainI" + str(i))

def set_d_gain(d): # approx 0 - 10
    msg("gainD" + str(d))

def red_LED(val): # controls LED light. 1 for on, 0 for off
    msg("lr" + str(val))

def blue_LED(val):
    msg("lb" + str(val))

def green_LED(val):
    msg("lg" + str(val))

def reset_integral(): # resets the value of integrands in the PID loops to 0
    msg("irst")

# returns [I_x, I_y] the integrands from the pitch and roll pid loops
def get_i_values():
    resp = msg("geti").split(",")
    return [float(resp[0]), float(resp[1])]

def set_yaw(y): # directly sets motor difference for yaw control
    msg("yaw" + str(y))
