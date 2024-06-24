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
    global DS, SI, SDK
    DS = runner.modules.Steering
    SI = runner.modules.ShowImage
    SDK = runner.modules.SDKController.SCSController()
    
def ToggleSteering(state:bool, *args, **kwargs):
    print("Steering is now " + str(state))

def plugin():
    # sine wave
    #angle = DS.run(value=math.sin(time.time()))
    #print(angle, end="\r")
    # black 720p image
    #img = np.zeros((720, 1280, 3), np.uint8)
    #SI.run(img=img, windowName="Lane Assist")
    if keyboard.is_pressed("1"):
        SDK.assistact1 = True
    else:
        SDK.assistact1 = False
    if keyboard.is_pressed("2"):
        SDK.assistact2 = True
    else:
        SDK.assistact2 = False
    if keyboard.is_pressed("3"):
        SDK.assistact3 = True
    else:
        SDK.assistact3 = False
    if keyboard.is_pressed("4"):
        SDK.assistact4 = True
    else:
        SDK.assistact4 = False
    if keyboard.is_pressed("5"):
        SDK.assistact5 = True
    else:
        SDK.assistact5 = False
    if keyboard.is_pressed("6"):
        SDK.light = True
    else:
        SDK.light = False
        