from ETS2LA.backend.globalServer import SendCrashReport
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.backend.variables as variables
from ETS2LA.utils.logging import *
from ETS2LA.plugins.runner import PluginRunner  

from pypresence import Presence
import time
import sys

runner:PluginRunner = None

def Initialize():
    global TruckSimAPI
    global rpc_update_interval
    global last_rpc_update
    global app_id
    global RPC
    
    # Connect to Discord application
    app_id = "1172916310519320606"
    RPC = Presence(app_id)
    RPC.connect()
    
    start = int(time.time())
    RPC.update(
        state="ETS2LA | Initializing...",
        large_image="la4",
        large_text="Lane Assist",
        buttons=[{"label": "ETS2LA Github", "url": "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist"}],
        start=start
    )
    logging.info("Discord Rich Presence has been started!")
    sys.stdout.write("Discord Rich Presence has been started!\n")

    rpc_update_interval = 10
    last_rpc_update = 0

    TruckSimAPI = runner.modules.TruckSimAPI


def plugin():
    global TruckSimAPI, rpc_update_interval, last_rpc_update, RPC

    if int(time.time()) - last_rpc_update >= rpc_update_interval:
        data = {}
        data["api"] = TruckSimAPI.run()

        connected = data["api"]["sdkActive"]
        if connected == True:
            paused = data["api"]["pause"]
            game = data["api"]["scsValues"]["game"]
            if game == "ETS2":
                small_image = "ets2"
                small_text = "Euro Truck Simulator 2"
            elif game == "ATS":
                small_image = "ats"
                small_text = "American Truck Simulator"
        else:
            paused = True
            game = "Game Disconnected"
            small_image = None
            small_text = None


        if paused == True:
            game_state = "Game Paused"
        else:
            game_state = "Game Running"
    
        if connected == False:
            RPC.update(
                details="ETS2LA | Menu",
                state="Game Disconnected",
                large_image="la4",
                large_text="Lane Assist",
                buttons=[{"label": "ETS2LA Github", "url": "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist"}]
            )
        else:
            RPC.update(
                details=f"ETS2LA | Enabled",
                state=f"{game} - {game_state}",
                large_image="la4",
                large_text="Lane Assist",
                small_image=small_image,
                small_text=small_text,
                buttons=[{"label": "ETS2LA Github", "url": "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist"}]
            )