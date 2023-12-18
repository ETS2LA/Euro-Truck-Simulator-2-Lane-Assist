"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import switchSelectedPlugin, resizeWindow

PluginInfo = PluginInformation(
    name="TrafficLightDetection", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will detect the traffic lights currently visible.",
    version="0.3",
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
import dxcam
import time
import pyautogui
import math

screen_width, screen_height = pyautogui.size()

finalwindow = True
grayscalewindow = True
redgreenwindow = True

coordinates = []
trafficlights = []
trafficlightframes = []

lower_red = np.array([200, 0, 0])
upper_red = np.array([255, 110, 110])
lower_green = np.array([0, 200, 0])
upper_green = np.array([150, 255, 230])
lower_yellow = np.array([200, 170, 50])
upper_yellow = np.array([255, 240, 170])


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
    global redgreenwindow
    global anywindowopen
    global automaticwindowsize
    global detectyellowlight
    global performancemode
    global advancedmode
    global windowscale
    global textsize
    global usefullframe
    global trafficlighttracking
    global aiconfirmation
    global coordinates
    global trafficlights
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
    redgreenwindow = settings.GetSettings("TrafficLightDetection", "redgreenwindow", False)
    automaticwindowsize = settings.GetSettings("TrafficLightDetection", "automaticwindowsize", True)
    detectyellowlight = settings.GetSettings("TrafficLightDetection", "detectyellowlight", False)
    performancemode = settings.GetSettings("TrafficLightDetection", "performancemode", True)
    advancedmode = settings.GetSettings("TrafficLightDetection", "advancedmode", False)
    usefullframe = settings.GetSettings("TrafficLightDetection", "usefullframe", True)
    windowscale = float(settings.GetSettings("TrafficLightDetection", "scale", 0.5))
    textsize = float(settings.GetSettings("TrafficLightDetection", "textsize", 1))
    x1 = settings.GetSettings("TrafficLightDetection", "x1ofsc", 0)
    y1 = settings.GetSettings("TrafficLightDetection", "y1ofsc", 0)
    x2 = settings.GetSettings("TrafficLightDetection", "x2ofsc", screen_width-1)
    y2 = settings.GetSettings("TrafficLightDetection", "y2ofsc", round(screen_height/1.5)-1)

    rectsizefilter = settings.GetSettings("TrafficLightDetection", "rectsizefilter", True)
    widthheightratiofilter = settings.GetSettings("TrafficLightDetection", "widthheightratiofilter", True)
    pixelpercentagefilter = settings.GetSettings("TrafficLightDetection", "pixelpercentagefilter", True)
    otherlightsofffilter = settings.GetSettings("TrafficLightDetection", "otherlightsofffilter", True)

    trafficlighttracking = settings.GetSettings("TrafficLightDetection", "trafficlighttracking", False)
    aiconfirmation = settings.GetSettings("TrafficLightDetection", "aiconfirmation", False)
    if aiconfirmation == True:
        trafficlighttracking = True
        settings.CreateSettings("TrafficLightDetection", "trafficlighttracking", True)
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

    if grayscalewindow == True:
        cv2.namedWindow('Traffic Light Detection - B/W', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Traffic Light Detection - B/W', round(windowwidth*windowscale), round(windowheight*windowscale))
        cv2.setWindowProperty('Traffic Light Detection - B/W', cv2.WND_PROP_TOPMOST, 1)
        startframe = np.zeros((round(windowheight * windowscale), round(windowwidth * windowscale), 3))
        cv2.putText(startframe, "enable app", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA) 
        cv2.imshow('Traffic Light Detection - B/W', startframe)
    if redgreenwindow == True:
        cv2.namedWindow('Traffic Light Detection - Red/Green', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Traffic Light Detection - Red/Green', round(windowwidth*windowscale), round(windowheight*windowscale))
        cv2.setWindowProperty('Traffic Light Detection - Red/Green', cv2.WND_PROP_TOPMOST, 1)
        startframe = np.zeros((round(windowheight * windowscale), round(windowwidth * windowscale), 3))
        cv2.putText(startframe, "enable app", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA) 
        cv2.imshow('Traffic Light Detection - Red/Green', startframe)
    if finalwindow == True:
        cv2.namedWindow('Traffic Light Detection - Final', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Traffic Light Detection - Final', round(windowwidth*windowscale), round(windowheight*windowscale))
        cv2.setWindowProperty('Traffic Light Detection - Final', cv2.WND_PROP_TOPMOST, 1)
        startframe = np.zeros((round(windowheight * windowscale), round(windowwidth * windowscale), 3))
        cv2.putText(startframe, "enable app", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA) 
        cv2.imshow('Traffic Light Detection - Final', startframe)
    
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

    if ((finalwindow + grayscalewindow + redgreenwindow) > 0):
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
    if urr == None:
        settings.CreateSettings("TrafficLightDetection", "upperred_r", 255)
        urr = 255
    urg = settings.GetSettings("TrafficLightDetection", "upperred_g")
    if urg == None:
        settings.CreateSettings("TrafficLightDetection", "upperred_g", 110)
        urg = 110
    urb = settings.GetSettings("TrafficLightDetection", "upperred_b")
    if urb == None:
        settings.CreateSettings("TrafficLightDetection", "upperred_b", 110)
        urb = 110
    lrr = settings.GetSettings("TrafficLightDetection", "lowerred_r")
    if lrr == None:
        settings.CreateSettings("TrafficLightDetection", "lowerred_r", 200)
        lrr = 200
    lrg = settings.GetSettings("TrafficLightDetection", "lowerred_g")
    if lrg == None:
        settings.CreateSettings("TrafficLightDetection", "lowerred_g", 0)
        lrg = 0
    lrb = settings.GetSettings("TrafficLightDetection", "lowerred_b")
    if lrb == None:
        settings.CreateSettings("TrafficLightDetection", "lowerred_b", 0)
        lrb = 0
    uyr = settings.GetSettings("TrafficLightDetection", "upperyellow_r")
    if uyr == None:
        settings.CreateSettings("TrafficLightDetection", "upperyellow_r", 255)
        uyr = 255
    uyg = settings.GetSettings("TrafficLightDetection", "upperyellow_g")
    if uyg == None:
        settings.CreateSettings("TrafficLightDetection", "upperyellow_g", 240)
        uyg = 240
    uyb = settings.GetSettings("TrafficLightDetection", "upperyellow_b")
    if uyb == None:
        settings.CreateSettings("TrafficLightDetection", "upperyellow_b", 170)
        uyb = 170
    lyr = settings.GetSettings("TrafficLightDetection", "loweryellow_r")
    if lyr == None:
        settings.CreateSettings("TrafficLightDetection", "loweryellow_r", 200)
        lyr = 200
    lyg = settings.GetSettings("TrafficLightDetection", "loweryellow_g")
    if lyg == None:
        settings.CreateSettings("TrafficLightDetection", "loweryellow_g", 170)
        lyg = 170
    lyb = settings.GetSettings("TrafficLightDetection", "loweryellow_b")
    if lyb == None:
        settings.CreateSettings("TrafficLightDetection", "loweryellow_b", 50)
        lyb = 50
    ugr = settings.GetSettings("TrafficLightDetection", "uppergreen_r")
    if ugr == None:
        settings.CreateSettings("TrafficLightDetection", "uppergreen_r", 150)
        ugr = 150
    ugg = settings.GetSettings("TrafficLightDetection", "uppergreen_g")
    if ugg == None:
        settings.CreateSettings("TrafficLightDetection", "uppergreen_g", 255)
        ugg = 255
    ugb = settings.GetSettings("TrafficLightDetection", "uppergreen_b")
    if ugb == None:
        settings.CreateSettings("TrafficLightDetection", "uppergreen_b", 230)
        ugb = 230
    lgr = settings.GetSettings("TrafficLightDetection", "lowergreen_r")
    if lgr == None:
        settings.CreateSettings("TrafficLightDetection", "lowergreen_r", 0)
        lgr = 0
    lgg = settings.GetSettings("TrafficLightDetection", "lowergreen_g")
    if lgg == None:
        settings.CreateSettings("TrafficLightDetection", "lowergreen_g", 200)
        lgg = 200
    lgb = settings.GetSettings("TrafficLightDetection", "lowergreen_b")
    if lgb == None:
        settings.CreateSettings("TrafficLightDetection", "lowergreen_b", 0)
        lgb = 0

    upper_red_advanced = np.array([urr, urg, urb])
    lower_red_advanced = np.array([lrr, lrg, lrb])
    upper_yellow_advanced = np.array([uyr, uyg, uyb])
    lower_yellow_advanced = np.array([lyr, lyg, lyb])
    upper_green_advanced = np.array([ugr, ugg, ugb])
    lower_green_advanced = np.array([lgr, lgg, lgb])
    


# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    global coordinates
    global trafficlights
    global trafficlightframes
    
    try:
        frame = data["frameFull"]
        if usefullframe == False and x2-x1 > 0 and y2-y1 > 0:
            frame = frame[y1:y1+(y2-y1), x1:x1+(x2-x1)]
        else: 
            frame = frame[0:round(screen_height/1.5), 0:screen_width] 
    except:
        return data
    
    if frame is None: return data
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ALL CASES:
    # (they are in order how to code below "reads" them)

    # True: anywindowopen --- False: trafficlighttracking, advancedmode, performancemode, detectyellowlight
    # True: anywindowopen, detectyellowlight --- False: trafficlighttracking, advancedmode, performancemode
    # True: anywindowopen, performancemode --- False: trafficlighttracking, advancedmode
    # True: --- False: trafficlighttracking, advancedmode, anywindowopen, performancemode, detectyellowlight
    # True: detectyellowlight --- False: trafficlighttracking, advancedmode, anywindowopen, performancemode
    # True: performancemode --- False: trafficlighttracking, advancedmode, anywindowopen
    # True: advancedmode, anywindowopen --- False: trafficlighttracking, performancemode, detectyellowlight
    # True: advancedmode, anywindowopen, detectyellowlight --- False: trafficlighttracking, performancemode
    # True: advancedmode, anywindowopen, performancemode --- False: trafficlighttracking
    # True: advancedmode --- False: trafficlighttracking, anywindowopen, performancemode, detectyellowlight
    # True: advancedmode, detectyellowlight --- False: trafficlighttracking, anywindowopen, performancemode
    # True: advancedmode, performancemode --- False: trafficlighttracking, anywindowopen
    # True: trafficlighttracking, anywindowopen --- False: advancedmode, performancemode, detectyellowlight
    # True: trafficlighttracking, anywindowopen, detectyellowlight --- False: advancedmode, performancemode
    # True: trafficlighttracking, anywindowopen, performancemode --- False: advancedmode
    # True: trafficlighttracking --- False: advancedmode, anywindowopen, performancemode, detectyellowlight
    # True: trafficlighttracking, detectyellowlight --- False: advancedmode, anywindowopen, performancemode
    # True: trafficlighttracking, performancemode --- False: advancedmode, anywindowopen
    # True: trafficlighttracking, advancedmode, anywindowopen --- False: performancemode, detectyellowlight
    # True: trafficlighttracking, advancedmode, anywindowopen, detectyellowlight --- False: performancemode
    # True: trafficlighttracking, advancedmode, anywindowopen, performancemode --- False: 
    # True: trafficlighttracking, advancedmode --- False: anywindowopen, performancemode, detectyellowlight
    # True: trafficlighttracking, advancedmode, detectyellowlight --- False: anywindowopen, performancemode
    # True: trafficlighttracking, advancedmode, performancemode --- False: anywindowopen

    last_coordinates = coordinates.copy()
    coordinates = []

    if trafficlighttracking == False:
        if advancedmode == False:
            if anywindowopen == True:
                if performancemode == False:
                    if detectyellowlight == False:
                        # True: anywindowopen --- False: trafficlighttracking, advancedmode, performancemode, detectyellowlight
                        mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                        mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)

                        filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                        color = (0, 0, 255) if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else (0, 255, 0)
                                        colorstr = "Red" if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else "Green"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        else:
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
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
                                            
                                            centerx = round(x+w/2)
                                            centery = round(y+h/2)
                                            radius = round((w+h)/4)
                                            cv2.circle(filtered_frame_red_green, (centerx,centery),radius,color,4)
                                            cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                            cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                            if colorstr == "Green":
                                                yoffset1 = y-h
                                                yoffset2 = y-h*2
                                                cv2.rectangle(filtered_frame_red_green, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                            else:
                                                yoffset1 = y+h*2
                                                yoffset2 = y+h*3
                                                cv2.rectangle(filtered_frame_red_green, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))

                                            if grayscalewindow == True:
                                                cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            if redgreenwindow == True:
                                                cv2.rectangle(filtered_frame_red_green, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                            if finalwindow == True:
                                                cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                    else:
                        # True: anywindowopen, detectyellowlight --- False: trafficlighttracking, advancedmode, performancemode
                        mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                        mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)
                        mask_yellow = cv2.inRange(rgb_frame, lower_yellow, upper_yellow)

                        combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                        filtered_frame_red_green_yellow = cv2.bitwise_and(frame, frame, mask=combined_mask)
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                            color = (0, 0, 255)
                                            colorstr = "Red"
                                        if green_ratio > red_ratio and green_ratio > yellow_ratio:
                                            color = (0, 255, 0)
                                            colorstr = "Green"
                                        if yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                            color = (0, 255, 255)
                                            colorstr = "Yellow"
                                        

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        if colorstr == "Green":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
                                        if colorstr == "Yellow":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)+h
                            
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
                                            
                                            centerx = round(x+w/2)
                                            centery = round(y+h/2)
                                            radius = round((w+h)/4)
                                            cv2.circle(filtered_frame_red_green_yellow, (centerx,centery),radius,color,4)
                                            cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                            cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                            if colorstr == "Green":
                                                yoffset1 = y-h
                                                yoffset2 = y-h*2
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                            if colorstr == "Red":
                                                yoffset1 = y+h*2
                                                yoffset2 = y+h*3
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                            if colorstr == "Yellow":
                                                yoffset1 = y-h
                                                yoffset2 = y+h*2
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), yoffset1-round(h/2)), (x + w+round(w/2), yoffset2 + h-round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset1-round(h/2)), (x + w+round(w/2), yoffset2 + h-round(h/2)), color, round((w+h)/4))

                                            if grayscalewindow == True:
                                                cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            if redgreenwindow == True:
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                            if finalwindow == True:
                                                cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0
                        
                else:
                    # True: anywindowopen, performancemode --- False: trafficlighttracking, advancedmode
                    mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)

                    filtered_frame_red = mask_red
                    filtered_frame_bw = filtered_frame_red
                    final_frame = frame

                    currentnearest = 0
                    currentneareststate = "---"
                    currentdistance = "---"
                    
                    contours, _ = cv2.findContours(filtered_frame_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)
                        if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                            if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:

                                red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                                total_pixels = w * h
                                red_ratio = red_pixel_count / total_pixels
                                if red_ratio < circleplusoffset and red_ratio > circleminusoffset:

                                    color = (0, 0, 255)
                                    colorstr = "Red"
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
                                        
                                        centerx = round(x+w/2)
                                        centery = round(y+h/2)
                                        radius = round((w+h)/4)
                                        cv2.circle(filtered_frame_red, (centerx,centery),radius,color,4)
                                        cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                        cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                        
                                        yoffset1 = y+h*2
                                        yoffset2 = y+h*3
                                        cv2.rectangle(filtered_frame_red, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))

                                        if grayscalewindow == True:
                                            cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                        if redgreenwindow == True:
                                            cv2.rectangle(filtered_frame_red, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(filtered_frame_red, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(filtered_frame_red, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                        if finalwindow == True:
                                            cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                        if currentnearest < w:
                                            currentnearest = w
                                            currentneareststate = colorstr
                                            currentdistance = max_rect_size - w - min_rect_size
                                            if currentdistance < 0:
                                                currentdistance = 0
            else:

                if performancemode == False:
                    if detectyellowlight == False:
                        # True: --- False: trafficlighttracking, advancedmode, anywindowopen, performancemode, detectyellowlight
                        mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                        mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)

                        filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                        colorstr = "Red" if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else "Green"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        else:
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
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

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                    else:
                        # True: detectyellowlight --- False: trafficlighttracking, advancedmode, anywindowopen, performancemode
                        mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                        mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)
                        mask_yellow = cv2.inRange(rgb_frame, lower_yellow, upper_yellow)

                        combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                        filtered_frame_red_green_yellow = cv2.bitwise_and(frame, frame, mask=combined_mask)
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                            color = (0, 0, 255)
                                            colorstr = "Red"
                                        if green_ratio > red_ratio and green_ratio > yellow_ratio:
                                            color = (0, 255, 0)
                                            colorstr = "Green"
                                        if yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                            color = (0, 255, 255)
                                            colorstr = "Yellow"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        if colorstr == "Green":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
                                        if colorstr == "Yellow":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)+h
                            
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

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0
                        
                else:
                    # True: performancemode --- False: trafficlighttracking, advancedmode, anywindowopen
                    mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)

                    filtered_frame_red = mask_red
                    filtered_frame_bw = filtered_frame_red
                    final_frame = frame

                    currentnearest = 0
                    currentneareststate = "---"
                    currentdistance = "---"
                    
                    contours, _ = cv2.findContours(filtered_frame_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)
                        if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                            if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:

                                red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                                total_pixels = w * h
                                red_ratio = red_pixel_count / total_pixels
                                if red_ratio < circleplusoffset and red_ratio > circleminusoffset:

                                    color = (0, 0, 255)
                                    colorstr = "Red"
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
                                    
                                        if currentnearest < w:
                                            currentnearest = w
                                            currentneareststate = colorstr
                                            currentdistance = max_rect_size - w - min_rect_size
                                            if currentdistance < 0:
                                                currentdistance = 0
        else:
            
            if anywindowopen == True:
                if performancemode == False:
                    if detectyellowlight == False:
                        # True: advancedmode, anywindowopen --- False: trafficlighttracking, performancemode, detectyellowlight
                        mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                        mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)

                        filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                        color = (0, 0, 255) if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else (0, 255, 0)
                                        colorstr = "Red" if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else "Green"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        else:
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
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
                                            
                                            centerx = round(x+w/2)
                                            centery = round(y+h/2)
                                            radius = round((w+h)/4)
                                            cv2.circle(filtered_frame_red_green, (centerx,centery),radius,color,4)
                                            cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                            cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                            if colorstr == "Green":
                                                yoffset1 = y-h
                                                yoffset2 = y-h*2
                                                cv2.rectangle(filtered_frame_red_green, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                            else:
                                                yoffset1 = y+h*2
                                                yoffset2 = y+h*3
                                                cv2.rectangle(filtered_frame_red_green, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))

                                            if grayscalewindow == True:
                                                cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            if redgreenwindow == True:
                                                cv2.rectangle(filtered_frame_red_green, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                            if finalwindow == True:
                                                cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                    else:
                        # True: advancedmode, anywindowopen, detectyellowlight --- False: trafficlighttracking, performancemode
                        mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                        mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)
                        mask_yellow = cv2.inRange(rgb_frame, lower_yellow_advanced, upper_yellow_advanced)

                        combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                        filtered_frame_red_green_yellow = cv2.bitwise_and(frame, frame, mask=combined_mask)
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                            color = (0, 0, 255)
                                            colorstr = "Red"
                                        if green_ratio > red_ratio and green_ratio > yellow_ratio:
                                            color = (0, 255, 0)
                                            colorstr = "Green"
                                        if yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                            color = (0, 255, 255)
                                            colorstr = "Yellow"
                                        

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        if colorstr == "Green":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
                                        if colorstr == "Yellow":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)+h
                            
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
                                            
                                            centerx = round(x+w/2)
                                            centery = round(y+h/2)
                                            radius = round((w+h)/4)
                                            cv2.circle(filtered_frame_red_green_yellow, (centerx,centery),radius,color,4)
                                            cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                            cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                            if colorstr == "Green":
                                                yoffset1 = y-h
                                                yoffset2 = y-h*2
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                            if colorstr == "Red":
                                                yoffset1 = y+h*2
                                                yoffset2 = y+h*3
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                            if colorstr == "Yellow":
                                                yoffset1 = y-h
                                                yoffset2 = y+h*2
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), yoffset1-round(h/2)), (x + w+round(w/2), yoffset2 + h-round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset1-round(h/2)), (x + w+round(w/2), yoffset2 + h-round(h/2)), color, round((w+h)/4))

                                            if grayscalewindow == True:
                                                cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            if redgreenwindow == True:
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                            if finalwindow == True:
                                                cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0
                        
                else:
                    # True: advancedmode, anywindowopen, performancemode --- False: trafficlighttracking
                    mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)

                    filtered_frame_red = mask_red
                    filtered_frame_bw = filtered_frame_red
                    final_frame = frame

                    currentnearest = 0
                    currentneareststate = "---"
                    currentdistance = "---"
                    
                    contours, _ = cv2.findContours(filtered_frame_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                    color = (0, 0, 255)
                                    colorstr = "Red"
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
                                        
                                        centerx = round(x+w/2)
                                        centery = round(y+h/2)
                                        radius = round((w+h)/4)
                                        cv2.circle(filtered_frame_red, (centerx,centery),radius,color,4)
                                        cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                        cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                        
                                        yoffset1 = y+h*2
                                        yoffset2 = y+h*3
                                        cv2.rectangle(filtered_frame_red, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))

                                        if grayscalewindow == True:
                                            cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                        if redgreenwindow == True:
                                            cv2.rectangle(filtered_frame_red, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(filtered_frame_red, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(filtered_frame_red, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                        if finalwindow == True:
                                            cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                        if currentnearest < w:
                                            currentnearest = w
                                            currentneareststate = colorstr
                                            currentdistance = max_rect_size - w - min_rect_size
                                            if currentdistance < 0:
                                                currentdistance = 0
            else:
                # True: advancedmode --- False: trafficlighttracking, anywindowopen, performancemode, detectyellowlight
                if performancemode == False:
                    if detectyellowlight == False:
                        mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                        mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)

                        filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                        colorstr = "Red" if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else "Green"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        else:
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
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

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                    else:
                        # True: advancedmode, detectyellowlight --- False: trafficlighttracking, anywindowopen, performancemode
                        mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                        mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)
                        mask_yellow = cv2.inRange(rgb_frame, lower_yellow_advanced, upper_yellow_advanced)

                        combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                        filtered_frame_red_green_yellow = cv2.bitwise_and(frame, frame, mask=combined_mask)
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"

                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                            color = (0, 0, 255)
                                            colorstr = "Red"
                                        if green_ratio > red_ratio and green_ratio > yellow_ratio:
                                            color = (0, 255, 0)
                                            colorstr = "Green"
                                        if yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                            color = (0, 255, 255)
                                            colorstr = "Yellow"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        if colorstr == "Green":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
                                        if colorstr == "Yellow":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)+h
                            
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

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0
                        
                else:
                    # True: advancedmode, performancemode --- False: trafficlighttracking, anywindowopen
                    mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)

                    filtered_frame_red = mask_red
                    filtered_frame_bw = filtered_frame_red
                    final_frame = frame

                    currentnearest = 0
                    currentneareststate = "---"
                    currentdistance = "---"

                    contours, _ = cv2.findContours(filtered_frame_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                    color = (0, 0, 255)
                                    colorstr = "Red"
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
                                    
                                        if currentnearest < w:
                                            currentnearest = w
                                            currentneareststate = colorstr
                                            currentdistance = max_rect_size - w - min_rect_size
                                            if currentdistance < 0:
                                                currentdistance = 0
    else:
        if advancedmode == False:
            if anywindowopen == True:
                if performancemode == False:
                    if detectyellowlight == False:
                        # True: trafficlighttracking, anywindowopen --- False: advancedmode, performancemode, detectyellowlight
                        mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                        mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)

                        filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"

                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                        color = (0, 0, 255) if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else (0, 255, 0)
                                        colorstr = "Red" if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else "Green"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        else:
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
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
                                            
                                            centerx = round(x+w/2)
                                            centery = round(y+h/2)
                                            radius = round((w+h)/4)
                                            cv2.circle(filtered_frame_red_green, (centerx,centery),radius,color,4)
                                            cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                            cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                            if colorstr == "Green":
                                                yoffset1 = y-h
                                                yoffset2 = y-h*2
                                                cv2.rectangle(filtered_frame_red_green, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                            else:
                                                yoffset1 = y+h*2
                                                yoffset2 = y+h*3
                                                cv2.rectangle(filtered_frame_red_green, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))

                                            if grayscalewindow == True:
                                                cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            if redgreenwindow == True:
                                                cv2.rectangle(filtered_frame_red_green, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                            if finalwindow == True:
                                                cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                                            coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h))

                    else:
                        # True: trafficlighttracking, anywindowopen, detectyellowlight --- False: advancedmode, performancemode
                        mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                        mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)
                        mask_yellow = cv2.inRange(rgb_frame, lower_yellow, upper_yellow)

                        combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                        filtered_frame_red_green_yellow = cv2.bitwise_and(frame, frame, mask=combined_mask)
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"

                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                            color = (0, 0, 255)
                                            colorstr = "Red"
                                        if green_ratio > red_ratio and green_ratio > yellow_ratio:
                                            color = (0, 255, 0)
                                            colorstr = "Green"
                                        if yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                            color = (0, 255, 255)
                                            colorstr = "Yellow"
                                        

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        if colorstr == "Green":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
                                        if colorstr == "Yellow":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)+h
                            
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
                                            
                                            centerx = round(x+w/2)
                                            centery = round(y+h/2)
                                            radius = round((w+h)/4)
                                            cv2.circle(filtered_frame_red_green_yellow, (centerx,centery),radius,color,4)
                                            cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                            cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                            if colorstr == "Green":
                                                yoffset1 = y-h
                                                yoffset2 = y-h*2
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                            if colorstr == "Red":
                                                yoffset1 = y+h*2
                                                yoffset2 = y+h*3
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                            if colorstr == "Yellow":
                                                yoffset1 = y-h
                                                yoffset2 = y+h*2
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), yoffset1-round(h/2)), (x + w+round(w/2), yoffset2 + h-round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset1-round(h/2)), (x + w+round(w/2), yoffset2 + h-round(h/2)), color, round((w+h)/4))

                                            if grayscalewindow == True:
                                                cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            if redgreenwindow == True:
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                            if finalwindow == True:
                                                cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                                            coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h))
                        
                else:
                    # True: trafficlighttracking, anywindowopen, performancemode --- False: advancedmode
                    mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)

                    filtered_frame_red = mask_red
                    filtered_frame_bw = filtered_frame_red
                    final_frame = frame

                    currentnearest = 0
                    currentneareststate = "---"
                    currentdistance = "---"
                    
                    contours, _ = cv2.findContours(filtered_frame_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)
                        if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                            if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:

                                red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                                total_pixels = w * h
                                red_ratio = red_pixel_count / total_pixels
                                if red_ratio < circleplusoffset and red_ratio > circleminusoffset:

                                    color = (0, 0, 255)
                                    colorstr = "Red"
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
                                        
                                        centerx = round(x+w/2)
                                        centery = round(y+h/2)
                                        radius = round((w+h)/4)
                                        cv2.circle(filtered_frame_red, (centerx,centery),radius,color,4)
                                        cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                        cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                        
                                        yoffset1 = y+h*2
                                        yoffset2 = y+h*3
                                        cv2.rectangle(filtered_frame_red, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))

                                        if grayscalewindow == True:
                                            cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                        if redgreenwindow == True:
                                            cv2.rectangle(filtered_frame_red, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(filtered_frame_red, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(filtered_frame_red, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                        if finalwindow == True:
                                            cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                        if currentnearest < w:
                                            currentnearest = w
                                            currentneareststate = colorstr
                                            currentdistance = max_rect_size - w - min_rect_size
                                            if currentdistance < 0:
                                                currentdistance = 0

                                        coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h))
                                      
            else:

                if performancemode == False:
                    if detectyellowlight == False:
                        # True: trafficlighttracking --- False: advancedmode, anywindowopen, performancemode, detectyellowlight
                        mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                        mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)

                        filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                        colorstr = "Red" if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else "Green"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        else:
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
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

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                                            coordinates.append((round(x+w/2),centery1,w,h))

                    else:
                        # True: trafficlighttracking, detectyellowlight --- False: advancedmode, anywindowopen, performancemode
                        mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
                        mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)
                        mask_yellow = cv2.inRange(rgb_frame, lower_yellow, upper_yellow)

                        combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                        filtered_frame_red_green_yellow = cv2.bitwise_and(frame, frame, mask=combined_mask)
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                            color = (0, 0, 255)
                                            colorstr = "Red"
                                        if green_ratio > red_ratio and green_ratio > yellow_ratio:
                                            color = (0, 255, 0)
                                            colorstr = "Green"
                                        if yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                            color = (0, 255, 255)
                                            colorstr = "Yellow"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        if colorstr == "Green":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
                                        if colorstr == "Yellow":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)+h
                            
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

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                                            coordinates.append((round(x+w/2),centery1,w,h))
                        
                else:
                    # True: trafficlighttracking, performancemode --- False: advancedmode, anywindowopen
                    mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)

                    filtered_frame_red = mask_red
                    filtered_frame_bw = filtered_frame_red
                    final_frame = frame

                    currentnearest = 0
                    currentneareststate = "---"
                    currentdistance = "---"
                    
                    contours, _ = cv2.findContours(filtered_frame_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)
                        if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                            if w / h - 1 < width_height_ratio and w / h - 1 > -width_height_ratio:

                                red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                                total_pixels = w * h
                                red_ratio = red_pixel_count / total_pixels
                                if red_ratio < circleplusoffset and red_ratio > circleminusoffset:

                                    color = (0, 0, 255)
                                    colorstr = "Red"
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
                                    
                                        if currentnearest < w:
                                            currentnearest = w
                                            currentneareststate = colorstr
                                            currentdistance = max_rect_size - w - min_rect_size
                                            if currentdistance < 0:
                                                currentdistance = 0

                                        coordinates.append((round(x+w/2),centery1,w,h))
        else:
            
            if anywindowopen == True:
                if performancemode == False:
                    if detectyellowlight == False:
                        # True: trafficlighttracking, advancedmode, anywindowopen --- False: performancemode, detectyellowlight
                        mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                        mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)

                        filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                        color = (0, 0, 255) if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else (0, 255, 0)
                                        colorstr = "Red" if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else "Green"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        else:
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
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
                                            
                                            centerx = round(x+w/2)
                                            centery = round(y+h/2)
                                            radius = round((w+h)/4)
                                            cv2.circle(filtered_frame_red_green, (centerx,centery),radius,color,4)
                                            cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                            cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                            if colorstr == "Green":
                                                yoffset1 = y-h
                                                yoffset2 = y-h*2
                                                cv2.rectangle(filtered_frame_red_green, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                            else:
                                                yoffset1 = y+h*2
                                                yoffset2 = y+h*3
                                                cv2.rectangle(filtered_frame_red_green, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))

                                            if grayscalewindow == True:
                                                cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            if redgreenwindow == True:
                                                cv2.rectangle(filtered_frame_red_green, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                            if finalwindow == True:
                                                cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                                            coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h))

                    else:
                        # True: trafficlighttracking, advancedmode, anywindowopen, detectyellowlight --- False: performancemode
                        mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                        mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)
                        mask_yellow = cv2.inRange(rgb_frame, lower_yellow_advanced, upper_yellow_advanced)

                        combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                        filtered_frame_red_green_yellow = cv2.bitwise_and(frame, frame, mask=combined_mask)
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                            color = (0, 0, 255)
                                            colorstr = "Red"
                                        if green_ratio > red_ratio and green_ratio > yellow_ratio:
                                            color = (0, 255, 0)
                                            colorstr = "Green"
                                        if yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                            color = (0, 255, 255)
                                            colorstr = "Yellow"
                                        

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        if colorstr == "Green":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
                                        if colorstr == "Yellow":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)+h
                            
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
                                            
                                            centerx = round(x+w/2)
                                            centery = round(y+h/2)
                                            radius = round((w+h)/4)
                                            cv2.circle(filtered_frame_red_green_yellow, (centerx,centery),radius,color,4)
                                            cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                            cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                            if colorstr == "Green":
                                                yoffset1 = y-h
                                                yoffset2 = y-h*2
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset2-round(h/2)), (x + w+round(w/2), yoffset2 + h*3+round(h/2)), color, round((w+h)/4))
                                            if colorstr == "Red":
                                                yoffset1 = y+h*2
                                                yoffset2 = y+h*3
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                            if colorstr == "Yellow":
                                                yoffset1 = y-h
                                                yoffset2 = y+h*2
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x-round(w/2), yoffset1-round(h/2)), (x + w+round(w/2), yoffset2 + h-round(h/2)), color, round((w+h)/4))
                                                cv2.rectangle(final_frame, (x-round(w/2), yoffset1-round(h/2)), (x + w+round(w/2), yoffset2 + h-round(h/2)), color, round((w+h)/4))

                                            if grayscalewindow == True:
                                                cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            if redgreenwindow == True:
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(filtered_frame_red_green_yellow, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                            if finalwindow == True:
                                                cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                                cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                                            coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h))
                        
                else:
                    # True: trafficlighttracking, advancedmode, anywindowopen, performancemode --- False:     
                    mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)

                    filtered_frame_red = mask_red
                    filtered_frame_bw = filtered_frame_red
                    final_frame = frame

                    currentnearest = 0
                    currentneareststate = "---"
                    currentdistance = "---"
                    
                    contours, _ = cv2.findContours(filtered_frame_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                    color = (0, 0, 255)
                                    colorstr = "Red"
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
                                        
                                        centerx = round(x+w/2)
                                        centery = round(y+h/2)
                                        radius = round((w+h)/4)
                                        cv2.circle(filtered_frame_red, (centerx,centery),radius,color,4)
                                        cv2.circle(final_frame, (centerx,centery),radius,color,4)
                                        cv2.circle(filtered_frame_bw, (centerx,centery),radius,(255, 255, 255),4)
                                        
                                        yoffset1 = y+h*2
                                        yoffset2 = y+h*3
                                        cv2.rectangle(filtered_frame_red, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))
                                        cv2.rectangle(final_frame, (x-round(w/2), y-round(h/2)), (x + w+round(w/2), yoffset1 + h+round(h/2)), color, round((w+h)/4))

                                        if grayscalewindow == True:
                                            cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                        if redgreenwindow == True:
                                            cv2.rectangle(filtered_frame_red, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(filtered_frame_red, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(filtered_frame_red, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                                        if finalwindow == True:
                                            cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                                            cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                                        if currentnearest < w:
                                            currentnearest = w
                                            currentneareststate = colorstr
                                            currentdistance = max_rect_size - w - min_rect_size
                                            if currentdistance < 0:
                                                currentdistance = 0

                                        coordinates.append((round(x+w/2),round(yoffset1-h/2),w,h))
            else:
                # True: trafficlighttracking, advancedmode --- False: anywindowopen, performancemode, detectyellowlight
                if performancemode == False:
                    if detectyellowlight == False:
                        mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                        mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)

                        filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                        colorstr = "Red" if cv2.countNonZero(mask_red[y:y+h, x:x+w]) > cv2.countNonZero(mask_green[y:y+h, x:x+w]) else "Green"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        else:
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
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

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                                            coordinates.append((round(x+w/2),centery1,w,h))

                    else:
                        # True: trafficlighttracking, advancedmode, detectyellowlight --- False: anywindowopen, performancemode
                        mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)
                        mask_green = cv2.inRange(rgb_frame, lower_green_advanced, upper_green_advanced)
                        mask_yellow = cv2.inRange(rgb_frame, lower_yellow_advanced, upper_yellow_advanced)

                        combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                        filtered_frame_red_green_yellow = cv2.bitwise_and(frame, frame, mask=combined_mask)
                        filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY)
                        final_frame = frame

                        currentnearest = 0
                        currentneareststate = "---"
                        currentdistance = "---"
                        
                        contours, _ = cv2.findContours(cv2.cvtColor(filtered_frame_red_green_yellow, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                                            color = (0, 0, 255)
                                            colorstr = "Red"
                                        if green_ratio > red_ratio and green_ratio > yellow_ratio:
                                            color = (0, 255, 0)
                                            colorstr = "Green"
                                        if yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                            color = (0, 255, 255)
                                            colorstr = "Yellow"

                                        if colorstr == "Red":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)+h
                                            centery2 = round(y + h / 2)+h*2
                                        if colorstr == "Green":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)-h*2
                                        if colorstr == "Yellow":
                                            centerx = round(x + w / 2)
                                            centery1 = round(y + h / 2)-h
                                            centery2 = round(y + h / 2)+h
                            
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

                                            if currentnearest < w:
                                                currentnearest = w
                                                currentneareststate = colorstr
                                                currentdistance = max_rect_size - w - min_rect_size
                                                if currentdistance < 0:
                                                    currentdistance = 0

                                            coordinates.append((round(x+w/2),centery1,w,h))
                        
                else:
                    # True: trafficlighttracking, advancedmode, performancemode --- False: anywindowopen
                    mask_red = cv2.inRange(rgb_frame, lower_red_advanced, upper_red_advanced)

                    filtered_frame_red = mask_red
                    filtered_frame_bw = filtered_frame_red
                    final_frame = frame

                    currentnearest = 0
                    currentneareststate = "---"
                    currentdistance = "---"
                    
                    contours, _ = cv2.findContours(filtered_frame_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                                    color = (0, 0, 255)
                                    colorstr = "Red"
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
                                    
                                        if currentnearest < w:
                                            currentnearest = w
                                            currentneareststate = colorstr
                                            currentdistance = max_rect_size - w - min_rect_size
                                            if currentdistance < 0:
                                                currentdistance = 0

                                        coordinates.append((round(x+w/2),centery1,w,h))

    if trafficlighttracking == True:
        try:
            # Tracking with IDs:

            def generate_new_id():
                used_ids = set(id for _, id in trafficlights)
                new_id = 1
                while new_id in used_ids:
                    new_id += 1
                return new_id

            if last_coordinates:
                for i in range(len(last_coordinates)):
                    last_x, last_y, w, h = last_coordinates[i]
                    closest = screen_width
                    nearestpoint = None
                    exists_in_trafficlights = False
                    saved_id = None
                    for j in range(len(coordinates)):
                        x, y, w, h = coordinates[j]
                        distance = math.sqrt((x - last_x)**2 + (y - last_y)**2)
                        if distance < closest:
                            closest = distance
                            nearestpoint = x, y, w, h

                    # Remove missing points from traffic lights and update list
                    if nearestpoint:
                        for k, (coord, id) in enumerate(trafficlights):
                            if coord == last_coordinates[i]:
                                exists_in_trafficlights = True
                                saved_id = id
                                del trafficlights[k]
                                break
                        if exists_in_trafficlights:
                            trafficlights.append((nearestpoint, saved_id))
                        else:
                            new_id = generate_new_id()
                            trafficlights.append((nearestpoint, new_id))

                # Remove lost traffic lights based on distance traveled
                lost_trafficlights = len(last_coordinates) - len(coordinates)
                if lost_trafficlights > 0:
                    max_distances = []
                    for i, ((x, y, w, h), _) in enumerate(trafficlights):
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
                    for _, id in trafficlights:
                        id_counts[id] = id_counts.get(id, 0) + 1

                    for _ in range(len(trafficlights) - len(coordinates)):
                        max_index = None
                        max_count = 0
                        for i, (_, id) in enumerate(trafficlights):
                            if id_counts[id] > max_count:
                                max_index = i
                                max_count = id_counts[id]

                        if max_index is not None:
                            del trafficlights[max_index]
                            id_counts[trafficlights[max_index][1]] -= 1

                
            if grayscalewindow == True:
                for i in range(len(trafficlights)):
                    coord, id = trafficlights[i]
                    x, y, w, h = coord
                    cv2.putText(filtered_frame_bw, "ID: " + str(id), (x-round(w/2), y-round(h*1.5)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
        
        except Exception as e:
            print("TrafficLightDetection - Tracking Error: " + str(e))
        
    data["TrafficLightDetection"] = currentneareststate                   

    if grayscalewindow == True:
        if textsize > 0:         
            cv2.putText(filtered_frame_bw, f"Nearest: {currentneareststate}, Distance: {currentdistance}", (20, round(40*textsize)), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 2, cv2.LINE_AA) 
        cv2.imshow('Traffic Light Detection - B/W', filtered_frame_bw)
    if redgreenwindow == True:      
        if performancemode == False:
            if detectyellowlight == False:
                cv2.imshow('Traffic Light Detection - Red/Green', filtered_frame_red_green)
            else:
                cv2.imshow('Traffic Light Detection - Red/Green', filtered_frame_red_green_yellow)
        else:
            cv2.imshow('Traffic Light Detection - Red/Green', filtered_frame_red)
    if finalwindow == True:
        cv2.imshow('Traffic Light Detection - Final', final_frame)

    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    UpdateSettings()
    pass

def onDisable():
    pass

class UI():
    try: 
        
        def __init__(self, master) -> None:
            self.master = master 
            self.exampleFunction()
            resizeWindow(850,655)
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def tabFocused(self):
            resizeWindow(850,655)

        def UpdateScaleValueFromSlider(self):
            self.textsize.set(self.textsizeSlider.get())
            self.x1ofsc.set(self.x1ofscSlider.get())
            self.y1ofsc.set(self.y1ofscSlider.get())
            self.x2ofsc.set(self.x2ofscSlider.get())
            self.y2ofsc.set(self.y2ofscSlider.get())
            self.windowwidth.set(self.windowwidthSlider.get())
            self.windowheight.set(self.windowheightSlider.get())
            self.scale.set(self.scaleSlider.get())
            self.minrectsize.set(self.minrectsizeSlider.get())
            self.maxrectsize.set(self.maxrectsizeSlider.get())

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() 
            except: pass
            
            self.root = tk.Canvas(self.master, width=750, height=650, border=0, highlightthickness=0)
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


            colorsettingsFrame.configure(height=500)
            colorsettingsFrame.columnconfigure(0, weight=1)
            colorsettingsFrame.columnconfigure(1, weight=1)
            colorsettingsFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(colorsettingsFrame, "Color Settings", 0, 0, font=("Robot", 12, "bold"), columnspan=7)

            filtersFrame.configure(height=500)
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
            
            ttk.Button(self.root, text="Save", command=self.save, width=15).pack(anchor="center", pady=6)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()


            helpers.MakeCheckButton(outputwindowFrame, "Final Window\n--------------------\nIf enabled, the app creates a window with the result of the traffic light detection.", "TrafficLightDetection", "finalwindow", 1, 0, width=80, callback=UpdateSettings())
            helpers.MakeCheckButton(outputwindowFrame, "Grayscale Window\n---------------------------\nIf enabled, the app creates a window with the color masks combined in a grayscaled frame.", "TrafficLightDetection", "grayscalewindow", 2, 0, width=80, callback=UpdateSettings())
            helpers.MakeCheckButton(outputwindowFrame, "Red/Green Window\n----------------------------\nIf enabled, the app creates a window with the color masks combined in a frame.", "TrafficLightDetection", "redgreenwindow", 3, 0, width=80, callback=UpdateSettings())
            helpers.MakeCheckButton(outputwindowFrame, "Automatic Windowsize\n---------------------------------\nIf enabled, the Window Width and Window Height sliders will no longer have any effect\nand the output window keeps the aspect ratio of the captured frame. Set the size of the\noutput window with the Window Scale slider.", "TrafficLightDetection", "automaticwindowsize", 4, 0, width=80, callback=UpdateSettings())
            helpers.MakeEmptyLine(outputwindowFrame,5,0)

            helpers.MakeCheckButton(generalFrame, "Yellow Light Detection (not recommended)\n-------------------------------------------------------------\nIf enabled, the trafficlight detection tries to detect yellow traffic\nlights, but it is not recommended because it causes more wrong\ndetected traffic lights.", "TrafficLightDetection", "detectyellowlight", 4, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Performance Mode (recommended)\n---------------------------------------------------\nIf enabled, the traffic light detection only detects red traffic lights,\nwhich increases performance, but does not reduce detection accuracy.", "TrafficLightDetection", "performancemode", 5, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Advanced Settings\n---------------------------\nIf enabled, the traffic light detection uses the settings you set in\nthe Advanced tab. (could have a bad impact on performance)", "TrafficLightDetection", "advancedmode", 6, 0, width=60, callback=UpdateSettings())
            helpers.MakeEmptyLine(generalFrame,7,0)

            helpers.MakeCheckButton(filtersFrame, "Rect Size Filter", "TrafficLightDetection", "rectsizefilter", 3, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(filtersFrame, "Width Height Ratio Filter", "TrafficLightDetection", "widthheightratiofilter", 4, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(filtersFrame, "Pixel Percentage Filter", "TrafficLightDetection", "pixelpercentagefilter", 5, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(filtersFrame, "Other Lights Filter", "TrafficLightDetection", "otherlightsofffilter", 6, 0, width=60, callback=UpdateSettings())

            helpers.MakeCheckButton(trackeraiFrame, "Tracking of Traffic Lights\n-----------------------------------\nIf enabled, the app tracks the detected traffic lights and gives them an ID.\n(required for AI)", "TrafficLightDetection", "trafficlighttracking", 1, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(trackeraiFrame, "AI Mode\n------------\nIf enabled, the app uses AI (Yolov5) to confirm the detected traffic lights,\nwhich increases accuracy.\nThis feature does not work yet. I am working on it.", "TrafficLightDetection", "aiconfirmation", 2, 0, width=60, callback=UpdateSettings())

            self.textsizeSlider = tk.Scale(generalFrame, from_=0, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=700, command=lambda x: self.UpdateScaleValueFromSlider())
            self.textsizeSlider.set(settings.GetSettings("TrafficLightDetection", "textsize", 0.5))
            self.textsizeSlider.grid(row=8, column=0, padx=10, pady=0, columnspan=2)
            self.textsize = helpers.MakeComboEntry(generalFrame, "Font Size (Grayscale Window)", "TrafficLightDetection", "textsize", 9, 0, width=32, labelwidth=30)
            
            helpers.MakeCheckButton(screencaptureFrame, "Use Full Frame\n----------------------\nIf enabled, the screencapture for the traffic light detection uses the top ⅔ of the screen for\nthe traffic light detection. (not recommended, could have a bad impact on performance)\n\nTo set own screencapture coordinates disable Use Full Frame and use sliders below.", "TrafficLightDetection", "usefullframe", 1, 0, width=80, callback=UpdateSettings())
            
            self.x1ofscSlider = tk.Scale(screencaptureFrame, from_=0, to=screen_width-1, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateScaleValueFromSlider())
            self.x1ofscSlider.set(settings.GetSettings("TrafficLightDetection", "x1ofsc", 0))
            self.x1ofscSlider.grid(row=3, column=0, padx=10, pady=0, columnspan=2)
            self.x1ofsc = helpers.MakeComboEntry(screencaptureFrame, "X1 (topleft)", "TrafficLightDetection", "x1ofsc", 3,0)

            self.y1ofscSlider = tk.Scale(screencaptureFrame, from_=0, to=screen_height-1, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateScaleValueFromSlider())
            self.y1ofscSlider.set(settings.GetSettings("TrafficLightDetection", "y1ofsc", 0))
            self.y1ofscSlider.grid(row=5, column=0, padx=10, pady=0, columnspan=2)
            self.y1ofsc = helpers.MakeComboEntry(screencaptureFrame, "Y1 (topleft)", "TrafficLightDetection", "y1ofsc", 5,0)

            self.x2ofscSlider = tk.Scale(screencaptureFrame, from_=0, to=screen_width-1, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateScaleValueFromSlider())
            self.x2ofscSlider.set(settings.GetSettings("TrafficLightDetection", "x2ofsc", screen_width-1))
            self.x2ofscSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.x2ofsc = helpers.MakeComboEntry(screencaptureFrame, "X2 (buttomright)", "TrafficLightDetection", "x2ofsc", 7,0)

            self.y2ofscSlider = tk.Scale(screencaptureFrame, from_=0, to=screen_height-1, resolution=1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateScaleValueFromSlider())
            self.y2ofscSlider.set(settings.GetSettings("TrafficLightDetection", "y2ofsc", round(screen_height/1.5)-1))
            self.y2ofscSlider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.y2ofsc = helpers.MakeComboEntry(screencaptureFrame, "Y2 (buttomright)", "TrafficLightDetection", "y2ofsc", 9,0)


            self.windowwidthSlider = tk.Scale(outputwindowFrame, from_=round(screen_width/20), to=screen_width, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.windowwidthSlider.set(settings.GetSettings("TrafficLightDetection", "outputwindowwidth", round(screen_width/2)))
            self.windowwidthSlider.grid(row=6, column=0, padx=10, pady=0, columnspan=2)
            self.windowwidth = helpers.MakeComboEntry(outputwindowFrame, "Window Width", "TrafficLightDetection", "outputwindowwidth", 6,0, labelwidth=13, width=10)

            self.windowheightSlider = tk.Scale(outputwindowFrame, from_=round(screen_height/20), to=screen_height, resolution=1, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.windowheightSlider.set(settings.GetSettings("TrafficLightDetection", "outputwindowheight", round(screen_height/3)))
            self.windowheightSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.windowheight = helpers.MakeComboEntry(outputwindowFrame, "Window Height", "TrafficLightDetection", "outputwindowheight", 7,0, labelwidth=13, width=10)

            self.scaleSlider = tk.Scale(outputwindowFrame, from_=0.1, to=2, resolution=0.01, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.scaleSlider.set(settings.GetSettings("TrafficLightDetection", "scale", 0.5))
            self.scaleSlider.grid(row=8, column=0, padx=10, pady=0, columnspan=2)
            self.scale = helpers.MakeComboEntry(outputwindowFrame, "Window Scale", "TrafficLightDetection", "scale", 8,0, labelwidth=13, width=10)

            self.minrectsizeSlider = tk.Scale(filtersFrame, from_=1, to=round(screen_width / 2), resolution=1, orient=tk.HORIZONTAL, length=700, command=lambda x: self.UpdateScaleValueFromSlider())
            self.minrectsizeSlider.set(settings.GetSettings("TrafficLightDetection", "minrectsize", round(screen_width / 240)))
            self.minrectsizeSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.minrectsize = helpers.MakeComboEntry(filtersFrame, "Min. Traffic Light Size Filter", "TrafficLightDetection", "minrectsize", 8,0, labelwidth=80, width=20)

            self.maxrectsizeSlider = tk.Scale(filtersFrame, from_=1, to=round(screen_width / 2), resolution=1, orient=tk.HORIZONTAL, length=700, command=lambda x: self.UpdateScaleValueFromSlider())
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
            settings.CreateSettings("TrafficLightDetection", "scale", self.scaleSlider.get())
            settings.CreateSettings("TrafficLightDetection", "textsize", self.textsizeSlider.get())
            settings.CreateSettings("TrafficLightDetection", "x1ofsc", self.x1ofscSlider.get())
            settings.CreateSettings("TrafficLightDetection", "y1ofsc", self.y1ofscSlider.get())
            settings.CreateSettings("TrafficLightDetection", "x2ofsc", self.x2ofscSlider.get())
            settings.CreateSettings("TrafficLightDetection", "y2ofsc", self.y2ofscSlider.get())
            settings.CreateSettings("TrafficLightDetection", "outputwindowwidth", self.windowwidthSlider.get())
            settings.CreateSettings("TrafficLightDetection", "outputwindowheight", self.windowheightSlider.get())
            settings.CreateSettings("TrafficLightDetection", "minrectsize", self.minrectsizeSlider.get())
            settings.CreateSettings("TrafficLightDetection", "maxrectsize", self.maxrectsizeSlider.get())

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
            UpdateSettings()
            switchSelectedPlugin("plugins." + "TrafficLightDetection" + ".main")

        def resetadvancedfilterstodefault(self):
            settings.CreateSettings("TrafficLightDetection", "rectsizefilter", True)
            settings.CreateSettings("TrafficLightDetection", "widthheightratiofilter", True)
            settings.CreateSettings("TrafficLightDetection", "pixelpercentagefilter", True)
            settings.CreateSettings("TrafficLightDetection", "otherlightsofffilter", True)

            settings.CreateSettings("TrafficLightDetection", "minrectsize", round(screen_width / 240))
            settings.CreateSettings("TrafficLightDetection", "maxrectsize", round(screen_width / 10))
            UpdateSettings()
            switchSelectedPlugin("plugins." + "TrafficLightDetection" + ".main")

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
            UpdateSettings()
            switchSelectedPlugin("plugins." + "TrafficLightDetection" + ".main")

        
        def update(self, data): 
            self.root.update()
            
    
    
    except Exception as ex:
        print(ex.args)