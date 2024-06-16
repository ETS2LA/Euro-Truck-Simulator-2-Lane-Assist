from ETS2LA.plugins.runner import PluginRunner
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
    time.sleep(0.1)
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
    
    return None, {
        "vehicles": [vehicle]
    }
    