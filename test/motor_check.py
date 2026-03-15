# this is not working, run directly on main

"""
run this, to check if the motor will spin
"""

# motor_check.py
import drone_comm as drone
import time

def spin_test():
    print("Initializing Motors... STAY CLEAR.")
    
    # 1. Unlock the motors (Mode 2 enables internal stability)
    drone.set_mode(2) 
    time.sleep(0.5)
    
    # 2. Send 'Idle' Thrust (40 is usually the minimum to overcpome friction)
    # manual_thrusts(MotorA, MotorB, MotorC, MotorD)
    print("Sending Idle Thrust (40/250)...")
    drone.manual_thrusts(80, 80, 80, 80)
    
    # 3. Spin for 3 seconds so you can verify all 4 motors are working
    time.sleep(5)
    
    # 4. Mandatory Kill Command
    print("Shutting down.")
    drone.emergency_stop()

if __name__ == "__main__":
    spin_test()
