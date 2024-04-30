import cv2
import numpy as np
from ETS2LA.plugins.runner import PluginRunner
import os

runner:PluginRunner = None

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

    def run(imgtype:str = "both"):
        """imgtype: "both", "cropped", "full" """
        global cam
        try:
            img = cam.get_latest_frame()
            img = np.array(img)
            croppedImg = img[monitor[1]:monitor[3], monitor[0]:monitor[2]]
            if imgtype == "both":
                return croppedImg, img
            elif imgtype == "cropped":
                return croppedImg
            elif imgtype == "full":
                return img
            else:
                return croppedImg, img
        except:
            import traceback
            runner.logger.exception(traceback.format_exc())
            pass
    
else:
    import mss

    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

    def run():
        try:
            with mss.mss() as sct:
                # Capture the entire screen and then crop to the monitor size
                fullMonitor = sct.monitors[1]
                img = np.array(sct.grab(fullMonitor))
                croppedImg = img[monitor["top"]:monitor["top"]+monitor["height"], monitor["left"]:monitor["left"]+monitor["width"]]
                return croppedImg, img
        except:
            import traceback
            runner.logger.exception(traceback.format_exc())
            pass