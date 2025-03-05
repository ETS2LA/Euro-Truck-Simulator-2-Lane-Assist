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

from ETS2LA.Utils.translator import Translate
from ETS2LA.Controls import ControlEvent
import ETS2LA.Utils.settings as settings

import multiprocessing
import threading

import keyboard

import logging
import time
import sys
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


def joystick_update_process(joystick_queue: multiprocessing.Queue) -> None:
    """This is the main joystick update process. It will listen
    to joystick events and send the joystick state out every 50ms.

    :param multiprocessing.Queue joystick_queue: The queue to send 
                                                 the joystick state to.
    """     
    from ETS2LA.Utils.Console.logging import setup_global_logging
    setup_global_logging(write_file=False)
    import pygame
    
    joystick_objects = []
    state = {}
    
    pygame.init()
    pygame.joystick.init()
    
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        logging.info(f"Found joystick: {joystick.get_name()[1:-1]} ({joystick.get_guid()})")
        joystick_objects.append(joystick)
        state[joystick.get_guid()] = {}
        
    while True:
        pygame.event.pump()
        for joystick in joystick_objects:
            for j in range(joystick.get_numbuttons()):
                value = joystick.get_button(j)
                state[joystick.get_guid()][f"button_{j}"] = value
                
            for j in range(joystick.get_numaxes()):
                value = joystick.get_axis(j)
                state[joystick.get_guid()][f"axis_{j}"] = value
            
        joystick_queue.put(state)
        pygame.time.wait(50) # 20 fps
    
    
def queue_listener_thread(joystick_queue: multiprocessing.Queue) -> None:
    """This thread will listen to the joystick state updates and
    update the global joysticks variable.

    :param multiprocessing.Queue joystick_queue: The queue to listen to.
    """
    global joysticks
    while True:
        try:
            state = joystick_queue.get(block=False)
        except:
            time.sleep(0.025) # 40 fps
            continue
        
        joysticks = state


def event_information_update_thread() -> None:
    """This thread will check the modified time of the
    settings file. If the modified time doesn't match then
    it will update the event_information variable.
    """
    global event_information
    last_modify_time = 0
    while True:
        if os.path.getmtime(settings_file) != last_modify_time:
            event_information = settings.GetJSON(settings_file)
            last_modify_time = os.path.getmtime(settings_file)
        
        time.sleep(1)


def get_event_information(event: ControlEvent) -> dict:
    """This function will return the information for 
    a given event. This information can change as time goes on.

    :param ControlEvent event: The event to get the information for.
    :return dict: The return dictionary.
    """
    if event.alias not in event_information:
        return {
            "guid": "",
            "key": ""
        }
    
    return event_information[event.alias]


def get_states(items: list[ControlEvent]) -> dict:
    """This file will loop through all given events
    and then return the state for each.

    :param list[ControlEvent] items: Input events.
    :return dict: Return dictionary with event states.
    """
    
    states = {}
    for item in items:
        info = get_event_information(item)
        if info["guid"] == "":
            states[item.alias] = None
            continue
        
        if info["guid"] == "keyboard":
            states[item.alias] = keyboard.is_pressed(info["key"])
            continue
        
        if item.type == "button":
            states[item.alias] = joysticks[info["guid"]][f"{info['key']}"]
        elif item.type == "axis":
            states[item.alias] = joysticks[info["guid"]][f"{info['key']}"]
    
    return states


def run():
    # Initialize the control listener.
    queue = multiprocessing.Queue()
    multiprocessing.Process(target=joystick_update_process, args=(queue,), daemon=True).start()
    threading.Thread(target=queue_listener_thread, args=(queue,), daemon=True).start()
    
    # Start the event information update thread.
    threading.Thread(target=event_information_update_thread, daemon=True).start()

    logging.info(Translate("controls.listener_started"))