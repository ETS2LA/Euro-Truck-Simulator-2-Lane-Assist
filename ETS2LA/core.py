import time
import ETS2LA.networking.webserver as webserver
import ETS2LA.networking.pluginNetworking as pluginNetworking
from ETS2LA.utils.logging import *
import multiprocessing

logger = SetupGlobalLogging()
webserver.run()

pluginNetworking.AddPluginRunner("ScreenCapture")
pluginNetworking.AddPluginRunner("ShowImage")

logging.info("ETS2LA backend has been started successfully.")
while True:
    time.sleep(1)
    fpsString = "Plugins are running at: \n"
    for frameTime in pluginNetworking.frameTimes:
        fpsString += f"{frameTime}: {1 / pluginNetworking.frameTimes[frameTime]:.2f} FPS\n"
    logging.info(fpsString)
    pass
    