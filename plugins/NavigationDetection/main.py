"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="NavigationDetection", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Uses the navigation line in the minimap.",
    version="0.1",
    author="Glas42,Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="LaneDetection"
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os

import numpy as np
import os

import cv2

pidKp = 0.01
pidKi = 0
pidKd = 0.002
pidTarget = 0
piderror = 0
pidlast_error = 0
pidintegral = 0
pidderivative = 0
pidsteering = 0
steeringsmoothness = 5
trim = 0
laneYOffset = 0
turnYOffset = 0

smoothed_pidsteering = 0
smoothed_rounded_pidsteering = 0

red_lower_limit = (187, 0, 0)
red_upper_limit = (237, 42, 42)

green_lower_limit = (0, 231, 0)
green_upper_limit = (47, 255, 36)

enableSteering = True

def LoadSettings():
    global trim
    global laneYOffset
    global turnYOffset
    global steeringsmoothness
    
    trim = settings.GetSettings("NavigationDetection", "trim")
    if trim == None:
        settings.CreateSettings("NavigationDetection", "trim", 0)
        trim = 0
    
    trim = -trim
    
    laneYOffset = settings.GetSettings("NavigationDetection", "laneYOffset")
    if laneYOffset == None:
        settings.CreateSettings("NavigationDetection", "laneYOffset", 0)
        laneYOffset = 0
        
    turnYOffset = settings.GetSettings("NavigationDetection", "turnYOffset")
    if turnYOffset == None:
        settings.CreateSettings("NavigationDetection", "turnYOffset", 0)
        turnYOffset = 0
    
    steeringsmoothness = settings.GetSettings("NavigationDetection", "smoothness")
    if steeringsmoothness == None:
        settings.CreateSettings("NavigationDetection", "smoothness", 10)
        steeringsmoothness = 10
    
    

LoadSettings()


def plugin(data):
    global trim
    global pidKp
    global pidKi
    global pidKd
    global pidTarget
    global piderror
    global pidlast_error
    global pidintegral
    global pidderivative
    global pidsteering
    global steeringsmoothness

    global smoothed_pidsteering
    global smoothed_rounded_pidsteering

    global red_lower_limit
    global red_upper_limit

    global green_lower_limit
    global green_upper_limit


    picture_np = data["frame"]
    
    try:
        width = picture_np.shape[1]
        height = picture_np.shape[0]
    except:
        return data


    #########################
    target = width/2 + trim
    curvemultip = 0.15
    y_coordinate_of_lane_detection = int(height/2) + laneYOffset
    y_coordinate_of_curve_detection = int(height/2-height/12) + turnYOffset
    #########################

    curve = None


    left_x = None
    right_x = None
    left_x_curve = None
    right_x_curve = None


    for x in range((0), int(width)):

        pixel_farbe_oben = picture_np[y_coordinate_of_lane_detection, x]
        pixel_farbe_oben = (pixel_farbe_oben[2], pixel_farbe_oben[1], pixel_farbe_oben[0])
        if (red_lower_limit[0] <= pixel_farbe_oben[0] <= red_upper_limit[0] and
            red_lower_limit[1] <= pixel_farbe_oben[1] <= red_upper_limit[1] and
            red_lower_limit[2] <= pixel_farbe_oben[2] <= red_upper_limit[2]) or \
            (green_lower_limit[0] <= pixel_farbe_oben[0] <= green_upper_limit[0] and
            green_lower_limit[1] <= pixel_farbe_oben[1] <= green_upper_limit[1] and
            green_lower_limit[2] <= pixel_farbe_oben[2] <= green_upper_limit[2]):
            if left_x is None:
                left_x = x
            else:
                right_x = x

        pixel_farbe_kurve = picture_np[y_coordinate_of_curve_detection, x]
        pixel_farbe_kurve = (pixel_farbe_kurve[2], pixel_farbe_kurve[1], pixel_farbe_kurve[0])
        if (red_lower_limit[0] <= pixel_farbe_kurve[0] <= red_upper_limit[0] and
            red_lower_limit[1] <= pixel_farbe_kurve[1] <= red_upper_limit[1] and
            red_lower_limit[2] <= pixel_farbe_kurve[2] <= red_upper_limit[2]) or \
            (green_lower_limit[0] <= pixel_farbe_kurve[0] <= green_upper_limit[0] and
            green_lower_limit[1] <= pixel_farbe_kurve[1] <= green_upper_limit[1] and
            green_lower_limit[2] <= pixel_farbe_kurve[2] <= green_upper_limit[2]):
            if left_x_curve is None:
                left_x_curve = x
            else:
                right_x_curve = x


    center_x = (left_x + right_x) / 2 if left_x and right_x is not None else None
    center_x_curve = (left_x_curve + right_x_curve) / 2 if left_x_curve and right_x_curve is not None else None
    if center_x is not None and center_x_curve is not None:
        curve = (center_x - center_x_curve)*curvemultip
        distancetocenter = ((target-center_x)-curve)
        lanedetected = "Yes"
    else:
        lanedetected = "No"
        distancetocenter = 0
        curve = 0
        center_x = 0
        center_x_curve = 0



    cv2.line(picture_np, (int(0), y_coordinate_of_lane_detection), (int(width), y_coordinate_of_lane_detection), (0, 0, 255), 1)
    
    cv2.line(picture_np, (int(0), y_coordinate_of_curve_detection), (int(width), y_coordinate_of_curve_detection), (0, 0, 255), 1)
    
    try:
        cv2.line(picture_np, (int(left_x), y_coordinate_of_lane_detection), (int(right_x), y_coordinate_of_lane_detection), (0, 255, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(left_x_curve), y_coordinate_of_curve_detection), (int(right_x_curve), y_coordinate_of_curve_detection), (0, 255, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(center_x), y_coordinate_of_lane_detection), (int(center_x_curve), y_coordinate_of_curve_detection), (255, 0, 0), 1)
    except:
        pass
    
    cv2.putText(picture_np, f"lane coordinate:{center_x}x   curve:{curve}   correction:{distancetocenter}   lane detected:{lanedetected}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    if lanedetected == "Yes":
        piderror = pidTarget - distancetocenter
        pidintegral = pidintegral + piderror
        pidderivative = piderror - pidlast_error
        pidsteering = (piderror*pidKp)+(pidintegral*pidKi)+(pidderivative*pidKd)*-1

        pidlast_error = piderror

        smoothed_pidsteering = smoothed_pidsteering + (pidsteering-smoothed_pidsteering)/steeringsmoothness

        #data["controller"] = {}
        #data["controller"]["leftStick"] = (smoothed_pidsteering) * 1
        data["LaneDetection"] = {}
        data["LaneDetection"]["difference"] = -distancetocenter
        # gamepad.left_joystick(x_value=smoothed_rounded_pidsteering, y_value=0)
        # gamepad.update()
    else:
        data["controller"] = {}
        data["controller"]["leftStick"] = 0


    data["frame"] = picture_np
    # os.system('cls')
    # print("running")
    # print(f"lane coordinate:{center_x}x   curve:{curve}   correction:{distancetocenter}   lane detected:{lanedetected}" + "\r")
    
    
    return data
        


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    pass

def onDisable():
    pass

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

        def UpdateSettings(self):
            self.trim.set(self.trimSlider.get())
            self.laneY.set(self.laneYSlider.get())
            self.turnY.set(self.turnYSlider.get())
            self.smoothness.set(self.smoothnessSlider.get())
            
            settings.CreateSettings("NavigationDetection", "trim", self.trimSlider.get())
            settings.CreateSettings("NavigationDetection", "laneYOffset", self.laneYSlider.get())
            settings.CreateSettings("NavigationDetection", "turnYOffset", self.turnYSlider.get())
            settings.CreateSettings("NavigationDetection", "smoothness", self.smoothnessSlider.get())
            
            LoadSettings()

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.trimSlider = tk.Scale(self.root, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.trimSlider.set(settings.GetSettings("NavigationDetection", "trim"))
            self.trimSlider.grid(row=0, column=0, padx=10, pady=0, columnspan=2)
            self.trim = helpers.MakeComboEntry(self.root, "Trim", "NavigationDetection", "trim", 1,0)
            
            self.laneYSlider = tk.Scale(self.root, from_=-400, to=400, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.laneYSlider.set(settings.GetSettings("NavigationDetection", "laneYOffset"))
            self.laneYSlider.grid(row=2, column=0, padx=10, pady=0, columnspan=2)
            self.laneY = helpers.MakeComboEntry(self.root, "Lane Y Offset", "NavigationDetection", "laneYOffset", 3,0)
            
            self.turnYSlider = tk.Scale(self.root, from_=-400, to=400, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.turnYSlider.set(settings.GetSettings("NavigationDetection", "laneYOffset"))
            self.turnYSlider.grid(row=4, column=0, padx=10, pady=0, columnspan=2)
            self.turnY = helpers.MakeComboEntry(self.root, "Turn Y Offset", "NavigationDetection", "turnYOffset", 5,0)

            self.smoothnessSlider = tk.Scale(self.root, from_=0, to=20, resolution=1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.smoothnessSlider.set(settings.GetSettings("NavigationDetection", "smoothness"))
            self.smoothnessSlider.grid(row=6, column=0, padx=10, pady=0, columnspan=2)
            self.smoothness = helpers.MakeComboEntry(self.root, "Smoothness", "NavigationDetection", "smoothness", 7,0)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)