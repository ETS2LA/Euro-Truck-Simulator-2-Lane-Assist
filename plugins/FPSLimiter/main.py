"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="FPSLimiter", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will limit the FPS to the desired amount.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="last" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import time

fps = settings.GetSettings("FPS Limiter", "fps")
if fps == None:
    settings.CreateSettings("FPS Limiter", "fps", 30)
    fps = 30

def onEnable():
    pass

def onDisable():
    pass

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    global fps
    
    # Calculate the ms so far this frame
    executionTime = 0
    for plugin in data["executionTimes"]:
        executionTime += float(data["executionTimes"][plugin])
    
    # Calculate the ms needed to reach the desired FPS
    timeNeeded = 1 / fps
    
    # Sleep for the remaining time
    sleepLenght = timeNeeded - executionTime
    if sleepLenght > 0:
        time.sleep(sleepLenght)
        
    return data

# Plugins can also have UIs, this works the same as the panel example
class UI():
    global fps
    
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
            self.fps = helpers.MakeComboEntry(self.root, "Desired FPS", "FPS Limiter", "fps", 0, 0, width=7)
            helpers.MakeLabel(self.root, "Please note that the accuracity depends on your system. (linux > macOS > windows)", 1,0, font=("Roboto", 8), padx=30, pady=10, columnspan=2)
            helpers.MakeButton(self.root, "Apply", lambda: self.applyFPS(), 2,0)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def applyFPS(self):
            global fps
            fps = self.fps.get()
            print(fps)
            settings.CreateSettings("FPS Limiter", "fps", fps)
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
            
    
    
    except Exception as ex:
        print(ex.args)