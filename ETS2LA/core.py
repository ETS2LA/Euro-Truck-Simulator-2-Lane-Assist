from ETS2LA.Utils.Console.logging import *
logger = SetupGlobalLogging()

from ETS2LA.Window.utils import CheckIfWindowStillOpen
import ETS2LA.Networking.Servers.webserver as webserver
import ETS2LA.Networking.Servers.notifications as notifications
from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.translator as translator
import ETS2LA.Handlers.plugins as plugins
import ETS2LA.Handlers.controls as controls
import ETS2LA.Window.window as window
import ETS2LA.Networking.Servers.godot as godot
import ETS2LA.Networking.cloud as cloud
import ETS2LA.Events.base_events as base_events
import ETS2LA.Handlers.sounds as sounds
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
plugins.run()    # Run the backend
notifications.run()  # Websockets server for immediate data
webserver.run()  # External webserver for the UI
godot.run()      # Godot server for the visualisation
window.run()    # Webview to the website.
base_events.run()     # Event handlers
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