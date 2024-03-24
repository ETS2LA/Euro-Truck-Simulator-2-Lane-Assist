import bettercam
import cv2
import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import ctypes 

user32 = ctypes.windll.user32

PluginInfo = PluginInformation(
    name="ScreenCapture",
    description="Will capture the screen with MSS, and return the data back to the app.",
    version="1.0",
    author="Tumppi066"
)

monitor = (0, 0, int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1)))

def CreateBettercam():
    global cam
    try:
        cam.close()
        del cam
    except: pass
    cam = bettercam.create()
    cam.start()

CreateBettercam()

def plugin(runner:PluginRunner):
    global cam
    try:
        img = cam.get_latest_frame()
        img = np.array(img)
        img = img[monitor[1]:monitor[3], monitor[0]:monitor[2]]
        return img
    except:
        import traceback
        runner.logger.exception(traceback.format_exc())
        pass
