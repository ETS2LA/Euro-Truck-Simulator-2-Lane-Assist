from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.variables as variables
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls

if variables.OS == "nt":
    from ctypes import windll, byref, sizeof, c_int
    import win32gui, win32con
import numpy as np
import ctypes
import mouse
import time
import cv2
import mss

runner:PluginRunner = None

controls.RegisterKeybind("Switch to next TruckStats tab",
                         notBoundInfo="You can switch to the next tab with this keybind.",
                         description="You can switch to the next tab with this keybind.")

sct = mss.mss()
monitor = sct.monitors[(settings.Get("TrafficLightDetection", ["ScreenCapture", "display"], 0) + 1)]
screen_x = monitor["left"]
screen_y = monitor["top"]
width_screen = monitor["width"]
height_screen = monitor["height"]

def Initialize():
    global TruckSimAPI

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

    global switch_next_tab_pressed
    global last_switch_next_tab_pressed

    global settings_allow_graphs

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
    
    TruckSimAPI = runner.modules.TruckSimAPI

    name_window = "TruckStats"
    current_tab = settings.Get("TruckStats", "current_tab", 1)
    text_color = (255,255,255)

    width_frame = settings.Get("TruckStats", "width_frame", round(height_screen/2.57))
    height_frame = settings.Get("TruckStats", "height_frame", round(height_screen/4.9))
    last_width_frame = width_frame
    last_height_frame = height_frame
    frame_original = np.zeros((height_frame, width_frame, 3), dtype=np.uint8)

    settings_show_graphs = settings.Get("TruckStats", "show_graphs", True)
    settings_use_imperial_system = settings.Get("TruckStats", "use_imperial_system", False)
    settings_use_us_gallons = settings.Get("TruckStats", "use_us_gallons", False)
    settings_fuel_tab_color = settings.Get("TruckStats", "show_in_green", True)
    settings_fuel_value_to_graph = settings.Get("TruckStats", "fuel_value_to_graph", "fuel_current")
    settings_engine_value_to_graph = settings.Get("TruckStats", "engine_value_to_graph", "rpm")

    switch_next_tab_pressed = False
    last_switch_next_tab_pressed = False

    settings_allow_graphs = True

    fuel_last_avg_consumption = 0

    fuel_value_history = []
    fuel_value_history_adder = settings.Get("TruckStats", "fuel_value_history_adder", 60)
    fuel_value_history_time = time.time() + 1
    fuel_value_history_count = 0

    engine_value_history = []
    engine_value_history_adder = settings.Get("TruckStats", "engine_value_history_adder", 60)
    engine_value_history_time = time.time() + 1
    engine_value_history_count = 0

    reset_trip = settings.Get("TruckStats", "reset_trip", False)
    reset_fuelgraph = settings.Get("TruckStats", "reset_fuelgraph", False)
    reset_enginegraph = settings.Get("TruckStats", "reset_enginegraph", False)
    last_route_distance_left = 0

    open_tab_color_r = settings.Get("TruckStats", "open_tab_color_r")
    if open_tab_color_r == None or not isinstance(open_tab_color_r, int) or not (0 <= open_tab_color_r <= 255):
        settings.Set("TruckStats", "open_tab_color_r", 255)
        open_tab_color_r = 255
    open_tab_color_g = settings.Get("TruckStats", "open_tab_color_g")
    if open_tab_color_g == None or not isinstance(open_tab_color_g, int) or not (0 <= open_tab_color_g <= 255):
        settings.Set("TruckStats", "open_tab_color_g", 127)
        open_tab_color_g = 127
    open_tab_color_b = settings.Get("TruckStats", "open_tab_color_b")
    if open_tab_color_b == None or not isinstance(open_tab_color_b, int) or not (0 <= open_tab_color_b <= 255):
        settings.Set("TruckStats", "open_tab_color_b", 0)
        open_tab_color_b = 0
    open_tab_color = (open_tab_color_b, open_tab_color_g, open_tab_color_r)
    open_tab_hover_color_r = settings.Get("TruckStats", "open_tab_hover_color_r")
    if open_tab_hover_color_r == None or not isinstance(open_tab_hover_color_r, int) or not (0 <= open_tab_hover_color_r <= 255):
        settings.Set("TruckStats", "open_tab_hover_color_r", 255)
        open_tab_hover_color_r = 255
    open_tab_hover_color_g = settings.Get("TruckStats", "open_tab_hover_color_g")
    if open_tab_hover_color_g == None or not isinstance(open_tab_hover_color_g, int) or not (0 <= open_tab_hover_color_g <= 255):
        settings.Set("TruckStats", "open_tab_hover_color_g", 157)
        open_tab_hover_color_g = 157
    open_tab_hover_color_b = settings.Get("TruckStats", "open_tab_hover_color_b")
    if open_tab_hover_color_b == None or not isinstance(open_tab_hover_color_b, int) or not (0 <= open_tab_hover_color_b <= 255):
        settings.Set("TruckStats", "open_tab_hover_color_b", 30)
        open_tab_hover_color_b = 30
    open_tab_hover_color = (open_tab_hover_color_b, open_tab_hover_color_g, open_tab_hover_color_r)
    closed_tab_color_r = settings.Get("TruckStats", "closed_tab_color_r")
    if closed_tab_color_r == None or not isinstance(closed_tab_color_r, int) or not (0 <= closed_tab_color_r <= 255):
        settings.Set("TruckStats", "closed_tab_color_r", 100)
        closed_tab_color_r = 100
    closed_tab_color_g = settings.Get("TruckStats", "closed_tab_color_g")
    if closed_tab_color_g == None or not isinstance(closed_tab_color_g, int) or not (0 <= closed_tab_color_g <= 255):
        settings.Set("TruckStats", "closed_tab_color_g", 100)
        closed_tab_color_g = 100
    closed_tab_color_b = settings.Get("TruckStats", "closed_tab_color_b")
    if closed_tab_color_b == None or not isinstance(closed_tab_color_b, int) or not (0 <= closed_tab_color_b <= 255):
        settings.Set("TruckStats", "closed_tab_color_b", 100)
        closed_tab_color_b = 100
    closed_tab_color = (closed_tab_color_b, closed_tab_color_g, closed_tab_color_r)
    closed_tab_hover_color_r = settings.Get("TruckStats", "closed_tab_hover_color_r")
    if closed_tab_hover_color_r == None or not isinstance(closed_tab_hover_color_r, int) or not (0 <= closed_tab_hover_color_r <= 255):
        settings.Set("TruckStats", "closed_tab_hover_color_r", 130)
        closed_tab_hover_color_r = 130
    closed_tab_hover_color_g = settings.Get("TruckStats", "closed_tab_hover_color_g")
    if closed_tab_hover_color_g == None or not isinstance(closed_tab_hover_color_g, int) or not (0 <= closed_tab_hover_color_g <= 255):
        settings.Set("TruckStats", "closed_tab_hover_color_g", 130)
        closed_tab_hover_color_g = 130
    closed_tab_hover_color_b = settings.Get("TruckStats", "closed_tab_hover_color_b")
    if closed_tab_hover_color_b == None or not isinstance(closed_tab_hover_color_b, int) or not (0 <= closed_tab_hover_color_b <= 255):
        settings.Set("TruckStats", "closed_tab_hover_color_b", 130)
        closed_tab_hover_color_b = 130
    closed_tab_hover_color = (closed_tab_hover_color_b, closed_tab_hover_color_g, closed_tab_hover_color_r)


def plugin():

    data = {}
    data["api"] = TruckSimAPI.run(Fallback=False)

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

    global switch_next_tab_pressed
    global last_switch_next_tab_pressed

    global settings_allow_graphs

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
            if width_frame >= 50 and height_frame >= 50:
                settings_allow_graphs = True
                frame_original = np.zeros((height_frame, width_frame, 3), dtype=np.uint8)
                settings.Set("TruckStats", "width_frame", width_frame)
                settings.Set("TruckStats", "height_frame", height_frame)
            else:
                settings_allow_graphs = False
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

    switch_next_tab_pressed = controls.GetKeybindValue("Switch to next TruckStats tab")
    if switch_next_tab_pressed == True and last_switch_next_tab_pressed == False:
        current_tab += 1
        if current_tab > 5:
            current_tab = 1
        settings.Set("TruckStats", "current_tab", current_tab)
    last_switch_next_tab_pressed = switch_next_tab_pressed

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
        route_destination = data["api"]["configString"]["cityDstId"]
        route_destination = route_destination.capitalize()

        truck_name = data["api"]["configString"]["truckName"]
        truck_cargo = data["api"]["configString"]["cargo"]

    except:

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
                settings.Set("TruckStats", "current_tab", 1)
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
                settings.Set("TruckStats", "current_tab", 2)
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
                settings.Set("TruckStats", "current_tab", 3)
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
                settings.Set("TruckStats", "current_tab", 4)
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
                settings.Set("TruckStats", "current_tab", 5)
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
        if settings_show_graphs == True and settings_allow_graphs == True:
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
        if settings_show_graphs == True and settings_allow_graphs == True:
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


    cv2.imshow(name_window, frame)
    cv2.waitKey(1)

    if resize_frame == True:
        cv2.namedWindow(name_window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name_window, width_frame, height_frame)
        cv2.setWindowProperty(name_window, cv2.WND_PROP_TOPMOST, 1)

        hwnd = win32gui.FindWindow(None, name_window)
        windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))

        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(None, f"{variables.PATH}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)

        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)

    return data