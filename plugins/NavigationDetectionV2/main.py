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
    exclusive="LaneDetection",
    requires=["TruckSimAPI"]
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os

import plugins.DefaultSteering.main as DefaultSteering

import cv2
import numpy as np
import dxcam
import time
import pyautogui
import mouse
import math

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
        lanewidth = 1
    lanewidth = round(lanewidth, 2)

LoadSettings()


def plugin(data):
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
            

        if mouse.is_pressed(button="left") == True and circlex > 5 and circlex < width-5 and circley > 5 and circley < height-5:
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
                trafficlight = data["TrafficLightDetection"]
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
                    left_x_lane, right_x_lane = closest_x_pair
                except:
                    if leftsidetraffic == False:
                        left_x_lane = lanes[len(lanes)-2]
                        right_x_lane = lanes[len(lanes)-1]
                    else:
                        try:
                            left_x_lane = lanes[len(lanes)-4]
                            right_x_lane = lanes[len(lanes)-3]
                        except:
                            left_x_lane = lanes[len(lanes)-2]
                            right_x_lane = lanes[len(lanes)-1]
            else:
                if leftsidetraffic == False:
                    left_x_lane = lanes[len(lanes)-2]
                    right_x_lane = lanes[len(lanes)-1]
                else:
                    try:
                        left_x_lane = lanes[len(lanes)-4]
                        right_x_lane = lanes[len(lanes)-3]
                    except:
                        left_x_lane = lanes[len(lanes)-2]
                        right_x_lane = lanes[len(lanes)-1]
            cv2.line(filtered_frame_bw, (left_x_lane,y_coordinate_lane), (right_x_lane,y_coordinate_lane), (255,255,255),1)

            if left_x_lane == 0:
                left_x_lane = 1
            if left_x_turnincdetec == 0:
                left_x_turnincdetec = 1

            lane_width = right_x_lane - left_x_lane
        
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

            if trafficlight == "Red":
                if turnincoming == True:
                    timerforturnincoming = time.time() - 10

            if turnincoming == False and lane_width != 0:
                avg_lanewidth_counter += 1
                avg_lanewidth_value += lane_width
                avg_lanewidth = avg_lanewidth_value/avg_lanewidth_counter
            
            if turnincoming == False:
                center_x = (left_x_lane + right_x_lane) / 2 if left_x_lane and right_x_lane is not None else None
            else:
                if turnincdirec == "Right":
                    center_x = left_x_lane + avg_lanewidth/2
                else:
                    center_x = right_x_lane - avg_lanewidth/2
        
            center_x_turnincdetec = (left_x_turnincdetec + right_x_turnincdetec) / 2 if left_x_turnincdetec and right_x_turnincdetec is not None else None
            

        if lane_width > width/5: ######################################################### change the minimum lane width
            if width/2 - left_x_lane > right_x_lane - width/2:
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
        

        if center_x != width and center_x is not None:

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
        
        correction = round(distancetocenter * sensitivity, 3)

        data["LaneDetection"] = {}
        data["LaneDetection"]["difference"] = -correction/15

        data["NavigationDetectionV2"] = {}
        data["NavigationDetectionV2"]["turnincoming"] = turnincoming

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
        
    return data
        


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    pass

def onDisable():
    pass

# Plugins can also have UIs, this works the same as the panel example
class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        global colortheme
        colortheme = settings.GetSettings("User Interface", "ColorTheme")
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
            
            if colortheme == "SunValley":
                resizeWindow(985,740)
            if colortheme == "Azure" or colortheme == "AutumnOrange":
                resizeWindow(950,770)
            if colortheme == "Forest":
                resizeWindow(950,748)       
        
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
            
            self.root = tk.Canvas(self.master, width=750, height=750, border=0, highlightthickness=0)
            self.root.grid_propagate(1) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.curvemultipSlider = tk.Scale(self.root, from_=0.01, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=600, command=lambda x: self.UpdateSettings())
            self.curvemultipSlider.set(settings.GetSettings("NavigationDetectionV2", "curvemultip"))
            self.curvemultipSlider.grid(row=0, column=1, padx=10, pady=0, columnspan=2)
            self.curvemultip = helpers.MakeComboEntry(self.root, "Curvemultip", "NavigationDetectionV2", "curvemultip", 1,0)
            
            self.sensitivitySlider = tk.Scale(self.root, from_=0.01, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=600, command=lambda x: self.UpdateSettings())
            self.sensitivitySlider.set(settings.GetSettings("NavigationDetectionV2", "sensitivity"))
            self.sensitivitySlider.grid(row=2, column=1, padx=10, pady=0, columnspan=2)
            self.sensitivity = helpers.MakeComboEntry(self.root, "Sensitivity", "NavigationDetectionV2", "sensitivity", 3,0)

            self.offsetSlider = tk.Scale(self.root, from_=-20, to=20, resolution=0.1, orient=tk.HORIZONTAL, length=600, command=lambda x: self.UpdateSettings())
            self.offsetSlider.set(settings.GetSettings("NavigationDetectionV2", "offset"))
            self.offsetSlider.grid(row=4, column=1, padx=10, pady=0, columnspan=2)
            self.offset = helpers.MakeComboEntry(self.root, "Offset", "NavigationDetectionV2", "offset", 5,0)

            self.textsizeSlider = tk.Scale(self.root, from_=0, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=600, command=lambda x: self.UpdateSettings())
            self.textsizeSlider.set(settings.GetSettings("NavigationDetectionV2", "textsize"))
            self.textsizeSlider.grid(row=6, column=1, padx=10, pady=0, columnspan=2)
            self.textsize = helpers.MakeComboEntry(self.root, "Textsize", "NavigationDetectionV2", "textsize", 7,0)
            
            self.textdistancescaleSlider = tk.Scale(self.root, from_=0.1, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=600, command=lambda x: self.UpdateSettings())
            self.textdistancescaleSlider.set(settings.GetSettings("NavigationDetectionV2", "textdistancescale"))
            self.textdistancescaleSlider.grid(row=8, column=1, padx=10, pady=0, columnspan=2)
            self.textdistancescale = helpers.MakeComboEntry(self.root, "Textspacescale", "NavigationDetectionV2", "textdistancescale", 9,0)
            
            helpers.MakeEmptyLine(self.root, 10, 0)
            helpers.MakeCheckButton(self.root, "Lane Changing", "NavigationDetectionV2", "lanechanging", 11, 0, callback=lambda: LoadSettings())
            helpers.MakeLabel(self.root, "If activated, you can change the lane you are driving on using the indicators", 11, 1)
            self.lanechangingspeed = helpers.MakeComboEntry(self.root, "Lane Changing Speed", "NavigationDetectionV2", "lanechangingspeed", 12, 0, labelwidth=20, isFloat=True)
            self.lanewidth = helpers.MakeComboEntry(self.root, "Lane Width", "NavigationDetectionV2", "lanewidth", 13, 0, labelwidth=20, isFloat=True)
            helpers.MakeButton(self.root, "Save Lane Settings", self.save, 12, 2, pady=0, padx=0, width=16)

            def setnavcordstrue():
                global getnavcoordinates
                global disableshowimagelater
                getnavcoordinates = True
                if "ShowImage" not in settings.GetSettings("Plugins", "Enabled"):
                    disableshowimagelater = True
                    settings.AddToList("Plugins", "Enabled", "ShowImage")
                DefaultSteering.enabled = False
                variables.ENABLELOOP = True

            helpers.MakeButton(self.root, "Grab Coordinates", setnavcordstrue, 14, 2, pady=20, padx=5)

            helpers.MakeCheckButton(self.root, "Left-hand traffic", "NavigationDetectionV2", "leftsidetraffic", 14, 1, callback=lambda: LoadSettings())

            helpers.MakeCheckButton(self.root, "Automatic lane", "NavigationDetectionV2", "automaticlaneselection", 14, 0, callback=lambda: LoadSettings())

            self.root.pack(anchor="center", expand=False)
            self.root.update()

        def save(self):
            settings.CreateSettings("NavigationDetectionV2", "lanechangingspeed", float(self.lanechangingspeed.get()))
            settings.CreateSettings("NavigationDetectionV2", "lanewidth", float(self.lanewidth.get()))
            
            LoadSettings()
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)