import bettercam
import cv2
import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
PluginInfo = PluginInformation(
    name="ScreenCapture",
    description="Will capture the screen with MSS, and return the data back to the app.",
    version="1.0",
    author="Tumppi066"
)

monitor = {
    "top": 0,
    "left": 0,
    "width": 1920,
    "height": 1200,
}

def CreateBettercam():
    global cam
    try:
        cam.close()
        del cam
    except: pass
    cam = bettercam.create()
    cam.start()

CreateBettercam()

def plugin(runner):
    global cam
    try:
        img = cam.get_latest_frame()
        img = np.array(img)
        return img
    except:
        import traceback
        runner.logger.exception(traceback.format_exc())
        pass