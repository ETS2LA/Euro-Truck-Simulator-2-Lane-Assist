"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="LaneDepartureWarning", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will beep at you if you leave your lane.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before controller" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.sounds as sounds
import os

rightLimit = 0.13
leftLimit = -0.13

def loadSettings():
    rightLimit = settings.GetSettings("laneDepartureAssist", "rightLimit")
    if rightLimit == None:
        settings.CreateSettings("laneDepartureAssist", "rightLimit", 0.13)
        rightLimit = 0.13
        
    leftLimit = settings.GetSettings("laneDepartureAssist", "leftLimit")
    if leftLimit == None:
        settings.CreateSettings("laneDepartureAssist", "leftLimit", -0.13)
        leftLimit = -0.13


# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    try:
        currentOffset = data["LaneDetection"]["difference"]

        indicating = data["api"]["truckBool"]["blinkerLeftActive"] or data["api"]["truckBool"]["blinkerLeftActive"]
        
        if (currentOffset > rightLimit or currentOffset < leftLimit) and not indicating:
            sounds.PlaysoundFromLocalPath("assets/sounds/warning.mp3")
    except:
        pass

    return data # Plugins need to ALWAYS return the data


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
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def updateRightLimit(self, value):
            settings.CreateSettings("laneDepartureAssist", "rightLimit", value)
            loadSettings()
        
        def updateLeftLimit(self, value):
            settings.CreateSettings("laneDepartureAssist", "leftLimit", value)
            loadSettings()
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Make a slider for both the right and left limit
            self.rightLimit = tk.Scale(self.root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=300, label="Right Limit", command=self.updateRightLimit)
            self.rightLimit.set(settings.GetSettings("laneDepartureAssist", "rightLimit", value=0.13))
            self.rightLimit.pack(anchor="center", expand=False)
            
            self.leftLimit = tk.Scale(self.root, from_=0, to=-1, resolution=0.01, orient=tk.HORIZONTAL, length=300, label="Left Limit", command=self.updateLeftLimit)
            self.leftLimit.set(settings.GetSettings("laneDepartureAssist", "leftLimit", value=-0.13))
            self.leftLimit.pack(anchor="center", expand=False)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)
