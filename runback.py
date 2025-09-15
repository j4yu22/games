"""
Simple gamepad and keyboard input recorder/playback utility.

Records Xbox controller and keyboard inputs (even when PowerShell is not focused),
triggered by keys 8, 9, and 0.

Parameters:
    None

Returns:
    None
"""

import time
import threading
from inputs import get_gamepad, devices
import keyboard

recorded_events = []
recording = False
start_time = None


def read_gamepad():
    """
    Continuously reads gamepad events during recording and stores them with timestamps.

    Parameters:
        None

    Returns:
        None
    """
    global recording, start_time, recorded_events
    while recording:
        try:
            events = get_gamepad()
            now = time.time() - start_time
            for event in events:
                recorded_events.append(('gamepad', event.ev_type, event.code, event.state, now))
        except Exception as e:
            print("Gamepad read error:", e)
        time.sleep(0.01)  # Poll every 10ms


def read_keyboard():
    """
    Records keyboard key presses/releases with timestamps.

    Parameters:
        None

    Returns:
        None
    """
    global start_time

    def handler(event):
        if recording:
            now = time.time() - start_time
            recorded_events.append(('keyboard', event.event_type, event.name, None, now))

    keyboard.hook(handler)


"""
Starts recording both keyboard and controller inputs.

Parameters:
    None

Returns:
    None
"""
def start_recording():
    global recording, recorded_events, start_time
    print("Recording started...")
    recorded_events = []
    start_time = time.time()
    recording = True

    # Start gamepad thread
    threading.Thread(target=read_gamepad, daemon=True).start()


"""
Stops the recording session.

Parameters:
    None

Returns:
    None
"""
def stop_recording():
    global recording
    recording = False
    print("Recording stopped. {} events captured.".format(len(recorded_events)))


"""
Plays back recorded input events (keyboard only unless vjoy configured).

Parameters:
    None

Returns:
    None
"""
def playback():
    if not recorded_events:
        print("No input recorded.")
        return

    print("Playback started...")
    for i, event in enumerate(recorded_events):
        device_type, ev_type, code, value, timestamp = event
        delay = 0
        if i > 0:
            delay = timestamp - recorded_events[i - 1][4]
        time.sleep(delay)

        if device_type == 'keyboard':
            if ev_type == 'down':
                keyboard.press(code)
            elif ev_type == 'up':
                keyboard.release(code)
        elif device_type == 'gamepad':
            # Controller playback not implemented (requires vJoy setup)
            print(f"[Simulate Gamepad] {ev_type}: {code} = {value}")
    print("Playback finished.")


"""
Main control loop using 8, 9, and 0 keys.

Parameters:
    None

Returns:
    None
"""
def main():
    read_keyboard()  # Hook keyboard globally
    print("Press 8 to start recording, 9 to stop, 0 to playback.")

    while True:
        if keyboard.is_pressed('8') and not recording:
            start_recording()
            time.sleep(1)
        elif keyboard.is_pressed('9') and recording:
            stop_recording()
            time.sleep(1)
        elif keyboard.is_pressed('0') and not recording:
            playback()
            time.sleep(1)


if __name__ == "__main__":
    main()
