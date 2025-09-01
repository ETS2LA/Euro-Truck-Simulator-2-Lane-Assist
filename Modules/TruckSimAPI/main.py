from Modules.TruckSimAPI.virtualAPI import scsTelemetry as virtualTelemetry
from Modules.TruckSimAPI.api import scsTelemetry
from ETS2LA.Module import ETS2LAModule


class Module(ETS2LAModule):
    def imports(self): ...

    lastX: float
    lastY: float
    isConnected: bool
    API: scsTelemetry
    VIRTUAL_API: scsTelemetry | virtualTelemetry
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
            "refuelPayed": [],
        }

    def listen(self, event, callback):
        if event in self.eventCallbacks:
            self.eventCallbacks[event].append(callback)

    def setSpecialBool(self, bool, value):
        offset = self.API.specialBoolOffsets[bool]
        try:
            self.API.setBool(offset, value)
        except Exception:
            self.VIRTUAL_API.setBool(offset, value)

    def _checkEvents(self, data):
        onJob = data["specialBool"]["onJob"]
        refueling = data["specialBool"]["refuel"]
        finished = data["specialBool"]["jobFinished"]
        cancelled = data["specialBool"]["jobCancelled"]
        delivered = data["specialBool"]["jobDelivered"]
        refuelPayed = data["specialBool"]["refuelPayed"]

        if onJob is True and self.wasOnJob is False:
            for callback in self.eventCallbacks["jobStarted"]:
                callback(data)
            self.wasOnJob = True
        elif onJob is False and self.wasOnJob is True:
            self.wasOnJob = False

        if refueling is True and self.wasRefueling is False:
            for callback in self.eventCallbacks["refuelStarted"]:
                callback(data)
            self.wasRefueling = True
        elif refueling is False and self.wasRefueling is True:
            self.wasRefueling = False

        if refuelPayed is True:
            for callback in self.eventCallbacks["refuelPayed"]:
                callback(data)
            self.setSpecialBool("refuelPayed", False)

        if finished is True:
            for callback in self.eventCallbacks["jobFinished"]:
                callback(data)
            self.setSpecialBool("jobFinished", False)

        if cancelled is True:
            for callback in self.eventCallbacks["jobCancelled"]:
                callback(data)
            self.setSpecialBool("jobCancelled", False)

        if delivered is True:
            for callback in self.eventCallbacks["jobDelivered"]:
                callback(data)
            self.setSpecialBool("jobDelivered", False)

    def run(self, Fallback=True):
        try:
            data = self.API.update(trailerData=self.TRAILER)
            if data["sdkActive"] is False:
                if Fallback is False:
                    return "not connected"
                else:
                    data = self.VIRTUAL_API.update(trailerData=self.TRAILER)
        except Exception:
            if Fallback is False:
                return "not connected"
            else:
                data = self.VIRTUAL_API.update(trailerData=self.TRAILER)

        if self.CHECK_EVENTS:
            self._checkEvents(data)

        return data
