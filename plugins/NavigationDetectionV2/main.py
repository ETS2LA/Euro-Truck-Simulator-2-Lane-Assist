"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import resizeWindow

PluginInfo = PluginInformation(
    name="NavigationDetectionV2", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Uses the navigation line in the minimap.",
    version="0.1",
    author="Glas42",
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



import cv2
import numpy as np
import dxcam
import time
import pyautogui
import mouse

screen_width, screen_height = pyautogui.size()

timerforturnincoming = 0
white_limit = (1, 1, 1)
getnavcoordinates = False

def LoadSettings():
    global curvemultip
    global sensitivity
    global offset
    global textsize
    global textdistancescale
    global navsymbolx
    global navsymboly
    global getnavcoordinates
    global navcoordsarezero
    
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
    else:
        navcoordsarezero = False

LoadSettings()


def plugin(data):
    global timerforturnincoming
    global white_limit
    global getnavcoordinates
    global navcoordsarezero

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

        if mouse.is_pressed(button="left") == True and circlex > 5 and circlex < width-5 and circley > 5 and circley < height-5:
            settings.CreateSettings("NavigationDetectionV2", "navsymbolx", circlex)    
            settings.CreateSettings("NavigationDetectionV2", "navsymboly", circley)
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

        if circley != None:        
        
            lanes = GetArrayOfLaneEdges(y_coordinate_turnincdetec)
            left_x_turnincdetec = lanes[len(lanes)-2]
            right_x_turnincdetec = lanes[len(lanes)-1]
            cv2.line(filtered_frame_bw, (left_x_turnincdetec,y_coordinate_turnincdetec), (right_x_turnincdetec,y_coordinate_turnincdetec), (255,255,255),1)

            lanes = GetArrayOfLaneEdges(y_coordinate_lane)
            left_x_lane = lanes[len(lanes)-2]
            right_x_lane = lanes[len(lanes)-1]
            cv2.line(filtered_frame_bw, (left_x_lane,y_coordinate_lane), (right_x_lane,y_coordinate_lane), (255,255,255),1)

            
            center_x = (left_x_lane + right_x_lane) / 2 if left_x_lane and right_x_lane is not None else None
        
            center_x_turnincdetec = (left_x_turnincdetec + right_x_turnincdetec) / 2 if left_x_turnincdetec and right_x_turnincdetec is not None else None
            
            lane_width = right_x_lane - left_x_lane
        
            lane_width_turnincdetec = right_x_turnincdetec - left_x_turnincdetec

        
        if lane_width_turnincdetec > width/5:
            timerforturnincoming = time.time()
        
        if start_time - timerforturnincoming < 30:
            turnincoming = True
        else:
            turnincoming = False

        if lane_width > width/5:
            if width/2 - left_x_lane > right_x_lane - width/2:
                turn = "Left"
                timerforturnincoming = time.time() - 27
            else:
                turn = "Right"
                timerforturnincoming = time.time() - 27
        else:
            turn = "none"


        if center_x != width and center_x is not None:

            curve = round((center_x - center_x_turnincdetec)/30 * curvemultip, 3)
            if turn != "none" or turnincoming == True:
                curve = 0
            distancetocenter = round((width/2-center_x)-curve-automaticxoffset, 3) - offset
            lanedetected = "Yes"
        else:
            lanedetected = "No"
            distancetocenter = 0
            curve = 0
            center_x = round(width/2)
            center_x_turnincdetec = round(width/2)
        
        correction = round(distancetocenter * sensitivity, 3)

        data["LaneDetection"] = {}
        data["LaneDetection"]["difference"] = -correction/15

        filtered_frame_red_green = cv2.cvtColor(filtered_frame_red_green, cv2.COLOR_BGR2RGB)
 
        if textsize != 0:      
            cv2.putText(filtered_frame_bw, f"lanedetected: {lanedetected}", (round(10*textdistancescale), round(20*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(filtered_frame_bw, f"curve: {curve}", (round(10*textdistancescale), round(40*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(filtered_frame_bw, f"correction: {correction}", (round(10*textdistancescale), round(60*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(filtered_frame_bw, f"turninc: {turnincoming}", (round(10*textdistancescale), round(80*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(filtered_frame_bw, f"turn: {turn}", (round(10*textdistancescale), round(100*textdistancescale)+30), cv2.FONT_HERSHEY_SIMPLEX, textsize, (255, 255, 255), 1, cv2.LINE_AA)
        
        data["frame"] = filtered_frame_bw
        
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
            self.curvemultip.set(self.curvemultipSlider.get())
            self.sensitivity.set(self.sensitivitySlider.get())
            self.offset.set(self.offsetSlider.get())
            self.textsize.set(self.textsizeSlider.get())
            self.textdistancescale.set(self.textdistancescaleSlider.get())
            
            settings.CreateSettings("NavigationDetectionV2", "curvemultip", self.curvemultipSlider.get())
            settings.CreateSettings("NavigationDetectionV2", "sensitivity", self.sensitivitySlider.get())
            settings.CreateSettings("NavigationDetectionV2", "offset", self.offsetSlider.get())
            settings.CreateSettings("NavigationDetectionV2", "textsize", self.textsizeSlider.get())
            settings.CreateSettings("NavigationDetectionV2", "textdistancescale", self.textdistancescaleSlider.get())
            
            LoadSettings()
            
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(1) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.curvemultipSlider = tk.Scale(self.root, from_=0.01, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.curvemultipSlider.set(settings.GetSettings("NavigationDetectionV2", "curvemultip"))
            self.curvemultipSlider.grid(row=0, column=1, padx=10, pady=0, columnspan=2)
            self.curvemultip = helpers.MakeComboEntry(self.root, "Curvemultip", "NavigationDetectionV2", "curvemultip", 1,0)
            
            self.sensitivitySlider = tk.Scale(self.root, from_=0.01, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.sensitivitySlider.set(settings.GetSettings("NavigationDetectionV2", "sensitivity"))
            self.sensitivitySlider.grid(row=2, column=1, padx=10, pady=0, columnspan=2)
            self.sensitivity = helpers.MakeComboEntry(self.root, "Sensitivity", "NavigationDetectionV2", "sensitivity", 3,0)

            self.offsetSlider = tk.Scale(self.root, from_=-20, to=20, resolution=0.1, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.offsetSlider.set(settings.GetSettings("NavigationDetectionV2", "offset"))
            self.offsetSlider.grid(row=4, column=1, padx=10, pady=0, columnspan=2)
            self.offset = helpers.MakeComboEntry(self.root, "Offset", "NavigationDetectionV2", "offset", 5,0)

            self.textsizeSlider = tk.Scale(self.root, from_=0, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.textsizeSlider.set(settings.GetSettings("NavigationDetectionV2", "textsize"))
            self.textsizeSlider.grid(row=6, column=1, padx=10, pady=0, columnspan=2)
            self.textsize = helpers.MakeComboEntry(self.root, "Textsize", "NavigationDetectionV2", "textsize", 7,0)
            
            self.textdistancescaleSlider = tk.Scale(self.root, from_=0.1, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=460, command=lambda x: self.UpdateSettings())
            self.textdistancescaleSlider.set(settings.GetSettings("NavigationDetectionV2", "textdistancescale"))
            self.textdistancescaleSlider.grid(row=8, column=1, padx=10, pady=0, columnspan=2)
            self.textdistancescale = helpers.MakeComboEntry(self.root, "Textspacescale", "NavigationDetectionV2", "textdistancescale", 9,0)
            
            def setnavcordstrue():
                global getnavcoordinates
                getnavcoordinates = True
                print(getnavcoordinates)
            helpers.MakeButton(self.root, "Grab Coordinates", setnavcordstrue, 10, 0, pady=20, padx=5)

            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)