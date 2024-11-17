from ETS2LA.utils.logging import *
logger = SetupGlobalLogging()

from ETS2LA.frontend.webpageExtras.utils import CheckIfWindowStillOpen
import ETS2LA.networking.webserver as webserver
import ETS2LA.frontend.immediate as immediate
from ETS2LA.utils.translator import Translate
import ETS2LA.utils.translator as translator
import ETS2LA.backend.backend as backend
import ETS2LA.backend.controls as controls
import ETS2LA.frontend.webpage as webpage
import ETS2LA.networking.godot as godot
import ETS2LA.networking.cloud as cloud
import ETS2LA.backend.events as events
import ETS2LA.backend.sounds as sounds
import ETS2LA.variables as variables
import rich
import time
import sys
import os

# Check that Python version is supported
supported_versions = [(3, 11, "x"), (3, 12, "x")]
reccomended_version = (3, 12, 7)

major, minor, micro = sys.version_info[:3]
accepted = [False] * 3 # Major, Minor, Micro
for version in supported_versions:
    if version[0] == major: accepted[0] = True # Major version accepted
    if version[1] == minor: accepted[1] = True # Minor version accepted
    if version[2] == "x" and version[1] == minor: accepted[2] = True # Any micro version of a minor version accepted
    if version[2] == micro: accepted[2] = True # Micro version accepted

if not all(accepted):
    current_version_formatted = f"{major}.{minor}.{micro}"
    recomended_version_formatted = f"{reccomended_version[0]}.{reccomended_version[1]}.{reccomended_version[2]}"
    recomended_link = f"https://www.python.org/ftp/python/{recomended_version_formatted}/python-{recomended_version_formatted}-amd64.exe"
    error = f"Your Python version is {current_version_formatted}, which is not supported by ETS2LA. Download the reccomended version ({recomended_version_formatted}) here:\n{recomended_link}"
    logging.error(error)
    raise Exception("exit")

# Initialize the backend
translator.CheckLanguageDatabase()          # Check if all languages have all keys
translator.UpdateFrontendTranslations()     # Update the frontend translations
backend.run()    # Run the backend
immediate.run()  # Websockets server for immediate data
webserver.run()  # External webserver for the UI
godot.run()      # Godot server for the visualisation
webpage.run()    # Webview to the website.
events.run()     # Event handlers
controls.run()   # Control handlers

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
            webpage.minimize_window()
            variables.MINIMIZE = False
        
        if frameCounter % 100 == 0: # 1 second 
            translator.CheckForLanguageUpdates()
            frameCounter = 0
        
        # if lastPingTime + 60 < time.time():
        #     lastPingTime = time.time()
        #     try:
        #         cloud.Ping()
        #     except:
        #         logging.debug("Could not ping the server.")
        #         pass
            
        frameCounter += 1

if __name__ == "__main__":
    run()