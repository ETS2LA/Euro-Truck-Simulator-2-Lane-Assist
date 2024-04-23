from ETS2LA.plugins.plugin import PluginInformation
from ETS2LA.plugins.runner import PluginRunner
import time
PluginInfo = PluginInformation(
    name="Test",
    description="Test plugin",
    version="0.1",
    author="Test"
)

pluginRunner = None
lastTime = time.time()
def plugin(runner:PluginRunner):
    image = runner.modules.ScreenCapture.run(runner)
    runner.modules.ShowImage.run(runner, image)