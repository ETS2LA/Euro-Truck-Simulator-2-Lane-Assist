from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.variables as variables

import numpy as np
import cv2

runner:PluginRunner = None

def SendCrashReport(): # REMOVE THIS LATER
    return

def Initialize():
    global Steering
    global ShowImage
    global TruckSimAPI
    global ScreenCapture

    Steering = runner.modules.Steering
    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    ScreenCapture = runner.modules.ScreenCapture

    cv2.namedWindow("Vehicle Detection")
    cv2.resizeWindow("Vehicle Detection", 300, 300)
    cv2.setWindowProperty("Vehicle Detection", cv2.WND_PROP_TOPMOST, 1)

Initialize()

def plugin():
    data = {}
    data["api"] = TruckSimAPI.run()
    data["frame"] = ScreenCapture.run(imgtype="cropped")

    frame = data["frame"]
    if frame is None: 
        return data
    
    cv2.imshow("Vehicle Detection", frame)