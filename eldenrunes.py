import time
import json
import threading
import sys
from pynput import keyboard, mouse
import pygame

# Initialize pygame
pygame.init()

# Initialize game variables
grid = [[0] * 4 for _ in range(4)]
score = 0

class InputRecorder:
    def __init__(self):
        self.inputs = []
        self.recording = False
        self.playing = False
        self.looping = False
        self.start_time = None
        self.playback_thread = None

    def start_recording(self):
        self.inputs = []
        self.recording = True
        self.start_time = time.time()
        print("Recording started...")

    def stop_recording(self):
        self.recording = False
        print("Recording stopped.")

    def save_recording(self, filename="recording.json"):
        # Convert KeyCode and Button objects to their string representations
        for input_event in self.inputs:
            if input_event["key"] is not None:
                input_event["key"] = str(input_event["key"])
            if input_event["button"] is not None:
                input_event["button"] = str(input_event["button"])
        with open(filename, "w") as f:
            json.dump(self.inputs, f)
        print(f"Recording saved to {filename}.")

    def load_recording(self, filename="recording.json"):
        with open(filename, "r") as f:
            self.inputs = json.load(f)
        # Convert string representations back to KeyCode and Button objects
        for input_event in self.inputs:
            if input_event["key"] is not None:
                input_event["key"] = keyboard.KeyCode.from_char(input_event["key"].strip("'"))
            if input_event["button"] is not None:
                input_event["button"] = getattr(mouse.Button, input_event["button"].split('.')[-1])
        print(f"Recording loaded from {filename}.")

    def record_input(self, input_type, event_type, key=None, pos=None, button=None, value=None):
        if self.recording:
            timestamp = time.time() - self.start_time
            self.inputs.append({
                "timestamp": timestamp,
                "type": input_type,
                "event_type": event_type,
                "key": key,
                "pos": pos,
                "button": button,
                "value": value
            })

    def playback(self):
        self.playing = True
        print("Playback started.")
        while self.playing:
            start_time = time.time()
            for input_event in self.inputs:
                if not self.playing:
                    break
                print(f"Processing event: {input_event}")
                time.sleep(max(0, input_event["timestamp"] - (time.time() - start_time)))
                if input_event["type"] == "keyboard":
                    if input_event["event_type"] == "press":
                        keyboard_controller.press(input_event["key"])
                    elif input_event["event_type"] == "release":
                        keyboard_controller.release(input_event["key"])
                elif input_event["type"] == "mouse":
                    if input_event["event_type"] == "click":
                        mouse_controller.click(input_event["button"], 1)
                    elif input_event["event_type"] == "move":
                        mouse_controller.position = input_event["pos"]
                elif input_event["type"] == "controller":
                    # Handle controller input playback
                    pass
            if not self.looping:
                break
            else:
                time.sleep(1)  # Adding delay between loops
        print("Playback stopped.")

    def start_playback(self, loop=False):
        if not self.playing:
            self.looping = loop
            self.playback_thread = threading.Thread(target=self.playback)
            self.playback_thread.start()

    def stop_playback(self):
        self.playing = False
        if self.playback_thread:
            self.playback_thread.join()
        print("Playback stopped.")
        self.looping = False

class XboxController:
    def __init__(self, recorder):
        pygame.init()
        pygame.joystick.init()
        self.recorder = recorder
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.listen).start()

    def stop(self):
        self.running = False

    def listen(self):
        while self.running:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    self.recorder.record_input("controller", "press", value=event.button)
                elif event.type == pygame.JOYBUTTONUP:
                    self.recorder.record_input("controller", "release", value=event.button)
                elif event.type == pygame.JOYAXISMOTION:
                    self.recorder.record_input("controller", "axis", value=(event.axis, event.value))
            time.sleep(0.01)

recorder = InputRecorder()
keyboard_controller = keyboard.Controller()
mouse_controller = mouse.Controller()
xbox_controller = XboxController(recorder)

def on_press(key):
    try:
        if key.char == 't':
            recorder.start_recording()
        elif key.char == 'y':
            recorder.stop_recording()
            recorder.save_recording()
        elif key.char == 'u':
            if not recorder.playing:
                recorder.load_recording()
                recorder.start_playback(loop=False)
        elif key.char == 'i':
            if not recorder.playing:
                recorder.load_recording()
                recorder.start_playback(loop=True)
        elif key.char == 'o':
            recorder.stop_playback()
        elif key.char == '\\':
            stop_program()
        else:
            recorder.record_input("keyboard", "press", key=key)
    except AttributeError:
        recorder.record_input("keyboard", "press", key=key)

def on_release(key):
    recorder.record_input("keyboard", "release", key=key)

def on_click(x, y, button, pressed):
    if pressed:
        recorder.record_input("mouse", "click", pos=(x, y), button=button)
    else:
        recorder.record_input("mouse", "release", pos=(x, y), button=button)

def on_move(x, y):
    recorder.record_input("mouse", "move", pos=(x, y))

keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)

def stop_program():
    xbox_controller.stop()
    keyboard_listener.stop()
    mouse_listener.stop()
    pygame.quit()
    print("Program terminated.")
    sys.exit()

def main():
    xbox_controller.start()
    keyboard_listener.start()
    mouse_listener.start()

    print("Keybinds:")
    print("  't' to start recording")
    print("  'y' to stop recording and save")
    print("  'u' to playback once")
    print("  'i' to loop playback until 'o' is pressed")
    print("  'o' to stop playback")
    print("  '\\' to quit the program")

    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
