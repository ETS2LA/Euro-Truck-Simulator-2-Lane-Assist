from ETS2LA.modules.TruckSimAPI.virtualAPI import scsTelemetry as virtualTelemetry
from ETS2LA.modules.TruckSimAPI.api import scsTelemetry
from ETS2LA.Module import *

class Module(ETS2LAModule):
    def imports(self):
        ...

    lastX: float
    lastY: float
    isConnected: bool
    API: scsTelemetry
    VIRTUAL_API: scsTelemetry
    TRAILER: bool
    CHECK_EVENTS: bool
    wasOnJob: bool
    wasRefueling: bool
    
    def init(self):
        self.API = scsTelemetry()
        self.VIRTUAL_API = virtualTelemetry()
        self.TRAILER = False
        self.CHECK_EVENTS = False
        self.lastX = 0
        self.lastY = 0
        self.isConnected = False

        self.wasOnJob = False
        self.wasRefueling = False

        self.eventCallbacks = {
            "jobStarted": [],
            "jobCancelled": [],
            "jobDelivered": [],
            "jobFinished": [],
            "refuelStarted": [],
            "refuelPayed": []
        }


    def listen(self, event, callback):
        if event in self.eventCallbacks:
            self.eventCallbacks[event].append(callback)
            
    def setSpecialBool(self, bool, value):
        offset = self.API.specialBoolOffsets[bool]
        try:
            self.API.setBool(offset, value)
        except:
            self.VIRTUAL_API.setBool(offset, value)
            
    def _checkEvents(self, data):
        onJob = data["specialBool"]["onJob"]
        refueling = data["specialBool"]["refuel"]
        finished = data["specialBool"]["jobFinished"]
        cancelled = data["specialBool"]["jobCancelled"]
        delivered = data["specialBool"]["jobDelivered"]
        refuelPayed = data["specialBool"]["refuelPayed"]
        
        if onJob == True and self.wasOnJob == False:
            for callback in self.eventCallbacks["jobStarted"]:
                callback(data)
            self.wasOnJob = True
        elif onJob == False and self.wasOnJob == True:
            self.wasOnJob = False
            
        if refueling == True and self.wasRefueling == False:
            for callback in self.eventCallbacks["refuelStarted"]:
                callback(data)
            self.wasRefueling = True
        elif refueling == False and self.wasRefueling == True:
            self.wasRefueling = False
            
        if refuelPayed == True:
            for callback in self.eventCallbacks["refuelPayed"]:
                callback(data)
            self.setSpecialBool("refuelPayed", False)
            
        if finished == True:
            for callback in self.eventCallbacks["jobFinished"]:
                callback(data)
            self.setSpecialBool("jobFinished", False)
                
        if cancelled == True:
            for callback in self.eventCallbacks["jobCancelled"]:
                callback(data)
            self.setSpecialBool("jobCancelled", False)
                
        if delivered == True:
            for callback in self.eventCallbacks["jobDelivered"]:
                callback(data)
            self.setSpecialBool("jobDelivered", False)
        

    def run(self, Fallback=True):
        try:
            data = self.API.update(trailerData=self.TRAILER)
            if data["sdkActive"] == False:
                if Fallback == False:
                    return "not connected"
                else:
                    data = self.VIRTUAL_API.update(trailerData=self.TRAILER)
        except:
            if Fallback == False:
                return "not connected"
            else:
                data = self.VIRTUAL_API.update(trailerData=self.TRAILER)

        if self.CHECK_EVENTS:
            self._checkEvents(data)

        return data 