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
    runner.state = "test"
    runner.state_progress = math.sin(time.time() * 2) * 0.5 + 0.5 # 0 to 1