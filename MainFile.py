"""
Main loop and UI for Euro-Truck-Simulator-2-Lane-Assist
Tumppi066 @ https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist
"""

# Set default variables
enabled = False
close = False
settings = False
settingsOpen = False
disableLaneAssistWhenIndicating = True
sensitivity = 500
# Default controller settings
defaultControllerIndex = 0 # This can be changed if your desired controller is not always the first input device (ie. if you have multiple controllers, like a HOTAS setup)
steeringAxis = 0
enableDisableButton = 5
rightIndicator = 1
leftIndicator = 2
maximumControl = 0.2 # This changes the max control angle (between 0 and 1)
controlSmoothness = 2 # How many smoothness iterations to do ((oldValue * smoothness + newValue) / smoothness + 1)
# Default video settings
w, h = 833, 480
x, y = 544, 300


# UI imports
import tkinter as tk
from tkinter import Toplevel, ttk

# Image editing and processing
from matplotlib.pyplot import draw
import cv2
from mss import mss
import numpy as np
from PIL import Image, ImageTk
from torch import true_divide

# Gamepad
import vgamepad as vg
import pygame
import threading

# Time and LaneDetection bridge
import ets2LaneDetection as LaneDetection
import time


# Pygame initialization
# and gamepad detection
pygame.display.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
try:
    wheel = pygame.joystick.Joystick(defaultControllerIndex)
except:
    print("No input devices connected")

# Gamepad driver initialization
gamepad = vg.VX360Gamepad()

sct = mss()
monitor = {'top': y, 'left': x, 'width': w, 'height': h}

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
    LaneDetection.ChangeLaneAssist(value2)

def TogglePreview():
    LaneDetection.showPreview = not LaneDetection.showPreview

def ToggleEnable():
    global enabled
    enabled = not enabled

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

def ChangeModel(model, useGPU):
    model = model.replace("Model to use (see github). Current : ", "")
    LaneDetection.ChangeModel(model, useGPU)


"""
Main UI
"""

width = 500
height = 510

# This initializes the Main UI tkinter window
root = tk.Tk() # The main window
root.geometry(str(width) + "x" + str(height))
big_frame = ttk.Frame(root) # A frame in that window
big_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Draw the logo, and check if it has been deleted
try:
    logo = Image.open("LaneAssistLogoWide.jpg")
    logo = logo.resize((500,300), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(logo)
    panel = tk.Label(root, image = logo)
    panel.pack(side = "bottom", fill = "both", expand = "yes")
except:
    print("Logo not found")
    pass

# Set the desired theme
root.tk.call("source", "sun-valley.tcl")
root.tk.call("set_theme", "dark")
root.protocol("WM_DELETE_WINDOW", OnClosing)
root.title("ETS2 Lane Assist")

# Add the fps values up top
fpsVal = AddLabel("Video FPS: To be determined", big_frame)

# Add a visualizer to tell what the program is doing
currentVal = AddLabel("Control: To be determined", big_frame)
currentSlider = ttk.Scale(big_frame, from_=-500, to=500, orient=tk.HORIZONTAL, length=width)
currentSlider.pack()

# Add all of the main buttons
AddButton("Toggle Preview", TogglePreview, big_frame)
AddButton("Toggle Enable", ToggleEnable, big_frame)
AddButton("Settings", OpenSettings, big_frame)
AddButton("Exit", OnClosing, big_frame)

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

        # Makes sure the thread will close if the program is closed.
        if(close): break
        try:
            pygame.event.pump() # Update the controller values
            
            # Enable and disable from the controller button.
            if(wheel.get_button(enableDisableButton)):
                enabled = not enabled
                time.sleep(0.3)

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
                        print("Right")
                    elif(IndicatingLeft):
                        gamepad.left_joystick_float(x_value_float = wheel.get_axis(steeringAxis), y_value_float = 0)
                        print("Left")
                        LaneDetection.isIndicating = 2
                    else:
                        LaneDetection.isIndicating = 0
                        gamepad.left_joystick_float(x_value_float = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + wheel.get_axis(steeringAxis), y_value_float = 0)
                else:
                    LaneDetection.isIndicating = 0
                    gamepad.left_joystick_float(x_value_float = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + wheel.get_axis(steeringAxis), y_value_float = 0)
                gamepad.update()
                oldDesiredControl = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1)
            else:
                # If the lane assist is disabled we just input the default control.
                gamepad.left_joystick_float(x_value_float = wheel.get_axis(steeringAxis), y_value_float = 0)
                gamepad.update()
            
            time.sleep(0.01) # These time.sleep commands make sure that the control thread does not crashing
        except Exception as ex:
            print(ex.args)
            print("Most likely fix : change your indicator and or enable/disable buttons.")
            time.sleep(0.01) # These time.sleep commands make sure that the control thread does not crashing
            pass


"""
Settings UI
"""

# This will be assinged by the program
# don't change it.
settingsWindow = None

def CloseSettings():
    global settings
    global settingsWindow
    settingsWindow.destroy()
    settings = False

def UpdateControllersForMenu(menu, menuText, axisMenu, axisVar, buttonMenu, buttonVar):
    # This function will update the controller selection menu and the axis and button selection menu.
    try:
        for x in range(pygame.joystick.get_count()):
            menu.delete(0)
    except:
        pass # Fallback for no controllers
    
    try:
        for x in range(pygame.joystick.get_count()):
            menu.add_command(label=pygame.joystick.Joystick(x).get_name(), command=lambda x=x: ChangeController(x, menuText, axisMenu, axisVar, buttonMenu, buttonVar))
    except:
        print("Can't update controller selection menu, no controllers present.")
        pass # Fallback for no controllers

# I like to put all my variables outside the function
# these should not be changed.  
axisSlider = None
runs = 0
drawCircles = None
settingsWidth = 550
settingsHeight = 300

def OpenSettings():
    global runs
    global root
    global settingsWindow
    global axisSlider
    global drawCircles
    global settingsHeight
    global settingsWidth
    
    # Don't log runs too far, eventually it will cause problems.
    if runs < 10:
        runs += 1

    # Initialize the main settings window.
    settingsWindow = Toplevel(root)
    settingsWindow.title = "Settings"
    settingsWindow.geometry(str(settingsWidth) + "x" + str(settingsHeight))
    settingsWindow.protocol("WM_DELETE_WINDOW", CloseSettings) # When closing settings we call this function.

    tabs = ttk.Notebook(settingsWindow) # Handle the settings window tabs.

    """
    Entry is a text entry box.
    Button is obviously a button.
    Label is a normal text label.
    """

    # General Tab
    generalFrame = ttk.Frame(tabs) # Make the general tab frame
    tabs.add(generalFrame, text="General") # and add it to the tabs.
    dimensionEntry = AddEntry("Width and Height of the video feed (not recommended to change). Current : ", generalFrame)
    positionEntry = AddEntry("Position of the video feed. Current : ", generalFrame)
    AddButton("Change Video Settings", lambda: ChangeVideoDimensions(dimensionEntry.get(), positionEntry.get()), generalFrame)
    sensitivityEntry = AddEntry("Sensitivity of lane assist. Current : ", generalFrame)
    steeringOffsetEntry = AddEntry("Steering offset of lane assist. Current : ", generalFrame)
    AddButton("Change Lane Assist Settings", lambda: ChangeLaneAssist(sensitivityEntry.get(), steeringOffsetEntry.get()), generalFrame)
    # Make the toggle for drawing raw lane data.
    drawCircles = tk.BooleanVar()
    drawCircles.set(value=False)
    circles = ttk.Checkbutton(generalFrame, text="Show raw lane data", width=100, variable=drawCircles, offvalue=False, onvalue=True)
    circles.pack()

    # Update the options with default information on the first run.
    if(runs == 1):
        dimensionEntry.insert(0, "Width and Height of the video feed (not recommended to change). Current : " + str(LaneDetection.w) + "x" + str(LaneDetection.h))
        positionEntry.insert(0, "Position of the video feed. Current : " + str(LaneDetection.x) + "x" + str(LaneDetection.y))
        sensitivityEntry.insert(0, "Sensitivity of lane assist. Current : " + str(sensitivity))
        steeringOffsetEntry.insert(0, "Steering offset of lane assist. Current : " + str(LaneDetection.steeringOffset))

    # Controller Tab

    # Make all default variables
    axisVar = tk.StringVar()
    axisMenu = tk.Menu()
    buttonVar = tk.StringVar()
    buttonMenu = tk.Menu()
    rightIndicatorVar = tk.StringVar()
    rightIndicatorMenu = tk.Menu()
    leftIndicatorVar = tk.StringVar()
    leftIndicatorMenu = tk.Menu()
    controllerVar = tk.StringVar()
    controllerMenu = tk.Menu(postcommand=lambda: UpdateControllersForMenu(controllerMenu, controllerVar, axisMenu, axisVar, buttonMenu, buttonVar)) # When opening the menu it will update all controllers.

    controllerFrame = ttk.Frame(tabs) # Make the controller tab frame
    tabs.add(controllerFrame, text="Controller") # and add it to the tabs.
    
    # Make all the menubuttons, I did not write a function for some reason.
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

    # Update the options with default information on the first run.
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
    modelFrame = ttk.Frame(tabs) # Make the model tab frame
    tabs.add(modelFrame, text="Model") # and add it to the tabs.
    # Make the two model options and an apply button.
    modelEntry = AddEntry("Model to use (see github). Current : ", modelFrame)
    useGPUVar = tk.BooleanVar()
    useGPU = ttk.Checkbutton(modelFrame, text="Use GPU", variable=useGPUVar, offvalue=False, onvalue=True)
    useGPU.pack()
    AddButton("Change Model", lambda: ChangeModel(modelEntry.get(), useGPUVar), modelFrame) # When pressed, change the model.
    
    # Update the options with default information on the first run.
    if(runs == 1):
        modelEntry.insert(0, "Model to use (see github). Current : " + LaneDetection.model_path.replace("models/", ""))

    # Apply the tabs to the settings window.
    tabs.pack(fill="both", expand=True)

# Start the controller thread.
controllerThread = threading.Thread(target=ControllerThread)
controllerThread.start()

print("One second timer just to be sure the lane detection is ready")
time.sleep(1)
while True:

    """
    Main UI and control Loop
    """

    desiredControl = LaneDetection.difference / (sensitivity * 6) # The desired control is the difference between the center of the lane and the center of the screen.
    currentVal.set("Current Control : " + str(round(LaneDetection.difference, 2))) # Apply the current control to the current control slider.
    currentSlider.set(LaneDetection.difference)

    if(enabled):
        # This will signal the LaneDetection bridge to update the frame.
        try:
            LaneDetection.UpdateLanes(drawCircles.get())
        except:
            # Incase for some reason raw data is not available.
            pass
        
        fpsVal.set("LaneDetection FPS: " + str(round(LaneDetection.fps, 2)))
    else:
        # If the lane detection is disabled then we will just show the original frame.
        image = cv2.cvtColor(np.array(Image.frombytes('RGB', (LaneDetection.w,LaneDetection.h), sct.grab(LaneDetection.monitor).rgb)), cv2.COLOR_RGB2BGR)
        cv2.imshow("Detected lanes", cv2.putText(image, "Lane Assist is disabled", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2))
        fpsVal.set("LaneDetection FPS: Disabled")
    if(close):
        # Make sure the LaneDetection is closing with the program.
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
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit()
    root.update()