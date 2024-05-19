import logging
print = logging.info

import math
from ETS2LA.modules.TruckSimAPI.api import scsTelemetry
from ETS2LA.modules.TruckSimAPI.virtualAPI import scsTelemetry as virtualTelemetry

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
API = None
lastX = 0
lastY = 0
isConnected = False
popup = None
def run(returnVirtualTelemetryInstead=True):
    global API
    global lastX
    global lastY
    
    try:
        checkAPI(returnVirtualTelemetryInstead=returnVirtualTelemetryInstead)
        if isConnected == False and returnVirtualTelemetryInstead == False:
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

def checkAPI(returnVirtualTelemetryInstead=True):
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

    if isConnected == False and returnVirtualTelemetryInstead == True:
        API = virtualTelemetry()

def Initialize():
    pass # Do nothing