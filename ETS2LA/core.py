from ETS2LA.Utils.Console.logging import *
logger = SetupGlobalLogging()

import ETS2LA.Networking.Servers.notifications as notifications
import ETS2LA.Networking.Servers.webserver as webserver
from ETS2LA.Window.utils import CheckIfWindowStillOpen
from ETS2LA.Utils.version import check_python_version
import ETS2LA.Events.base_events as base_events
from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.translator as translator
import ETS2LA.Handlers.controls as controls
import ETS2LA.Handlers.plugins as plugins
import ETS2LA.Handlers.sounds as sounds
import ETS2LA.Networking.cloud as cloud
import ETS2LA.Window.window as window
import ETS2LA.variables as variables
import rich
import time
import os
import sys

if not check_python_version():
    raise Exception("Python version not supported.")

# Initialize the backend
translator.CheckLanguageDatabase()          # Check if all languages have all keys
translator.UpdateFrontendTranslations()     # Update the frontend translations
plugins.run()       # Run the backend
notifications.run() # Websockets server for immediate data
webserver.run()     # External webserver for the UI
window.run()        # Webview to the website.
base_events.run()   # Event handlers
controls.run()      # Control handlers

logging.info(Translate("core.backend_started"))

lastPingTime = 0
frameCounter = 0
def run():
    global lastPingTime, frameCounter
    while True:
        time.sleep(0.01) # Relieve CPU time (100fps)
        
        for func in webserver.mainThreadQueue:
            func[0](*func[1], **func[2])
            webserver.mainThreadQueue.remove(func)
            logging.debug(f"Executed queue item: {func[0].__name__}")
        
        if not CheckIfWindowStillOpen():
            raise Exception("exit")
        
        if variables.CLOSE:
            raise Exception("exit")
        
        if variables.RESTART:
            raise Exception("restart")
        
        if variables.MINIMIZE:
            window.minimize_window()
            variables.MINIMIZE = False
        
        if frameCounter % 100 == 0: # 1 second 
            translator.CheckForLanguageUpdates()
            frameCounter = 0
        
        # if lastPingTime + 60 < time.perf_counter():
        #     lastPingTime = time.perf_counter()
        #     try:
        #         cloud.Ping()
        #     except:
        #         logging.debug("Could not ping the server.")
        #         pass
            
        frameCounter += 1

if __name__ == "__main__":
    run()