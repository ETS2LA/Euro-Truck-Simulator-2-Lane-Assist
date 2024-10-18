from ETS2LA.Module import *
from ETS2LA.modules.PositionEstimation.classes import (
    UpdateGamePosition,
    HeadTranslation,
    Position,
    ObjectDetection,
    ObjectTrack,
    ConvertToAngle
)
from ETS2LA.modules.PositionEstimation.api import GetHeadTranslation, GetPosition


class Module(ETS2LAModule):
    def imports(self):
        global settings, variables, np, logging, time, math, cv2, os
        import ETS2LA.backend.settings as settings
        import ETS2LA.variables as variables
        import numpy as np
        import logging
        import time
        import math
        import cv2
        import os

        # Conditional import for window management
        if os.name == "nt":
            global win32gui
            import win32gui
        else:
            global display, X, Xlib, XK
            from Xlib import X, display
            import Xlib.error
            import Xlib.ext
            import Xlib.XK

    objects: list[ObjectTrack]
    time_time_to_retain_objects: float
    
    def init(self):
        self.objects = []
        self.time_to_retain_objects = 1 # second(s)
        global API
        API = self.plugin.modules.TruckSimAPI
        

    def DeleteOldObjects(self) -> None:
        current_time = time.time()
        self.objects = [obj for obj in self.objects if current_time - obj.last_update_time <= self.time_to_retain_objects]


    def GetIDs(self) -> list[str]:
        return [obj.id for obj in self.objects]


    def GetObjectById(self, id: str) -> ObjectTrack:
        for obj in self.objects:
            if obj.id == id:
                return obj


    def get(self, d: str) -> ObjectTrack | None:
        for obj in self.objects:
            if obj.id == id:
                return obj
        return None


    def run(self, id: str, detection: tuple | ObjectDetection) -> ObjectTrack | None:
        try:
            if type(id) != str:
                id = str(id)

            data = {}
            data["api"] = API.run()
            UpdateGamePosition()

            head = GetHeadTranslation(data)

            if type(detection) == tuple:
                detection = ObjectDetection(detection[0], detection[1], detection[2], detection[3])

            head.angle = ConvertToAngle(detection.x, detection.y)[0]

            if id not in self.GetIDs():
                obj = ObjectTrack(id, detection, head)
                self.objects.append(obj)
            else:
                obj = self.GetObjectById(id)
                obj.update(detection, head)

            self.DeleteOldObjects()
            return obj
        except:
            logging.exception("Failed to run position estimation for object " + id)
            return None