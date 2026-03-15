import time
from pynput import keyboard

def on_press(key):
    try:
        # For letters (w, a, s, d)
        print(f'Alphanumeric key pressed: {key.char}')
    except AttributeError:
        # For special keys (Arrows, Shift, etc.)
        print(f'Special key pressed: {key}')

def on_release(key):
    if key == keyboard.Key.esc:
        print("Exiting...")
        return False  # Stops the listener

# 1. Start the listener in a non-blocking way
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

print("--- KEYBOARD TEST ACTIVE ---")
print("1. Click inside this terminal window.")
print("2. Press WASD or Arrow keys.")
print("3. Press 'ESC' to stop.")

try:
    # 2. Keep the main script running so the listener has time to work
    while listener.running:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nManual stop.")
finally:
    listener.stop()
