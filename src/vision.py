# Drone detection & tracking (OpenCV)

""" 
1. THIS IS THE EYES 
- through the camera, it takes raw pixels and turns them into data
-> using the camera we find where the drone is (x, y, z) in the box
-> tracking using the camera's LED 

Essentially: 
takes the camera feed and finds the (x, y) pixel location of the drone's LED 


Functions: 
'cv2.cvtColor' : converts usual video (RGB) to HSV 
'cv2.inRange' : this is a colorFilter. turns LED color into WHITE, everything else into BLACK
'cv2.findContours' : this finds the WHITE (among the blacked out plane)
'cv2.moments' : math function that calculates the center of the drone (according to the 4 LEDs)

"""



# new tailored version, combining Kevin's and mine 
import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, Dict

@dataclass
class Detection:
    found: bool
    center: Optional[Tuple[int, int]]
    area: float = 0.0
    color: str = "unknown"
    confidence: float = 0.0

class DroneTracker:
    def __init__(self):
        # Parameters matched to your friend's logic
        self.min_area = 1
        self.max_area = 100 
        self.smoothing_alpha = 0.7
        self.last_centers: Dict[int, Optional[Tuple[float, float]]] = {}
        
    def _build_color_masks(self, hsv, bgr):
        b, g, r = cv2.split(bgr)
        masks = {}
        
        # Blue Mask (The one your drone uses during calibration)
        lower_blue = np.array([90, 60, 60])
        upper_blue = np.array([145, 255, 255])
        hsv_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        b_excess = cv2.threshold(b.astype(np.int16) - ((r.astype(np.int16) + g.astype(np.int16)) // 2), 18, 255, cv2.THRESH_BINARY)[1]
        masks["blue"] = cv2.bitwise_and(hsv_blue, b_excess.astype(np.uint8))
        
        # Green Mask (The one the drone uses when ready)
        lower_green = np.array([40, 80, 80])
        upper_green = np.array([90, 255, 255])
        hsv_green = cv2.inRange(hsv, lower_green, upper_green)
        g_excess = cv2.threshold(g.astype(np.int16) - ((r.astype(np.int16) + b.astype(np.int16)) // 2), 18, 255, cv2.THRESH_BINARY)[1]
        masks["green"] = cv2.bitwise_and(hsv_green, g_excess.astype(np.uint8))

        return masks

    def get_drone_coords(self, frame, cam_id=0):
        """
        Main interface for main.py. 
        Returns (x, y) tuple or None.
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_masks = self._build_color_masks(hsv, frame)
        
        best_center = None
        
        for color_name, mask in color_masks.items():
            # Clean up noise
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2,2), np.uint8))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if self.min_area < area < self.max_area:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        new_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                        
                        # Apply smoothing
                        if cam_id in self.last_centers and self.last_centers[cam_id] is not None:
                            lc = self.last_centers[cam_id]
                            sx = self.smoothing_alpha * new_center[0] + (1.0 - self.smoothing_alpha) * lc[0]
                            sy = self.smoothing_alpha * new_center[1] + (1.0 - self.smoothing_alpha) * lc[1]
                            best_center = (int(sx), int(sy))
                        else:
                            best_center = new_center
                        
                        self.last_centers[cam_id] = best_center
                        return best_center
        return None





# import cv2
# import numpy as np

# class DroneTracker:
#     def __init__(self):
#         # Typical HSV range for a Blue LED
#         self.lower_blue = np.array([100, 150, 150])
#         self.upper_blue = np.array([140, 255, 255])

#     def get_drone_coords(self, frame):
#         hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#         mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        
#         # Find contours of the LED
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
#         if contours:
#             # Get the largest contour (the LED)
#             c = max(contours, key=cv2.contourArea)
#             M = cv2.moments(c)
#             if M["m00"] != 0:
#                 cX = int(M["m10"] / M["m00"])
#                 cY = int(M["m01"] / M["m00"])
#                 return (cX, cY)
#         return None
    






# """
# kevin's
# """

# import cv2
# import numpy as np
# from dataclasses import dataclass
# from typing import Optional, Tuple, Dict


# @dataclass
# class Detection:
#     found: bool
#     center: Optional[Tuple[int, int]]
#     area: float = 0.0
#     bbox: Optional[Tuple[int, int, int, int]] = None
#     confidence: float = 0.0
#     color: str = "unknown"


# class DroneLEDDetector:
#     def __init__(
#         self,
#         min_area: int = 1,
#         max_area: int = 60,
#         blur_size: int = 3,
#         morph_kernel_size: int = 2,
#         roi_half_size: int = 80,
#         max_missed_frames: int = 6,
#         smoothing_alpha: float = 0.7,
#         detect_blue: bool = True,
#         detect_green: bool = True,
#         detect_red: bool = True,
#     ):
#         self.min_area = min_area
#         self.max_area = max_area
#         self.blur_size = blur_size if blur_size % 2 == 1 else blur_size + 1
#         self.roi_half_size = roi_half_size
#         self.max_missed_frames = max_missed_frames
#         self.smoothing_alpha = smoothing_alpha

#         self.detect_blue = detect_blue
#         self.detect_green = detect_green
#         self.detect_red = detect_red

#         self.kernel = np.ones((morph_kernel_size, morph_kernel_size), np.uint8)

#         self.last_centers: Dict[int, Optional[Tuple[float, float]]] = {}
#         self.last_areas: Dict[int, Optional[float]] = {}
#         self.missed_frames: Dict[int, int] = {}
#         self.last_masks: Dict[int, Optional[np.ndarray]] = {}

#     def _get_roi(
#         self, frame: np.ndarray, cam_id: int
#     ) -> Tuple[np.ndarray, Tuple[int, int], bool]:
#         h, w = frame.shape[:2]
#         last_center = self.last_centers.get(cam_id)

#         if last_center is None:
#             return frame, (0, 0), False

#         cx, cy = int(last_center[0]), int(last_center[1])
#         hs = self.roi_half_size

#         x1 = max(0, cx - hs)
#         y1 = max(0, cy - hs)
#         x2 = min(w, cx + hs)
#         y2 = min(h, cy + hs)

#         if x2 <= x1 or y2 <= y1:
#             return frame, (0, 0), False

#         return frame[y1:y2, x1:x2], (x1, y1), True

#     def _build_color_masks(self, frame_bgr: np.ndarray) -> Dict[str, np.ndarray]:
#         """
#         Returns masks for blue, green, and red LEDs.
#         Uses BOTH HSV and channel-dominance logic.
#         """
#         hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
#         b, g, r = cv2.split(frame_bgr)
#         gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

#         masks: Dict[str, np.ndarray] = {}

#         # Shared brightness gate
#         _, bright_mask = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

#         if self.detect_green:
#             lower_green = np.array([40, 80, 80], dtype=np.uint8)
#             upper_green = np.array([90, 255, 255], dtype=np.uint8)
#             hsv_green = cv2.inRange(hsv, lower_green, upper_green)

#             g_excess = g.astype(np.int16) - ((r.astype(np.int16) + b.astype(np.int16)) // 2)
#             g_excess = np.clip(g_excess, 0, 255).astype(np.uint8)
#             _, g_dom = cv2.threshold(g_excess, 18, 255, cv2.THRESH_BINARY)

#             masks["green"] = cv2.bitwise_and(hsv_green, cv2.bitwise_and(g_dom, bright_mask))

#         if self.detect_blue:
#             lower_blue = np.array([90, 60, 60], dtype=np.uint8)
#             upper_blue = np.array([145, 255, 255], dtype=np.uint8)
#             hsv_blue = cv2.inRange(hsv, lower_blue, upper_blue)

#             b_excess = b.astype(np.int16) - ((r.astype(np.int16) + g.astype(np.int16)) // 2)
#             b_excess = np.clip(b_excess, 0, 255).astype(np.uint8)
#             _, b_dom = cv2.threshold(b_excess, 18, 255, cv2.THRESH_BINARY)

#             masks["blue"] = cv2.bitwise_and(hsv_blue, cv2.bitwise_and(b_dom, bright_mask))

#         if self.detect_red:
#             lower_red1 = np.array([0, 80, 80], dtype=np.uint8)
#             upper_red1 = np.array([12, 255, 255], dtype=np.uint8)
#             lower_red2 = np.array([170, 80, 80], dtype=np.uint8)
#             upper_red2 = np.array([179, 255, 255], dtype=np.uint8)

#             hsv_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
#             hsv_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
#             hsv_red = cv2.bitwise_or(hsv_red1, hsv_red2)

#             r_excess = r.astype(np.int16) - ((g.astype(np.int16) + b.astype(np.int16)) // 2)
#             r_excess = np.clip(r_excess, 0, 255).astype(np.uint8)
#             _, r_dom = cv2.threshold(r_excess, 18, 255, cv2.THRESH_BINARY)

#             masks["red"] = cv2.bitwise_and(hsv_red, cv2.bitwise_and(r_dom, bright_mask))

#         return masks

#     def _score_candidate(
#         self,
#         contour: np.ndarray,
#         region: np.ndarray,
#         offset: Tuple[int, int],
#         cam_id: int,
#     ) -> Tuple[float, Tuple[int, int], float, Tuple[int, int, int, int], float]:
#         area = cv2.contourArea(contour)
#         x, y, w, h = cv2.boundingRect(contour)

#         if area <= 0:
#             return -1e9, (0, 0), 0.0, (x, y, w, h), 0.0

#         cx_local = x + w // 2
#         cy_local = y + h // 2
#         cx = cx_local + offset[0]
#         cy = cy_local + offset[1]

#         patch = region[y:y + h, x:x + w]
#         if patch.size == 0:
#             brightness = 0.0
#         else:
#             brightness = float(np.mean(cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)))

#         aspect_ratio = max(w, h) / max(1, min(w, h))
#         shape_penalty = abs(aspect_ratio - 1.0)

#         last_center = self.last_centers.get(cam_id)
#         if last_center is None:
#             dist_penalty = 0.0
#         else:
#             dist = np.hypot(cx - last_center[0], cy - last_center[1])
#             dist_penalty = 0.05 * dist

#         last_area = self.last_areas.get(cam_id)
#         if last_area is None:
#             area_penalty = 0.0
#         else:
#             area_penalty = 0.08 * abs(area - last_area)

#         score = (
#             1.5 * area
#             + 0.7 * brightness
#             - 8.0 * shape_penalty
#             - dist_penalty
#             - area_penalty
#         )

#         return score, (cx, cy), area, (x + offset[0], y + offset[1], w, h), brightness

#     def _detect_in_region(
#         self, region: np.ndarray, offset: Tuple[int, int], cam_id: int
#     ) -> Optional[Detection]:
#         blurred = cv2.GaussianBlur(region, (self.blur_size, self.blur_size), 0)
#         color_masks = self._build_color_masks(blurred)

#         # Store a combined debug mask
#         combined = None
#         for mask in color_masks.values():
#             combined = mask if combined is None else cv2.bitwise_or(combined, mask)
#         self.last_masks[cam_id] = combined

#         best_score = -1e9
#         best_detection = None

#         for color_name, mask in color_masks.items():
#             mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
#             mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, self.kernel)

#             contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#             for contour in contours:
#                 area = cv2.contourArea(contour)
#                 if area < self.min_area or area > self.max_area:
#                     continue

#                 score, center, area, bbox, brightness = self._score_candidate(
#                     contour, blurred, offset, cam_id
#                 )

#                 if score > best_score:
#                     best_score = score
#                     conf = min(1.0, 0.5 * (area / 20.0) + 0.5 * (brightness / 255.0))
#                     best_detection = Detection(
#                         found=True,
#                         center=center,
#                         area=area,
#                         bbox=bbox,
#                         confidence=float(conf),
#                         color=color_name,
#                     )

#         return best_detection

#     def _smooth_center(self, cam_id: int, new_center: Tuple[int, int]) -> Tuple[int, int]:
#         last_center = self.last_centers.get(cam_id)
#         if last_center is None:
#             return new_center

#         a = self.smoothing_alpha
#         sx = a * new_center[0] + (1.0 - a) * last_center[0]
#         sy = a * new_center[1] + (1.0 - a) * last_center[1]
#         return int(round(sx)), int(round(sy))

#     def detect(self, frame: np.ndarray, cam_id: int = 0) -> Detection:
#         if cam_id not in self.missed_frames:
#             self.missed_frames[cam_id] = 0

#         roi, offset, used_roi = self._get_roi(frame, cam_id)
#         detection = self._detect_in_region(roi, offset, cam_id)

#         if detection is None and used_roi:
#             detection = self._detect_in_region(frame, (0, 0), cam_id)

#         if detection is None:
#             self.missed_frames[cam_id] += 1

#             if (
#                 self.missed_frames[cam_id] <= self.max_missed_frames
#                 and self.last_centers.get(cam_id) is not None
#             ):
#                 last_center = self.last_centers[cam_id]
#                 last_area = self.last_areas.get(cam_id, 0.0) or 0.0
#                 return Detection(
#                     found=False,
#                     center=(int(last_center[0]), int(last_center[1])),
#                     area=last_area,
#                     bbox=None,
#                     confidence=0.0,
#                     color="predicted",
#                 )

#             self.last_centers[cam_id] = None
#             self.last_areas[cam_id] = None
#             return Detection(found=False, center=None, confidence=0.0, color="none")

#         self.missed_frames[cam_id] = 0

#         smoothed_center = self._smooth_center(cam_id, detection.center)
#         detection.center = smoothed_center

#         self.last_centers[cam_id] = (float(smoothed_center[0]), float(smoothed_center[1]))
#         self.last_areas[cam_id] = detection.area

#         return detection

#     def get_last_mask(self, cam_id: int) -> Optional[np.ndarray]:
#         return self.last_masks.get(cam_id)

#     def draw_detection(self, frame: np.ndarray, detection: Detection, cam_name: str) -> np.ndarray:
#         out = frame.copy()

#         cv2.putText(out, cam_name, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

#         if detection.center is not None:
#             cx, cy = detection.center
#             color = (0, 255, 0) if detection.found else (0, 165, 255)

#             cv2.circle(out, (cx, cy), 8, color, 2)
#             cv2.line(out, (cx - 12, cy), (cx + 12, cy), color, 2)
#             cv2.line(out, (cx, cy - 12), (cx, cy + 12), color, 2)

#             if detection.bbox is not None:
#                 x, y, w, h = detection.bbox
#                 cv2.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 2)

#             text = (
#                 f"{'FOUND' if detection.found else 'PREDICT'} "
#                 f"{detection.color} "
#                 f"area={detection.area:.1f} "
#                 f"conf={detection.confidence:.2f}"
#             )
#             cv2.putText(out, text, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
#         else:
#             cv2.putText(out, "LOST", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

#         return out


# def apply_camera_settings(cap: cv2.VideoCapture) -> None:
#     cap.set(cv2.CAP_PROP_AUTO_WB, 0)
#     cap.set(cv2.CAP_PROP_GAIN, 0)
#     cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
#     cap.set(cv2.CAP_PROP_EXPOSURE, -8)


# def open_camera(index: int, width: int = 1280, height: int = 720, fps: int = 30) -> cv2.VideoCapture:
#     cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
#     if not cap.isOpened():
#         cap = cv2.VideoCapture(index)

#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#     cap.set(cv2.CAP_PROP_FPS, fps)

#     apply_camera_settings(cap)
#     return cap


# def crop_cage_region(frame: np.ndarray, cam_id: int) -> Tuple[np.ndarray, Tuple[int, int]]:
#     h, w = frame.shape[:2]

#     if cam_id == 0:
#         y1 = int(0.42 * h)
#         y2 = int(0.92 * h)
#         x1 = int(0.18 * w)
#         x2 = int(0.82 * w)
#     else:
#         y1 = int(0.35 * h)
#         y2 = int(0.92 * h)
#         x1 = int(0.12 * w)
#         x2 = int(0.88 * w)

#     crop = frame[y1:y2, x1:x2]
#     return crop, (x1, y1)


# def add_offset_to_detection(detection: Detection, offset: Tuple[int, int]) -> Detection:
#     if detection.center is not None:
#         detection.center = (detection.center[0] + offset[0], detection.center[1] + offset[1])

#     if detection.bbox is not None:
#         x, y, w, h = detection.bbox
#         detection.bbox = (x + offset[0], y + offset[1], w, h)

#     return detection


# def draw_crop_box(frame: np.ndarray, offset: Tuple[int, int], crop_shape: Tuple[int, int, int]) -> np.ndarray:
#     out = frame.copy()
#     x1, y1 = offset
#     h, w = crop_shape[:2]
#     x2 = x1 + w
#     y2 = y1 + h
#     cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 255), 1)
#     return out


# def main():
#     cap0 = open_camera(0)
#     cap1 = open_camera(1)

#     if not cap0.isOpened():
#         raise RuntimeError("Could not open camera 0")
#     if not cap1.isOpened():
#         raise RuntimeError("Could not open camera 1")

#     detector = DroneLEDDetector(
#         min_area=1,
#         max_area=60,
#         blur_size=3,
#         morph_kernel_size=2,
#         roi_half_size=80,
#         max_missed_frames=6,
#         smoothing_alpha=0.7,
#         detect_blue=True,
#         detect_green=True,
#         detect_red=True,
#     )

#     while True:
#         ok0, frame0 = cap0.read()
#         ok1, frame1 = cap1.read()

#         if not ok0 or frame0 is None:
#             print("Warning: failed to read camera 0")
#             continue
#         if not ok1 or frame1 is None:
#             print("Warning: failed to read camera 1")
#             continue

#         crop0, offset0 = crop_cage_region(frame0, cam_id=0)
#         crop1, offset1 = crop_cage_region(frame1, cam_id=1)

#         det0 = detector.detect(crop0, cam_id=0)
#         det1 = detector.detect(crop1, cam_id=1)

#         det0 = add_offset_to_detection(det0, offset0)
#         det1 = add_offset_to_detection(det1, offset1)

#         vis0 = draw_crop_box(frame0, offset0, crop0.shape)
#         vis1 = draw_crop_box(frame1, offset1, crop1.shape)

#         vis0 = detector.draw_detection(vis0, det0, "Camera 0")
#         vis1 = detector.draw_detection(vis1, det1, "Camera 1")

#         if det0.center is not None:
#             cv2.putText(
#                 vis0,
#                 f"center={det0.center}",
#                 (10, 85),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (255, 255, 255),
#                 2,
#             )

#         if det1.center is not None:
#             cv2.putText(
#                 vis1,
#                 f"center={det1.center}",
#                 (10, 85),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (255, 255, 255),
#                 2,
#             )

#         mask0 = detector.get_last_mask(0)
#         mask1 = detector.get_last_mask(1)

#         cv2.imshow("Drone Detection - Camera 0", vis0)
#         cv2.imshow("Drone Detection - Camera 1", vis1)

#         if mask0 is not None:
#             cv2.imshow("Mask 0", mask0)
#         if mask1 is not None:
#             cv2.imshow("Mask 1", mask1)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord("q"):
#             break
#         elif key == ord("1"):
#             cap0.set(cv2.CAP_PROP_EXPOSURE, -10)
#             cap1.set(cv2.CAP_PROP_EXPOSURE, -10)
#             print("Exposure set to -10")
#         elif key == ord("2"):
#             cap0.set(cv2.CAP_PROP_EXPOSURE, -8)
#             cap1.set(cv2.CAP_PROP_EXPOSURE, -8)
#             print("Exposure set to -8")
#         elif key == ord("3"):
#             cap0.set(cv2.CAP_PROP_EXPOSURE, -6)
#             cap1.set(cv2.CAP_PROP_EXPOSURE, -6)
#             print("Exposure set to -6")

#     cap0.release()
#     cap1.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()
# import cv2
# import numpy as np
# from dataclasses import dataclass
# from typing import Optional, Tuple, Dict


# @dataclass
# class Detection:
#     found: bool
#     center: Optional[Tuple[int, int]]
#     area: float = 0.0
#     bbox: Optional[Tuple[int, int, int, int]] = None
#     confidence: float = 0.0
#     color: str = "unknown"


# class DroneLEDDetector:
#     def __init__(
#         self,
#         min_area: int = 1,
#         max_area: int = 60,
#         blur_size: int = 3,
#         morph_kernel_size: int = 2,
#         roi_half_size: int = 80,
#         max_missed_frames: int = 6,
#         smoothing_alpha: float = 0.7,
#         detect_blue: bool = True,
#         detect_green: bool = True,
#         detect_red: bool = True,
#     ):
#         self.min_area = min_area
#         self.max_area = max_area
#         self.blur_size = blur_size if blur_size % 2 == 1 else blur_size + 1
#         self.roi_half_size = roi_half_size
#         self.max_missed_frames = max_missed_frames
#         self.smoothing_alpha = smoothing_alpha

#         self.detect_blue = detect_blue
#         self.detect_green = detect_green
#         self.detect_red = detect_red

#         self.kernel = np.ones((morph_kernel_size, morph_kernel_size), np.uint8)

#         self.last_centers: Dict[int, Optional[Tuple[float, float]]] = {}
#         self.last_areas: Dict[int, Optional[float]] = {}
#         self.missed_frames: Dict[int, int] = {}
#         self.last_masks: Dict[int, Optional[np.ndarray]] = {}

#     def _get_roi(
#         self, frame: np.ndarray, cam_id: int
#     ) -> Tuple[np.ndarray, Tuple[int, int], bool]:
#         h, w = frame.shape[:2]
#         last_center = self.last_centers.get(cam_id)

#         if last_center is None:
#             return frame, (0, 0), False

#         cx, cy = int(last_center[0]), int(last_center[1])
#         hs = self.roi_half_size

#         x1 = max(0, cx - hs)
#         y1 = max(0, cy - hs)
#         x2 = min(w, cx + hs)
#         y2 = min(h, cy + hs)

#         if x2 <= x1 or y2 <= y1:
#             return frame, (0, 0), False

#         return frame[y1:y2, x1:x2], (x1, y1), True

#     def _build_color_masks(self, frame_bgr: np.ndarray) -> Dict[str, np.ndarray]:
#         """
#         Returns masks for blue, green, and red LEDs.
#         Uses BOTH HSV and channel-dominance logic.
#         """
#         hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
#         b, g, r = cv2.split(frame_bgr)
#         gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

#         masks: Dict[str, np.ndarray] = {}

#         # Shared brightness gate
#         _, bright_mask = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

#         if self.detect_green:
#             lower_green = np.array([40, 80, 80], dtype=np.uint8)
#             upper_green = np.array([90, 255, 255], dtype=np.uint8)
#             hsv_green = cv2.inRange(hsv, lower_green, upper_green)

#             g_excess = g.astype(np.int16) - ((r.astype(np.int16) + b.astype(np.int16)) // 2)
#             g_excess = np.clip(g_excess, 0, 255).astype(np.uint8)
#             _, g_dom = cv2.threshold(g_excess, 18, 255, cv2.THRESH_BINARY)

#             masks["green"] = cv2.bitwise_and(hsv_green, cv2.bitwise_and(g_dom, bright_mask))

#         if self.detect_blue:
#             lower_blue = np.array([90, 60, 60], dtype=np.uint8)
#             upper_blue = np.array([145, 255, 255], dtype=np.uint8)
#             hsv_blue = cv2.inRange(hsv, lower_blue, upper_blue)

#             b_excess = b.astype(np.int16) - ((r.astype(np.int16) + g.astype(np.int16)) // 2)
#             b_excess = np.clip(b_excess, 0, 255).astype(np.uint8)
#             _, b_dom = cv2.threshold(b_excess, 18, 255, cv2.THRESH_BINARY)

#             masks["blue"] = cv2.bitwise_and(hsv_blue, cv2.bitwise_and(b_dom, bright_mask))

#         if self.detect_red:
#             lower_red1 = np.array([0, 80, 80], dtype=np.uint8)
#             upper_red1 = np.array([12, 255, 255], dtype=np.uint8)
#             lower_red2 = np.array([170, 80, 80], dtype=np.uint8)
#             upper_red2 = np.array([179, 255, 255], dtype=np.uint8)

#             hsv_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
#             hsv_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
#             hsv_red = cv2.bitwise_or(hsv_red1, hsv_red2)

#             r_excess = r.astype(np.int16) - ((g.astype(np.int16) + b.astype(np.int16)) // 2)
#             r_excess = np.clip(r_excess, 0, 255).astype(np.uint8)
#             _, r_dom = cv2.threshold(r_excess, 18, 255, cv2.THRESH_BINARY)

#             masks["red"] = cv2.bitwise_and(hsv_red, cv2.bitwise_and(r_dom, bright_mask))

#         return masks

#     def _score_candidate(
#         self,
#         contour: np.ndarray,
#         region: np.ndarray,
#         offset: Tuple[int, int],
#         cam_id: int,
#     ) -> Tuple[float, Tuple[int, int], float, Tuple[int, int, int, int], float]:
#         area = cv2.contourArea(contour)
#         x, y, w, h = cv2.boundingRect(contour)

#         if area <= 0:
#             return -1e9, (0, 0), 0.0, (x, y, w, h), 0.0

#         cx_local = x + w // 2
#         cy_local = y + h // 2
#         cx = cx_local + offset[0]
#         cy = cy_local + offset[1]

#         patch = region[y:y + h, x:x + w]
#         if patch.size == 0:
#             brightness = 0.0
#         else:
#             brightness = float(np.mean(cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)))

#         aspect_ratio = max(w, h) / max(1, min(w, h))
#         shape_penalty = abs(aspect_ratio - 1.0)

#         last_center = self.last_centers.get(cam_id)
#         if last_center is None:
#             dist_penalty = 0.0
#         else:
#             dist = np.hypot(cx - last_center[0], cy - last_center[1])
#             dist_penalty = 0.05 * dist

#         last_area = self.last_areas.get(cam_id)
#         if last_area is None:
#             area_penalty = 0.0
#         else:
#             area_penalty = 0.08 * abs(area - last_area)

#         score = (
#             1.5 * area
#             + 0.7 * brightness
#             - 8.0 * shape_penalty
#             - dist_penalty
#             - area_penalty
#         )

#         return score, (cx, cy), area, (x + offset[0], y + offset[1], w, h), brightness

#     def _detect_in_region(
#         self, region: np.ndarray, offset: Tuple[int, int], cam_id: int
#     ) -> Optional[Detection]:
#         blurred = cv2.GaussianBlur(region, (self.blur_size, self.blur_size), 0)
#         color_masks = self._build_color_masks(blurred)

#         # Store a combined debug mask
#         combined = None
#         for mask in color_masks.values():
#             combined = mask if combined is None else cv2.bitwise_or(combined, mask)
#         self.last_masks[cam_id] = combined

#         best_score = -1e9
#         best_detection = None

#         for color_name, mask in color_masks.items():
#             mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
#             mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, self.kernel)

#             contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#             for contour in contours:
#                 area = cv2.contourArea(contour)
#                 if area < self.min_area or area > self.max_area:
#                     continue

#                 score, center, area, bbox, brightness = self._score_candidate(
#                     contour, blurred, offset, cam_id
#                 )

#                 if score > best_score:
#                     best_score = score
#                     conf = min(1.0, 0.5 * (area / 20.0) + 0.5 * (brightness / 255.0))
#                     best_detection = Detection(
#                         found=True,
#                         center=center,
#                         area=area,
#                         bbox=bbox,
#                         confidence=float(conf),
#                         color=color_name,
#                     )

#         return best_detection

#     def _smooth_center(self, cam_id: int, new_center: Tuple[int, int]) -> Tuple[int, int]:
#         last_center = self.last_centers.get(cam_id)
#         if last_center is None:
#             return new_center

#         a = self.smoothing_alpha
#         sx = a * new_center[0] + (1.0 - a) * last_center[0]
#         sy = a * new_center[1] + (1.0 - a) * last_center[1]
#         return int(round(sx)), int(round(sy))

#     def detect(self, frame: np.ndarray, cam_id: int = 0) -> Detection:
#         if cam_id not in self.missed_frames:
#             self.missed_frames[cam_id] = 0

#         roi, offset, used_roi = self._get_roi(frame, cam_id)
#         detection = self._detect_in_region(roi, offset, cam_id)

#         if detection is None and used_roi:
#             detection = self._detect_in_region(frame, (0, 0), cam_id)

#         if detection is None:
#             self.missed_frames[cam_id] += 1

#             if (
#                 self.missed_frames[cam_id] <= self.max_missed_frames
#                 and self.last_centers.get(cam_id) is not None
#             ):
#                 last_center = self.last_centers[cam_id]
#                 last_area = self.last_areas.get(cam_id, 0.0) or 0.0
#                 return Detection(
#                     found=False,
#                     center=(int(last_center[0]), int(last_center[1])),
#                     area=last_area,
#                     bbox=None,
#                     confidence=0.0,
#                     color="predicted",
#                 )

#             self.last_centers[cam_id] = None
#             self.last_areas[cam_id] = None
#             return Detection(found=False, center=None, confidence=0.0, color="none")

#         self.missed_frames[cam_id] = 0

#         smoothed_center = self._smooth_center(cam_id, detection.center)
#         detection.center = smoothed_center

#         self.last_centers[cam_id] = (float(smoothed_center[0]), float(smoothed_center[1]))
#         self.last_areas[cam_id] = detection.area

#         return detection

#     def get_last_mask(self, cam_id: int) -> Optional[np.ndarray]:
#         return self.last_masks.get(cam_id)

#     def draw_detection(self, frame: np.ndarray, detection: Detection, cam_name: str) -> np.ndarray:
#         out = frame.copy()

#         cv2.putText(out, cam_name, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

#         if detection.center is not None:
#             cx, cy = detection.center
#             color = (0, 255, 0) if detection.found else (0, 165, 255)

#             cv2.circle(out, (cx, cy), 8, color, 2)
#             cv2.line(out, (cx - 12, cy), (cx + 12, cy), color, 2)
#             cv2.line(out, (cx, cy - 12), (cx, cy + 12), color, 2)

#             if detection.bbox is not None:
#                 x, y, w, h = detection.bbox
#                 cv2.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 2)

#             text = (
#                 f"{'FOUND' if detection.found else 'PREDICT'} "
#                 f"{detection.color} "
#                 f"area={detection.area:.1f} "
#                 f"conf={detection.confidence:.2f}"
#             )
#             cv2.putText(out, text, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
#         else:
#             cv2.putText(out, "LOST", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

#         return out


# def apply_camera_settings(cap: cv2.VideoCapture) -> None:
#     cap.set(cv2.CAP_PROP_AUTO_WB, 0)
#     cap.set(cv2.CAP_PROP_GAIN, 0)
#     cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
#     cap.set(cv2.CAP_PROP_EXPOSURE, -8)


# def open_camera(index: int, width: int = 1280, height: int = 720, fps: int = 30) -> cv2.VideoCapture:
#     cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
#     if not cap.isOpened():
#         cap = cv2.VideoCapture(index)

#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#     cap.set(cv2.CAP_PROP_FPS, fps)

#     apply_camera_settings(cap)
#     return cap


# def crop_cage_region(frame: np.ndarray, cam_id: int) -> Tuple[np.ndarray, Tuple[int, int]]:
#     h, w = frame.shape[:2]

#     if cam_id == 0:
#         y1 = int(0.42 * h)
#         y2 = int(0.92 * h)
#         x1 = int(0.18 * w)
#         x2 = int(0.82 * w)
#     else:
#         y1 = int(0.35 * h)
#         y2 = int(0.92 * h)
#         x1 = int(0.12 * w)
#         x2 = int(0.88 * w)

#     crop = frame[y1:y2, x1:x2]
#     return crop, (x1, y1)


# def add_offset_to_detection(detection: Detection, offset: Tuple[int, int]) -> Detection:
#     if detection.center is not None:
#         detection.center = (detection.center[0] + offset[0], detection.center[1] + offset[1])

#     if detection.bbox is not None:
#         x, y, w, h = detection.bbox
#         detection.bbox = (x + offset[0], y + offset[1], w, h)

#     return detection


# def draw_crop_box(frame: np.ndarray, offset: Tuple[int, int], crop_shape: Tuple[int, int, int]) -> np.ndarray:
#     out = frame.copy()
#     x1, y1 = offset
#     h, w = crop_shape[:2]
#     x2 = x1 + w
#     y2 = y1 + h
#     cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 255), 1)
#     return out


# def main():
#     cap0 = open_camera(0)
#     cap1 = open_camera(1)

#     if not cap0.isOpened():
#         raise RuntimeError("Could not open camera 0")
#     if not cap1.isOpened():
#         raise RuntimeError("Could not open camera 1")

#     detector = DroneLEDDetector(
#         min_area=1,
#         max_area=60,
#         blur_size=3,
#         morph_kernel_size=2,
#         roi_half_size=80,
#         max_missed_frames=6,
#         smoothing_alpha=0.7,
#         detect_blue=True,
#         detect_green=True,
#         detect_red=True,
#     )

#     while True:
#         ok0, frame0 = cap0.read()
#         ok1, frame1 = cap1.read()

#         if not ok0 or frame0 is None:
#             print("Warning: failed to read camera 0")
#             continue
#         if not ok1 or frame1 is None:
#             print("Warning: failed to read camera 1")
#             continue

#         crop0, offset0 = crop_cage_region(frame0, cam_id=0)
#         crop1, offset1 = crop_cage_region(frame1, cam_id=1)

#         det0 = detector.detect(crop0, cam_id=0)
#         det1 = detector.detect(crop1, cam_id=1)

#         det0 = add_offset_to_detection(det0, offset0)
#         det1 = add_offset_to_detection(det1, offset1)

#         vis0 = draw_crop_box(frame0, offset0, crop0.shape)
#         vis1 = draw_crop_box(frame1, offset1, crop1.shape)

#         vis0 = detector.draw_detection(vis0, det0, "Camera 0")
#         vis1 = detector.draw_detection(vis1, det1, "Camera 1")

#         if det0.center is not None:
#             cv2.putText(
#                 vis0,
#                 f"center={det0.center}",
#                 (10, 85),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (255, 255, 255),
#                 2,
#             )

#         if det1.center is not None:
#             cv2.putText(
#                 vis1,
#                 f"center={det1.center}",
#                 (10, 85),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (255, 255, 255),
#                 2,
#             )

#         mask0 = detector.get_last_mask(0)
#         mask1 = detector.get_last_mask(1)

#         cv2.imshow("Drone Detection - Camera 0", vis0)
#         cv2.imshow("Drone Detection - Camera 1", vis1)

#         if mask0 is not None:
#             cv2.imshow("Mask 0", mask0)
#         if mask1 is not None:
#             cv2.imshow("Mask 1", mask1)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord("q"):
#             break
#         elif key == ord("1"):
#             cap0.set(cv2.CAP_PROP_EXPOSURE, -10)
#             cap1.set(cv2.CAP_PROP_EXPOSURE, -10)
#             print("Exposure set to -10")
#         elif key == ord("2"):
#             cap0.set(cv2.CAP_PROP_EXPOSURE, -8)
#             cap1.set(cv2.CAP_PROP_EXPOSURE, -8)
#             print("Exposure set to -8")
#         elif key == ord("3"):
#             cap0.set(cv2.CAP_PROP_EXPOSURE, -6)
#             cap1.set(cv2.CAP_PROP_EXPOSURE, -6)
#             print("Exposure set to -6")

#     cap0.release()
#     cap1.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()
