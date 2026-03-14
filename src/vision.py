# Drone detection & tracking (OpenCV)

""" 
THIS IS THE EYES 
- sees the world (through the two cameras), but you need to make sense of it. 
- therefore we need to process the image 

Essentially: 
takes the camera feed and finds the (x, y) pixel location of the drone's LED 

"""

import cv2
import numpy as np

class DroneTracker:
    def __init__(self):
        # Typical HSV range for a Blue LED
        self.lower_blue = np.array([100, 150, 150])
        self.upper_blue = np.array([140, 255, 255])

    def get_drone_coords(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        
        # Find contours of the LED
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get the largest contour (the LED)
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                return (cX, cY)
        return None