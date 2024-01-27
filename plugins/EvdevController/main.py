"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="EvdevController", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="A virtual controller for linux using the evdev library.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before UI", # Will run the plugin before anything else in the mainloop (data will be empty)
    noUI=True
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
from sys import platform
import os

if platform != "linux" or platform != "linux2":
    print("This plugin only works on linux!")
else:
    from evdev import UInput, ecodes, AbsInfo

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]


def plugin(data):
    # Get left stick value
    try:
        leftStick = int(32767*data["controller"]["leftStick"])
        controller.write(ecodes.EV_ABS, ecodes.ABS_RX, leftStick)
        controller.syn()
    except:
        pass

    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    if platform == "linux" or platform == "linux2":
        global controller
        # Create a virtual controller with one axis
        cap = {
            ecodes.EV_KEY: [ecodes.BTN_A, ecodes.BTN_B, ecodes.BTN_X, ecodes.BTN_Y, ecodes.BTN_TL, ecodes.BTN_TR, ecodes.BTN_SELECT, ecodes.BTN_START, ecodes.BTN_MODE, ecodes.BTN_THUMBL, ecodes.BTN_THUMBR],
            ecodes.EV_ABS: [(ecodes.ABS_RX, AbsInfo(value=0, min=-32767, max=32767,fuzz=0, flat=0, resolution=0)),(ecodes.ABS_RY, AbsInfo(value=0, min=-32767, max=32767,fuzz=0, flat=0, resolution=0))]
        }
    
        controller = UInput(cap, name="Lane Assist Simulated Controller")
    

def onDisable():
    global controller
    del controller
    
