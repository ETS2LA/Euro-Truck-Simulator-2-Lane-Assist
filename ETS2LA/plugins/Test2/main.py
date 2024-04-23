from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import time
import screeninfo
import os

PluginInfo = PluginInformation(
    name="Test2",
    description="Test plugin",
    version="0.1",
    author="Test"
)
runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    global API
    API = runner.modules.TruckSimAPI

def plugin():
    global API
    API.run()