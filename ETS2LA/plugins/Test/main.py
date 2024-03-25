from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import time
PluginInfo = PluginInformation(
    name="Test",
    description="Test plugin",
    version="0.1",
    author="Test"
)

lastTime = time.time()
def plugin(runner:PluginRunner):
    global lastTime
    if time.time() - lastTime > 2:
        lastTime = time.time()
        runner.Notification("This is a test plugin!", "success")
        print("Sent a sonner notification to the frontend!")