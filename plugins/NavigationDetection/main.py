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


import pyautogui
import numpy as np
import os

import cv2

pidKp = 400
pidKi = 0
pidKd = 20
pidTarget = 0
piderror = 0
pidlast_error = 0
pidintegral = 0
pidderivative = 0
pidsteering = 0
steeringsmoothes = 2

smoothed_pidsteering = 0
smoothed_rounded_pidsteering = 0

red_lower_limit = (187, 0, 0)
red_upper_limit = (227, 32, 32)

green_lower_limit = (0, 231, 0)
green_upper_limit = (37, 255, 26)
def plugin(data):

    global pidKp
    global pidKi
    global pidKd
    global pidTarget
    global piderror
    global pidlast_error
    global pidintegral
    global pidderivative
    global pidsteering
    global steeringsmoothes

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
    target = width/2
    trim = 0
    curvemultip = 0.15
    y_coordinate_of_lane_detection = int(height/2)
    y_coordinate_of_curve_detection = int(height/2+30)
    #########################

    curve = None


    left_x = None
    right_x = None
    left_x_curve = None
    right_x_curve = None


    for x in range(int(width/4), int(width/4*3)):

        pixel_farbe_oben = picture_np[y_coordinate_of_lane_detection, x]
        if (red_lower_limit[0] <= pixel_farbe_oben[0] <= red_upper_limit[0] and
            red_lower_limit[1] <= pixel_farbe_oben[1] <= red_upper_limit[1] and
            red_lower_limit[2] <= pixel_farbe_oben[2] <= red_upper_limit[2]) or \
            (green_lower_limit[0] <= pixel_farbe_oben[0] <= green_upper_limit[0] and
            green_lower_limit[1] <= pixel_farbe_oben[1] <= green_upper_limit[1] and
            green_lower_limit[2] <= pixel_farbe_oben[2] <= green_upper_limit[2]):
            if left_x is None:
                left_x = x
            right_x = x


        pixel_farbe_kurve = picture_np[y_coordinate_of_curve_detection, x]
        if (red_lower_limit[0] <= pixel_farbe_kurve[0] <= red_upper_limit[0] and
            red_lower_limit[1] <= pixel_farbe_kurve[1] <= red_upper_limit[1] and
            red_lower_limit[2] <= pixel_farbe_kurve[2] <= red_upper_limit[2]) or \
            (green_lower_limit[0] <= pixel_farbe_kurve[0] <= green_upper_limit[0] and
            green_lower_limit[1] <= pixel_farbe_kurve[1] <= green_upper_limit[1] and
            green_lower_limit[2] <= pixel_farbe_kurve[2] <= green_upper_limit[2]):
            if left_x_curve is None:
                left_x_curve = x
            right_x_curve = x


    center_x = (left_x + right_x) // 2 if left_x is not None else None
    center_x_curve = (left_x_curve + right_x_curve) // 2 if left_x_curve is not None else None
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



    cv2.line(picture_np, (int(0), y_coordinate_of_lane_detection), (int(width), y_coordinate_of_lane_detection), (0, 0, 255), 2)
    cv2.putText(picture_np, f"lane coordinate:{center_x}x   curve:{curve}   correction:{distancetocenter}   lane detected:{lanedetected}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    data["frame"] = picture_np

    if lanedetected == "Yes":

        piderror = pidTarget - distancetocenter
        pidintegral = pidintegral + piderror
        pidderivative = piderror - pidlast_error
        pidsteering = (piderror*pidKp)+(pidintegral*pidKi)+(pidderivative*pidKd)*-1

        pidlast_error = piderror

        smoothed_pidsteering = smoothed_pidsteering + (pidsteering-smoothed_pidsteering)/steeringsmoothes

        smoothed_rounded_pidsteering = round(smoothed_pidsteering)

        print(smoothed_rounded_pidsteering)
        data["controller"] = {}
        data["controller"]["leftStick"] = smoothed_rounded_pidsteering
        # gamepad.left_joystick(x_value=smoothed_rounded_pidsteering, y_value=0)
        # gamepad.update()
    else:
        data["controller"] = {}
        data["controller"]["leftStick"] = 0


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

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Helpers provides easy to use functions for creating consistent widgets!
            helpers.MakeLabel(self.root, "This is a plugin!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            # Use the mainUI.quit() function to quit the app
            helpers.MakeButton(self.root, "Quit", lambda: mainUI.quit(), 1,0, padx=30, pady=10)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)