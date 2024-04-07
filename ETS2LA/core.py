import time
import os
import ETS2LA.networking.webserver as webserver
import ETS2LA.backend.backend as backend
import ETS2LA.frontend.immediate as immediate
from ETS2LA.utils.logging import *
import ETS2LA.frontend.webpage as webpage
import ETS2LA.variables as variables

# Initialize the backend
logger = SetupGlobalLogging()
immediate.run() # Websockets server for immediate data
webserver.run() # External webserver for the UI
webpage.run() # Tkinter webview to the website.
logging.info("Available CPU cores: " + str(os.cpu_count()))


logging.info("ETS2LA backend has been started successfully.")
def run():
    while True:
        time.sleep(1)
        if not webpage.CheckIfWindowStillOpen():
            raise Exception("exit")
        if variables.CLOSE:
            raise Exception("exit")
        if variables.RESTART:
            raise Exception("restart")
