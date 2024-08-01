from ETS2LA.frontend.webpageExtras.utils import CheckIfWindowStillOpen
import ETS2LA.networking.webserver as webserver
import ETS2LA.frontend.immediate as immediate
import ETS2LA.backend.controls as controls
import ETS2LA.frontend.webpage as webpage
import ETS2LA.networking.godot as godot
import ETS2LA.networking.cloud as cloud
import ETS2LA.backend.events as events
import ETS2LA.variables as variables
from ETS2LA.utils.logging import *
import rich
import time
import os

# Initialize the backend
logger = SetupGlobalLogging()
immediate.run()  # Websockets server for immediate data
webserver.run()  # External webserver for the UI
godot.run()      # Godot server for the visualisation
webpage.run()    # Webview to the website.
events.run()     # Event handlers
controls.run()   # Control handlers

logging.info("ETS2LA backend has been started successfully.")

lastPingTime = 0
def run():
    global lastPingTime
    while True:
        time.sleep(0.01) # Relieve CPU time
        
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
            logging.info("Minimizing the window.")
            webpage.minimize_window()
            variables.MINIMIZE = False
        
        if lastPingTime + 60 < time.time():
            lastPingTime = time.time()
            try:
                cloud.Ping()
            except:
                logging.debug("Could not ping the server.")
                pass

if __name__ == "__main__":
    run()