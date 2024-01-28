"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""



from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="DefaultSteering", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will use the LaneDetection data to output steering.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before controller", # Will run the plugin before anything else in the mainloop (data will be empty)
    requires=["TruckSimAPI"]
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.sounds as sounds
from src.translator import Translate
import os
import pygame
import cv2
import keyboard as kb
from tkinter import messagebox
import src.controls as controls

pygame.joystick.init()
pygame.display.init()

controls.RegisterKeybind("Enable/Disable Steering", 
                         defaultButtonIndex="n", 
                         notBoundInfo="You should bind this. It's useful to have on hand.",
                         description="Enable or disable the steering.")
controls.RegisterKeybind("Steering Axis", 
                         axis=True, 
                         notBoundInfo="This is optional when using a keyboard.",
                         description="The steering axis. Not used when in keyboard mode.")
controls.RegisterKeybind("Steer Left Key", 
                         defaultButtonIndex="a", 
                         notBoundInfo="This is optional when using a controller.",
                         description="Steer left key. Not used when in controller mode.")
controls.RegisterKeybind("Steer Right Key", 
                         defaultButtonIndex="d", 
                         notBoundInfo="This is optional when using a controller.",
                         description="Steer right key. Not used when in controller mode.")

def onEnable():
    pass

def onDisable():
    pass

def verifySetting(category, key, default):
    value = settings.GetSettings(category, key)
    
    if value == None:
        value = default
        settings.CreateSettings(category, key, default)
        
    return value

lastWheelIndex = -1
def updateSettings():
    global lastWheelIndex
    global maximumControl
    global controlSmoothness
    global sensitivity
    global offset
    global gamepadMode
    global gamepadSmoothness
    global enableDisable
    global keyboard
    global lanechangingnavdetection
    global keyboardSensitivity
    global keyboardReturnSensitivity
        
    maximumControl = verifySetting("DefaultSteering", "maximumControl", 0.2)
    controlSmoothness = verifySetting("DefaultSteering", "smoothness", 4)
    sensitivity = verifySetting("DefaultSteering", "sensitivity", 0.4)
    offset = verifySetting("DefaultSteering", "offset", 0)
    gamepadMode = verifySetting("DefaultSteering", "gamepad", False)
    gamepadSmoothness = verifySetting("DefaultSteering", "gamepadSmoothness", 0.05)
    enableDisable = verifySetting("DefaultSteering", "enableDisable", 5)
    
    keyboard = verifySetting("DefaultSteering", "keyboard", False)
    
    keyboardSensitivity = verifySetting("DefaultSteering", "keyboardSensitivity", 0.5)
    keyboardReturnSensitivity = verifySetting("DefaultSteering", "keyboardReturnSensitivity", 0.2)

    lanechangingnavdetection = settings.GetSettings("NavigationDetectionV2", "lanechanging", True)
    
    
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
keyboardControlValue = 0
def plugin(data):
    global desiredControl
    global oldDesiredControl
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
    global keyboard
    global keyboardControlValue
    global keyboardSensitivity
    global keyboardReturnSensitivity
    # global disableLaneAssistWhenIndicating

    try:
        desiredControl = data["LaneDetection"]["difference"] * sensitivity + offset
    except Exception as ex:
        if "LaneDetection" not in ex.args[0] and "difference" not in ex.args[0]:
            print(ex)
            
        desiredControl = oldDesiredControl * 0.9
        

    try:
        testData = data["api"]
        if testData == None:
            apiAvailable = False
        else:
            apiAvailable = True
    except:
        apiAvailable = False

    data["controller"] = {}

    # Keyboard based control
    if keyboard:
        try:
            speed = data["api"]["truckFloat"]["speed"]
            if speed < 0:
                speed = -speed
            if speed == 0:
                speed = 1
        except:
            speed = 50
        
        if controls.GetKeybindValue("Steer Left Key"):
            if keyboardControlValue < -1:
                keyboardControlValue = -1
            else:
                keyboardControlValue -= keyboardSensitivity / speed
                if keyboardControlValue > 0:
                    keyboardControlValue -= 1 / speed
        elif controls.GetKeybindValue("Steer Right Key"):
            if keyboardControlValue > 1:
                keyboardControlValue = 1
            else:
                keyboardControlValue += keyboardSensitivity / speed
                if keyboardControlValue < 0:
                    keyboardControlValue += 1 / speed
        else:
            # Move closer to the center
            if keyboardControlValue > keyboardReturnSensitivity / speed:
                keyboardControlValue -= keyboardReturnSensitivity / speed
            elif keyboardControlValue < -keyboardReturnSensitivity / speed:
                keyboardControlValue += keyboardReturnSensitivity / speed
            else:
                keyboardControlValue = 0
            
        
        try:
            IndicatingLeft = data["api"]["truckBool"]["blinkerLeftActive"]
            IndicatingRight = data["api"]["truckBool"]["blinkerRightActive"]
            if IndicatingLeft == True or IndicatingRight == True:
                if "NavigationDetection" in settings.GetSettings("Plugins", "Enabled"):
                    IndicatingLeft = False
                    IndicatingRight = False

            enabledTimer += 1 # Frames, this helps to prevent accidentally enabling disabling multiple times.
            if(controls.GetKeybindValue("Enable/Disable Steering") and enabledTimer > 15):
                if enabled == True:
                    enabled = False
                    print("Disabled")
                    enabledTimer = 0
                    sounds.PlaysoundFromLocalPath("assets/sounds/end.mp3")
                else:
                    enabled = True
                    print("Enabled")
                    enabledTimer = 0
                    sounds.PlaysoundFromLocalPath("assets/sounds/start.mp3")

            try:
                pygame.event.pump() # Update the controller values

                # Main controller update loop.
                if(enabled):
                    # Clamp the control
                    if desiredControl > maximumControl:
                        desiredControl = maximumControl
                    if desiredControl < -maximumControl:
                        desiredControl = -maximumControl

                    if lanechangingnavdetection == False:
                        # If we are indicating, then disable the automatic control.
                        if(IndicatingRight or IndicatingLeft):
                            if gamepadMode:
                                value = pow(keyboardControlValue, 2) 
                                if(keyboardControlValue < 0) : value = -value
                                newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                                lastFrame = newValue
                                data["controller"]["leftStick"] = newValue
                            else:
                                data["controller"]["leftStick"] = keyboardControlValue
                        else:
                            if gamepadMode:
                                value = pow(keyboardControlValue, 2) 
                                if(keyboardControlValue < 0) : value = -value
                                newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                                lastFrame = newValue
                                data["controller"]["leftStick"] = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + newValue
                            else:
                                data["controller"]["leftStick"] = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + keyboardControlValue
                    else:
                        if gamepadMode:
                            value = pow(keyboardControlValue, 2) 
                            if(keyboardControlValue < 0) : value = -value
                            newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                            lastFrame = newValue
                            data["controller"]["leftStick"] = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + newValue
                        else:
                            data["controller"]["leftStick"] = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + keyboardControlValue


                    oldDesiredControl = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1)
                else:
                    # If the lane assist is disabled we just input the default control.
                    if gamepadMode:
                        value = pow(keyboardControlValue, 2) 
                        if(keyboardControlValue < 0) : value = -value
                        newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                        lastFrame = newValue
                        data["controller"]["leftStick"] = newValue
                    else:
                        data["controller"]["leftStick"] = keyboardControlValue
                
            except Exception as ex:
                print(ex)
                pass
        except Exception as ex:
            print(ex)
            pass
    
    # Controller based control
    else:
        try:
            enabledTimer += 1
            IndicatingLeft = data["api"]["truckBool"]["blinkerLeftActive"]
            IndicatingRight = data["api"]["truckBool"]["blinkerRightActive"]
            if IndicatingLeft == True:
                IndicatingLeft_original = True
            else:
                IndicatingLeft_original = False
            if IndicatingRight == True:
                IndicatingRight_original = True
            else:
                IndicatingRight_original = False
            if IndicatingLeft == True or IndicatingRight == True:
                if "NavigationDetection" in settings.GetSettings("Plugins", "Enabled"):
                    IndicatingLeft = False
                    IndicatingRight = False

            if(controls.GetKeybindValue("Enable/Disable Steering") and enabledTimer > 15):
                if enabled == True:
                    enabled = False
                    print("Disabled")
                    enabledTimer = 0
                    sounds.PlaysoundFromLocalPath("assets/sounds/end.mp3")
                else:
                    enabled = True
                    print("Enabled")
                    enabledTimer = 0
                    sounds.PlaysoundFromLocalPath("assets/sounds/start.mp3")

            try:
                pygame.event.pump() # Update the controller values
                steeringAxisValue = controls.GetKeybindValue("Steering Axis")
                # Check if the SDK controller is enabled and vgamepad is not
                try:
                    if "SDKController" in settings.GetSettings("Plugins", "Enabled") and "VGamepadController" not in settings.GetSettings("Plugins", "Enabled"):
                        steeringAxisValue = 0 # Don't pass the users control values to the game
                except:
                    steeringAxisValue = 0 # Don't pass the users control values to the game
                    
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
                            value = pow(steeringAxisValue, 2) 
                            if(steeringAxisValue < 0) : value = -value
                            newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                            lastFrame = newValue
                            data["controller"]["leftStick"] = newValue
                        else:
                            data["controller"]["leftStick"] = steeringAxisValue
                    else:
                        if gamepadMode:
                            value = pow(steeringAxisValue, 2) 
                            if(steeringAxisValue < 0) : value = -value
                            newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                            lastFrame = newValue
                            data["controller"]["leftStick"] = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + newValue
                        else:
                            data["controller"]["leftStick"] = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1) + steeringAxisValue
                    
                    oldDesiredControl = ((oldDesiredControl*controlSmoothness)+desiredControl)/(controlSmoothness+1)
                else:
                    # If the lane assist is disabled we just input the default control.
                    if gamepadMode:
                        value = pow(steeringAxisValue, 2) 
                        if(steeringAxisValue < 0) : value = -value
                        newValue = lastFrame + (value - lastFrame) * gamepadSmoothness
                        lastFrame = newValue
                        data["controller"]["leftStick"] = newValue
                    else:
                        data["controller"]["leftStick"] = steeringAxisValue
                
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
            try:
                output_img = cv2.cvtColor(data["frame"], cv2.COLOR_GRAY2RGB)
            except:
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
                if IndicatingLeft_original or IndicatingRight_original:
                    current_text = "Indicating"
                    width_target_current_text = w/4
                    fontscale_current_text = 1
                    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                    width_current_text, height_current_text = textsize_current_text
                    max_count_current_text = 3
                    while width_current_text != width_target_current_text:
                        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
                        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                        width_current_text, height_current_text = textsize_current_text
                        max_count_current_text -= 1
                        if max_count_current_text <= 0:
                            break
                    fontthickness_current_text = round(fontscale_current_text*2)
                    if fontthickness_current_text <= 0:
                        fontthickness_current_text = 1
                    cv2.putText(output_img, "Indicating", (round(0.99*w - width_current_text), round(0.02*w + height_current_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 255, 255), fontthickness_current_text, cv2.LINE_AA)
            except:
                pass    
            
            # Also draw a enabled text to the top left
            current_text = "Enabled"
            width_target_current_text = w/4
            fontscale_current_text = 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text = 3
            while width_current_text != width_target_current_text:
                fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
                textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                width_current_text, height_current_text = textsize_current_text
                max_count_current_text -= 1
                if max_count_current_text <= 0:
                    break
            fontthickness_current_text = round(fontscale_current_text*2)
            if fontthickness_current_text <= 0:
                fontthickness_current_text = 1
            cv2.putText(output_img, "Enabled", (round(0.01*w), round(0.02*w)+height_current_text), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 255, 0), fontthickness_current_text, cv2.LINE_AA)
            
            data["frame"] = output_img
        else:
            try:
                output_img = cv2.cvtColor(data["frame"], cv2.COLOR_GRAY2RGB)
            except:
                output_img = data["frame"]
            w = output_img.shape[1]
            h = output_img.shape[0]
            
            divider = 5
            
            if not keyboard:
                if lastFrame != 0:
                    wheelValue = lastFrame
                else:
                    try:
                        wheelValue = wheel.get_axis(steeringAxis)
                    except:
                        wheelValue = 0
            else:
                wheelValue = keyboardControlValue
            # First draw a gray line to indicate the background
            cv2.line(output_img, (int(w/divider), int(h - h/10)), (int(w/divider*(divider-1)), int(h - h/10)), (100, 100, 100), 6, cv2.LINE_AA)
            # Then draw a light green line to indicate the wheel
            cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + wheelValue * (w/2 - w/divider)), int(h - h/10)), (0, 255, 100), 6, cv2.LINE_AA)

            # Also draw a disabled text to the top left
            current_text = "Enabled" # Using text "Enabled" to keep the same text size
            width_target_current_text = w/4
            fontscale_current_text = 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text = 3
            while width_current_text != width_target_current_text:
                fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
                textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                width_current_text, height_current_text = textsize_current_text
                max_count_current_text -= 1
                if max_count_current_text <= 0:
                    break
            fontthickness_current_text = round(fontscale_current_text*2)
            if fontthickness_current_text <= 0:
                fontthickness_current_text = 1
            cv2.putText(output_img, "Disabled", (round(0.01*w), round(0.02*w)+height_current_text), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), fontthickness_current_text, cv2.LINE_AA)
            
            
            data["frame"] = output_img

    except Exception as ex:
        pass

    try:
        if data["controller"]["leftstick"] == None:
            data["controller"]["leftstick"] = 0
    except KeyError:
        data["controller"]["leftstick"] = 0

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
            
            self.root = tk.Canvas(self.master, width=700, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Create a notebook 
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            gamepadFrame = ttk.Frame(notebook)
            gamepadFrame.pack()
            keyboardFrame = ttk.Frame(notebook)
            keyboardFrame.pack()
            
            # Scuffed way to get the settings to be in the center
            generalFrame.columnconfigure(0, weight=1)
            generalFrame.columnconfigure(1, weight=1)
            generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)
            # self.offset = helpers.MakeComboEntry(generalFrame, "Steering Offset", "DefaultSteering", "offset", 1, 1, width=12, value=-0.2, isFloat=True)
            self.offset = tk.Scale(generalFrame, from_=-0.5, to=0.5, orient="horizontal", length=500, resolution=0.01, label=Translate("Steering Offset"))
            self.offset.grid(row=1, column=0, columnspan=3, pady=0)
            value = settings.GetSettings("DefaultSteering", "offset")
            if value == None: value = 0.0
            self.offset.set(value)
            
            self.smoothness = tk.Scale(generalFrame, from_=0, to=10, orient="horizontal", length=500, resolution=1, label=Translate("Control Smoothness"))
            self.smoothness.grid(row=2, column=0, columnspan=3, pady=0)
            value = settings.GetSettings("DefaultSteering", "smoothness")
            if value == None: value = 4
            self.smoothness.set(value)
            
            self.sensitivity = tk.Scale(generalFrame, from_=0, to=1, orient="horizontal", length=500, resolution=0.01, label=Translate("Sensitivity"))
            self.sensitivity.grid(row=3, column=0, columnspan=3, pady=0)
            value = settings.GetSettings("DefaultSteering", "sensitivity")
            if value == None: value = 0.4
            self.sensitivity.set(value)
            
            self.maximumControl = tk.Scale(generalFrame, from_=0, to=1, orient="horizontal", length=500, resolution=0.01, label=Translate("Maximum Control"))
            self.maximumControl.grid(row=4, column=0, columnspan=3, pady=0)
            value = settings.GetSettings("DefaultSteering", "maximumControl")
            if value == None: value = 0.2
            self.maximumControl.set(value)
            
            
            gamepadFrame.columnconfigure(0, weight=1)
            gamepadFrame.columnconfigure(1, weight=1)
            gamepadFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(gamepadFrame, "Gamepad", 0, 0, font=("Robot", 12, "bold"), columnspan=3)
            self.gamepad = helpers.MakeCheckButton(gamepadFrame, "Gamepad Mode", "DefaultSteering", "gamepad", 1, 1, width=15, default=True)
            self.gamepadSmoothness = tk.Scale(gamepadFrame, from_=0, to=0.4, orient="horizontal", length=500, resolution=0.01, label=Translate("Gamepad Smoothness"))
            self.gamepadSmoothness.grid(row=2, column=0, columnspan=3, pady=0)
            value = settings.GetSettings("DefaultSteering", "gamepadSmoothness")
            if value == None: value = 0.05
            self.gamepadSmoothness.set(value)
            
            keyboardFrame.columnconfigure(0, weight=1)
            keyboardFrame.columnconfigure(1, weight=1)
            keyboardFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(keyboardFrame, "Keyboard", 3, 0, font=("Robot", 12, "bold"), columnspan=3)
            self.keyboard = helpers.MakeCheckButton(keyboardFrame, "Keyboard Mode", "DefaultSteering", "keyboard", 4, 1, width=15, default=False)
            
            self.keyboardSensitivity = tk.Scale(keyboardFrame, from_=0, to=1, orient="horizontal", length=500, resolution=0.01, label=Translate("Keyboard Sensitivity"))
            self.keyboardSensitivity.grid(row=6, column=0, columnspan=3, pady=0)
            value = settings.GetSettings("DefaultSteering", "keyboardSensitivity")
            if value == None: value = 0.5
            self.keyboardSensitivity.set(value)
            
            self.keyboardReturnSens = tk.Scale(keyboardFrame, from_=0, to=1, orient="horizontal", length=500, resolution=0.01, label=Translate("Keyboard Return Sensitivity"))
            self.keyboardReturnSens.grid(row=7, column=0, columnspan=3, pady=0)
            value = settings.GetSettings("DefaultSteering", "keyboardReturnSensitivity")
            if value == None: value = 0.2
            self.keyboardReturnSens.set(value)
            
            # self.rightIndicatorKey = helpers.MakeComboEntry(keyboardFrame, "Right Indicator Key", "DefaultSteering", "rightIndicatorKey", 6, 1, width=12, value="e", isString=True)
            # self.leftIndicatorKey = helpers.MakeComboEntry(keyboardFrame, "Left Indicator Key", "DefaultSteering", "leftIndicatorKey", 7, 1, width=12, value="q", isString=True)
            
            notebook.add(generalFrame, text=Translate("General"))
            notebook.add(gamepadFrame, text=Translate("Gamepad"))
            notebook.add(keyboardFrame, text=Translate("Keyboard"))
            
            ttk.Button(self.root, text="Save", command=self.save, width=20).pack(anchor="center", pady=10)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
            
        
        def save(self):
            settings.CreateSettings("DefaultSteering", "offset", self.offset.get())
            settings.CreateSettings("DefaultSteering", "smoothness", self.smoothness.get())
            settings.CreateSettings("DefaultSteering", "sensitivity", self.sensitivity.get())
            settings.CreateSettings("DefaultSteering", "maximumControl", self.maximumControl.get())
            # settings.CreateSettings("DefaultSteering", "rightIndicator", self.rightIndicator.get())
            # settings.CreateSettings("DefaultSteering", "leftIndicator", self.leftIndicator.get())
            settings.CreateSettings("DefaultSteering", "gamepad", self.gamepad.get())
            settings.CreateSettings("DefaultSteering", "gamepadSmoothness", self.gamepadSmoothness.get())
            settings.CreateSettings("DefaultSteering", "keyboard", self.keyboard.get())
            # settings.CreateSettings("DefaultSteering", "rightIndicatorKey", self.rightIndicatorKey.get())
            # settings.CreateSettings("DefaultSteering", "leftIndicatorKey", self.leftIndicatorKey.get())
            settings.CreateSettings("DefaultSteering", "keyboardSensitivity", self.keyboardSensitivity.get())
            settings.CreateSettings("DefaultSteering", "keyboardReturnSensitivity", self.keyboardReturnSens.get())
            updateSettings()
            
        
        def update(self, data): # When the panel is open this function is called each frame 
            pygame.event.pump()
            
            self.root.update()
            
    
    
    except Exception as ex:
        print(ex.args)