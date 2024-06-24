import ETS2LA.backend.globalServer as globalServer
import ETS2LA.networking.webserver as webserver
import ETS2LA.frontend.immediate as immediate
import ETS2LA.backend.variables as variables
import ETS2LA.backend.controls as controls
import ETS2LA.frontend.webpage as webpage
import ETS2LA.backend.backend as backend
import ETS2LA.networking.godot as godot
import ETS2LA.backend.events as events
from ETS2LA.utils.logging import *
import time
import os

# Initialize the backend
logger = SetupGlobalLogging()
immediate.run() # Websockets server for immediate data
webserver.run() # External webserver for the UI
godot.run() # Godot server for the visualisation
webpage.run() # webview to the website.
events.run() # Event handlers
controls.run() # Control handlers

logging.info("ETS2LA backend has been started successfully.")

import ETS2LA.backend.sounds as sounds
sounds.Play("boot")

lastPingTime = 0
def run():
    global lastPingTime
    while True:
        time.sleep(0.01)
        
        for func in webserver.mainThreadQueue:
            func[0](*func[1], **func[2])
            webserver.mainThreadQueue.remove(func)
        
        if not webpage.CheckIfWindowStillOpen():
            raise Exception("exit")
        if variables.CLOSE:
            raise Exception("exit")
        if variables.RESTART:
            raise Exception("restart")
        if variables.MINIMIZE:
            webpage.minimize_window()
            variables.MINIMIZE = False
        
        if lastPingTime + 60 < time.time():
            lastPingTime = time.time()
            try:
                globalServer.Ping()
            except:
                logging.debug("Could not ping the server.")
                pass

if __name__ == "__main__":
    run()