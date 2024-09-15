from ETS2LA.networking.cloud import SendCrashReport
from ETS2LA.plugins.runner import PluginRunner  
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.variables as variables
import numpy as np
import time
import cv2

runner:PluginRunner = None

def Initialize():
    global screen
    screen = runner.modules.ScreenCapture

def plugin():
    print("Plugin started")
    runner.terminate()
    print("Plugin stopped")