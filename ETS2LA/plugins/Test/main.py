from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import time
PluginInfo = PluginInformation(
    name="Test",
    description="Test plugin",
    version="0.1",
    author="Test"
)

def SendNotification():
    # pluginRunner.Notification("This is a test plugin!", "success")
    return "This is a test plugin call!"

pluginRunner = None
lastTime = time.time()
def plugin(runner:PluginRunner):
    global pluginRunner
    pluginRunner = runner
    time.sleep(0.1)
    return None