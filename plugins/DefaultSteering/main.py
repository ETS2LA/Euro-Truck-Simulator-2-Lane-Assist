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
    dynamicOrder="before controller" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.sounds as sounds
import os
import pygame
import cv2
import keyboard as kb
from tkinter import messagebox


pygame.joystick.init()
pygame.display.init()

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
    global keyboard
    global enableDisableKey
    global rightIndicatorKey
    global leftIndicatorKey
    global useAPI
    
    try:
        wheel = pygame.joystick.Joystick(verifySetting("DefaultSteering", "controller", 0))
    except:
        try:    
            wheel = pygame.joystick.Joystick(0)
            messagebox.showinfo("DefaultSteering", "Controller setup changed, defaulting to controller 0.")
            settings.CreateSettings("DefaultSteering", "controller", 0)
        except:
            wheel = None
        
    
    rightIndicator = verifySetting("DefaultSteering", "rightIndicator", 13)
    leftIndicator = verifySetting("DefaultSteering", "leftIndicator", 14)
    steeringAxis = verifySetting("DefaultSteering", "steeringAxis", 0)
    maximumControl = verifySetting("DefaultSteering", "maximumControl", 0.2)
    controlSmoothness = verifySetting("DefaultSteering", "smoothness", 8)
    sensitivity = verifySetting("DefaultSteering", "sensitivity", 0.4)
    offset = verifySetting("DefaultSteering", "offset", 0)
    gamepadMode = verifySetting("DefaultSteering", "gamepad", False)
    gamepadSmoothness = verifySetting("DefaultSteering", "gamepadSmoothness", 0.05)
    enableDisable = verifySetting("DefaultSteering", "enableDisable", 5)
    useAPI = verifySetting("DefaultSteering", "useAPI", False)
    
    keyboard = verifySetting("DefaultSteering", "keyboard", False)
    enableDisableKey = verifySetting("DefaultSteering", "enableDisableKey", "n")
    rightIndicatorKey = verifySetting("DefaultSteering", "rightIndicatorKey", "e")
    leftIndicatorKey = verifySetting("DefaultSteering", "leftIndicatorKey", "q")
    
    
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
    global keyboard
    global enableDisableKey
    global rightIndicatorKey
    global leftIndicatorKey
    global keyboardControlValue
    # global disableLaneAssistWhenIndicating

    try:
        desiredControl = data["LaneDetection"]["difference"] * sensitivity + offset
    except Exception as ex:
        if "LaneDetection" not in ex.args[0]:
            print(ex)
            
        desiredControl = oldDesiredControl
        
    data["controller"] = {}

    try:
        data["api"]
        apiAvailable = True
    except:
        apiAvailable = False


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
        
        if kb.is_pressed("a") and keyboardControlValue > -1:
            keyboardControlValue -= 0.5 / speed
            if keyboardControlValue > 0:
                keyboardControlValue -= 1 / speed
        elif kb.is_pressed("d") and keyboardControlValue < 1:
            keyboardControlValue += 0.5 / speed
            if keyboardControlValue < 0:
                keyboardControlValue += 1 / speed
        else:
            # Move closer to the center
            if keyboardControlValue > 0.2 / speed:
                keyboardControlValue -= 0.2 / speed
            elif keyboardControlValue < -0.2 / speed:
                keyboardControlValue += 0.2 / speed
            else:
                keyboardControlValue = 0
            
        
        try:
            IndicatingLeft = data["api"]["truckBool"]["blinkerLeftActive"]
            IndicatingRight = data["api"]["truckBool"]["blinkerRightActive"]

            enabledTimer += 1 # Frames, this helps to prevent accidentally enabling disabling multiple times.
            if(kb.is_pressed(enableDisableKey) and enabledTimer > 15):
                if enabled == True:
                    enabled = False
                    print("Disabled")
                    enabledTimer = 0
                    sounds.PlaySound("assets/sounds/end.mp3")
                else:
                    enabled = True
                    print("Enabled")
                    enabledTimer = 0
                    sounds.PlaySound("assets/sounds/start.mp3")

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

            if(wheel.get_button(enableDisable) and enabledTimer > 15):
                if enabled == True:
                    enabled = False
                    print("Disabled")
                    enabledTimer = 0
                    sounds.PlaySound("assets/sounds/end.mp3")
                else:
                    enabled = True
                    print("Enabled")
                    enabledTimer = 0
                    sounds.PlaySound("assets/sounds/start.mp3")

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
            
            if not keyboard:
                if lastFrame != 0:
                    wheelValue = lastFrame
                else:
                    wheelValue = wheel.get_axis(steeringAxis)
            else:
                wheelValue = keyboardControlValue
            # First draw a gray line to indicate the background
            cv2.line(output_img, (int(w/divider), int(h - h/10)), (int(w/divider*(divider-1)), int(h - h/10)), (100, 100, 100), 6, cv2.LINE_AA)
            # Then draw a light green line to indicate the wheel
            cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + wheelValue * (w/2 - w/divider)), int(h - h/10)), (0, 255, 100), 6, cv2.LINE_AA)

            # Also draw a disabled text to the top left
            cv2.putText(output_img, "Disabled", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            
            data["frame"] = output_img

    except Exception as ex:
        pass

    try:
        if data["controller"]["leftstick"] == None:
            data["controller"]["leftstick"] = 0
            print("Leftstick was None, setting it to 0")
    except KeyError:
        print("Leftstick was None, setting it to 0")
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
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Create a notebook 
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            controllerFrame = ttk.Frame(notebook)
            controllerFrame.pack()
            gamepadFrame = ttk.Frame(notebook)
            gamepadFrame.pack()
            keyboardFrame = ttk.Frame(notebook)
            keyboardFrame.pack()
            
            # Scuffed way to get the settings to be in the center
            generalFrame.columnconfigure(0, weight=1)
            generalFrame.columnconfigure(1, weight=1)
            generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)
            self.offset = helpers.MakeComboEntry(generalFrame, "Steering Offset", "DefaultSteering", "offset", 1, 1, width=12, value=-0.2, isFloat=True)
            self.smoothness = helpers.MakeComboEntry(generalFrame, "Smoothening", "DefaultSteering", "smoothness", 2, 1, width=12, value=8)
            self.sensitivity = helpers.MakeComboEntry(generalFrame, "Sensitivity", "DefaultSteering", "sensitivity", 3, 1, width=12, value=0.6, isFloat=True)
            self.maximumControl = helpers.MakeComboEntry(generalFrame, "Maximum Control", "DefaultSteering", "maximumControl", 4, 1, isFloat=True, width=12, value=0.2)
            self.useAPI = helpers.MakeCheckButton(generalFrame, "Use ETS2/ATS API", "DefaultSteering", "useAPI", 5, 1, width=15, default=False)
            
            controllerFrame.columnconfigure(0, weight=1)
            controllerFrame.columnconfigure(1, weight=1)
            controllerFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(controllerFrame, "Controller (indexes)", 5, 0, font=("Robot", 12, "bold"), columnspan=3)
            
            # List of controllers
            pygame.event.pump()

            self.joysticks = pygame.joystick.get_count()
            self.joysticks = [pygame.joystick.Joystick(i) for i in range(self.joysticks)]
            
            self.listVariable = tk.StringVar(controllerFrame)
            self.listVariable.set([j.get_name() for j in self.joysticks])
            
            self.list = tk.Listbox(controllerFrame, width=50, height=4, listvariable=self.listVariable, selectmode="single")
            self.list.grid(row=6, column=0, columnspan=3, padx=30, pady=10)
            
            # Select the current controller by default
            try:
                self.list.selection_set(settings.GetSettings("DefaultSteering", "controller"))
            except:
                pass
            
            self.steeringAxis = helpers.MakeComboEntry(controllerFrame, "Steering Axis", "DefaultSteering", "steeringAxis", 7, 1, width=12, value=0)
            self.enableDisable = helpers.MakeComboEntry(controllerFrame, "Enable/Disable", "DefaultSteering", "enableDisable", 8, 1, width=12, value=5)
            # self.rightIndicator = helpers.MakeComboEntry(controllerFrame, "Right Indicator", "DefaultSteering", "rightIndicator", 9, 1, width=12, value=13)
            # self.leftIndicator = helpers.MakeComboEntry(controllerFrame, "Left Indicator", "DefaultSteering", "leftIndicator", 10, 1, width=12, value=14)
            # Make a slider to show the current axis value
            helpers.MakeLabel(controllerFrame, "Steering Axis Value: ", 11, 0, columnspan=3, pady=0)
            self.slider = tk.Scale(controllerFrame, from_=-1, to=1, orient="horizontal", length=500, resolution=0.01)
            self.slider.grid(row=12, column=0, columnspan=3, pady=0)
            
            helpers.MakeLabel(controllerFrame, "Pressed Controller Buttons: ", 13, 0, columnspan=3)
            self.pressedControllerButtons = helpers.MakeLabel(controllerFrame, "", 14, 0, columnspan=3)
            
            gamepadFrame.columnconfigure(0, weight=1)
            gamepadFrame.columnconfigure(1, weight=1)
            gamepadFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(gamepadFrame, "Gamepad", 0, 0, font=("Robot", 12, "bold"), columnspan=3)
            self.gamepad = helpers.MakeCheckButton(gamepadFrame, "Gamepad Mode", "DefaultSteering", "gamepad", 1, 1, width=15, default=True)
            self.gamepadSmoothness = helpers.MakeComboEntry(gamepadFrame, "Gamepad Smoothness", "DefaultSteering", "gamepadSmoothness", 2, 1, isFloat=True, width=12, labelwidth=18, value=0.05)
            
            keyboardFrame.columnconfigure(0, weight=1)
            keyboardFrame.columnconfigure(1, weight=1)
            keyboardFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(keyboardFrame, "Keyboard", 3, 0, font=("Robot", 12, "bold"), columnspan=3)
            self.keyboard = helpers.MakeCheckButton(keyboardFrame, "Keyboard Mode", "DefaultSteering", "keyboard", 4, 1, width=15, default=False)
            self.enableDisableKey = helpers.MakeComboEntry(keyboardFrame, "Enable/Disable Key", "DefaultSteering", "enableDisableKey", 5, 1, width=12, value="n", isString=True)
            # self.rightIndicatorKey = helpers.MakeComboEntry(keyboardFrame, "Right Indicator Key", "DefaultSteering", "rightIndicatorKey", 6, 1, width=12, value="e", isString=True)
            # self.leftIndicatorKey = helpers.MakeComboEntry(keyboardFrame, "Left Indicator Key", "DefaultSteering", "leftIndicatorKey", 7, 1, width=12, value="q", isString=True)
            
            notebook.add(generalFrame, text="General")
            notebook.add(controllerFrame, text="Controller")
            notebook.add(gamepadFrame, text="Gamepad")
            notebook.add(keyboardFrame, text="Keyboard")
            
            ttk.Button(self.root, text="Save", command=self.save, width=20).pack(anchor="center", pady=10)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
            
        
        def save(self):
            settings.CreateSettings("DefaultSteering", "offset", self.offset.get())
            settings.CreateSettings("DefaultSteering", "smoothness", self.smoothness.get())
            settings.CreateSettings("DefaultSteering", "sensitivity", self.sensitivity.get())
            settings.CreateSettings("DefaultSteering", "maximumControl", self.maximumControl.get())
            settings.CreateSettings("DefaultSteering", "steeringAxis", self.steeringAxis.get())
            settings.CreateSettings("DefaultSteering", "enableDisable", self.enableDisable.get())
            # settings.CreateSettings("DefaultSteering", "rightIndicator", self.rightIndicator.get())
            # settings.CreateSettings("DefaultSteering", "leftIndicator", self.leftIndicator.get())
            try:
                controller = self.list.curselection()[0]
            except:
                controller = self.list.curselection()
            settings.CreateSettings("DefaultSteering", "controller", controller)
            settings.CreateSettings("DefaultSteering", "gamepad", self.gamepad.get())
            settings.CreateSettings("DefaultSteering", "gamepadSmoothness", self.gamepadSmoothness.get())
            settings.CreateSettings("DefaultSteering", "keyboard", self.keyboard.get())
            settings.CreateSettings("DefaultSteering", "enableDisableKey", self.enableDisableKey.get())
            # settings.CreateSettings("DefaultSteering", "rightIndicatorKey", self.rightIndicatorKey.get())
            # settings.CreateSettings("DefaultSteering", "leftIndicatorKey", self.leftIndicatorKey.get())
            updateSettings()
            
        
        def update(self, data): # When the panel is open this function is called each frame 
            pygame.event.pump()
            try:
                
                value = ""
                for i in range(self.joysticks[settings.GetSettings("DefaultSteering", "controller")].get_numbuttons()):
                    if self.joysticks[settings.GetSettings("DefaultSteering", "controller")].get_button(i):
                        value += (" Button " + str(i))
                self.pressedControllerButtons.set(value)
                
                self.slider.set(self.joysticks[settings.GetSettings("DefaultSteering", "controller")].get_axis(settings.GetSettings("DefaultSteering", "steeringAxis")))
                
            except Exception as ex:
                print(ex) 
                pass
            
            self.root.update()
            
    
    
    except Exception as ex:
        print(ex.args)