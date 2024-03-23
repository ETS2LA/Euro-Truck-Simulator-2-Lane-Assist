import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
import rpyc
import time
import cv2
import copy
import ctypes
user32 = ctypes.windll.user32

PluginInfo = PluginInformation(
    name="ShowImage",
    description="Will show the screen capture img.",
    version="1.0",
    author="Tumppi066"
)

cv2.namedWindow("img", cv2.WINDOW_NORMAL)
cv2.resizeWindow("img", round(user32.GetSystemMetrics(0)*0.40), round(user32.GetSystemMetrics(1)*0.40))

def plugin(runner):
    try:
        startTime = time.time()
        img = runner.GetData(["ScreenCapture"]) # MSS image object
        endTime = time.time()
        # print(f"GetData(['ScreenCapture']) time: {round((endTime - startTime)*1000,1)}ms")
        img = img[0]
        if type(img) != np.ndarray:
            return
        cv2.imshow("img", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        cv2.waitKey(1)
    except:
        import traceback
        runner.logger.exception(traceback.format_exc())
        pass
