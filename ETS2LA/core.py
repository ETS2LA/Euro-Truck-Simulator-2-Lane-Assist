import time
import ETS2LA.networking.webserver as webserver
import ETS2LA.networking.appserver as appserver
from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.utils.logging import *
import multiprocessing

SetupLogging()
webserver.run()
appserver.run()

plugin = "Test"
# Run the plugin runner in a separate process
p = multiprocessing.Process(target=PluginRunner, args=(plugin,))
p.start()

logging.info("ETS2LA backend has been started successfully.")
while True:
    time.sleep(0.1)
    