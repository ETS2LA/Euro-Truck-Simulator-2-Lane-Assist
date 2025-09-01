from ETS2LA.Handlers.utils.key_mappings import key_to_str
from pynput import keyboard as pynput_keyboard
from ETS2LA.Controls import ControlEvent
from ETS2LA.Utils.translator import _
from ETS2LA.UI import SendPopup
import multiprocessing
import time

new_guid = ""
new_key = ""


def keyboard_callback(key):
    global new_guid
    global new_key
    try:
        new_key = key_to_str(key)
    except AttributeError:
        new_key = str(key)
    new_guid = "keyboard"


listener = pynput_keyboard.Listener(on_press=keyboard_callback)
listener.start()


def distance(a: float, b: float):
    return abs(a - b)


def control_picker(
    event: ControlEvent, controller_queue: multiprocessing.Queue
) -> tuple[str, str]:
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

    new_guid = ""
    new_key = ""

    start_time = time.perf_counter()
    while new_key == "" and time.perf_counter() - start_time < 10:
        time.sleep(0.01)
        if not controller_queue.empty():
            data = controller_queue.get()
            for guid, values in data.items():
                if new_key != "":
                    break
                for key, value in values.items():
                    if (
                        "button" in key
                        and value != start_values[guid][key]
                        and is_button
                    ):
                        new_key = key
                        new_guid = guid
                        break

                    if (
                        "axis" in key
                        and distance(start_values[guid][key], value) > 0.1
                        and not is_button
                    ):
                        new_key = key
                        new_guid = guid
                        break

    if new_key == "":
        SendPopup(_("Timeout, please try again."), "error")
        return "", ""

    name = "Keyboard key" if new_guid == "keyboard" else start_values[new_guid]["name"]
    SendPopup(
        _("Event bound to {device} {action}").format(
            device=name, action=new_key.capitalize().replace("_", " ")
        ),
        "success",
    )
    return new_guid, new_key
