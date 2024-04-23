

from ETS2LA.plugins.plugin import PluginInformation
#from src.logger import print
import logging
print = logging.info

PluginInfo = PluginInformation(
    name="TruckSimAPI", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="API for the app to communicate with ETS2 and ATS.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/ETS2LA",
    type="dynamic", # = Panel
    dynamicOrder="before image capture" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import time
import os
import math
from ETS2LA.modules.TruckSimAPI.api import scsTelemetry

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
API = None
lastX = 0
lastY = 0
isConnected = False
popup = None
def run():
    global API
    global lastX
    global lastY
    
    try:
        checkAPI()
        if not isConnected:
            return "not connected"
    except:
        print("Error checking API status")
        import traceback
        traceback.print_exc()
        return "error checking API status"
    
    apiData = API.update()    
    data = apiData
    
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
        
        data["angle"] = angle
        data["velocity"] = [dx, dy]
        
        lastY = y
        lastX = x
        
    except: pass

    return data 

def checkAPI(dontClosePopup=False):
    global API
    global isConnected
    global popup
    
    if API == None:
        API = scsTelemetry()
        
    data = API.update()
    
    if data["scsValues"]["telemetryPluginRevision"] < 2: 
        isConnected = False
    elif isConnected == False:
        isConnected = True


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    global API
    if API == None:
        API = scsTelemetry()
    
    data = API.update()

def onDisable():
    pass
