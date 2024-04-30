import numpy as np
from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import cv2

runner:PluginRunner = None
overlays = {}
"""Dictionary of overlays... (name: np.ndarray)"""

LAST_WIDTH = 1280
LAST_HEIGHT = 720

def run(img: np.ndarray = None, windowName:str = "Lane Assist"):
    global LAST_WIDTH, LAST_HEIGHT
    try:
        if type(img) != np.ndarray:
            return

        LAST_WIDTH, LAST_HEIGHT = img.shape[1], img.shape[0]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Add overlays
        for overlay in overlays:
            img = cv2.addWeighted(img, 1, overlays[overlay], 1, 0)
        cv2.imshow(windowName, img)
        cv2.waitKey(1)
    except:
        import traceback
        runner.logger.exception(traceback.format_exc())
        pass
