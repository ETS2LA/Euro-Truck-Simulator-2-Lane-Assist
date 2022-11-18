"""
Main loop and UI for Euro-Truck-Simulator-2-Lane-Assist
Tumppi066 @ https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist
"""

# CHANGE THESE VALUES IN THE SETTINGS.JSON FILE
# THEY WILL NOT UPDATE IF CHANGED HERE

# Set default variables
enabled = False
close = False
disableLaneAssistWhenIndicating = True
sensitivity = 500
useDirectX = False
# Default controller settings
defaultControllerIndex = 0 # This can be changed if your desired controller is not always the first input device (ie. if you have multiple controllers, like a HOTAS setup)
useLogitech = 0
steeringAxis = 0
enableDisableButton = 5
rightIndicator = 1
leftIndicator = 2
maximumControl = 0.2 # This changes the max control angle (between 0 and 1)
controlSmoothness = 2 # How many smoothness iterations to do ((oldValue * smoothness + newValue) / smoothness + 1)
# Debug settings
printControlDebug = False
preview = None

# UI imports
import tkinter as tk
from tkinter import Toplevel, ttk
from tracemalloc import start

# Image editing and processing
from matplotlib.pyplot import draw
import cv2
import numpy as np
from PIL import Image, ImageTk
from torch import true_divide
import mss

# Gamepad
import vgamepad as vg
import pygame
import threading

# Misc.
import ets2LaneDetection as LaneDetection
import time
import json
import settingsInterface as settings

# Loads all the settings from the settings.json file.
def LoadSettings():
    global sensitivity
    global maximumControl
    global controlSmoothness
    global disableLaneAssistWhenIndicating
    global defaultControllerIndex
    global steeringAxis
    global enableDisableButton
    global rightIndicator
    global leftIndicator
    global printControlDebug
    global useDirectX
    global useLogitech
    global preview

    # Set settings
    preview = settings.GetSettings("generalSettings","capturePreview")
    sensitivity = settings.GetSettings("controlSettings","sensitivity")
    useLogitech = settings.GetSettings("controlSettings","experimentalLogitechSupport")
    maximumControl = settings.GetSettings("controlSettings","maximumControl")
    controlSmoothness = settings.GetSettings("controlSettings","controlSmoothness")
    disableLaneAssistWhenIndicating = settings.GetSettings("controlSettings","disableLaneAssistWhenIndicating")
    defaultControllerIndex = settings.GetSettings("controlSettings","defaultControllerIndex")
    steeringAxis = settings.GetSettings("controlSettings","steeringAxis")
    enableDisableButton = settings.GetSettings("controlSettings","enableDisableButton")
    rightIndicator = settings.GetSettings("controlSettings","rightIndicator")
    leftIndicator = settings.GetSettings("controlSettings","leftIndicator")
    printControlDebug = settings.GetSettings("debugSettings","printControlDebug")
    useDirectX = settings.GetSettings("screenCapture","useDirectX")

    LaneDetection.LoadSettings()


LoadSettings()


"""
Application functions.
"""

def ChangeVideoDimensions(dimension, position):
    # Interface with Lane Detection to change  
    # the video dimensions and position

    dimension = dimension.replace("Width and Height of the video feed (not recommended to change). Current : ", "")
    dimension = dimension.split("x")
    position = position.replace("Position of the video feed. Current : ", "")
    position = position.split("x")
    LaneDetection.ChangeVideoDimension(dimension, position)

def ChangeLaneAssist(value, value2):
    # Interface with Lane Detection to change  
    # the sensitivity and offset of the lane assist

    global sensitivity
    value = value.replace("Sensitivity of lane assist. Current : ", "")
    value2 = value2.replace("Steering offset of lane assist. Current : ", "")
    value = int(value)
    value2 = int(value2)
    sensitivity = value
    LaneDetection.SaveSettings("controlSettings", "sensitivity", sensitivity)
    LaneDetection.ChangeLaneAssist(value2)

def TogglePreview():
    LaneDetection.showPreview = not LaneDetection.showPreview
    LaneDetection.SaveSettings("generalSettings", "showPreview", LaneDetection.showPreview)

def ToggleEnable():
    global enabled
    enabled = not enabled
    LaneDetection.UpdateLanes()

def OnClosing():
    # This will signal the threads to stop, 
    # preventing crashes.
    global close
    close = True

# The next three are repeated commands in the UI
# that I made a function for less clutter.
def AddButton(name, callback, frame):
    button = ttk.Button(frame, text=name, command=callback, width=100)
    button.pack()

def AddLabel(text, frame):
    labelVal = tk.StringVar()
    labelVal.set(text)
    label = ttk.Label(frame, textvariable=labelVal)
    label.pack()
    return labelVal

def AddEntry(name, frame, width = 100):
    entry = ttk.Entry(frame, text = name, width=width)
    entry.pack()
    return entry

def OpenSettings():
    global settings
    settings = True

def ChangeController(x, menuText, axisMenu, axisVar, buttonMenu, buttonVar):
    # This functions makes sure that all the UI is updated for the new controller.
    # x = controller index
    global wheel
    wheel = pygame.joystick.Joystick(x)
    menuText.set("Controller : " + wheel.get_name())

    axisMenu.delete(0, axisMenu.index(tk.END))
    buttonMenu.delete(0, buttonMenu.index(tk.END))

    for x in range(wheel.get_numbuttons()):
        buttonMenu.add_command(label="Button : " + str(x), command=lambda x=x: ChangeButton(x, buttonVar))

    for x in range(wheel.get_numaxes()):
        axisMenu.add_command(label="Axis : " + str(x), command=lambda x=x: ChangeAxis(x, axisVar))

def ChangeControllerSettingsFromFile():
    global wheel
    global rightIndicator
    global leftIndicator
    global enableDisableButton
    global steeringAxis
    global sensitivity
    global maximumControl
    global controlSmoothness
    global disableLaneAssistWhenIndicating
    global joysticks

    
    # Get settings
    rightIndicator = settings.GetSettings("controlSettings","rightIndicator")
    leftIndicator = settings.GetSettings("controlSettings","leftIndicator")
    enableDisableButton = settings.GetSettings("controlSettings","enableDisableButton")
    steeringAxis = settings.GetSettings("controlSettings","steeringAxis")
    sensitivity = settings.GetSettings("controlSettings","sensitivity")
    LaneDetection.steeringOffset = settings.GetSettings("controlSettings","steeringOffset")
    maximumControl = settings.GetSettings("controlSettings","maximumControl")
    controlSmoothness = settings.GetSettings("controlSettings","controlSmoothness")
    disableLaneAssistWhenIndicating = settings.GetSettings("controlSettings","disableLaneAssistWhenIndicating")
    defaultControllerIndex = settings.GetSettings("controlSettings","defaultControllerIndex")

    wheel = pygame.joystick.Joystick(settings.GetSettings("controlSettings","defaultControllerIndex"))

    print("\033[92mController settings updated! \033[00m")


# The next four serve the same purpose as the last one.
def ChangeButton(x, menuText):
    global enableDisableButton
    enableDisableButton = x
    menuText.set("Button : " + str(x))

def ChangeAxis(x, menuText):
    global steeringAxis
    steeringAxis = x
    menuText.set("Steering axis : " + str(x))

def ChangeRightIndicator(x, menuText):
    global rightIndicator
    rightIndicator = x
    menuText.set("Right indicator : " + str(x))

def ChangeLeftIndicator(x, menuText):
    global leftIndicator
    leftIndicator = x
    menuText.set("Left indicator : " + str(x))



# Gamepad driver initialization
try:
    gamepad = vg.VX360Gamepad()
except Exception as e:
    print(e.args)
    print("\033[91mCouldn't connect to the VIGEM driver. Make sure it's installed and updated\nIf not then go to\nC:/Users/*Username*/AppData/Local/Programs/Python/*Python Version*/Lib/site-packages/vgamepad/win/install \033[00m")

# Pygame initialization
# and gamepad detection
pygame.display.init()
pygame.joystick.init()
try:
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    joystickNames = []
    for x in joysticks:
        joystickNames.append(x.get_name())

except Exception as e:
    print(e.args)
    print("\033[91mError when loading gamepads \033[00m")


try:
    wheel = pygame.joystick.Joystick(defaultControllerIndex)
except Exception as e:
    print(e.args)
    print("\033[91mCould not load wheel from default index (have you changed your controller around?) \033[00m")


# Get the logitech wheel information
# This code is mosly from the documentation
if useLogitech:
    import logitech_steering_wheel as lsw
    import pygetwindow as gw
    # Apparently it needs a window?
    window_handle = gw.getActiveWindow()._hWnd
    initialized = lsw.initialize_with_window(ignore_x_input_controllers=True, hwnd=window_handle)
    
    print("Logitech SDK version is: " + str(lsw.get_sdk_version()))
    connected = lsw.is_device_connected(defaultControllerIndex, lsw.DeviceType.WHEEL)
    lsw.update()
    if connected:
        print("Logitech wheel on index {} : connected".format(defaultControllerIndex))
        print("Logitech wheel on index {} has force feedback : ".format(defaultControllerIndex) + str(lsw.has_force_feedback(defaultControllerIndex)))
        print("Testing force feedback...")
        lsw.play_constant_force(defaultControllerIndex, 20)
        for i in range(0, 30):
            time.sleep(.1)
            lsw.update()
            data = lsw.get_state(defaultControllerIndex)
            print("Playing force feedback for {} seconds".format(round(2.9-i/10, 1)) + " Current angle : " + str(data.lX / 32768 * 900)+ "\r", end='')
        lsw.stop_constant_force(defaultControllerIndex)
        print("\nForce feedback test complete")
    else:
        print("Logitech Steering Wheel not found")
    
# I like to put all my variables outside the function
# these should not be changed.
desiredControl = 0
oldDesiredControl = 0
IndicatingRight = False
IndicatingLeft = False
lastIndicatingRight = False
lastIndicatingLeft = False
def ControllerThread():
    """
    This is the function we assing to another thread.
    It handles updating the virtual controller position based on the wheel position
    and what the program wants to do.

    Because this function is in another thread it is able to run
    at very high speeds.
    """
    global desiredControl
    global oldDesiredControl
    global close
    global enabled
    global IndicatingRight
    global IndicatingLeft
    global lastIndicatingLeft
    global lastIndicatingRight
    global maximumControl
    global controlSmoothness
    global disableLaneAssistWhenIndicating

    while True:
        try:
            # Makes sure the thread will close if the program is closed.
            if(close): break

            # This kind of if, elif statement converts the presses of the indicator to
            # a constant on/off value.
            if disableLaneAssistWhenIndicating:
                if(wheel.get_button(rightIndicator) and not lastIndicatingRight):
                    IndicatingRight = not IndicatingRight
                    lastIndicatingRight = True
                elif(not wheel.get_button(rightIndicator)):
                    lastIndicatingRight = False
                if(wheel.get_button(leftIndicator) and not lastIndicatingLeft):
                    IndicatingLeft = not IndicatingLeft
                    lastIndicatingLeft = True
                elif(not wheel.get_button(leftIndicator)):
                    lastIndicatingLeft = False

            # Make sure we can't indicate in both directions.
            if disableLaneAssistWhenIndicating:
                if(wheel.get_button(leftIndicator) and IndicatingRight):
                    IndicatingLeft = True
                    lastIndicatingLeft = True
                    lastIndicatingRight = False
                    IndicatingRight = False
                elif(wheel.get_button(rightIndicator) and IndicatingLeft):
                    IndicatingLeft = False
                    lastIndicatingLeft = False
                    lastIndicatingRight = True
                    IndicatingRight = True

            try:
                pygame.event.pump() # Update the controller values


                # Main controller update loop.
                if(enabled):
                    # Clamp the control
                    if desiredControl > maximumControl:
                        desiredControl = maximumControl
                    if desiredControl < -maximumControl:
                        desiredControl = -maximumControl

                    # If we are indicating, then disable the automatic control.
                    if disableLaneAssistWhenIndicating:
                        if(IndicatingRight):
                            gamepad.left_joystick_float(x_value_float = wheel.get_axis(steeringAxis), y_value_float = 0)
                            LaneDetection.isIndicating = 1
                        elif(IndicatingLeft):
                            gamepad.left_joystick_float(x_value_float = wheel.get_axis(steeringAxis), y_value_float = 0)
                            LaneDetection.isIndicating = 2
                        else:
                            LaneDetection.isIndicating = 0
                            gamepad.left_joystick_float(x_value_float = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + wheel.get_axis(steeringAxis), y_value_float = 0)
                    else:
                        LaneDetection.isIndicating = 0
                        gamepad.left_joystick_float(x_value_float = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + wheel.get_axis(steeringAxis), y_value_float = 0)
                    gamepad.update()
                    if useLogitech:
                        data = lsw.get_state(defaultControllerIndex)
                        currentLogitechAngle = data.lX/32768
                        desiredAngle = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1)
                        if currentLogitechAngle > desiredAngle:
                            lsw.play_constant_force(defaultControllerIndex, 10)
                        elif currentLogitechAngle < desiredAngle:
                            lsw.play_constant_force(defaultControllerIndex, -10)
                        else:
                            lsw.stop_constant_force(defaultControllerIndex)

                        if printControlDebug:
                            print("Control: " + str(((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + wheel.get_axis(steeringAxis)) + " Wheel : " + str(currentLogitechAngle) + "                          \r", end="")
                    elif printControlDebug:
                        print("Control: " + str(((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + wheel.get_axis(steeringAxis)) + "\r", end="")
                    oldDesiredControl = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1)
                else:
                    # If the lane assist is disabled we just input the default control.
                    gamepad.left_joystick_float(x_value_float = wheel.get_axis(steeringAxis), y_value_float = 0)
                    gamepad.update()

                time.sleep(0.01) # These time.sleep commands make sure that the control thread does not crash
            except Exception as ex:
                
                print(ex.args)
                print(ex)
                print("Most likely fix : change your indicator and or enable/disable buttons.")

                time.sleep(0.01) # These time.sleep commands make sure that the control thread does not crash
                pass
        except Exception as ex:
            
            print(ex.args)
            print(ex)
            print("Most likely fix : change your indicator and or enable/disable buttons.")
                    
            time.sleep(0.01) # These time.sleep commands make sure that the control thread does not crash
            pass


# Start the controller thread.
controllerThread = threading.Thread(target=ControllerThread)
controllerThread.start()
image = None
sct = mss.mss()
lastImageUpdate = time.time()
def mainFileLoop():
    """
    Main UI and control Loop
    """

    global desiredControl

    startTime = time.time_ns()
    desiredControl = LaneDetection.difference / (sensitivity * 6) # The desired control is the difference between the center of the lane and the center of the screen.

    if(enabled):
        # This will signal the LaneDetection bridge to update the frame.
        try:
            LaneDetection.UpdateLanes()
            image = LaneDetection.image
        except Exception as e:
            # Incase for some reason raw data is not available.
            print(e.args)
            pass
    elif LaneDetection.showPreview:
        # If the lane detection is disabled then we will just show the original frame.
        if not useDirectX:
            image = cv2.cvtColor(np.array(Image.frombytes('RGB', (LaneDetection.w,LaneDetection.h), sct.grab(LaneDetection.monitor).rgb)), cv2.COLOR_RGB2BGR)
        else:
            image = LaneDetection.camera.get_latest_frame()
        
        
        cv2.imshow("Detected lanes", cv2.putText(image, "Lane Assist is disabled", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2))
    else:
        cv2.destroyAllWindows()
        
    if(close):
        # Make sure the LaneDetection is closing with the program.
        LaneDetection.close = True
    
    if close:
        LaneDetection.close = True
        del LaneDetection.camera
        exit()
    
