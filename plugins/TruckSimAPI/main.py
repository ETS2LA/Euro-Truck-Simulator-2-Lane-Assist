

from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="TruckSimAPI", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="API for the app to communicate with ETS2 and ATS.",
    version="0.1",
    author="Cloud-121",
    url="https://github.com/Cloud-121/ETS2-Python-Api",
    type="dynamic", # = Panel
    dynamicOrder="before image capture" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
from src.loading import LoadingWindow
from src.translator import Translate
import src.mainUI as mainUI
import time
import os
import math
from plugins.TruckSimAPI.scsPlugin import scsTelemetry

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
API = None
lastX = 0
lastY = 0
isConnected = False
popup = None
def plugin(data):
    global API
    global lastX
    global lastY
    
    try:
        checkAPI()
        if not isConnected:
            return data
    except:
        print("Error checking API status")
        import traceback
        traceback.print_exc()
        return data
    
    apiData = API.update()    
    data["api"] = apiData
    
    # Calculate the current driving angle based on this and last frames coordinates
    try:
        x = apiData["truckPosition"]["coordinateX"]
        y = apiData["truckPosition"]["coordinateZ"]
        
        dx = x - lastX
        dy = y - lastY
        
        # Make them a unit vector
        velocity = math.sqrt(dx**2 + dy**2)
        
        # Calculate the angle
        angle = math.degrees(math.atan2(dy, dx))
        
        # Add some smoothening to the angle
        try:
            angle = angle * 0.025 + data["last"]["api"]["angle"] * 0.975
        except: pass
        data["api"]["angle"] = angle
        data["api"]["velocity"] = [dx, dy]
        
        lastY = y
        lastX = x
        
    except: pass

    return data # Plugins need to ALWAYS return the data

def checkAPI(dontClosePopup=False):
    global API
    global isConnected
    global popup
    
    if API == None:
        API = scsTelemetry()
        
    data = API.update()
    
    if data["scsValues"]["telemetryPluginRevision"] < 2: 
        isConnected = False
        if popup == None:
            popup = helpers.ShowPopup("Waiting for ETS2 to connect\n\nIf you've just installed the SDK\nthen please restart the game.", "Telemetry Server", timeout=0, indeterminate=True, closeIfMainloopStopped=True if not dontClosePopup else False)
        if popup.closed:
            popup = None
    elif isConnected == False:
        isConnected = True
        helpers.ShowPopup("\nETS2 connected", "Telemetry Server", timeout=2)
        try:
            popup.close()
            popup = None
        except: pass


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    global API
    if API == None:
        API = scsTelemetry()
    
    data = API.update()

def onDisable():
    global popup
    
    try:
        popup.close()
        popup = None
    except: pass

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def updateData(self):
            self.list.delete(0, tk.END)
            # recursively get all the data from the API
            for key, value in self.data["api"].items():
                if type(value) == dict:
                    self.list.insert(tk.END, key + ":")
                    for key2, value2 in value.items():
                        self.list.insert(tk.END, "    " + key2 + ": " + str(value2))
                else:
                    self.list.insert(tk.END, key + ": " + str(value))
    
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            
            ttk.Button(self.root, text=Translate("Update Data"), command=self.updateData).pack()
            ttk.Label(self.root, text=Translate("Will only work when the app is enabled -> scrollable")).pack()
            # Create a list to hold all of the API data
            self.listVar = tk.StringVar()
            self.list = tk.Listbox(self.root, width=600, height=520, border=0, highlightthickness=0, listvariable=self.listVar)
            self.list.pack()
            
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
            self.data = data
    
    except Exception as ex:
        print(ex.args)
