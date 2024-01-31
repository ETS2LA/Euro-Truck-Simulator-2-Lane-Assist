"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import switchSelectedPlugin, resizeWindow

PluginInfo = PluginInformation(
    name="TrafficLightDetection", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Detects traffic lights with vision.",
    version="0.4",
    author="Glas42, Tumppi066",
    url="https://github.com/Glas42/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before lane detection" # Will run the plugin before anything else in the mainloop (data will be empty)
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
import math

screen_width, screen_height = pyautogui.size()

coordinates = []
trafficlights = []

lower_red = np.array([200, 0, 0])
upper_red = np.array([255, 110, 110])
lower_green = np.array([0, 200, 0])
upper_green = np.array([150, 255, 230])
lower_yellow = np.array([200, 170, 50])
upper_yellow = np.array([255, 240, 170])

yolo_model_loaded = False

def UpdateSettings():
    global min_rect_size
    global max_rect_size
    global width_height_ratio
    global circlepercent
    global maxcircleoffset
    global circleplusoffset
    global circleminusoffset
    global finalwindow
    global grayscalewindow
    global redyellowgreenwindow
    global anywindowopen
    global automaticwindowsize
    global detectyellowlight
    global performancemode
    global advancedmode
    global windowscale
    global usefullframe
    global yolo_detection
    global yolo_showunconfirmed
    global yolo_model_loaded
    global yolo_model
    global coordinates
    global trafficlights
    global windowwidth
    global windowheight
    global reset_window
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
    
    finalwindow = settings.GetSettings("TrafficLightDetection", "finalwindow", True)
    grayscalewindow = settings.GetSettings("TrafficLightDetection", "grayscalewindow", False)
    redyellowgreenwindow = settings.GetSettings("TrafficLightDetection", "redyellowgreenwindow", False)
    automaticwindowsize = settings.GetSettings("TrafficLightDetection", "automaticwindowsize", True)
    detectyellowlight = settings.GetSettings("TrafficLightDetection", "detectyellowlight", False)
    performancemode = settings.GetSettings("TrafficLightDetection", "performancemode", True)
    advancedmode = settings.GetSettings("TrafficLightDetection", "advancedmode", False)
    usefullframe = settings.GetSettings("TrafficLightDetection", "usefullframe", True)
    windowscale = float(settings.GetSettings("TrafficLightDetection", "scale", 0.5))
    x1 = settings.GetSettings("TrafficLightDetection", "x1ofsc", 0)
    y1 = settings.GetSettings("TrafficLightDetection", "y1ofsc", 0)
    x2 = settings.GetSettings("TrafficLightDetection", "x2ofsc", screen_width-1)
    y2 = settings.GetSettings("TrafficLightDetection", "y2ofsc", round(screen_height/1.5)-1)

    rectsizefilter = settings.GetSettings("TrafficLightDetection", "rectsizefilter", True)
    widthheightratiofilter = settings.GetSettings("TrafficLightDetection", "widthheightratiofilter", True)
    pixelpercentagefilter = settings.GetSettings("TrafficLightDetection", "pixelpercentagefilter", True)
    otherlightsofffilter = settings.GetSettings("TrafficLightDetection", "otherlightsofffilter", True)

    yolo_detection = settings.GetSettings("TrafficLightDetection", "yolo_detection", True)
    yolo_showunconfirmed = settings.GetSettings("TrafficLightDetection", "yolo_showunconfirmed", True)

    coordinates = []
    trafficlights = []

    if automaticwindowsize == True:
        if usefullframe == False:
            windowwidth = x2-x1
            windowheight = y2-y1
        else:
            windowwidth = screen_width
            windowheight = round(screen_height/1.5)
    else:
        windowwidth = settings.GetSettings("TrafficLightDetection", "outputwindowwidth", round(screen_width/2))
        windowheight = settings.GetSettings("TrafficLightDetection", "outputwindowheight", round(screen_height/3))
    
    reset_window = True

    if advancedmode == False:
        min_rect_size = screen_width / 240
        max_rect_size = screen_width / 10
    else:
        min_rect_size = settings.GetSettings("TrafficLightDetection", "minrectsize", round(screen_width / 240))
        max_rect_size = settings.GetSettings("TrafficLightDetection", "maxrectsize", round(screen_width / 10))

    width_height_ratio = 0.2
    circlepercent = 0.785
    maxcircleoffset = 0.15
    circleplusoffset = circlepercent + maxcircleoffset
    circleminusoffset = circlepercent - maxcircleoffset

    if min_rect_size < 8:
        min_rect_size = 8

    if ((finalwindow + grayscalewindow + redyellowgreenwindow) > 0):
        anywindowopen = True
    else:
        anywindowopen = False

    if x2-x1-1 < 0:
        print("Your Screen Capture Coordinates are invalid because the right X is to the left of the left X (message from TrafficLightDetection)")
        messagebox.showwarning(title="TrafficLightDetection", message="Your Screen Capture Coordinates are invalid because the right X is to the left of the left X (message from TrafficLightDetection)")
    if y2-y1-1 < 0:
        print("Your Screen Capture Coordinates are invalid because the bottom Y is above the top Y (message from TrafficLightDetection)")
        messagebox.showwarning(title="TrafficLightDetection", message="Your Screen Capture Coordinates are invalid because the bottom Y is above the top Y (message from TrafficLightDetection)")
    
    urr = settings.GetSettings("TrafficLightDetection", "upperred_r")
    if urr == None or not isinstance(urr, int) or not (0 <= urr <= 255):
        settings.CreateSettings("TrafficLightDetection", "upperred_r", 255)
        urr = 255
    urg = settings.GetSettings("TrafficLightDetection", "upperred_g")
    if urg == None or not isinstance(urg, int) or not (0 <= urg <= 255):
        settings.CreateSettings("TrafficLightDetection", "upperred_g", 110)
        urg = 110
    urb = settings.GetSettings("TrafficLightDetection", "upperred_b")
    if urb == None or not isinstance(urb, int) or not (0 <= urb <= 255):
        settings.CreateSettings("TrafficLightDetection", "upperred_b", 110)
        urb = 110
    lrr = settings.GetSettings("TrafficLightDetection", "lowerred_r")
    if lrr == None or not isinstance(lrr, int) or not (0 <= lrr <= 255):
        settings.CreateSettings("TrafficLightDetection", "lowerred_r", 200)
        lrr = 200
    lrg = settings.GetSettings("TrafficLightDetection", "lowerred_g")
    if lrg == None or not isinstance(lrg, int) or not (0 <= lrg <= 255):
        settings.CreateSettings("TrafficLightDetection", "lowerred_g", 0)
        lrg = 0
    lrb = settings.GetSettings("TrafficLightDetection", "lowerred_b")
    if lrb == None or not isinstance(lrb, int) or not (0 <= lrb <= 255):
        settings.CreateSettings("TrafficLightDetection", "lowerred_b", 0)
        lrb = 0
    uyr = settings.GetSettings("TrafficLightDetection", "upperyellow_r")
    if uyr == None or not isinstance(uyr, int) or not (0 <= uyr <= 255):
        settings.CreateSettings("TrafficLightDetection", "upperyellow_r", 255)
        uyr = 255
    uyg = settings.GetSettings("TrafficLightDetection", "upperyellow_g")
    if uyg == None or not isinstance(uyg, int) or not (0 <= uyg <= 255):
        settings.CreateSettings("TrafficLightDetection", "upperyellow_g", 240)
        uyg = 240
    uyb = settings.GetSettings("TrafficLightDetection", "upperyellow_b")
    if uyb == None or not isinstance(uyb, int) or not (0 <= uyb <= 255):
        settings.CreateSettings("TrafficLightDetection", "upperyellow_b", 170)
        uyb = 170
    lyr = settings.GetSettings("TrafficLightDetection", "loweryellow_r")
    if lyr == None or not isinstance(lyr, int) or not (0 <= lyr <= 255):
        settings.CreateSettings("TrafficLightDetection", "loweryellow_r", 200)
        lyr = 200
    lyg = settings.GetSettings("TrafficLightDetection", "loweryellow_g")
    if lyg == None or not isinstance(lyg, int) or not (0 <= lyg <= 255):
        settings.CreateSettings("TrafficLightDetection", "loweryellow_g", 170)
        lyg = 170
    lyb = settings.GetSettings("TrafficLightDetection", "loweryellow_b")
    if lyb == None or not isinstance(lyb, int) or not (0 <= lyb <= 255):
        settings.CreateSettings("TrafficLightDetection", "loweryellow_b", 50)
        lyb = 50
    ugr = settings.GetSettings("TrafficLightDetection", "uppergreen_r")
    if ugr == None or not isinstance(ugr, int) or not (0 <= ugr <= 255):
        settings.CreateSettings("TrafficLightDetection", "uppergreen_r", 150)
        ugr = 150
    ugg = settings.GetSettings("TrafficLightDetection", "uppergreen_g")
    if ugg == None or not isinstance(ugg, int) or not (0 <= ugg <= 255):
        settings.CreateSettings("TrafficLightDetection", "uppergreen_g", 255)
        ugg = 255
    ugb = settings.GetSettings("TrafficLightDetection", "uppergreen_b")
    if ugb == None or not isinstance(ugb, int) or not (0 <= ugb <= 255):
        settings.CreateSettings("TrafficLightDetection", "uppergreen_b", 230)
        ugb = 230
    lgr = settings.GetSettings("TrafficLightDetection", "lowergreen_r")
    if lgr == None or not isinstance(lgr, int) or not (0 <= lgr <= 255):
        settings.CreateSettings("TrafficLightDetection", "lowergreen_r", 0)
        lgr = 0
    lgg = settings.GetSettings("TrafficLightDetection", "lowergreen_g")
    if lgg == None or not isinstance(lgg, int) or not (0 <= lgg <= 255):
        settings.CreateSettings("TrafficLightDetection", "lowergreen_g", 200)
        lgg = 200
    lgb = settings.GetSettings("TrafficLightDetection", "lowergreen_b")
    if lgb == None or not isinstance(lgb, int) or not (0 <= lgb <= 255):
        settings.CreateSettings("TrafficLightDetection", "lowergreen_b", 0)
        lgb = 0

    upper_red_advanced = np.array([urr, urg, urb])
    lower_red_advanced = np.array([lrr, lrg, lrb])
    upper_yellow_advanced = np.array([uyr, uyg, uyb])
    lower_yellow_advanced = np.array([lyr, lyg, lyb])
    upper_green_advanced = np.array([ugr, ugg, ugb])
    lower_green_advanced = np.array([lgr, lgg, lgb])
UpdateSettings()
    
def loadYOLO():
    global yolo_model_loaded
    global yolo_model
    global yolo_detection
    global yolo_showunconfirmed
    global yolo_model_str
    
    yolo_detection = settings.GetSettings("TrafficLightDetection", "yolo_detection", True)
    yolo_showunconfirmed = settings.GetSettings("TrafficLightDetection", "yolo_showunconfirmed", True)
    yolo_model_str = settings.GetSettings("TrafficLightDetection", "yolo_model", "yolov5n") # 'yolov5n', 'yolov5s', 'yolov5m', 'yolov5l', 'yolov5x'
    if yolo_model_loaded == False:
        print("\033[92m" + f"Loading the {yolo_model_str} model..." + "\033[0m")
        try:
            import torch
            torch.hub.set_dir(f"{variables.PATH}plugins\\TrafficLightDetection\\YoloFiles")
            yolo_model = torch.hub.load("ultralytics/yolov5", yolo_model_str)
            print("\033[92m" + f"Successfully loaded the {yolo_model_str} model!" + "\033[0m")
        except Exception as e:
            print("\033[91m" + f"Failed to load the {yolo_model_str} model: " + "\033[0m" + str(e))
        yolo_model_loaded = True

def yolo_detection_function(yolo_detection_frame, x, y, w, h):
    trafficlight = False
    if yolo_model is None or yolo_model_loaded == False:
        loadYOLO()
    results = yolo_model(yolo_detection_frame)
    boxes = results.pandas().xyxy[0]
    for _, box in boxes.iterrows():
        if box['name'] in ['traffic light']:
            if (int(box['xmin']) < round(yolo_detection_frame.shape[1] / 2) < int(box['xmax'])) and (int(box['ymin']) < round(yolo_detection_frame.shape[0] / 2) < int(box['ymax'])):
                trafficlight = True
    return trafficlight


# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    global coordinates
    global trafficlights
    global reset_window
    
    try:
        frameFull = data["frameFull"]
        if usefullframe == False and x2-x1 > 0 and y2-y1 > 0:
            frame = frameFull[y1:y1+(y2-y1), x1:x1+(x2-x1)]
        else: 
            frame = frameFull[0:round(screen_height/1.5), 0:screen_width] 
    except:
        return data
    
    if frame is None: return data
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ALL CASES:

    # True: --- False: advancedmode, performancemode, detectyellowlight
    # True: detectyellowlight --- False: advancedmode, performancemode
    # True: performancemode --- False: advancedmode
    # True: --- False: advancedmode, performancemode, detectyellowlight
    # True: detectyellowlight --- False: advancedmode, performancemode
    # True: performancemode --- False: advancedmode
    # True: advancedmode --- False: performancemode, detectyellowlight
    # True: advancedmode, detectyellowlight --- False: performancemode
    # True: advancedmode, performancemode --- False: 
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
                filtered_frame_red_yellow_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                filtered_frame_bw = cv2.cvtColor(filtered_frame_red_yellow_green, cv2.COLOR_BGR2GRAY)
                final_frame = frame
                contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_yellow_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                    yoffset1 = y-h
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
                filtered_frame_red_yellow_green = cv2.bitwise_and(frame, frame, mask=combined_mask)
                filtered_frame_bw = cv2.cvtColor(filtered_frame_red_yellow_green, cv2.COLOR_BGR2GRAY)
                final_frame = frame
                contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_yellow_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                    yoffset1 = y-h
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
            filtered_frame_red_yellow_green = cv2.bitwise_and(frame, frame, mask=mask_red)
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
                filtered_frame_red_yellow_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                filtered_frame_bw = cv2.cvtColor(filtered_frame_red_yellow_green, cv2.COLOR_BGR2GRAY)
                final_frame = frame
                contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_yellow_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                    yoffset1 = y-h
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
                filtered_frame_red_yellow_green = cv2.bitwise_and(frame, frame, mask=combined_mask)
                filtered_frame_bw = cv2.cvtColor(filtered_frame_red_yellow_green, cv2.COLOR_BGR2GRAY)
                final_frame = frame
                contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_yellow_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                    yoffset1 = y-h
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
            filtered_frame_red_yellow_green = cv2.bitwise_and(frame, frame, mask=mask_red)
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

    if yolo_detection == True:
        try:
            # Tracking with IDs:

            def generate_new_id():
                used_ids = set(id for _, id, _ in trafficlights)
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
                        for k, (coord, id, approved) in enumerate(trafficlights):
                            if coord == last_coordinates[i]:
                                exists_in_trafficlights = True
                                saved_id = id
                                saved_approved = approved
                                del trafficlights[k]
                                break
                        if exists_in_trafficlights:
                            trafficlights.append((nearestpoint, saved_id, saved_approved))
                        else:
                            new_id = generate_new_id()
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
                            if usefullframe == False and x2-x1 > 0 and y2-y1 > 0:
                                yolo_detection_frame = frameFull[y1+y1_confirmation:y1+y2_confirmation, x1+x1_confirmation:x1+x2_confirmation]
                            else:
                                yolo_detection_frame = frameFull[y1_confirmation:y2_confirmation, x1_confirmation:x2_confirmation]
                            approved = yolo_detection_function(yolo_detection_frame, x, y, w, h)
                            trafficlights.append((nearestpoint, new_id, approved))

                # Remove lost traffic lights based on distance traveled
                lost_trafficlights = len(last_coordinates) - len(coordinates)
                if lost_trafficlights > 0:
                    max_distances = []
                    for i, ((x, y, w, h, state), _, _) in enumerate(trafficlights):
                        if i < len(last_coordinates):
                            distance = math.sqrt((x - last_coordinates[i][0])**2 + (y - last_coordinates[i][1])**2)
                            max_distances.append((distance, i))
                    max_distances.sort(reverse=True)
                    for _ in range(lost_trafficlights):
                        if max_distances:
                            max_index = max_distances.pop(0)[1]
                            del trafficlights[max_index]

                # Filter to remove extra IDs
                if len(trafficlights) > len(coordinates):
                    id_counts = {}
                    for _, id, _ in trafficlights:
                        id_counts[id] = id_counts.get(id, 0) + 1

                    for _ in range(len(trafficlights) - len(coordinates)):
                        max_index = None
                        max_count = 0
                        for i, (_, id, _) in enumerate(trafficlights):
                            if id_counts[id] > max_count:
                                max_index = i
                                max_count = id_counts[id]

                        if max_index is not None:
                            del trafficlights[max_index]
                            id_counts[trafficlights[max_index][1]] -= 1

                
            if anywindowopen == True:
                for i in range(len(trafficlights)):
                    coord, id, approved = trafficlights[i]
                    x, y, w, h, state = coord
                    radius = round((w+h)/4)
                    thickness = round((w+h)/30)
                    if thickness < 1:
                        thickness = 1
                    if approved == True:
                        if state == "Red":
                            color = (0, 0, 255)
                            cv2.circle(final_frame, (x,y-h), radius, color, thickness)
                            cv2.circle(filtered_frame_bw, (x,y-h), radius, (255, 255, 255), thickness)
                            cv2.circle(filtered_frame_red_yellow_green, (x,y-h), radius,color, thickness)
                            cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                            cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                            if grayscalewindow == True:
                                cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                            if redyellowgreenwindow == True:
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                            if finalwindow == True:
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                        if state == "Yellow":
                            color = (0, 255, 255)
                            cv2.circle(final_frame, (x,y), radius, color, thickness)
                            cv2.circle(filtered_frame_bw, (x,y), radius, (255, 255, 255), thickness)
                            cv2.circle(filtered_frame_red_yellow_green, (x,y), radius,color, thickness)
                            cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                            cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                            if grayscalewindow == True:
                                cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            if redyellowgreenwindow == True:
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                            if finalwindow == True:
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                        if state == "Green":
                            color = (0, 255, 0)
                            cv2.circle(final_frame, (x,y+h*2), radius, color, thickness)
                            cv2.circle(filtered_frame_bw, (x,y+h*2), radius, (255, 255, 255), thickness)
                            cv2.circle(filtered_frame_red_yellow_green, (x,y+h*2), radius,color, thickness)
                            cv2.rectangle(final_frame, (x-w, y-h), (x+w, y+h*3), color, radius)
                            cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h), (x+w, y+h*3), color, radius)
                            if grayscalewindow == True:
                                cv2.rectangle(filtered_frame_bw, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)
                            if redyellowgreenwindow == True:
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)
                            if finalwindow == True:
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)
                    elif approved == False and yolo_showunconfirmed == True:
                        if state == "Red":
                            color = (150, 150, 150)
                            cv2.circle(final_frame, (x,y-h), radius, color, thickness)
                            cv2.circle(filtered_frame_bw, (x,y-h), radius, (255, 255, 255), thickness)
                            cv2.circle(filtered_frame_red_yellow_green, (x,y-h), radius,color, thickness)
                            cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                            cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                            if grayscalewindow == True:
                                cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                            if redyellowgreenwindow == True:
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                            if finalwindow == True:
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                        if state == "Yellow":
                            color = (150, 150, 150)
                            cv2.circle(final_frame, (x,y), radius, color, thickness)
                            cv2.circle(filtered_frame_bw, (x,y), radius, (255, 255, 255), thickness)
                            cv2.circle(filtered_frame_red_yellow_green, (x,y), radius,color, thickness)
                            cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                            cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                            if grayscalewindow == True:
                                cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                            if redyellowgreenwindow == True:
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                            if finalwindow == True:
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                        if state == "Green":
                            color = (150, 150, 150)
                            cv2.circle(final_frame, (x,y+h*2), radius, color, thickness)
                            cv2.circle(filtered_frame_bw, (x,y+h*2), radius, (255, 255, 255), thickness)
                            cv2.circle(filtered_frame_red_yellow_green, (x,y+h*2), radius,color, thickness)
                            cv2.rectangle(final_frame, (x-w, y-h), (x+w, y+h*3), color, radius)
                            cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h), (x+w, y+h*3), color, radius)
                            if grayscalewindow == True:
                                cv2.rectangle(filtered_frame_bw, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)
                            if redyellowgreenwindow == True:
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                                cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)
                            if finalwindow == True:
                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                                cv2.rectangle(final_frame, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)

        except Exception as e:
            print("TrafficLightDetection - Tracking/YOLO Error: " + str(e))
    else:
        if anywindowopen == True:
            for i in range(len(coordinates)):
                x, y, w, h, state = coordinates[i]
                radius = round((w+h)/4)
                thickness = round((w+h)/30)
                if thickness < 1:
                    thickness = 1
                if state == "Red":
                    color = (0, 0, 255)
                    cv2.circle(final_frame, (x,y-h), radius, color, thickness)
                    cv2.circle(filtered_frame_bw, (x,y-h), radius, (255, 255, 255), thickness)
                    cv2.circle(filtered_frame_red_yellow_green, (x,y-h), radius,color, thickness)
                    cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                    cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                    if grayscalewindow == True:
                        cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                    if redyellowgreenwindow == True:
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                    if finalwindow == True:
                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                if state == "Yellow":
                    color = (0, 255, 255)
                    cv2.circle(final_frame, (x,y), radius, color, thickness)
                    cv2.circle(filtered_frame_bw, (x,y), radius, (255, 255, 255), thickness)
                    cv2.circle(filtered_frame_red_yellow_green, (x,y), radius,color, thickness)
                    cv2.rectangle(final_frame, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                    cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h*2), (x+w, y+h*2), color, radius)
                    if grayscalewindow == True:
                        cv2.rectangle(filtered_frame_bw, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                    if redyellowgreenwindow == True:
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                    if finalwindow == True:
                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h*1.5)), (x+round(w/2), y-round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                if state == "Green":
                    color = (0, 255, 0)
                    cv2.circle(final_frame, (x,y+h*2), radius, color, thickness)
                    cv2.circle(filtered_frame_bw, (x,y+h*2), radius, (255, 255, 255), thickness)
                    cv2.circle(filtered_frame_red_yellow_green, (x,y+h*2), radius,color, thickness)
                    cv2.rectangle(final_frame, (x-w, y-h), (x+w, y+h*3), color, radius)
                    cv2.rectangle(filtered_frame_red_yellow_green, (x-w, y-h), (x+w, y+h*3), color, radius)
                    if grayscalewindow == True:
                        cv2.rectangle(filtered_frame_bw, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)
                    if redyellowgreenwindow == True:
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                        cv2.rectangle(filtered_frame_red_yellow_green, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)
                    if finalwindow == True:
                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x+round(w/2), y+round(h/2)), (150, 150, 150), thickness)
                        cv2.rectangle(final_frame, (x-round(w/2), y+round(h/2)), (x+round(w/2), y+round(h*1.5)), (150, 150, 150), thickness)
                        cv2.rectangle(final_frame, (x-round(w/2), y+round(h*1.5)), (x+round(w/2), y+round(h*2.5)), (150, 150, 150), thickness)

    try:
        if yolo_detection == True:
            data_simple = None
            for i in range(len(trafficlights)):
                coord, id, approved = trafficlights[i]
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
        else:
            data_simple = None
            for i in range(len(coordinates)):
                x, y, w, h, state = coordinates[i]
                if state == "Red":
                    data_simple = "Red"
                    break
                elif state == "Yellow":
                    data_simple = "Yellow"
                    break
                elif state == "Green":
                    data_simple = "Green"
                    break
            data["TrafficLightDetection"] = {}
            data["TrafficLightDetection"]["simple"] = data_simple
            data["TrafficLightDetection"]["detailed"] = coordinates
    except Exception as e:
        print("TrafficLightDetection - Data Error: " + str(e))

    if reset_window == True:
        if grayscalewindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - B/W')
            except:
                pass
        if redyellowgreenwindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - Red/Yellow/Green')
            except:
                pass
        if finalwindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - Final')
            except:
                pass

    if grayscalewindow == True:
        window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - B/W')
        if window_handle == 0 or reset_window == True:
            cv2.namedWindow('Traffic Light Detection - B/W', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Light Detection - B/W', round(windowwidth*windowscale), round(windowheight*windowscale))
            cv2.setWindowProperty('Traffic Light Detection - B/W', cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow('Traffic Light Detection - B/W', filtered_frame_bw)
    if redyellowgreenwindow == True:      
        if performancemode == False:
            if detectyellowlight == False:
                window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - Red/Yellow/Green')
                if window_handle == 0 or reset_window == True:
                    cv2.namedWindow('Traffic Light Detection - Red/Yellow/Green', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('Traffic Light Detection - Red/Yellow/Green', round(windowwidth*windowscale), round(windowheight*windowscale))
                    cv2.setWindowProperty('Traffic Light Detection - Red/Yellow/Green', cv2.WND_PROP_TOPMOST, 1)
                cv2.imshow('Traffic Light Detection - Red/Yellow/Green', filtered_frame_red_yellow_green)
            else:
                window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - Red/Yellow/Green')
                if window_handle == 0 or reset_window == True:
                    cv2.namedWindow('Traffic Light Detection - Red/Yellow/Green', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('Traffic Light Detection - Red/Yellow/Green', round(windowwidth*windowscale), round(windowheight*windowscale))
                    cv2.setWindowProperty('Traffic Light Detection - Red/Yellow/Green', cv2.WND_PROP_TOPMOST, 1)
                cv2.imshow('Traffic Light Detection - Red/Yellow/Green', filtered_frame_red_yellow_green)
        else:
            window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - Red/Yellow/Green')
            if window_handle == 0 or reset_window == True:
                cv2.namedWindow('Traffic Light Detection - Red/Yellow/Green', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Traffic Light Detection - Red/Yellow/Green', round(windowwidth*windowscale), round(windowheight*windowscale))
                cv2.setWindowProperty('Traffic Light Detection - Red/Yellow/Green', cv2.WND_PROP_TOPMOST, 1)
            cv2.imshow('Traffic Light Detection - Red/Yellow/Green', filtered_frame_red_yellow_green)
    if finalwindow == True:
        window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - Final')
        if window_handle == 0 or reset_window == True:
            cv2.namedWindow('Traffic Light Detection - Final', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Light Detection - Final', round(windowwidth*windowscale), round(windowheight*windowscale))
            cv2.setWindowProperty('Traffic Light Detection - Final', cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow('Traffic Light Detection - Final', final_frame)
    if reset_window == True:
        reset_window = False
    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    UpdateSettings()
    loadYOLO()
    pass

def onDisable():
    pass

class UI():
    try: 
        
        def __init__(self, master) -> None:
            self.master = master 
            self.exampleFunction()
            resizeWindow(850,600)
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def tabFocused(self):
            resizeWindow(850,600)
            
        def UpdateSliderValue_scale(self):
            self.scale.set(self.scaleSlider.get())
            settings.CreateSettings("TrafficLightDetection", "scale", self.scaleSlider.get())
            UpdateSettings()
        def UpdateSliderValue_x1ofsc(self):
            self.x1ofsc.set(self.x1ofscSlider.get())
            settings.CreateSettings("TrafficLightDetection", "x1ofsc", self.x1ofscSlider.get())
            UpdateSettings()
        def UpdateSliderValue_y1ofsc(self):
            self.y1ofsc.set(self.y1ofscSlider.get())
            settings.CreateSettings("TrafficLightDetection", "y1ofsc", self.y1ofscSlider.get())
            UpdateSettings()
        def UpdateSliderValue_x2ofsc(self):
            self.x2ofsc.set(self.x2ofscSlider.get())
            settings.CreateSettings("TrafficLightDetection", "x2ofsc", self.x2ofscSlider.get())
            UpdateSettings()
        def UpdateSliderValue_y2ofsc(self):
            self.y2ofsc.set(self.y2ofscSlider.get())
            settings.CreateSettings("TrafficLightDetection", "y2ofsc", self.y2ofscSlider.get())
            UpdateSettings()
        def UpdateSliderValue_windowwidth(self):
            self.windowwidth.set(self.windowwidthSlider.get())
            settings.CreateSettings("TrafficLightDetection", "outputwindowwidth", self.windowwidthSlider.get())
            UpdateSettings()
        def UpdateSliderValue_windowheight(self):
            self.windowheight.set(self.windowheightSlider.get())
            settings.CreateSettings("TrafficLightDetection", "outputwindowheight", self.windowheightSlider.get())
            UpdateSettings()
        def UpdateSliderValue_minrectsize(self):
            self.minrectsize.set(self.minrectsizeSlider.get())
            settings.CreateSettings("TrafficLightDetection", "minrectsize", self.minrectsizeSlider.get())
            UpdateSettings()
        def UpdateSliderValue_maxrectsize(self):
            self.maxrectsize.set(self.maxrectsizeSlider.get())
            settings.CreateSettings("TrafficLightDetection", "maxrectsize", self.maxrectsizeSlider.get())
            UpdateSettings()
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() 
            except: pass
            
            self.root = tk.Canvas(self.master, width=750, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(0) 
            self.root.pack_propagate(0)
            
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            screencaptureFrame = ttk.Frame(notebook)
            screencaptureFrame.pack()
            outputwindowFrame = ttk.Frame(notebook)
            outputwindowFrame.pack()
            trackeraiFrame = ttk.Frame(notebook)
            trackeraiFrame.pack()
            advancedFrame = ttk.Frame(notebook)
            advancedFrame.pack()

            advancedNotebook = ttk.Notebook(advancedFrame)
            advancedNotebook.grid_anchor("center")
            advancedNotebook.grid()
            
            colorsettingsFrame = ttk.Frame(advancedNotebook)
            colorsettingsFrame.pack()
            filtersFrame = ttk.Frame(advancedNotebook)
            filtersFrame.pack()


            colorsettingsFrame.columnconfigure(0, weight=1)
            colorsettingsFrame.columnconfigure(1, weight=1)
            colorsettingsFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(colorsettingsFrame, "Color Settings", 0, 0, font=("Robot", 12, "bold"), columnspan=7)

            filtersFrame.columnconfigure(0, weight=1)
            filtersFrame.columnconfigure(1, weight=1)
            filtersFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(filtersFrame, "Filters", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            generalFrame.columnconfigure(0, weight=1)
            generalFrame.columnconfigure(1, weight=1)
            generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)
            
            screencaptureFrame.columnconfigure(0, weight=1)
            screencaptureFrame.columnconfigure(1, weight=1)
            screencaptureFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(screencaptureFrame, "Screen Capture", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            outputwindowFrame.columnconfigure(0, weight=1)
            outputwindowFrame.columnconfigure(1, weight=1)
            outputwindowFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(outputwindowFrame, "Output Window", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            trackeraiFrame.columnconfigure(0, weight=1)
            trackeraiFrame.columnconfigure(1, weight=1)
            trackeraiFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(trackeraiFrame, "Tracker/AI", 0, 0, font=("Robot", 12, "bold"), columnspan=7)

            advancedFrame.columnconfigure(0, weight=1)
            advancedFrame.columnconfigure(1, weight=1)
            advancedFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(advancedFrame, "Advanced", 0, 0, font=("Robot", 12, "bold"), columnspan=7)
            

            notebook.add(generalFrame, text=Translate("General"))
            notebook.add(screencaptureFrame, text=Translate("ScreenCapture"))
            notebook.add(outputwindowFrame, text=Translate("OutputWindow"))
            notebook.add(trackeraiFrame, text=Translate("Tracker/AI"))
            notebook.add(advancedFrame, text=Translate("Advanced"))
            advancedNotebook.add(colorsettingsFrame, text=Translate("ColorSettings"))
            advancedNotebook.add(filtersFrame, text=Translate("Filters"))
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()


            helpers.MakeCheckButton(outputwindowFrame, "Final Window\n--------------------\nIf enabled, the app creates a window with the result of the traffic light detection.", "TrafficLightDetection", "finalwindow", 1, 0, width=80, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(outputwindowFrame, "Grayscale Window\n---------------------------\nIf enabled, the app creates a window with the color masks combined in a grayscaled frame.", "TrafficLightDetection", "grayscalewindow", 2, 0, width=80, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(outputwindowFrame, "Red/Yellow/Green Window\n----------------------------\nIf enabled, the app creates a window with the color masks combined in a frame.", "TrafficLightDetection", "redyellowgreenwindow", 3, 0, width=80, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(outputwindowFrame, "Automatic Windowsize\n---------------------------------\nIf enabled, the Window Width and Window Height sliders will no longer have any effect\nand the output window keeps the aspect ratio of the captured frame. Set the size of the\noutput window with the Window Scale slider.", "TrafficLightDetection", "automaticwindowsize", 4, 0, width=80, callback=lambda:UpdateSettings())
            helpers.MakeEmptyLine(outputwindowFrame,5,0)

            helpers.MakeCheckButton(generalFrame, "Yellow Light Detection (not recommended)\n-------------------------------------------------------------\nIf enabled, the trafficlight detection tries to detect yellow traffic\nlights, but it is not recommended because it causes more wrong\ndetected traffic lights.", "TrafficLightDetection", "detectyellowlight", 4, 0, width=60, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Performance Mode (recommended)\n---------------------------------------------------\nIf enabled, the traffic light detection only detects red traffic lights,\nwhich increases performance, but does not reduce detection accuracy.", "TrafficLightDetection", "performancemode", 5, 0, width=60, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Advanced Settings\n---------------------------\nIf enabled, the traffic light detection uses the settings you set in\nthe Advanced tab. (could have a bad impact on performance)", "TrafficLightDetection", "advancedmode", 6, 0, width=60, callback=lambda:UpdateSettings())
            helpers.MakeEmptyLine(generalFrame,7,0)

            helpers.MakeCheckButton(filtersFrame, "Rect Size Filter", "TrafficLightDetection", "rectsizefilter", 3, 0, width=60, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(filtersFrame, "Width Height Ratio Filter", "TrafficLightDetection", "widthheightratiofilter", 4, 0, width=60, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(filtersFrame, "Pixel Percentage Filter", "TrafficLightDetection", "pixelpercentagefilter", 5, 0, width=60, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(filtersFrame, "Other Lights Filter", "TrafficLightDetection", "otherlightsofffilter", 6, 0, width=60, callback=lambda:UpdateSettings())

            helpers.MakeCheckButton(trackeraiFrame, "Do Yolo Detection confirmation\n---------------------------------------------\nIf enabled, the app tracks the detected traffic lights and confirms them with the YOLO object detection.\nWhat this means: higher accuracy, but a small lag every time the detection detects a new traffic light.", "TrafficLightDetection", "yolo_detection", 1, 0, width=100, callback=lambda:UpdateSettings())
            helpers.MakeCheckButton(trackeraiFrame, "Show unconfirmed traffic lights\n--------------------------------------------\nIf enabled, the app will show unconfirmed or wrongly detected traffic lights in gray in the output window.", "TrafficLightDetection", "yolo_showunconfirmed", 2, 0, width=100, callback=lambda:UpdateSettings())
            helpers.MakeEmptyLine(trackeraiFrame,3,0)
            helpers.MakeLabel(trackeraiFrame, "YOLOv5 Model:", 4, 0, sticky="nw")
            model_ui = tk.StringVar() 
            previous_model_ui = settings.GetSettings("TrafficLightDetection", "yolo_model")
            if previous_model_ui == "yolov5n":
                model_ui.set("yolov5n")
            if previous_model_ui == "yolov5s":
                model_ui.set("yolov5s")
            if previous_model_ui == "yolov5m":
                model_ui.set("yolov5m")
            if previous_model_ui == "yolov5l":
                model_ui.set("yolov5l")
            if previous_model_ui == "yolov5x":
                model_ui.set("yolov5x")
            def model_selection():
                self.model_ui = model_ui.get()
            yolov5n = ttk.Radiobutton(trackeraiFrame, text="YOLOv5n (fastest, lowest accuracy) RECOMMENDED", variable=model_ui, value="yolov5n", command=model_selection)
            yolov5n.grid(row=5, column=0, sticky="nw")
            yolov5s = ttk.Radiobutton(trackeraiFrame, text="YOLOv5s (fast, low accuracy)", variable=model_ui, value="yolov5s", command=model_selection)
            yolov5s.grid(row=6, column=0, sticky="nw")
            yolov5m = ttk.Radiobutton(trackeraiFrame, text="YOLOv5m (slow, medium accuracy)", variable=model_ui, value="yolov5m", command=model_selection)
            yolov5m.grid(row=7, column=0, sticky="nw")
            yolov5l = ttk.Radiobutton(trackeraiFrame, text="YOLOv5l (slow, high accuracy)", variable=model_ui, value="yolov5l", command=model_selection)
            yolov5l.grid(row=8, column=0, sticky="nw")
            yolov5x = ttk.Radiobutton(trackeraiFrame, text="YOLOv5x (slowest, highest accuracy)", variable=model_ui, value="yolov5x", command=model_selection)
            yolov5x.grid(row=9, column=0, sticky="nw")
            model_selection()
            helpers.MakeButton(trackeraiFrame, "Save and Load Model\n-------------------------------\nLoading the model could take some time.\nIt's normal that the app won't respond for a while.", self.save_and_load_model, 10, 0, width=50, sticky="nw")

            helpers.MakeCheckButton(screencaptureFrame, "Use Full Frame\n----------------------\nIf enabled, the screencapture for the traffic light detection uses the top ⅔ of the screen for\nthe traffic light detection. (not recommended, could have a bad impact on performance)\n\nTo set own screencapture coordinates disable Use Full Frame and use sliders below.", "TrafficLightDetection", "usefullframe", 1, 0, width=80, callback=lambda:UpdateSettings())
            
            self.x1ofscSlider = tk.Scale(screencaptureFrame, from_=0, to=screen_width-1, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSliderValue_x1ofsc())
            self.x1ofscSlider.set(settings.GetSettings("TrafficLightDetection", "x1ofsc", 0))
            self.x1ofscSlider.grid(row=3, column=0, padx=10, pady=0, columnspan=2)
            self.x1ofsc = helpers.MakeComboEntry(screencaptureFrame, "X1 (topleft)", "TrafficLightDetection", "x1ofsc", 3,0)

            self.y1ofscSlider = tk.Scale(screencaptureFrame, from_=0, to=screen_height-1, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSliderValue_y1ofsc())
            self.y1ofscSlider.set(settings.GetSettings("TrafficLightDetection", "y1ofsc", 0))
            self.y1ofscSlider.grid(row=5, column=0, padx=10, pady=0, columnspan=2)
            self.y1ofsc = helpers.MakeComboEntry(screencaptureFrame, "Y1 (topleft)", "TrafficLightDetection", "y1ofsc", 5,0)

            self.x2ofscSlider = tk.Scale(screencaptureFrame, from_=0, to=screen_width-1, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSliderValue_x2ofsc())
            self.x2ofscSlider.set(settings.GetSettings("TrafficLightDetection", "x2ofsc", screen_width-1))
            self.x2ofscSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.x2ofsc = helpers.MakeComboEntry(screencaptureFrame, "X2 (buttomright)", "TrafficLightDetection", "x2ofsc", 7,0)

            self.y2ofscSlider = tk.Scale(screencaptureFrame, from_=0, to=screen_height-1, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSliderValue_y2ofsc())
            self.y2ofscSlider.set(settings.GetSettings("TrafficLightDetection", "y2ofsc", round(screen_height/1.5)-1))
            self.y2ofscSlider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.y2ofsc = helpers.MakeComboEntry(screencaptureFrame, "Y2 (buttomright)", "TrafficLightDetection", "y2ofsc", 9,0)

            helpers.MakeButton(screencaptureFrame, "Open/Refresh preview", lambda: screencapture_open_refresh(), 11, 0, width=30, sticky="w")
            helpers.MakeButton(screencaptureFrame, "Close preview", lambda: screencapture_close(), 12, 0, width=30, sticky="w")

            def screencapture_open_refresh():
                self.UpdateSliderValue_x1ofsc()
                self.UpdateSliderValue_y1ofsc()
                self.UpdateSliderValue_x2ofsc()
                self.UpdateSliderValue_y2ofsc()
                if settings.GetSettings("TrafficLightDetection", "usefullframe", True) == False:
                    x1_preview = self.x1ofscSlider.get()
                    y1_preview = self.y1ofscSlider.get()
                    x2_preview = self.x2ofscSlider.get()
                    y2_preview = self.y2ofscSlider.get()
                    screenshot = cv2.cvtColor(np.array(pyautogui.screenshot(region=(x1_preview, y1_preview, x2_preview - x1_preview, y2_preview - y1_preview))), cv2.COLOR_RGB2BGR)
                else:
                    x1_preview = 0
                    y1_preview = 0
                    x2_preview = screen_width-1
                    y2_preview = round(screen_height/1.5)-1
                    screenshot = cv2.cvtColor(np.array(pyautogui.screenshot(region=(x1_preview, y1_preview, x2_preview - x1_preview, y2_preview - y1_preview))), cv2.COLOR_RGB2BGR)
                    current_text = '"Use Full Frame" enabled, disable to set own screencapture area'
                    width_target_current_text = (x2_preview - x1_preview)*0.9
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
                    cv2.putText(screenshot, current_text, (round((x2-x1)/2 - width_current_text/2), height_current_text*2), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
                cv2.namedWindow('Screencapture Preview', cv2.WINDOW_NORMAL)
                cv2.setWindowProperty('Screencapture Preview', cv2.WND_PROP_TOPMOST, 1)
                cv2.resizeWindow('Screencapture Preview', round((x2-x1)/2), round((y2-y1)/2))
                cv2.imshow('Screencapture Preview', screenshot)
                cv2.waitKey(1)
                
            def screencapture_close():
                try: 
                    cv2.destroyWindow('Screencapture Preview')
                except: 
                    pass

            self.windowwidthSlider = tk.Scale(outputwindowFrame, from_=round(screen_width/20), to=screen_width, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateSliderValue_windowwidth())
            self.windowwidthSlider.set(settings.GetSettings("TrafficLightDetection", "outputwindowwidth", round(screen_width/2)))
            self.windowwidthSlider.grid(row=6, column=0, padx=10, pady=0, columnspan=2)
            self.windowwidth = helpers.MakeComboEntry(outputwindowFrame, "Window Width", "TrafficLightDetection", "outputwindowwidth", 6,0, labelwidth=13, width=10)

            self.windowheightSlider = tk.Scale(outputwindowFrame, from_=round(screen_height/20), to=screen_height, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateSliderValue_windowheight())
            self.windowheightSlider.set(settings.GetSettings("TrafficLightDetection", "outputwindowheight", round(screen_height/3)))
            self.windowheightSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.windowheight = helpers.MakeComboEntry(outputwindowFrame, "Window Height", "TrafficLightDetection", "outputwindowheight", 7,0, labelwidth=13, width=10)

            self.scaleSlider = tk.Scale(outputwindowFrame, from_=0.1, to=2, resolution=0.01, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateSliderValue_scale())
            self.scaleSlider.set(settings.GetSettings("TrafficLightDetection", "scale", 0.5))
            self.scaleSlider.grid(row=8, column=0, padx=10, pady=0, columnspan=2)
            self.scale = helpers.MakeComboEntry(outputwindowFrame, "Window Scale", "TrafficLightDetection", "scale", 8,0, labelwidth=13, width=10)

            self.minrectsizeSlider = tk.Scale(filtersFrame, from_=1, to=round(screen_width / 2), resolution=1, orient=tk.HORIZONTAL, length=700, command=lambda x: self.UpdateSliderValue_minrectsize())
            self.minrectsizeSlider.set(settings.GetSettings("TrafficLightDetection", "minrectsize", round(screen_width / 240)))
            self.minrectsizeSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.minrectsize = helpers.MakeComboEntry(filtersFrame, "Min. Traffic Light Size Filter", "TrafficLightDetection", "minrectsize", 8,0, labelwidth=80, width=20)

            self.maxrectsizeSlider = tk.Scale(filtersFrame, from_=1, to=round(screen_width / 2), resolution=1, orient=tk.HORIZONTAL, length=700, command=lambda x: self.UpdateSliderValue_maxrectsize())
            self.maxrectsizeSlider.set(settings.GetSettings("TrafficLightDetection", "maxrectsize", round(screen_width / 10)))
            self.maxrectsizeSlider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.maxrectsize = helpers.MakeComboEntry(filtersFrame, "Max. Traffic Light Size Filter", "TrafficLightDetection", "maxrectsize", 10,0, labelwidth=80, width=20)

            self.upperredr = helpers.MakeComboEntry(colorsettingsFrame, "RED:         Upper R:", "TrafficLightDetection", "upperred_r", 2, 0, labelwidth=20, width=7)
            self.upperredg = helpers.MakeComboEntry(colorsettingsFrame, "Upper G:", "TrafficLightDetection", "upperred_g", 2, 2, labelwidth=13, width=7)
            self.upperredb = helpers.MakeComboEntry(colorsettingsFrame, "Upper B:", "TrafficLightDetection", "upperred_b", 2, 4, labelwidth=13, width=7)
            self.lowerredr = helpers.MakeComboEntry(colorsettingsFrame, "RED:         Lower R:", "TrafficLightDetection", "lowerred_r", 3, 0, labelwidth=20, width=7)
            self.lowerredg = helpers.MakeComboEntry(colorsettingsFrame, "Lower G:", "TrafficLightDetection", "lowerred_g", 3, 2, labelwidth=13, width=7)
            self.lowerredb = helpers.MakeComboEntry(colorsettingsFrame, "Lower B:", "TrafficLightDetection", "lowerred_b", 3, 4, labelwidth=13, width=7)
            self.upperyellowr = helpers.MakeComboEntry(colorsettingsFrame, "YELLOW:  Upper R:", "TrafficLightDetection", "upperyellow_r", 4, 0, labelwidth=20, width=7)
            self.upperyellowg = helpers.MakeComboEntry(colorsettingsFrame, "Upper G:", "TrafficLightDetection", "upperyellow_g", 4, 2, labelwidth=13, width=7)
            self.upperyellowb = helpers.MakeComboEntry(colorsettingsFrame, "Upper B:", "TrafficLightDetection", "upperyellow_b", 4, 4, labelwidth=13, width=7)
            self.loweryellowr = helpers.MakeComboEntry(colorsettingsFrame, "YELLOW:  Lower R:", "TrafficLightDetection", "loweryellow_r", 5, 0, labelwidth=20, width=7)
            self.loweryellowg = helpers.MakeComboEntry(colorsettingsFrame, "Lower G:", "TrafficLightDetection", "loweryellow_g", 5, 2, labelwidth=13, width=7)
            self.loweryellowb = helpers.MakeComboEntry(colorsettingsFrame, "Lower B:", "TrafficLightDetection", "loweryellow_b", 5, 4, labelwidth=13, width=7)
            self.uppergreenr = helpers.MakeComboEntry(colorsettingsFrame, "GREEN:    Upper R:", "TrafficLightDetection", "uppergreen_r", 6, 0, labelwidth=20, width=7)
            self.uppergreeng = helpers.MakeComboEntry(colorsettingsFrame, "Upper G:", "TrafficLightDetection", "uppergreen_g", 6, 2, labelwidth=13, width=7)
            self.uppergreenb = helpers.MakeComboEntry(colorsettingsFrame, "Upper B:", "TrafficLightDetection", "uppergreen_b", 6, 4, labelwidth=13, width=7)
            self.lowergreenr = helpers.MakeComboEntry(colorsettingsFrame, "GREEN:    Lower R:", "TrafficLightDetection", "lowergreen_r", 7, 0, labelwidth=20, width=7)
            self.lowergreeng = helpers.MakeComboEntry(colorsettingsFrame, "Lower G:", "TrafficLightDetection", "lowergreen_g", 7, 2, labelwidth=13, width=7)
            self.lowergreenb = helpers.MakeComboEntry(colorsettingsFrame, "Lower B:", "TrafficLightDetection", "lowergreen_b", 7, 4, labelwidth=13, width=7)
            helpers.MakeButton(colorsettingsFrame, "Save", command=self.save, row=15, column=0, sticky="w")

            helpers.MakeLabel(colorsettingsFrame, "", 13, 0, columnspan=7)
            helpers.MakeLabel(colorsettingsFrame, "", 14, 0, columnspan=7)
            helpers.MakeButton(colorsettingsFrame, "Reset", command=self.resetadvancedcolorstodefault, row=15, column=5)
            helpers.MakeEmptyLine(colorsettingsFrame,12,1)
            helpers.MakeEmptyLine(colorsettingsFrame,13,1)
            helpers.MakeEmptyLine(colorsettingsFrame,14,1)
            helpers.MakeButton(filtersFrame, "Reset", command=self.resetadvancedfilterstodefault, row=15, column=1, width=20)
            helpers.MakeEmptyLine(filtersFrame,14,1)
            helpers.MakeButton(generalFrame, "Reset Advanced Settings\nto Default\n------------------------------------", command=self.resetalladvancedsettingstodefault, row=6, column=1, width=32,)
            
        
        def save(self):
            
            try:
                self.upperredr.get()
            except:
                self.upperredr.set(255)
            try:
                self.upperredg.get()
            except:
                self.upperredg.set(110)
            try:
                self.upperredb.get()
            except:
                self.upperredb.set(110)
            try:
                self.lowerredr.get()
            except:
                self.lowerredr.set(200)
            try:
                self.lowerredg.get()
            except:
                self.lowerredg.set(0)
            try:
                self.lowerredb.get()
            except:
                self.lowerredb.set(0)
            try:
                self.upperyellowr.get()
            except:
                self.upperyellowr.set(255)
            try:
                self.upperyellowg.get()
            except:
                self.upperyellowg.set(240)
            try:
                self.upperyellowb.get()
            except:
                self.upperyellowb.set(170)
            try:
                self.loweryellowr.get()
            except:
                self.loweryellowr.set(200)
            try:
                self.loweryellowg.get()
            except:
                self.loweryellowg.set(170)
            try:
                self.loweryellowb.get()
            except:
                self.loweryellowb.set(50)
            try:
                self.uppergreenr.get()
            except:
                self.uppergreenr.set(150)
            try:
                self.uppergreeng.get()
            except:
                self.uppergreeng.set(255)
            try:
                self.uppergreenb.get()
            except:
                self.uppergreenb.set(230)
            try:
                self.lowergreenr.get()
            except:
                self.lowergreenr.set(0)
            try:
                self.lowergreeng.get()
            except:
                self.lowergreeng.set(200)
            try:
                self.lowergreenb.get()
            except:
                self.lowergreenb.set(0)
            if not (0 <= self.upperredr.get() <= 255):
                self.upperredr.set(255)
            if not (0 <= self.upperredg.get() <= 255):
                self.upperredg.set(110)
            if not (0 <= self.upperredb.get() <= 255):
                self.upperredb.set(110)
            if not (0 <= self.lowerredr.get() <= 255):
                self.lowerredr.set(200)  
            if not (0 <= self.lowerredg.get() <= 255):
                self.lowerredg.set(0)
            if not (0 <= self.lowerredb.get() <= 255):
                self.lowerredb.set(0)
            if not (0 <= self.upperyellowr.get() <= 255):
                self.upperyellowr.set(255)
            if not (0 <= self.upperyellowg.get() <= 255):
                self.upperyellowg.set(240)
            if not (0 <= self.upperyellowb.get() <= 255):
                self.upperyellowb.set(170)
            if not (0 <= self.loweryellowr.get() <= 255):
                self.loweryellowr.set(200)
            if not (0 <= self.loweryellowg.get() <= 255):
                self.loweryellowg.set(170)
            if not (0 <= self.loweryellowb.get() <= 255):
                self.loweryellowb.set(50)
            if not (0 <= self.uppergreenr.get() <= 255):
                self.uppergreenr.set(150)
            if not (0 <= self.uppergreeng.get() <= 255):
                self.uppergreeng.set(255)
            if not (0 <= self.uppergreenb.get() <= 255):
                self.uppergreenb.set(230)
            if not (0 <= self.lowergreenr.get() <= 255):
                self.lowergreenr.set(0)
            if not (0 <= self.lowergreeng.get() <= 255):
                self.lowergreeng.set(200)
            if not (0 <= self.lowergreenb.get() <= 255):
                self.lowergreenb.set(0)
            settings.CreateSettings("TrafficLightDetection", "upperred_r", self.upperredr.get())
            settings.CreateSettings("TrafficLightDetection", "upperred_g", self.upperredg.get())
            settings.CreateSettings("TrafficLightDetection", "upperred_b", self.upperredb.get())
            settings.CreateSettings("TrafficLightDetection", "lowerred_r", self.lowerredr.get())
            settings.CreateSettings("TrafficLightDetection", "lowerred_g", self.lowerredg.get())
            settings.CreateSettings("TrafficLightDetection", "lowerred_b", self.lowerredb.get())
            settings.CreateSettings("TrafficLightDetection", "upperyellow_r", self.upperyellowr.get())
            settings.CreateSettings("TrafficLightDetection", "upperyellow_g", self.upperyellowg.get())
            settings.CreateSettings("TrafficLightDetection", "upperyellow_b", self.upperyellowb.get())
            settings.CreateSettings("TrafficLightDetection", "loweryellow_r", self.loweryellowr.get())
            settings.CreateSettings("TrafficLightDetection", "loweryellow_g", self.loweryellowg.get())
            settings.CreateSettings("TrafficLightDetection", "loweryellow_b", self.loweryellowb.get())
            settings.CreateSettings("TrafficLightDetection", "uppergreen_r", self.uppergreenr.get())
            settings.CreateSettings("TrafficLightDetection", "uppergreen_g", self.uppergreeng.get())
            settings.CreateSettings("TrafficLightDetection", "uppergreen_b", self.uppergreenb.get())
            settings.CreateSettings("TrafficLightDetection", "lowergreen_r", self.lowergreenr.get())
            settings.CreateSettings("TrafficLightDetection", "lowergreen_g", self.lowergreeng.get())
            settings.CreateSettings("TrafficLightDetection", "lowergreen_b", self.lowergreenb.get())
            UpdateSettings()

        
        def resetadvancedcolorstodefault(self):
            settings.CreateSettings("TrafficLightDetection", "upperred_r", 255)
            settings.CreateSettings("TrafficLightDetection", "upperred_g", 110)
            settings.CreateSettings("TrafficLightDetection", "upperred_b", 110)
            settings.CreateSettings("TrafficLightDetection", "lowerred_r", 200)
            settings.CreateSettings("TrafficLightDetection", "lowerred_g", 0)
            settings.CreateSettings("TrafficLightDetection", "lowerred_b", 0)
            settings.CreateSettings("TrafficLightDetection", "upperyellow_r", 255)
            settings.CreateSettings("TrafficLightDetection", "upperyellow_g", 240)
            settings.CreateSettings("TrafficLightDetection", "upperyellow_b", 170)
            settings.CreateSettings("TrafficLightDetection", "loweryellow_r", 200)
            settings.CreateSettings("TrafficLightDetection", "loweryellow_g", 170)
            settings.CreateSettings("TrafficLightDetection", "loweryellow_b", 50)
            settings.CreateSettings("TrafficLightDetection", "uppergreen_r", 150)
            settings.CreateSettings("TrafficLightDetection", "uppergreen_g", 255)
            settings.CreateSettings("TrafficLightDetection", "uppergreen_b", 230)
            settings.CreateSettings("TrafficLightDetection", "lowergreen_r", 0)
            settings.CreateSettings("TrafficLightDetection", "lowergreen_g", 200)
            settings.CreateSettings("TrafficLightDetection", "lowergreen_b", 0)
            self.upperredr.set(255)
            self.upperredg.set(110)
            self.upperredb.set(110)
            self.lowerredr.set(200)
            self.lowerredg.set(0)
            self.lowerredb.set(0)
            self.upperyellowr.set(255)
            self.upperyellowg.set(240)
            self.upperyellowb.set(170)
            self.loweryellowr.set(200)
            self.loweryellowg.set(170)
            self.loweryellowb.set(50)
            self.uppergreenr.set(150)
            self.uppergreeng.set(255)
            self.uppergreenb.set(230)
            self.lowergreenr.set(0)
            self.lowergreeng.set(200)
            self.lowergreenb.set(0)
            UpdateSettings()

        def resetadvancedfilterstodefault(self):
            settings.CreateSettings("TrafficLightDetection", "rectsizefilter", True)
            settings.CreateSettings("TrafficLightDetection", "widthheightratiofilter", True)
            settings.CreateSettings("TrafficLightDetection", "pixelpercentagefilter", True)
            settings.CreateSettings("TrafficLightDetection", "otherlightsofffilter", True)

            settings.CreateSettings("TrafficLightDetection", "minrectsize", round(screen_width / 240))
            settings.CreateSettings("TrafficLightDetection", "maxrectsize", round(screen_width / 10))
            self.minrectsizeSlider.set(round(screen_width / 240))
            self.minrectsize.set(round(screen_width / 240))
            self.maxrectsizeSlider.set(round(screen_width / 10))
            self.maxrectsize.set(round(screen_width / 10))
            self.exampleFunction()
            UpdateSettings()

        def resetalladvancedsettingstodefault(self):
            settings.CreateSettings("TrafficLightDetection", "rectsizefilter", True)
            settings.CreateSettings("TrafficLightDetection", "widthheightratiofilter", True)
            settings.CreateSettings("TrafficLightDetection", "pixelpercentagefilter", True)
            settings.CreateSettings("TrafficLightDetection", "otherlightsofffilter", True)

            settings.CreateSettings("TrafficLightDetection", "minrectsize", round(screen_width / 240))
            settings.CreateSettings("TrafficLightDetection", "maxrectsize", round(screen_width / 10))

            settings.CreateSettings("TrafficLightDetection", "upperred_r", 255)
            settings.CreateSettings("TrafficLightDetection", "upperred_g", 110)
            settings.CreateSettings("TrafficLightDetection", "upperred_b", 110)
            settings.CreateSettings("TrafficLightDetection", "lowerred_r", 200)
            settings.CreateSettings("TrafficLightDetection", "lowerred_g", 0)
            settings.CreateSettings("TrafficLightDetection", "lowerred_b", 0)
            settings.CreateSettings("TrafficLightDetection", "upperyellow_r", 255)
            settings.CreateSettings("TrafficLightDetection", "upperyellow_g", 240)
            settings.CreateSettings("TrafficLightDetection", "upperyellow_b", 170)
            settings.CreateSettings("TrafficLightDetection", "loweryellow_r", 200)
            settings.CreateSettings("TrafficLightDetection", "loweryellow_g", 170)
            settings.CreateSettings("TrafficLightDetection", "loweryellow_b", 50)
            settings.CreateSettings("TrafficLightDetection", "uppergreen_r", 150)
            settings.CreateSettings("TrafficLightDetection", "uppergreen_g", 255)
            settings.CreateSettings("TrafficLightDetection", "uppergreen_b", 230)
            settings.CreateSettings("TrafficLightDetection", "lowergreen_r", 0)
            settings.CreateSettings("TrafficLightDetection", "lowergreen_g", 200)
            settings.CreateSettings("TrafficLightDetection", "lowergreen_b", 0)
            self.upperredr.set(255)
            self.upperredg.set(110)
            self.upperredb.set(110)
            self.lowerredr.set(200)
            self.lowerredg.set(0)
            self.lowerredb.set(0)
            self.upperyellowr.set(255)
            self.upperyellowg.set(240)
            self.upperyellowb.set(170)
            self.loweryellowr.set(200)
            self.loweryellowg.set(170)
            self.loweryellowb.set(50)
            self.uppergreenr.set(150)
            self.uppergreeng.set(255)
            self.uppergreenb.set(230)
            self.lowergreenr.set(0)
            self.lowergreeng.set(200)
            self.lowergreenb.set(0)
            self.exampleFunction()
            UpdateSettings()

        def save_and_load_model(self):
            global yolo_model_loaded
            yolo_model_loaded = False
            settings.CreateSettings("TrafficLightDetection", "yolo_model", self.model_ui)
            loadYOLO()
            UpdateSettings()
        
        def update(self, data): 
            self.root.update()
            
    except Exception as ex:
        print(ex.args)