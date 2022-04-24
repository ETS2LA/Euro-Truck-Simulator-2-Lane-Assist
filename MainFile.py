"""
Main loop and UI for ETS2 AutoDrive
"""
import tkinter as tk
from tkinter import Toplevel, ttk

from matplotlib.pyplot import draw
import ets2LaneDetection as LaneDetection
import time
import vgamepad as vg
import pygame
import threading
import cv2
from mss import mss
import numpy as np
from PIL import Image
from simple_pid import PID

steeringPid = PID(0.75, 0.3, 0, setpoint=0)
pygame.display.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
gamepad = vg.VX360Gamepad()
try:
    wheel = pygame.joystick.Joystick(0)
except:
    print("No input devices connected")


enabled = False
close = False
settings = False
settingsOpen = False
steeringAxis = 0
enableDisableButton = 23
rightIndicator = 4
leftIndicator = 5


def ChangeVideoDimensions(dimension, position):
    dimension = dimension.replace("Width and Height of the video feed (not recommended to change). Current : ", "")
    dimension = dimension.split("x")
    position = position.replace("Position of the video feed. Current : ", "")
    position = position.split("x")
    LaneDetection.ChangeVideoDimension(dimension, position)

def ChangeLaneAssist(value, value2):
    global sensitivity
    global steeringPid
    value = value.replace("Sensitivity of lane assist. Current : ", "")
    value2 = value2.replace("Steering offset of lane assist. Current : ", "")
    value = int(value)
    value2 = int(value2)
    sensitivity = value
    LaneDetection.ChangeLaneAssist(value2)

def TogglePreview():
    LaneDetection.showPreview = not LaneDetection.showPreview

def ToggleEnable():
    global enabled
    enabled = not enabled

def OnClosing():
    global close
    close = True
    
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
    global wheel
    wheel = pygame.joystick.Joystick(x)
    menuText.set("Controller : " + wheel.get_name())

    axisMenu.delete(0, axisMenu.index(tk.END))
    buttonMenu.delete(0, buttonMenu.index(tk.END))

    for x in range(wheel.get_numbuttons()):
        buttonMenu.add_command(label="Button : " + str(x), command=lambda x=x: ChangeButton(x, buttonVar))

    for x in range(wheel.get_numaxes()):
        axisMenu.add_command(label="Axis : " + str(x), command=lambda x=x: ChangeAxis(x, axisVar))
      
def ChangeButton(x, menuText):
    global enableDisableButton
    enableDisableButton = x
    menuText.set("Button : " + str(x))

def ChangeAxis(x, menuText):
    global steeringAxis
    steeringAxis = x
    menuText.set("Steering axis : " + str(x))

def ChangeModel(model, useGPU):
    model = model.replace("Model to use (see github). Current : ", "")
    LaneDetection.ChangeModel(model, useGPU)

def ChangeRightIndicator(x, menuText):
    global rightIndicator
    rightIndicator = x
    menuText.set("Right indicator : " + str(x))

def ChangeLeftIndicator(x, menuText):
    global leftIndicator
    leftIndicator = x
    menuText.set("Left indicator : " + str(x))

"""
Main UI
"""

width = 500
height = 220

root = tk.Tk()
root.geometry(str(width) + "x" + str(height))
big_frame = ttk.Frame(root)
big_frame.pack(fill="both", expand=True, padx=10, pady=10)


root.tk.call("source", "sun-valley.tcl")
root.tk.call("set_theme", "dark")
root.protocol("WM_DELETE_WINDOW", OnClosing)
root.title("ETS2 Lane Assist")


# Add the fps values up top
fpsVal = AddLabel("Video FPS: To be determined", big_frame)


# Add a current control slider
currentVal = AddLabel("Control: To be determined", big_frame)
currentSlider = ttk.Scale(big_frame, from_=-500, to=500, orient=tk.HORIZONTAL, length=width)
currentSlider.pack()

# Add all of the buttons
AddButton("Toggle Preview", TogglePreview, big_frame)
AddButton("Toggle Enable", ToggleEnable, big_frame)
AddButton("Settings", OpenSettings, big_frame)
AddButton("Exit", OnClosing, big_frame)

desiredControl = 0
oldDesiredControl = 0
minSpikeSize = 0.1
IndicatingRight = False
IndicatingLeft = False
lastIndicatingRight = False
lastIndicatingLeft = False

def ControllerThread():
    global desiredControl
    global oldDesiredControl
    global close
    global enabled
    global IndicatingRight
    global IndicatingLeft
    global lastIndicatingLeft
    global lastIndicatingRight
    while True:
        
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

        if(IndicatingRight):
            indicatingLeft = False
        if(IndicatingLeft):
            indicatingRight = False

        if(close): break
        try:
            pygame.event.pump()
            if(wheel.get_button(enableDisableButton)):
                enabled = not enabled
                time.sleep(0.3)

            if(enabled):
                if desiredControl > 0.2:
                    desiredControl = 0.2
                if desiredControl < -0.2:
                    desiredControl = -0.2
                if(IndicatingRight):
                    gamepad.left_joystick_float(x_value_float = wheel.get_axis(steeringAxis), y_value_float = 0)
                elif(IndicatingLeft):
                    gamepad.left_joystick_float(x_value_float = wheel.get_axis(steeringAxis), y_value_float = 0)
                else:
                    gamepad.left_joystick_float(x_value_float = steeringPid(-desiredControl) + wheel.get_axis(steeringAxis), y_value_float = 0)
                gamepad.update()
                oldDesiredControl = (oldDesiredControl+oldDesiredControl+desiredControl)/3
            else:
                gamepad.left_joystick_float(x_value_float = wheel.get_axis(0), y_value_float = 0)
                gamepad.update()
        except:
            pass


"""
Settings UI
"""

settingsWindow = None

def CloseSettings():
    global settings
    global settingsWindow
    settingsWindow.destroy()
    settings = False

def UpdateControllersForMenu(menu, menuText, axisMenu, axisVar, buttonMenu, buttonVar, rightIndicatorVar, rightIndicatorMenu, leftIndicatorVar, leftIndicatorMenu):
    try:
        for x in range(pygame.joystick.get_count()):
            menu.delete(0)
    except:
        pass
    
    for x in range(pygame.joystick.get_count()):
        menu.add_command(label=pygame.joystick.Joystick(x).get_name(), command=lambda x=x: ChangeController(x, menuText, axisMenu, axisVar, buttonMenu, buttonVar))
        
axisSlider = None
runs = 0
drawCircles = None
def OpenSettings():
    global runs
    global root
    global settingsWindow
    global axisSlider
    global drawCircles

    width = 550
    height = 300

    runs += 1

    settingsWindow = Toplevel(root)
    settingsWindow.title = "Settings"
    settingsWindow.geometry(str(width) + "x" + str(height))
    settingsWindow.protocol("WM_DELETE_WINDOW", CloseSettings)

    tabs = ttk.Notebook(settingsWindow)

    # General Tab
    generalFrame = ttk.Frame(tabs)
    tabs.add(generalFrame, text="General")
    dimensionEntry = AddEntry("Width and Height of the video feed (not recommended to change). Current : ", generalFrame)
    positionEntry = AddEntry("Position of the video feed. Current : ", generalFrame)
    AddButton("Change Video Settings", lambda: ChangeVideoDimensions(dimensionEntry.get(), positionEntry.get()), generalFrame)
    sensitivityEntry = AddEntry("Sensitivity of lane assist. Current : ", generalFrame)
    steeringOffsetEntry = AddEntry("Steering offset of lane assist. Current : ", generalFrame)
    AddButton("Change Lane Assist Settings", lambda: ChangeLaneAssist(sensitivityEntry.get(), steeringOffsetEntry.get()), generalFrame)
    drawCircles = tk.BooleanVar()
    drawCircles.set(value=False)
    circles = ttk.Checkbutton(generalFrame, text="Show raw lane data", width=100, variable=drawCircles, offvalue=False, onvalue=True)
    circles.pack()

    if(runs == 1):
        dimensionEntry.insert(0, "Width and Height of the video feed (not recommended to change). Current : " + str(LaneDetection.w) + "x" + str(LaneDetection.h))
        positionEntry.insert(0, "Position of the video feed. Current : " + str(LaneDetection.x) + "x" + str(LaneDetection.y))
        sensitivityEntry.insert(0, "Sensitivity of lane assist. Current : " + str(sensitivity))
        steeringOffsetEntry.insert(0, "Steering offset of lane assist. Current : " + str(LaneDetection.steeringOffset))

    # Controller Tab
    axisVar = tk.StringVar()
    axisMenu = tk.Menu()
    buttonVar = tk.StringVar()
    buttonMenu = tk.Menu()
    rightIndicatorVar = tk.StringVar()
    rightIndicatorMenu = tk.Menu()
    leftIndicatorVar = tk.StringVar()
    leftIndicatorMenu = tk.Menu()
    controllerVar = tk.StringVar()
    controllerMenu = tk.Menu(postcommand=lambda: UpdateControllersForMenu(controllerMenu, controllerVar, axisMenu, axisVar, buttonMenu, buttonVar, rightIndicatorVar, rightIndicatorMenu, leftIndicatorVar, leftIndicatorMenu))

    controllerFrame = ttk.Frame(tabs)
    tabs.add(controllerFrame, text="Controller")
    controllers = ttk.Menubutton(controllerFrame, textvariable=controllerVar, width=100, menu=controllerMenu)
    controllers.pack()

    axis = ttk.Menubutton(controllerFrame, textvariable=axisVar, width=100, menu=axisMenu)
    axis.pack()

    axisSlider = ttk.Scale(controllerFrame, from_=-1, to=1, orient=tk.HORIZONTAL, length=width)
    axisSlider.pack()

    buttons = ttk.Menubutton(controllerFrame, textvariable=buttonVar, width=100, menu=buttonMenu)
    buttons.pack()

    leftIndicators = ttk.Menubutton(controllerFrame, textvariable=leftIndicatorVar, width=100, menu=leftIndicatorMenu)
    leftIndicators.pack()

    rightIndicators = ttk.Menubutton(controllerFrame, textvariable=rightIndicatorVar, width=100, menu=rightIndicatorMenu)
    rightIndicators.pack()


    if(runs == 1):
        for x in range(len(joysticks)):
            controllerMenu.add_command(label=joysticks[x].get_name(), command=lambda x=x: ChangeController(x, controllerVar, axisMenu, axisVar, buttonMenu, buttonVar))

        for x in range(wheel.get_numaxes()):
            axisMenu.add_command(label="Axis : " + str(x), command=lambda x=x: ChangeAxis(x, axisVar))

        for x in range(wheel.get_numbuttons()):
            buttonMenu.add_command(label="Button : " + str(x), command=lambda x=x: ChangeButton(x, buttonVar))
        
        for x in range(wheel.get_numbuttons()):
            leftIndicatorMenu.add_command(label="Left Indicator Button : " + str(x), command=lambda x=x: ChangeLeftIndicator(x, leftIndicatorVar))
        
        for x in range(wheel.get_numbuttons()):
            rightIndicatorMenu.add_command(label="Right Indicator Button : " + str(x), command=lambda x=x: ChangeRightIndicator(x, rightIndicatorVar))

        rightIndicatorVar.set("Right Indicator Button : " + str(rightIndicator))
        leftIndicatorVar.set("Left Indicator Button : " + str(leftIndicator))
        buttonVar.set("Button : " + str(enableDisableButton))
        controllerVar.set("Controller : " + wheel.get_name())
        axisVar.set("Axis : " + str(steeringAxis))

    # Model tab
    modelFrame = ttk.Frame(tabs)
    tabs.add(modelFrame, text="Model")
    modelEntry = AddEntry("Model to use (see github). Current : ", modelFrame)

    
    useGPUVar = tk.BooleanVar()
    useGPU = ttk.Checkbutton(modelFrame, text="Use GPU", variable=useGPUVar, offvalue=False, onvalue=True)
    useGPU.pack()
    
    AddButton("Change Model", lambda: ChangeModel(modelEntry.get(), useGPUVar), modelFrame)

    if(runs == 1):
        modelEntry.insert(0, "Model to use (see github). Current : " + LaneDetection.model_path.replace("models/", ""))

    tabs.pack(fill="both", expand=True)



controllerThread = threading.Thread(target=ControllerThread)
controllerThread.start()

print("One second timer just to be sure the lane detection is ready")
time.sleep(1)
sensitivity = 500
sct = mss()
while True:

    desiredControl = LaneDetection.difference / (sensitivity * 6)
    currentVal.set("Current Control : " + str(round(LaneDetection.difference, 2)))
    currentSlider.set(LaneDetection.difference)


    if(enabled):
        try:
            LaneDetection.UpdateLanes(drawCircles.get())
        except:
            LaneDetection.UpdateLanes(drawCircles=False)
        fpsVal.set("Video FPS: " + str(round(LaneDetection.fps, 2)))
    else:
        image = cv2.cvtColor(np.array(Image.frombytes('RGB', (LaneDetection.w,LaneDetection.h), sct.grab(LaneDetection.monitor).rgb)), cv2.COLOR_RGB2BGR)
        cv2.imshow("Detected lanes", cv2.putText(image, "Lane Assist is disabled", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2))
        fpsVal.set("Video FPS: Disabled")
    if(close):
        LaneDetection.close = True
        break
    if(settings):
        try:
            axisSlider.set(wheel.get_axis(steeringAxis))
        except: pass
        if(not settingsOpen):
            OpenSettings()
            settingsOpen = True
    else:
        settingsOpen = False
    root.update()