"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
PluginInfo = PluginInformation(
    name="MSSScreenCapture", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Uses more cpu power than bettercam, but works on linux.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="ScreenCapture" # Will disable the other screen capture plugins
)

import src.settings as settings
import src.helpers as helpers
from src.logger import print
from PIL import Image
import tkinter as tk
import numpy as np
import pyautogui
import mss
import cv2

sct = mss.mss()

def CreateCamera():
    global width
    global height
    global monitor
    global monitor_full
    
    width = settings.GetSettings("bettercam", "width")
    if width == None:
        settings.CreateSettings("bettercam", "width", 1280)
        width = 1280

    height = settings.GetSettings("bettercam", "height")
    if height == None:
        settings.CreateSettings("bettercam", "height", 720)
        height = 720
        
    x = settings.GetSettings("bettercam", "x")
    if x == None:
        settings.CreateSettings("bettercam", "x", 0)
        x = 0

    y = settings.GetSettings("bettercam", "y")
    if y == None:
        settings.CreateSettings("bettercam", "y", 0)
        y = 0

    left, top = x, y
    right, bottom = left + width, top + height
    monitor = (left,top,right,bottom)
    monitor_full = (0,0,pyautogui.size().width,pyautogui.size().height)

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
        # Capture full screen
        frame = sct.grab(monitor_full)
        # Make it so that cv2 can read it
        frame = np.array(Image.frombytes('RGB', (monitor_full[2], monitor_full[3]), sct.grab(monitor_full).rgb)) 
        # Convert to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Save the frame
        data["frameFull"] = frame
        # Crop the frame to the selected area
        frame = frame[monitor[1]:monitor[3], monitor[0]:monitor[2]]
        # Save the cropped frame
        data["frame"] = frame
        data["frameOriginal"] = frame
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
            
            import screeninfo
            
            try:
                screen = screeninfo.get_monitors()[settings.GetSettings("bettercam", "display")]
            except:
                screen = screeninfo.get_monitors()[0]
                
            self.screenHeight = int(screen.height)
            self.screenWidth = int(screen.width)
            
            def updateWidth(value):
                self.width.set(value)
                self.xSlider.config(to=self.screenWidth - int(value))
                
            def updateHeight(value):
                self.height.set(value)
                self.ySlider.config(to=self.screenHeight - int(value))
            
            def updateX(value):
                self.x.set(value)
                
            def updateY(value):
                self.y.set(value)
            
            self.root = tk.Canvas(self.master, width=600, height=520)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Helpers provides easy to use functions for creating consistent widgets!
            self.widthSlider = tk.Scale(self.root, from_=0, to=self.screenWidth, orient=tk.HORIZONTAL, length=500, command=lambda x: updateWidth(self.widthSlider.get()))
            self.widthSlider.set(settings.GetSettings("bettercam", "width"))
            self.widthSlider.grid(row=0, column=0, padx=10, pady=0, columnspan=2)
            self.width = helpers.MakeComboEntry(self.root, "Width", "bettercam", "width", 1,0)
            
            self.heightSlider = tk.Scale(self.root, from_=0, to=self.screenHeight, orient=tk.HORIZONTAL, length=500, command=lambda x: updateHeight(self.heightSlider.get()))
            self.heightSlider.set(settings.GetSettings("bettercam", "height"))
            self.heightSlider.grid(row=2, column=0, padx=10, pady=0, columnspan=2)
            self.height = helpers.MakeComboEntry(self.root, "Height", "bettercam", "height", 3,0)
            
            self.xSlider = tk.Scale(self.root, from_=0, to=self.screenWidth - self.width.get(), orient=tk.HORIZONTAL, length=500, command=lambda x: updateX(self.xSlider.get()))
            self.xSlider.set(settings.GetSettings("bettercam", "x"))
            self.xSlider.grid(row=4, column=0, padx=10, pady=0, columnspan=2)
            self.x = helpers.MakeComboEntry(self.root, "X", "bettercam", "x", 5,0)
            
            self.ySlider = tk.Scale(self.root, from_=0, to=self.screenHeight - self.height.get(), orient=tk.HORIZONTAL, length=500, command=lambda x: updateY(self.ySlider.get()))
            self.ySlider.set(settings.GetSettings("bettercam", "y"))
            self.ySlider.grid(row=6, column=0, padx=10, pady=0, columnspan=2)
            self.y = helpers.MakeComboEntry(self.root, "Y", "bettercam", "y", 7,0)
            self.display = helpers.MakeComboEntry(self.root, "Display", "bettercam", "display", 8,0, value=0)
            
            helpers.MakeButton(self.root, "Apply", lambda: self.updateSettings(), 9,0)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def updateSettings(self):
            settings.CreateSettings("bettercam", "width", self.width.get())
            settings.CreateSettings("bettercam", "height", self.height.get())
            settings.CreateSettings("bettercam", "x", self.x.get())
            settings.CreateSettings("bettercam", "y", self.y.get())
            CreateCamera()
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)