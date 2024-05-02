from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.variables as variables
import ETS2LA.backend.settings as settings

import numpy as np
import threading
import traceback
import socket
import ctypes
import math
import cv2
import mss
import os

runner:PluginRunner = None

sct = mss.mss()
monitor = settings.Get("ScreenCapture", "display", 0)
monitor = sct.monitors[(monitor + 1)]
screen_width = monitor["width"]
screen_height = monitor["height"]

lower_red = np.array([200, 0, 0])
upper_red = np.array([255, 110, 110])
lower_green = np.array([0, 200, 0])
upper_green = np.array([150, 255, 230])
lower_yellow = np.array([200, 170, 50])
upper_yellow = np.array([255, 240, 170])

yolo_model_loaded = False

def LoadSettings():
    global min_rect_size
    global max_rect_size
    global width_height_ratio
    global circlepercent
    global maxcircleoffset
    global circleplusoffset
    global circleminusoffset
    global finalwindow
    global grayscalewindow
    global positionestimationwindow
    global anywindowopen
    global detectyellowlight
    global performancemode
    global advancedmode
    global windowscale
    global posestwindowscale
    global yolo_detection
    global yolo_showunconfirmed
    global yolo_model_loaded
    global yolo_model_str
    global yolo_model
    global coordinates
    global trafficlights
    global windowwidth
    global windowheight
    global reset_window
    global positionestimation_default_frame
    global positionestimation_topview
    global positionestimation_sideview
    global fov
    global x1
    global y1
    global x2
    global y2

    global rectsizefilter
    global widthheightratiofilter
    global pixelpercentagefilter
    global otherlightsofffilter
    global urr
    global urg
    global urb
    global lrr
    global lrg
    global lrb
    global uyr
    global uyg
    global uyb
    global lyr
    global lyg
    global lyb
    global ugr
    global ugg
    global ugb
    global lgr
    global lgg
    global lgb
    global lower_red_advanced
    global upper_red_advanced
    global lower_green_advanced
    global upper_green_advanced
    global lower_yellow_advanced
    global upper_yellow_advanced
    
    finalwindow = settings.Get("TrafficLightDetection", "finalwindow", True)
    grayscalewindow = settings.Get("TrafficLightDetection", "grayscalewindow", False)
    positionestimationwindow = settings.Get("TrafficLightDetection", "positionestimationwindow", False)
    detectyellowlight = settings.Get("TrafficLightDetection", "detectyellowlight", False)
    performancemode = settings.Get("TrafficLightDetection", "performancemode", True)
    advancedmode = settings.Get("TrafficLightDetection", "advancedmode", False)
    windowscale = float(settings.Get("TrafficLightDetection", "scale", 0.5))
    posestwindowscale = float(settings.Get("TrafficLightDetection", "posestscale", 0.5))
    x1 = settings.Get("TrafficLightDetection", "x1ofsc", 0)
    y1 = settings.Get("TrafficLightDetection", "y1ofsc", 0)
    x2 = settings.Get("TrafficLightDetection", "x2ofsc", screen_width-1)
    y2 = settings.Get("TrafficLightDetection", "y2ofsc", round(screen_height/1.5)-1)

    if x1 >= x2:
        if screen_width-x1 > screen_width-x2:
            x1 = x2-1
        else:
            x2 = x1+1
    if y1 >= y2:
        if screen_height-y1 > screen_height-y2:
            y1 = y2-1
        else:
            y2 = y1+1

    windowwidth = x2-x1
    windowheight = y2-y1

    rectsizefilter = settings.Get("TrafficLightDetection", "rectsizefilter", True)
    widthheightratiofilter = settings.Get("TrafficLightDetection", "widthheightratiofilter", True)
    pixelpercentagefilter = settings.Get("TrafficLightDetection", "pixelpercentagefilter", True)
    otherlightsofffilter = settings.Get("TrafficLightDetection", "otherlightsofffilter", True)

    yolo_detection = settings.Get("TrafficLightDetection", "yolo_detection", True)
    yolo_showunconfirmed = settings.Get("TrafficLightDetection", "yolo_showunconfirmed", True)
    yolo_model_str = settings.Get("TrafficLightDetection", "yolo_model", "yolov5n")

    coordinates = []
    trafficlights = []

    if positionestimationwindow == True:
        if os.path.exists(variables.PATH + "assets/TrafficLightDetection/topview.png") and os.path.exists(variables.PATH + "assets/TrafficLightDetection/sideview.png"):
            positionestimation_topview = cv2.imread(variables.PATH + "assets/TrafficLightDetection/topview.png")
            positionestimation_sideview = cv2.imread(variables.PATH + "assets/TrafficLightDetection/sideview.png")
            positionestimation_default_frame = np.zeros((round(((screen_width-1)/2.5)*posestwindowscale), round((screen_width-1)*posestwindowscale), 3), np.uint8)
            pixel_per_meter = 25
            posest_zoom = (positionestimation_default_frame.shape[1] / 300) * pixel_per_meter
            temp = positionestimation_topview.copy()
            posest_x1 = 0.24 * positionestimation_default_frame.shape[1] - posest_zoom / 2
            posest_y1 = positionestimation_default_frame.shape[0] - posest_zoom * (temp.shape[0] / temp.shape[1])
            posest_x2 = 0.24 * positionestimation_default_frame.shape[1] + posest_zoom / 2
            posest_y2 = positionestimation_default_frame.shape[0]
            temp = cv2.resize(temp, ((round(posest_x2) - round(posest_x1)), (round(posest_y2) - round(posest_y1))))
            positionestimation_default_frame[round(posest_y1):round(posest_y2), round(posest_x1):round(posest_x2)] = temp
            temp = positionestimation_sideview.copy()
            posest_x1 = positionestimation_default_frame.shape[1] - posest_zoom
            posest_y1 = 0.7 * positionestimation_default_frame.shape[0] - posest_zoom * (temp.shape[0] / temp.shape[1]) * 0.5
            posest_x2 = positionestimation_default_frame.shape[1]
            posest_y2 = 0.7 * positionestimation_default_frame.shape[0] + posest_zoom * (temp.shape[0] / temp.shape[1]) * 0.5
            temp = cv2.resize(temp, ((round(posest_x2) - round(posest_x1)), (round(posest_y2) - round(posest_y1))))
            positionestimation_default_frame[round(posest_y1):round(posest_y2), round(posest_x1):round(posest_x2)] = temp
            cv2.line(positionestimation_default_frame, (round(positionestimation_default_frame.shape[1]/2), round(0.05*positionestimation_default_frame.shape[0])), (round(positionestimation_default_frame.shape[1]/2), round(0.95*positionestimation_default_frame.shape[0])), (50, 50, 50), round(positionestimation_default_frame.shape[1]/500) if round(positionestimation_default_frame.shape[1]/500) > 1 else 1)
        else:
            positionestimationwindow = False

    fov = settings.Get("TrafficLightDetection", "fov", 80)

    reset_window = True

    if advancedmode == False:
        min_rect_size = screen_width / 240
        max_rect_size = screen_width / 10
    else:
        min_rect_size = settings.Get("TrafficLightDetection", "minrectsize", round(screen_width / 240))
        max_rect_size = settings.Get("TrafficLightDetection", "maxrectsize", round(screen_width / 10))

    width_height_ratio = 0.2
    circlepercent = 0.785
    maxcircleoffset = 0.15
    circleplusoffset = circlepercent + maxcircleoffset
    circleminusoffset = circlepercent - maxcircleoffset

    if min_rect_size < 8:
        min_rect_size = 8

    if finalwindow == True or grayscalewindow == True:
        anywindowopen = True
    else:
        anywindowopen = False

    urr = settings.Get("TrafficLightDetection", "upperred_r")
    if urr == None or not isinstance(urr, int) or not (0 <= urr <= 255):
        settings.Set("TrafficLightDetection", "upperred_r", 255)
        urr = 255
    urg = settings.Get("TrafficLightDetection", "upperred_g")
    if urg == None or not isinstance(urg, int) or not (0 <= urg <= 255):
        settings.Set("TrafficLightDetection", "upperred_g", 110)
        urg = 110
    urb = settings.Get("TrafficLightDetection", "upperred_b")
    if urb == None or not isinstance(urb, int) or not (0 <= urb <= 255):
        settings.Set("TrafficLightDetection", "upperred_b", 110)
        urb = 110
    lrr = settings.Get("TrafficLightDetection", "lowerred_r")
    if lrr == None or not isinstance(lrr, int) or not (0 <= lrr <= 255):
        settings.Set("TrafficLightDetection", "lowerred_r", 200)
        lrr = 200
    lrg = settings.Get("TrafficLightDetection", "lowerred_g")
    if lrg == None or not isinstance(lrg, int) or not (0 <= lrg <= 255):
        settings.Set("TrafficLightDetection", "lowerred_g", 0)
        lrg = 0
    lrb = settings.Get("TrafficLightDetection", "lowerred_b")
    if lrb == None or not isinstance(lrb, int) or not (0 <= lrb <= 255):
        settings.Set("TrafficLightDetection", "lowerred_b", 0)
        lrb = 0
    uyr = settings.Get("TrafficLightDetection", "upperyellow_r")
    if uyr == None or not isinstance(uyr, int) or not (0 <= uyr <= 255):
        settings.Set("TrafficLightDetection", "upperyellow_r", 255)
        uyr = 255
    uyg = settings.Get("TrafficLightDetection", "upperyellow_g")
    if uyg == None or not isinstance(uyg, int) or not (0 <= uyg <= 255):
        settings.Set("TrafficLightDetection", "upperyellow_g", 240)
        uyg = 240
    uyb = settings.Get("TrafficLightDetection", "upperyellow_b")
    if uyb == None or not isinstance(uyb, int) or not (0 <= uyb <= 255):
        settings.Set("TrafficLightDetection", "upperyellow_b", 170)
        uyb = 170
    lyr = settings.Get("TrafficLightDetection", "loweryellow_r")
    if lyr == None or not isinstance(lyr, int) or not (0 <= lyr <= 255):
        settings.Set("TrafficLightDetection", "loweryellow_r", 200)
        lyr = 200
    lyg = settings.Get("TrafficLightDetection", "loweryellow_g")
    if lyg == None or not isinstance(lyg, int) or not (0 <= lyg <= 255):
        settings.Set("TrafficLightDetection", "loweryellow_g", 170)
        lyg = 170
    lyb = settings.Get("TrafficLightDetection", "loweryellow_b")
    if lyb == None or not isinstance(lyb, int) or not (0 <= lyb <= 255):
        settings.Set("TrafficLightDetection", "loweryellow_b", 50)
        lyb = 50
    ugr = settings.Get("TrafficLightDetection", "uppergreen_r")
    if ugr == None or not isinstance(ugr, int) or not (0 <= ugr <= 255):
        settings.Set("TrafficLightDetection", "uppergreen_r", 150)
        ugr = 150
    ugg = settings.Get("TrafficLightDetection", "uppergreen_g")
    if ugg == None or not isinstance(ugg, int) or not (0 <= ugg <= 255):
        settings.Set("TrafficLightDetection", "uppergreen_g", 255)
        ugg = 255
    ugb = settings.Get("TrafficLightDetection", "uppergreen_b")
    if ugb == None or not isinstance(ugb, int) or not (0 <= ugb <= 255):
        settings.Set("TrafficLightDetection", "uppergreen_b", 230)
        ugb = 230
    lgr = settings.Get("TrafficLightDetection", "lowergreen_r")
    if lgr == None or not isinstance(lgr, int) or not (0 <= lgr <= 255):
        settings.Set("TrafficLightDetection", "lowergreen_r", 0)
        lgr = 0
    lgg = settings.Get("TrafficLightDetection", "lowergreen_g")
    if lgg == None or not isinstance(lgg, int) or not (0 <= lgg <= 255):
        settings.Set("TrafficLightDetection", "lowergreen_g", 200)
        lgg = 200
    lgb = settings.Get("TrafficLightDetection", "lowergreen_b")
    if lgb == None or not isinstance(lgb, int) or not (0 <= lgb <= 255):
        settings.Set("TrafficLightDetection", "lowergreen_b", 0)
        lgb = 0

    upper_red_advanced = np.array([urr, urg, urb])
    lower_red_advanced = np.array([lrr, lrg, lrb])
    upper_yellow_advanced = np.array([uyr, uyg, uyb])
    lower_yellow_advanced = np.array([lyr, lyg, lyb])
    upper_green_advanced = np.array([ugr, ugg, ugb])
    lower_green_advanced = np.array([lgr, lgg, lgb])


settings.Set("TrafficLightDetection", "enabled", True)
settings.Listen("TrafficLightDetection", LoadSettings)


def check_internet_connection(host="github.com", port=443, timeout=3):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except:
        return False


def yolo_load_model():
    global yolo_model
    global yolo_model_loaded
    global yolo_detection
    global yolo_showunconfirmed
    global yolo_model_str
    yolo_detection = settings.Get("TrafficLightDetection", "yolo_detection", True)
    yolo_showunconfirmed = settings.Get("TrafficLightDetection", "yolo_showunconfirmed", True)
    yolo_model_str = settings.Get("TrafficLightDetection", "yolo_model", "yolov5n")
    if yolo_model_loaded == False:
        yolo_model_loaded = "loading..."
        yolo_model = None
        def yolo_load_model_thread():
            global yolo_model
            global yolo_model_loaded
            global yolo_detection
            try:
                print("\033[92m" + f"Loading the {yolo_model_str} model..." + "\033[0m")
                import torch
                torch.hub.set_dir(f"{variables.PATH}plugins\\TrafficLightDetection\\YOLOFiles")
                yolo_model = torch.hub.load("ultralytics/yolov5:master", 'custom', f"{variables.PATH}plugins\\TrafficLightDetection\\YOLOModels\\{yolo_model_str}")
                print("\033[92m" + f"Successfully loaded the {yolo_model_str} model!" + "\033[0m")
                yolo_model_loaded = True
            except Exception as e:
                exc = traceback.format_exc()
                SendCrashReport("TrafficLightDetection - Loading YOLO Error.", str(exc))
                console.RestoreConsole()
                print("\033[91m" + f"Failed to load the {yolo_model_str} model: " + "\033[0m" + str(e))
                internet_connection = check_internet_connection()
                if internet_connection == False:
                    print("\033[91m" + f"Possible reason: No internet connection" + "\033[0m")
                yolo_model_loaded = False
                yolo_detection = False
    
        import matplotlib
        matplotlib.use("Agg")

        model_thread = threading.Thread(target=yolo_load_model_thread, daemon=True)
        model_thread.start()


def yolo_detection_function(yolo_detection_frame):
    trafficlight = False
    if yolo_model is None or yolo_model_loaded == False:
        if yolo_model_loaded != "loading...":
            yolo_load_model()
        else:
            return trafficlight
    results = yolo_model(yolo_detection_frame)
    boxes = results.pandas().xyxy[0]
    for _, box in boxes.iterrows():
        if box['name'] in ['traffic light']:
            if (int(box['xmin']) < round(yolo_detection_frame.shape[1] / 2) < int(box['xmax'])) and (int(box['ymin']) < round(yolo_detection_frame.shape[0] / 2) < int(box['ymax'])):
                trafficlight = True
    return trafficlight


def plugin():
    global coordinates
    global trafficlights
    global reset_window
    
    try:
        frameFull = data["frameFull"]
        if x1 < x2 and y1 < y2:
            frame = frameFull[y1:y1+(y2-y1), x1:x1+(x2-x1)]
        else:
            frame = frameFull[0:round(screen_height/1.5), 0:screen_width]
    except:
        return data
    
    if frame is None: return data
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    try:
        truck_x = data["api"]["truckPlacement"]["coordinateX"]
        truck_y = data["api"]["truckPlacement"]["coordinateY"]
        truck_z = data["api"]["truckPlacement"]["coordinateZ"]
        truck_rotation_y = data["api"]["truckPlacement"]["rotationY"]
        truck_rotation_x = data["api"]["truckPlacement"]["rotationX"]

        cabin_offset_x = data["api"]["headPlacement"]["cabinOffsetX"] + data["api"]["configVector"]["cabinPositionX"]
        cabin_offset_y = data["api"]["headPlacement"]["cabinOffsetY"] + data["api"]["configVector"]["cabinPositionY"]
        cabin_offset_z = data["api"]["headPlacement"]["cabinOffsetZ"] + data["api"]["configVector"]["cabinPositionZ"]
        cabin_offset_rotation_y = data["api"]["headPlacement"]["cabinOffsetrotationY"]
        cabin_offset_rotation_x = data["api"]["headPlacement"]["cabinOffsetrotationX"]

        head_offset_x = data["api"]["headPlacement"]["headOffsetX"] + data["api"]["configVector"]["headPositionX"] + cabin_offset_x
        head_offset_y = data["api"]["headPlacement"]["headOffsetY"] + data["api"]["configVector"]["headPositionY"] + cabin_offset_y
        head_offset_z = data["api"]["headPlacement"]["headOffsetZ"] + data["api"]["configVector"]["headPositionZ"] + cabin_offset_z
        head_offset_rotation_y = data["api"]["headPlacement"]["headOffsetrotationY"]
        head_offset_rotation_x = data["api"]["headPlacement"]["headOffsetrotationX"]

        truck_rotation_degrees_x = truck_rotation_x * 360
        if truck_rotation_degrees_x < 0:
            truck_rotation_degrees_x = 360 + truck_rotation_degrees_x
        truck_rotation_radians_x = -math.radians(truck_rotation_degrees_x)

        head_rotation_degrees_x = (truck_rotation_x + cabin_offset_rotation_x + head_offset_rotation_x) * 360
        if head_rotation_degrees_x < 0:
            head_rotation_degrees_x = 360 + head_rotation_degrees_x

        head_rotation_degrees_y = (truck_rotation_y + cabin_offset_rotation_y + head_offset_rotation_y) * 360
        if head_rotation_degrees_y > 180:
            head_rotation_degrees_y = head_rotation_degrees_y - 360

        point_x = head_offset_x
        point_y = head_offset_y
        point_z = head_offset_z
        head_x = point_x * math.cos(truck_rotation_radians_x) - point_z * math.sin(truck_rotation_radians_x) + truck_x
        head_y = point_y * math.cos(head_rotation_degrees_y) - point_y * math.sin(head_rotation_degrees_y) + truck_y
        head_z = point_x * math.sin(truck_rotation_radians_x) + point_z * math.cos(truck_rotation_radians_x) + truck_z
    except:
        truck_x = 0
        truck_y = 0
        truck_z = 0
        truck_rotation_y = 0
        truck_rotation_x = 0

        cabin_offset_x = 0
        cabin_offset_y = 0
        cabin_offset_z = 0
        cabin_offset_rotation_y = 0
        cabin_offset_rotation_x = 0

        head_offset_x = 0
        head_offset_y = 0
        head_offset_z = 0
        head_offset_rotation_y = 0
        head_offset_rotation_x = 0

        truck_rotation_degrees_x = 0
        truck_rotation_radians_x = 0

        head_rotation_degrees_x = 0
        head_rotation_degrees_y = 0

        head_x = 0
        head_y = 0
        head_z = 0


    # ALL CASES:

    # True: --- False: advancedmode, performancemode, detectyellowlight
    # True: detectyellowlight --- False: advancedmode, performancemode
    # True: performancemode --- False: advancedmode
    # True: advancedmode --- False: performancemode, detectyellowlight
    # True: advancedmode, detectyellowlight --- False: performancemode
    # True: advancedmode, performancemode --- False: 


    last_coordinates = coordinates.copy()
    coordinates = []
    if advancedmode == False:
        if performancemode == False:
            if detectyellowlight == False:
                # True: --- False: advancedmode, performancemode, detectyellowlight
                mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)
                filtered_frame_colored = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                filtered_frame_bw = cv2.cvtColor(filtered_frame_colored, cv2.COLOR_BGR2GRAY)
                final_frame = frame
                contours, _ = cv2.findContours(filtered_frame_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                        if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:
                            red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                            green_pixel_count = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                            total_pixels = w * h
                            red_ratio = red_pixel_count / total_pixels
                            green_ratio = green_pixel_count / total_pixels
                            if green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1 or red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1:
                                if red_ratio > green_ratio:
                                    colorstr = "Red"
                                    yoffset1 = y+h*2
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)+h
                                    centery2 = round(y + h / 2)+h*2
                                elif green_ratio > red_ratio:
                                    colorstr = "Green"
                                    yoffset1 = y
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)-h
                                    centery2 = round(y + h / 2)-h*2
                                else:
                                    colorstr = "Red"
                                    yoffset1 = y+h*2
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)+h
                                    centery2 = round(y + h / 2)+h*2
                                try:
                                    centery1_color = rgb_frame[centery1, centerx]
                                except:
                                    centery1_color = (0,0,0)
                                try:
                                    centery2_color = rgb_frame[centery2, centerx]
                                except:
                                    centery2_color = (0,0,0)
                                r_centery1, g_centery1, b_centery1 = centery1_color
                                r_centery2, g_centery2, b_centery2 = centery2_color
                                if r_centery1 < 100 and g_centery1 < 100 and b_centery1 < 100 and r_centery2 < 100 and g_centery2 < 100 and b_centery2 < 100:
                                    coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h,colorstr))

            else:
                # True: detectyellowlight --- False: advancedmode, performancemode
                mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)
                mask_yellow = cv2.inRange(rgb_frame, lower_yellow, upper_yellow)
                combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                filtered_frame_colored = cv2.bitwise_and(frame, frame, mask=combined_mask)
                filtered_frame_bw = cv2.cvtColor(filtered_frame_colored, cv2.COLOR_BGR2GRAY)
                final_frame = frame
                contours, _ = cv2.findContours(filtered_frame_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                        if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:
                            red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                            green_pixel_count = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                            yellow_pixel_count = cv2.countNonZero(mask_yellow[y:y+h, x:x+w])
                            total_pixels = w * h
                            red_ratio = red_pixel_count / total_pixels
                            green_ratio = green_pixel_count / total_pixels
                            yellow_ratio = yellow_pixel_count / total_pixels
                            if (green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1 and yellow_ratio < 0.1 or 
                                red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1 and yellow_ratio < 0.1 or 
                                yellow_ratio < circleplusoffset and yellow_ratio > circleminusoffset and green_ratio < 0.1 and red_ratio < 0.1):
                                if red_ratio > green_ratio and red_ratio > yellow_ratio:
                                    colorstr = "Red"
                                    yoffset1 = y+h*2
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)+h
                                    centery2 = round(y + h / 2)+h*2
                                elif yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                    colorstr = "Yellow"
                                    yoffset1 = y+h
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)-h
                                    centery2 = round(y + h / 2)+h
                                elif green_ratio > red_ratio and green_ratio > yellow_ratio:
                                    colorstr = "Green"
                                    yoffset1 = y
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)-h
                                    centery2 = round(y + h / 2)-h*2
                                else:
                                    colorstr = "Red"
                                    yoffset1 = y+h*2
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)+h
                                    centery2 = round(y + h / 2)+h*2
                                try:
                                    centery1_color = rgb_frame[centery1, centerx]
                                except:
                                    centery1_color = (0,0,0)
                                try:
                                    centery2_color = rgb_frame[centery2, centerx]
                                except:
                                    centery2_color = (0,0,0)
                                r_centery1, g_centery1, b_centery1 = centery1_color
                                r_centery2, g_centery2, b_centery2 = centery2_color
                                if r_centery1 < 100 and g_centery1 < 100 and b_centery1 < 100 and r_centery2 < 100 and g_centery2 < 100 and b_centery2 < 100:
                                    coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h,colorstr))
                
        else:
            # True: performancemode --- False: advancedmode
            mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
            filtered_frame_bw = mask_red.copy()
            final_frame = frame
            contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                    if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:
                        red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                        total_pixels = w * h
                        red_ratio = red_pixel_count / total_pixels
                        if red_ratio < circleplusoffset and red_ratio > circleminusoffset:
                            colorstr = "Red"
                            yoffset1 = y+h*2
                            centerx = round(x + w / 2)
                            centery1 = round(y + h / 2)+h
                            centery2 = round(y + h / 2)+h*2
                            try:
                                centery1_color = rgb_frame[centery1, centerx]
                            except:
                                centery1_color = (0,0,0)
                            try:
                                centery2_color = rgb_frame[centery2, centerx]
                            except:
                                centery2_color = (0,0,0)
                            r_centery1, g_centery1, b_centery1 = centery1_color
                            r_centery2, g_centery2, b_centery2 = centery2_color
                            if r_centery1 < 100 and g_centery1 < 100 and b_centery1 < 100 and r_centery2 < 100 and g_centery2 < 100 and b_centery2 < 100:
                                coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h,colorstr))

    else:

        if performancemode == False:
            if detectyellowlight == False:
                # True: advancedmode --- False: performancemode, detectyellowlight
                mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)
                filtered_frame_colored = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                filtered_frame_bw = cv2.cvtColor(filtered_frame_colored, cv2.COLOR_BGR2GRAY)
                final_frame = frame
                contours, _ = cv2.findContours(filtered_frame_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    istrue = False
                    if rectsizefilter == True:
                        if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                            istrue = True
                    else:
                        istrue = True
                    if istrue == True:
                        istrue = False
                        if widthheightratiofilter == True:
                            if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:
                                istrue = True
                        else:
                            istrue = True
                        if istrue == True:
                            red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                            green_pixel_count = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                            total_pixels = w * h
                            red_ratio = red_pixel_count / total_pixels
                            green_ratio = green_pixel_count / total_pixels
                            istrue = False
                            if pixelpercentagefilter == True:
                                if green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1 or red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1:
                                    istrue = True
                            else:
                                istrue = True
                            if istrue == True:
                                if red_ratio > green_ratio:
                                    colorstr = "Red"
                                    yoffset1 = y+h*2
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)+h
                                    centery2 = round(y + h / 2)+h*2
                                elif green_ratio > red_ratio:
                                    colorstr = "Green"
                                    yoffset1 = y
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)-h
                                    centery2 = round(y + h / 2)-h*2
                                else:
                                    colorstr = "Red"
                                    yoffset1 = y+h*2
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)+h
                                    centery2 = round(y + h / 2)+h*2
                                try:
                                    centery1_color = rgb_frame[centery1, centerx]
                                except:
                                    centery1_color = (0,0,0)
                                try:
                                    centery2_color = rgb_frame[centery2, centerx]
                                except:
                                    centery2_color = (0,0,0)
                                r_centery1, g_centery1, b_centery1 = centery1_color
                                r_centery2, g_centery2, b_centery2 = centery2_color
                                istrue = False
                                if otherlightsofffilter == True:
                                    if r_centery1 < 100 and g_centery1 < 100 and b_centery1 < 100 and r_centery2 < 100 and g_centery2 < 100 and b_centery2 < 100:
                                        istrue = True
                                else:
                                    istrue = True
                                if istrue == True:
                                    coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h,colorstr))

            else:
                # True: advancedmode, detectyellowlight --- False: performancemode
                mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)
                mask_yellow = cv2.inRange(rgb_frame, lower_yellow_advanced, upper_yellow_advanced)
                combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                filtered_frame_colored = cv2.bitwise_and(frame, frame, mask=combined_mask)
                filtered_frame_bw = cv2.cvtColor(filtered_frame_colored, cv2.COLOR_BGR2GRAY)
                final_frame = frame
                contours, _ = cv2.findContours(filtered_frame_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    istrue = False
                    if rectsizefilter == True:
                        if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                            istrue = True
                    else:
                        istrue = True
                    if istrue == True:
                        istrue = False
                        if widthheightratiofilter == True:
                            if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:
                                istrue = True
                        else:
                            istrue = True
                        if istrue == True:
                            red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                            green_pixel_count = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                            yellow_pixel_count = cv2.countNonZero(mask_yellow[y:y+h, x:x+w])
                            total_pixels = w * h
                            red_ratio = red_pixel_count / total_pixels
                            green_ratio = green_pixel_count / total_pixels
                            yellow_ratio = yellow_pixel_count / total_pixels
                            istrue = False
                            if pixelpercentagefilter == True:
                                if (green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1 and yellow_ratio < 0.1 or 
                                    red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1 and yellow_ratio < 0.1 or 
                                    yellow_ratio < circleplusoffset and yellow_ratio > circleminusoffset and green_ratio < 0.1 and red_ratio < 0.1):
                                    istrue = True
                            else:
                                istrue = True
                            if istrue == True:
                                if red_ratio > green_ratio and red_ratio > yellow_ratio:
                                    colorstr = "Red"
                                    yoffset1 = y+h*2
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)+h
                                    centery2 = round(y + h / 2)+h*2
                                elif yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                    colorstr = "Yellow"
                                    yoffset1 = y+h
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)-h
                                    centery2 = round(y + h / 2)+h
                                elif green_ratio > red_ratio and green_ratio > yellow_ratio:
                                    colorstr = "Green"
                                    yoffset1 = y
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)-h
                                    centery2 = round(y + h / 2)-h*2
                                else:
                                    colorstr = "Red"
                                    yoffset1 = y+h*2
                                    centerx = round(x + w / 2)
                                    centery1 = round(y + h / 2)+h
                                    centery2 = round(y + h / 2)+h*2
                                try:
                                    centery1_color = rgb_frame[centery1, centerx]
                                except:
                                    centery1_color = (0,0,0)
                                try:
                                    centery2_color = rgb_frame[centery2, centerx]
                                except:
                                    centery2_color = (0,0,0)
                                r_centery1, g_centery1, b_centery1 = centery1_color
                                r_centery2, g_centery2, b_centery2 = centery2_color
                                istrue = False
                                if otherlightsofffilter == True:
                                    if r_centery1 < 100 and g_centery1 < 100 and b_centery1 < 100 and r_centery2 < 100 and g_centery2 < 100 and b_centery2 < 100:
                                        istrue = True
                                else:
                                    istrue = True
                                if istrue == True:
                                    coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h,colorstr))
                    
        else:
            # True: advancedmode, performancemode --- False:     
            mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
            filtered_frame_bw = mask_red.copy()
            final_frame = frame
            contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                istrue = False
                if rectsizefilter == True:
                    if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                        istrue = True
                else:
                    istrue = True
                if istrue == True:
                    istrue = False
                    if widthheightratiofilter == True:
                        if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:
                            istrue = True
                    else:
                        istrue = True
                    if istrue == True:
                        red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                        total_pixels = w * h
                        red_ratio = red_pixel_count / total_pixels
                        istrue = False
                        if pixelpercentagefilter == True:
                            if red_ratio < circleplusoffset and red_ratio > circleminusoffset:
                                istrue = True
                        else:
                            istrue = True
                        if istrue == True:
                            colorstr = "Red"
                            yoffset1 = y+h*2
                            centerx = round(x + w / 2)
                            centery1 = round(y + h / 2)+h
                            centery2 = round(y + h / 2)+h*2
                            try:
                                centery1_color = rgb_frame[centery1, centerx]
                            except:
                                centery1_color = (0,0,0)
                            try:
                                centery2_color = rgb_frame[centery2, centerx]
                            except:
                                centery2_color = (0,0,0)
                            r_centery1, g_centery1, b_centery1 = centery1_color
                            r_centery2, g_centery2, b_centery2 = centery2_color
                            istrue = False
                            if otherlightsofffilter == True:
                                if r_centery1 < 100 and g_centery1 < 100 and b_centery1 < 100 and r_centery2 < 100 and g_centery2 < 100 and b_centery2 < 100:
                                    istrue = True
                            else:
                                istrue = True
                            if istrue == True:
                                coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h,colorstr))


    try:
        # Tracking with IDs:
        def generate_new_id():
            used_ids = set(id for _, _, id, _ in trafficlights)
            new_id = 1
            while new_id in used_ids:
                new_id += 1
            return new_id

        if last_coordinates:
            for i in range(len(last_coordinates)):
                last_x, last_y, w, h, state = last_coordinates[i]
                closest = screen_width
                nearestpoint = None
                exists_in_trafficlights = False
                saved_position = None
                saved_id = None
                saved_approved = None
                for j in range(len(coordinates)):
                    x, y, w, h, state = coordinates[j]
                    distance = math.sqrt((x - last_x)**2 + (y - last_y)**2)
                    if distance < closest:
                        closest = distance
                        nearestpoint = x, y, w, h, state

                # Remove missing points from traffic lights and update list
                if nearestpoint:
                    for k, (coord, position, id, approved) in enumerate(trafficlights):
                        if coord == last_coordinates[i]:
                            exists_in_trafficlights = True
                            angle = ((x1 + nearestpoint[0]) - screen_width / 2) * (fov / screen_width)
                            saved_position = (position[0], (head_x, head_z, angle, head_rotation_degrees_x), position[2])
                            saved_id = id
                            saved_approved = approved
                            del trafficlights[k]
                            break
                    if exists_in_trafficlights:
                        trafficlights.append((nearestpoint, saved_position, saved_id, saved_approved))
                    else:
                        new_id = generate_new_id()
                        angle = ((x1 + nearestpoint[0]) - screen_width / 2) * (fov / screen_width)
                        if yolo_detection == True:
                            x, y, w, h, state = nearestpoint
                            x1_confirmation = round(x - w*6)
                            y1_confirmation = round(y - w*7)
                            x2_confirmation = round(x + w*6)
                            y2_confirmation = round(y + w*7)
                            if x1_confirmation < 0:
                                x1_confirmation = 0
                            if y1_confirmation < 0:
                                y1_confirmation = 0
                            if x2_confirmation > screen_width - 1:
                                x2_confirmation = screen_width - 1
                            if y2_confirmation > screen_height - 1:
                                y2_confirmation = screen_height - 1
                            yolo_detection_frame = frameFull[y1+y1_confirmation:y1+y2_confirmation, x1+x1_confirmation:x1+x2_confirmation]
                            approved = yolo_detection_function(yolo_detection_frame)
                        else:
                            approved = True
                        trafficlights.append((nearestpoint, ((None, None, None), (head_x, head_z, angle, head_rotation_degrees_x), (head_x, head_z, angle, head_rotation_degrees_x)), new_id, approved))

        # Remove lost traffic lights from the list, the traffic light which has the highest distance to the nearest traffic light in the current frame gets removed
        exists = []
        for coord_x, coord_y, _, _, _ in coordinates:
            for (x, y, _, _, _), _, id, _ in trafficlights:
                if x == coord_x and y == coord_y:
                    exists.append(id)
                    break
        for i, (_, _, id, _) in enumerate(trafficlights):
            if id not in exists:
                del trafficlights[i]
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Tracking/YOLO Error.", str(exc))
        print("TrafficLightDetection - Tracking/YOLO Error: " + str(exc))


    try:
        for i, (coord, ((previous_trafficlight_x, previous_trafficlight_y, previous_trafficlight_z), (head_x, head_z, head_angle, head_rotation), (first_head_x, first_head_z, first_head_angle, first_head_rotation)), id, approved) in enumerate(trafficlights):

            angle_offset = first_head_rotation - head_rotation

            angle_A = 180 - head_angle - angle_offset
            angle_B = first_head_angle
            if angle_B < 0:
                angle_B = 360 + angle_B

            position_A = head_x, head_z
            position_B = first_head_x, first_head_z

            if math.sqrt((position_B[0] - position_A[0]) ** 2 + (position_B[1] - position_A[1]) ** 2) > 0.01:
                angle_A_rad = math.radians(angle_A)
                angle_B_rad = math.radians(angle_B)
                angle_C_rad = math.pi - angle_A_rad - angle_B_rad
                distance_AB = math.sqrt((position_B[0] - position_A[0]) ** 2 + (position_B[1] - position_A[1]) ** 2)
                length_A = distance_AB * math.sin(angle_A_rad) / math.sin(angle_C_rad)
                length_B = distance_AB * math.sin(angle_B_rad) / math.sin(angle_C_rad)
                position_C_x = length_B * math.cos(angle_A_rad)
                position_C_y = length_B * math.sin(angle_A_rad)
                direction_AB = (position_B[0] - position_A[0], position_B[1] - position_A[1])
                length_AB = math.sqrt(direction_AB[0] ** 2 + direction_AB[1] ** 2)
                direction_unit_AB = (direction_AB[0] / length_AB, direction_AB[1] / length_AB)
                direction_unit_perpendicular_ab = (-direction_unit_AB[1], direction_unit_AB[0])
                position_C = (position_A[0] + position_C_x * direction_unit_AB[0] - position_C_y * direction_unit_perpendicular_ab[0], position_A[1] + position_C_x * direction_unit_AB[1] - position_C_y * direction_unit_perpendicular_ab[1])

                trafficlight_x, trafficlight_z = position_C
                
                angle = (y1 - screen_height / 2) * (fov / screen_height) - head_rotation_degrees_y
                trafficlight_y = head_y + (math.sin(head_rotation_degrees_y) * math.sqrt((truck_x - head_x)**2 + (truck_z - head_z)**2))

                if previous_trafficlight_x != None and previous_trafficlight_y != None and previous_trafficlight_z != None:
                    trafficlight_x = previous_trafficlight_x + (trafficlight_x - previous_trafficlight_x) / 5
                    trafficlight_y = previous_trafficlight_y + (trafficlight_y - previous_trafficlight_y) / 5
                    trafficlight_z = previous_trafficlight_z + (trafficlight_z - previous_trafficlight_z) / 5
                
                trafficlights[i] = (coord, ((trafficlight_x, trafficlight_y, trafficlight_z), (head_x, head_z, head_angle, head_rotation), (first_head_x, first_head_z, first_head_angle, first_head_rotation)), id, approved)

    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Position Estimation Error.", str(exc))
        print("TrafficLightDetection - Position Estimation Error: " + str(e))


    try:
        if anywindowopen == True:
            if grayscalewindow == True and len(trafficlights) > 0:
                current_text = f"Traffic Lights:"
                width_target_current_text = 0.15 * filtered_frame_bw.shape[1]
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
                cv2.putText(filtered_frame_bw, current_text, (round(0.01*filtered_frame_bw.shape[0]), round(0.01*filtered_frame_bw.shape[0]+height_current_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text)
            for i in range(len(trafficlights)):
                coord, position, id, approved = trafficlights[i]
                x, y, w, h, state = coord
                if grayscalewindow == True:
                    if yolo_showunconfirmed == False and approved == True:
                        cv2.putText(filtered_frame_bw, f"ID: {id}, {state}", (round(0.01*filtered_frame_bw.shape[0]), round(0.01*filtered_frame_bw.shape[0]+height_current_text*(i+2)*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text)
                        cv2.line(filtered_frame_bw, (round(0.01*filtered_frame_bw.shape[0]+cv2.getTextSize(f"ID: {id}, {state}", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)[0][0]), round(0.01*filtered_frame_bw.shape[0]+height_current_text*(i+2)*1.5-height_current_text/2)), (x, y - h) if state == "Red" else ((x, y + h) if state == "Green" else (x, y)), (255, 255, 255), thickness_current_text)
                    elif yolo_showunconfirmed == True:
                        cv2.putText(filtered_frame_bw, f"ID: {id}, {state}", (round(0.01*filtered_frame_bw.shape[0]), round(0.01*filtered_frame_bw.shape[0]+height_current_text*(i+2)*1.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text)
                        cv2.line(filtered_frame_bw, (round(0.01*filtered_frame_bw.shape[0]+cv2.getTextSize(f"ID: {id}, {state}", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)[0][0]), round(0.01*filtered_frame_bw.shape[0]+height_current_text*(i+2)*1.5-height_current_text/2)), (x, y - h) if state == "Red" else ((x, y + h) if state == "Green" else (x, y)), (255, 255, 255), thickness_current_text)
                radius = round((w+h)/4)
                thickness = round((w+h)/30)
                if thickness < 1:
                    thickness = 1
                if approved == True:
                    if state == "Red":
                        color = (0, 0, 255)
                        cv2.circle(final_frame, (x,y-h), radius, color, thickness)
                        cv2.circle(filtered_frame_bw, (x,y-h), radius, (255, 255, 255), thickness)
                        cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                        if grayscalewindow == True:
                            cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                    if state == "Yellow":
                        color = (0, 255, 255)
                        cv2.circle(final_frame, (x,y), radius, color, thickness)
                        cv2.circle(filtered_frame_bw, (x,y), radius, (255, 255, 255), thickness)
                        cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                        if grayscalewindow == True:
                            cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                    if state == "Green":
                        color = (0, 255, 0)
                        cv2.circle(final_frame, (x,y+h), radius, color, thickness)
                        cv2.circle(filtered_frame_bw, (x,y+h), radius, (255, 255, 255), thickness)
                        cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                        if grayscalewindow == True:
                            cv2.rectangle(filtered_frame_bw, (x-round(w/2), y+round(h*0.5)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                elif approved == False and yolo_showunconfirmed == True:
                    if state == "Red":
                        color = (150, 150, 150)
                        cv2.circle(final_frame, (x,y-h), radius, color, thickness)
                        cv2.circle(filtered_frame_bw, (x,y-h), radius, (255, 255, 255), thickness)
                        cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                        if grayscalewindow == True:
                            cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                    if state == "Yellow":
                        color = (150, 150, 150)
                        cv2.circle(final_frame, (x,y), radius, color, thickness)
                        cv2.circle(filtered_frame_bw, (x,y), radius, (255, 255, 255), thickness)
                        cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                        if grayscalewindow == True:
                            cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                    if state == "Green":
                        color = (150, 150, 150)
                        cv2.circle(final_frame, (x,y+h), radius, color, thickness)
                        cv2.circle(filtered_frame_bw, (x,y+h), radius, (255, 255, 255), thickness)
                        cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                        if grayscalewindow == True:
                            cv2.rectangle(filtered_frame_bw, (x-round(w/2), y+round(h*0.5)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Draw Output Error.", str(exc))
        print("TrafficLightDetection - Draw Output Error: " + str(e))


    if positionestimationwindow == True:
        try:
            positionestimation_frame = positionestimation_default_frame.copy()
            positionestimation_frame_width = positionestimation_frame.shape[1]
            positionestimation_frame_height = positionestimation_frame.shape[0]

            for i, ((_, _, _, _, state), ((trafficlight_x, trafficlight_y, trafficlight_z), _, _), _, _) in enumerate(trafficlights):
                if trafficlight_x != None and trafficlight_y != None and trafficlight_z != None:
                    ppm = 0.1
                    x = (trafficlight_x - truck_x) * (1/ppm)
                    y = (trafficlight_z - truck_z) * (1/ppm)

                    point_x = x
                    point_y = y
                    x = round(positionestimation_frame_width/4 + (point_x * math.cos(truck_rotation_radians_x) + point_y * math.sin(truck_rotation_radians_x)))
                    y = round(positionestimation_frame_height - (point_x * math.sin(truck_rotation_radians_x) - point_y * math.cos(truck_rotation_radians_x)))

                    if state == "Red":
                        color = (0, 0, 255)
                    elif state == "Yellow":
                        color = (0, 255, 255)
                    elif state == "Green":
                        color = (0, 255, 0)
                    cv2.circle(positionestimation_frame, (x, y - round(positionestimation_frame_height * 0.179)), round(positionestimation_frame_height/100), color, -1)

        except Exception as e:
            exc = traceback.format_exc()
            SendCrashReport("TrafficLightDetection - Position Estimation Drawing Error.", str(exc))
            print("TrafficLightDetection - Position Estimation Drawing Error: " + str(e))


    try:
        data_simple = None
        for i in range(len(trafficlights)):
            coord, id, position, approved = trafficlights[i]
            x, y, w, h, state = coord
            if state == "Red" and approved == True:
                data_simple = "Red"
                break
            elif state == "Yellow" and approved == True:
                data_simple = "Yellow"
                break
            elif state == "Green" and approved == True:
                data_simple = "Green"
                break
        data["TrafficLightDetection"] = {}
        data["TrafficLightDetection"]["simple"] = data_simple
        data["TrafficLightDetection"]["detailed"] = trafficlights
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Data Error.", str(exc))
        print("TrafficLightDetection - Data Error: " + str(e))


    if reset_window == True:
        if finalwindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - Final')
            except:
                pass
        if grayscalewindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - B/W')
            except:
                pass
        if positionestimationwindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - Position Estimation')
            except:
                pass

    if finalwindow == True:
        window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - Final')
        if window_handle == 0 or reset_window == True:
            cv2.namedWindow('Traffic Light Detection - Final', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Light Detection - Final', round(windowwidth*windowscale), round(windowheight*windowscale))
            cv2.setWindowProperty('Traffic Light Detection - Final', cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow('Traffic Light Detection - Final', final_frame)
    if grayscalewindow == True:
        window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - B/W')
        if window_handle == 0 or reset_window == True:
            cv2.namedWindow('Traffic Light Detection - B/W', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Light Detection - B/W', round(windowwidth*windowscale), round(windowheight*windowscale))
            cv2.setWindowProperty('Traffic Light Detection - B/W', cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow('Traffic Light Detection - B/W', filtered_frame_bw)
    if positionestimationwindow == True:
        window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - Position Estimation')
        if window_handle == 0 or reset_window == True:
            cv2.namedWindow('Traffic Light Detection - Position Estimation', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Light Detection - Position Estimation', positionestimation_frame.shape[1], positionestimation_frame.shape[0])
            cv2.setWindowProperty('Traffic Light Detection - Position Estimation', cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow('Traffic Light Detection - Position Estimation', positionestimation_frame)
    if reset_window == True:
        reset_window = False
    return data