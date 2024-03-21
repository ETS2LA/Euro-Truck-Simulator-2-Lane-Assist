import cv2
import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
import rpyc
import time
PluginInfo = PluginInformation(
    name="ShowImage",
    description="Will show the screen capture img.",
    version="1.0",
    author="Tumppi066"
)

def plugin(runner):
    img = runner.GetData("ScreenCapture")
    try:
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow("img", img)
        cv2.waitKey(1)
    except:
        pass