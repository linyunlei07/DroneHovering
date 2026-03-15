"""
just a test file to see if our cameras work, detect feed, etc.

camera 1 = 0    => black
camera 1 = 1    => this is the laptop 
camera 2 = 2
"""


import cv2

def run_test():

    cap0 = cv2.VideoCapture(0)
    cap1 = cv2.VideoCapture(1)
    cap2 = cv2.VideoCapture(2)

    print("Checking cameras... Press 'q' to exit.")

    while True:
        # Read frames from all possible cameras
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()
        ##ret2, frame2 = cap2.read() 

        if ret0: cv2.imshow("Camera 0", frame0)
        if ret1: cv2.imshow("Camera 1", frame1)
        ##if ret2: cv2.imshow("Camera 2", frame2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap0.release()
    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_test()