# ruff: noqa: E402
"""Welcome to the main entrypoint for ETS2LA.

- This file is responsible for starting the backend and frontend
  via all the necessary handlers and servers.

- Please note that ETS2LA V2 doesn't really have a "main loop" as
  this application is heavily multiprocessed. If you want to find
  the plugin entrypoint, then you should look at Handlers/plugins.py.

- The loop in this file is just to handle exits, updates and restarts
  from the frontend via the webserver.
"""

from ETS2LA.Utils.Console.logging import setup_global_logging, logging

setup_global_logging()  # has to be called first

# UI
import ETS2LA.Networking.Servers.notifications as notifications
import ETS2LA.Networking.Servers.webserver as webserver
import ETS2LA.Networking.Servers.discovery as discovery
import ETS2LA.Networking.Servers.pages as pages
from ETS2LA.Utils.translator import _
from ETS2LA.Window.utils import minimize_window

# Backend
import ETS2LA.Handlers.controls as controls
import ETS2LA.Handlers.plugins as plugins
import ETS2LA.Utils.listener as listener

# Utils
from ETS2LA.Utils.Console.visibility import RestoreConsole
from ETS2LA.Utils.version import check_python_version
import ETS2LA.Networking.cloud as cloud
import ETS2LA.variables as variables

# Misc
import pygame
import time


def run():
    pygame.init()

    if not check_python_version():
        raise Exception("Python version not supported. Please install 3.11 or 3.12.")

    discovery.run()  # Rebind local IP to http://ets2la.local:37520
    controls.run()  # Control handlers
    plugins.run()  # Run the plugin handler

    notifications.run()  # Websockets server for notifications
    pages.run()  # Websocket for sending page data to the frontend
    webserver.run()  # Main webserver
    # This is blocking until the window opens (or a 10s timeout)

    logging.info("[green]" + _("Backend started successfully") + "[/green]")

    frame_counter = 0
    while True:
        try:
            time.sleep(0.01)  # Relieve CPU time (100fps)

            # Execute all main thread commands from the webserver
            if webserver.mainThreadQueue:
                func = webserver.mainThreadQueue[0]
                func[0](*func[1], **func[2])
                webserver.mainThreadQueue.remove(func)
                logging.debug(f"Executed queue item: {func[0].__name__}")

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
                minimize_window()
                variables.MINIMIZE = False

            if frame_counter % 100 == 0:  # ~1 second
                frame_counter = 0
                if variables.DEVELOPMENT_MODE:
                    listener.check_for_changes()

            cloud.Ping()
            frame_counter += 1
        except KeyboardInterrupt:
            RestoreConsole()
            plugins.save_running_plugins()
            raise Exception("exit") from KeyboardInterrupt
