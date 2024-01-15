"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import switchSelectedPlugin, resizeWindow

PluginInfo = PluginInformation(
    name="TruckStats", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="This Plugin shows some statistics about the truck and the game",
    version="0.1",
    author="Glas42",
    url="https://github.com/Glas42/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before game", # Will run the plugin before anything else in the mainloop (data will be empty)
    requires=["TruckSimAPI"]
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

import cv2
import numpy as np
import pyautogui
import ctypes
import mouse
import time

def LoadSettings():
    global name_window
    global current_tab
    global text_color
    global open_tab_color
    global open_tab_hover_color
    global closed_tab_color
    global closed_tab_hover_color

    global width_screen
    global height_screen
    global last_width_frame
    global last_height_frame
    global frame_original

    global settings_show_graphs
    global settings_use_imperial_system
    global settings_use_us_gallons
    global settings_fuel_tab_color
    global settings_fuel_value_to_graph
    global settings_engine_value_to_graph

    global fuel_last_avg_consumption
    global fuel_value_history
    global fuel_value_history_time
    global fuel_value_history_adder
    global fuel_value_history_count

    global engine_value_history
    global engine_value_history_time
    global engine_value_history_adder
    global engine_value_history_count

    global reset_trip
    global reset_fuelgraph
    global reset_enginegraph
    global last_route_distance_left

    name_window = "TruckStats"
    current_tab = settings.GetSettings("TruckStats", "current_tab", 1)
    text_color = (255,255,255)

    width_screen, height_screen = pyautogui.size()
    width_frame = settings.GetSettings("TruckStats", "width_frame", round(height_screen/2.5))
    height_frame = settings.GetSettings("TruckStats", "height_frame", round(height_screen/4))
    last_width_frame = width_frame
    last_height_frame = height_frame
    frame_original = np.zeros((height_frame, width_frame, 3), dtype=np.uint8)

    settings_show_graphs = settings.GetSettings("TruckStats", "show_graphs", True)
    settings_use_imperial_system = settings.GetSettings("TruckStats", "use_imperial_system", False)
    settings_use_us_gallons = settings.GetSettings("TruckStats", "use_us_gallons", False)
    settings_fuel_tab_color = settings.GetSettings("TruckStats", "show_in_green", True)
    settings_fuel_value_to_graph = settings.GetSettings("TruckStats", "fuel_value_to_graph", "fuel_current")
    settings_engine_value_to_graph = settings.GetSettings("TruckStats", "engine_value_to_graph", "rpm")

    fuel_last_avg_consumption = 0

    fuel_value_history = []
    fuel_value_history_adder = settings.GetSettings("TruckStats", "fuel_value_history_adder", 60)
    fuel_value_history_time = time.time() + 1
    fuel_value_history_count = 0

    engine_value_history = []
    engine_value_history_adder = settings.GetSettings("TruckStats", "engine_value_history_adder", 60)
    engine_value_history_time = time.time() + 1
    engine_value_history_count = 0

    reset_trip = settings.GetSettings("TruckStats", "reset_trip", False)
    reset_fuelgraph = settings.GetSettings("TruckStats", "reset_fuelgraph", False)
    reset_enginegraph = settings.GetSettings("TruckStats", "reset_enginegraph", False)
    last_route_distance_left = 0

    open_tab_color_r = settings.GetSettings("TruckStats", "open_tab_color_r")
    if open_tab_color_r == None or not isinstance(open_tab_color_r, int) or not (0 <= open_tab_color_r <= 255):
        settings.CreateSettings("TruckStats", "open_tab_color_r", 255)
        open_tab_color_r = 255
    open_tab_color_g = settings.GetSettings("TruckStats", "open_tab_color_g")
    if open_tab_color_g == None or not isinstance(open_tab_color_g, int) or not (0 <= open_tab_color_g <= 255):
        settings.CreateSettings("TruckStats", "open_tab_color_g", 127)
        open_tab_color_g = 127
    open_tab_color_b = settings.GetSettings("TruckStats", "open_tab_color_b")
    if open_tab_color_b == None or not isinstance(open_tab_color_b, int) or not (0 <= open_tab_color_b <= 255):
        settings.CreateSettings("TruckStats", "open_tab_color_b", 0)
        open_tab_color_b = 0
    open_tab_color = (open_tab_color_b, open_tab_color_g, open_tab_color_r)
    open_tab_hover_color_r = settings.GetSettings("TruckStats", "open_tab_hover_color_r")
    if open_tab_hover_color_r == None or not isinstance(open_tab_hover_color_r, int) or not (0 <= open_tab_hover_color_r <= 255):
        settings.CreateSettings("TruckStats", "open_tab_hover_color_r", 255)
        open_tab_hover_color_r = 255
    open_tab_hover_color_g = settings.GetSettings("TruckStats", "open_tab_hover_color_g")
    if open_tab_hover_color_g == None or not isinstance(open_tab_hover_color_g, int) or not (0 <= open_tab_hover_color_g <= 255):
        settings.CreateSettings("TruckStats", "open_tab_hover_color_g", 157)
        open_tab_hover_color_g = 157
    open_tab_hover_color_b = settings.GetSettings("TruckStats", "open_tab_hover_color_b")
    if open_tab_hover_color_b == None or not isinstance(open_tab_hover_color_b, int) or not (0 <= open_tab_hover_color_b <= 255):
        settings.CreateSettings("TruckStats", "open_tab_hover_color_b", 30)
        open_tab_hover_color_b = 30
    open_tab_hover_color = (open_tab_hover_color_b, open_tab_hover_color_g, open_tab_hover_color_r)
    closed_tab_color_r = settings.GetSettings("TruckStats", "closed_tab_color_r")
    if closed_tab_color_r == None or not isinstance(closed_tab_color_r, int) or not (0 <= closed_tab_color_r <= 255):
        settings.CreateSettings("TruckStats", "closed_tab_color_r", 100)
        closed_tab_color_r = 100
    closed_tab_color_g = settings.GetSettings("TruckStats", "closed_tab_color_g")
    if closed_tab_color_g == None or not isinstance(closed_tab_color_g, int) or not (0 <= closed_tab_color_g <= 255):
        settings.CreateSettings("TruckStats", "closed_tab_color_g", 100)
        closed_tab_color_g = 100
    closed_tab_color_b = settings.GetSettings("TruckStats", "closed_tab_color_b")
    if closed_tab_color_b == None or not isinstance(closed_tab_color_b, int) or not (0 <= closed_tab_color_b <= 255):
        settings.CreateSettings("TruckStats", "closed_tab_color_b", 100)
        closed_tab_color_b = 100
    closed_tab_color = (closed_tab_color_b, closed_tab_color_g, closed_tab_color_r)
    closed_tab_hover_color_r = settings.GetSettings("TruckStats", "closed_tab_hover_color_r")
    if closed_tab_hover_color_r == None or not isinstance(closed_tab_hover_color_r, int) or not (0 <= closed_tab_hover_color_r <= 255):
        settings.CreateSettings("TruckStats", "closed_tab_hover_color_r", 130)
        closed_tab_hover_color_r = 130
    closed_tab_hover_color_g = settings.GetSettings("TruckStats", "closed_tab_hover_color_g")
    if closed_tab_hover_color_g == None or not isinstance(closed_tab_hover_color_g, int) or not (0 <= closed_tab_hover_color_g <= 255):
        settings.CreateSettings("TruckStats", "closed_tab_hover_color_g", 130)
        closed_tab_hover_color_g = 130
    closed_tab_hover_color_b = settings.GetSettings("TruckStats", "closed_tab_hover_color_b")
    if closed_tab_hover_color_b == None or not isinstance(closed_tab_hover_color_b, int) or not (0 <= closed_tab_hover_color_b <= 255):
        settings.CreateSettings("TruckStats", "closed_tab_hover_color_b", 130)
        closed_tab_hover_color_b = 130
    closed_tab_hover_color = (closed_tab_hover_color_b, closed_tab_hover_color_g, closed_tab_hover_color_r)
    
LoadSettings()


def plugin(data):
    global name_window
    global current_tab
    global text_color
    global open_tab_color
    global open_tab_hover_color
    global closed_tab_color
    global closed_tab_hover_color

    global width_screen
    global height_screen
    global last_width_frame
    global last_height_frame
    global frame_original

    global settings_show_graphs
    global settings_use_imperial_system
    global settings_use_us_gallons
    global settings_fuel_tab_color
    global settings_fuel_value_to_graph
    global settings_engine_value_to_graph

    global fuel_last_avg_consumption
    global fuel_value_history
    global fuel_value_history_time
    global fuel_value_history_adder
    global fuel_value_history_count

    global engine_value_history
    global engine_value_history_time
    global engine_value_history_adder
    global engine_value_history_count

    global reset_trip
    global reset_fuelgraph
    global reset_enginegraph
    global last_route_distance_left

    try:
        size_frame = cv2.getWindowImageRect(name_window)
        width_frame = size_frame[2]
        height_frame = size_frame[3]
        x1, y1, _, _ = size_frame
        x2, y2 = mouse.get_position()
        mousex = x2-x1
        mousey = y2-y1
        if width_frame != 0 and height_frame != 0:
            mouseposx = mousex/width_frame
            mouseposy = mousey/height_frame
        else:
            mouseposx = 0
            mouseposy = 0
        resize_frame = False
    except:
        width_frame = last_width_frame
        height_frame = last_height_frame
        mouseposx = 0
        mouseposy = 0
        resize_frame = True

    try:
        gamepaused = data["api"]["pause"]
    except:
        gamepaused = False

    try:
        data["sdk"]
    except:
        data["sdk"] = {}

    try:
        if width_frame != last_width_frame or height_frame != last_height_frame:
            frame_original = np.zeros((height_frame, width_frame, 3), dtype=np.uint8)
            if width_frame >= 50 and height_frame >= 50:
                settings.CreateSettings("TruckStats", "width_frame", width_frame)
                settings.CreateSettings("TruckStats", "height_frame", height_frame)
    except:
        pass
    last_width_frame = width_frame
    last_height_frame = height_frame

    frame = frame_original.copy()
    
    if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, name_window):
        mouse_left_clicked = True
    else:
        mouse_left_clicked = False

    current_time = time.time()

    try:
        fuel_total = data["api"]["configFloat"]["fuelCapacity"]
        fuel_current = data["api"]["truckFloat"]["fuel"]
        if fuel_total != 0:
            fuel_percentage = (fuel_current/fuel_total)*100
        else:
            fuel_percentage = 0
        fuel_range = data["api"]["truckFloat"]["fuelRange"]
        fuel_avg_consumption = data["api"]["truckFloat"]["fuelAvgConsumption"]
        if fuel_avg_consumption == 0:
            fuel_avg_consumption = fuel_last_avg_consumption
        fuel_last_avg_consumption = fuel_avg_consumption

        engine_rpm = data["api"]["truckFloat"]["engineRpm"]
        engine_throttle = data["api"]["truckFloat"]["gameThrottle"]
        engine_throttle = engine_throttle*100
        engine_oil_temperature = data["api"]["truckFloat"]["oilTemperature"]
        engine_oil_pressure = data["api"]["truckFloat"]["oilPressure"]

        lights_beamlow = data["api"]["truckBool"]["lightsBeamLow"]
        lights_beamhigh = data["api"]["truckBool"]["lightsBeamHigh"]
        lights_brake = data["api"]["truckBool"]["lightsBrake"]
        lights_reverse = data["api"]["truckBool"]["lightsReverse"]
        lights_indicator = "False"
        istrue = data["api"]["truckBool"]["blinkerLeftActive"]
        if istrue == True:
            lights_indicator = "Left"
        istrue = data["api"]["truckBool"]["blinkerRightActive"]
        if istrue == True:
            lights_indicator = "Right"
        istrue = data["api"]["truckBool"]["lightsHazard"]
        if istrue == True:
            lights_indicator = "Hazard"

        time_route_left = data["api"]["truckFloat"]["routeTime"]
        time_route_left_real = time_route_left/20

        route_distance_left = data["api"]["truckFloat"]["routeDistance"]
        route_distance_left = route_distance_left/1000
        route_speed = data["api"]["truckFloat"]["speed"]
        route_speed = route_speed*3.6
        route_speed_kmh = route_speed
        route_speedlimit = data["api"]["truckFloat"]["speedLimit"]
        route_speedlimit = route_speedlimit*3.6
        route_speedlimit_kmh = route_speedlimit
        route_destination = data["api"]["configString"]["cityDst"]

        truck_name = data["api"]["configString"]["truckName"]
        truck_cargo = data["api"]["configString"]["cargo"]

        look_for_trucksimapi = False
    except:
        look_for_trucksimapi = True

        fuel_total = 0
        fuel_current = 0
        fuel_percentage = 0
        fuel_range = 0
        fuel_avg_consumption = 0

        engine_rpm = 0
        engine_throttle = 0
        engine_oil_temperature = 0
        engine_oil_pressure = 0

        lights_beamlow = False
        lights_beamhigh = False
        lights_brake = False
        lights_reverse = False
        lights_indicator = "False"

        time_route_left = 0
        time_route_left_real = 0

        route_distance_left = 0
        route_speed = 0
        route_speed_kmh = 0
        route_speedlimit = 0
        route_speedlimit_kmh = 0
        route_destination = ""

        truck_name = ""
        truck_cargo = ""
    
    time_route_left_hours = round(time_route_left // 3600)
    time_route_left_minutes = round((time_route_left % 3600) // 60)
    time_route_left_seconds = round(time_route_left % 60)
    if time_route_left_minutes == 60:
        time_route_left_hours += 1
        time_route_left_minutes = 0
    if time_route_left_seconds == 60:
        time_route_left_minutes += 1
        time_route_left_seconds = 0
    time_route_left_hours_str = f"0{time_route_left_hours}" if time_route_left_hours < 10 else str(time_route_left_hours)
    time_route_left_minutes_str = f"0{time_route_left_minutes}" if time_route_left_minutes < 10 else str(time_route_left_minutes)
    time_route_left_seconds_str = f"0{time_route_left_seconds}" if time_route_left_seconds < 10 else str(time_route_left_seconds)
    time_route_left_hours_real = round(time_route_left_real // 3600)
    time_route_left_minutes_real = round((time_route_left_real % 3600) // 60)
    time_route_left_seconds_real = round(time_route_left_real % 60)
    if time_route_left_minutes_real == 60:
        time_route_left_hours_real += 1
        time_route_left_minutes_real = 0
    if time_route_left_seconds_real == 60:
        time_route_left_minutes_real += 1
        time_route_left_seconds_real = 0
    time_route_left_hours_real_str = f"0{time_route_left_hours_real}" if time_route_left_hours_real < 10 else str(time_route_left_hours_real)
    time_route_left_minutes_real_str = f"0{time_route_left_minutes_real}" if time_route_left_minutes_real < 10 else str(time_route_left_minutes_real)
    time_route_left_seconds_real_str = f"0{time_route_left_seconds_real}" if time_route_left_seconds_real < 10 else str(time_route_left_seconds_real)
    
    if settings_use_imperial_system == True:
        fuel_range = fuel_range/1.609344
        engine_oil_temperature = engine_oil_temperature * (9/5) + 32
        route_distance_left = route_distance_left/1.609344
        route_speed = route_speed/1.609344
        route_speedlimit = route_speedlimit/1.609344
        if settings_use_us_gallons == True:
            fuel_total = fuel_total/3.785411784
            fuel_current = fuel_current/3.785411784
        else:
            fuel_total = fuel_total/4.54609
            fuel_current = fuel_current/4.54609

    if gamepaused == True:
        fuel_value_history_time = current_time - round(fuel_value_history_adder/2)
        engine_value_history_time = current_time - round(engine_value_history_adder/2)

    if settings_show_graphs == True and gamepaused == False:
        if fuel_value_history_time <= current_time:
            if settings_fuel_value_to_graph == "avg_consumption":
                if fuel_avg_consumption != 0:
                    fuel_value_history.append((fuel_avg_consumption, fuel_value_history_count))
                    fuel_value_history_time += fuel_value_history_adder
                    fuel_value_history_count += 1
            if settings_fuel_value_to_graph == "range":
                fuel_value_history.append((fuel_range, fuel_value_history_count))
                fuel_value_history_time += fuel_value_history_adder
                fuel_value_history_count += 1
            if settings_fuel_value_to_graph == "fuel_percentage":
                fuel_value_history.append((fuel_percentage, fuel_value_history_count))
                fuel_value_history_time += fuel_value_history_adder
                fuel_value_history_count += 1
            if settings_fuel_value_to_graph == "fuel_current":
                fuel_value_history.append((fuel_current, fuel_value_history_count))
                fuel_value_history_time += fuel_value_history_adder
                fuel_value_history_count += 1

        if engine_value_history_time <= current_time:
            if settings_engine_value_to_graph == "rpm":
                engine_value_history.append((engine_rpm, engine_value_history_count))
                engine_value_history_time += engine_value_history_adder
                engine_value_history_count += 1
            if settings_engine_value_to_graph == "throttle":
                engine_value_history.append((engine_throttle, engine_value_history_count))
                engine_value_history_time += engine_value_history_adder
                engine_value_history_count += 1
            if settings_engine_value_to_graph == "oil_temperature":
                engine_value_history.append((engine_oil_temperature, engine_value_history_count))
                engine_value_history_time += engine_value_history_adder
                engine_value_history_count += 1
            if settings_engine_value_to_graph == "oil_pressure":
                engine_value_history.append((engine_oil_pressure, engine_value_history_count))
                engine_value_history_time += engine_value_history_adder
                engine_value_history_count += 1

    if route_distance_left == 0 and last_route_distance_left != 0:
        if reset_trip == True:
            data["sdk"]["TripReset"] = True
        if reset_fuelgraph == True:
            fuel_value_history = []
            fuel_value_history_time = current_time + 1
            fuel_value_history_count = 0
        if reset_enginegraph == True:
            engine_value_history = []
            engine_value_history_time = current_time + 1
            engine_value_history_count = 0
    last_route_distance_left = route_distance_left

    if current_tab != 1:
        if mouseposx >= 0.14 and mouseposy >= 0.02 and mouseposx <= 0.26 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.15*width_frame), round(0.03*height_frame)), (round(0.25*width_frame), round(0.05*height_frame)), closed_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.15*width_frame), round(0.03*height_frame)), (round(0.25*width_frame), round(0.05*height_frame)), closed_tab_hover_color, -1)
            if mouse_left_clicked == True:
                current_tab = 1
                settings.CreateSettings("TruckStats", "current_tab", 1)
        else:
            cv2.rectangle(frame, (round(0.15*width_frame), round(0.03*height_frame)), (round(0.25*width_frame), round(0.05*height_frame)), closed_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.15*width_frame), round(0.03*height_frame)), (round(0.25*width_frame), round(0.05*height_frame)), closed_tab_color, -1)
    else:
        if mouseposx >= 0.14 and mouseposy >= 0.02 and mouseposx <= 0.26 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.15*width_frame), round(0.03*height_frame)), (round(0.25*width_frame), round(0.05*height_frame)), open_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.15*width_frame), round(0.03*height_frame)), (round(0.25*width_frame), round(0.05*height_frame)), open_tab_hover_color, -1)
        else:
            cv2.rectangle(frame, (round(0.15*width_frame), round(0.03*height_frame)), (round(0.25*width_frame), round(0.05*height_frame)), open_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.15*width_frame), round(0.03*height_frame)), (round(0.25*width_frame), round(0.05*height_frame)), open_tab_color, -1)
    current_text = "Fuel"
    width_target_current_text = 0.07*width_frame
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
    cv2.putText(frame, current_text, (round(0.20*width_frame-width_current_text/2), round(0.04*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)

    if current_tab != 2:
        if mouseposx >= 0.29 and mouseposy >= 0.02 and mouseposx <= 0.41 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.30*width_frame), round(0.03*height_frame)), (round(0.40*width_frame), round(0.05*height_frame)), closed_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.30*width_frame), round(0.03*height_frame)), (round(0.40*width_frame), round(0.05*height_frame)), closed_tab_hover_color, -1)
            if mouse_left_clicked == True:
                current_tab = 2
                settings.CreateSettings("TruckStats", "current_tab", 2)
        else:
            cv2.rectangle(frame, (round(0.30*width_frame), round(0.03*height_frame)), (round(0.40*width_frame), round(0.05*height_frame)), closed_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.30*width_frame), round(0.03*height_frame)), (round(0.40*width_frame), round(0.05*height_frame)), closed_tab_color, -1)
    else:
        if mouseposx >= 0.29 and mouseposy >= 0.02 and mouseposx <= 0.41 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.30*width_frame), round(0.03*height_frame)), (round(0.40*width_frame), round(0.05*height_frame)), open_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.30*width_frame), round(0.03*height_frame)), (round(0.40*width_frame), round(0.05*height_frame)), open_tab_hover_color, -1)
        else:
            cv2.rectangle(frame, (round(0.30*width_frame), round(0.03*height_frame)), (round(0.40*width_frame), round(0.05*height_frame)), open_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.30*width_frame), round(0.03*height_frame)), (round(0.40*width_frame), round(0.05*height_frame)), open_tab_color, -1)
    current_text = "Engine"
    width_target_current_text = 0.1*width_frame
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
    cv2.putText(frame, current_text, (round(0.35*width_frame-width_current_text/2), round(0.04*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)

    if current_tab != 3:
        if mouseposx >= 0.44 and mouseposy >= 0.02 and mouseposx <= 0.56 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.45*width_frame), round(0.03*height_frame)), (round(0.55*width_frame), round(0.05*height_frame)), closed_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.45*width_frame), round(0.03*height_frame)), (round(0.55*width_frame), round(0.05*height_frame)), closed_tab_hover_color, -1)
            if mouse_left_clicked == True:
                current_tab = 3
                settings.CreateSettings("TruckStats", "current_tab", 3)
        else:
            cv2.rectangle(frame, (round(0.45*width_frame), round(0.03*height_frame)), (round(0.55*width_frame), round(0.05*height_frame)), closed_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.45*width_frame), round(0.03*height_frame)), (round(0.55*width_frame), round(0.05*height_frame)), closed_tab_color, -1)
    else:
        if mouseposx >= 0.44 and mouseposy >= 0.02 and mouseposx <= 0.56 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.45*width_frame), round(0.03*height_frame)), (round(0.55*width_frame), round(0.05*height_frame)), open_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.45*width_frame), round(0.03*height_frame)), (round(0.55*width_frame), round(0.05*height_frame)), open_tab_hover_color, -1)
        else:
            cv2.rectangle(frame, (round(0.45*width_frame), round(0.03*height_frame)), (round(0.55*width_frame), round(0.05*height_frame)), open_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.45*width_frame), round(0.03*height_frame)), (round(0.55*width_frame), round(0.05*height_frame)), open_tab_color, -1)
    current_text = "Lights"
    width_target_current_text = 0.1*width_frame
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
    cv2.putText(frame, current_text, (round(0.50*width_frame-width_current_text/2), round(0.04*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)

    if current_tab != 4:
        if mouseposx >= 0.59 and mouseposy >= 0.02 and mouseposx <= 0.71 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.60*width_frame), round(0.03*height_frame)), (round(0.70*width_frame), round(0.05*height_frame)), closed_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.60*width_frame), round(0.03*height_frame)), (round(0.70*width_frame), round(0.05*height_frame)), closed_tab_hover_color, -1)
            if mouse_left_clicked == True:
                current_tab = 4
                settings.CreateSettings("TruckStats", "current_tab", 4)
        else:
            cv2.rectangle(frame, (round(0.60*width_frame), round(0.03*height_frame)), (round(0.70*width_frame), round(0.05*height_frame)), closed_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.60*width_frame), round(0.03*height_frame)), (round(0.70*width_frame), round(0.05*height_frame)), closed_tab_color, -1)
    else:
        if mouseposx >= 0.59 and mouseposy >= 0.02 and mouseposx <= 0.71 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.60*width_frame), round(0.03*height_frame)), (round(0.70*width_frame), round(0.05*height_frame)), open_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.60*width_frame), round(0.03*height_frame)), (round(0.70*width_frame), round(0.05*height_frame)), open_tab_hover_color, -1)
        else:
            cv2.rectangle(frame, (round(0.60*width_frame), round(0.03*height_frame)), (round(0.70*width_frame), round(0.05*height_frame)), open_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.60*width_frame), round(0.03*height_frame)), (round(0.70*width_frame), round(0.05*height_frame)), open_tab_color, -1)
    current_text = "Route"
    width_target_current_text = 0.1*width_frame
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
    cv2.putText(frame, current_text, (round(0.65*width_frame-width_current_text/2), round(0.04*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
    
    if current_tab != 5:
        if mouseposx >= 0.74 and mouseposy >= 0.02 and mouseposx <= 0.86 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.75*width_frame), round(0.03*height_frame)), (round(0.85*width_frame), round(0.05*height_frame)), closed_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.75*width_frame), round(0.03*height_frame)), (round(0.85*width_frame), round(0.05*height_frame)), closed_tab_hover_color, -1)
            if mouse_left_clicked == True:
                current_tab = 5
                settings.CreateSettings("TruckStats", "current_tab", 5)
        else:
            cv2.rectangle(frame, (round(0.75*width_frame), round(0.03*height_frame)), (round(0.85*width_frame), round(0.05*height_frame)), closed_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.75*width_frame), round(0.03*height_frame)), (round(0.85*width_frame), round(0.05*height_frame)), closed_tab_color, -1)
    else:
        if mouseposx >= 0.74 and mouseposy >= 0.02 and mouseposx <= 0.86 and mouseposy <= 0.06:
            cv2.rectangle(frame, (round(0.75*width_frame), round(0.03*height_frame)), (round(0.85*width_frame), round(0.05*height_frame)), open_tab_hover_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.75*width_frame), round(0.03*height_frame)), (round(0.85*width_frame), round(0.05*height_frame)), open_tab_hover_color, -1)
        else:
            cv2.rectangle(frame, (round(0.75*width_frame), round(0.03*height_frame)), (round(0.85*width_frame), round(0.05*height_frame)), open_tab_color, round(0.02*width_frame))
            cv2.rectangle(frame, (round(0.75*width_frame), round(0.03*height_frame)), (round(0.85*width_frame), round(0.05*height_frame)), open_tab_color, -1)
    current_text = "Truck"
    width_target_current_text = 0.1*width_frame
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
    cv2.putText(frame, current_text, (round(0.80*width_frame-width_current_text/2), round(0.04*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)

    
    if current_tab == 1:
        current_text = f"Fuel: "
        width_target_current_text = 0.2*width_frame
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
        width_original_text = width_current_text
        height_original_text = height_current_text
        thickness_current_text = round(fontscale_current_text*2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        if settings_fuel_tab_color == True:
            current_text_color = (0,255,0)
        else:
            current_text_color = text_color
        if fuel_percentage <= 20:
            current_text_color = (0,255,255)
        if fuel_percentage <= 10:
            current_text_color = (0,0,255)
        fuel_percentage_str = str(round(fuel_percentage, 1)) + ".0" if "." not in str(round(fuel_percentage, 1)) else str(round(fuel_percentage, 1))
        fuel_current_str = str(round(fuel_current, 1)) + ".0" if "." not in str(round(fuel_current, 1)) else str(round(fuel_current, 1))
        fuel_total_str = str(round(fuel_total, 1)) + ".0" if "." not in str(round(fuel_total, 1)) else str(round(fuel_total, 1))
        fuel_range_str = str(round(fuel_range, 1)) + ".0" if "." not in str(round(fuel_range, 1)) else str(round(fuel_range, 1))
        textsize_current_text, _ = cv2.getTextSize(f"{fuel_current_str}L", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_fuel_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, current_text, (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(f"{fuel_percentage_str}%", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, f"{fuel_percentage_str}%", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
        cv2.putText(frame, f"Est. Range: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_current_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        if settings_use_imperial_system == False:
            textsize_current_text, _ = cv2.getTextSize(f"{fuel_range_str}Km", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{fuel_range_str}Km", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
        else:
            textsize_current_text, _ = cv2.getTextSize(f"{fuel_range_str}Mi", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{fuel_range_str}Mi", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
        if settings_use_imperial_system == False:
            textsize_current_text, _ = cv2.getTextSize(f"{fuel_current_str}L", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{fuel_current_str}L", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_current_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
        else:
            textsize_current_text, _ = cv2.getTextSize(f"{fuel_current_str}Gal", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{fuel_current_str}Gal", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_current_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
        if settings_use_imperial_system == False:
            cv2.putText(frame, f"of {fuel_total_str}L", (round(width_current_text + 0.135*width_frame), round(0.2*height_frame+height_current_text/2+height_current_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        else:
            cv2.putText(frame, f"of {fuel_total_str}Gal", (round(width_current_text + 0.135*width_frame), round(0.2*height_frame+height_current_text/2+height_current_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        if settings_show_graphs == True:
            cv2.line(frame, (round(0.05*width_frame), round(0.93*height_frame)), (round(0.05*width_frame), round(0.55*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.05*width_frame-0.04*height_frame), round(0.59*height_frame)), (round(0.05*width_frame), round(0.55*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.05*width_frame+0.04*height_frame), round(0.59*height_frame)), (round(0.05*width_frame), round(0.55*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.05*width_frame), round(0.93*height_frame)), (round(0.95*width_frame), round(0.93*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.95*width_frame-0.04*height_frame), round(0.97*height_frame)), (round(0.95*width_frame), round(0.93*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.95*width_frame-0.04*height_frame), round(0.89*height_frame)), (round(0.95*width_frame), round(0.93*height_frame)), text_color, thickness_current_text)
            plot_width = int(0.8 * width_frame)
            plot_height = int(0.3 * height_frame)
            plot_origin = (int(0.1 * width_frame), int(0.6 * height_frame))
            plot_img = np.zeros((plot_height, plot_width, 3), dtype=np.uint8)
            max_value = max(fuel_value_history, key=lambda x: x[0])[0] if fuel_value_history else 1
            if max_value == 0:
                max_value = 1
            points = []
            for i, (value, _) in enumerate(fuel_value_history):
                x = plot_width - int((i / (len(fuel_value_history) - 1)) * plot_width) if len(fuel_value_history) > 1 else plot_width
                y = plot_height - int((value / max_value) * plot_height)
                points.append((round(0.8*width_frame-x), y))
            for i in range(1, len(points)):
                cv2.line(plot_img, points[i - 1], points[i], (255, 255, 255), max(1, round(thickness_current_text/2)), cv2.LINE_AA)
            frame[plot_origin[1]:plot_origin[1] + plot_height, plot_origin[0]:plot_origin[0] + plot_width] = plot_img


    if current_tab == 2:
        current_text = f"RPM: "
        width_target_current_text = 0.2066*width_frame
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
        width_original_text = width_current_text
        height_original_text = height_current_text
        thickness_current_text = round(fontscale_current_text*2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        current_text_color = text_color
        engine_rpm_str = str(round(engine_rpm, 1)) + ".0" if "." not in str(round(engine_rpm, 1)) else str(round(engine_rpm, 1))
        engine_oil_temperature_str = str(round(engine_oil_temperature, 1)) + ".0" if "." not in str(round(engine_oil_temperature, 1)) else str(round(engine_oil_temperature, 1))
        engine_throttle_str = str(round(engine_throttle, 1)) + ".0" if "." not in str(round(engine_throttle, 1)) else str(round(engine_throttle, 1))
        cv2.putText(frame, current_text, (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(f"{engine_rpm_str}RPM", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, f"{engine_rpm_str}RPM", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Oil Temp: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        if settings_use_imperial_system == False:
            textsize_current_text, _ = cv2.getTextSize(f"{engine_oil_temperature_str}C", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{engine_oil_temperature_str}C", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        else:
            textsize_current_text, _ = cv2.getTextSize(f"{engine_oil_temperature_str}F", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{engine_oil_temperature_str}F", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Throttle: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(f"{engine_throttle_str}%", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, f"{engine_throttle_str}%", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        if settings_show_graphs == True:
            cv2.line(frame, (round(0.05*width_frame), round(0.93*height_frame)), (round(0.05*width_frame), round(0.55*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.05*width_frame-0.04*height_frame), round(0.59*height_frame)), (round(0.05*width_frame), round(0.55*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.05*width_frame+0.04*height_frame), round(0.59*height_frame)), (round(0.05*width_frame), round(0.55*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.05*width_frame), round(0.93*height_frame)), (round(0.95*width_frame), round(0.93*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.95*width_frame-0.04*height_frame), round(0.97*height_frame)), (round(0.95*width_frame), round(0.93*height_frame)), text_color, thickness_current_text)
            cv2.line(frame, (round(0.95*width_frame-0.04*height_frame), round(0.89*height_frame)), (round(0.95*width_frame), round(0.93*height_frame)), text_color, thickness_current_text)
            plot_width = int(0.8 * width_frame)
            plot_height = int(0.3 * height_frame)
            plot_origin = (int(0.1 * width_frame), int(0.6 * height_frame))
            plot_img = np.zeros((plot_height, plot_width, 3), dtype=np.uint8)
            max_value = max(engine_value_history, key=lambda x: x[0])[0] if engine_value_history else 1
            if max_value == 0:
                max_value = 1
            points = []
            for i, (value, _) in enumerate(engine_value_history):
                x = plot_width - int((i / (len(engine_value_history) - 1)) * plot_width) if len(engine_value_history) > 1 else plot_width
                y = plot_height - int((value / max_value) * plot_height)
                points.append((round(0.8*width_frame-x), y))
            for i in range(1, len(points)):
                cv2.line(plot_img, points[i - 1], points[i], (255, 255, 255), max(1, round(thickness_current_text/2)), cv2.LINE_AA)
            frame[plot_origin[1]:plot_origin[1] + plot_height, plot_origin[0]:plot_origin[0] + plot_width] = plot_img


    if current_tab == 3:
        current_text = f"Low Beam: "
        width_target_current_text = 0.39*width_frame
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
        width_original_text = width_current_text
        height_original_text = height_current_text
        thickness_current_text = round(fontscale_current_text*2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        current_text_color = text_color
        cv2.putText(frame, current_text, (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(str(lights_beamlow), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, str(lights_beamlow), (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "High Beam: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(str(lights_beamhigh), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, str(lights_beamhigh), (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Brake Light: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(str(lights_brake), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, str(lights_brake), (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Reverse Light: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*4.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(str(lights_reverse), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, str(lights_reverse), (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*4.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Indicator: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*6)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(str(lights_indicator), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        if lights_indicator == "Left":
            current_text_color = (0, 127, 255)
        if lights_indicator == "Right":
            current_text_color = (0, 127, 255)
        if lights_indicator == "Hazard":
            current_text_color = (0, 0, 255)
        cv2.putText(frame, str(lights_indicator), (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*6)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
    
    
    if current_tab == 4:
        current_text = f"Time left: "
        width_target_current_text = 0.34*width_frame
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
        width_original_text = width_current_text
        height_original_text = height_current_text
        thickness_current_text = round(fontscale_current_text*2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        current_text_color = text_color
        if route_speed_kmh >= route_speedlimit_kmh + 0.5:
            current_text_color = (0, 127, 255)
        if route_speed_kmh >= route_speedlimit_kmh + 3:
            current_text_color = (0, 0, 255)
        route_distance_left_str = str(round(route_distance_left, 1)) + ".0" if "." not in str(round(route_distance_left, 1)) else str(round(route_distance_left, 1))
        route_speedlimit_str = str(round(route_speedlimit, 1)) + ".0" if "." not in str(round(route_speedlimit, 1)) else str(round(route_speedlimit, 1))
        cv2.putText(frame, current_text, (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(f"{time_route_left_hours_str}:{time_route_left_minutes_str}:{time_route_left_seconds_str}", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, f"{time_route_left_hours_str}:{time_route_left_minutes_str}:{time_route_left_seconds_str}", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Real time left: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(f"{time_route_left_hours_real_str}:{time_route_left_minutes_real_str}:{time_route_left_seconds_real_str}", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        cv2.putText(frame, f"{time_route_left_hours_real_str}:{time_route_left_minutes_real_str}:{time_route_left_seconds_real_str}", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Distance left: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        if settings_use_imperial_system == False:
            textsize_current_text, _ = cv2.getTextSize(f"{route_distance_left_str}Km", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{route_distance_left_str}Km", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        else:
            textsize_current_text, _ = cv2.getTextSize(f"{route_distance_left_str}Mi", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{route_distance_left_str}Mi", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*3)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Speed limit: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*4.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        if settings_use_imperial_system == False:
            textsize_current_text, _ = cv2.getTextSize(f"{route_speedlimit_str}Km/h", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{route_speedlimit_str}Km/h", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*4.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
        else:
            textsize_current_text, _ = cv2.getTextSize(f"{route_speedlimit_str}Mph", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
            width_current_text, height_current_text = textsize_current_text
            cv2.putText(frame, f"{route_speedlimit_str}Mph", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_current_text/2+height_original_text*4.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_text_color, thickness_current_text)
        cv2.putText(frame, "Destination: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*6)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(f"{route_destination}", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        if width_current_text > 0.4*width_frame:
            current_text = f"{route_destination}"
            width_target_current_text = 0.4*width_frame
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
            current_text_color = text_color
            if route_speed_kmh >= route_speedlimit_kmh + 0.5:
                current_text_color = (0, 127, 255)
            if route_speed_kmh >= route_speedlimit_kmh + 3:
                current_text_color = (0, 0, 255)
        cv2.putText(frame, f"{route_destination}", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_original_text/2+height_original_text*6)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
    
    
    if current_tab == 5:
        current_text = f"Truck: "
        width_target_current_text = 0.225*width_frame
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
        width_original_text = width_current_text
        height_original_text = height_current_text
        thickness_current_text = round(fontscale_current_text*2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        fontscale_original_text = fontscale_current_text
        thickness_original_text = thickness_current_text
        current_text_color = text_color
        if route_speed_kmh >= route_speedlimit_kmh + 0.5:
            current_text_color = (0, 127, 255)
        if route_speed_kmh >= route_speedlimit_kmh + 3:
            current_text_color = (0, 0, 255)
        cv2.putText(frame, current_text, (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        textsize_current_text, _ = cv2.getTextSize(f"{truck_name}", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        if width_current_text > 0.58*width_frame:
            current_text = f"{truck_name}"
            width_target_current_text = 0.58*width_frame
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
            current_text_color = text_color
            if route_speed_kmh >= route_speedlimit_kmh + 0.5:
                current_text_color = (0, 127, 255)
            if route_speed_kmh >= route_speedlimit_kmh + 3:
                current_text_color = (0, 0, 255)
        cv2.putText(frame, f"{truck_name}", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_original_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
        cv2.putText(frame, "Cargo: ", (round(0.1*width_frame), round(0.2*height_frame+height_current_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_original_text, text_color, thickness_original_text)
        textsize_current_text, _ = cv2.getTextSize(f"{truck_cargo}", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, thickness_current_text)
        width_current_text, height_current_text = textsize_current_text
        if width_current_text > 0.565*width_frame:
            current_text = f"{truck_cargo}"
            width_target_current_text = 0.565*width_frame
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
            current_text_color = text_color
            if route_speed_kmh >= route_speedlimit_kmh + 0.5:
                current_text_color = (0, 127, 255)
            if route_speed_kmh >= route_speedlimit_kmh + 3:
                current_text_color = (0, 0, 255)
        cv2.putText(frame, f"{truck_cargo}", (round(0.9*width_frame-width_current_text), round(0.2*height_frame+height_original_text/2+height_original_text*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)


    if look_for_trucksimapi == True:
        if "TruckSimAPI" not in settings.GetSettings("Plugins", "Enabled"):
            frame = frame_original
            current_text = f"Enable TruckSimAPI"
            width_target_current_text = 0.8*width_frame
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
            width_original_text = width_current_text
            height_original_text = height_current_text
            thickness_current_text = round(fontscale_current_text*2)
            if thickness_current_text <= 0:
                thickness_current_text = 1
            current_text_color = text_color
            cv2.putText(frame, current_text, (round(0.5*width_frame-width_original_text/2), round(0.5*height_frame+height_original_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, text_color, thickness_current_text)
            

    cv2.namedWindow(name_window, cv2.WINDOW_NORMAL)
    cv2.imshow(name_window, frame)
    if resize_frame == True:
        cv2.resizeWindow(name_window, width_frame, height_frame)
        cv2.setWindowProperty(name_window, cv2.WND_PROP_TOPMOST, 1)

    return data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    LoadSettings()
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

        def UpdateSettings(self):
            self.graph_update_time_fuel.set(self.graph_update_time_fuel_Slider.get())
            self.graph_update_time_engine.set(self.graph_update_time_engine_Slider.get())
        
        def exampleFunction(self):
            try:
                self.root.destroy() 
            except: pass
            
            self.root = tk.Canvas(self.master, width=800, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(0) 
            self.root.pack_propagate(0)
            
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            colorsFrame = ttk.Frame(notebook)
            colorsFrame.pack()
            FuelTabFrame = ttk.Frame(notebook)
            FuelTabFrame.pack()
            EngineTabFrame = ttk.Frame(notebook)
            EngineTabFrame.pack()
            
            generalFrame.columnconfigure(0, weight=1)
            generalFrame.columnconfigure(1, weight=1)
            generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            colorsFrame.columnconfigure(0, weight=1)
            colorsFrame.columnconfigure(1, weight=1)
            colorsFrame.columnconfigure(2, weight=1)
            colorsFrame.columnconfigure(3, weight=1)
            colorsFrame.columnconfigure(4, weight=1)
            helpers.MakeLabel(colorsFrame, "Color Settings", 0, 0, font=("Robot", 12, "bold"), columnspan=5)

            FuelTabFrame.columnconfigure(0, weight=1)
            FuelTabFrame.columnconfigure(1, weight=1)
            FuelTabFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(FuelTabFrame, "Fuel Tab", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            EngineTabFrame.columnconfigure(0, weight=1)
            EngineTabFrame.columnconfigure(1, weight=1)
            EngineTabFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(EngineTabFrame, "Engine Tab", 0, 0, font=("Robot", 12, "bold"), columnspan=3)
            
            notebook.add(generalFrame, text=Translate("General"))
            notebook.add(colorsFrame, text=Translate("Color Settings"))
            notebook.add(FuelTabFrame, text=Translate("Fuel Tab"))
            notebook.add(EngineTabFrame, text=Translate("Engine Tab"))
            
            ttk.Button(self.root, text="Save", command=self.save, width=15).pack(anchor="center", pady=6)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()

            helpers.MakeEmptyLine(generalFrame, 1, 0)
            helpers.MakeCheckButton(generalFrame, "Show the fuel and engine graphs.", "TruckStats", "show_graphs", 2, 0, width=100)
            helpers.MakeCheckButton(generalFrame, "Use Imperial Units instead of Metric Units.\n(Miles instead of Kilometers, Mph instead of Km/h, Fahrenheit instead of Celsius and Gallons instead of Liters)", "TruckStats", "use_imperial_system", 3, 0, width=100)
            helpers.MakeCheckButton(generalFrame, "Use US Gallons.", "TruckStats", "use_us_gallons", 4, 0, width=100)
            helpers.MakeCheckButton(generalFrame, "Reset the in-game trip info if you reach your destination.", "TruckStats", "reset_trip", 5, 0, width=100)
            helpers.MakeCheckButton(generalFrame, "Reset the fuel graph if you reach your destination.", "TruckStats", "reset_fuelgraph", 6, 0, width=100)
            helpers.MakeCheckButton(generalFrame, "Reset the engine graph if you reach your destination.", "TruckStats", "reset_enginegraph", 7, 0, width=100)
            helpers.MakeLabel(generalFrame, "Note: If you close the TruckStats window, it will save the location of the window.", 8, 0, sticky="w")

            
            self.open_tab_color_r = helpers.MakeComboEntry(colorsFrame, "Open Tab Color R", "TruckStats", "open_tab_color_r", 3, 0, labelwidth=17, width=7, sticky="w",labelPadX=40, translate=False)
            self.open_tab_color_g = helpers.MakeComboEntry(colorsFrame, "Open Tab Color G", "TruckStats", "open_tab_color_g", 4, 0, labelwidth=17, width=7, sticky="w",labelPadX=40, translate=False)
            self.open_tab_color_b = helpers.MakeComboEntry(colorsFrame, "Open Tab Color B", "TruckStats", "open_tab_color_b", 5, 0, labelwidth=17, width=7, sticky="w",labelPadX=40, translate=False)

            self.open_tab_hover_color_r = helpers.MakeComboEntry(colorsFrame, "Open Tab Hover Color R", "TruckStats", "open_tab_hover_color_r", 3, 3, labelwidth=22, width=7, sticky="w", translate=False)
            self.open_tab_hover_color_g = helpers.MakeComboEntry(colorsFrame, "Open Tab Hover Color G", "TruckStats", "open_tab_hover_color_g", 4, 3, labelwidth=22, width=7, sticky="w", translate=False)
            self.open_tab_hover_color_b = helpers.MakeComboEntry(colorsFrame, "Open Tab Hover Color B", "TruckStats", "open_tab_hover_color_b", 5, 3, labelwidth=22, width=7, sticky="w", translate=False)

            helpers.MakeEmptyLine(colorsFrame, 6, 0)

            self.closed_tab_color_r = helpers.MakeComboEntry(colorsFrame, "Closed Tab Color R", "TruckStats", "closed_tab_color_r", 7, 0, labelwidth=17, width=7, sticky="w",labelPadX=40, translate=False)
            self.closed_tab_color_g = helpers.MakeComboEntry(colorsFrame, "Closed Tab Color G", "TruckStats", "closed_tab_color_g", 8, 0, labelwidth=17, width=7, sticky="w",labelPadX=40, translate=False)
            self.closed_tab_color_b = helpers.MakeComboEntry(colorsFrame, "Closed Tab Color B", "TruckStats", "closed_tab_color_b", 9, 0, labelwidth=17, width=7, sticky="w",labelPadX=40, translate=False)

            self.closed_tab_hover_color_r = helpers.MakeComboEntry(colorsFrame, "Closed Tab Hover Color R", "TruckStats", "closed_tab_hover_color_r", 7, 3, labelwidth=22, width=7, sticky="w", translate=False)
            self.closed_tab_hover_color_g = helpers.MakeComboEntry(colorsFrame, "Closed Tab Hover Color G", "TruckStats", "closed_tab_hover_color_g", 8, 3, labelwidth=22, width=7, sticky="w", translate=False)
            self.closed_tab_hover_color_b = helpers.MakeComboEntry(colorsFrame, "Closed Tab Hover Color B", "TruckStats", "closed_tab_hover_color_b", 9, 3, labelwidth=22, width=7, sticky="w", translate=False)

            helpers.MakeButton(colorsFrame, "Blue Preset", self.load_blue_color_preset, 10, 0)
            helpers.MakeButton(colorsFrame, "Green Preset", self.load_green_color_preset, 11, 0)
            helpers.MakeButton(colorsFrame, "Red Preset", self.load_red_color_preset, 10, 1)
            helpers.MakeButton(colorsFrame, "Gray Preset", self.load_gray_color_preset, 11, 1)

            helpers.MakeButton(colorsFrame, "Reset To Default", self.reset_colors_to_default, 11, 4)


            helpers.MakeEmptyLine(FuelTabFrame, 1, 0)
            helpers.MakeCheckButton(FuelTabFrame, "Show the Values in green instead of white, if enough fuel is left.", "TruckStats", "show_in_green", 2, 0, width=85)
            helpers.MakeEmptyLine(FuelTabFrame, 3, 0)
            helpers.MakeLabel(FuelTabFrame, "Value to be displayed in the graph:", 4, 0, sticky="w")
            value_to_graph_fuel = tk.StringVar() 
            previous_value_to_graph_fuel = settings.GetSettings("TruckStats", "fuel_value_to_graph")
            if previous_value_to_graph_fuel == "fuel_current":
                value_to_graph_fuel.set("fuel_current")
            if previous_value_to_graph_fuel == "fuel_percentage":
                value_to_graph_fuel.set("fuel_percentage")
            if previous_value_to_graph_fuel == "range":
                value_to_graph_fuel.set("range")
            if previous_value_to_graph_fuel == "avg_consumption":
                value_to_graph_fuel.set("avg_consumption")
            def value_to_graph_fuel_selection():
                self.value_to_graph_fuel = value_to_graph_fuel.get()
            fuel_current_radio_button = ttk.Radiobutton(FuelTabFrame, text="Fuel", variable=value_to_graph_fuel, value="fuel_current", command=value_to_graph_fuel_selection)
            fuel_current_radio_button.grid(row=5, column=0, sticky="w")
            fuel_percentage_radio_button = ttk.Radiobutton(FuelTabFrame, text="Fuel Percentage", variable=value_to_graph_fuel, value="fuel_percentage", command=value_to_graph_fuel_selection)
            fuel_percentage_radio_button.grid(row=6, column=0, sticky="w")
            range_radio_button = ttk.Radiobutton(FuelTabFrame, text="Range", variable=value_to_graph_fuel, value="range", command=value_to_graph_fuel_selection)
            range_radio_button.grid(row=7, column=0, sticky="w")
            avg_consumption_radio_button = ttk.Radiobutton(FuelTabFrame, text="Average Fuel Consumption", variable=value_to_graph_fuel, value="avg_consumption", command=value_to_graph_fuel_selection)
            avg_consumption_radio_button.grid(row=8, column=0, sticky="w")
            value_to_graph_fuel_selection()
            self.graph_update_time_fuel_Slider = tk.Scale(FuelTabFrame, from_=1, to=300, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.graph_update_time_fuel_Slider.set(settings.GetSettings("TruckStats", "fuel_value_history_adder", 60))
            self.graph_update_time_fuel_Slider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.graph_update_time_fuel = helpers.MakeComboEntry(FuelTabFrame, "Graph Refresh\nRate in Seconds", "TruckStats", "fuel_value_history_adder", 9, 0, width=13)


            helpers.MakeLabel(EngineTabFrame, "                                                                                                                                                          ", 2, 0, translate=False)
            helpers.MakeLabel(EngineTabFrame, "Value to be displayed in the graph:", 3, 0, sticky="w")
            value_to_graph_engine = tk.StringVar() 
            previous_value_to_graph_engine = settings.GetSettings("TruckStats", "engine_value_to_graph")
            if previous_value_to_graph_engine == "rpm":
                value_to_graph_engine.set("rpm")
            if previous_value_to_graph_engine == "throttle":
                value_to_graph_engine.set("throttle")
            if previous_value_to_graph_engine == "oil_temperature":
                value_to_graph_engine.set("oil_temperature")
            if previous_value_to_graph_engine == "oil_pressure":
                value_to_graph_engine.set("oil_pressure")
            def value_to_graph_engine_selection():
                self.value_to_graph_engine = value_to_graph_engine.get()
            engine_current_radio_button = ttk.Radiobutton(EngineTabFrame, text="RPM", variable=value_to_graph_engine, value="rpm", command=value_to_graph_engine_selection)
            engine_current_radio_button.grid(row=4, column=0, sticky="w")
            engine_percentage_radio_button = ttk.Radiobutton(EngineTabFrame, text="Throttle", variable=value_to_graph_engine, value="throttle", command=value_to_graph_engine_selection)
            engine_percentage_radio_button.grid(row=5, column=0, sticky="w")
            range_radio_button = ttk.Radiobutton(EngineTabFrame, text="Oil Temperature", variable=value_to_graph_engine, value="oil_temperature", command=value_to_graph_engine_selection)
            range_radio_button.grid(row=6, column=0, sticky="w")
            avg_consumption_radio_button = ttk.Radiobutton(EngineTabFrame, text="Oil Pressure", variable=value_to_graph_engine, value="oil_pressure", command=value_to_graph_engine_selection)
            avg_consumption_radio_button.grid(row=7, column=0, sticky="w")
            value_to_graph_engine_selection()
            self.graph_update_time_engine_Slider = tk.Scale(EngineTabFrame, from_=1, to=300, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.graph_update_time_engine_Slider.set(settings.GetSettings("TruckStats", "engine_value_history_adder", 60))
            self.graph_update_time_engine_Slider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.graph_update_time_engine = helpers.MakeComboEntry(EngineTabFrame, "Graph Refresh\nRate in Seconds", "TruckStats", "engine_value_history_adder", 9, 0, width=13)


        def save(self):

            try:
                self.open_tab_color_r.get()
            except:
                self.open_tab_color_r.set(255)
            try:
                self.open_tab_color_g.get()
            except:
                self.open_tab_color_g.set(127)
            try:
                self.open_tab_color_b.get()
            except:
                self.open_tab_color_b.set(0)
            try:
                self.open_tab_hover_color_r.get()
            except:
                self.open_tab_hover_color_r.set(255)
            try:
                self.open_tab_hover_color_g.get()
            except:
                self.open_tab_hover_color_g.set(157)
            try:
                self.open_tab_hover_color_b.get()
            except:
                self.open_tab_hover_color_b.set(30)
            try:
                self.closed_tab_color_r.get()
            except:
                self.closed_tab_color_r.set(100)
            try:
                self.closed_tab_color_g.get()
            except:
                self.closed_tab_color_g.set(100)
            try:
                self.closed_tab_color_b.get()
            except:
                self.closed_tab_color_b.set(100)
            try:
                self.closed_tab_hover_color_r.get()
            except:
                self.closed_tab_hover_color_r.set(130)
            try:
                self.closed_tab_hover_color_g.get()
            except:
                self.closed_tab_hover_color_g.set(130)
            try:
                self.closed_tab_hover_color_b.get()
            except:
                self.closed_tab_hover_color_b.set(130)
            if not (0 <= self.open_tab_color_r.get() <= 255):
                self.open_tab_color_r.set(255)
            if not (0 <= self.open_tab_color_g.get() <= 255):
                self.open_tab_color_g.set(127)
            if not (0 <= self.open_tab_color_b.get() <= 255):
                self.open_tab_color_b.set(0)
            if not (0 <= self.open_tab_hover_color_r.get() <= 255):
                self.open_tab_hover_color_r.set(255)
            if not (0 <= self.open_tab_hover_color_g.get() <= 255):
                self.open_tab_hover_color_g.set(157)
            if not (0 <= self.open_tab_hover_color_b.get() <= 255):
                self.open_tab_hover_color_b.set(30)
            if not (0 <= self.closed_tab_color_r.get() <= 255):
                self.closed_tab_color_r.set(100)
            if not (0 <= self.closed_tab_color_g.get() <= 255):
                self.closed_tab_color_g.set(100)
            if not (0 <= self.closed_tab_color_b.get() <= 255):
                self.closed_tab_color_b.set(100)
            if not (0 <= self.closed_tab_hover_color_r.get() <= 255):
                self.closed_tab_hover_color_r.set(130)
            if not (0 <= self.closed_tab_hover_color_g.get() <= 255):
                self.closed_tab_hover_color_g.set(130)
            if not (0 <= self.closed_tab_hover_color_b.get() <= 255):
                self.closed_tab_hover_color_b.set(130)
            settings.CreateSettings("TruckStats", "open_tab_color_r", self.open_tab_color_r.get())
            settings.CreateSettings("TruckStats", "open_tab_color_g", self.open_tab_color_g.get())
            settings.CreateSettings("TruckStats", "open_tab_color_b", self.open_tab_color_b.get())
            settings.CreateSettings("TruckStats", "open_tab_hover_color_r", self.open_tab_hover_color_r.get())
            settings.CreateSettings("TruckStats", "open_tab_hover_color_g", self.open_tab_hover_color_g.get())
            settings.CreateSettings("TruckStats", "open_tab_hover_color_b", self.open_tab_hover_color_b.get())
            settings.CreateSettings("TruckStats", "closed_tab_color_r", self.closed_tab_color_r.get())
            settings.CreateSettings("TruckStats", "closed_tab_color_g", self.closed_tab_color_g.get())
            settings.CreateSettings("TruckStats", "closed_tab_color_b", self.closed_tab_color_b.get())
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_r", self.closed_tab_hover_color_r.get())
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_g", self.closed_tab_hover_color_g.get())
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_b", self.closed_tab_hover_color_b.get())
            
            settings.CreateSettings("TruckStats", "fuel_value_to_graph", self.value_to_graph_fuel)
            settings.CreateSettings("TruckStats", "fuel_value_history_adder", self.graph_update_time_fuel_Slider.get())
            settings.CreateSettings("TruckStats", "engine_value_to_graph", self.value_to_graph_engine)
            settings.CreateSettings("TruckStats", "engine_value_history_adder", self.graph_update_time_engine_Slider.get())
            LoadSettings()

        def reset_colors_to_default(self):
            settings.CreateSettings("TruckStats", "open_tab_color_r", 255)
            settings.CreateSettings("TruckStats", "open_tab_color_g", 127)
            settings.CreateSettings("TruckStats", "open_tab_color_b", 0)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_r", 255)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_g", 157)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_b", 30)
            settings.CreateSettings("TruckStats", "closed_tab_color_r", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_g", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_b", 100)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_r", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_g", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_b", 130)
            self.open_tab_color_r.set(255)
            self.open_tab_color_g.set(127)
            self.open_tab_color_b.set(0)
            self.open_tab_hover_color_r.set(255)
            self.open_tab_hover_color_g.set(157)
            self.open_tab_hover_color_b.set(30)
            self.closed_tab_color_r.set(100)
            self.closed_tab_color_g.set(100)
            self.closed_tab_color_b.set(100)
            self.closed_tab_hover_color_r.set(130)
            self.closed_tab_hover_color_g.set(130)
            self.closed_tab_hover_color_b.set(130)
            LoadSettings()

        def load_blue_color_preset(self):
            settings.CreateSettings("TruckStats", "open_tab_color_r", 0)
            settings.CreateSettings("TruckStats", "open_tab_color_g", 127)
            settings.CreateSettings("TruckStats", "open_tab_color_b", 255)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_r", 30)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_g", 157)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_b", 255)
            settings.CreateSettings("TruckStats", "closed_tab_color_r", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_g", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_b", 100)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_r", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_g", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_b", 130)
            self.open_tab_color_r.set(0)
            self.open_tab_color_g.set(127)
            self.open_tab_color_b.set(255)
            self.open_tab_hover_color_r.set(30)
            self.open_tab_hover_color_g.set(157)
            self.open_tab_hover_color_b.set(255)
            self.closed_tab_color_r.set(100)
            self.closed_tab_color_g.set(100)
            self.closed_tab_color_b.set(100)
            self.closed_tab_hover_color_r.set(130)
            self.closed_tab_hover_color_g.set(130)
            self.closed_tab_hover_color_b.set(130)
            LoadSettings()

        def load_green_color_preset(self):
            settings.CreateSettings("TruckStats", "open_tab_color_r", 0)
            settings.CreateSettings("TruckStats", "open_tab_color_g", 175)
            settings.CreateSettings("TruckStats", "open_tab_color_b", 0)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_r", 30)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_g", 205)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_b", 30)
            settings.CreateSettings("TruckStats", "closed_tab_color_r", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_g", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_b", 100)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_r", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_g", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_b", 130)
            self.open_tab_color_r.set(0)
            self.open_tab_color_g.set(175)
            self.open_tab_color_b.set(0)
            self.open_tab_hover_color_r.set(30)
            self.open_tab_hover_color_g.set(205)
            self.open_tab_hover_color_b.set(30)
            self.closed_tab_color_r.set(100)
            self.closed_tab_color_g.set(100)
            self.closed_tab_color_b.set(100)
            self.closed_tab_hover_color_r.set(130)
            self.closed_tab_hover_color_g.set(130)
            self.closed_tab_hover_color_b.set(130)
            LoadSettings()

        def load_red_color_preset(self):
            settings.CreateSettings("TruckStats", "open_tab_color_r", 175)
            settings.CreateSettings("TruckStats", "open_tab_color_g", 0)
            settings.CreateSettings("TruckStats", "open_tab_color_b", 0)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_r", 205)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_g", 30)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_b", 30)
            settings.CreateSettings("TruckStats", "closed_tab_color_r", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_g", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_b", 100)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_r", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_g", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_b", 130)
            self.open_tab_color_r.set(175)
            self.open_tab_color_g.set(0)
            self.open_tab_color_b.set(0)
            self.open_tab_hover_color_r.set(205)
            self.open_tab_hover_color_g.set(30)
            self.open_tab_hover_color_b.set(30)
            self.closed_tab_color_r.set(100)
            self.closed_tab_color_g.set(100)
            self.closed_tab_color_b.set(100)
            self.closed_tab_hover_color_r.set(130)
            self.closed_tab_hover_color_g.set(130)
            self.closed_tab_hover_color_b.set(130)
            LoadSettings()

        def load_gray_color_preset(self):
            settings.CreateSettings("TruckStats", "open_tab_color_r", 150)
            settings.CreateSettings("TruckStats", "open_tab_color_g", 150)
            settings.CreateSettings("TruckStats", "open_tab_color_b", 150)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_r", 180)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_g", 180)
            settings.CreateSettings("TruckStats", "open_tab_hover_color_b", 180)
            settings.CreateSettings("TruckStats", "closed_tab_color_r", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_g", 100)
            settings.CreateSettings("TruckStats", "closed_tab_color_b", 100)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_r", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_g", 130)
            settings.CreateSettings("TruckStats", "closed_tab_hover_color_b", 130)
            self.open_tab_color_r.set(150)
            self.open_tab_color_g.set(150)
            self.open_tab_color_b.set(150)
            self.open_tab_hover_color_r.set(180)
            self.open_tab_hover_color_g.set(180)
            self.open_tab_hover_color_b.set(180)
            self.closed_tab_color_r.set(100)
            self.closed_tab_color_g.set(100)
            self.closed_tab_color_b.set(100)
            self.closed_tab_hover_color_r.set(130)
            self.closed_tab_hover_color_g.set(130)
            self.closed_tab_hover_color_b.set(130)
            LoadSettings()

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)