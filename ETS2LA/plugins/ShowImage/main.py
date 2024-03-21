import PIL.Image as Image
import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
import rpyc
import time
import cv2
import copy
PluginInfo = PluginInformation(
    name="ShowImage",
    description="Will show the screen capture img.",
    version="1.0",
    author="Tumppi066"
)

def plugin(runner):
    img = runner.GetData("ScreenCapture") # MSS image object
    img = copy.deepcopy(img) # This is what makes it really slow...
    try:
        cv2.imshow("img", np.array(img))
        cv2.waitKey(1)
    except:
        #import traceback
        #traceback.print_exc()
        pass