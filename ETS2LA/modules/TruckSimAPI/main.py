import math
from ETS2LA.modules.TruckSimAPI.api import scsTelemetry
from ETS2LA.modules.TruckSimAPI.virtualAPI import scsTelemetry as virtualTelemetry

API = None
VIRTUAL_API = None
TRAILER = False
lastX = 0
lastY = 0
isConnected = False

eventCallbacks = {
    "jobEnded": [],
    "jobStarted": []
}

def listen(event, callback):
    if event in eventCallbacks:
        eventCallbacks[event].append(callback)
        
wasOnJob = False
def _checkEvents(data):
    global wasOnJob
    
    if data["specialBool"]["onJob"] == True and wasOnJob == False:
        for callback in eventCallbacks["jobStarted"]:
            callback(data)
        wasOnJob = True
    elif data["specialBool"]["onJob"] == False and wasOnJob == True:
        for callback in eventCallbacks["jobEnded"]:
            callback(data)
        wasOnJob = False
    

def run(Fallback=True):
    global API
    global lastX
    global lastY

    try:
        data = API.update(trailerData=TRAILER)
        if data["sdkActive"] == False:
            if Fallback == False:
                return "not connected"
            else:
                data = VIRTUAL_API.update(trailerData=TRAILER)
    except:
        if Fallback == False:
            return "not connected"
        else:
            data = VIRTUAL_API.update(trailerData=TRAILER)

    _checkEvents(data)

    return data 

def Initialize():
    global API
    global VIRTUAL_API
    API = scsTelemetry()
    VIRTUAL_API = virtualTelemetry()