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
    time.sleep(1)
    print("Horn on")
    controller.horn = True
    time.sleep(1)
    print("Horn off")
    controller.horn = False