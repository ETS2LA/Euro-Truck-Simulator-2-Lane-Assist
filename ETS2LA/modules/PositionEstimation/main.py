from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import ETS2LA.variables as variables
import numpy as np
import win32gui
import logging
import time
import math
import cv2

from ETS2LA.modules.PositionEstimation.classes import \
    HeadTranslation, Position, \
    ObjectDetection, ObjectTrack, \
    UpdateGamePosition, ConvertToAngle
    
from ETS2LA.modules.PositionEstimation.api import \
    GetHeadTranslation, GetPosition

runner:PluginRunner = None
objects: list[ObjectTrack] = []
time_to_retain_objects = 1 # second(s)

def DeleteOldObjects() -> None:
    global objects
    current_time = time.time()
    for i, obj in enumerate(objects):
        if current_time - obj.last_update_time > time_to_retain_objects:
            del objects[i]

def GetIDs() -> list[str]:
    return [obj.id for obj in objects]

def GetObjectById(id: str) -> ObjectTrack:
    for obj in objects:
        if obj.id == id:
            return obj

def Initialize():
    global API
    API = runner.modules.TruckSimAPI

def get(id: str) -> ObjectTrack | None:
    for obj in objects:
        if obj.id == id:
            return obj
    return None

def run(id: str, detection: tuple | ObjectDetection) -> ObjectTrack | None:
    try:
        if type(id) != str:
            id = str(id)
            
        data = {}
        data["api"] = API.run()
        UpdateGamePosition()
        
        # Get this frame's data
        head = GetHeadTranslation(data)
        
        if type(detection) == tuple:
            detection = ObjectDetection(detection[0], detection[1], detection[2], detection[3])
        
        head.angle = ConvertToAngle(detection.x, detection.y)[0]
        
        if id not in GetIDs():
            # Create a new object
            obj = ObjectTrack(id, detection, head)
            objects.append(obj)
        else:
            # Update the object
            obj = GetObjectById(id)
            obj.update(detection, head)
            if obj.position != None:
                print(obj.position.tuple())
            
        DeleteOldObjects()
        return obj
    except:
        logging.exception("Failed to run position estimation for object " + id)
        return None