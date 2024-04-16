import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import rpyc
import time
import cv2
import copy
import ctypes

PluginInfo = PluginInformation(
    name="ShowImage",
    description="Will show the screen capture img.",
    version="1.0",
    author="Tumppi066"
)

def LoadSettings(json):
    print(json)

settings.Set("ShowImage", "enabled", True)
settings.Listen("ShowImage", LoadSettings)

cv2.namedWindow("Lane Assist", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Lane Assist", cv2.WND_PROP_TOPMOST, 1)
cv2.resizeWindow("Lane Assist", settings.Get("ScreenCapture", "width", 420), settings.Get("ScreenCapture", "height", 220))

def plugin(runner:PluginRunner):
    try:
        try:
            _, _, window_width, window_height = cv2.getWindowImageRect("Lane Assist")
        except:
            window_width = settings.Get("ScreenCapture", "width", 420)
            window_height = settings.Get("ScreenCapture", "height", 220)
            cv2.namedWindow("Lane Assist", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Lane Assist", cv2.WND_PROP_TOPMOST, 1)
            cv2.resizeWindow("Lane Assist", window_width, window_height)

        img = runner.GetData(["ScreenCapture"])
        img = img[0]
        if type(img) != np.ndarray:
            return

        cv2.imshow("Lane Assist", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        cv2.waitKey(1)
    except:
        import traceback
        runner.logger.exception(traceback.format_exc())
        pass
