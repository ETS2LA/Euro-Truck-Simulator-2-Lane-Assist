from ETS2LA.plugins.runner import PluginRunner
import time
import screeninfo
import os
import math
import numpy as np

runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    global DS, SI
    DS = runner.modules.Steering
    SI = runner.modules.ShowImage

def plugin():
    # sine wave
    angle = DS.run(value=math.sin(time.time()))
    print(angle, end="\r")
    # black 720p image
    img = np.zeros((720, 1280, 3), np.uint8)
    SI.run(img=img, windowName="Lane Assist")