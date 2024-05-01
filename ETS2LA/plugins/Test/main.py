from ETS2LA.plugins.runner import PluginRunner
import time
import ETS2LA.backend.settings as settings

runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    global ScreenCapture
    global ShowImage
    ScreenCapture = runner.modules.ScreenCapture
    ShowImage = runner.modules.ShowImage

    # main display = 0, x1 < x2, y1 < y2
    ScreenCapture.CreateCam(CamSetupDisplay = 1) # sets the display for both mss and bettercam and creates the cam for bettercam
    ScreenCapture.monitor_x1 = 100
    ScreenCapture.monitor_y1 = 100
    ScreenCapture.monitor_x2 = 400
    ScreenCapture.monitor_y2 = 400

def plugin():
    img = ScreenCapture.run(imgtype="cropped")
    ShowImage.run(img)