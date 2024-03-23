import time
import ETS2LA.networking.webserver as webserver
import ETS2LA.networking.pluginNetworking as pluginNetworking
from ETS2LA.utils.logging import *

# Initialize the backend
logger = SetupGlobalLogging()
webserver.run() # External webserver for the UI

# This is how we temporarily enable plugins
pluginNetworking.AddPluginRunner("ScreenCapture")
pluginNetworking.AddPluginRunner("ShowImage")

logging.info("ETS2LA backend has been started successfully.")

while True:
    # Print the FPS values
    time.sleep(1)
    fpsString = "Plugins are running at: \n"
    for frameTime in pluginNetworking.frameTimes:
        fpsString += f"{frameTime}: {1 / pluginNetworking.frameTimes[frameTime]:.2f} FPS\n"
    logging.info(fpsString)
    pass
    