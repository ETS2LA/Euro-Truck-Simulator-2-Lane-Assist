from ETS2LA.plugins.runner import PluginRunner
import time
import screeninfo
import os
import math
import numpy as np
import keyboard

runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    ...

def plugin():
    runner.state = "This is doing some kind of loading... I think..."
    runner.state_progress = math.sin(time.time() * 0.5) * 0.5 + 0.5 # 0 to 1