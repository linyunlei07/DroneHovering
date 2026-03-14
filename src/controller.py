#PID or control logic

"""
2. THIS IS THE BRAIN 
INPUT : makes the adjustement needed to keep the drone in place, accoriding to 'vision.py' data
OUTPUT : ends up calculating an output value so we can tell the motor to, speed up, slow down for ex. 


Using PIDController to implement a feedback loop
- P (Proportional): Corrects based on how far away you are from the 0.5m target
- I (Integral): Fixes small, persistent errors (like a slight breeze pushing the drone)
- D (Derivative): Predicts the drone's momentum to prevent it from "overshooting" and hitting the ceiling


"""




class PIDController:
    def __init__(self, kp, ki, kd, target):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target = target
        self.prev_error = 0
        self.integral = 0

    def compute(self, current_val, dt):
        error = self.target - current_val
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_error = error
        return output