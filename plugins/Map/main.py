"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="Map", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Very experimental!",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before game", # Will run the plugin before anything else in the mainloop (data will be empty)
    noUI=True
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os

import plugins.Map.VisualizeRoads.main as VisualizeRoads
import cv2

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):

    try:
        try: 
            x = data["api"]["x"]
            y = data["api"]["y"]
            z = data["api"]["z"]
        except: 
            return data
        
        cv2.namedWindow("Roads", cv2.WINDOW_NORMAL)
        # Make it on top
        cv2.setWindowProperty("Roads", cv2.WND_PROP_TOPMOST, 1)
        roads, img = VisualizeRoads.GetRoadsWithinRange(x, z, 1024)
        cv2.imshow("Roads", img)
        
        
    except Exception as ex:
        print(ex)

    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    VisualizeRoads.ParseJsonFile()
    pass

def onDisable():
    pass

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
#             self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
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