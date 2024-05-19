import logging
#print = logging.info

import math
from ETS2LA.modules.TruckSimAPI.api import scsTelemetry
from ETS2LA.modules.TruckSimAPI.virtualAPI import scsTelemetry as virtualTelemetry

API = None
lastX = 0
lastY = 0
isConnected = False

def run(VirtualTelemetry_instead_of_notConnected=True):
    global API
    global lastX
    global lastY

    try:
        API = scsTelemetry()
        data = API.update()
        if data["sdkActive"] == False:
            return "not connected"
    except:
        if VirtualTelemetry_instead_of_notConnected == False:
            return "not connected"
        else:
            API = virtualTelemetry()
            data = API.update()

    # Calculate the current driving angle based on this and last frames coordinates
    try:
        x = data["truckPosition"]["coordinateX"]
        y = data["truckPosition"]["coordinateZ"]
        
        dx = x - lastX
        dy = y - lastY

        # Calculate the angle
        angle = math.degrees(math.atan2(dy, dx))

        data["angle"] = angle

        lastY = y
        lastX = x
    except:
        pass

    return data 

def Initialize():
    pass # Do nothing