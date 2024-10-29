from ETS2LA.modules.SDKController.main import SCSController
from ETS2LA.networking.cloud import SendCrashReport
from ETS2LA.plugins.runner import PluginRunner  
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.variables as variables
import numpy as np
import time
import cv2

runner:PluginRunner = None
controller: SCSController = None

def Initialize():
    global screen
    global controller
    controller = runner.modules.SDKController.SCSController()
    screen = runner.modules.ScreenCapture

def plugin():
    askDict = [
        {
            "name": "Test",
            "description": "I need this value innit'",
            "type": {
                "type": "number"
            }
        }
    ]
    value = runner.get_value("Test", askDict)
    print(value)
    time.sleep(30)