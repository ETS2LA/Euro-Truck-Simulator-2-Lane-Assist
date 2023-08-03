"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="LSTRDrawLanes", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="ExamplePlugin.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", 
    dynamicOrder="before game"
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
from PIL import ImageColor


# Copied from LSTRLaneDetection/LSTRLaneDetection/lstr/lstr.py
def draw_lanes(input_img, lane_points, lane_ids, color=(255,191,0), fillPoly=True, drawDots=False, drawLines=True):
    lane_colors = [(68,65,249),(44,114,243),(30,150,248),(74,132,249),(79,199,249),(109,190,144),(142, 144, 77),(161, 125, 39)]
    
    color = (color[2], color[1], color[0])
    
    # Write the detected line points in the image
    visualization_img = input_img.copy()

    # Draw a mask for the current lane
    right_lane = np.where(lane_ids==0)[0]
    left_lane = np.where(lane_ids==5)[0]

    if fillPoly:
        if(len(left_lane) and len(right_lane)):
            
            lane_segment_img = visualization_img.copy()

            points = np.vstack((lane_points[left_lane[0]].T,
                                np.flipud(lane_points[right_lane[0]].T)))
            cv2.fillConvexPoly(lane_segment_img, points, color, cv2.LINE_AA)

            visualization_img = cv2.addWeighted(visualization_img, 0.7, lane_segment_img, 0.3, 0)

    # Draw the lane points
    if drawDots or drawLines:   
        for lane_num,points in zip(lane_ids, lane_points):
            if drawDots:
                for lane_point in points.T:
                    cv2.circle(visualization_img, (lane_point[0],lane_point[1]), 3, lane_colors[lane_num], -1, cv2.LINE_AA)

            # Create a line from the lane points
            if drawLines:
                cv2.polylines(visualization_img, [points.T], False, lane_colors[lane_num], 2, cv2.LINE_AA)

            
    return visualization_img


def loadSettings():
    global drawLaneLines, drawLanePoints, fillLane, fillLaneColor
    
    drawLaneLines = settings.GetSettings("LSTRDrawLanes", "drawLaneLines")
    drawLanePoints = settings.GetSettings("LSTRDrawLanes", "drawLanePoints")
    fillLane = settings.GetSettings("LSTRDrawLanes", "fillLane")
    fillLaneColor = settings.GetSettings("LSTRDrawLanes", "fillLaneColor")
    

loadSettings()

import traceback

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    try:
        points, ids = data["LSTR"]["points"], data["LSTR"]["ids"]
        frame = data["frame"]
        
        newImage = draw_lanes(frame, points, ids, fillPoly=fillLane, drawDots=drawLanePoints, drawLines=drawLaneLines, color=ImageColor.getcolor(fillLaneColor, "RGB"))
        data["frame"] = newImage
        
    except Exception as ex:
        #traceback.print_exc()
        pass
    
    return data
    
    
def onEnable():
    pass

def onDisable():
    pass


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
            
            self.root = tk.Canvas(self.master, width=600, height=520)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.drawLanes = helpers.MakeCheckButton(self.root, "Draw Lane Lines", "LSTRDrawLanes", "drawLaneLines", 0, 0, default=True)
            self.drawPoints = helpers.MakeCheckButton(self.root, "Draw Lane Points", "LSTRDrawLanes", "drawLanePoints", 0, 1, default=False)
            self.fillLane = helpers.MakeCheckButton(self.root, "Fill Lane", "LSTRDrawLanes", "fillLane", 0, 2, default=True)
            self.fillLaneColor = helpers.MakeComboEntry(self.root, "Fill Lane Color", "LSTRDrawLanes", "fillLaneColor", 1, 0, isString=True, value="#10615D")
            
            helpers.MakeButton(self.root, "Save", self.save, 2, 0)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def save(self):
            settings.CreateSettings("LSTRDrawLanes", "drawLaneLines", self.drawLanes.get())
            settings.CreateSettings("LSTRDrawLanes", "drawLanePoints", self.drawPoints.get())
            settings.CreateSettings("LSTRDrawLanes", "fillLane", self.fillLane.get())
            settings.CreateSettings("LSTRDrawLanes", "fillLaneColor", self.fillLaneColor.get())
            loadSettings()
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)