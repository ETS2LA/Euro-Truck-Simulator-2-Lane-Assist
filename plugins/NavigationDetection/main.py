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
    author="Glas42",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="LaneDetection",
    requires=["DefaultSteering", "DXCamScreenCapture", "TruckSimAPI", "SDKController"]
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.sounds as sounds
import src.controls as controls
from src.translator import Translate
from tkinter import messagebox
import os



import plugins.DefaultSteering.main as DefaultSteering
import keyboard as kb
import numpy as np
import pyautogui
import ctypes
import mouse
import math
import time
import cv2
import os

path = variables.PATH + r"\assets\NavigationDetectionV3\v3setupexample.jpg"
exampleimage = cv2.imread(path)

controls.RegisterKeybind("Lane change to the left",
                         notBoundInfo="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.",
                         description="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.")

controls.RegisterKeybind("Lane change to the right",
                         notBoundInfo="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.",
                         description="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.")

# Code Parts:
#-
# NavigationDetectionV1 Settings
# NavigationDetectionV1 Code
#-
# NavigationDetectionV2 Settings
# NavigationDetectionV2 Code
#-
# NavigationDetectionV3 Settings
# NavigationDetectionV3 Code
#-
# UI



############################################################################################################################
# NavigationDetectionV1 Settings
############################################################################################################################
def LoadSettingsV1():
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
    global pidKp
    global pidKi
    global pidKd
    global pidTarget
    global piderror
    global pidlast_error
    global pidintegral
    global pidderivative
    global pidsteering
    global turnXOffset
    global highest_y
    global lowest_y
    global turnincomingv1
    global last_navsymboldetecXOffset
    global navsymboldetecXOffset_lasttimemoved
    global navsymboldetecXOffset_timedifference
    global smoothed_pidsteering
    global smoothed_rounded_pidsteering
    global red_lower_limit
    global red_upper_limit
    global green_lower_limit
    global green_upper_limit
    global blue_lower_limit
    global blue_upper_limit
    global enableSteering

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
    highest_y = None
    lowest_y = None
    turnstrength = 40
    turnincomingv1 = 0
    last_navsymboldetecXOffset = 0
    navsymboldetecXOffset_lasttimemoved = time.time
    navsymboldetecXOffset_timedifference = 0
    smoothed_pidsteering = 0
    smoothed_rounded_pidsteering = 0

    red_lower_limit = (170, 0, 0)
    red_upper_limit = (247, 42, 42)

    green_lower_limit = (0, 231, 0)
    green_upper_limit = (47, 255, 36)

    blue_lower_limit = (0, 68, 121)
    blue_upper_limit = (109, 184, 250)

    enableSteering = True
    
    trim = settings.GetSettings("NavigationDetectionV1", "trim")
    if trim == None:
        settings.CreateSettings("NavigationDetectionV1", "trim", 0)
        trim = 0
    
    trim = -trim
    
    laneXOffset = settings.GetSettings("NavigationDetectionV1", "laneXOffset")
    if laneXOffset == None:
        settings.CreateSettings("NavigationDetectionV1", "laneXOffset", 0)
        laneXOffset = 0

    scale = settings.GetSettings("NavigationDetectionV1", "scale")
    if scale == None:
        settings.CreateSettings("NavigationDetectionV1", "scale", 0)
        scale = 0
    
    steeringsmoothness = settings.GetSettings("NavigationDetectionV1", "smoothness")
    if steeringsmoothness == None:
        settings.CreateSettings("NavigationDetectionV1", "smoothness", 10)
        steeringsmoothness = 0
        
    curvemultip = settings.GetSettings("NavigationDetectionV1", "CurveMultiplier")
    if curvemultip == None:
        settings.CreateSettings("NavigationDetectionV1", "CurveMultiplier", 0.15)
        curvemultip = 0.15

    turnstrength = settings.GetSettings("NavigationDetectionV1", "TurnStrength")
    if turnstrength == None:
        settings.CreateSettings("NavigationDetectionV1", "TurnStrength", 40)
        turnstrength = 40
        
    steeringsmoothness += 1


############################################################################################################################
# NavigationDetectionV2 Settings
############################################################################################################################
def LoadSettingsV2():
    global curvemultip
    global sensitivity
    global offset
    global textsize
    global textdistancescale
    global navsymbolx
    global navsymboly
    global getnavcoordinates
    global navcoordsarezero
    global leftsidetraffic
    global automaticlaneselection
    global trafficlightdetectionisenabled
    global trucksimapiisenabled
    global lanechanging
    global lanechangingspeed
    global lanewidth
    global avg_lanewidth
    global avg_lanewidth_counter
    global avg_lanewidth_value
    global disableshowimagelater
    global screen_width
    global screen_height
    global timerforturnincoming
    global turnincdirec
    global white_limit
    global currentlane
    global lastblinker
    global currentoffsetsteeringvalue

    screen_width, screen_height = pyautogui.size()

    timerforturnincoming = 0
    turnincdirec = None
    white_limit = (1, 1, 1)
    getnavcoordinates = False
    trafficlightdetectionisenabled = False
    trucksimapiisenabled = False

    currentlane = 0
    lastblinker = None
    currentoffsetsteeringvalue = 0

    avg_lanewidth = None
    avg_lanewidth_counter = 1
    avg_lanewidth_value = 0

    disableshowimagelater = False
    
    curvemultip = settings.GetSettings("NavigationDetectionV2", "curvemultip")
    if curvemultip == None:
        settings.CreateSettings("NavigationDetectionV2", "curvemultip", 1)
        curvemultip = 1
    
    sensitivity = settings.GetSettings("NavigationDetectionV2", "sensitivity")
    if sensitivity == None:
        settings.CreateSettings("NavigationDetectionV2", "sensitivity", 1)
        sensitivity = 1

    offset = settings.GetSettings("NavigationDetectionV2", "offset")
    if offset == None:
        settings.CreateSettings("NavigationDetectionV2", "offset", 0)
        offset = 0
    
    textsize = settings.GetSettings("NavigationDetectionV2", "textsize")
    if textsize == None:
        settings.CreateSettings("NavigationDetectionV2", "textsize", 0.5)
        textsize = 0.5
        
    textdistancescale = settings.GetSettings("NavigationDetectionV2", "textdistancescale")
    if textdistancescale == None:
        settings.CreateSettings("NavigationDetectionV2", "textdistancescale", 1)
        textdistancescale = 1

    leftsidetraffic = settings.GetSettings("NavigationDetectionV2", "leftsidetraffic")
    if leftsidetraffic == None:
        settings.CreateSettings("NavigationDetectionV2", "leftsidetraffic", 0)
        leftsidetraffic = 0

    automaticlaneselection = settings.GetSettings("NavigationDetectionV2", "automaticlaneselection")
    if automaticlaneselection == None:
        settings.CreateSettings("NavigationDetectionV2", "automaticlaneselection", 1)
        automaticlaneselection = 1

    navsymbolx = settings.GetSettings("NavigationDetectionV2", "navsymbolx")
    if navsymbolx == None:
        settings.CreateSettings("NavigationDetectionV2", "navsymbolx", 0)
        navsymbolx = 0

    navsymboly = settings.GetSettings("NavigationDetectionV2", "navsymboly")
    if navsymboly == None:
        settings.CreateSettings("NavigationDetectionV2", "navsymboly", 0)
        navsymboly = 0

    if navsymbolx == 0 or navsymboly == 0:
        navcoordsarezero = True
        DefaultSteering.enabled = False
        if "ShowImage" not in settings.GetSettings("Plugins", "Enabled"):
            disableshowimagelater = True
            settings.AddToList("Plugins", "Enabled", "ShowImage")
    else:
        navcoordsarezero = False


    widthofscreencapture = settings.GetSettings("dxcam", "width")
    heightofscreencapture = settings.GetSettings("dxcam", "height")
    if navsymbolx > widthofscreencapture - 3 or navsymbolx < 3:
        getnavcoordinates = True
        if "ShowImage" not in settings.GetSettings("Plugins", "Enabled"):
            disableshowimagelater = True
            settings.AddToList("Plugins", "Enabled", "ShowImage")

    if navsymboly > heightofscreencapture - 3 or navsymboly < 3:
        getnavcoordinates = True
        DefaultSteering.enabled = False
        if "ShowImage" not in settings.GetSettings("Plugins", "Enabled"):
            disableshowimagelater = True
            settings.AddToList("Plugins", "Enabled", "ShowImage")

    
    if "TrafficLightDetection" in settings.GetSettings("Plugins", "Enabled"):
        trafficlightdetectionisenabled = True
    else:
        trafficlightdetectionisenabled = False

    if "TruckSimAPI" in settings.GetSettings("Plugins", "Enabled"):
        trucksimapiisenabled = True
    else:
        trucksimapiisenabled = False

    lanechanging = settings.GetSettings("NavigationDetectionV2", "lanechanging", True)
    lanechangingspeed = settings.GetSettings("NavigationDetectionV2", "lanechangingspeed")
    if lanechangingspeed == None:
        settings.CreateSettings("NavigationDetectionV2", "lanechangingspeed", 1)
        lanechangingspeed = 1
    lanewidth = settings.GetSettings("NavigationDetectionV2", "lanewidth")
    if lanewidth == None:
        settings.CreateSettings("NavigationDetectionV2", "lanewidth", 10)
        lanewidth = 10
    lanewidth = round(lanewidth, 2)


############################################################################################################################    
# NavigationDetectionV3 Settings
############################################################################################################################
def LoadSettingsV3():
    global setupmode
    global last_window_size
    global last_mouse_position
    global v3setupzoom
    global zoomoffsetx
    global zoomoffsety
    global moverootx
    global moverooty
    global gettopleft
    global getbottomright
    global getcentercoord
    global topleft
    global bottomright
    global centercoord
    global mousecoordroot

    global navigationsymbol_x
    global navigationsymbol_y

    global v3_offset

    global trafficlightdetection_is_enabled
    global lefthand_traffic

    global check_zoom_timer
    global do_zoom
    global do_blocked
    global allow_playsound
    global allow_playsound_timer

    global controls_last_left
    global controls_last_right

    global left_x_lane
    global right_x_lane
    global left_x_turn
    global right_x_turn
    global left_x_turndrive
    global right_x_turndrive
    global approve_upper_y_left
    global approve_lower_y_left
    global approve_upper_y_right
    global approve_lower_y_right
    
    global detection_offset_lane_y

    global turnincoming_detected
    global turnincoming_direction
    global turnincoming_last_detected

    global indicator_last_left
    global indicator_last_right
    global indicator_left_wait_for_response
    global indicator_right_wait_for_response
    global indicator_left_response_timer
    global indicator_right_response_timer
    global indicator_enable_left
    global indicator_enable_right
    global indicator_changed_by_code

    global lanechanging_do_lane_changing
    global lanechanging_speed
    global lanechanging_width
    global lanechanging_autolanezero
    global lanechanging_current_lane
    global lanechanging_final_offset

    setupmode = False
    last_window_size = 0
    last_mouse_position = 0
    v3setupzoom = 0
    zoomoffsetx = 0
    zoomoffsety = 0
    moverootx = 0
    moverooty = 0
    gettopleft = False
    getbottomright = False
    getcentercoord = False
    mousecoordroot = None
    topleft = settings.GetSettings("NavigationDetectionV3", "topleft", "unset")
    bottomright = settings.GetSettings("NavigationDetectionV3", "bottomright", "unset")
    centercoord = settings.GetSettings("NavigationDetectionV3", "centercoord", "unset")
    screencap_x = settings.GetSettings("dxcam", "x")
    screencap_y = settings.GetSettings("dxcam", "y")

    if topleft == "unset":
        topleft = None
    if bottomright == "unset":
        bottomright = None
    if centercoord == "unset":
        centercoord = None

    if centercoord != None and screencap_x != None and screencap_y != None:
        navigationsymbol_x = centercoord[0] - screencap_x
        navigationsymbol_y = centercoord[1] - screencap_y
        if navigationsymbol_x < 0:
            navigationsymbol_x = 0
        if navigationsymbol_y < 0:
            navigationsymbol_y = 0
    else:
        navigationsymbol_y = 0
        navigationsymbol_x = 0

    v3_offset = settings.GetSettings("NavigationDetectionV3", "offset", 0)

    if "TrafficLightDetection" in settings.GetSettings("Plugins", "Enabled"):
        trafficlightdetection_is_enabled = True
    else:
        trafficlightdetection_is_enabled = False

    lefthand_traffic = settings.GetSettings("NavigationDetectionV3", "lefthand_traffic", False)

    check_zoom_timer = 0
    do_zoom = False
    do_blocked = False
    allow_playsound = False
    allow_playsound_timer = time.time()

    controls_last_left = False
    controls_last_right = False

    left_x_lane = 0
    right_x_lane = 0
    left_x_turn = 0
    right_x_turn = 0
    left_x_turndrive = 0
    right_x_turndrive = 0
    last_width_lane = 0
    approve_upper_y_left = 0
    approve_lower_y_left = 0
    approve_upper_y_right = 0
    approve_lower_y_right = 0

    detection_offset_lane_y = 0

    turnincoming_detected = False
    turnincoming_direction = None
    turnincoming_last_detected = 0

    indicator_last_left = False
    indicator_last_right = False
    indicator_left_wait_for_response = False
    indicator_right_wait_for_response = False
    indicator_left_response_timer = 0
    indicator_right_response_timer = 0
    indicator_enable_left = False
    indicator_enable_right = False
    indicator_changed_by_code = True

    lanechanging_do_lane_changing = settings.GetSettings("NavigationDetectionV3", "lanechanging_do_lane_changing", True)
    lanechanging_speed = settings.GetSettings("NavigationDetectionV3", "lanechanging_speed", 1)
    lanechanging_width = settings.GetSettings("NavigationDetectionV3", "lanechanging_width", 10)
    lanechanging_autolanezero = settings.GetSettings("NavigationDetectionV3", "lanechanging_autolanezero", True)
    lanechanging_current_lane = 0
    lanechanging_final_offset = 0


############################################################################################################################
# Main Settings
############################################################################################################################
def LoadSettings():
    global version
    version = settings.GetSettings("NavigationDetection", "version", "NavigationDetectionV3")
    if version == "NavigationDetectionV1":         
        LoadSettingsV1()
    if version == "NavigationDetectionV2":              
        LoadSettingsV2()
    if version == "NavigationDetectionV3":
        LoadSettingsV3()
    global mod
    mod = settings.GetSettings("NavigationDetection", "mod", "0")
LoadSettings()


def plugin(data):

############################################################################################################################
# NavigationDetectionV1 Code
############################################################################################################################
    if version == "NavigationDetectionV1":
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

        global highest_y
        global lowest_y

        global navsymboldetecXOffset
        global navsymboldetecXOffset_lasttimemoved
        global navsymboldetecXOffset_timedifference
        global navsymboldetecXOffset_wasmoved
        global last_navsymboldetecXOffset

        global turnincoming
        global timerforturnincomingv1
        global width_y_symbol
        
        global turnstrength

        try:
            picture_np = data["frame"]
        except:
            return data
        
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

        if lowest_y is None or highest_y is None:
            navsymboldetecXOffset_timedifference = 15

        if navsymboldetecXOffset_timedifference < 20:
            highest_y = None
            lowest_y = None

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
                timerforturnincomingv1 = time.time()
        except:
            pass
        try:
            currenttime = time.time()
            timerdifference = (currenttime - timerforturnincomingv1)
        except:
            pass
        try:
            if turnincoming == 1:
                cv2.putText(picture_np, f"turn inc", (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (2, 137, 240), 1, cv2.LINE_AA)
                if timerdifference > 30:
                    turnincoming = 0
        except:
            pass
        
        
        if lane_width:
            if lane_width > 60:
                if left_x < width/2-40:
                    turndetected = 1
                    timerforturnincomingv1 = time.time()-27
                if right_x > width/2+40:
                    turndetected = 2
                    timerforturnincomingv1 = time.time()-27
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

        if center_x != width and center_x is not None and center_x_curve is not None:
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
            if center_x != 0 and center_x != width and center_x_curve != 0 and center_x_curve != width:
                cv2.line(picture_np, (int(center_x), y_coordinate_of_lane_detection), (int(center_x_curve), y_coordinate_of_curve_detection), (255, 0, 0), 1)
        except:
            pass
        try:
            if center_x_curve != 0 and center_x_curve != width and center_x_turnincdetec != 0 and center_x_turnincdetec != width:
                cv2.line(picture_np, (int(center_x_curve), y_coordinate_of_curve_detection), (int(center_x_turnincdetec), y_coordinate_of_turnincdetec), (255, 0, 0), 1)
        except:
            pass
        try:
            if center_x != 0 and center_x != width and center_x_drivenroad != 0 and center_x_drivenroad != width:
                cv2.line(picture_np, (int(center_x), y_coordinate_of_lane_detection), (int(center_x_drivenroad), y_coordinate_of_drivenroad), (255, 0, 0), 1)
        except:
            pass
        try:
            if left_x != 0 and left_x != width and left_x_curve != 0 and left_x_curve  != width:
                cv2.line(picture_np, (int(left_x), y_coordinate_of_lane_detection), (int(left_x_curve), y_coordinate_of_curve_detection), (255, 175, 0), 2)
        except:
            pass
        try:
            if right_x != 0 and right_x != width and right_x_curve != 0 and right_x_curve  != width:
                cv2.line(picture_np, (int(right_x), y_coordinate_of_lane_detection), (int(right_x_curve), y_coordinate_of_curve_detection), (255, 175, 0), 2)
        except:
            pass
        try:
            if left_x_curve != 0 and left_x_curve != width and left_x_turnincdetec != 0 and left_x_turnincdetec != width:
                cv2.line(picture_np, (int(left_x_curve), y_coordinate_of_curve_detection), (int(left_x_turnincdetec), y_coordinate_of_turnincdetec), (255, 175, 0), 2)
        except:
            pass
        try:
            if right_x_curve != 0 and right_x_curve != width and right_x_turnincdetec != 0 and right_x_turnincdetec != width:
                cv2.line(picture_np, (int(right_x_curve), y_coordinate_of_curve_detection), (int(right_x_turnincdetec), y_coordinate_of_turnincdetec), (255, 175, 0), 2)
        except:
            pass
        try:
            if left_x != 0 and left_x != width and left_x_drivenroad != 0 and left_x_drivenroad != width:
                cv2.line(picture_np, (int(left_x), y_coordinate_of_lane_detection), (int(left_x_drivenroad), y_coordinate_of_drivenroad), (255, 175, 0), 2)
        except:
            pass
        try:
            if right_x != 0 and right_x != width and right_x_drivenroad != 0 and right_x_drivenroad != width:
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
            if navsymboldetecXOffset_timedifference < 20:
                try:
                    cv2.line(picture_np, (int(navsymboldetecXOffset), 10), (int(navsymboldetecXOffset), height-10), (255, 255, 255), 1)
                except:
                    pass
        except:
            pass

        distancetocenter = round(distancetocenter/10,3)
        
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


############################################################################################################################
# NavigationDetectionV2 Code
############################################################################################################################
    if version == "NavigationDetectionV2":
        global timerforturnincoming
        global turnincdirec
        global white_limit
        global getnavcoordinates
        global navcoordsarezero
        global trafficlightdetectionisenabled
        global trucksimapiisenabled

        global currentlane
        global lastblinker
        global currentoffsetsteeringvalue
        global lanechangingspeed
        global lanechanging
        global lanewidth

        global avg_lanewidth
        global avg_lanewidth_counter
        global avg_lanewidth_value

        global disableshowimagelater

        if getnavcoordinates == True or navcoordsarezero == True:

            
            try:
                frame = data["frame"]
                width = frame.shape[1]
                height = frame.shape[0]
                min_x = settings.GetSettings("dxcam", "x")
                min_y = settings.GetSettings("dxcam", "y")
            except:
                return data 
            

            mousex, mousey = mouse.get_position()
            circlex = mousex - min_x
            circley = mousey - min_y
            if circlex > 5 and circlex < width-5 and circley > 5 and circley < height-5:
                cv2.circle(frame, (circlex,circley), round(width/40), (40,130,210), 2)
            else:

                vector_mousetocenter_x = round((min_x + width/2) - mousex)
                vector_mousetocenter_y = round((min_y + height/2) - mousey)

                original_length = math.sqrt(vector_mousetocenter_x**2 + vector_mousetocenter_y**2)

                vector_mousetocenter_x = round((vector_mousetocenter_x / original_length) * width*1.5)
                vector_mousetocenter_y = round((vector_mousetocenter_y / original_length) * width*1.5)

                scaled_length = original_length / 2

                angle_degrees = 45

                angle_radians = math.radians(angle_degrees)

                x_scaled = (vector_mousetocenter_x / original_length) * scaled_length
                y_scaled = (vector_mousetocenter_y / original_length) * scaled_length

                x_counterclockwise = x_scaled * math.cos(angle_radians) - y_scaled * math.sin(angle_radians)
                y_counterclockwise = x_scaled * math.sin(angle_radians) + y_scaled * math.cos(angle_radians)

                x_clockwise = x_scaled * math.cos(-angle_radians) - y_scaled * math.sin(-angle_radians)
                y_clockwise = x_scaled * math.sin(-angle_radians) + y_scaled * math.cos(-angle_radians)

                cv2.line(frame, (round(width/2 - x_counterclockwise/10), round(height/1.5 - y_counterclockwise/10)), (round(width/2), round(height/1.5)), (156,0,91), 2, cv2.LINE_AA)
                cv2.line(frame, (round(width/2 - x_clockwise/10), round(height/1.5 - y_clockwise/10)), (round(width/2), round(height/1.5)), (156,0,91), 2, cv2.LINE_AA)
                cv2.line(frame, (round(width/2 - vector_mousetocenter_x/10), round(height/1.5 - vector_mousetocenter_y/10)), (round(width/2), round(height/1.5)), (156,0,91), 2, cv2.LINE_AA)
                cv2.putText(frame, "move your mouse in the", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (156,0,91), 2)
                cv2.putText(frame, "direction the arrow shows", (5, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (156,0,91), 2)
            
            if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0:
                left_clicked = True
            else:
                left_clicked = False

            if left_clicked == True and circlex > 5 and circlex < width-5 and circley > 5 and circley < height-5:
                settings.CreateSettings("NavigationDetectionV2", "navsymbolx", circlex)    
                settings.CreateSettings("NavigationDetectionV2", "navsymboly", circley)
                
                if disableshowimagelater == True:
                    settings.RemoveFromList("Plugins", "Enabled", "ShowImage")

                    if "ShowImage" not in settings.GetSettings("Plugins", "Enabled"):
                        DefaultSteering.enabled = True
                        variables.ENABLELOOP = False
                        disableshowimagelater = False
                        getnavcoordinates = False
                        navcoordsarezero = False
                else:
                    DefaultSteering.enabled = True
                    variables.ENABLELOOP = False
                    disableshowimagelater = False
                    getnavcoordinates = False
                    navcoordsarezero = False


            data["frame"] = frame

        else:

            start_time = time.time()
            
            try:
                frame = data["frame"]
            except:
                return data
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            try:
                width = frame.shape[1]
                height = frame.shape[0]
                min_x = settings.GetSettings("dxcam", "x")
                min_y = settings.GetSettings("dxcam", "y")
            except:
                return data
            
            try:
                gamepaused = data["api"]["pause"]
            except:
                gamepaused = False

            lower_red = np.array([160, 0, 0])
            upper_red = np.array([255, 110, 110])
            lower_green = np.array([0, 200, 0])
            upper_green = np.array([150, 255, 230])

            mask_red = cv2.inRange(frame, lower_red, upper_red)
            mask_green = cv2.inRange(frame, lower_green, upper_green)

            filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))

            cv2.rectangle(filtered_frame_red_green, (0,0), (round((width/6)),round((height/3))),(0,0,0),-1)

            filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)

            filtered_frame_bw = cv2.GaussianBlur(filtered_frame_bw,(3,3),0)


            #get the left and right x coordinates
            def GetArrayOfLaneEdges(y_coordinate_of_lane_detection):
                detectingLane = False
                laneEdges = []
                
                for x in range(0, int(width)):
                    pixel = filtered_frame_bw[y_coordinate_of_lane_detection, x]
                    pixel = (pixel, pixel, pixel)
                    if (white_limit[0] <= pixel[0]):
                        
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
            
            circley = settings.GetSettings("NavigationDetectionV2", "navsymboly")
            circlex = settings.GetSettings("NavigationDetectionV2", "navsymbolx")
            y_coordinate_turnincdetec = round(circley / 4)
            y_coordinate_lane = round(circley / 1.4)
            automaticxoffset = round(width/2-circlex)

            if trafficlightdetectionisenabled == True:
                try:
                    trafficlight = data["TrafficLightDetection"]["simple"]
                except:
                    trafficlightdetectionisenabled = False
                    trafficlight = "Off"
            else:
                trafficlight = "Off"

            if circley != None:        
                lanes = GetArrayOfLaneEdges(y_coordinate_turnincdetec)
                if automaticlaneselection == True:
                    try:
                        closest_x_pair = min([(left_x, right_x) for left_x, right_x in zip(lanes[::2], lanes[1::2])], key=lambda pair: abs((pair[0] + pair[1]) / 2 - circlex))
                        left_x_turnincdetec, right_x_turnincdetec = closest_x_pair
                    except:
                        if leftsidetraffic == False:
                            left_x_turnincdetec = lanes[len(lanes)-2]
                            right_x_turnincdetec = lanes[len(lanes)-1]
                        else:
                            try:
                                left_x_turnincdetec = lanes[len(lanes)-4]
                                right_x_turnincdetec = lanes[len(lanes)-3]
                            except:
                                left_x_turnincdetec = lanes[len(lanes)-2]
                                right_x_turnincdetec = lanes[len(lanes)-1]
                else:
                    if leftsidetraffic == False:
                        left_x_turnincdetec = lanes[len(lanes)-2]
                        right_x_turnincdetec = lanes[len(lanes)-1]
                    else:
                        try:
                            left_x_turnincdetec = lanes[len(lanes)-4]
                            right_x_turnincdetec = lanes[len(lanes)-3]
                        except:
                            left_x_turnincdetec = lanes[len(lanes)-2]
                            right_x_turnincdetec = lanes[len(lanes)-1]
                cv2.line(filtered_frame_bw, (left_x_turnincdetec,y_coordinate_turnincdetec), (right_x_turnincdetec,y_coordinate_turnincdetec), (255,255,255),1)

                lanes = GetArrayOfLaneEdges(y_coordinate_lane)
                if automaticlaneselection == True:
                    try:
                        closest_x_pair = min([(left_x, right_x) for left_x, right_x in zip(lanes[::2], lanes[1::2])], key=lambda pair: abs((pair[0] + pair[1]) / 2 - circlex))
                        left_x_laneedge, right_x_laneedge = closest_x_pair
                    except:
                        if leftsidetraffic == False:
                            left_x_laneedge = lanes[len(lanes)-2]
                            right_x_laneedge = lanes[len(lanes)-1]
                        else:
                            try:
                                left_x_laneedge = lanes[len(lanes)-4]
                                right_x_laneedge = lanes[len(lanes)-3]
                            except:
                                left_x_laneedge = lanes[len(lanes)-2]
                                right_x_laneedge = lanes[len(lanes)-1]
                else:
                    if leftsidetraffic == False:
                        left_x_laneedge = lanes[len(lanes)-2]
                        right_x_laneedge = lanes[len(lanes)-1]
                    else:
                        try:
                            left_x_laneedge = lanes[len(lanes)-4]
                            right_x_laneedge = lanes[len(lanes)-3]
                        except:
                            left_x_laneedge = lanes[len(lanes)-2]
                            right_x_laneedge = lanes[len(lanes)-1]
                cv2.line(filtered_frame_bw, (left_x_laneedge,y_coordinate_lane), (right_x_laneedge,y_coordinate_lane), (255,255,255),1)

                if left_x_laneedge == 0:
                    left_x_laneedge = 1
                if left_x_turnincdetec == 0:
                    left_x_turnincdetec = 1

                lane_width = right_x_laneedge - left_x_laneedge
            
                lane_width_turnincdetec = right_x_turnincdetec - left_x_turnincdetec

                if lane_width_turnincdetec > width/5:
                    timerforturnincoming = time.time()
                    currentlane = 0
                    if width/2 - left_x_turnincdetec > right_x_turnincdetec - width/2:
                        turnincdirec = "Left"
                    else:
                        turnincdirec = "Right"

                if start_time - timerforturnincoming < 20:
                    turnincoming = True
                else:
                    turnincoming = False

                if DefaultSteering.enabled == False:
                    timerforturnincoming = time.time()-21
                    turnincoming = False

                if trafficlight == "Red":
                    if turnincoming == True:
                        timerforturnincoming = time.time() - 10

                if turnincoming == False and lane_width != 0:
                    avg_lanewidth_counter += 1
                    avg_lanewidth_value += lane_width
                    avg_lanewidth = avg_lanewidth_value/avg_lanewidth_counter
                
                if turnincoming == False:
                    center_x = (left_x_laneedge + right_x_laneedge) / 2 if left_x_laneedge and right_x_laneedge is not None else None
                else:
                    if turnincdirec == "Right":
                        center_x = left_x_laneedge + avg_lanewidth/2
                    else:
                        center_x = right_x_laneedge - avg_lanewidth/2
            
                center_x_turnincdetec = (left_x_turnincdetec + right_x_turnincdetec) / 2 if left_x_turnincdetec and right_x_turnincdetec is not None else None
                

            if lane_width > width/5: ######################################################### change the minimum lane width
                if width/2 - left_x_laneedge > right_x_laneedge - width/2:
                    turn = "Left"
                    timerforturnincoming = time.time() - 17
                else:
                    turn = "Right"
                    timerforturnincoming = time.time() - 17
            else:
                turn = "none"

            if lanechanging == True:
                if trucksimapiisenabled == True:
                    try:
                        IndicatingLeft = data["api"]["truckBool"]["blinkerLeftActive"]
                        IndicatingRight = data["api"]["truckBool"]["blinkerRightActive"]
                    except:
                        IndicatingLeft = False
                        IndicatingRight = False
                        trucksimapiisenabled = False
                
                    if IndicatingLeft == True and lastblinker != "left":
                        currentlane += 1
                        lastblinker = "left"

                    if IndicatingRight == True and lastblinker != "right":
                        currentlane -= 1
                        lastblinker = "right"

                    if IndicatingLeft == False and IndicatingRight == False:
                        lastblinker = None

                    targetoffsetsteeringvalue = round(lanewidth * currentlane, 2)
                    
                    lanecorrection = targetoffsetsteeringvalue - currentoffsetsteeringvalue
                    if abs(lanecorrection) > lanechangingspeed/10:
                        if lanecorrection > 0:
                            lanecorrection = lanechangingspeed/10
                        else:
                            lanecorrection = -lanechangingspeed/10

                    currentoffsetsteeringvalue += lanecorrection
            

            if center_x != width and center_x is not None and gamepaused == False:
                curve = round((center_x - center_x_turnincdetec)/30 * curvemultip, 3)
                if turn != "none" or turnincoming == True or center_x_turnincdetec == width:
                    curve = 0
                distancetocenter = round((width/2-center_x)-curve-automaticxoffset + currentoffsetsteeringvalue, 3) - offset
                lanedetected = "Yes"
            else:
                lanedetected = "No"
                distancetocenter = 0
                curve = 0
                center_x = round(width/2)
                center_x_turnincdetec = round(width/2)
            
            correction = distancetocenter * sensitivity

            data["LaneDetection"] = {}
            data["LaneDetection"]["difference"] = -correction/30

            correction = round(correction, 3)

            if lanedetected == "Yes":
                lane_detected = True
            else:
                lane_detected = False

            data["NavigationDetection"] = {}
            data["NavigationDetection"]["lanedetected"] = lane_detected
            data["NavigationDetection"]["turnincoming"] = turnincoming

            if turn != "none" or turnincoming == True or center_x_turnincdetec == width:
                data["NavigationDetection"]["curve"] = correction / 5
            else:
                data["NavigationDetection"]["curve"] = (center_x - center_x_turnincdetec)/30 

            data["NavigationDetection"]["lane"] = currentlane
            data["NavigationDetection"]["laneoffsetpercent"] = currentoffsetsteeringvalue/lanewidth

            filtered_frame_red_green = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2RGB)
    
            if textsize != 0:      
                cv2.putText(filtered_frame_bw, f"lanedetected: {lanedetected}", (round(10*textdistancescale), round(20*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(filtered_frame_bw, f"curve: {curve}", (round(10*textdistancescale), round(40*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(filtered_frame_bw, f"correction: {correction}", (round(10*textdistancescale), round(60*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(filtered_frame_bw, f"turninc: {turnincoming}", (round(10*textdistancescale), round(80*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(filtered_frame_bw, f"turn: {turn}", (round(10*textdistancescale), round(100*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(filtered_frame_bw, f"lane: {currentlane}", (round(10*textdistancescale), round(120*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(filtered_frame_bw, f"trafficlight: {trafficlight}", (round(10*textdistancescale), round(140*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)

            data["frame"] = filtered_frame_bw



############################################################################################################################
# NavigationDetectionV3 Code
############################################################################################################################
    if version == "NavigationDetectionV3":
        global setupmode
        global setupframe
        global last_window_size
        global last_mouse_position
        global v3setupzoom
        global zoomoffsetx
        global zoomoffsety
        global moverootx
        global moverooty
        global gettopleft
        global getbottomright
        global getcentercoord
        global topleft
        global bottomright
        global centercoord
        global mousecoordroot

        global navigationsymbol_x
        global navigationsymbol_y

        global v3_offset

        global trafficlightdetection_is_enabled
        global lefthand_traffic

        global check_zoom_timer
        global do_zoom
        global do_blocked
        global allow_playsound
        global allow_playsound_timer
        
        global controls_last_left
        global controls_last_right

        global left_x_lane
        global right_x_lane
        global left_x_turn
        global right_x_turn
        global left_x_turndrive
        global right_x_turndrive
        global approve_upper_y_left
        global approve_lower_y_left
        global approve_upper_y_right
        global approve_lower_y_right
        
        global detection_offset_lane_y

        global turnincoming_detected
        global turnincoming_direction
        global turnincoming_last_detected

        global indicator_last_left
        global indicator_last_right
        global indicator_left_wait_for_response
        global indicator_right_wait_for_response
        global indicator_left_response_timer
        global indicator_right_response_timer
        global indicator_enable_left
        global indicator_enable_right
        global indicator_changed_by_code

        global lanechanging_do_lane_changing
        global lanechanging_speed
        global lanechanging_width
        global lanechanging_autolanezero
        global lanechanging_current_lane
        global lanechanging_final_offset
        
        
        if setupmode == True:
            finishedsetup = False

            frame = setupframe.copy()
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]

            if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, 'Setup'):
                left_clicked = True
            else:
                left_clicked = False

            try:
                x1, y1, width, height = cv2.getWindowImageRect('Setup')
                x2, y2 = mouse.get_position()
                mousex = x2-x1
                mousey = y2-y1
                last_window_size = (x1, y1, width, height)
                last_mouse_position = (x2, y2)
            except:
                x1, y1, width, height = last_window_size
                x2, y2 = last_mouse_position
                mousex = x2-x1
                mousey = y2-y1
                frame_width = setupframe.shape[1]
                frame_height = setupframe.shape[0]
                cv2.namedWindow('Setup', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Setup', round(frame_width/2), round(frame_height/2))
                startframe = np.zeros((round(frame_height/2), round(frame_width/2), 3))
                cv2.putText(startframe, "waiting...", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            if width != 0 and height != 0:
                mouseposx = mousex/width
                mouseposy = mousey/height

            setupframetextsize = math.sqrt(width)/35
            setupframetextthickness = round(math.sqrt(width)/35)*2
            setupframelinethickness = round(math.sqrt(width)/35)*2
            if setupframetextthickness == 0:
                setupframetextthickness = 1
            if setupframelinethickness == 0:
                setupframelinethickness = 1

            corner1 = round(frame_height*v3setupzoom/100)+zoomoffsety
            corner2 = round(frame_height-frame_height*v3setupzoom/100)+zoomoffsety
            corner3 = round(frame_width*v3setupzoom/100)+zoomoffsetx
            corner4 = round(frame_width-frame_width*v3setupzoom/100)+zoomoffsetx

            if corner1 < 0:
                corner1 = 0
            if corner1 > frame_height:
                corner1 = frame_height
            
            if corner2 < 0:
                corner2 = 0
            if corner2 > frame_height:
                corner2 = frame_height
            
            if corner3 < 0:
                corner3 = 0
            if corner3 > frame_width:
                corner3 = frame_width
            
            if corner4 < 0:
                corner4 = 0
            if corner4 > frame_width:
                corner4 = frame_width
            
            original_pixel_x = round(corner3+mouseposx*(corner4-corner3))
            original_pixel_y = round(corner1+mouseposy*(corner2-corner1))

            if left_clicked == False:
                mousecoordroot = mouseposx, mouseposy
            if mousecoordroot == None:
                mousecoordroot = 0, 0

            if gettopleft == True:
                cv2.line(frame, (round(original_pixel_x), round(0*frame_height)), (round(original_pixel_x), round(1*frame_height)), (0,0,150), setupframelinethickness)
                cv2.line(frame, (round(0*frame_width), round(original_pixel_y)), (round(1*frame_width), round(original_pixel_y)), (0,0,150), setupframelinethickness)
                cv2.putText(frame, "Top Left", (round(original_pixel_x+setupframetextsize*5), round(original_pixel_y+setupframetextsize*30)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
                cv2.putText(frame, f"{round(original_pixel_x), round(original_pixel_y)}", (round(original_pixel_x+setupframetextsize*5), round(original_pixel_y-setupframetextsize*10)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
            else:
                if topleft != None:
                    xpos, ypos = topleft
                    cv2.line(frame, (round(xpos), round(0*frame_height)), (round(xpos), round(1*frame_height)), (0,0,150), setupframelinethickness)
                    cv2.line(frame, (round(0*frame_width), round(ypos)), (round(1*frame_width), round(ypos)), (0,0,150), setupframelinethickness)
                    cv2.putText(frame, "Top Left", (round(xpos+setupframetextsize*5), round(ypos+setupframetextsize*30)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
                    cv2.putText(frame, f"{topleft}", (round(xpos+setupframetextsize*5), round(ypos-setupframetextsize*10)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
            
            if getbottomright == True:
                cv2.line(frame, (round(original_pixel_x), round(0*frame_height)), (round(original_pixel_x), round(1*frame_height)), (0,0,150), setupframelinethickness)
                cv2.line(frame, (round(0*frame_width), round(original_pixel_y)), (round(1*frame_width), round(original_pixel_y)), (0,0,150), setupframelinethickness)
                cv2.putText(frame, "Bottom Right", (round(original_pixel_x-setupframetextsize*220), round(original_pixel_y-setupframetextsize*10)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
                cv2.putText(frame, f"{round(original_pixel_x), round(original_pixel_y)}", (round(original_pixel_x-setupframetextsize*220), round(original_pixel_y+setupframetextsize*30)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
            else:
                if bottomright != None:
                    xpos, ypos = bottomright
                    cv2.line(frame, (round(xpos), round(0*frame_height)), (round(xpos), round(1*frame_height)), (0,0,150), setupframelinethickness)
                    cv2.line(frame, (round(0*frame_width), round(ypos)), (round(1*frame_width), round(ypos)), (0,0,150), setupframelinethickness)
                    cv2.putText(frame, "Bottom Right", (round(xpos-setupframetextsize*220), round(ypos-setupframetextsize*10)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
                    cv2.putText(frame, f"{bottomright}", (round(xpos-setupframetextsize*220), round(ypos+setupframetextsize*30)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
            
            if topleft != None and bottomright != None and gettopleft == False and getbottomright == False:
                cv2.line(frame, (round(topleft[0]), round(topleft[1])), (round(topleft[0]), round(bottomright[1])), (0,0,255), setupframelinethickness)
                cv2.line(frame, (round(bottomright[0]), round(topleft[1])), (round(bottomright[0]), round(bottomright[1])), (0,0,255), setupframelinethickness)
                cv2.line(frame, (round(topleft[0]), round(topleft[1])), (round(bottomright[0]), round(topleft[1])), (0,0,255), setupframelinethickness)
                cv2.line(frame, (round(topleft[0]), round(bottomright[1])), (round(bottomright[0]), round(bottomright[1])), (0,0,255), setupframelinethickness)

            if getcentercoord == True:
                cv2.circle(frame, (round(original_pixel_x), round(original_pixel_y)), round(setupframetextsize*10), (40,130,210), setupframelinethickness)
            else:
                if centercoord != None:
                    xpos, ypos = centercoord
                    cv2.circle(frame, (round(xpos), round(ypos)), round(setupframetextsize*10), (40,130,210), setupframelinethickness)
            
            if gettopleft == True and left_clicked == True:
                if mouseposx >= 0.22 and mouseposy >= 0.0 and mouseposx <= 0.35 and mouseposy <= 0.1:
                    pass
                else:
                    gettopleft = False
                    topleft = (original_pixel_x, original_pixel_y)
                    allowerror = True
                    if topleft != None and bottomright != None:
                        if topleft[0] > bottomright[0] and allowerror == True:
                            messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                            allowerror = False
                        if topleft[1] > bottomright[1] and allowerror == True:
                            messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                            allowerror = False
                    if allowerror == True:
                        settings.CreateSettings("NavigationDetectionV3", "topleft", (round(original_pixel_x), round(original_pixel_y)))
                    else:
                        topleft = settings.GetSettings("NavigationDetectionV3", "topleft", None)

            if getbottomright == True and left_clicked == True:
                if mouseposx >= 0.42 and mouseposy >= 0.0 and mouseposx <= 0.58 and mouseposy <= 0.1:
                    pass
                else:
                    getbottomright = False
                    bottomright = (original_pixel_x, original_pixel_y)
                    allowerror = True
                    if topleft != None and bottomright != None:
                        if topleft[0] > bottomright[0] and allowerror == True:
                            messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                            allowerror = False
                        if topleft[1] > bottomright[1] and allowerror == True:
                            messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                            allowerror = False
                    if allowerror == True:
                        settings.CreateSettings("NavigationDetectionV3", "bottomright", (round(original_pixel_x), round(original_pixel_y)))
                    else:
                        bottomright = settings.GetSettings("NavigationDetectionV3", "bottomright", None)

            if getcentercoord == True and left_clicked == True:
                if mouseposx >= 0.65 and mouseposy >= 0.0 and mouseposx <= 0.78 and mouseposy <= 0.1:
                    pass
                else:
                    getcentercoord = False
                    centercoord = (original_pixel_x, original_pixel_y)
                    allowerror = True
                    if topleft != None and bottomright != None:
                        if topleft[0] > bottomright[0] and allowerror == True:
                            messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                            allowerror = False
                        if topleft[1] > bottomright[1] and allowerror == True:
                            messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                            allowerror = False
                    if allowerror == True:
                        settings.CreateSettings("NavigationDetectionV3", "centercoord", (round(original_pixel_x), round(original_pixel_y)))
                    else:
                        centercoord = settings.GetSettings("NavigationDetectionV3", "centercoord", None)

            if corner1 < corner2 and corner3 < corner4:
                frame = frame[corner1:corner2, corner3:corner4]
            else:
                zoomoffsetx = 0
                zoomoffsety = 0
            
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]

            if mouseposx >= 0.0 and mouseposy >= 0.0 and mouseposx <= 0.1 and mouseposy <= 0.05 and mousecoordroot[1] < 0.30:
                cv2.rectangle(frame, (round(0.0*frame_width), round(0.0*frame_height)), (round(0.1*frame_width), round(0.05*frame_height)), (70, 20, 20), -1)
                if left_clicked == True:
                    if round(frame_height*v3setupzoom/100) < round(frame_height-frame_height*v3setupzoom/100) - frame_height/2:
                        v3setupzoom += 0.3
                    if v3setupzoom < 0:
                        v3setupzoom = 0
            else:
                cv2.rectangle(frame, (round(0.0*frame_width), round(0.0*frame_height)), (round(0.1*frame_width), round(0.05*frame_height)), (50, 0, 0), -1)
            current_text = "Zoom IN"
            width_target_current_text = frame_width/10
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
            cv2.putText(frame, "Zoom IN", (round(0.0*frame_width), round(0.04*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

            
            if mouseposx >= 0.0 and mouseposy >= 0.07 and mouseposx <= 0.1 and mouseposy <= 0.12 and mousecoordroot[1] < 0.30:
                cv2.rectangle(frame, (round(0.0*frame_width), round(0.07*frame_height)), (round(0.1*frame_width), round(0.12*frame_height)), (70, 20, 20), -1)
                if left_clicked == True:
                    v3setupzoom -= 0.3
                    if v3setupzoom < 0:
                        v3setupzoom = 0
            else:
                cv2.rectangle(frame, (round(0.0*frame_width), round(0.07*frame_height)), (round(0.1*frame_width), round(0.12*frame_height)), (50, 0, 0), -1)
            current_text = "Zoom OUT"
            width_target_current_text = frame_width/10
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
            cv2.putText(frame, "Zoom OUT", (round(0.0*frame_width), round(0.11*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
            
            if mouseposx >= 0.0 and mouseposy >= 0.14 and mouseposx <= 0.1 and mouseposy <= 0.22 and mousecoordroot[1] < 0.30:
                cv2.rectangle(frame, (round(0.0*frame_width), round(0.14*frame_height)), (round(0.1*frame_width), round(0.22*frame_height)), (70, 20, 20), -1)
                if left_clicked == True:
                    screenshot = pyautogui.screenshot()
                    setupframe = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    frame = setupframe.copy()
                    frame_width = frame.shape[1]
                    frame_height = frame.shape[0]
            else:
                cv2.rectangle(frame, (round(0.0*frame_width), round(0.14*frame_height)), (round(0.1*frame_width), round(0.22*frame_height)), (50, 0, 0), -1)
            current_text = "Screenshot"
            width_target_current_text = frame_width/10
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
            cv2.putText(frame, "Screenshot", (round(0.0*frame_width), round(0.21*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
            textsize_current_text, _ = cv2.getTextSize("New", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, "New", (round(0.05*frame_width-width_current_text/2), round(0.17*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

            if mouseposx >= 0.0 and mouseposy >= 0.24 and mouseposx <= 0.1 and mouseposy <= 0.29 and mousecoordroot[1] < 0.30:
                cv2.rectangle(frame, (round(0.0*frame_width), round(0.24*frame_height)), (round(0.1*frame_width), round(0.29*frame_height)), (0, 0, 255), -1)
                if left_clicked == True:
                    if messagebox.askokcancel("Setup", (f"Do you really want to reset the setup to default settings?")):
                        zoomoffsetx = 0
                        zoomoffsety = 0
                        v3setupzoom = 0
                        topleft = None
                        bottomright = None
                        centercoord = None

                        frame = setupframe.copy()
                        frame_width = frame.shape[1]
                        frame_height = frame.shape[0]
                        
                        # Code below by Tumppi066
                        minimapDistanceFromRight = 27
                        minimapDistanceFromBottom = 134
                        minimapWidth = 560
                        minimapHeight = 293
                        scale = frame_height/1440
                        xCoord = frame_width - (minimapDistanceFromRight * scale + minimapWidth * scale)
                        yCoord = frame_height - (minimapDistanceFromBottom * scale + minimapHeight * scale)
                        topleft = (int(xCoord), int(yCoord))
                        xCoord = frame_width - (minimapDistanceFromRight * scale)
                        yCoord = frame_height - (minimapDistanceFromBottom * scale)
                        bottomright = (int(xCoord), int(yCoord))
                        #

                        if centercoord == None:
                            centercoord = round(topleft[0] + (bottomright[0] - topleft[0]) / 2), round(topleft[1] + (bottomright[1] - topleft[1]) / 1.86)
                            settings.CreateSettings("NavigationDetectionV3", "centercoord", centercoord)

                        settings.CreateSettings("NavigationDetectionV3", "topleft", topleft)
                        settings.CreateSettings("NavigationDetectionV3", "bottomright", bottomright)
                        settings.CreateSettings("NavigationDetectionV3", "centercoord", centercoord)
            else:
                cv2.rectangle(frame, (round(0.0*frame_width), round(0.24*frame_height)), (round(0.1*frame_width), round(0.29*frame_height)), (0, 0, 230), -1)
            current_text = "RESET"
            width_target_current_text = frame_width/12
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
            cv2.putText(frame, "RESET", (round(0.007*frame_width), round(0.28*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

            if left_clicked == False:
                moverootx = zoomoffsetx + mousex
                moverooty = zoomoffsety + mousey

            if mouseposx >= 0.0 and mouseposy >= 0.25 and mouseposx <= 1.0 and mouseposy <= 1.0:
                if left_clicked == True:
                    zoomoffsetx = moverootx - mousex
                    zoomoffsety = moverooty - mousey

            if mouseposx >= 0.9 and mouseposy >= 0.0 and mouseposx <= 1.0 and mouseposy <= 0.1 and mousecoordroot[1] < 0.30:
                cv2.rectangle(frame, (round(0.9*frame_width), round(0.0*frame_height)), (round(1.0*frame_width), round(0.1*frame_height)), (0, 235, 0), -1)
                if left_clicked == True:
                    finishedsetup = True
            else:
                cv2.rectangle(frame, (round(0.9*frame_width), round(0.0*frame_height)), (round(1.0*frame_width), round(0.1*frame_height)), (0, 215, 0), -1)
            current_text = "Finish"
            width_target_current_text = frame_width/15
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
            cv2.putText(frame, "Finish", (round(0.918*frame_width), round(0.041*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
            cv2.putText(frame, "Setup", (round(0.918*frame_width), round(0.084*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)


            if mouseposx >= 0.22 and mouseposy >= 0.0 and mouseposx <= 0.35 and mouseposy <= 0.1 and mousecoordroot[1] < 0.30:
                cv2.rectangle(frame, (round(0.22*frame_width), round(0.0*frame_height)), (round(0.35*frame_width), round(0.1*frame_height)), (252, 3, 90), -1)
                if left_clicked == True and getbottomright == False and getcentercoord == False:
                    gettopleft = True
            else:
                cv2.rectangle(frame, (round(0.22*frame_width), round(0.0*frame_height)), (round(0.35*frame_width), round(0.1*frame_height)), (232, 0, 70), -1)
            if gettopleft == True:
                cv2.rectangle(frame, (round(0.22*frame_width), round(0.0*frame_height)), (round(0.35*frame_width), round(0.1*frame_height)), (232, 0, 170), -1)
            current_text = "1. Get Top Left"
            width_target_current_text = frame_width/8
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
            cv2.putText(frame, "1. Get Top Left", (round(0.222*frame_width), round(0.035*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
            cv2.putText(frame, "   Coordinate", (round(0.218*frame_width), round(0.085*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)


            if mouseposx >= 0.42 and mouseposy >= 0.0 and mouseposx <= 0.58 and mouseposy <= 0.1 and mousecoordroot[1] < 0.30:
                cv2.rectangle(frame, (round(0.42*frame_width), round(0.0*frame_height)), (round(0.58*frame_width), round(0.1*frame_height)), (252, 3, 90), -1)
                if left_clicked == True and gettopleft == False and getcentercoord == False:
                    getbottomright = True
            else:
                cv2.rectangle(frame, (round(0.42*frame_width), round(0.0*frame_height)), (round(0.58*frame_width), round(0.1*frame_height)), (232, 0, 70), -1)
            if getbottomright == True:
                cv2.rectangle(frame, (round(0.42*frame_width), round(0.0*frame_height)), (round(0.58*frame_width), round(0.1*frame_height)), (232, 0, 170), -1)
            current_text = "2. Get Bottom Right"
            width_target_current_text = frame_width/6.5
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
            cv2.putText(frame, "2. Get Bottom Right", (round(0.424*frame_width), round(0.035*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
            cv2.putText(frame, "   Coordinate", (round(0.437*frame_width), round(0.085*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)


            if mouseposx >= 0.65 and mouseposy >= 0.0 and mouseposx <= 0.78 and mouseposy <= 0.1 and mousecoordroot[1] < 0.30:
                cv2.rectangle(frame, (round(0.65*frame_width), round(0.0*frame_height)), (round(0.78*frame_width), round(0.1*frame_height)), (252, 3, 90), -1)
                if left_clicked == True and gettopleft == False and getbottomright == False:
                    getcentercoord = True
            else:
                cv2.rectangle(frame, (round(0.65*frame_width), round(0.0*frame_height)), (round(0.78*frame_width), round(0.1*frame_height)), (232, 0, 70), -1)
            if getcentercoord == True:
                cv2.rectangle(frame, (round(0.65*frame_width), round(0.0*frame_height)), (round(0.78*frame_width), round(0.1*frame_height)), (232, 0, 170), -1)
            current_text = "3. Get Center"
            width_target_current_text = frame_width/7.9
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
            cv2.putText(frame, "3. Get Center", (round(0.652*frame_width), round(0.035*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
            cv2.putText(frame, "   Coordinate", (round(0.639*frame_width), round(0.085*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

            cv2.imshow('Setup', frame)
            cv2.imshow('Example Image', exampleimage)
            
            if finishedsetup == True:
                if topleft != None and bottomright != None:
                    settings.CreateSettings("dxcam", "x", topleft[0])
                    settings.CreateSettings("dxcam", "y", topleft[1])
                    settings.CreateSettings("dxcam", "width", bottomright[0] - topleft[0])
                    settings.CreateSettings("dxcam", "height", bottomright[1] - topleft[1])

                    import plugins.DXCamScreenCapture.main as dxcam
                    dxcam.CreateCamera()

                    if centercoord != None and topleft[0] != None and topleft[1] != None:
                        navigationsymbol_x = centercoord[0] - topleft[0]
                        navigationsymbol_y = centercoord[1] - topleft[1]
                        if navigationsymbol_x < 0:
                            navigationsymbol_x = 0
                        if navigationsymbol_y < 0:
                            navigationsymbol_y = 0
                    else:
                        navigationsymbol_y = 0
                        navigationsymbol_x = 0
                    
                    settings.CreateSettings("NavigationDetectionV2", "navsymbolx", navigationsymbol_x)
                    settings.CreateSettings("NavigationDetectionV2", "navsymboly", navigationsymbol_y)

                    screencap_display = settings.GetSettings("dxcam", "display")
                    if screencap_display == None:
                        settings.CreateSettings("dxcam", "display", 0)
                        screencap_display = 0
                    screencap_device = settings.GetSettings("dxcam", "device")
                    if screencap_device == None:
                        settings.CreateSettings("dxcam", "device", 0)
                        screencap_device = 0

                cv2.destroyWindow('Setup')
                cv2.destroyWindow('Example Image')

                if enabled_plugins != settings.GetSettings("Plugins", "Enabled"):
                    
                    for i in range(len(enabled_plugins)):
                        if enabled_plugins[i] != "NavigationDetection" and enabled_plugins[i] != "DXCamScreenCapture":
                            if enabled_plugins[i] not in settings.GetSettings("Plugins", "Enabled"):
                                settings.AddToList("Plugins", "Enabled", enabled_plugins[i])

                DefaultSteering.enabled = True
                variables.UPDATEPLUGINS = True
                variables.ENABLELOOP = False
                mainUI.update(data)
                setupmode = False
                LoadSettingsV3()

        if setupmode == False:
            current_time = time.time()
            
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
                gamepaused = data["api"]["pause"]
                if gamepaused == True:
                    speed = 0
                else:
                    speed = round(data["api"]["truckFloat"]["speed"]*3.6, 2)
            except:
                gamepaused = False
                speed = 0

            try:
                fuel_total = data["api"]["configFloat"]["fuelCapacity"]
                fuel_current = data["api"]["truckFloat"]["fuel"]
                if fuel_total != 0:
                    fuel_percentage = (fuel_current/fuel_total)*100
                else:
                    fuel_percentage = 100
            except:
                fuel_total = 0
                fuel_current = 0
                fuel_percentage = 100

            try:
                indicator_left = data["api"]["truckBool"]["blinkerLeftActive"]
                indicator_right = data["api"]["truckBool"]["blinkerRightActive"]
            except:
                indicator_left = False
                indicator_right = False

            if trafficlightdetection_is_enabled == True:
                try:
                    trafficlight = data["TrafficLightDetection"]["simple"]
                except:
                    trafficlightdetection_is_enabled = False
                    trafficlight = "Off"
            else:
                trafficlight = "Off"

            f5_key_state = ctypes.windll.user32.GetAsyncKeyState(0x74)
            f5_pressed = f5_key_state & 0x8000 != 0
            if f5_pressed == True:
                check_zoom_timer = current_time
            if current_time - 1 < check_zoom_timer or check_zoom_timer == 0:
                check_zoom = True
            else:
                check_zoom = False
            if check_zoom == True or check_zoom_timer == 0:
                lower_blue = np.array([121, 68, 0])
                upper_blue = np.array([250, 184, 109])
                mask_blue = cv2.inRange(frame, lower_blue, upper_blue)
                y, x = np.ogrid[:mask_blue.shape[0], :mask_blue.shape[1]]
                mask_circle = (x - navigationsymbol_x)**2 + (y - navigationsymbol_y)**2 <= round(width/10)**2
                mask_blue = np.where(mask_circle, mask_blue, 0)
                if width != 0 and height != 0:
                    pixel_ratio = cv2.countNonZero(mask_blue) / (width * height)
                else:
                    pixel_ratio = 0
                if pixel_ratio > 0.007 and pixel_ratio < 0.01:
                    do_zoom = False
                else:
                    do_zoom = True
                if pixel_ratio < 0.001:
                    do_blocked = True
                else:
                    do_blocked = False
                if check_zoom_timer == 0:
                    check_zoom_timer = current_time
            
            if mod != "1":
                lower_red = np.array([0, 0, 160])
                upper_red = np.array([110, 110, 255])
                lower_green = np.array([0, 200, 0])
                upper_green = np.array([230, 255, 150])
                white_limit = 1

                mask_red = cv2.inRange(frame, lower_red, upper_red)
                mask_green = cv2.inRange(frame, lower_green, upper_green)

                frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
            else:
                lower_red = np.array([7, 7, 202])
                upper_red = np.array([17, 17, 212])
                white_limit = 1

                mask_red = cv2.inRange(frame, lower_red, upper_red)

                frame_red_green = cv2.bitwise_and(frame, frame, mask=mask_red)

            cv2.rectangle(frame_red_green, (0,0), (round(width/6),round(height/3)),(0,0,0),-1)
            cv2.rectangle(frame_red_green, (width,0), (round(width-width/6),round(height/3)),(0,0,0),-1)

            frame_gray = cv2.cvtColor(frame_red_green, cv2.COLOR_BGR2GRAY)
            frame_gray_unblurred = frame_gray.copy()

            frame_gray = cv2.GaussianBlur(frame_gray,(3,3),0)

            frame = cv2.cvtColor(frame_gray_unblurred, cv2.COLOR_BGR2RGB)
            
            y_coordinate_of_lane = round(navigationsymbol_y / 1.4)
            y_coordinate_of_turn = round(navigationsymbol_y / 4) 
            automatic_x_offset = round(width/2-navigationsymbol_y)

            def GetArrayOfLaneEdges(y_coordinate_of_detection, tilt, x_offset, y_offset):
                detectingLane = False
                laneEdges = []

                for x in range(0, int(width)):
                    
                    y = round(y_coordinate_of_detection + y_offset + (navigationsymbol_x - x + x_offset) * tilt)
                    if y < 0:
                        y = 0
                    if y > height - 1:
                        y = height - 1

                    pixel = frame_gray[y, x]
                    if (white_limit <= pixel):
                        
                        if not detectingLane:
                            detectingLane = True
                            laneEdges.append(x - x_offset)
                    else:
                        if detectingLane:
                            detectingLane = False
                            laneEdges.append(x - x_offset)

                if len(laneEdges) < 2:
                    laneEdges.append(width)

                return laneEdges
            
            
            if turnincoming_direction != None:
                if turnincoming_direction == "Left":
                    tilt = 0.25
                else:
                    tilt = -0.25
            else:
                tilt = 0
            x_offset = lanechanging_final_offset - v3_offset
            y_offset = detection_offset_lane_y
            lanes = GetArrayOfLaneEdges(y_coordinate_of_lane, tilt, x_offset, y_offset)
            try:
                closest_x_pair = min([(left_x, right_x) for left_x, right_x in zip(lanes[::2], lanes[1::2])], key=lambda pair: abs((pair[0] + pair[1]) / 2 - navigationsymbol_x))
                left_x_lane, right_x_lane = closest_x_pair
            except:
                if lefthand_traffic == False:
                    left_x_lane = lanes[len(lanes)-2]
                    right_x_lane = lanes[len(lanes)-1]
                else:
                    try:
                        left_x_lane = lanes[len(lanes)-4]
                        right_x_lane = lanes[len(lanes)-3]
                    except:
                        left_x_lane = lanes[len(lanes)-2]
                        right_x_lane = lanes[len(lanes)-1]
            
            left_y_lane = round(y_coordinate_of_lane + detection_offset_lane_y + (navigationsymbol_x - left_x_lane - x_offset) * tilt)
            right_y_lane = round(y_coordinate_of_lane + detection_offset_lane_y + (navigationsymbol_x - right_x_lane - x_offset) * tilt)

            tilt = 0
            x_offset = lanechanging_final_offset - v3_offset
            y_offset = 0
            lanes = GetArrayOfLaneEdges(y_coordinate_of_turn, tilt, x_offset, y_offset)
            try:
                closest_x_pair = min([(left_x, right_x) for left_x, right_x in zip(lanes[::2], lanes[1::2])], key=lambda pair: abs((pair[0] + pair[1]) / 2 - navigationsymbol_x))
                left_x_turn, right_x_turn = closest_x_pair
            except:
                if lefthand_traffic == False:
                    left_x_turn = lanes[len(lanes)-2]
                    right_x_turn = lanes[len(lanes)-1]
                else:
                    try:
                        left_x_turn = lanes[len(lanes)-4]
                        right_x_turn = lanes[len(lanes)-3]
                    except:
                        left_x_turn = lanes[len(lanes)-2]
                        right_x_turn = lanes[len(lanes)-1]

            if left_x_lane + lanechanging_final_offset == width:
                left_x_lane = 0
                left_y_lane = 0
                right_x_lane = 0
                right_y_lane = 0
            if left_x_turn + lanechanging_final_offset == width:
                left_x_turn = 0
                right_x_turn = 0

            width_lane = right_x_lane - left_x_lane
            width_turn = right_x_turn - left_x_turn

            center_x_lane = (left_x_lane + right_x_lane) / 2
            center_x_turn = (left_x_turn + right_x_turn) / 2

            approve_x_left = round(navigationsymbol_x - width/4)
            if approve_x_left >= width:
                approve_x_left = width - 1
            if approve_x_left < 0:
                approve_x_left = 0
            approve_upper_y_left = 0
            approve_lower_y_left = 0
            for y in range(height-1, -1, -1):
                pixel = frame_gray[y, approve_x_left]
                if (white_limit <= pixel):
                    if approve_upper_y_left == 0:
                        approve_upper_y_left = y
                        approve_lower_y_left = y
                    else:
                        approve_lower_y_left = y
                else:
                    if approve_upper_y_left != 0:
                        break

            approve_x_right = round(navigationsymbol_x + width/4)
            if approve_x_right >= width:
                approve_x_right = width - 1
            if approve_x_right < 0:
                approve_x_right = 0
            approve_upper_y_right = 0
            approve_lower_y_right = 0
            for y in range(height-1, -1, -1):
                pixel = frame_gray[y, approve_x_right]
                if (white_limit <= pixel):
                    if approve_upper_y_right == 0:
                        approve_upper_y_right = y
                        approve_lower_y_right = y
                    else:
                        approve_lower_y_right = y
                else:
                    if approve_upper_y_right != 0:
                        break
            
            if approve_lower_y_left != 0 and approve_lower_y_right != 0:
                current_color = (0, 0, 255)
            else:
                current_color = (0, 255, 0)
            if approve_lower_y_left != 0:
                cv2.line(frame, (approve_x_left, approve_upper_y_left), (approve_x_left, approve_lower_y_left), current_color, 2)
            if approve_lower_y_right != 0:
                cv2.line(frame, (approve_x_right, approve_upper_y_right), (approve_x_right, approve_lower_y_right), current_color, 2)

            if approve_upper_y_left != 0 and approve_upper_y_right != 0:
                if approve_lower_y_left + round((approve_lower_y_left - approve_upper_y_left) / 2) <= y_coordinate_of_lane <= approve_upper_y_left - round((approve_lower_y_left - approve_upper_y_left) / 2) or approve_lower_y_right + round((approve_lower_y_right - approve_upper_y_right) / 2) <= y_coordinate_of_lane <= approve_upper_y_right - round((approve_lower_y_right - approve_upper_y_right) / 2):
                    if approve_lower_y_left < approve_lower_y_right:
                        distance = round((approve_lower_y_left + approve_lower_y_right) / 2 + (approve_lower_y_left - approve_upper_y_left) / 2) - y_coordinate_of_lane
                    else:
                        distance = round((approve_lower_y_left + approve_lower_y_right) / 2 + (approve_lower_y_right - approve_upper_y_right) / 2) - y_coordinate_of_lane
                    if distance < 0:
                        detection_offset_lane_y = distance
                    else:
                        detection_offset_lane_y = 0
                else:
                    detection_offset_lane_y = 0
            else:
                detection_offset_lane_y = 0

            if width_turn == 0:
                if approve_upper_y_left != 0:
                    turnincoming_detected = True
                    turnincoming_direction = "Left"
                if approve_upper_y_right != 0:
                    turnincoming_detected = True
                    turnincoming_direction = "Right"
            else:
                turnincoming_detected = False
                turnincoming_direction = None

            if approve_upper_y_left != 0 and approve_upper_y_right != 0:
                turnincoming_detected = False
                turnincoming_direction = None

            if approve_upper_y_left == 0 and approve_upper_y_right == 0:
                turnincoming_detected = False
                turnincoming_direction = None

            if turnincoming_detected == True:
                turnincoming_last_detected = current_time
                if lanechanging_autolanezero == True:
                    lanechanging_current_lane = 0
            
            if DefaultSteering.enabled == True:
                enabled = True
            else:
                enabled = False
            try:
                data["sdk"]
            except:
                data["sdk"] = {}
            indicator_changed_by_code = False
            if indicator_left != indicator_last_left:
                indicator_left_wait_for_response = False
            if indicator_right != indicator_last_right:
                indicator_right_wait_for_response = False
            if current_time - 1 > indicator_left_response_timer:
                indicator_left_wait_for_response = False
            if current_time - 1 > indicator_right_response_timer:
                indicator_right_wait_for_response = False
            if turnincoming_direction == "Left" and indicator_left == False and indicator_left_wait_for_response == False and enabled == True:
                data["sdk"]["LeftBlinker"] = True
                indicator_left_wait_for_response = True
                indicator_left_response_timer = current_time
            if turnincoming_direction == "Right" and indicator_right == False and indicator_right_wait_for_response == False and enabled == True:
                data["sdk"]["RightBlinker"] = True
                indicator_right_wait_for_response = True
                indicator_right_response_timer = current_time
            if turnincoming_direction == None and indicator_left == True and indicator_left_wait_for_response == False and current_time - 2 > turnincoming_last_detected and indicator_changed_by_code == True and enabled == True:
                data["sdk"]["LeftBlinker"] = True
                indicator_left_wait_for_response = True
                indicator_left_response_timer = current_time
            if turnincoming_direction == None and indicator_right == True and indicator_right_wait_for_response == False and current_time - 2 > turnincoming_last_detected and indicator_changed_by_code == True and enabled == True:
                data["sdk"]["RightBlinker"] = True
                indicator_right_wait_for_response = True
                indicator_right_response_timer = current_time
            if turnincoming_detected == True:
                indicator_changed_by_code = True
            else:
                indicator_changed_by_code = False

            if controls.GetKeybindFromName("Lane change to the left")['buttonIndex'] != -1:
                controls_left_set = True
                controls_left = controls.GetKeybindValue("Lane change to the left")
            else:
                controls_left_set = False
                controls_left = False
            if controls.GetKeybindFromName("Lane change to the right")['buttonIndex'] != -1:
                controls_right_set = True
                controls_right = controls.GetKeybindValue("Lane change to the right")
            else:
                controls_right_set = False
                controls_right = False

            if controls_left_set == False:
                if indicator_left != indicator_last_left and indicator_left == True and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                    lanechanging_current_lane += 1
            else:
                if controls_left == True and controls_last_left == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                    if indicator_left == True:
                        lanechanging_current_lane += 1
                    elif indicator_left == False and indicator_right_wait_for_response == False:
                        lanechanging_current_lane += 1
                        indicator_enable_left = True
            if controls_right_set == False:
                if indicator_right != indicator_last_right and indicator_right == True and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                    lanechanging_current_lane -= 1
            else:
                if controls_right == True and controls_last_right == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                    if indicator_right == True:
                        lanechanging_current_lane -= 1
                    elif indicator_right == False and indicator_left_wait_for_response == False:
                        lanechanging_current_lane -= 1
                        indicator_enable_right = True

            if indicator_enable_left == True and indicator_left == False and indicator_left_wait_for_response == False and enabled == True:
                data["sdk"]["LeftBlinker"] = True
                indicator_changed_by_code = True
                indicator_left_wait_for_response = True
                indicator_left_response_timer = current_time
            elif indicator_left == True and indicator_left_wait_for_response == False:
                indicator_enable_left = False
            if indicator_enable_right == True and indicator_right == False and indicator_right_wait_for_response == False and enabled == True:
                data["sdk"]["RightBlinker"] = True
                indicator_changed_by_code = True
                indicator_right_wait_for_response = True
                indicator_right_response_timer = current_time
            elif indicator_right == True and indicator_right_wait_for_response == False:
                indicator_enable_right = False

            lanechanging_target_offset = lanechanging_width * lanechanging_current_lane
            lanechanging_current_correction = lanechanging_target_offset - lanechanging_final_offset
            if abs(lanechanging_current_correction) > lanechanging_speed/10:
                if lanechanging_current_correction > 0:
                    lanechanging_current_correction = lanechanging_speed/10
                else:
                    lanechanging_current_correction = -lanechanging_speed/10
            lanechanging_final_offset += lanechanging_current_correction
            lanechanging_progress = lanechanging_final_offset/lanechanging_width
            
            if lanechanging_progress == lanechanging_current_lane and indicator_left == True and indicator_left_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_left_set == False:
                data["sdk"]["LeftBlinker"] = True
                indicator_left_wait_for_response = True
                indicator_left_response_timer = current_time
            elif lanechanging_progress == lanechanging_current_lane and indicator_left == True and indicator_left_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_left_set == True:
                data["sdk"]["LeftBlinker"] = True
                indicator_left_wait_for_response = True
                indicator_left_response_timer = current_time

            if lanechanging_progress == lanechanging_current_lane and indicator_right == True and indicator_right_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_right_set == False:
                data["sdk"]["RightBlinker"] = True
                indicator_right_wait_for_response = True
                indicator_right_response_timer = current_time
            elif lanechanging_progress == lanechanging_current_lane and indicator_right == True and indicator_right_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_right_set == True:
                data["sdk"]["RightBlinker"] = True
                indicator_right_wait_for_response = True
                indicator_right_response_timer = current_time

            if width_lane != 0:
                if turnincoming_detected == False:
                    correction = navigationsymbol_x - center_x_lane
                else:
                    if turnincoming_direction == "Left":
                        correction = navigationsymbol_x - center_x_lane - width_lane/40
                    else:
                        correction = navigationsymbol_x - center_x_lane + width_lane/40
            else:
                correction = 0
                if turnincoming_direction == "Left" and enabled == True:
                    data["sdk"]["LeftBlinker"] = False
                if turnincoming_direction == "Right" and enabled == True:
                    data["sdk"]["RightBlinker"] = False
                turnincoming_detected = False
                tunincoming_direction = None
            
            if topleft == None or bottomright == None or centercoord == None:
                if allow_playsound == True:
                    sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
                    allow_playsound = False
                    allow_playsound_timer = current_time
                frame = cv2.GaussianBlur(frame, (9, 9), 0)
                frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

                xofinfo = round(width/2)
                yofinfo = round(height/3.5)
                sizeofinfo = round(height/5)
                infothickness = round(height/50)
                cv2.circle(frame, (xofinfo,yofinfo), sizeofinfo, (0,127,255), infothickness, cv2.LINE_AA)
                cv2.line(frame, (xofinfo,round(yofinfo+sizeofinfo/2)), (xofinfo,round(yofinfo-sizeofinfo/10)), (0,127,255), infothickness*2, cv2.LINE_AA)
                cv2.circle(frame, (xofinfo,round(yofinfo-sizeofinfo/2)), round(infothickness*1.3), (0,127,255), -1, cv2.LINE_AA)

                sizeoftext = round(height/200)
                textthickness = round(height/100)
                text_size, _ = cv2.getTextSize("Do the", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
                text_width, text_height = text_size
                cv2.putText(frame, "Do the", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)
                text_size, _ = cv2.getTextSize("Setup", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
                text_width, text_height = text_size
                cv2.putText(frame, "Setup", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height*2.4)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)

                allow_trafficlight_symbol = False
                allow_no_lane_detected = False
                allow_do_blocked = False
                allow_do_zoom = False
                show_turn_line = False
            else:
                allow_trafficlight_symbol = True
                allow_no_lane_detected = True
                allow_do_blocked = True
                allow_do_zoom = True
                show_turn_line = True

            if do_blocked == True and allow_do_blocked == True:
                if allow_playsound == True:
                    sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
                    allow_playsound = False
                    allow_playsound_timer = current_time
                frame = cv2.GaussianBlur(frame, (9, 9), 0)
                frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

                xofinfo = round(width/2)
                yofinfo = round(height/3.5)
                sizeofinfo = round(height/5)
                infothickness = round(height/50)
                cv2.circle(frame, (xofinfo,yofinfo), sizeofinfo, (0,127,255), infothickness, cv2.LINE_AA)
                cv2.line(frame, (xofinfo,round(yofinfo+sizeofinfo/2)), (xofinfo,round(yofinfo-sizeofinfo/10)), (0,127,255), infothickness*2, cv2.LINE_AA)
                cv2.circle(frame, (xofinfo,round(yofinfo-sizeofinfo/2)), round(infothickness*1.3), (0,127,255), -1, cv2.LINE_AA)

                sizeoftext = round(height/200)
                textthickness = round(height/100)
                text_size, _ = cv2.getTextSize("Minimap vision", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
                text_width, text_height = text_size
                cv2.putText(frame, "Minimap vision", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)
                text_size, _ = cv2.getTextSize("blocked", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
                text_width, text_height = text_size
                cv2.putText(frame, "blocked", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height*2.4)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)

                correction = 0

                allow_trafficlight_symbol = False
                allow_no_lane_detected = False
                show_turn_line = False

            elif do_zoom == True and allow_do_zoom == True:
                if allow_playsound == True:
                    sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
                    allow_playsound = False
                    allow_playsound_timer = current_time
                frame = cv2.GaussianBlur(frame, (9, 9), 0)
                frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

                xofinfo = round(width/2)
                yofinfo = round(height/3.5)
                sizeofinfo = round(height/5)
                infothickness = round(height/50)
                cv2.circle(frame, (xofinfo,yofinfo), sizeofinfo, (0,127,255), infothickness, cv2.LINE_AA)
                cv2.line(frame, (xofinfo,round(yofinfo+sizeofinfo/2)), (xofinfo,round(yofinfo-sizeofinfo/10)), (0,127,255), infothickness*2, cv2.LINE_AA)
                cv2.circle(frame, (xofinfo,round(yofinfo-sizeofinfo/2)), round(infothickness*1.3), (0,127,255), -1, cv2.LINE_AA)

                sizeoftext = round(height/200)
                textthickness = round(height/100)
                text_size, _ = cv2.getTextSize("Zoom Minimap in", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
                text_width, text_height = text_size
                cv2.putText(frame, "Zoom Minimap in", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height*1.7)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)
                
                correction = 0

                allow_trafficlight_symbol = False
                allow_no_lane_detected = False
                show_turn_line = False
            else:
                allow_trafficlight_symbol = True
                allow_no_lane_detected = True
                show_turn_line = True

            if width_lane == 0 and allow_no_lane_detected == True:
                if allow_playsound == True:
                    sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
                    allow_playsound = False
                    allow_playsound_timer = current_time
                frame = cv2.GaussianBlur(frame, (9, 9), 0)
                frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

                xofinfo = round(width/2)
                yofinfo = round(height/3.5)
                sizeofinfo = round(height/5)
                infothickness = round(height/50)
                cv2.circle(frame, (xofinfo,yofinfo), sizeofinfo, (0,127,255), infothickness, cv2.LINE_AA)
                cv2.line(frame, (xofinfo,round(yofinfo+sizeofinfo/2)), (xofinfo,round(yofinfo-sizeofinfo/10)), (0,127,255), infothickness*2, cv2.LINE_AA)
                cv2.circle(frame, (xofinfo,round(yofinfo-sizeofinfo/2)), round(infothickness*1.3), (0,127,255), -1, cv2.LINE_AA)

                sizeoftext = round(height/200)
                textthickness = round(height/100)
                text_size, _ = cv2.getTextSize("No Lane", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
                text_width, text_height = text_size
                cv2.putText(frame, "No Lane", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)
                text_size, _ = cv2.getTextSize("Detected", cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, textthickness)
                text_width, text_height = text_size
                cv2.putText(frame, "Detected", (round(width/2-text_width/2), round(yofinfo+sizeofinfo*1.3+text_height*2.4)), cv2.FONT_HERSHEY_SIMPLEX, sizeoftext, (0,127,255), textthickness, cv2.LINE_AA)

                correction = 0

                allow_trafficlight_symbol = False
                show_turn_line = False
            else:
                if allow_no_lane_detected == True:
                    allow_trafficlight_symbol = True
                else:
                    allow_trafficlight_symbol = False
                show_turn_line = True

            showing_traffic_light_symbol = False
            if trafficlightdetection_is_enabled == True and allow_trafficlight_symbol == True:
                if trafficlight == "Red":
                    traffic_light_symbol = round(width/2), round(height/5), round(width/75)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
                    cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1] - traffic_light_symbol[2] * 2), traffic_light_symbol[2], (0, 0, 255), -1, cv2.LINE_AA)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 255), traffic_light_symbol[2])
                    showing_traffic_light_symbol = True
                if trafficlight == "Yellow":
                    traffic_light_symbol = round(width/2), round(height/5), round(width/75)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
                    cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1]), traffic_light_symbol[2], (0, 255, 255), -1, cv2.LINE_AA)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 255, 255), traffic_light_symbol[2])
                    showing_traffic_light_symbol = True
                if trafficlight == "Green":
                    traffic_light_symbol = round(width/2), round(height/5), round(width/75)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
                    cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1] + traffic_light_symbol[2] * 2), traffic_light_symbol[2], (0, 255, 0), -1, cv2.LINE_AA)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 255, 0), traffic_light_symbol[2])
                    showing_traffic_light_symbol = True
            
            if allow_trafficlight_symbol == True:
                if width_lane != 0:
                    cv2.line(frame, (round(left_x_lane + lanechanging_final_offset - v3_offset), left_y_lane), (round(right_x_lane + lanechanging_final_offset - v3_offset), right_y_lane),  (255, 255, 255), 2)
                if width_turn != 0 and showing_traffic_light_symbol == False and show_turn_line == True:
                    cv2.line(frame, (round(left_x_turn + lanechanging_final_offset - v3_offset), y_coordinate_of_turn), (round(right_x_turn + lanechanging_final_offset - v3_offset), y_coordinate_of_turn), (255, 255, 255), 2)
            
            if lanechanging_do_lane_changing == True or fuel_percentage < 15:
                current_text = "Enabled"
                width_target_current_text = width/4
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
                width_enabled_text, height_enabled_text = width_current_text, height_current_text

            if lanechanging_do_lane_changing == True:
                current_text = f"Lane: {lanechanging_current_lane}"
                width_target_current_text = width/4
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
                width_lane_text, height_lane_text = width_current_text, height_current_text
                thickness_current_text = round(fontscale_current_text*2)
                if thickness_current_text <= 0:
                    thickness_current_text = 1
                if turnincoming_detected == True:
                    current_color = (150, 150, 150)
                else:
                    current_color = (200, 200, 200)
                cv2.putText(frame, f"Lane: {lanechanging_current_lane}", (round(0.01*width), round(0.07*height+height_current_text+height_enabled_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_color, thickness_current_text)
            
            if fuel_percentage < 15:
                current_text = "Refuel!"
                width_target_current_text = width/4
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
                thickness_current_text = round(fontscale_current_text*2)
                if thickness_current_text <= 0:
                    thickness_current_text = 1
                if lanechanging_do_lane_changing == True:
                    cv2.putText(frame, current_text, (round(0.01*width), round(0.10*height+height_current_text+height_enabled_text+height_lane_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
                else:
                    cv2.putText(frame, current_text, (round(0.01*width), round(0.07*height+height_current_text+height_enabled_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
                
            if current_time - 1 > allow_playsound_timer and allow_trafficlight_symbol == True and allow_no_lane_detected == True and allow_do_zoom == True and show_turn_line == True:
                allow_playsound = True

            indicator_last_left = indicator_left
            indicator_last_right = indicator_right
            controls_last_left = controls_left
            controls_last_right = controls_right
            
            lanechanging_last_progress = lanechanging_progress

            if speed > 63:
                correction *= 63/speed

            if turnincoming_detected == False and width_turn != 0 and width_turn < width_lane:
                curve = (center_x_lane - center_x_turn)/30
            else:
                curve = correction/10
            if gamepaused == True:
                curve = 0

            if width_lane == 0:
                lane_detected = False
                check_zoom_timer = current_time
            else:
                lane_detected = True

            if speed > -0.5:
                data["LaneDetection"] = {}
                data["LaneDetection"]["difference"] = -correction/30
            else:
                data["LaneDetection"] = {}
                data["LaneDetection"]["difference"] = correction/30
            data["NavigationDetection"] = {}
            data["NavigationDetection"]["lanedetected"] = lane_detected
            data["NavigationDetection"]["turnincoming"] = turnincoming_detected
            data["NavigationDetection"]["curve"] = curve
            data["NavigationDetection"]["lane"] = lanechanging_current_lane
            data["NavigationDetection"]["laneoffsetpercent"] = lanechanging_progress

            
            data["frame"] = frame

############################################################################################################################
    
    if version == None:
        try:
            frame = data["frame"]
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]

            current_text = "No NavigationDetection"
            width_target_current_text = frame_width/1.2
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
            cv2.putText(frame, "No NavigationDetection", (round(frame_width/2 - frame_width/2.4), round(frame_height/3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
            cv2.putText(frame, "Version Selected!", (round(frame_width/2 - frame_width/3.2), round(frame_height/1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
        except:
            pass

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
            self.version_ui = ""
            self.mod_ui = ""
            self.exampleFunction()
            resizeWindow(950,665)        
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self
        
        def tabFocused(self): # Called when the tab is focused
            resizeWindow(950,665)

        def UpdateSettings(self):
            # V1:
            self.trim.set(self.trimSlider.get())
            self.laneX.set(self.laneXSlider.get())
            self.sca.set(self.scale.get())
            self.smoothness.set(self.smoothnessSlider.get())
            self.curveMultip.set(self.curveMultipSlider.get())
            self.turnstrength.set(self.turnstrengthSlider.get())
            
            settings.CreateSettings("NavigationDetectionV1", "trim", self.trimSlider.get())
            settings.CreateSettings("NavigationDetectionV1", "laneXOffset", self.laneXSlider.get())
            settings.CreateSettings("NavigationDetectionV1", "scale", self.scale.get())
            settings.CreateSettings("NavigationDetectionV1", "smoothness", self.smoothnessSlider.get())
            settings.CreateSettings("NavigationDetectionV1", "CurveMultiplier", self.curveMultipSlider.get())
            settings.CreateSettings("NavigationDetectionV1", "TurnStrength", self.turnstrengthSlider.get())
            
            # V2:
            self.curvemultipv2.set(self.curvemultipv2Slider.get())
            self.sensitivityv2.set(self.sensitivityv2Slider.get())
            self.offsetv2.set(self.offsetv2Slider.get())
            self.textsizev2.set(self.textsizev2Slider.get())
            self.textdistancescalev2.set(self.textdistancescalev2Slider.get())
            
            settings.CreateSettings("NavigationDetectionV2", "curvemultip", self.curvemultipv2Slider.get())
            settings.CreateSettings("NavigationDetectionV2", "sensitivity", self.sensitivityv2Slider.get())
            settings.CreateSettings("NavigationDetectionV2", "offset", self.offsetv2Slider.get())
            settings.CreateSettings("NavigationDetectionV2", "textsize", self.textsizev2Slider.get())
            settings.CreateSettings("NavigationDetectionV2", "textdistancescale", self.textdistancescalev2Slider.get())

            # V3:
            self.offset.set(self.offsetSlider.get())

            settings.CreateSettings("NavigationDetectionV3", "offset", self.offsetSlider.get())

            LoadSettings()
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=950, height=665, border=0, highlightthickness=0)
            self.root.grid_propagate(1) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            v1Tab = ttk.Frame(notebook)
            v1Tab.pack()
            v2Tab = ttk.Frame(notebook)
            v2Tab.pack()
            v3Tab = ttk.Frame(notebook)
            v3Tab.pack()


            v3Notebook = ttk.Notebook(v3Tab)
            v3Notebook.grid_anchor("center")
            v3Notebook.grid()

            v3generalFrame = ttk.Frame(v3Notebook)
            v3generalFrame.pack()
            v3setupFrame = ttk.Frame(v3Notebook)
            v3setupFrame.pack()
            
            v3generalFrame.columnconfigure(0, weight=1)
            v3generalFrame.columnconfigure(1, weight=1)
            v3generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(v3generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            v3setupFrame.columnconfigure(0, weight=1)
            v3setupFrame.columnconfigure(1, weight=1)
            v3setupFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(v3setupFrame, "Setup", 0, 0, font=("Robot", 12, "bold"), columnspan=3)


            generalFrame.columnconfigure(0, weight=1)
            generalFrame.columnconfigure(1, weight=1)
            generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            v1Tab.columnconfigure(0, weight=1)
            v1Tab.columnconfigure(1, weight=1)
            v1Tab.columnconfigure(2, weight=1)
            helpers.MakeLabel(v1Tab, "NavigationDetectionV1", 0, 0, font=("Robot", 12, "bold"), columnspan=7)

            v2Tab.columnconfigure(0, weight=1)
            v2Tab.columnconfigure(1, weight=1)
            v2Tab.columnconfigure(2, weight=1)
            helpers.MakeLabel(v2Tab, "NavigationDetectionV2", 0, 0, font=("Robot", 12, "bold"), columnspan=3)
            
            v3Tab.columnconfigure(0, weight=1)
            v3Tab.columnconfigure(1, weight=1)
            v3Tab.columnconfigure(2, weight=1)
            helpers.MakeLabel(v3Tab, "NavigationDetectionV3", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            notebook.add(generalFrame, text=Translate("General"))
            notebook.add(v1Tab, text=Translate("NavigationDetectionV1"))
            notebook.add(v2Tab, text=Translate("NavigationDetectionV2"))
            notebook.add(v3Tab, text=Translate("NavigationDetectionV3"))

            v3Notebook.add(v3generalFrame, text=Translate("General"))
            v3Notebook.add(v3setupFrame, text=Translate("Setup"))
            
            ttk.Button(self.root, text="Save", command=self.save, width=15).pack(anchor="center", pady=6)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()

            LoadSettingsV1()
            LoadSettingsV2()
            LoadSettingsV3()
            
            ############################################################################################################################
            # UI
            ############################################################################################################################
            
            helpers.MakeLabel(generalFrame, "NavigationDetection Version:", 1, 1, font=("Segoe UI", 12))
            # version selector
            version_ui = tk.StringVar() 
            previous_version_ui = settings.GetSettings("NavigationDetection", "version", "NavigationDetectionV3")
            if previous_version_ui == "NavigationDetectionV1":
                version_ui.set("NavigationDetectionV1")
            if previous_version_ui == "NavigationDetectionV2":
                version_ui.set("NavigationDetectionV2")
            if previous_version_ui == "NavigationDetectionV3":
                version_ui.set("NavigationDetectionV3")
            def version_selection():
                self.version_ui = version_ui.get()
            v1_radio_button = ttk.Radiobutton(generalFrame, text="NavigationDetectionV1", variable=version_ui, value="NavigationDetectionV1", command=version_selection)
            v1_radio_button.grid(row=2, column=1)
            v2_radio_button = ttk.Radiobutton(generalFrame, text="NavigationDetectionV2", variable=version_ui, value="NavigationDetectionV2", command=version_selection)
            v2_radio_button.grid(row=3, column=1)
            v3_radio_button = ttk.Radiobutton(generalFrame, text="NavigationDetectionV3", variable=version_ui, value="NavigationDetectionV3", command=version_selection)
            v3_radio_button.grid(row=4, column=1)
            version_selection()

            helpers.MakeEmptyLine(generalFrame, 5, 1)

            helpers.MakeLabel(generalFrame, "CleanRouteAdvisor Mod:", 6, 1, font=("Segoe UI", 12))
            # mod selection
            mod_ui = tk.StringVar()
            previous_mod_ui = settings.GetSettings("NavigationDetection", "mod", "0")
            if previous_mod_ui == "1":
                mod_ui.set("1")
            if previous_mod_ui == "0":
                mod_ui.set("0")
            def mod_selection():
                self.mod_ui = mod_ui.get()
            mod_true_radio_button = ttk.Radiobutton(generalFrame, text="I use the CleanRouteAdvisor mod.", variable=mod_ui, value="1", command=mod_selection)
            mod_true_radio_button.grid(row=7, column=1)
            mod_false_radio_button = ttk.Radiobutton(generalFrame, text="I do not use the CleanRouteAdvisor mod / the mod does not work.", variable=mod_ui, value="0", command=mod_selection)
            mod_false_radio_button.grid(row=8, column=1)
            mod_selection()

            # V1 Tab
            self.trimSlider = tk.Scale(v1Tab, from_=-10, to=10, resolution=0.1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.trimSlider.set(settings.GetSettings("NavigationDetectionV1", "trim"))
            self.trimSlider.grid(row=2, column=3, padx=10, pady=0, columnspan=2)
            self.trim = helpers.MakeComboEntry(v1Tab, "Trim", "NavigationDetectionV1", "trim", 2,0, labelwidth=20)
            
            self.laneXSlider = tk.Scale(v1Tab, from_=1, to=400, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.laneXSlider.set(settings.GetSettings("NavigationDetectionV1", "laneXOffset"))
            self.laneXSlider.grid(row=3, column=3, padx=10, pady=0, columnspan=2)
            self.laneX = helpers.MakeComboEntry(v1Tab, "Navisymbol Offset", "NavigationDetectionV1", "laneXOffset", 3,0, labelwidth=20)

            self.scale = tk.Scale(v1Tab, from_=0.01, to=10, resolution=0.01, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.scale.set(settings.GetSettings("NavigationDetectionV1", "scale"))
            self.scale.grid(row=4, column=3, padx=10, pady=0, columnspan=2)
            self.sca = helpers.MakeComboEntry(v1Tab, "Scale", "NavigationDetectionV1", "scale", 4,0, labelwidth=20)

            self.smoothnessSlider = tk.Scale(v1Tab, from_=0, to=20, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.smoothnessSlider.set(settings.GetSettings("NavigationDetectionV1", "smoothness"))
            self.smoothnessSlider.grid(row=5, column=3, padx=10, pady=0, columnspan=2)
            self.smoothness = helpers.MakeComboEntry(v1Tab, "Smoothness", "NavigationDetectionV1", "smoothness", 5,0, labelwidth=20)
            
            self.curveMultipSlider = tk.Scale(v1Tab, from_=0, to=3, resolution=0.01, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.curveMultipSlider.set(settings.GetSettings("NavigationDetectionV1", "CurveMultiplier"))
            self.curveMultipSlider.grid(row=6, column=3, padx=10, pady=0, columnspan=2)
            self.curveMultip = helpers.MakeComboEntry(v1Tab, "Curve Multiplier", "NavigationDetectionV1", "CurveMultiplier", 6,0, labelwidth=20)

            self.turnstrengthSlider = tk.Scale(v1Tab, from_=1, to=100, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.turnstrengthSlider.set(settings.GetSettings("NavigationDetectionV1", "TurnStrength"))
            self.turnstrengthSlider.grid(row=7, column=3, padx=10, pady=0, columnspan=2)
            self.turnstrength = helpers.MakeComboEntry(v1Tab, "TurnStrength", "NavigationDetectionV1", "TurnStrength", 7,0, labelwidth=20)


            # V2 Tab
            self.curvemultipv2Slider = tk.Scale(v2Tab, from_=0.01, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=400, command=lambda x: self.UpdateSettings())
            self.curvemultipv2Slider.set(settings.GetSettings("NavigationDetectionV2", "curvemultip"))
            self.curvemultipv2Slider.grid(row=2, column=1, padx=10, pady=0, columnspan=2)
            self.curvemultipv2 = helpers.MakeComboEntry(v2Tab, "Curvemultip", "NavigationDetectionV2", "curvemultip", 2,0)
            
            self.sensitivityv2Slider = tk.Scale(v2Tab, from_=0.01, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=400, command=lambda x: self.UpdateSettings())
            self.sensitivityv2Slider.set(settings.GetSettings("NavigationDetectionV2", "sensitivity"))
            self.sensitivityv2Slider.grid(row=3, column=1, padx=10, pady=0, columnspan=2)
            self.sensitivityv2 = helpers.MakeComboEntry(v2Tab, "Sensitivity", "NavigationDetectionV2", "sensitivity", 3,0)

            self.offsetv2Slider = tk.Scale(v2Tab, from_=-20, to=20, resolution=0.1, orient=tk.HORIZONTAL, length=400, command=lambda x: self.UpdateSettings())
            self.offsetv2Slider.set(settings.GetSettings("NavigationDetectionV2", "offset"))
            self.offsetv2Slider.grid(row=4, column=1, padx=10, pady=0, columnspan=2)
            self.offsetv2 = helpers.MakeComboEntry(v2Tab, "Offset", "NavigationDetectionV2", "offset", 4,0)

            self.textsizev2Slider = tk.Scale(v2Tab, from_=0, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=400, command=lambda x: self.UpdateSettings())
            self.textsizev2Slider.set(settings.GetSettings("NavigationDetectionV2", "textsize"))
            self.textsizev2Slider.grid(row=5, column=1, padx=10, pady=0, columnspan=2)
            self.textsizev2 = helpers.MakeComboEntry(v2Tab, "Textsize", "NavigationDetectionV2", "textsize", 5,0)
            
            self.textdistancescalev2Slider = tk.Scale(v2Tab, from_=0.1, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=400, command=lambda x: self.UpdateSettings())
            self.textdistancescalev2Slider.set(settings.GetSettings("NavigationDetectionV2", "textdistancescale"))
            self.textdistancescalev2Slider.grid(row=6, column=1, padx=10, pady=0, columnspan=2)
            self.textdistancescalev2 = helpers.MakeComboEntry(v2Tab, "Textspacescale", "NavigationDetectionV2", "textdistancescale", 6,0)
            
            helpers.MakeCheckButton(v2Tab, "Lane Changing", "NavigationDetectionV2", "lanechanging", 11, 0, callback=lambda: LoadSettings())
            helpers.MakeLabel(v2Tab, "If activated, you can change the lane you are driving on using the indicators", 11, 1)
            self.lanechangingspeedv2 = helpers.MakeComboEntry(v2Tab, "Lane Changing Speed", "NavigationDetectionV2", "lanechangingspeed", 12, 0, labelwidth=20, isFloat=True)
            self.lanewidthv2 = helpers.MakeComboEntry(v2Tab, "Lane Width", "NavigationDetectionV2", "lanewidth", 13, 0, labelwidth=20, isFloat=True)
            helpers.MakeButton(v2Tab, "Save Lane Settings", self.save, 12, 2, pady=0, padx=0, width=16)

            def setnavcordstrue():
                global getnavcoordinates
                global disableshowimagelater
                getnavcoordinates = True
                if "ShowImage" not in settings.GetSettings("Plugins", "Enabled"):
                    disableshowimagelater = True
                    settings.AddToList("Plugins", "Enabled", "ShowImage")
                DefaultSteering.enabled = False
                variables.ENABLELOOP = True

            helpers.MakeButton(v2Tab, "Grab Coordinates", setnavcordstrue, 14, 2, pady=20, padx=5, width=16)

            helpers.MakeCheckButton(v2Tab, "Left-hand traffic", "NavigationDetectionV2", "leftsidetraffic", 14, 1, callback=lambda: LoadSettings())

            helpers.MakeCheckButton(v2Tab, "Automatic lane", "NavigationDetectionV2", "automaticlaneselection", 14, 0, callback=lambda: LoadSettings())
            

            # V3 Tab
            def v3setup():
                if variables.ENABLELOOP == False:
                    global setupmode
                    global enabled_plugins
                    global setupframe
                    global topleft
                    global bottomright
                    global centercoord
                    screenshot = pyautogui.screenshot()
                    setupframe = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    frame_width = setupframe.shape[1]
                    frame_height = setupframe.shape[0]
                    settings.CreateSettings("NavigationDetection", "version", "NavigationDetectionV3")
                    version_ui.set("NavigationDetectionV3")
                    version_selection()
                    self.save()

                    LoadSettingsV3()

                    # Code below by Tumppi066
                    minimapDistanceFromRight = 27
                    minimapDistanceFromBottom = 134
                    minimapWidth = 560
                    minimapHeight = 293
                    scale = frame_height/1440
                    if topleft == None:
                        xCoord = frame_width - (minimapDistanceFromRight * scale + minimapWidth * scale)
                        yCoord = frame_height - (minimapDistanceFromBottom * scale + minimapHeight * scale)
                        topleft = (int(xCoord), int(yCoord))
                        settings.CreateSettings("NavigationDetectionV3", "topleft", topleft)
                    if bottomright == None:
                        xCoord = frame_width - (minimapDistanceFromRight * scale)
                        yCoord = frame_height - (minimapDistanceFromBottom * scale)
                        bottomright = (int(xCoord), int(yCoord))
                        settings.CreateSettings("NavigationDetectionV3", "bottomright", bottomright)
                    if centercoord == None:
                        centercoord = round(topleft[0] + (bottomright[0] - topleft[0]) / 2), round(topleft[1] + (bottomright[1] - topleft[1]) / 1.85)
                        settings.CreateSettings("NavigationDetectionV3", "centercoord", centercoord)
                    #
                    LoadSettingsV3()
                    setupmode = True
                    cv2.namedWindow('Setup', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('Setup', round(frame_width/2), round(frame_height/2))
                    startframe = np.zeros((round(frame_height/2), round(frame_width/2), 3))
                    cv2.putText(startframe, "waiting...", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA) 
                    cv2.imshow('Setup', startframe)

                    enabled_plugins = settings.GetSettings("Plugins", "Enabled")
                    if "NavigationDetection" not in enabled_plugins:
                        settings.AddToList("Plugins", "Enabled", "NavigationDetection")
                    if "DXCamScreenCapture" not in enabled_plugins:
                        settings.AddToList("Plugins", "Enabled", "DXCamScreenCapture")
                    for i in range(len(enabled_plugins)):
                        if enabled_plugins[i] != "NavigationDetection" and enabled_plugins[i] != "DXCamScreenCapture":
                            settings.RemoveFromList("Plugins", "Enabled", enabled_plugins[i])

                    DefaultSteering.enabled = False
                    variables.UPDATEPLUGINS = True
                    variables.ENABLELOOP = True
                else:
                    messagebox.showwarning(title="NavigationDetection Setup", message="Disable the app before entering setup mode.")

            helpers.MakeLabel(v3setupFrame, 'You need to do this setup before you can use the NavigationDetectionV3.\nPlease make sure that the mimimap from the game is visible on your screen\nand on the cloesest zoom level before you enter the setup mode.\n‎\nIf you press the button below, a window should come up and you should do the following things:\n‎\nPress on the "Get Top Left Coordinate" and then you can select the top left corner of the\nscreencapture by a left click with your mouse on the top left corner of the minimap.\n(look example image window, it opens when you enter the setup mode)\n‎\nPress on the "Get Bottom Right Coordinate" and then you can select the bottom right corner of the\nscreencapture by a left click with your mouse on the bottom right corner of the minimap.\n(look example image window, it opens when you enter the setup mode)\n‎\nPress on the "Get Center Coordinate" and then you can select the position of the blue navigation\narrow symbol from the games minimap. So you should place the orange circle over the hole in the\nblue navigation arrow symbol.\n(look example image window, it opens when you enter the setup mode)\n‎\n‎\n‎\n‎\n‎', 2, 0, sticky="nw")
            helpers.MakeButton(v3setupFrame, "Start Setup", v3setup, 14, 0, pady=0, padx=0, width=500)

            self.offsetSlider = tk.Scale(v3generalFrame, from_=-20, to=20, resolution=0.1, orient=tk.HORIZONTAL, length=510, command=lambda x: self.UpdateSettings())
            self.offsetSlider.set(settings.GetSettings("NavigationDetectionV3", "offset"))
            self.offsetSlider.grid(row=3, column=0, padx=10, pady=0, columnspan=2)
            self.offset = helpers.MakeComboEntry(v3generalFrame, "Offset", "NavigationDetectionV3", "offset", 3, 0, labelwidth=10, width=15, isFloat=True)
            helpers.MakeCheckButton(v3generalFrame, "Left-hand traffic\n----------------------\nEnable this if you are driving in a country with left-hand traffic.", "NavigationDetectionV3", "lefthand_traffic", 4, 0, width=90, callback=lambda: LoadSettings())
            helpers.MakeCheckButton(v3generalFrame, "Lane Changing\n---------------------\nIf enabled, you can change the lane you are driving on using the games indicators.\nTo change the values in the input boxex below, disable the app.", "NavigationDetectionV3", "lanechanging_do_lane_changing", 5, 0, width=90, callback=lambda: LoadSettings())
            helpers.MakeEmptyLine(v3generalFrame, 6, 0)
            self.lanechanging_speed = helpers.MakeComboEntry(v3generalFrame, "Lane Changing Speed\n--------------------------------\nThis sets how fast the truck changes the lane.\n‎", "NavigationDetectionV3", "lanechanging_speed", 6, 0, labelwidth=90, width=15, isFloat=True)
            self.lanechanging_width = helpers.MakeComboEntry(v3generalFrame, "Lane Width\n-----------------\nThis sets how much the truck needs to go left or right to change the lane.\n‎", "NavigationDetectionV3", "lanechanging_width", 7, 0, labelwidth=90, width=15, isFloat=True)
            helpers.MakeCheckButton(v3generalFrame, "Automatically change to lane 0 if a turn got detected and lane changing is enabled.\nNote: You wont be able to change lanes when a turn is detected.", "NavigationDetectionV3", "lanechanging_autolanezero", 8, 0, width=90, callback=lambda: LoadSettings())
            helpers.MakeLabel(v3generalFrame, "If you set the buttons for changing lanes in the controls menu, you can no longer change lanes\nusing the indicators. Remove the buttons from the controls menu if you want to use the indicators\nfor lane changing.", 9, 0, sticky="nw")

        def save(self):
            
            # V2:
            settings.CreateSettings("NavigationDetectionV2", "lanechangingspeed", float(self.lanechangingspeedv2.get()))
            settings.CreateSettings("NavigationDetectionV2", "lanewidth", float(self.lanewidthv2.get()))
            
            # V3:
            settings.CreateSettings("NavigationDetectionV3", "lanechanging_speed", float(self.lanechanging_speed.get()))
            settings.CreateSettings("NavigationDetectionV3", "lanechanging_width", float(self.lanechanging_width.get()))

            settings.CreateSettings("NavigationDetection", "version", self.version_ui)
            version = settings.GetSettings("NavigationDetection", "version", "NavigationDetectionV3")
            if version == "NavigationDetectionV1":         
                LoadSettingsV1()
            if version == "NavigationDetectionV2":              
                LoadSettingsV2()
            if version == "NavigationDetectionV3":
                LoadSettingsV3()
                
            settings.CreateSettings("NavigationDetection", "mod", self.mod_ui)
            LoadSettings()
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)