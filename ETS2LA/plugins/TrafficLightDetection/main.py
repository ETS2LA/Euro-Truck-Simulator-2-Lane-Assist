from ETS2LA.plugins.plugin import PluginInformation
PluginInfo = PluginInformation(
    name="TrafficLightDetection",
    description="Detects traffic lights using computer vision and can display them in an output window. It communicates with the CruiseControl plugin to stop the truck at red traffic lights.",
    version="1.0",
    author="Glas42"
)

from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import time

def plugin(runner):
    time.sleep(0.1) # Cap to 10fps to limit it from running at 7mil fps
    pass