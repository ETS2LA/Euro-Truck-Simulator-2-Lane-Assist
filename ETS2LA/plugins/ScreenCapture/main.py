import mss
import cv2
import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
PluginInfo = PluginInformation(
    name="ScreenCapture",
    description="Will capture the screen with MSS, and return the data back to the app.",
    version="1.0",
    author="Tumppi066"
)

def plugin(runner):
    # Capture a 200x200 area in the middle of the monitor
    monitor = {
        "top": 0,
        "left": 0,
        "width": 1920,
        "height": 1200,
    }
    try:
        img = mss.mss().grab(monitor)
        img = np.array(img)
        return img
    except:
        pass