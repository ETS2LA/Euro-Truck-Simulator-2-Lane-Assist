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

def UpdateSettings():
    global trafficlightdetectionisenabled
    global navigationdetectionisenabled
    global auto_enable
    global stop_trafficlight
    global trafficlight_accelerate
    global auto_accelerate
    global acceleration_strength
    global brake_strength
    global cruisespeed_turn
    global cruisespeed_trafficlight
    global wait_for_response
    global wait_for_response_timer
    global last_speed
    global last_speedlimit
    global last_cruisecontrolspeed
    global trafficlight_last_time_without
    global trafficlight_last_time_with
    global turnincoming_last_time_with
    global trafficlight_allow_acceleration
    
    if "TrafficLightDetection" in settings.GetSettings("Plugins", "Enabled"):
        trafficlightdetectionisenabled = True
    else:
        trafficlightdetectionisenabled = False

    if "NavigationDetection" in settings.GetSettings("Plugins", "Enabled"):
        navigationdetectionisenabled = True
    else:
        navigationdetectionisenabled = False

    auto_enable = settings.GetSettings("CruiseControl", "auto_enable", True)
    stop_trafficlight = settings.GetSettings("CruiseControl", "stop_trafficlight", True)
    trafficlight_accelerate = settings.GetSettings("CruiseControl", "trafficlight_accelerate", True)
    auto_accelerate = settings.GetSettings("CruiseControl", "auto_accelerate", False)
    acceleration_strength = settings.GetSettings("CruiseControl", "acceleration", 50)
    acceleration_strength /= 100
    brake_strength = settings.GetSettings("CruiseControl", "brake", 100)
    brake_strength /= 100

    cruisespeed_turn = 30
    cruisespeed_trafficlight = 0

    wait_for_response = False
    wait_for_response_timer = 0

    last_speed = 0
    last_speedlimit = 0
    last_cruisecontrolspeed = 0
    trafficlight_last_time_without = 0
    trafficlight_last_time_with = 0
    turnincoming_last_time_with = 0

    trafficlight_allow_acceleration = False

def plugin(data):
    global trafficlightdetectionisenabled
    global navigationdetectionisenabled
    global auto_enable
    global stop_trafficlight
    global trafficlight_accelerate
    global auto_accelerate
    global acceleration_strength
    global brake_strength
    global cruisespeed_turn
    global cruisespeed_trafficlight
    global wait_for_response
    global wait_for_response_timer
    global last_speed
    global last_speedlimit
    global last_cruisecontrolspeed
    global trafficlight_last_time_without
    global trafficlight_last_time_with
    global turnincoming_last_time_with
    global trafficlight_allow_acceleration

    current_time = time.time()

    try:
        speed = round(data["api"]["truckFloat"]["speed"]*3.6, 1)
        last_speed = speed
        speedlimit = round(data["api"]["truckFloat"]["speedLimit"]*3.6, 1)
        if speedlimit != 0 and speedlimit > 0:
            last_speedlimit = speedlimit
        cruisecontrolspeed = round(data["api"]["truckFloat"]["cruiseControlSpeed"]*3.6, 1)
        gamepaused = data["api"]["pause"]
    except:
        speed = last_speed
        speedlimit = last_speedlimit
        cruisecontrolspeed = 0
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
        if targetspeed == 0 and speed > 1:
            data["sdk"]["acceleration"] = 0
            data["sdk"]["brake"] = brake_strength
        if speed < 30 and cruisecontrolspeed == 0 and targetspeed != 0 and auto_accelerate == True:
            data["sdk"]["acceleration"] = acceleration_strength
            data["sdk"]["brake"] = 0
    else:
        data["sdk"]["acceleration"] = 0
        data["sdk"]["brake"] = 0
    
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

            self.accelerationSlider = tk.Scale(generalFrame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.accelerationSlider.set(settings.GetSettings("CruiseControl", "acceleration", 50))
            self.accelerationSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.acceleration = helpers.MakeComboEntry(generalFrame, "Acceleration\nstrength in %", "CruiseControl", "acceleration", 7, 0)
            
            self.brakeSlider = tk.Scale(generalFrame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.brakeSlider.set(settings.GetSettings("CruiseControl", "brake", 100))
            self.brakeSlider.grid(row=8, column=0, padx=10, pady=0, columnspan=2)
            self.brake = helpers.MakeComboEntry(generalFrame, "Brake\nstrength in %", "CruiseControl", "brake", 8, 0)

            helpers.MakeEmptyLine(generalFrame, 9, 0)
            helpers.MakeLabel(generalFrame, "For the best experience, you need to go in the settings under Gameplay and set the\nAdaptive cruise control to the highest possible distance and set the Emergency\nbrake system to Full detection!", 10, 0, sticky="w")

        def save(self):
            settings.CreateSettings("CruiseControl", "acceleration", self.accelerationSlider.get())
            settings.CreateSettings("CruiseControl", "brake", self.brakeSlider.get())
            UpdateSettings()

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)