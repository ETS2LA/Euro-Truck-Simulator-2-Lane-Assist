"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="VGamepadController", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Outputs controller data to the game.",
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
import os
import vgamepad as vg
import random

gamepad = None
def createController():
    global gamepad
    try:
        gamepad = vg.VX360Gamepad()
        print("Created controller")
    except Exception as e:
        print("\033[91mCouldn't connect to the VIGEM driver.\n1. Make sure it's installed and updated\nIf not then go to\nC:/Users/*Username*/AppData/Local/Programs/Python/*Python Version*/Lib/site-packages/vgamepad/win/install \033[00m")
        print("\033[91m2. Install the VC Redist 2017 here (https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170). \033[00m")
        print("\033[91m3. Try restarting your pc. \033[00m")
        input("Press enter to safely close the application. ")
        exit()


def onEnable():
    pass

def onDisable():
    pass

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    if gamepad == None:
        createController()
        
    try:
        controller = data["controller"]
        try:
            leftStick = controller["leftStick"]
        except:
            leftStick = 0
        
        
        if leftStick > 1:
            leftStick = 1
        elif leftStick < -1:
            leftStick = -1
        
        gamepad.left_joystick_float(x_value_float = leftStick, y_value_float = 0)
        gamepad.update()
        # print(leftStick)
    
    except Exception as ex:
        print(ex)
        pass

    return data # Plugins need to ALWAYS return the data