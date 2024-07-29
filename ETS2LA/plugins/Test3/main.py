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
    #runner.sonner("Hello!", "info")
    response = runner.ask("Do you like ETS2LA?", options=["Love it!", "Yes", "No"])
    print(response)
    response = runner.ask("I will install a virus on your PC. Do you agree?", options=["Yes", "Yes", "Yes", "Yes", "Yes"])
    print(response)
    time.sleep(60)