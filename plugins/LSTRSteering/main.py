"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""



from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="LSTRSteering", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will use the lstr lane data to output steering.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before controller" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import pygame
import cv2

pygame.joystick.init()
pygame.display.init()

def verifySetting(category, key, default):
    value = settings.GetSettings(category, key)
    
    if value == None:
        value = default
        settings.CreateSettings(category, key, default)
        
    return value

def updateSettings():
    global wheel
    global rightIndicator
    global leftIndicator
    global steeringAxis
    global maximumControl
    global controlSmoothness
    global sensitivity
    global offset
    global gamepadMode
    global gamepadSmoothness
    global enableDisable
    
    wheel = pygame.joystick.Joystick(verifySetting("LSTRSteering", "wheel", 0))
    
    rightIndicator = verifySetting("LSTRSteering", "rightIndicator", 13)
    leftIndicator = verifySetting("LSTRSteering", "leftIndicator", 14)
    steeringAxis = verifySetting("LSTRSteering", "steeringAxis", 0)
    maximumControl = verifySetting("LSTRSteering", "maximumControl", 0.2)
    controlSmoothness = verifySetting("LSTRSteering", "smoothness", 8)
    sensitivity = verifySetting("LSTRSteering", "sensitivity", 400)
    offset = verifySetting("LSTRSteering", "offset", 0)
    gamepadMode = verifySetting("LSTRSteering", "gamepad", False)
    gamepadSmoothness = verifySetting("LSTRSteering", "gamepadSmoothness", 0.05)
    enableDisable = verifySetting("LSTRSteering", "enableDisable", 5)
    
updateSettings()

# MOST OF THIS FILE IS COPIED FROM THE OLD VERSION
desiredControl = 0
oldDesiredControl = 0
lastFrame = 0
IndicatingRight = False
IndicatingLeft = False
lastIndicatingRight = False
lastIndicatingLeft = False
enabled = True
enabledTimer = 0
def plugin(data):
    global desiredControl
    global oldDesiredControl
    global wheel
    global enabled
    global IndicatingRight
    global IndicatingLeft
    global lastIndicatingLeft
    global lastIndicatingRight
    global maximumControl
    global controlSmoothness
    global sensitivity
    global offset
    global gamepadMode
    global gamepadSmoothness
    global lastFrame
    global enableDisable
    global enabledTimer
    # global disableLaneAssistWhenIndicating

    try:
        desiredControl = (data["LSTR"]["difference"] + offset) / (sensitivity * 6)
    except:
        desiredControl = oldDesiredControl
        
    data["controller"] = {}

    try:
        enabledTimer += 1 # Frames, this helps to prevent accidentally enabling disabling multiple times.
        if(wheel.get_button(enableDisable) and enabledTimer > 15):
            if enabled == True:
                enabled = False
                print("Disabled")
                enabledTimer = 0
                #sound.PlaySoundDisable()
            else:
                enabled = True
                print("Enabled")
                enabledTimer = 0
                #sound.PlaySoundEnable()
        
        # This kind of if, elif statement converts the presses of the indicator to
        # a constant on/off value.
        if(wheel.get_button(rightIndicator) and not lastIndicatingRight):
            if(IndicatingRight and enabled):
                pass
                #sound.PlaySoundEnable()
            elif(enabled):
                pass
                #sound.PlaySoundDisable()

            IndicatingRight = not IndicatingRight
            lastIndicatingRight = True
        elif(not wheel.get_button(rightIndicator) and lastIndicatingRight):
            lastIndicatingRight = False
        if(wheel.get_button(leftIndicator) and not lastIndicatingLeft):
            if(IndicatingLeft and enabled):
                #sound.PlaySoundEnable()
                pass
            elif(enabled):
                #sound.PlaySoundDisable()
                pass

            IndicatingLeft = not IndicatingLeft
            lastIndicatingLeft = True

        elif(not wheel.get_button(leftIndicator) and lastIndicatingLeft):
            lastIndicatingLeft = False

        # Make sure we can't indicate in both directions.
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
                if(IndicatingRight or IndicatingLeft):
                    
                    if gamepadMode:
                        value = pow(wheel.get_axis(steeringAxis), 2) 
                        if(wheel.get_axis(steeringAxis) < 0) : value = -value
                        newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                        lastFrame = newValue
                        data["controller"]["leftStick"] = newValue
                    else:
                        data["controller"]["leftStick"] = wheel.get_axis(steeringAxis)
                else:
                    if gamepadMode:
                        value = pow(wheel.get_axis(steeringAxis), 2) 
                        if(wheel.get_axis(steeringAxis) < 0) : value = -value
                        newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                        lastFrame = newValue
                        data["controller"]["leftStick"] = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + newValue
                    else:
                        data["controller"]["leftStick"] = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + wheel.get_axis(steeringAxis)
                
                oldDesiredControl = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1)
            else:
                # If the lane assist is disabled we just input the default control.
                if gamepadMode:
                    value = pow(wheel.get_axis(steeringAxis), 2) 
                    if(wheel.get_axis(steeringAxis) < 0) : value = -value
                    newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                    lastFrame = newValue
                    data["controller"]["leftStick"] = newValue
                else:
                    data["controller"]["leftStick"] = wheel.get_axis(steeringAxis)
            
        except Exception as ex:
            print(ex)
            print("Most likely fix : change your indicator and or enable/disable buttons.")
            pass
    except Exception as ex:
        print(ex)
        print("Most likely fix : change your indicator and or enable/disable buttons.")
        pass


    try:
        
        if enabled:
            output_img = data["frame"]
            w = output_img.shape[1]
            h = output_img.shape[0]
            
            currentDesired = desiredControl * (1/maximumControl)
            actualSteering = oldDesiredControl * (1/maximumControl)

            divider = 5
            # First draw a gray line to indicate the background
            cv2.line(output_img, (int(w/divider), int(h - h/10)), (int(w/divider*(divider-1)), int(h - h/10)), (100, 100, 100), 6, cv2.LINE_AA)
            # Then draw a light green line to indicate the actual steering
            cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + actualSteering * (w/2 - w/divider)), int(h - h/10)), (0, 255, 100), 6, cv2.LINE_AA)
            # Then draw a light red line to indicate the desired steering
            cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + currentDesired * (w/2 - w/divider)), int(h - h/10)), (0, 100, 255), 2, cv2.LINE_AA)

            try:
                if IndicatingLeft or IndicatingRight:
                    cv2.putText(output_img, "Indicating", (int(w/2), int(h - h/10 - 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)
            except:
                pass    
            
            # Also draw a enabled text to the top left
            cv2.putText(output_img, "Enabled", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)    
            
            data["frame"] = output_img
        else:
            output_img = data["frame"]
            w = output_img.shape[1]
            h = output_img.shape[0]
            
            divider = 5
            
            if lastFrame != 0:
                wheelValue = lastFrame
            else:
                wheelValue = wheel.get_axis(steeringAxis)
            # First draw a gray line to indicate the background
            cv2.line(output_img, (int(w/divider), int(h - h/10)), (int(w/divider*(divider-1)), int(h - h/10)), (100, 100, 100), 6, cv2.LINE_AA)
            # Then draw a light green line to indicate the wheel
            cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + wheelValue * (w/2 - w/divider)), int(h - h/10)), (0, 255, 100), 6, cv2.LINE_AA)

            # Also draw a disabled text to the top left
            cv2.putText(output_img, "Disabled", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    except Exception as ex:
        print(ex)
        pass

    return data # Plugins need to ALWAYS return the data


# Plugins can also have UIs, this works the same as the panel example
class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            helpers.MakeLabel(self.root, "General", 0, 0, font=("Robot", 12, "bold"))
            self.offset = helpers.MakeComboEntry(self.root, "Steering Offset", "LSTRSteering", "offset", 1, 0, width=12, value=0)
            self.smoothness = helpers.MakeComboEntry(self.root, "Smoothening", "LSTRSteering", "smoothness", 2, 0, width=12, value=8)
            self.sensitivity = helpers.MakeComboEntry(self.root, "Sensitivity", "LSTRSteering", "sensitivity", 3, 0, width=12, value=400)
            self.maximumControl = helpers.MakeComboEntry(self.root, "Maximum Control", "LSTRSteering", "maximumControl", 4, 0, isFloat=True, width=12, value=0.2)
            
            helpers.MakeLabel(self.root, "Controller (indexes)", 5, 0, font=("Robot", 12, "bold"))
            self.controller = helpers.MakeComboEntry(self.root, "Controller", "LSTRSteering", "controller", 6, 0, width=12, value=0)
            self.steeringAxis = helpers.MakeComboEntry(self.root, "Steering Axis", "LSTRSteering", "steeringAxis", 7, 0, width=12, value=0)
            self.enableDisable = helpers.MakeComboEntry(self.root, "Enable/Disable", "LSTRSteering", "enableDisable", 8, 0, width=12, value=5)
            self.rightIndicator = helpers.MakeComboEntry(self.root, "Right Indicator", "LSTRSteering", "rightIndicator", 9, 0, width=12, value=13)
            self.leftIndicator = helpers.MakeComboEntry(self.root, "Left Indicator", "LSTRSteering", "leftIndicator", 10, 0, width=12, value=14)
            
            
            helpers.MakeLabel(self.root, "Gamepad", 0, 2, font=("Robot", 12, "bold"))
            self.gamepad = helpers.MakeCheckButton(self.root, "Gamepad Mode", "LSTRSteering", "gamepad", 1, 2, width=15, default=True)
            self.gamepadSmoothness = helpers.MakeComboEntry(self.root, "Gamepad Smoothness", "LSTRSteering", "gamepadSmoothness", 2, 2, isFloat=True, width=12, labelwidth=18, value=0.05)
            
            helpers.MakeButton(self.root, "Save", self.save, 11, 0, width=12, center=True)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def save(self):
            settings.CreateSettings("LSTRSteering", "offset", self.offset.get())
            settings.CreateSettings("LSTRSteering", "smoothness", self.smoothness.get())
            settings.CreateSettings("LSTRSteering", "sensitivity", self.sensitivity.get())
            settings.CreateSettings("LSTRSteering", "maximumControl", self.maximumControl.get())
            settings.CreateSettings("LSTRSteering", "controller", self.controller.get())
            settings.CreateSettings("LSTRSteering", "steeringAxis", self.steeringAxis.get())
            settings.CreateSettings("LSTRSteering", "enableDisable", self.enableDisable.get())
            settings.CreateSettings("LSTRSteering", "rightIndicator", self.rightIndicator.get())
            settings.CreateSettings("LSTRSteering", "leftIndicator", self.leftIndicator.get())
            settings.CreateSettings("LSTRSteering", "gamepad", self.gamepad.get())
            settings.CreateSettings("LSTRSteering", "gamepadSmoothness", self.gamepadSmoothness.get())
            updateSettings()
            
        
        def update(self): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)