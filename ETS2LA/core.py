import time
import ETS2LA.networking.webserver as webserver
import ETS2LA.networking.appserver as appserver
from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.utils.logging import *
import multiprocessing

logger = SetupLogging()
webserver.run()
appserver.run()

plugin = "ScreenCapture"
# Run the plugin runner in a separate process
p = multiprocessing.Process(target=PluginRunner, args=(plugin, logger,), daemon=True)
p.start()

plugin = "ShowImage"
# Run the plugin runner in a separate process
p = multiprocessing.Process(target=PluginRunner, args=(plugin, logger,), daemon=True)
p.start()

logging.info("ETS2LA backend has been started successfully.")
while True:
    time.sleep(0.1)
    