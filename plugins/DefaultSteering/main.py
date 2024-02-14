"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""



from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="DefaultSteering", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will use the LaneDetection data to output steering.",
    version="0.2",
    author="Tumppi066, Erdosis",
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
import cv2
import keyboard as kb
from tkinter import messagebox
import src.controls as controls
import time

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
    global offset
    global gamepadMode
    global gamepadSmoothness
    global enableDisable
    global keyboard
    global lanechangingnavdetection
    global keyboardControlValue
    global keyboardSensitivity
    global keyboardReturnSensitivity
    global sensitivity # determines how hard the system reacts to the current error. AKA: Proportional Gain
    global integralgain # deals with errors that accumulate over time, should be zero since it's a video game. No wind here! 
    global derivativegain # anticipates future errors based on the rate of change.
        
    maximumControl = verifySetting("DefaultSteering", "maximumControl", 0.2)
    controlSmoothness = verifySetting("DefaultSteering", "smoothness", 4)
    sensitivity = verifySetting("DefaultSteering", "sensitivity", 0.4)
    offset = verifySetting("DefaultSteering", "offset", 0)
    gamepadMode = verifySetting("DefaultSteering", "gamepad", False)
    gamepadSmoothness = verifySetting("DefaultSteering", "gamepadSmoothness", 0.05)
    enableDisable = verifySetting("DefaultSteering", "enableDisable", 5)
    
    keyboard = verifySetting("DefaultSteering", "keyboard", False)
    
    keyboardControlValue = 0
    keyboardSensitivity = verifySetting("DefaultSteering", "keyboardSensitivity", 0.5)
    keyboardReturnSensitivity = verifySetting("DefaultSteering", "keyboardReturnSensitivity", 0.2)

    lanechangingnavdetection = settings.GetSettings("NavigationDetectionV2", "lanechanging", True)

    integralgain = verifySetting("DefaultSteering", "integralgain", 0.0)
    derivativegain = verifySetting("DefaultSteering", "derivativegain", 0.0)
    
    
updateSettings()

# MOST OF THIS FILE IS COPIED FROM THE OLD VERSION
desiredControl = 0
lastDesiredControl = 0
lastFrame = 0
indicatingRight = False
indicatingLeft = False
enabled = True
isHolding = False
keyboardControlValue = 0
integral_error = 0.0
previous_error = 0.0
lastFrameTime = 0
derivative_buffer = []
derivative_buffer_max_len = 100

def plugin(data):
    global desiredControl
    global lastDesiredControl
    global enabled
    global indicatingRight
    global indicatingLeft
    global maximumControl
    global controlSmoothness
    global sensitivity
    global offset
    global gamepadMode
    global gamepadSmoothness
    global lastFrame
    global enableDisable
    global isHolding
    global keyboard
    global keyboardControlValue
    global keyboardSensitivity
    global keyboardReturnSensitivity
    global integralgain 
    global derivativegain 
    global lastFrameTime
    global integral_error
    global previous_error
    global derivative_buffer
    global derivative_buffer_max_len


    data["controller"] = {}

    def get_speed():
        try:
            speed = abs(data["api"]["truckFloat"]["speed"]) or 1
        except KeyError:  # More specific exception
            speed = 50
        return speed

    def update_control_value(direction, sensitivity, speed):
        global keyboardControlValue
        if direction == "left":
            decrement = sensitivity / speed
            if keyboardControlValue < -1:
                keyboardControlValue = -1
            elif keyboardControlValue > 0:
                keyboardControlValue -= (1 + decrement) / speed
            else:
                keyboardControlValue -= decrement
        elif direction == "right":
            increment = sensitivity / speed
            if keyboardControlValue > 1:
                keyboardControlValue = 1
            elif keyboardControlValue < 0:
                keyboardControlValue += (1 + increment) / speed
            else:
                keyboardControlValue += increment

    def adjust_control_towards_center(speed):
        global keyboardControlValue
        global keyboardReturnSensitivity
        if keyboardControlValue > keyboardReturnSensitivity / speed:
            keyboardControlValue -= keyboardReturnSensitivity / speed
        elif keyboardControlValue < -keyboardReturnSensitivity / speed:
            keyboardControlValue += keyboardReturnSensitivity / speed
        else:
            keyboardControlValue = 0


    def get_indicating_state():
        global indicatingLeft, indicatingRight
        try:
            indicating_left = data["api"]["truckBool"]["blinkerLeftActive"]
            indicating_right = data["api"]["truckBool"]["blinkerRightActive"]
            indicating_state = indicating_left or indicating_right
            if indicating_state:
                if "NavigationDetection" in settings.GetSettings("Plugins", "Enabled"):
                    return False, False, indicating_state
            return indicating_state
        except KeyError: 
            return False, False, False
        
    def toggle_enabled_state():
        global enabled, isHolding 
        if enabled:
            enabled = False
            print("Disabled")
            sounds.PlaysoundFromLocalPath("assets/sounds/end.mp3")
        else:
            enabled = True
            print("Enabled")
            sounds.PlaysoundFromLocalPath("assets/sounds/start.mp3")
        isHolding = True

    def pid_controller(currentdesiredControl, lastDesiredControl):
        global integral_error, previous_error, lastFrameTime
        global sensitivity, integralgain, derivativegain
        
        currentTime = time.time()
        deltaTime = max(currentTime - lastFrameTime, 1e-4)  # Avoid division by zero
        lastFrameTime = currentTime  # Update for the next call

        integral_error += currentdesiredControl * deltaTime  # Accumulate error over time, considering function call rate
        current_derivative = (currentdesiredControl - lastDesiredControl) / deltaTime  # Rate of error change, considering function call rate

        derivative_buffer.append(current_derivative)
        if len(derivative_buffer) > derivative_buffer_max_len:
            derivative_buffer.pop(0) 
        if derivative_buffer:  # Check to avoid division by zero if the list is somehow empty
            smoothed_derivative = sum(derivative_buffer) / len(derivative_buffer)
        else:
            smoothed_derivative = 0
        

        # Compute the control value using PID formula
        pid_control_value = (sensitivity * currentdesiredControl) + (integralgain * integral_error) + (derivativegain/100 * smoothed_derivative)
        
        return pid_control_value
    

    def update_controller_input(input_value, lane_assist_enabled):
        global lastFrame, lastDesiredControl, controlSmoothness, indicatingLeft, indicatingRight, lanechangingnavdetection

        # Calculate the value based on whether we are in gamepad mode
        if gamepadMode:
            squared_value = pow(input_value, 2) if input_value >= 0 else -pow(input_value, 2)
            newValue = lastFrame + (squared_value - lastFrame) * gamepadSmoothness
            lastFrame = newValue
            control_value = newValue
        else:
            control_value = input_value

        # Check if lane assist is enabled or not
        if lane_assist_enabled:
            # Adjust control value based on control smoothness and desired control, if not indicating
            if not (indicatingLeft or indicatingRight) or lanechangingnavdetection:
                pid_control_value = pid_controller(desiredControl, lastDesiredControl) # Calculate PID value before user corrections
                # Clamp the control based on the maximum amount the user wants the wheel to turn
                clamped_desired_control = max(min(pid_control_value, maximumControl), -maximumControl)
                control_value = ((lastDesiredControl * controlSmoothness) + clamped_desired_control) / (controlSmoothness + 1) + pid_control_value

        # Update the control
        data["controller"]["leftStick"] = control_value
        if lane_assist_enabled:
            lastDesiredControl = ((lastDesiredControl * controlSmoothness) + clamped_desired_control) / (controlSmoothness + 1)

    speed = get_speed()
    lastFrameTime = time.time()
    
    try:
        desiredControl = data["LaneDetection"]["difference"] + offset
    except Exception as ex:
        if "LaneDetection" not in ex.args[0] and "difference" not in ex.args[0]:
            print(ex)
            
        desiredControl = lastDesiredControl * 0.9

    try:
        indicating_ui_state = get_indicating_state()
    except Exception as ex:
        print(ex)
        print("Most likely fix : change your indicator and or enable/disable buttons.")
        pass

    if controls.GetKeybindValue("Enable/Disable Steering") and not isHolding:
        toggle_enabled_state()
    elif not controls.GetKeybindValue("Enable/Disable Steering"):
        isHolding = False


    # Keyboard based control
    if keyboard:
                
        if controls.GetKeybindValue("Steer Left Key"):
            update_control_value("left", keyboardSensitivity, speed)
        elif controls.GetKeybindValue("Steer Right Key"):
            update_control_value("right", keyboardSensitivity, speed)
        else:
            adjust_control_towards_center(speed)

        try:
            if enabled:
                update_controller_input(keyboardControlValue, lane_assist_enabled=True)
            else:
                # If the lane assist is disabled, we just input the default control.
                update_controller_input(keyboardControlValue, lane_assist_enabled=False)
        except Exception as ex:
            print(ex)
        
    
    # Controller based control
    else:

        try:
            steeringAxisValue = controls.GetKeybindValue("Steering Axis")
            # Check if the SDK controller is enabled and vgamepad is not
            try:
                if "SDKController" in settings.GetSettings("Plugins", "Enabled") and "VGamepadController" not in settings.GetSettings("Plugins", "Enabled"):
                    steeringAxisValue = 0 # Don't pass the users control values to the game
            except:
                steeringAxisValue = 0 # Don't pass the users control values to the game
        except Exception as ex:
            print(ex)
            print("Most likely fix : change your indicator and or enable/disable buttons.")
            pass
        
        if enabled:
            update_controller_input(steeringAxisValue, lane_assist_enabled=True)
        else:
            # If the lane assist is disabled, we just input the default control.
            update_controller_input(steeringAxisValue, lane_assist_enabled=False)

    # Draw Correction UI
    def convert_to_rgb_if_necessary(image):
        try:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        except:
            return image

    def draw_steering_lines(output_img, w, h, value, color, thickness):
        divider = 5
        cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + value * (w/2 - w/divider)), int(h - h/10)), color, thickness, cv2.LINE_AA)

    def draw_text(output_img, text, target_width, position, font_scale=1, color=(0, 0, 0)):
        # Initial text size calculation
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
        max_count = 3
        while text_size[0] != target_width and max_count > 0:
            font_scale *= target_width / text_size[0] if text_size[0] != 0 else 1
            text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
            max_count -= 1
        font_thickness = max(round(font_scale * 2), 1)
        position = position[0], position[1] + text_size[1]
        cv2.putText(output_img, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, font_thickness, cv2.LINE_AA)
    
    try:
        output_img = convert_to_rgb_if_necessary(data["frame"])
        w, h = output_img.shape[1], output_img.shape[0]

        # Common line to indicate the background
        cv2.line(output_img, (int(w/5), int(h - h/10)), (int(4*w/5), int(h - h/10)), (100, 100, 100), 6, cv2.LINE_AA)
        enabled_position = (round(0.01*w), round(0.02*h))
        indicating_position = (round(0.99*w - w/4), round(0.02*h))
        if enabled:
            currentDesired = desiredControl * (1/maximumControl)
            actualSteering = lastDesiredControl * (1/maximumControl)
            draw_steering_lines(output_img, w, h, actualSteering, (0, 255, 100), 6)  # Actual steering
            draw_steering_lines(output_img, w, h, currentDesired, (0, 100, 255), 2)  # Desired steering
            if indicating_ui_state:
                draw_text(output_img, "Indicating", w/4, indicating_position, color=(0, 255, 255))
            draw_text(output_img, "Enabled", w/4, enabled_position, color=(0, 255, 0))
        else:
            wheelValue = keyboardControlValue if keyboard else (lastFrame if lastFrame != 0 else 0)
            draw_steering_lines(output_img, w, h, wheelValue, (0, 255, 100), 6)  # Wheel indication
            draw_text(output_img, "Disabled", w/4, enabled_position, color=(0, 0, 255))

        data["frame"] = output_img


    except Exception as ex:
        pass


    try:
        if data["controller"]["leftstick"] == None:
            data["controller"]["leftstick"] = 0
    except KeyError:
        data["controller"]["leftstick"] = 0

    return data # Plugins need to ALWAYS return the data


# Plugin UI
class UI:
    def __init__(self, master):
        self.master = master  # "master" is the main UI window
        self.setupUI()

    def setupUI(self):
        try:
            self.destroyUIIfExists()
            self.createCanvas()
            self.createNotebook()
            self.createFrames()
            self.populateGeneralFrame()
            self.populateGamepadFrame()
            self.populateKeyboardFrame()
            self.addFramesToNotebook()
            self.createSaveButton()
        except Exception as ex:
            print(ex)

    def destroyUIIfExists(self):
        try:
            self.root.destroy()  # Attempt to destroy the UI if it exists
        except AttributeError:
            pass  # If self.root doesn't exist, do nothing

    def createCanvas(self):
        self.root = tk.Canvas(self.master, width=700, height=520, border=0, highlightthickness=0)
        self.root.grid_propagate(False)  # Don't fit the canvas to the widgets
        self.root.pack_propagate(False)
        self.root.pack(anchor="center", expand=False)

    def createNotebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(anchor="center", fill="both", expand=True)

    def createFrames(self):
        self.generalFrame = ttk.Frame(self.notebook)
        self.gamepadFrame = ttk.Frame(self.notebook)
        self.keyboardFrame = ttk.Frame(self.notebook)

    def populateGeneralFrame(self):
        self.configureFrameLayout(self.generalFrame, 3)
        self.addLabel(self.generalFrame, "General", 0, 0, 3)
        self.addScales(self.generalFrame, [
            ("Steering Offset", "offset", -0.5, 0.5, 0.01),
            ("Control Smoothness", "smoothness", 0, 10, 1),
            ("Maximum Control", "maximumControl", 0, 1, 0.01),
            ("Sensitivity", "sensitivity", 0, 1, 0.01),
            #("Prediction Strength", "derivativegain", 0, 1, 0),
            #("Error Correction Strength", "integralgain", 0, 1, 0),
        ], start_row=1)

    def populateGamepadFrame(self):
        self.configureFrameLayout(self.gamepadFrame, 3)
        self.addLabel(self.gamepadFrame, "Gamepad", 0, 0, 3)
        self.addCheckButton(self.gamepadFrame, "Gamepad Mode", "gamepad", row=1, default=True)
        self.addScales(self.gamepadFrame, [
            ("Gamepad Smoothness", "gamepadSmoothness", 0, 0.4, 0.01)
        ], start_row=2) # Assuming the next available row after the checkbox is 2

    def populateKeyboardFrame(self):
        self.configureFrameLayout(self.keyboardFrame, 3)
        self.addLabel(self.keyboardFrame, "Keyboard", 0, 0, 3)
        self.addCheckButton(self.keyboardFrame, "Keyboard Mode", "keyboard", default=False, row=1)
        self.addScales(self.keyboardFrame, [
            ("Keyboard Sensitivity", "keyboardSensitivity", 0, 1, 0.01),
            ("Keyboard Return Sensitivity", "keyboardReturnSensitivity", 0, 1, 0.01),
        ], start_row=2) # Assuming the next available row after the checkbox is 2


    def addFramesToNotebook(self):
        self.notebook.add(self.generalFrame, text="General")
        self.notebook.add(self.gamepadFrame, text="Gamepad")
        self.notebook.add(self.keyboardFrame, text="Keyboard")

    def createSaveButton(self):
        ttk.Button(self.root, text="Save", command=self.save, width=20).pack(anchor="center", pady=10)

    def configureFrameLayout(self, frame, num_columns):
        for i in range(num_columns):
            frame.columnconfigure(i, weight=1)

    def save(self):
    # Dynamically access each attribute based on its setting key and save the settings
        settings_keys = [
            "offset", "smoothness", "sensitivity", "derivativegain",
            "integralgain", "maximumControl", "gamepad", "gamepadSmoothness",
            "keyboard", "keyboardSensitivity", "keyboardReturnSensitivity"
        ]
        for key in settings_keys:
            setting_value = getattr(self, key).get()  # Use getattr to dynamically access the attribute
            settings.CreateSettings("DefaultSteering", key, setting_value)
        updateSettings()


    def addLabel(self, frame, text, row, column, columnspan, font=("Robot", 12, "bold")):
        ttk.Label(frame, text=text, font=font).grid(row=row, column=column, columnspan=columnspan)

    def addScales(self, frame, scale_info, start_row):
        for idx, (label, setting_key, from_, to, resolution) in enumerate(scale_info, start=start_row):
            scale = tk.Scale(frame, from_=from_, to=to, orient="horizontal", length=500, resolution=resolution, label=label)
            scale.grid(row=idx, column=0, columnspan=3, pady=0)
            value = settings.GetSettings("DefaultSteering", setting_key)
            if value is None: value = from_ + (to - from_) / 2  # Default to midpoint if not set
            scale.set(value)
            setattr(self, setting_key, scale)  # Save the scale widget as an attribute of the UI object


    def addCheckButton(self, frame, label, setting_key, row, column=0, columnspan=3, default=False):
        var = tk.BooleanVar(value=settings.GetSettings("DefaultSteering", setting_key) if settings.GetSettings("DefaultSteering", setting_key) is not None else default)
        checkButton = tk.Checkbutton(frame, text=label, variable=var)
        checkButton.grid(row=row, column=column, columnspan=columnspan, sticky="w", padx=(70, 0))
        setattr(self, setting_key, var)  # Store the variable for later retrieval




    def update(self, data):
        self.root.update() # When the panel is open this function is called each frame 
