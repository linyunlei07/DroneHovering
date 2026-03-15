"""
test to see if laptop can connect to drone, through the blingink of"""


# led_test.py
import drone_comm as drone
import time

def test_connection():
    print("Testing connection to ESP32-S2...")
    try:
        # 1. Turn on Blue LED (Ready Signal)
        drone.blue_LED(1)
        print("Blue LED ON")
        time.sleep(1)

        drone.blue_LED(0)
        print("Blue LED OFF")
        time.sleep(1)

        drone.blue_LED(1)
        print("Blue LED ON")
        time.sleep(1)

        drone.blue_LED(0)
        print("Blue LED OFF")
        time.sleep(1)
    


        # 2. Turn on Green LED
        drone.green_LED(1)
        print("Green LED ON")
        time.sleep(1)
        



        # 3. Emergency Stop (Resets to Mode 0)
        drone.emergency_stop() 
        print("Emergency Stop triggered. Lights should reset.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()