# # This handles the OpenCV logic and calculates how much the drone should lean.


# import cv2
# import socket
# import numpy as np

# # Connection to Drone
# UDP_IP = "192.168.4.1"
# UDP_PORT = 1234
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # External Cameras
# cam_front = cv2.VideoCapture(0) # Logic for X (Left/Right)
# cam_side = cv2.VideoCapture(1)  # Logic for Y (Depth)

# def find_drone_center(frame):
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     # Target: Bright Green LED/Marker
#     mask = cv2.inRange(hsv, (35, 100, 100), (85, 255, 255))
#     contours, _ = cv2.find_contours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     if contours:
#         best_cnt = max(contours, key=cv2.contourArea)
#         M = cv2.moments(best_cnt)
#         if M["m00"] > 0:
#             return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
#     return None

# while True:
#     _, frame_f = cam_front.read()
#     pos_f = find_drone_center(frame_f)
    
#     throttle = 600 # Base hover power (Tuned in Slot 1)
#     roll_adjustment = 0
    
#     if pos_f:
#         center_x = frame_f.shape[1] // 2
#         error_x = center_x - pos_f[0]
#         roll_adjustment = error_x * 0.7 # P-Gain
        
#     # Send to ESP32
#     packet = f"{throttle},{roll_adjustment}".encode()
#     sock.sendto(packet, (UDP_IP, UDP_PORT))

#     cv2.imshow('Brain View', frame_f)
#     if cv2.waitKey(1) & 0xFF == ord('q'): break