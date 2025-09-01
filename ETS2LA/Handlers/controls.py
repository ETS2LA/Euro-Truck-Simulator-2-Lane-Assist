"""
This file handles control inputs from users. It contains the
updating of joystick information as well as the editing
of control events.

It is mostly called from the plugins handler, where the information
for each plugin's events is going to be piped through a queue.

NOTE: If you are using controls from a plugin, DO NOT import this file.
      Instead you should create the `ControlEvent`(s) and assign them to the
      plugin with the `controls` attribute.
"""

from ETS2LA.Handlers.utils.key_mappings import key_to_str
from ETS2LA.Controls.picker import control_picker
from ETS2LA.Utils.translator import _
from ETS2LA.Controls import ControlEvent
import ETS2LA.Utils.settings as settings
from ETS2LA.UI import SendPopup

import multiprocessing
import threading

from pynput import keyboard as pynput_keyboard

import logging
import time
import os

settings_file = "ETS2LA/controls.json"
"""
The settings file to use when saving and editing the controls.
"""

joysticks = {}
"""
This variable will be update with the state of the joysticks
every 50ms.
"""

event_information = {}
"""
This variable will store information for all events.
It will be updated as any information changes.
"""

queue = multiprocessing.Queue()
"""
The multiprocessing queue that the joystick update process
will use to output the current values from joysticks.
"""

pause_queue_listener = False
"""
Whether to pause the queue listener to hijack the queue
output with another process.
"""


pressed_keys = set()


def on_press(key):
    key_str = key_to_str(key)
    pressed_keys.add(key_str)


def on_release(key):
    key_str = key_to_str(key)
    pressed_keys.discard(key_str)


listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()


def get_event_information_dictionary() -> dict:
    return event_information


def joystick_update_process(joystick_queue: multiprocessing.Queue) -> None:
    """This is the main joystick update process. It will listen
    to joystick events and send the joystick state out every 50ms.

    :param multiprocessing.Queue joystick_queue: The queue to send
                                                 the joystick state to.
    """
    from ETS2LA.Utils.Console.logging import setup_global_logging

    setup_global_logging(write_file=False)
    import pygame

    pygame.init()
    pygame.joystick.init()

    joystick_objects = []
    last_count = pygame.joystick.get_count()
    state = {}

    def load_joysticks(count: int):
        logging.info(_("Refreshing joysticks..."))
        joystick_objects.clear()
        old_state = state.copy()
        state.clear()

        for i in range(count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

            name = joystick.get_name()
            if name.startswith("("):
                name = name[1:]
            if name.endswith(")"):
                name = name[:-1]
            SendPopup(_("{} connected.").format(name))
            logging.info(
                _("Found joystick: [bold]{name}[/bold] [dim]({uid})[/dim]").format(
                    name=name, uid=joystick.get_guid()
                )
            )
            joystick_objects.append(joystick)
            state[joystick.get_guid()] = {}

        not_found = [
            guid
            for guid in old_state
            if guid not in [j.get_guid() for j in joystick_objects]
        ]
        names = [old_state[guid]["name"] for guid in not_found]
        for name in names:
            SendPopup(_("{} disconnected.").format(name), "warning")
            logging.info(_("{} disconnected.").format(name))

    load_joysticks(last_count)

    while True:
        pygame.event.pump()
        if pygame.joystick.get_count() != last_count:
            load_joysticks(pygame.joystick.get_count())
            last_count = pygame.joystick.get_count()

        for joystick in joystick_objects:
            name = joystick.get_name()
            if name.startswith("("):
                name = name[1:]
            if name.endswith(")"):
                name = name[:-1]

            state[joystick.get_guid()]["name"] = name

            for j in range(joystick.get_numbuttons()):
                value = joystick.get_button(j)
                state[joystick.get_guid()][f"button_{j}"] = value

            for j in range(joystick.get_numaxes()):
                value = joystick.get_axis(j)
                state[joystick.get_guid()][f"axis_{j}"] = value

        joystick_queue.put(state)
        pygame.time.wait(50)  # 20 fps


def queue_listener_thread(joystick_queue: multiprocessing.Queue) -> None:
    """This thread will listen to the joystick state updates and
    update the global joysticks variable.

    :param multiprocessing.Queue joystick_queue: The queue to listen to.
    """
    global joysticks
    global pause_queue_listener

    while True:
        while pause_queue_listener:
            time.sleep(0.5)

        try:
            state = joystick_queue.get(block=False)
        except Exception:
            time.sleep(0.025)  # 40 fps
            continue

        joysticks = state


def event_information_update(once: bool = False) -> None:
    """This thread will check the modified time of the
    settings file. If the modified time doesn't match then
    it will update the event_information variable.

    You can also call with `once=True` to only run once.
    """
    global event_information
    last_modify_time = 0

    if not os.path.exists(settings_file):
        with open(settings_file, "w") as f:
            f.write("{}")

    while True:
        if os.path.getmtime(settings_file) != last_modify_time:
            event_information = settings.GetJSON(settings_file)
            last_modify_time = os.path.getmtime(settings_file)

        if once:
            break

        time.sleep(1)


def save_event_information(
    label: str,
    guid: str,
    key: str,
    type: str,
    name: str,
    description: str,
    device: str,
    plugin: str,
) -> None:
    """This function will save the event information for a given
    event.

    :param str label: The label of the event.
    :param str guid: The guid of the joystick.
    :param str key: The key of the event.
    :param str type: The type of the event.
    :param str name: The name of the event.
    :param str description: The description of the event.
    :param str device: The device name of the event.
    :param str plugin: The plugin name of the event.
    """
    settings.Set(
        settings_file,
        label,
        {
            "guid": guid,
            "key": key,
            "type": type,
            "name": name,
            "description": description,
            "device": device,
            "plugin": plugin,
        },
    )

    event_information_update(once=True)


def get_event_information(event: ControlEvent) -> dict:
    """This function will return the information for
    a given event. This information can change as time goes on.

    :param ControlEvent event: The event to get the information for.
    :return dict: The return dictionary.
    """
    if event.alias not in event_information:
        if event.default != "":
            save_event_information(
                event.alias,
                "keyboard",
                event.default,
                event.type,
                event.name,
                event.description,
                "Keyboard",
                event.plugin,
            )
            return {
                "guid": "keyboard",
                "key": event.default,
                "type": event.type,
                "name": event.name,
                "description": event.description,
                "plugin": event.plugin,
            }

        save_event_information(
            event.alias,
            "",
            "",
            event.type,
            event.name,
            event.description,
            "",
            event.plugin,
        )
        return {
            "guid": "",
            "key": "",
            "type": event.type,
            "name": event.name,
            "description": event.description,
            "plugin": event.plugin,
        }

    return event_information[event.alias]


def load_event_from_alias(alias: str) -> ControlEvent:
    """This function will load an event from the alias.

    :param str alias: The alias of the event.
    :return ControlEvent: The event object.
    """
    if alias not in event_information:
        raise ValueError(_("Event with alias '{0}' not found.").format(alias))

    info = event_information[alias]
    return ControlEvent(
        alias,
        info["name"],
        info["type"],
        info["description"],
        info["key"],
        info["plugin"] if "plugin" in info else "",
    )


def validate_events(events: list[ControlEvent]) -> None:
    """Validate that the control events have their information
    already in the settings file. If not, then save it now.

    :param list[ControlEvent] events: List of events to validate.
    """
    event_information_update(once=True)
    for event in events:
        get_event_information(event)


def get_states(events: list[ControlEvent]) -> dict:
    """This function has been rewritten to support the pynput.

    :parma list[ControlEvent] events: input event.
    :return dict: The return dictionary.
    """

    states = {}
    for event in events:
        info = get_event_information(event)
        if info["guid"] == "keyboard":
            key = info["key"]
            states[event.alias] = key in pressed_keys
            continue

        if info["guid"] == "keyboard":
            key = info["key"]
            if len(key) == 1:
                states[event.alias] = key in pressed_keys
            else:
                states[event.alias] = (
                    getattr(pynput_keyboard.Key, key, None) in pressed_keys
                )
            continue

        if event.type == "button":
            if info["guid"] not in joysticks:
                states[event.alias] = False
                continue
            states[event.alias] = joysticks[info["guid"]][f"{info['key']}"]

        elif event.type == "axis":
            if info["guid"] not in joysticks:
                states[event.alias] = 0
                continue

            states[event.alias] = joysticks[info["guid"]][f"{info['key']}"]

    return states


def edit_event(event: ControlEvent | str) -> None:
    """
    Edit an event by asking the user for a new keybind
    to use for the event.

    :param ControlEvent | str event: The event to edit.
    """
    global pause_queue_listener
    pause_queue_listener = True

    if isinstance(event, str):
        try:
            event = load_event_from_alias(event)
        except ValueError:
            logging.error(_("Event with alias '{0}' not found.").format(event))
            return

    try:
        new_guid, new_key = control_picker(event, queue)
        device_name = (
            joysticks[new_guid]["name"]
            if new_guid != "" and new_guid != "keyboard"
            else "Keyboard"
        )
        if new_guid == "":
            save_event_information(
                event.alias,
                "",
                "",
                event.type,
                event.name,
                event.description,
                device_name,
                event.plugin,
            )
        else:
            save_event_information(
                event.alias,
                new_guid,
                new_key,
                event.type,
                event.name,
                event.description,
                device_name,
                event.plugin,
            )
    except Exception:
        logging.exception(_("Exception occurred while trying to edit the event."))

    pause_queue_listener = False


def unbind_event(event: ControlEvent | str) -> None:
    """
    Unbind an event by setting the guid to an empty string.

    :param ControlEvent | str event: The event to unbind.
    """
    if isinstance(event, str):
        try:
            event = load_event_from_alias(event)
        except ValueError:
            logging.error(_("Event with alias '{0}' not found.").format(event))
            return

    save_event_information(
        event.alias, "", "", event.type, event.name, event.description, "", event.plugin
    )


def run():
    # Initialize the control listener.
    multiprocessing.Process(
        target=joystick_update_process, args=(queue,), daemon=True
    ).start()
    threading.Thread(target=queue_listener_thread, args=(queue,), daemon=True).start()

    # Start the event information update thread.
    threading.Thread(target=event_information_update, daemon=True).start()

    logging.info(_("Controls listener started."))
