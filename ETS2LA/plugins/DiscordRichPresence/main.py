import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.backend.variables as variables
from ETS2LA.utils.logging import *
from ETS2LA.plugins.runner import PluginRunner  

from pypresence import Presence
import time

runner:PluginRunner = None

def SendCrashReport(): # REMOVE THIS LATER
    return

def Initialize():
    global TruckSimAPI
    global rpc_update_interval
    global last_rpc_update
    global client_id
    
    # Connect to Discord application
    client_id = "1175725825493045268"
    RPC = Presence(client_id)
    RPC.connect()
    
    start = int(time.time())
    RPC.update(
        state="ETS2LA | Menu",
        large_image="la4",
        large_text="Lane Assist",
        buttons=[{"label": "ETS2LA Github", "url": "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist"}],
        start=start
    )
    logging.info("Discord Rich Presence has been started!")

    rpc_update_interval = 10
    last_rpc_update = 0

    TruckSimAPI = runner.modules.TruckSimAPI


def plugin():
    data = {}
    data["api"] = TruckSimAPI.run()


        