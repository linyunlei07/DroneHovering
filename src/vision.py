import cv2
import numpy as np

"""
Processes raw pixels to find the (x, y) center of the drone's LED.
Utilizes HSV color filtering and Color Excess thresholding for reliability.
"""

class DroneTracker:
    def __init__(self):
        # Area constraints to filter out tiny noise or large background glares
        self.min_area = 2
        self.max_area = 200 
        
        # Internal smoothing to prevent coordinate jumping
        self.smoothing_alpha = 0.7
        self.last_centers = {} # Dictionary to store (x, y) per camera ID

    def _build_color_masks(self, hsv, bgr):
        """
        Creates binary masks for Blue (Calibration) and Green (Flight) LEDs.
        Combines HSV ranges with channel subtraction to isolate pure colors.
        """
        b, g, r = cv2.split(bgr)
        masks = {}
        
        # --- Blue LED Mask ---
        # Standard HSV range for blue
        lower_blue = np.array([90, 60, 60])
        upper_blue = np.array([145, 255, 255])
        hsv_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Color Excess: Only keep pixels where Blue is significantly stronger than Red/Green
        # Helps filter out white sunlight or overhead light bulbs
        b_excess = cv2.threshold(b.astype(np.int16) - ((r.astype(np.int16) + g.astype(np.int16)) // 2), 20, 255, cv2.THRESH_BINARY)[1]
        masks["blue"] = cv2.bitwise_and(hsv_blue, b_excess.astype(np.uint8))
        
        # --- Green LED Mask ---
        # Standard HSV range for green
        lower_green = np.array([40, 70, 70])
        upper_green = np.array([90, 255, 255])
        hsv_green = cv2.inRange(hsv, lower_green, upper_green)
        
        # Color Excess: Only keep pixels where Green is dominant
        g_excess = cv2.threshold(g.astype(np.int16) - ((r.astype(np.int16) + b.astype(np.int16)) // 2), 20, 255, cv2.THRESH_BINARY)[1]
        masks["green"] = cv2.bitwise_and(hsv_green, g_excess.astype(np.uint8))

        return masks

    def get_drone_coords(self, frame, cam_id=0):
        """
        Processes a frame and returns the (x, y) pixel coordinates of the drone.
        Returns None if the drone is not detected.
        """
        # 1. Convert to HSV for better color isolation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_masks = self._build_color_masks(hsv, frame)
        
        for mask in color_masks.values():
            # 2. Cleanup: Remove tiny specks of noise
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2,2), np.uint8))
            
            # 3. Find White Shapes (Contours) in the blacked-out mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if self.min_area < area < self.max_area:
                    # 4. Calculate Center of Gravity (Moments)
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        raw_x = int(M["m10"] / M["m00"])
                        raw_y = int(M["m01"] / M["m00"])
                        new_center = (raw_x, raw_y)
                        
                        # 5. Temporal Smoothing: Blend new data with previous frame position
                        # Prevents the "strobe" effect if tracking is lost for 1 frame
                        if cam_id in self.last_centers and self.last_centers[cam_id] is not None:
                            prev_center = self.last_centers[cam_id]
                            sx = self.smoothing_alpha * raw_x + (1.0 - self.smoothing_alpha) * prev_center[0]
                            sy = self.smoothing_alpha * raw_y + (1.0 - self.smoothing_alpha) * prev_center[1]
                            final_center = (int(sx), int(sy))
                        else:
                            final_center = new_center
                        
                        self.last_centers[cam_id] = final_center
                        return final_center
                        
        return None