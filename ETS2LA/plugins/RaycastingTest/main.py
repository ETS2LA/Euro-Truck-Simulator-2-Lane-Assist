from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.plugins.AR.main import ScreenLine
import mouse
import time
import json
import sys
import os

runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    global raycasting
    raycasting = runner.modules.Raycasting

class Vehicle:
    raycasts: list
    screenPoints: list
    vehicleType: str
    def __init__(self, raycasts, screenPoints, vehicleType):
        self.raycasts = raycasts
        self.screenPoints = screenPoints
        self.vehicleType = vehicleType
    
    def json(self):
        return {
            "raycasts": [raycast.json() for raycast in self.raycasts],
            "screenPoints": self.screenPoints,
            "vehicleType": self.vehicleType
        }

clearLines = 50
def plugin():
    time.sleep(0.01)
    # Get mouse position
    mousePos = mouse.get_position()
    # Make two new points to the left and right of the mouse
    leftPoint = (mousePos[0] - 10, mousePos[1])
    rightPoint = (mousePos[0] + 10, mousePos[1])
    
    vehicle = Vehicle(
        [raycasting.run(leftPoint[0], leftPoint[1]), raycasting.run(leftPoint[0], leftPoint[1])], 
        [leftPoint, rightPoint], 
        "car"
    )
    
    horizonYPixel = raycasting.CURRENT_HORIZON
    
    line = ScreenLine(
        (0, horizonYPixel),
        (5120, horizonYPixel),
        (255, 255, 255)
    )
    
    mouseYLine = ScreenLine(
        (mousePos[0], 0),
        (mousePos[0], 1440),
        (255, 255, 255)
    )
    
    mouseXLine = ScreenLine(
        (0, mousePos[1]),
        (5120, mousePos[1]),
        (255, 255, 255)
    )
    
    arData = {
        "lines": [],
        "circles": [],
        "boxes": [],
        "polygons": [],
        "texts": [],
        "screenLines": [line, mouseYLine, mouseXLine],
    }
    
    return None, {
        "vehicles": [vehicle],
        "ar": arData
    }
    