"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="UFLDDrawLanes", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will draw the lanes obtained by UFLD.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before game", # Will run the plugin before anything else in the mainloop (data will be empty)
    noUI = True
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import numpy as np
import cv2

# Copied from LSTRLaneDetection/LSTRLaneDetection/lstr/lstr.py
def draw_lanes(input_img, leftMostLane, leftLane, rightLane, rightMostLane, color=(0,191,255), fillPoly=True, drawDots=False, drawLines=True):

    color = (color[2], color[1], color[0])
    
    numbers = [0,1,2,3]
    
    # Write the detected line points in the image
    visualization_img = input_img.copy()


    if fillPoly:
        if(len(leftLane) and len(rightLane)):
            
            lane_segment_img = visualization_img.copy()

            points = np.vstack((leftLane,
                                np.flipud(rightLane)))
            cv2.fillConvexPoly(lane_segment_img, points, color, cv2.LINE_AA)

            visualization_img = cv2.addWeighted(visualization_img, 0.7, lane_segment_img, 0.3, 0)

    # Draw the lane points
    if drawDots or drawLines:   
        for lane_num,lanePoints in zip(numbers, [leftMostLane, leftLane, rightLane, rightMostLane]):
            if drawDots:
                for lane_point in lanePoints:
                    cv2.circle(visualization_img, (lane_point[0],lane_point[1]), 3, laneColors[lane_num], -1, cv2.LINE_AA)

            # Create a line from the lane points
            if drawLines:
                points = np.array(lanePoints)
                cv2.polylines(visualization_img, [points], False, laneColors[lane_num], 2, cv2.LINE_AA)

            
    return visualization_img

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    try:

        farLeftLane = data["LaneDetection"]["farLeftLane"]
        leftLane = data["LaneDetection"]["leftLane"]
        rightLane = data["LaneDetection"]["rightLane"]
        farRightLane = data["LaneDetection"]["farRightLane"]
        
        newImage = draw_lanes(data["frame"], farLeftLane, leftLane, rightLane, farRightLane)
        
        data["frame"] = newImage
        
    except Exception as ex: 
        if "LaneDetection" not in ex.args[0]:
            print(ex)
        pass

    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    global laneColors
    fillColor = color=(255,191,0)

    #Lanes are :   Left         Left most    Left side    Right Side   Right        Right most    ?              ?
    laneColors = [(68,65,249),(44,114,243),(30,150,248),(74,132,249),(79,199,249),(109,190,144),(142, 144, 77),(161, 125, 39)]
    laneColors = [(color[2], color[1], color[0]) for color in laneColors]
    #             Left most      Left           Right          Right most
    laneColors = [laneColors[1], laneColors[0], laneColors[4], laneColors[5]]
    pass

def onDisable():
    pass

# Plugins can also have UIs, this works the same as the panel example
class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Helpers provides easy to use functions for creating consistent widgets!
            helpers.MakeLabel(self.root, "This is a plugin!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            # Use the mainUI.quit() function to quit the app
            helpers.MakeButton(self.root, "Quit", lambda: mainUI.quit(), 1,0, padx=30, pady=10)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)
