"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import resizeWindow

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
import time
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
turnincdetecYOffset = 0
drivenroadYOffset = 0
turnXOffset = 0
curvemultip = 0.15
navsymboldetecXOffset = 148
turnstrength = 40
turnincoming = 0
last_navsymboldetecXOffset = 0
navsymboldetecXOffset_lasttimemoved = time.time
smoothed_pidsteering = 0
smoothed_rounded_pidsteering = 0

red_lower_limit = (170, 0, 0)
red_upper_limit = (247, 42, 42)

green_lower_limit = (0, 231, 0)
green_upper_limit = (47, 255, 36)

blue_lower_limit = (0, 68, 121)
blue_upper_limit = (109, 184, 250)

enableSteering = True

def LoadSettings():
    global trim
    global laneYOffset
    global turnYOffset
    global navsymboldetecXOffset
    global turnincdetecYOffset
    global drivenroadYOffset
    global laneXOffset
    global curvemultip
    global steeringsmoothness
    global turnstrength
    global scale
    
    trim = settings.GetSettings("NavigationDetection", "trim")
    if trim == None:
        settings.CreateSettings("NavigationDetection", "trim", 0)
        trim = 0
    
    trim = -trim
    
    laneXOffset = settings.GetSettings("NavigationDetection", "laneXOffset")
    if laneXOffset == None:
        settings.CreateSettings("NavigationDetection", "laneXOffset", 0)
        laneXOffset = 0

    scale = settings.GetSettings("NavigationDetection", "scale")
    if scale == None:
        settings.CreateSettings("NavigationDetection", "scale", 0)
        scale = 0
    
    steeringsmoothness = settings.GetSettings("NavigationDetection", "smoothness")
    if steeringsmoothness == None:
        settings.CreateSettings("NavigationDetection", "smoothness", 10)
        steeringsmoothness = 0
        
    curvemultip = settings.GetSettings("NavigationDetection", "CurveMultiplier")
    if curvemultip == None:
        settings.CreateSettings("NavigationDetection", "CurveMultiplier", 0.15)
        curvemultip = 0.15

    turnstrength = settings.GetSettings("NavigationDetection", "TurnStrength")
    if turnstrength == None:
        settings.CreateSettings("NavigationDetection", "TurnStrength", 0.15)
        turnstrength = 40
        
    steeringsmoothness += 1
    
    

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

    global curvemultip

    global navsymboldetecXOffset
    global navsymboldetecXOffset_lasttimemoved
    global navsymboldetecXOffset_timedifference
    global navsymboldetecXOffset_wasmoved
    global last_navsymboldetecXOffset

    global turnincoming
    global timerforturnincoming
    global width_y_symbol
    
    global turnstrength

    picture_np = data["frame"]
    
    try:
        width = picture_np.shape[1]
        height = picture_np.shape[0]
    except:
        return data

    navsymboldetecXOffset = laneXOffset
    #########################
    target = width/2 + trim
    y_coordinate_of_drivenroad = int(0+(height-1))
    #########################
    
    curve = None


    highest_y = None
    lowest_y = None

    left_x = None
    right_x = None
    left_x_curve = None
    right_x_curve = None
    left_x_turnincdetec = None
    right_x_turnincdetec = None
    left_x_drivenroad = None
    right_x_drivenroad = None

    lane_width = None
    lane_width_turnincdetec = None
    turndetected = 0


    for y in range(height):
        pixel_color = picture_np[y, navsymboldetecXOffset]
        pixel_color = (pixel_color[2], pixel_color[1], pixel_color[0])

        # Check if the pixel is red
        if blue_lower_limit[0] <= pixel_color[0] <= blue_upper_limit[0] and \
                blue_lower_limit[1] <= pixel_color[1] <= blue_upper_limit[1] and \
                blue_lower_limit[2] <= pixel_color[2] <= blue_upper_limit[2]:

            if highest_y is None:
                highest_y = y
                lowest_y = y
            else:
                lowest_y = y

    try:
        y_coordinate_of_lane_detection = highest_y - round(height/scale/9)
        y_coordinate_of_curve_detection = highest_y - round(height/scale/3.5)
        y_coordinate_of_turnincdetec = highest_y - round(height/scale/1.5)
        scaletarget = highest_y - round(height/scale)
    except:
        pass


    def GetArrayOfLaneEdges(y_coordinate_of_lane_detection):
        detectingLane = False
        laneEdges = []
        
        for x in range(0, int(width)):
            pixel = picture_np[y_coordinate_of_lane_detection, x]
            pixel = (pixel[2], pixel[1], pixel[0])
            if (red_lower_limit[0] <= pixel[0] <= red_upper_limit[0] and
                red_lower_limit[1] <= pixel[1] <= red_upper_limit[1] and
                red_lower_limit[2] <= pixel[2] <= red_upper_limit[2]) or \
                (green_lower_limit[0] <= pixel[0] <= green_upper_limit[0] and
                green_lower_limit[1] <= pixel[1] <= green_upper_limit[1] and
                green_lower_limit[2] <= pixel[2] <= green_upper_limit[2]):
                if not detectingLane:
                    detectingLane = True
                    laneEdges.append(x)
            else:
                if detectingLane:
                    detectingLane = False
                    laneEdges.append(x)

        if len(laneEdges) < 2:
            laneEdges.append(width)

        return laneEdges

            

    try:
        lanes = GetArrayOfLaneEdges(y_coordinate_of_lane_detection)
        left_x = lanes[len(lanes)-2]
        right_x = lanes[len(lanes)-1]
    except:
        pass
    
    try:
        lanes = GetArrayOfLaneEdges(y_coordinate_of_curve_detection)
        left_x_curve = lanes[len(lanes)-2]
        right_x_curve = lanes[len(lanes)-1]
    except:
        pass
    
    try:
        lanes = GetArrayOfLaneEdges(y_coordinate_of_turnincdetec)
        left_x_turnincdetec = lanes[len(lanes)-2]
        right_x_turnincdetec = lanes[len(lanes)-1]
    except:
        pass
    
    try:
        lanes = GetArrayOfLaneEdges(y_coordinate_of_drivenroad)
        left_x_drivenroad = lanes[len(lanes)-2]
        right_x_drivenroad = lanes[len(lanes)-1]
    except:
        pass

    try:
        lane_width = right_x - left_x
        lane_width_curve = right_x_curve - left_x_curve
    except:
        pass   

    try:
        lane_width_turnincdetec = right_x_turnincdetec - left_x_turnincdetec
    except:
        pass
        

    
    try:
        if lane_width_turnincdetec > 40:
            turnincoming = 1
            timerforturnincoming = time.time()
    except:
        pass
    try:
        currenttime = time.time()
        timerdifference = (currenttime - timerforturnincoming)
    except:
        pass
    try:
        if turnincoming == 1:
            cv2.putText(picture_np, f"turn inc", (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (2, 137, 240), 1, cv2.LINE_AA)
            if timerdifference > 30:
                turnincoming = 0
    except:
        pass
    
    
    if lane_width:
        if lane_width > 60:
            if left_x < width/2-40:
                turndetected = 1
                timerforturnincoming = time.time()-27
            if right_x > width/2+40:
                turndetected = 2
                timerforturnincoming = time.time()-27
        else:
            turndetected = 0

    if turndetected == 0:
        cv2.putText(picture_np, f"no", (150, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)
        turnvalue = 0

    if turndetected == 1:
        cv2.putText(picture_np, f"left", (150, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1, cv2.LINE_AA)
        turnvalue = -turnstrength

    if turndetected == 2:
        cv2.putText(picture_np, f"right", (150, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1, cv2.LINE_AA)
        turnvalue = turnstrength
    

    try:
        center_x = (left_x + right_x) / 2 if left_x and right_x is not None else None
    except:
        center_x = None
    try:
        center_x_curve = (left_x_curve + right_x_curve) / 2 if left_x_curve and right_x_curve is not None else None
    except:
        center_x_curve = None
    try:
        center_x_turnincdetec = (left_x_turnincdetec + right_x_turnincdetec) / 2 if left_x_turnincdetec and right_x_turnincdetec is not None else None
    except:
        center_x_turnincdetec = None
    try:    
        center_x_drivenroad = (left_x_drivenroad + right_x_drivenroad) / 2
    except:
        center_x_drivenroad = None
    try:
        width_y_symbol = lowest_y - highest_y
    except:
        width_y_symbol = 0

    if center_x is not None and center_x_curve is not None:
        if turnincoming == 0:
            curve = (center_x - center_x_curve)*curvemultip
            distancetocenter = ((target-center_x)-curve)
        else:
            distancetocenter = ((target-center_x))
        lanedetected = "Yes"
    else:
        lanedetected = "No"
        distancetocenter = 0
        curve = 0
        center_x = 0
        center_x_curve = 0

    if width_y_symbol > height/3.5:
        highest_y = 1
        lowest_y = 1
        draworangeline = 0
    else:
        draworangeline = 1

    try:
        if navsymboldetecXOffset != last_navsymboldetecXOffset:
            navsymboldetecXOffset_wasmoved = 1
            navsymboldetecXOffset_lasttimemoved = time.time()
        navsymboldetecXOffset_timedifference = (time.time() - navsymboldetecXOffset_lasttimemoved)
        last_navsymboldetecXOffset = navsymboldetecXOffset
    except:
        pass
   

    try:
        cv2.line(picture_np, (int(0), y_coordinate_of_lane_detection), (int(width), y_coordinate_of_lane_detection), (0, 0, 255), 1)
    
        cv2.line(picture_np, (int(0), y_coordinate_of_curve_detection), (int(width), y_coordinate_of_curve_detection), (0, 0, 255), 1)

        cv2.line(picture_np, (int(0), y_coordinate_of_turnincdetec), (int(width), y_coordinate_of_turnincdetec), (0, 0, 255), 1)
        
        cv2.line(picture_np, (int(0), scaletarget), (int(width), scaletarget), (235, 52, 143), 1)
    except:
        pass

    try:
        cv2.line(picture_np, (int(left_x), y_coordinate_of_lane_detection), (int(right_x), y_coordinate_of_lane_detection), (0, 255, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(left_x_curve), y_coordinate_of_curve_detection), (int(right_x_curve), y_coordinate_of_curve_detection), (0, 255, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(left_x_turnincdetec), y_coordinate_of_turnincdetec), (int(right_x_turnincdetec), y_coordinate_of_turnincdetec), (0, 255, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(left_x_drivenroad), y_coordinate_of_drivenroad), (int(right_x_drivenroad), y_coordinate_of_drivenroad), (0, 255, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(center_x), y_coordinate_of_lane_detection), (int(center_x_curve), y_coordinate_of_curve_detection), (255, 0, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(center_x_curve), y_coordinate_of_curve_detection), (int(center_x_turnincdetec), y_coordinate_of_turnincdetec), (255, 0, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(center_x), y_coordinate_of_lane_detection), (int(center_x_drivenroad), y_coordinate_of_drivenroad), (255, 0, 0), 1)
    except:
        pass
    try:
        cv2.line(picture_np, (int(left_x), y_coordinate_of_lane_detection), (int(left_x_curve), y_coordinate_of_curve_detection), (255, 175, 0), 2)
    except:
        pass
    try:
        cv2.line(picture_np, (int(right_x), y_coordinate_of_lane_detection), (int(right_x_curve), y_coordinate_of_curve_detection), (255, 175, 0), 2)
    except:
        pass
    try:
        cv2.line(picture_np, (int(left_x_curve), y_coordinate_of_curve_detection), (int(left_x_turnincdetec), y_coordinate_of_turnincdetec), (255, 175, 0), 2)
    except:
        pass
    try:
        cv2.line(picture_np, (int(right_x_curve), y_coordinate_of_curve_detection), (int(right_x_turnincdetec), y_coordinate_of_turnincdetec), (255, 175, 0), 2)
    except:
        pass
    try:
        cv2.line(picture_np, (int(left_x), y_coordinate_of_lane_detection), (int(left_x_drivenroad), y_coordinate_of_drivenroad), (255, 175, 0), 2)
    except:
        pass
    try:
        cv2.line(picture_np, (int(right_x), y_coordinate_of_lane_detection), (int(right_x_drivenroad), y_coordinate_of_drivenroad), (255, 175, 0), 2)
    except:
        pass
    if draworangeline == 1:
        try:
            cv2.line(picture_np, (int(navsymboldetecXOffset), lowest_y), (int(navsymboldetecXOffset), highest_y), (25, 127, 225), 1)
        except:
            pass
        try:
            cv2.line(picture_np, (int(navsymboldetecXOffset-round(width_y_symbol/2)), round(highest_y+width_y_symbol/2)), (int(navsymboldetecXOffset+round(width_y_symbol/2)), round(highest_y+width_y_symbol/2)), (25, 127, 225), 1)
        except:
            pass
    try:
        if navsymboldetecXOffset_timedifference < 10:
            try:
                cv2.line(picture_np, (int(navsymboldetecXOffset), 10), (int(navsymboldetecXOffset), height-10), (255, 255, 255), 1)
            except:
                pass
    except:
        pass
    
    cv2.putText(picture_np, f"lane detected:{lanedetected}   correction:{distancetocenter}   curve:{curve}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)

    if lanedetected == "Yes":
        piderror = pidTarget - distancetocenter
        pidintegral = pidintegral + piderror
        pidderivative = piderror - pidlast_error
        pidsteering = (piderror*pidKp)+(pidintegral*pidKi)+(pidderivative*pidKd)*-1

        pidlast_error = piderror

        smoothed_pidsteering = smoothed_pidsteering + (pidsteering-smoothed_pidsteering)/steeringsmoothness

    if center_x is not None:
        #data["controller"] = {}
        #data["controller"]["leftStick"] = (smoothed_pidsteering) * 1
        data["LaneDetection"] = {}
        data["LaneDetection"]["difference"] = -distancetocenter + turnvalue
        # gamepad.left_joystick(x_value=smoothed_rounded_pidsteering, y_value=0)
        # gamepad.update()
    else:
        data["LaneDetection"] = {}
        data["LaneDetection"]["difference"] = 0


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
            
            resizeWindow(800,600)
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def UpdateSettings(self):
            self.trim.set(self.trimSlider.get())
            self.laneX.set(self.laneXSlider.get())
            self.sca.set(self.scale.get())
            self.smoothness.set(self.smoothnessSlider.get())
            self.curveMultip.set(self.curveMultipSlider.get())
            self.turnstrength.set(self.turnstrengthSlider.get())
            
            settings.CreateSettings("NavigationDetection", "trim", self.trimSlider.get())
            settings.CreateSettings("NavigationDetection", "laneXOffset", self.laneXSlider.get())
            settings.CreateSettings("NavigationDetection", "scale", self.scale.get())
            settings.CreateSettings("NavigationDetection", "smoothness", self.smoothnessSlider.get())
            settings.CreateSettings("NavigationDetection", "CurveMultiplier", self.curveMultipSlider.get())
            settings.CreateSettings("NavigationDetection", "TurnStrength", self.turnstrengthSlider.get())
            
            LoadSettings()

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.trimSlider = tk.Scale(self.root, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.trimSlider.set(settings.GetSettings("NavigationDetection", "trim"))
            self.trimSlider.grid(row=0, column=0, padx=10, pady=0, columnspan=2)
            self.trim = helpers.MakeComboEntry(self.root, "Trim", "NavigationDetection", "trim", 1,0)
            
            self.laneXSlider = tk.Scale(self.root, from_=1, to=400, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.laneXSlider.set(settings.GetSettings("NavigationDetection", "laneXOffset"))
            self.laneXSlider.grid(row=2, column=0, padx=10, pady=0, columnspan=2)
            self.laneX = helpers.MakeComboEntry(self.root, "Navisymbol Offset", "NavigationDetection", "laneXOffset", 3,0)

            self.scale = tk.Scale(self.root, from_=0.01, to=10, resolution=0.01, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.scale.set(settings.GetSettings("NavigationDetection", "scale"))
            self.scale.grid(row=4, column=0, padx=10, pady=0, columnspan=2)
            self.sca = helpers.MakeComboEntry(self.root, "Scale", "NavigationDetection", "scale", 5,0)

            self.smoothnessSlider = tk.Scale(self.root, from_=0, to=20, resolution=1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.smoothnessSlider.set(settings.GetSettings("NavigationDetection", "smoothness"))
            self.smoothnessSlider.grid(row=6, column=0, padx=10, pady=0, columnspan=2)
            self.smoothness = helpers.MakeComboEntry(self.root, "Smoothness", "NavigationDetection", "smoothness", 7,0)
            
            self.curveMultipSlider = tk.Scale(self.root, from_=0, to=3, resolution=0.01, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.curveMultipSlider.set(settings.GetSettings("NavigationDetection", "CurveMultiplier"))
            self.curveMultipSlider.grid(row=8, column=0, padx=10, pady=0, columnspan=2)
            self.curveMultip = helpers.MakeComboEntry(self.root, "Curve Multiplier", "NavigationDetection", "CurveMultiplier", 9,0)

            self.turnstrengthSlider = tk.Scale(self.root, from_=1, to=100, resolution=1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.turnstrengthSlider.set(settings.GetSettings("NavigationDetection", "TurnStrength"))
            self.turnstrengthSlider.grid(row=10, column=0, padx=10, pady=0, columnspan=2)
            self.turnstrength = helpers.MakeComboEntry(self.root, "TurnStrength", "NavigationDetection", "TurnStrength", 11,0)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)