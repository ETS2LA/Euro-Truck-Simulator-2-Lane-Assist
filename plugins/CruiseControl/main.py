"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import switchSelectedPlugin, resizeWindow

PluginInfo = PluginInformation(
    name="CruiseControl", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="This Plugin automatically sets your cruise control speed,\nusing the SDKController.",
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
import src.controls as controls
from src.translator import Translate
from tkinter import messagebox
import os

import plugins.DefaultSteering.main as DefaultSteering
import time
import cv2
import numpy as np
import ctypes

controls.RegisterKeybind("Pause/Resume Automatic Acceleration",
                         notBoundInfo="Bind this if you use the CruiseControl\nplugin with automatic acceleration.",
                         description="Bind this if you use the CruiseControl\nplugin with automatic acceleration.")

def UpdateSettings():
    global trafficlightdetectionisenabled
    global navigationdetectionisenabled
    global map_topleft
    global map_bottomright
    global arrow_topleft
    global arrow_bottomright
    global arrow_percentage
    global navigationsymbol_x
    global navigationsymbol_y
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
    global auto_stop
    global show_symbols
    global acceleration_strength
    global brake_strength
    global cruisespeed_turn
    global cruisespeed_trafficlight
    global wait_for_response
    global wait_for_response_timer
    global last_hazard_light
    global wait_for_response_hazard_light
    global wait_for_response_hazard_light_timer
    global park_brake_target
    global last_park_brake
    global wait_for_response_park_brake
    global wait_for_response_park_brake_timer
    global last_speed
    global last_speedlimit
    global last_cruisecontrolspeed
    global trafficlight_last_time_without
    global trafficlight_last_time_with
    global turnincoming_last_time_with
    global trafficlight_allow_acceleration
    global user_emergency_braking
    global user_emergency_braking_timer
    global lanedetected_timer
    global do_lanedetected_stop
    global last_do_lanedetected_stop
    global last_lanedetected
    global allow_acceleration
    global pauseresume_allow
    global last_park_brake
    
    if "TrafficLightDetection" in settings.GetSettings("Plugins", "Enabled", []):
        trafficlightdetectionisenabled = True
    else:
        trafficlightdetectionisenabled = False

    if "NavigationDetection" in settings.GetSettings("Plugins", "Enabled", []):
        navigationdetectionisenabled = True
        map_topleft = settings.GetSettings("NavigationDetection", "map_topleft", "unset")
        map_bottomright = settings.GetSettings("NavigationDetection", "map_bottomright", "unset")
        arrow_topleft = settings.GetSettings("NavigationDetection", "arrow_topleft", "unset")
        arrow_bottomright = settings.GetSettings("NavigationDetection", "arrow_bottomright", "unset")
        arrow_percentage = settings.GetSettings("NavigationDetection", "arrow_percentage", "unset")

        if map_topleft == "unset":
            map_topleft = None
        if map_bottomright == "unset":
            map_bottomright = None
        if arrow_topleft == "unset":
            arrow_topleft = None
        if arrow_bottomright == "unset":
            arrow_bottomright = None
        if arrow_percentage == "unset":
            arrow_percentage = None
        
        if arrow_topleft != None and arrow_bottomright != None and map_topleft != None and map_bottomright != None:
            navigationsymbol_x = round((arrow_topleft[0] + arrow_bottomright[0]) / 2 - map_topleft[0])
            navigationsymbol_y = round((arrow_topleft[1] + arrow_bottomright[1]) / 2 - map_topleft[1])
        else:
            navigationsymbol_x = 0
            navigationsymbol_y = 0
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
    auto_stop = settings.GetSettings("CruiseControl", "auto_stop", False)
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
    wait_for_response_hazard_light = False
    wait_for_response_hazard_light_timer = 0

    park_brake_target = False
    last_park_brake = False
    wait_for_response_park_brake = False
    wait_for_response_park_brake_timer = 0

    last_speed = 0
    last_speedlimit = 0
    last_cruisecontrolspeed = 0
    trafficlight_last_time_without = 0
    trafficlight_last_time_with = 0
    turnincoming_last_time_with = 0

    trafficlight_allow_acceleration = False
    user_emergency_braking = False
    user_emergency_braking_timer = 0
    lanedetected_timer = 0
    do_lanedetected_stop = False
    last_do_lanedetected_stop = False
    last_lanedetected = False
    allow_acceleration = True
    pauseresume_allow = True

def plugin(data):
    global trafficlightdetectionisenabled
    global navigationdetectionisenabled
    global map_topleft
    global map_bottomright
    global arrow_topleft
    global arrow_bottomright
    global arrow_percentage
    global navigationsymbol_x
    global navigationsymbol_y
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
    global auto_stop
    global show_symbols
    global acceleration_strength
    global brake_strength
    global cruisespeed_turn
    global cruisespeed_trafficlight
    global wait_for_response
    global wait_for_response_timer
    global last_hazard_light
    global wait_for_response_hazard_light
    global wait_for_response_hazard_light_timer
    global park_brake_target
    global last_park_brake
    global wait_for_response_park_brake
    global wait_for_response_park_brake_timer
    global last_speed
    global last_speedlimit
    global last_cruisecontrolspeed
    global trafficlight_last_time_without
    global trafficlight_last_time_with
    global turnincoming_last_time_with
    global trafficlight_allow_acceleration
    global user_emergency_braking
    global user_emergency_braking_timer
    global lanedetected_timer
    global do_lanedetected_stop
    global last_do_lanedetected_stop
    global last_lanedetected
    global allow_acceleration
    global pauseresume_allow
    global last_park_brake

    current_time = time.time()
    park_brake_target = False

    try:
        speed = round(data["api"]["truckFloat"]["speed"]*3.6, 1)
        last_speed = speed
        speedlimit = round(data["api"]["truckFloat"]["speedLimit"]*3.6, -1)
        if speedlimit != 0 and speedlimit > 0:
            last_speedlimit = speedlimit
        cruisecontrolspeed = round(data["api"]["truckFloat"]["cruiseControlSpeed"]*3.6, 1)
        if data["api"]["truckFloat"]["userThrottle"] > 0.1:
            user_accelerating = True
        else:
            user_accelerating = False
        user_throttle = data["api"]["truckFloat"]["userThrottle"]
        if data["api"]["truckFloat"]["userBrake"] > 0.1:
            user_braking = True
        else:
            user_braking = False
        if speed >= 0.5 and speed > last_speed:
            user_emergency_braking = False
        if user_accelerating == True:
            user_emergency_braking = False
        if data["api"]["truckFloat"]["userBrake"] > 0.9 and speed > 30 and DefaultSteering.enabled == True:
            user_emergency_braking = True
        hazard_light = data["api"]["truckBool"]["lightsHazard"]
        park_brake = data["api"]["truckBool"]["parkBrake"]
        gamepaused = data["api"]["pause"]
    except:
        speed = last_speed
        speedlimit = last_speedlimit
        cruisecontrolspeed = 0
        user_accelerating = False
        user_throttle = 0
        user_braking = False
        user_emergency_braking = False
        hazard_light = False
        park_brake = False
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
            trafficlight = data["TrafficLightDetection"]["simple"]
        except:
            trafficlight = "None"
    else:
        trafficlight = "Off"
    if navigationdetectionisenabled == True:
        try:
            if data["NavigationDetection"]["turnincoming"] == True:
                turnincoming_last_time_with = current_time
            if data["NavigationDetection"]["lanedetected"] == True:
                lanedetected_timer = current_time
        except:
            pass
    if current_time - 1 < turnincoming_last_time_with:
        targetspeed = cruisespeed_turn
    if current_time - 1 < lanedetected_timer:
        lanedetected = True
    else:
        lanedetected = False

    if trafficlight != "Red":
        trafficlight_last_time_without = current_time
    else:
        trafficlight_last_time_with = current_time
    if current_time - 0.5 > trafficlight_last_time_without or current_time - 0.5 < trafficlight_last_time_with:
        if stop_trafficlight == True:
            targetspeed = cruisespeed_trafficlight
    
    if targetspeed == 0 and speed > 10:
        trafficlight_allow_acceleration = True

    if current_time - 1 > wait_for_response_timer:
        wait_for_response = False
    if last_cruisecontrolspeed != cruisecontrolspeed:
        wait_for_response = False
        
    if controls.GetKeybindValue("Pause/Resume Automatic Acceleration") == True and pauseresume_allow == True:
        if allow_acceleration == True:
            auto_accelerate = False
            trafficlight_accelerate = False
            allow_acceleration = False
        else:
            auto_accelerate = settings.GetSettings("CruiseControl", "auto_accelerate", False)
            trafficlight_accelerate = settings.GetSettings("CruiseControl", "trafficlight_accelerate", True)
            allow_acceleration = True
        pauseresume_allow = False
    elif controls.GetKeybindValue("Pause/Resume Automatic Acceleration") == False:
        pauseresume_allow = True

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
        if speed < 30 and cruisecontrolspeed == 0 and targetspeed != 0 and trafficlight_accelerate == True and trafficlight_allow_acceleration == True and user_emergency_braking == False and do_lanedetected_stop == False:
            data["sdk"]["acceleration"] = acceleration_strength
            if user_throttle == acceleration_strength:
                user_accelerating = False
            data["sdk"]["brake"] = 0
        if targetspeed == 0 and abs(speed) > 1 and user_accelerating == False:
            data["sdk"]["acceleration"] = 0
            data["sdk"]["brake"] = brake_strength
            user_emergency_braking_timer = current_time
        elif targetspeed == 0 and abs(speed) < 1 and user_accelerating == False:
            park_brake_target = True
        if speed < 30 and cruisecontrolspeed == 0 and targetspeed != 0 and auto_accelerate == True and user_emergency_braking == False and do_lanedetected_stop == False:
            data["sdk"]["acceleration"] = acceleration_strength
            if user_throttle == acceleration_strength:
                user_accelerating = False
            data["sdk"]["brake"] = 0
    else:
        data["sdk"]["acceleration"] = 0
        data["sdk"]["brake"] = 0

    if auto_hazard == True and do_lanedetected_stop == False:
        if current_time - 1 < user_emergency_braking_timer:
            user_emergency_braking = False
        if hazard_light != last_hazard_light or current_time - 1 >  wait_for_response_hazard_light_timer:
            wait_for_response_hazard_light = False
        if user_emergency_braking == True and hazard_light == False and wait_for_response_hazard_light == False:
            data["sdk"]["Hazards"] = True
            wait_for_response_hazard_light = True
            wait_for_response_hazard_light_timer = current_time
        if user_emergency_braking == False and hazard_light == True and wait_for_response_hazard_light == False:
            data["sdk"]["Hazards"] = True
            wait_for_response_hazard_light = True
            wait_for_response_hazard_light_timer = current_time
        if user_emergency_braking == True and abs(speed) < 1 and user_accelerating == False:
            park_brake_target = True

    if auto_stop == True:
        if gamepaused == False and DefaultSteering.enabled == True and lanedetected == False and last_lanedetected == True and user_accelerating == False:
            if navigationdetectionisenabled == True:
                try:
                    frame = data["frameOriginal"]
                    width = frame.shape[1]
                    height = frame.shape[0]
                except:
                    return data
                hwnd_ets2 = ctypes.windll.user32.FindWindowW(None, "Euro Truck Simulator 2")
                hwnd_ets2_multiplayer = ctypes.windll.user32.FindWindowW(None, "Euro Truck Simulator 2 Multiplayer")
                hwnd_ats = ctypes.windll.user32.FindWindowW(None, "American Truck Simulator")
                hwnd_ats_multiplayer = ctypes.windll.user32.FindWindowW(None, "American Truck Simulator Multiplayer")
                hwnd_active = ctypes.windll.user32.GetForegroundWindow()
                if hwnd_active == hwnd_ets2 or hwnd_active == hwnd_ats or hwnd_active == hwnd_ets2_multiplayer or hwnd_active == hwnd_ats_multiplayer:
                    if map_topleft != None and map_bottomright != None and arrow_topleft != None and arrow_bottomright != None and map_topleft[0] < map_bottomright[0] and map_topleft[1] < map_bottomright[1] and arrow_topleft[0] < arrow_bottomright[0] and arrow_topleft[1] < arrow_bottomright[1]:
                        lower_blue = np.array([121, 68, 0])
                        upper_blue = np.array([250, 184, 109])
                        mask_blue = cv2.inRange(frame[arrow_topleft[1] - map_topleft[1]:arrow_bottomright[1] - map_bottomright[1], arrow_topleft[0] - map_topleft[0]:arrow_bottomright[0] - map_bottomright[0]], lower_blue, upper_blue)
                        arrow_height, arrow_width = mask_blue.shape[:2]
                        pixel_ratio = round(cv2.countNonZero(mask_blue) / (arrow_width * arrow_height), 3)
                    else:
                        pixel_ratio = 0
                    if arrow_percentage != None:
                        if pixel_ratio > arrow_percentage * 0.9 and pixel_ratio < arrow_percentage * 1.1:
                            do_lanedetected_stop = True
                    else:
                        do_lanedetected_stop = False
            else:
                do_lanedetected_stop = False
        if user_accelerating == True:
            do_lanedetected_stop = False
        if hazard_light != last_hazard_light or current_time - 1 >  wait_for_response_hazard_light_timer:
            wait_for_response_hazard_light = False
    if do_lanedetected_stop == True:
        if abs(speed) > 1:
            data["sdk"]["acceleration"] = 0
            data["sdk"]["brake"] = 0.1
        elif abs(speed) < 1 and user_accelerating == False:
            park_brake_target = True
        if hazard_light == False and wait_for_response_hazard_light == False:
            data["sdk"]["Hazards"] = True
            wait_for_response_hazard_light = True
            wait_for_response_hazard_light_timer = current_time
    if do_lanedetected_stop == False and last_do_lanedetected_stop == True and hazard_light == True and wait_for_response_hazard_light == False:
        data["sdk"]["Hazards"] = True
        wait_for_response_hazard_light = True
        wait_for_response_hazard_light_timer = current_time

    if current_time - 1 > wait_for_response_park_brake_timer:
        wait_for_response_park_brake = False
    if last_park_brake != park_brake:
        wait_for_response_park_brake = False
    if park_brake_target == True and DefaultSteering.enabled == True:
        if park_brake == False and wait_for_response_park_brake == False:
            data["sdk"]["ParkingBrake"] = True
            wait_for_response_park_brake = True
            wait_for_response_park_brake_timer = current_time
    elif park_brake == True and wait_for_response_park_brake == False and DefaultSteering.enabled == True:
            data["sdk"]["ParkingBrake"] = True
            wait_for_response_park_brake = True
            wait_for_response_park_brake_timer = current_time

    if show_symbols == True:
        try:
            frame = data["frame"]
            width = frame.shape[1]
            height = frame.shape[0]
            if frame is None: return data
            if width == 0 or width == None: return data
            if height == 0 or height == None: return data
        except:
            return data
        try:
            indicator_left = data["api"]["truckBool"]["blinkerLeftActive"]
            indicator_right = data["api"]["truckBool"]["blinkerRightActive"]
        except:
            indicator_left = False
            indicator_right = False
        try:
           turnincoming = data["NavigationDetection"]["turnincoming"]
        except:
            turnincoming = False
        symbol = cruisecontrol_on_set.copy()
        if cruisecontrolspeed != 0:
            if cruisecontrolspeed == targetspeed and DefaultSteering.enabled == True:
                symbol = cruisecontrol_on_set.copy()
            else:
                symbol = cruisecontrol_on_unset.copy()
            if cruisecontrolspeed != targetspeed:
                symbol = cruisecontrol_on_unset.copy()
            if turnincoming == True:
                symbol = cruisecontrol_on_slowed.copy()
            if user_braking == True or user_accelerating == True:
                symbol = cruisecontrol_on_unset.copy()
        else:
            if cruisecontrolspeed == targetspeed:
                if auto_accelerate == True and DefaultSteering.enabled == True:
                    if turnincoming == True:
                        symbol = cruisecontrol_off_slowed.copy()
                    else:
                        symbol = cruisecontrol_off_set.copy()
                elif trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
                    if turnincoming == True:
                        symbol = cruisecontrol_off_slowed.copy()
                    else:
                        symbol = cruisecontrol_off_set.copy()
                else:
                    symbol = cruisecontrol_off_unset.copy()
            elif trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
                if turnincoming == True:
                    symbol = cruisecontrol_off_slowed.copy()
                else:
                    symbol = cruisecontrol_off_set.copy()
            elif auto_accelerate == True and DefaultSteering.enabled == True:
                if turnincoming == True:
                    symbol = cruisecontrol_off_slowed.copy()
                else:
                    symbol = cruisecontrol_off_set.copy()
            else:
                symbol = cruisecontrol_off_unset.copy()
            if user_braking == True or user_accelerating == True:
                symbol = cruisecontrol_off_unset.copy()
        
        if user_emergency_braking == True or do_lanedetected_stop == True:
            if cruisecontrolspeed != 0:
                if cruisecontrolspeed == targetspeed and DefaultSteering.enabled == True:
                    symbol = cruisecontrol_emergency_set.copy()
                else:
                    symbol = cruisecontrol_on_unset.copy()
                if cruisecontrolspeed != targetspeed:
                    symbol = cruisecontrol_emergency_unset.copy()
                if turnincoming == True:
                    symbol = cruisecontrol_emergency_slowed.copy()
                if user_braking == True or user_accelerating == True:
                    symbol = cruisecontrol_emergency_unset.copy()
            else:
                if cruisecontrolspeed == targetspeed:
                    if auto_accelerate == True and DefaultSteering.enabled == True:
                        if turnincoming == True:
                            symbol = cruisecontrol_emergency_slowed.copy()
                        else:
                            symbol = cruisecontrol_emergency_set.copy()
                    elif trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
                        if turnincoming == True:
                            symbol = cruisecontrol_emergency_slowed.copy()
                        else:
                            symbol = cruisecontrol_emergency_set.copy()
                    else:
                        symbol = cruisecontrol_emergency_unset.copy()
                elif trafficlight_accelerate == True and trafficlight_allow_acceleration == True:
                    if turnincoming == True:
                        symbol = cruisecontrol_emergency_slowed.copy()
                    else:
                        symbol = cruisecontrol_emergency_set.copy()
                elif auto_accelerate == True and DefaultSteering.enabled == True:
                    if turnincoming == True:
                        symbol = cruisecontrol_emergency_slowed.copy()
                    else:
                        symbol = cruisecontrol_emergency_set.copy()
                else:
                    symbol = cruisecontrol_emergency_unset.copy()
                if user_braking == True or user_accelerating == True:
                    symbol = cruisecontrol_emergency_unset.copy()
        
        symbol_resized = cv2.resize(symbol, (int(0.4 * height), int(0.234375 * height)))
        target_region = frame[int(height/2.8 - 0.2 * height):int(height/2.8 + 0.034375 * height), width - int(0.4 * height):width]
        if indicator_left or indicator_right:
            target_region = frame[int(height/2.8 - 0.2 * height):int(height/2.8 + 0.034375 * height), width - int(0.4 * height):width]
        else:
            target_region = frame[int(height/4 - 0.2 * height):int(height/4 + 0.034375 * height), width - int(0.4 * height):width]
        target_region[:symbol_resized.shape[0], :symbol_resized.shape[1]] = symbol_resized

    if allow_acceleration == False:
        if show_symbols == False:
            try:
                frame = data["frame"]
                width = frame.shape[1]
                height = frame.shape[0]
                if frame is None: return data
                if width == 0 or width == None: return data
                if height == 0 or height == None: return data
            except:
                return data
        current_text = "Acceleration"
        width_target_current_text = 0.2*width
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
        textsize_paused_text, _ = cv2.getTextSize("Paused", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_paused_text, height_paused_text = textsize_paused_text
        if indicator_left or indicator_right:
            if show_symbols == True:
                cv2.putText(frame, current_text, (round(0.79*width), round(0.4*height+height_current_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
                cv2.putText(frame, "Paused", (round(0.89*width-width_paused_text/2), round(0.4*height+height_current_text*2.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
            else:
                cv2.putText(frame, current_text, (round(0.79*width), round(0.5*height+height_current_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
                cv2.putText(frame, "Paused", (round(0.89*width-width_paused_text/2), round(0.5*height+height_current_text*2.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
        else:
            if show_symbols == True:
                cv2.putText(frame, current_text, (round(0.79*width), round(0.3*height+height_current_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
                cv2.putText(frame, "Paused", (round(0.89*width-width_paused_text/2), round(0.3*height+height_current_text*2.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
            else:
                cv2.putText(frame, current_text, (round(0.79*width), round(0.4*height+height_current_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
                cv2.putText(frame, "Paused", (round(0.89*width-width_paused_text/2), round(0.4*height+height_current_text*2.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)

    if show_symbols == True:
        try:
            data["frame"] = frame
        except:
            pass
    
    last_park_brake = park_brake
    last_lanedetected = lanedetected
    last_do_lanedetected_stop = do_lanedetected_stop
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
            settings.CreateSettings("CruiseControl", "acceleration", self.accelerationSlider.get())
            settings.CreateSettings("CruiseControl", "brake", self.brakeSlider.get())
            UpdateSettings()
        
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
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
            
            helpers.MakeCheckButton(generalFrame, "Automatically enable cruise control when available.", "CruiseControl", "auto_enable", 2, 0, width=90, callback=lambda: UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Stop the truck when a red traffic light is detected.\n(requires that the TrafficLightDetection plugin is enabled)", "CruiseControl", "stop_trafficlight", 3, 0, width=90, callback=lambda: UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatically accelerate when the red traffic light turns green.", "CruiseControl", "trafficlight_accelerate", 4, 0, width=90, callback=lambda: UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatically accelerate to the target speed, even if your truck is standing still.\n(if you disable the steering or pause this feature, the truck will not accelerate to the target speed)", "CruiseControl", "auto_accelerate", 5, 0, width=90, callback=lambda: UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatically enable the hazard light, when the user does a emergency stop.", "CruiseControl", "auto_hazard", 6, 0, width=90, callback=lambda: UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatically come to a stop and enable the hazard light if no lane is detected.", "CruiseControl", "auto_stop", 7, 0, width=90, callback=lambda: UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Show Cruise Control symbol in the Lane Assist window. (ShowImage Plugin)", "CruiseControl", "show_symbols", 8, 0, width=90, callback=lambda: UpdateSettings())
            
            self.accelerationSlider = tk.Scale(generalFrame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.accelerationSlider.set(settings.GetSettings("CruiseControl", "acceleration", 50))
            self.accelerationSlider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.acceleration = helpers.MakeComboEntry(generalFrame, "Acceleration\nstrength in %", "CruiseControl", "acceleration", 9, 0)
            
            self.brakeSlider = tk.Scale(generalFrame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.brakeSlider.set(settings.GetSettings("CruiseControl", "brake", 100))
            self.brakeSlider.grid(row=10, column=0, padx=10, pady=0, columnspan=2)
            self.brake = helpers.MakeComboEntry(generalFrame, "Brake\nstrength in %", "CruiseControl", "brake", 10, 0)

            helpers.MakeLabel(generalFrame, "For the best experience, you need to go in the game settings under Gameplay and enable\nthe Adaptive cruise control to the highest possible distance and set the Emergency brake\nsystem to Full detection!", 11, 0, sticky="w")

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)