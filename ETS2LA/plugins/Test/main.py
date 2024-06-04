from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import time
import cv2

runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    global ScreenCapture
    global ShowImage
    ScreenCapture = runner.modules.ScreenCapture
    ShowImage = runner.modules.ShowImage
    # main display = 0, x1 < x2, y1 < y2
    ScreenCapture.CreateCam(CamSetupDisplay = 0) # sets the display for both mss and bettercam and creates the cam for bettercam
    ScreenCapture.monitor_x1 = 100
    ScreenCapture.monitor_y1 = 100
    ScreenCapture.monitor_x2 = 400
    ScreenCapture.monitor_y2 = 400


def plugin():
    inputTime = time.time()
    img = ScreenCapture.run(imgtype="full")
    inputTime = time.time() - inputTime
    
    cv2.putText(img, f"Input: {inputTime*100:.2f}ms", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
    ShowImage.run(img)