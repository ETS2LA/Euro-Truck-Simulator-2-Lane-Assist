import math
import json
import os
from ETS2LA.modules.TruckSimAPI.api import scsTelemetry
from ETS2LA.modules.TruckSimAPI.virtualAPI import scsTelemetry as virtualTelemetry

API = None
VIRTUAL_API = None
TRAILER = False
CHECK_EVENTS = False # DO NOT TURN THIS ON!!! PLEASE USE THE EVENTS SYSTEM INSTEAD!!!
lastX = 0
lastY = 0
isConnected = False

eventCallbacks = {
    "jobStarted": [],
    "jobCancelled": [],
    "jobDelivered": [],
    "jobFinished": [],
    "refuelStarted": [],
    "refuelPayed": []
}

def listen(event, callback):
    if event in eventCallbacks:
        eventCallbacks[event].append(callback)
        
def setSpecialBool(bool, value):
    offset = API.specialBoolOffsets[bool]
    try:
        API.setBool(offset, value)
    except:
        VIRTUAL_API.setBool(offset, value)
        
wasOnJob = False
wasRefueling = False
def _checkEvents(data):
    global API
    global VIRTUAL_API
    global wasOnJob, wasRefueling
    onJob = data["specialBool"]["onJob"]
    refueling = data["specialBool"]["refuel"]
    finished = data["specialBool"]["jobFinished"]
    cancelled = data["specialBool"]["jobCancelled"]
    delivered = data["specialBool"]["jobDelivered"]
    refuelPayed = data["specialBool"]["refuelPayed"]
    
    #os.system("cls")
    #print(json.dumps(data["specialBool"], indent=4))
    
    if onJob == True and wasOnJob == False:
        for callback in eventCallbacks["jobStarted"]:
            callback(data)
        wasOnJob = True
    elif onJob == False and wasOnJob == True:
        wasOnJob = False
        
    if refueling == True and wasRefueling == False:
        for callback in eventCallbacks["refuelStarted"]:
            callback(data)
        wasRefueling = True
    elif refueling == False and wasRefueling == True:
        wasRefueling = False
        
    if refuelPayed == True:
        for callback in eventCallbacks["refuelPayed"]:
            callback(data)
        setSpecialBool("refuelPayed", False)
        
    if finished == True:
        for callback in eventCallbacks["jobFinished"]:
            callback(data)
        setSpecialBool("jobFinished", False)
            
    if cancelled == True:
        for callback in eventCallbacks["jobCancelled"]:
            callback(data)
        setSpecialBool("jobCancelled", False)
            
    if delivered == True:
        for callback in eventCallbacks["jobDelivered"]:
            callback(data)
        setSpecialBool("jobDelivered", False)
    

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

    if CHECK_EVENTS:
        _checkEvents(data)

    return data 

def Initialize():
    global API
    global VIRTUAL_API
    API = scsTelemetry()
    VIRTUAL_API = virtualTelemetry()