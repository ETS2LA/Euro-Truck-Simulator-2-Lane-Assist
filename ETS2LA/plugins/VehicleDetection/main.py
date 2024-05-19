import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.backend.variables as variables
from ETS2LA.plugins.runner import PluginRunner  
import cv2
import numpy as np

runner:PluginRunner = None

def SendCrashReport(): # REMOVE THIS LATER
    return

def Initialize():
    print("initializing")
    global Steering
    global ShowImage
    global TruckSimAPI
    global ScreenCapture

    Steering = runner.modules.Steering
    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    ScreenCapture = runner.modules.ScreenCapture
    ScreenCapture.CreateCam(CamSetupDisplay = 0)

    cv2.namedWindow("Vehicle Detection")
    cv2.resizeWindow("Vehicle Detection", 300, 300)
    cv2.setWindowProperty("Vehicle Detection", cv2.WND_PROP_TOPMOST, 1)

def plugin():
    print("running")
    data = {}
    data["api"] = TruckSimAPI.run()
    data["frame"] = ScreenCapture.run(imgtype="full")

    frame = data["frame"]
    if frame is None: 
        return data
    
    cv2.imshow("Vehicle Detection", frame)