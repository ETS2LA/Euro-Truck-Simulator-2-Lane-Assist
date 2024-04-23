import numpy as np
from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import cv2

PluginInfo = PluginInformation(
    name="ShowImage",
    description="Will show the screen capture img.",
    version="1.0",
    author="Tumppi066"
)

runner:PluginRunner = None

def run(img: np.ndarray = None):
    try:
        if type(img) != np.ndarray:
            return

        cv2.imshow("Lane Assist", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        cv2.waitKey(1)
    except:
        import traceback
        runner.logger.exception(traceback.format_exc())
        pass
