"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="MSSScreenCapture", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Uses more cpu power than DXCam, but works on linux.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="ScreenCapture" # Will disable the other screen capture plugins
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import mss
import numpy as np
from PIL import Image

sct = mss.mss()

def CreateCamera():
    global monitor
    global width
    global height
    
    width = settings.GetSettings("dxcam", "width")
    if width == None:
        settings.CreateSettings("dxcam", "width", 1280)
        width = 1280

    height = settings.GetSettings("dxcam", "height")
    if height == None:
        settings.CreateSettings("dxcam", "height", 720)
        height = 720
        
    x = settings.GetSettings("dxcam", "x")
    if x == None:
        settings.CreateSettings("dxcam", "x", 0)
        x = 0

    y = settings.GetSettings("dxcam", "y")
    if y == None:
        settings.CreateSettings("dxcam", "y", 0)
        y = 0

    left, top = x, y
    right, bottom = left + width, top + height
    monitor = (left,top,right,bottom)
        

CreateCamera()

def onEnable():
    pass

def onDisable():
    pass

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    try:
        # Capture part of the screen
        frame = sct.grab(monitor)
        # Make it so that cv2 can read it
        frame = np.array(Image.frombytes('RGB', (width,height), sct.grab(monitor).rgb)) 
        data["frame"] = frame
        return data
    except Exception as ex:
        print(ex)
    


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
            
            self.root = tk.Canvas(self.master, width=600, height=520)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Helpers provides easy to use functions for creating consistent widgets!
            self.width = helpers.MakeComboEntry(self.root, "Width", "dxcam", "width", 0,0)
            self.height = helpers.MakeComboEntry(self.root, "Height", "dxcam", "height", 1,0)
            self.x = helpers.MakeComboEntry(self.root, "X", "dxcam", "x", 2,0)
            self.y = helpers.MakeComboEntry(self.root, "Y", "dxcam", "y", 3,0)
            
            helpers.MakeButton(self.root, "Apply", lambda: self.updateSettings(), 4,0)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def updateSettings(self):
            settings.CreateSettings("dxcam", "width", self.width.get())
            settings.CreateSettings("dxcam", "height", self.height.get())
            settings.CreateSettings("dxcam", "x", self.x.get())
            settings.CreateSettings("dxcam", "y", self.y.get())
            CreateCamera()
        
        def update(self): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)