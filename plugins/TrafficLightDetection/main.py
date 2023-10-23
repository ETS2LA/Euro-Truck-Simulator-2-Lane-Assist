"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="TrafficLightDetection", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will detect the traffic lights currently visible.",
    version="0.1",
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
import os


import cv2
import numpy as np
import dxcam
import time
import pyautogui

screen_width, screen_height = pyautogui.size()

finalwindow = 1
grayscalewindow = 1
redgreenwindow = 1


# CHANGES : 
# 
# Everything in the while loop is now located in the plugin function
# Everything outside the while loop is in the update settings function. This includes the window size changing.
# I exchanged some variables to use the data[] dictionary for information (like the frame and current fps)

# RECOMMENDATIONS : 
# 
# You should probably make it so that people can change the cropping on each side (left, top, right, bottom), 
# since for example on my display 5120x1440 it is a lot of pixels to go through.

def UpdateSettings():
    global min_rect_size
    global max_rect_size
    global width_height_ratio
    global circlepercent
    global maxcircleoffset
    global finalwindow
    global grayscalewindow
    global redgreenwindow
    global windowscale
    global textsize
    
    finalwindow = int(settings.GetSettings("TrafficLightDetection", "finalwindow", True))
    grayscalewindow = int(settings.GetSettings("TrafficLightDetection", "grayscalewindow", True))
    redgreenwindow = int(settings.GetSettings("TrafficLightDetection", "redgreenwindow", True))
    windowscale = float(settings.GetSettings("TrafficLightDetection", "scale", 1))
    textsize = float(settings.GetSettings("TrafficLightDetection", "textsize", 1))

    if grayscalewindow == 1:
        cv2.namedWindow('Traffic Lights Detection - B/W', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Traffic Lights Detection - B/W', round(screen_width/2*windowscale), round(screen_height/3*windowscale))
        cv2.setWindowProperty('Traffic Lights Detection - B/W', cv2.WND_PROP_TOPMOST, 1)
    if redgreenwindow == 1:
        cv2.namedWindow('Traffic Lights Detection - Red/Green', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Traffic Lights Detection - Red/Green', round(screen_width/2*windowscale), round(screen_height/3*windowscale))
        cv2.setWindowProperty('Traffic Lights Detection - Red/Green', cv2.WND_PROP_TOPMOST, 1)
    if finalwindow == 1:
        cv2.namedWindow('Traffic Lights Detection - Final', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Traffic Lights Detection - Final', round(screen_width/2*windowscale), round(screen_height/3*windowscale))
        cv2.setWindowProperty('Traffic Lights Detection - Final', cv2.WND_PROP_TOPMOST, 1)
    
    min_rect_size = screen_height / 240
    max_rect_size = screen_height / 9
    width_height_ratio = 0.2
    circlepercent = 0.785
    maxcircleoffset = 0.15

    if min_rect_size < 8:
        min_rect_size = 8



# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    
    try:
        frame = data["frameFull"]
        frame = frame[0:round(screen_height/1.5), 0:screen_width]
    except:
        return data
    
    if frame is None: return data
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    

    lower_red = np.array([200, 0, 0])
    upper_red = np.array([255, 110, 110])
    lower_green = np.array([0, 200, 0])
    upper_green = np.array([150, 255, 230])

    
    mask_red = cv2.inRange(rgb_frame, lower_red, upper_red)
    mask_green = cv2.inRange(rgb_frame, lower_green, upper_green)

    filtered_frame_red_green = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
    filtered_frame_bw = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2GRAY)
    final_frame = frame

    currentnearest = 0
    currentneareststate = "---"
    currentdistance = "---"
    ratio = 0

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
                circleplusoffset = circlepercent + maxcircleoffset
                circleminusoffset = circlepercent - maxcircleoffset
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

                        if grayscalewindow == 1:
                            cv2.rectangle(filtered_frame_bw, (x, y), (x + w, y + h), (150, 150, 150), 2)
                        if redgreenwindow == 1:
                            cv2.rectangle(filtered_frame_red_green, (x, y), (x + w, y + h), (150, 150, 150), 2)
                            cv2.rectangle(filtered_frame_red_green, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                            cv2.rectangle(filtered_frame_red_green, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)
                        if finalwindow == 1:
                            cv2.rectangle(final_frame, (x, y), (x + w, y + h), (150, 150, 150), 2)
                            cv2.rectangle(final_frame, (x, yoffset1), (x + w, y + h), (150, 150, 150), 2)
                            cv2.rectangle(final_frame, (x, yoffset2), (x + w, y + h), (150, 150, 150), 2)

                        if green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1:
                            ratio = round(green_ratio - circlepercent, 2)
                            if grayscalewindow == 1:
                                cv2.putText(filtered_frame_bw, f"{round(ratio,2)}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,   0.8, (255, 255, 255), 1, cv2.LINE_AA)
                        if red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1:
                            ratio = round(red_ratio - circlepercent, 2)
                            if grayscalewindow == 1:
                                cv2.putText(filtered_frame_bw, f"{round(ratio,2)}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,   0.8, (255, 255, 255), 1, cv2.LINE_AA)

                        if currentnearest < w:
                            currentnearest = w
                            currentneareststate = colorstr
                            currentdistance = max_rect_size - w - min_rect_size
                            if currentdistance < 0:
                                currentdistance = 0

    data["TrafficLightDetection"] = currentneareststate                   

    if grayscalewindow == 1:
        if textsize > 0:         
            cv2.putText(filtered_frame_bw, f"Nearest: {currentneareststate}, Distance: {currentdistance}", (20, round(40*textsize)), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 2, cv2.LINE_AA) 
        cv2.imshow('Traffic Lights Detection - B/W', filtered_frame_bw)
    if redgreenwindow == 1:          
        cv2.imshow('Traffic Lights Detection - Red/Green', filtered_frame_red_green)
    if finalwindow == 1:
        cv2.imshow('Traffic Lights Detection - Final', final_frame)

    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    UpdateSettings()
    pass

def onDisable():
    # Delete the windows
    cv2.destroyWindow('Traffic Lights Detection - B/W')
    cv2.destroyWindow('Traffic Lights Detection - Red/Green')
    cv2.destroyWindow('Traffic Lights Detection - Final')
    pass

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
            
        def SaveAndLoadSettings(self):
            settings.CreateSettings("TrafficLightDetection", "scale", self.scaleSlider.get())
            settings.CreateSettings("TrafficLightDetection", "textsize", self.textsizeSlider.get())
            UpdateSettings()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self
            
        def UpdateScaleValueFromSlider(self):
            self.scale.set(self.scaleSlider.get())
            self.textsize.set(self.textsizeSlider.get())
        
        def exampleFunction(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(1) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            helpers.MakeCheckButton(self.root, "Final Window", "TrafficLightDetection", "finalwindow", 1, 0)
            helpers.MakeCheckButton(self.root, "Grayscale Window", "TrafficLightDetection", "grayscalewindow", 2, 0)
            helpers.MakeCheckButton(self.root, "Red/Green Window", "TrafficLightDetection", "redgreenwindow", 3, 0)
            
            self.scaleSlider = tk.Scale(self.root, from_=0.1, to=2, resolution=0.01, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateScaleValueFromSlider())
            self.scaleSlider.set(settings.GetSettings("TrafficLightDetection", "scale", 0.5))
            self.scaleSlider.grid(row=4, column=0, padx=10, pady=0, columnspan=2)
            self.scale = helpers.MakeComboEntry(self.root, "Scale", "TrafficLightDetection", "scale", 5,0)

            self.textsizeSlider = tk.Scale(self.root, from_=0, to=2, resolution=0.01, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateScaleValueFromSlider())
            self.textsizeSlider.set(settings.GetSettings("TrafficLightDetection", "textsize", 0.5))
            self.textsizeSlider.grid(row=6, column=0, padx=10, pady=0, columnspan=2)
            self.textsize = helpers.MakeComboEntry(self.root, "Font size", "TrafficLightDetection", "textsize", 7,0)
            
            helpers.MakeButton(self.root, "Save Settings", self.SaveAndLoadSettings, 9, 0)

            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def update(self, data): # When the panel is open this function is called each frame 
                self.root.update()
            
    except Exception as ex:
        print(ex.args)