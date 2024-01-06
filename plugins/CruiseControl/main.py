"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import switchSelectedPlugin, resizeWindow

PluginInfo = PluginInformation(
    name="CruiseControl", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="this is a plugin which uses a virtual controller\nor virtual keyboard to set the in-game cruise control,\nuses TrafficLightDetection to stop at red traffc lights",
    version="0.1",
    author="Glas42",
    url="https://github.com/Glas42/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before game", # Will run the plugin before anything else in the mainloop (data will be empty)
    requires=["TruckSimAPI", "SDKController"]
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
from src.translator import Translate
from tkinter import messagebox
import os

import plugins.DefaultSteering.main as DefaultSteering
import time
import cv2

def UpdateSettings():
    global trafficlightdetectionisenabled
    global navigationdetectionisenabled
    global cruisecontrol_off_set
    global cruisecontrol_off_unset
    global cruisecontrol_off_slowed
    global cruisecontrol_on_set
    global cruisecontrol_on_unset
    global cruisecontrol_on_slowed
    global cruisecontrol_emergency_set
    global cruisecontrol_emergency_unset
    global cruisecontrol_emergency_slowed
    global auto_enable
    global stop_trafficlight
    global trafficlight_accelerate
    global auto_accelerate
    global auto_hazard
    global show_symbols
    global acceleration_strength
    global brake_strength
    global cruisespeed_turn
    global cruisespeed_trafficlight
    global wait_for_response
    global wait_for_response_timer
    global last_hazard_light
    global need_to_disable_hazard_light
    global wait_for_response_hazard_light
    global wait_for_response_hazard_light_timer
    global last_speed
    global last_speedlimit
    global last_cruisecontrolspeed
    global trafficlight_last_time_without
    global trafficlight_last_time_with
    global turnincoming_last_time_with
    global trafficlight_allow_acceleration
    global user_emergency_braking
    global user_emergency_braking_timer
    
    if "TrafficLightDetection" in settings.GetSettings("Plugins", "Enabled"):
        trafficlightdetectionisenabled = True
    else:
        trafficlightdetectionisenabled = False

    if "NavigationDetection" in settings.GetSettings("Plugins", "Enabled"):
        navigationdetectionisenabled = True
    else:
        navigationdetectionisenabled = False

    cruisecontrol_off_set = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_off_set.png")
    cruisecontrol_off_unset = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_off_unset.png")
    cruisecontrol_off_slowed = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_off_slowed.png")
    cruisecontrol_on_set = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_on_set.png")
    cruisecontrol_on_unset = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_on_unset.png")
    cruisecontrol_on_slowed = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_on_slowed.png")
    cruisecontrol_emergency_set = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_emergency_set.png")
    cruisecontrol_emergency_unset = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_emergency_unset.png")
    cruisecontrol_emergency_slowed = cv2.imread(variables.PATH + r"\assets\CruiseControl\cruisecontrol_emergency_slowed.png")

    auto_enable = settings.GetSettings("CruiseControl", "auto_enable", True)
    stop_trafficlight = settings.GetSettings("CruiseControl", "stop_trafficlight", True)
    trafficlight_accelerate = settings.GetSettings("CruiseControl", "trafficlight_accelerate", True)
    auto_accelerate = settings.GetSettings("CruiseControl", "auto_accelerate", False)
    auto_hazard = settings.GetSettings("CruiseControl", "auto_hazard", True)
    show_symbols = settings.GetSettings("CruiseControl", "show_symbols", True)
    acceleration_strength = settings.GetSettings("CruiseControl", "acceleration", 50)
    acceleration_strength /= 100
    brake_strength = settings.GetSettings("CruiseControl", "brake", 100)
    brake_strength /= 100

    cruisespeed_turn = 30
    cruisespeed_trafficlight = 0

    wait_for_response = False
    wait_for_response_timer = 0

    last_hazard_light = False
    need_to_disable_hazard_light = False
    wait_for_response_hazard_light = False
    wait_for_response_hazard_light_timer = 0

    last_speed = 0
    last_speedlimit = 0
    last_cruisecontrolspeed = 0
    trafficlight_last_time_without = 0
    trafficlight_last_time_with = 0
    turnincoming_last_time_with = 0

    trafficlight_allow_acceleration = False
    user_emergency_braking = False
    user_emergency_braking_timer = 0

def plugin(data):
    global trafficlightdetectionisenabled
    global navigationdetectionisenabled
    global cruisecontrol_off_set
    global cruisecontrol_off_unset
    global cruisecontrol_off_slowed
    global cruisecontrol_on_set
    global cruisecontrol_on_unset
    global cruisecontrol_on_slowed
    global cruisecontrol_emergency_set
    global cruisecontrol_emergency_unset
    global cruisecontrol_emergency_slowed
    global auto_enable
    global stop_trafficlight
    global trafficlight_accelerate
    global auto_accelerate
    global auto_hazard
    global show_symbols
    global acceleration_strength
    global brake_strength
    global cruisespeed_turn
    global cruisespeed_trafficlight
    global wait_for_response
    global wait_for_response_timer
    global last_hazard_light
    global need_to_disable_hazard_light
    global wait_for_response_hazard_light
    global wait_for_response_hazard_light_timer
    global last_speed
    global last_speedlimit
    global last_cruisecontrolspeed
    global trafficlight_last_time_without
    global trafficlight_last_time_with
    global turnincoming_last_time_with
    global trafficlight_allow_acceleration
    global user_emergency_braking
    global user_emergency_braking_timer

    current_time = time.time()

    try:
        speed = round(data["api"]["truckFloat"]["speed"]*3.6, 1)
        if speed > 5 and speed > last_speed:
            user_emergency_braking = False
        last_speed = speed
        speedlimit = round(data["api"]["truckFloat"]["speedLimit"]*3.6, 1)
        if speedlimit != 0 and speedlimit > 0:
            last_speedlimit = speedlimit
        cruisecontrolspeed = round(data["api"]["truckFloat"]["cruiseControlSpeed"]*3.6, 1)
        if data["api"]["truckFloat"]["userThrottle"] > 0.1:
            user_accelerating = True
        else:
            user_accelerating = False
        if data["api"]["truckFloat"]["userBrake"] > 0.1:
            user_braking = True
        else:
            user_braking = False
        if data["api"]["truckFloat"]["userBrake"] > 0.9:
            user_emergency_braking = True
        hazard_light = data["api"]["truckBool"]["lightsHazard"]
        gamepaused = data["api"]["pause"]
    except:
        speed = last_speed
        speedlimit = last_speedlimit
        cruisecontrolspeed = 0
        user_accelerating = False
        user_braking = False
        user_emergency_braking = False
        hazard_light = False
        gamepaused = False

    if speedlimit != 0 and speedlimit > 0:
        targetspeed = speedlimit
    else:
        if last_speedlimit != 0 and last_speedlimit > 0:
            targetspeed = last_speedlimit
        else:
            targetspeed = 30
    
    if trafficlightdetectionisenabled == True:
        try:
            trafficlight = data["TrafficLightDetection"]
        except:
            trafficlight = "---"
    else:
        trafficlight = "Off"
    if navigationdetectionisenabled == True:
        try:
            if data["NavigationDetection"]["turnincoming"] == True:
                turnincoming_last_time_with = current_time
        except:
            pass
    if current_time - 1 < turnincoming_last_time_with:
        targetspeed = cruisespeed_turn

    if trafficlight != "Red":
        trafficlight_last_time_without = current_time
    else:
        trafficlight_last_time_with = current_time
    if current_time - 0.5 > trafficlight_last_time_without or current_time - 0.5 < trafficlight_last_time_with:
        if stop_trafficlight == True:
            targetspeed = cruisespeed_trafficlight
    
    if targetspeed == 0 and speed > 10:
        trafficlight_allow_acceleration = True

    if current_time - 1 > wait_for_response_timer and wait_for_response == True:
        wait_for_response = False
    if last_cruisecontrolspeed != cruisecontrolspeed:
        wait_for_response = False

    try:
        data["sdk"]
    except:
        data["sdk"] = {}
    if gamepaused == False and DefaultSteering.enabled == True:
        if speed > 30 and cruisecontrolspeed == 0 and auto_enable == True and wait_for_response == False and targetspeed != 0:
            data["sdk"]["CruiseControl"] = True
            wait_for_response = True
            wait_for_response_timer = current_time
            data["sdk"]["acceleration"] = 0
            trafficlight_allow_acceleration = False
        if cruisecontrolspeed != 0 and cruisecontrolspeed < targetspeed and wait_for_response == False and targetspeed != 0:
            data["sdk"]["CruiseControlIncrease"] = True
            wait_for_response = True
            wait_for_response_timer = current_time
        if cruisecontrolspeed != 0 and cruisecontrolspeed > targetspeed and wait_for_response == False and targetspeed != 0:
            data["sdk"]["CruiseControlDecrease"] = True
            wait_for_response = True
            wait_for_response_timer = current_time
        if speed < 30 and cruisecontrolspeed == 0 and targetspeed != 0 and trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
            data["sdk"]["acceleration"] = acceleration_strength
            data["sdk"]["brake"] = 0
        if targetspeed == 0 and speed > 1 and user_accelerating == False:
            data["sdk"]["acceleration"] = 0
            data["sdk"]["brake"] = brake_strength
            user_emergency_braking_timer = current_time
        if speed < 30 and cruisecontrolspeed == 0 and targetspeed != 0 and auto_accelerate == True:
            data["sdk"]["acceleration"] = acceleration_strength
            data["sdk"]["brake"] = 0
    else:
        data["sdk"]["acceleration"] = 0
        data["sdk"]["brake"] = 0

    if current_time - 1 < user_emergency_braking_timer:
        user_emergency_braking = False
    if hazard_light != last_hazard_light or current_time - 1 >  wait_for_response_hazard_light_timer:
        wait_for_response_hazard_light = False
    if hazard_light != last_hazard_light and hazard_light == False:
        need_to_disable_hazard_light = False
    if user_emergency_braking == True and hazard_light == False and wait_for_response_hazard_light == False and auto_hazard == True:
        # add code to enable hazard light in sdk (just set the sdk for hazard light to true)
        wait_for_response_hazard_light = True
        wait_for_response_hazard_light_timer = current_time
        need_to_disable_hazard_light = True
    if user_emergency_braking == False and hazard_light == True and wait_for_response_hazard_light == False and need_to_disable_hazard_light == True and auto_hazard == True:
        # add code to disable hazard light in sdk (just set the sdk for hazard light to true)
        wait_for_response_hazard_light = True
        wait_for_response_hazard_light_timer = current_time

    if show_symbols == True:
        try:
            frame = data["frame"]
        except:
            return data
        try:
            width = frame.shape[1]
            height = frame.shape[0]
        except:
            return data
        try:
            indicator_left = data["api"]["truckBool"]["blinkerLeftActive"]
            indicator_right = data["api"]["truckBool"]["blinkerRightActive"]
        except:
            indicator_left = False
            indicator_right = False
        symbol = cruisecontrol_on_set.copy()
        if cruisecontrolspeed != 0:
            if cruisecontrolspeed == targetspeed:
                symbol = cruisecontrol_on_set.copy()
            if cruisecontrolspeed != targetspeed:
                symbol = cruisecontrol_on_unset.copy()
            if data["NavigationDetection"]["turnincoming"] == True:
                symbol = cruisecontrol_on_slowed.copy()
        else:
            if cruisecontrolspeed == targetspeed:
                if auto_accelerate == True:
                    if data["NavigationDetection"]["turnincoming"] == True:
                        symbol = cruisecontrol_off_slowed.copy()
                    else:
                        symbol = cruisecontrol_off_set.copy()
                elif trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
                    if data["NavigationDetection"]["turnincoming"] == True:
                        symbol = cruisecontrol_off_slowed.copy()
                    else:
                        symbol = cruisecontrol_off_set.copy()
                else:
                    symbol = cruisecontrol_off_unset.copy()
            elif trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
                if data["NavigationDetection"]["turnincoming"] == True:
                    symbol = cruisecontrol_off_slowed.copy()
                else:
                    symbol = cruisecontrol_off_set.copy()
            else:
                symbol = cruisecontrol_off_unset.copy()
        
        if user_emergency_braking == True:
            if cruisecontrolspeed != 0:
                if cruisecontrolspeed == targetspeed:
                    symbol = cruisecontrol_emergency_set.copy()
                if cruisecontrolspeed != targetspeed:
                    symbol = cruisecontrol_emergency_unset.copy()
                if data["NavigationDetection"]["turnincoming"] == True:
                    symbol = cruisecontrol_emergency_slowed.copy()
            else:
                if cruisecontrolspeed == targetspeed:
                    if auto_accelerate == True:
                        if data["NavigationDetection"]["turnincoming"] == True:
                            symbol = cruisecontrol_emergency_slowed.copy()
                        else:
                            symbol = cruisecontrol_emergency_set.copy()
                    elif trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
                        if data["NavigationDetection"]["turnincoming"] == True:
                            symbol = cruisecontrol_emergency_slowed.copy()
                        else:
                            symbol = cruisecontrol_emergency_set.copy()
                    else:
                        symbol = cruisecontrol_emergency_unset.copy()
                elif trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
                    if data["NavigationDetection"]["turnincoming"] == True:
                        symbol = cruisecontrol_emergency_slowed.copy()
                    else:
                        symbol = cruisecontrol_emergency_set.copy()
                else:
                    symbol = cruisecontrol_emergency_unset.copy()
        
        symbol_resized = cv2.resize(symbol, (int(0.4 * height), int(0.234375 * height)))
        target_region = frame[int(height/2.8 - 0.2 * height):int(height/2.8 + 0.034375 * height), width - int(0.4 * height):width]
        if indicator_left or indicator_right:
            target_region = frame[int(height/2.8 - 0.2 * height):int(height/2.8 + 0.034375 * height), width - int(0.4 * height):width]
        else:
            target_region = frame[int(height/4 - 0.2 * height):int(height/4 + 0.034375 * height), width - int(0.4 * height):width]
        target_region[:symbol_resized.shape[0], :symbol_resized.shape[1]] = symbol_resized

        data["frame"] = frame
    last_hazard_light = hazard_light
    last_cruisecontrolspeed = cruisecontrolspeed
    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    UpdateSettings()
    pass

def onDisable():
    pass

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur

        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
            resizeWindow(900,600)
        
        def tabFocused(self):
            resizeWindow(900,600)
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self
        
        def UpdateScaleValueFromSlider(self):
            self.acceleration.set(self.accelerationSlider.get())
            self.brake.set(self.brakeSlider.get())
        
        def exampleFunction(self):
            try:
                self.root.destroy() 
            except: pass
            
            self.root = tk.Canvas(self.master, width=800, height=580, border=0, highlightthickness=0)
            self.root.grid_propagate(0) 
            self.root.pack_propagate(0)
            
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            
            generalFrame.columnconfigure(0, weight=1)
            generalFrame.columnconfigure(1, weight=1)
            generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            notebook.add(generalFrame, text=Translate("General"))
            
            ttk.Button(self.root, text="Save", command=self.save, width=15).pack(anchor="center", pady=6)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()

            helpers.MakeCheckButton(generalFrame, "Automatically enable cruise control when available.", "CruiseControl", "auto_enable", 2, 0, width=90, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Stop the truck when a red traffic light is detected.\n(requires that the TrafficLightDetection plugin is enabled)", "CruiseControl", "stop_trafficlight", 3, 0, width=90, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatically accelerate when the red traffic light turns green.", "CruiseControl", "trafficlight_accelerate", 4, 0, width=90, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatically accelerate to the target speed, even if your truck is standing still.\n(if you disable the steering, the truck will not accelerate to the target speed)", "CruiseControl", "auto_accelerate", 5, 0, width=90, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatically enable the hazard light, when the user does a emergency stop.", "CruiseControl", "auto_hazard", 6, 0, width=90, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Show Cruise Control symbol in the Lane Assist window. (ShowImage Plugin)", "CruiseControl", "show_symbols", 7, 0, width=90, callback=UpdateSettings())
            
            self.accelerationSlider = tk.Scale(generalFrame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.accelerationSlider.set(settings.GetSettings("CruiseControl", "acceleration", 50))
            self.accelerationSlider.grid(row=8, column=0, padx=10, pady=0, columnspan=2)
            self.acceleration = helpers.MakeComboEntry(generalFrame, "Acceleration\nstrength in %", "CruiseControl", "acceleration", 8, 0)
            
            self.brakeSlider = tk.Scale(generalFrame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.brakeSlider.set(settings.GetSettings("CruiseControl", "brake", 100))
            self.brakeSlider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.brake = helpers.MakeComboEntry(generalFrame, "Brake\nstrength in %", "CruiseControl", "brake", 9, 0)

            helpers.MakeLabel(generalFrame, "For the best experience, you need to go in the game settings under Gameplay and enable\nthe Adaptive cruise control to the highest possible distance and set the Emergency brake\nsystem to Full detection!", 10, 0, sticky="w")

        def save(self):
            settings.CreateSettings("CruiseControl", "acceleration", self.accelerationSlider.get())
            settings.CreateSettings("CruiseControl", "brake", self.brakeSlider.get())
            UpdateSettings()

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)