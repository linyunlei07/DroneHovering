# This script runs on the drone. Its main job is to listen for UDP packets 
# and translate them into motor speeds using a basic PID for leveling.



import network
import usocket as socket
from machine import Pin, PWM, I2C
from imu import MPU6050 # You'll need to upload imu.py to the ESP32

# 1. Setup WiFi Access Point
ap = network.WLAN(network.AP_IF)
ap.config(essid='Drone-Alpha', password='hackathon-drone')
ap.active(True)

# 2. Setup UDP Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 1234))
sock.setblocking(False)

# 3. Setup Motors (PWM)
m1 = PWM(Pin(12), freq=500) # Example pins
m2 = PWM(Pin(13), freq=500)

def main_loop():
    while True:
        # Check for PC commands
        try:
            data, addr = sock.recvfrom(1024)
            # data looks like b'0.5,0.02' -> (throttle, roll_adjust)
            cmd = data.decode().split(',')
            target_throttle = float(cmd[0])
        except:
            pass 

        # High-speed leveling logic here
        # motor_val = base_throttle + pid_output
        # m1.duty(int(motor_val))