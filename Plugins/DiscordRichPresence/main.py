from ETS2LA.Plugin import *
import json
import os
import time
import logging
from pypresence import Presence

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Discord Rich Presence",
        version="1.0",
        description="Displays speed and autopilot state on Discord",
        modules=["TruckSimAPI"],
        tags=["Base"],
        listen=["*.py"],
        fps_cap=0.067
    )

    author = Author(
        name="Playzzero97",
        url="https://github.com/Playzzero97",
        icon="https://avatars.githubusercontent.com/u/219891638?v=4"
    )

    def init(self):
        self.current_time = time.time()

        self.client_id = "1175725825493045268"
        self.rpc = Presence(self.client_id)
        self.rpc.connect()
        logging.warning("[DiscordRichPresence] Connected to Discord")
        

    def run(self):

        data = self.modules.TruckSimAPI.run()
        status = self.globals.tags.status
        acc = False
        map = False
        if status:
            status = self.globals.tags.merge(status)
            acc = status.get("AdaptiveCruiseControl", False)
            map = status.get("Map", False)

        speed = abs(data["truckFloat"]["speed"])
        unit = "m/s"
        game = data["scsValues"]["game"]
        if game == "ATS":
            speed = speed * 3.6 * 0.621371
            unit = "mph"
        else:
            speed = speed * 3.6
            unit = "km/h"

        truckspeed = f"{speed:.0f} {unit}"

        state = "Disabled"
        if map and acc:
            state = "Enabled"
        elif map:
            state = "Steering"
        elif acc:
            state = "ACC only"

        text = "Autopilot: " + state

        # print(f"[DiscordRichPresence] {text} | Speed: {truckspeed}")

        
        try:
            self.rpc.update(
                details = truckspeed,
                state = text,
                large_text = "ETS2LA",
                start = int(self.current_time)
            )
        except Exception as e:
            logging.exception(f"[DiscordRichPresence] Failed to update RPC: {e}")

