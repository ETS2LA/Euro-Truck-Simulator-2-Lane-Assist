"""
Welcome to the main entrypoint for ETS2LA.

- This file is responsible for starting the backend and frontend
  via all the necessary handlers and servers.

- Please note that ETS2LA V2 doesn't really have a "main loop" as
  this application is heavily multiprocessed. If you want to find
  the plugin entrypoint, then you should look at Handlers/plugins.py.

- The loop in this file is just to handle exits, updates and restarts
  from the frontend via the webserver.
  
"""

from ETS2LA.Utils.Console.logging import *
setup_global_logging() # has to be called first

# UI
import ETS2LA.Networking.Servers.notifications as notifications
import ETS2LA.Networking.Servers.webserver as webserver
from ETS2LA.Window.utils import check_if_window_still_open
import ETS2LA.Window.window as window

# Backend
import ETS2LA.Events.base_events as base_events
import ETS2LA.Handlers.controls as controls
import ETS2LA.Handlers.plugins as plugins
import ETS2LA.Utils.listener as listener

# Utils
from ETS2LA.Utils.Console.visibility import RestoreConsole
from ETS2LA.Utils.version import check_python_version
import ETS2LA.Utils.translator as translator
import ETS2LA.Networking.cloud as cloud

# Misc
import ETS2LA.variables as variables
import pygame
import time

pygame.init()

if not check_python_version():
    raise Exception("Python version not supported. Please install 3.11 or 3.12.")


# Initialize the backend
translator.CheckLanguageDatabase()      # Check if all languages have all keys
translator.UpdateFrontendTranslations() # Update the frontend translations (if running --local)

controls.run()      # Control handlers
plugins.run()       # Run the plugin handler

notifications.run() # Websockets server for notifications
webserver.run()     # Main webserver
window.run()        # Webview window (if not --no-ui)
                    # This is blocking until the window opens (or a 10s timeout)

base_events.run()   # Start listening for events


logging.info(translator.Translate("core.backend_started"))

frame_counter = 0
def run() -> None:
    """
    Run the main ETS2LA loop. As long as this function is running
    ETS2LA will stay open.
    """
    global frame_counter
    while True:
        time.sleep(0.01) # Relieve CPU time (100fps)
        
        # Execute all main thread commands from the webserver
        for func in webserver.mainThreadQueue:
            func[0](*func[1], **func[2])
            webserver.mainThreadQueue.remove(func)
            logging.debug(f"Executed queue item: {func[0].__name__}")
        
        if not variables.NO_UI and not check_if_window_still_open():
            RestoreConsole()
            plugins.save_running_plugins()
            raise Exception("exit")
        
        if variables.CLOSE:
            RestoreConsole()
            plugins.save_running_plugins()
            raise Exception("exit")
        
        if variables.RESTART:
            RestoreConsole()
            plugins.save_running_plugins()
            raise Exception("restart")
        
        if variables.UPDATE:
            RestoreConsole()
            plugins.save_running_plugins()
            raise Exception("Update")
        
        if variables.MINIMIZE:
            window.minimize_window()
            variables.MINIMIZE = False
            
        
        if frame_counter % 100 == 0: # ~1 second 
            frame_counter = 0
            if variables.DEVELOPMENT_MODE:
                translator.CheckForLanguageUpdates()
                listener.check_for_changes()
        
        cloud.Ping()
            
        frame_counter += 1
        
if __name__ == "__main__":
    run() # Start the main loop