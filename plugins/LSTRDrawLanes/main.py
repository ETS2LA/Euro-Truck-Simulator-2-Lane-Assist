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
    dynamicOrder="before game",
    noUI=True
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
def draw_lanes(input_img, lane_points, lane_ids, color=(255,191,0), fillPoly=False):
    lane_colors = [(68,65,249),(44,114,243),(30,150,248),(74,132,249),(79,199,249),(109,190,144),(142, 144, 77),(161, 125, 39)]

    # Create a black image of the size of the input image
    visualization_img = input_img.copy()

    # Draw a mask for the current lane
    right_lane = np.where(lane_ids==0)[0]
    left_lane = np.where(lane_ids==5)[0]

    if(len(left_lane) and len(right_lane)):
        
        lane_segment_img = visualization_img.copy()

        points = np.vstack((lane_points[left_lane[0]].T,
                            np.flipud(lane_points[right_lane[0]].T)))
        if fillPoly: cv2.fillConvexPoly(lane_segment_img, points, color=color)
        visualization_img = cv2.addWeighted(visualization_img, 0.7, lane_segment_img, 0.3, 0)
        
    for lane_num,lane_points in zip(lane_ids, lane_points):
        for lane_point in lane_points.T:
            cv2.circle(visualization_img, (lane_point[0],lane_point[1]), 3, lane_colors[lane_num], -1)

    return visualization_img

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    try:
        points, ids = data["LSTR"]["points"], data["LSTR"]["ids"]
        frame = data["frame"]
        
        newImage = draw_lanes(frame, points, ids, fillPoly=False)
        data["frame"] = newImage
        
    except Exception as ex:
        pass
    
    return data
    
    


# Plugins can also have UIs, this works the same as the panel example
# class UI():
#     try: # The panel is in a try loop so that the logger can log errors if they occur
#         
#         def __init__(self, master) -> None:
#             self.master = master # "master" is the mainUI window
#             self.exampleFunction()
#         
#         def destroy(self):
#             self.done = True
#             self.root.destroy()
#             del self
# 
#         
#         def exampleFunction(self):
#             
#             try:
#                 self.root.destroy() # Load the UI each time this plugin is called
#             except: pass
#             
#             self.root = tk.Canvas(self.master, width=600, height=520)
#             self.root.grid_propagate(0) # Don't fit the canvast to the widgets
#             self.root.pack_propagate(0)
#             
#             # Helpers provides easy to use functions for creating consistent widgets!
#             helpers.MakeLabel(self.root, "This is a plugin!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
#             # Use the mainUI.quit() function to quit the app
#             helpers.MakeButton(self.root, "Quit", lambda: mainUI.quit(), 1,0, padx=30, pady=10)
#             
#             self.root.pack(anchor="center", expand=False)
#             self.root.update()
#         
#         
#         def update(self): # When the panel is open this function is called each frame 
#             self.root.update()
#     
#     
#     except Exception as ex:
#         print(ex.args)