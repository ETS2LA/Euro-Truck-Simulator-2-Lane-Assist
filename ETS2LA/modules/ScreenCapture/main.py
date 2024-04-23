import cv2
import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import os

PluginInfo = PluginInformation(
    name="ScreenCapture",
    description="Will capture the screen with MSS, and return the data back to the app.",
    version="1.0",
    author="Tumppi066"
)

if os.name == "nt":
    import ctypes 
    import bettercam

    user32 = ctypes.windll.user32


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

    def run(runner:PluginRunner):
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
    
else:
    import mss

    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

    def run(runner:PluginRunner):
        try:
            with mss.mss() as sct:
                img = sct.grab(monitor)
                img = np.array(img)
                return img
        except:
            import traceback
            runner.logger.exception(traceback.format_exc())
            pass