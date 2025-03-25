from ETS2LA.Controls import ControlEvent
from ETS2LA.UI import SendPopup
import multiprocessing
import keyboard
import queue
import time
import os

def distance(a: float, b: float):
    return abs(a - b)

def keyboard_callback(e):
    global new_guid
    global new_key
    if e.event_type == keyboard.KEY_DOWN:
        new_key = e.name
        new_guid = "keyboard"

def control_picker(event: ControlEvent, controller_queue: multiprocessing.Queue) -> tuple[str, str]:
    """Pick a control for the given control event.

    :param ControlEvent event: The control event to pick a control for.
    :param multiprocessing.Queue controller_queue: The queue to listen for control events on.
    :return tuple[str, str]: new guid, new key
    """
    global new_guid
    global new_key
    
    while controller_queue.empty():
        time.sleep(0.01)
        pass
    
    start_values = controller_queue.get()
    is_button = event.type == "button"
    if is_button:
        print("Keyboard listener is loading...")
        keyboard.hook(keyboard_callback)
        print("Keyboard listener loaded.")
    
    start_time = time.perf_counter()
    new_guid = ""
    new_key = ""
    while new_key == "" and time.perf_counter() - start_time < 10:
        time.sleep(0.01)
        if not controller_queue.empty():
            data = controller_queue.get()
            for guid, values in data.items():
                if new_key != "":
                    break
                for key, value in values.items():
                    if "button" in key and value != start_values[guid][key] and is_button:
                        new_key = key
                        new_guid = guid
                        break
                    
                    if "axis" in key and distance(start_values[guid][key], value) > 0.1 and not is_button:
                        new_key = key
                        new_guid = guid
                        break
    
    if new_key == "":
        SendPopup("Timeout, please try again.", "error")
        return "", ""
    
    name = "Keyboard key" if new_guid == "keyboard" else start_values[new_guid]["name"]
    SendPopup("Event bound to " + name + " " + new_key, "success")
    return new_guid, new_key