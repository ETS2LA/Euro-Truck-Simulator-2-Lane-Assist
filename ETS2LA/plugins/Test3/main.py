from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import time

PluginInfo = PluginInformation(
    name="Test3",
    description="Test plugin",
    version="0.1",
    author="Test"
)
runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    global controller
    SDK = runner.modules.SDKController
    controller = SDK.SCSController()

steering_time = time.time()
steering = "left"
def plugin():
    global steering
    global steering_time
    global controller

    if steering == "left" and time.time() - steering_time > 1:
        controller.steering = -1.0
        steering = "right"
        steering_time = time.time()
    elif steering == "right" and time.time() - steering_time > 1:
        controller.steering = 1.0
        steering = "left"
        steering_time = time.time()