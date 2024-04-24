from ETS2LA.plugins.runner import PluginRunner
import time
import screeninfo
import os

runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    global API
    API = runner.modules.TruckSimAPI

def plugin():
    global API
    API.run()