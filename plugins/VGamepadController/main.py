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
import time
import threading

gamepad = None
def createController():
    global gamepad
    try:
        gamepad = vg.VX360Gamepad()
        print("Created controller")
    except Exception as e:
        try:
            gamepad = vg.VX360Gamepad()
            print("Created controller")
        except:
            print("\033[91mCouldn't connect to the VIGEM driver.\n1. Make sure it's installed and updated\nIf not then go to\nC:/Users/*Username*/AppData/Local/Programs/Python/*Python Version*/Lib/site-packages/vgamepad/win/install \033[00m")
            print("\033[91m2. Install the VC Redist 2017 here (https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170). \033[00m")
            print("\033[91m3. Try restarting your pc. \033[00m")
            input("Press enter to safely close the application. ")
            exit()

ControllerThread = None
def onEnable():
    global ControllerThread
    ControllerThread = threading.Thread(target=controllerThread).start()
    pass

def onDisable():
    global stop
    stop = True
    global ControllerThread
    try:
        ControllerThread.stop()
    except:
        pass

button_A_pressed = False
button_B_pressed = False
button_X_pressed = False

lastControl = 0
currentControl = 0
lastFrameTime = 0
lastUpdateTime = time.time()
stop = False
def controllerThread():
    global gamepad
    while True:
        if stop:
            break
        try:
            # Lerp between the two values depending on how long it's been since the last frame
            # print(lastControl + (currentControl - lastControl) * ((time.time() - lastUpdateTime) / lastFrameTime))
            gamepad.left_joystick_float(x_value_float=lastControl + (currentControl - lastControl) * ((time.time() - lastUpdateTime) / lastFrameTime), y_value_float=0)
            gamepad.update()
        except Exception as e:
            # print(e.args)
            pass
        
        time.sleep(0.01)

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    global lastControl
    global currentControl
    global lastFrameTime
    global lastUpdateTime
    lastUpdateTime = time.time()
    
    global button_A_pressed
    global button_B_pressed
    global button_X_pressed
    if gamepad == None:
        createController()
        
    try:
        controller = data["controller"]
        try:
            leftStick = controller["leftStick"]
        except:
            leftStick = 0
        
        try:
            lefttrigger = controller["lefttrigger"]
            righttrigger = controller["righttrigger"]
        except:
            lefttrigger = 0
            righttrigger = 0
        
        try:
            button_A = controller["button_A"]
            button_B = controller["button_B"]
            button_X = controller["button_X"]
        except:
            button_A = False
            button_B = False
            button_X = False
        
        if leftStick > 1:
            leftStick = 1
        elif leftStick < -1:
            leftStick = -1
        
        if lefttrigger > 1:
            lefttrigger = 1
        elif lefttrigger < 0:
            lefttrigger = 0

        if righttrigger > 1:
            righttrigger = 1
        elif righttrigger < 0:
            righttrigger = 0

        if button_A_pressed == True:
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

        if button_B_pressed == True:
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)

        if button_X_pressed == True:
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

        button_A_pressed = False
        button_B_pressed = False
        button_X_pressed = False

        lastControl = currentControl
        currentControl = leftStick
        lastFrameTime = data["last"]["executionTimes"]["all"]
        # gamepad.left_joystick_float(x_value_float = leftStick, y_value_float = 0)
        gamepad.left_trigger_float(value_float = lefttrigger)
        gamepad.right_trigger_float(value_float = righttrigger)

        if button_A == True:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            button_A_pressed = True

        if button_B == True:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            button_B_pressed = True

        if button_X == True:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            button_X_pressed = True

        # gamepad.update()
        # print(leftStick)
    
    except Exception as ex:
        if "controller" not in ex.args:
            print(ex)
        pass

    return data # Plugins need to ALWAYS return the data