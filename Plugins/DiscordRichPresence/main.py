from ETS2LA.Plugin import *
import json
import os
import time
from pypresence import Presence

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Discord Rich Presence",
        version="1.0",
        description="Displays speed and autopilot state on Discord",
        modules=["TruckSimAPI"],
        tags=["Base"],
        listen=["*.py"],
    )

    author = Author(
        name="Playzzero97",
        url="",
        icon=""
    )

    def init(self):
        global status, current_time
        current_time = time.time()
        self.cooldown_counter = 0

        print("[DiscordRichPresence] Plugin initialized")

        self.client_id = "1392138129636462642"
        self.rpc = Presence(self.client_id)
        self.rpc.connect()
        print("[DiscordRichPresence] Connected to Discord")
        

    def run(self):
        # The cooldown is in ticks
        self.cooldown_counter += 1
        if self.cooldown_counter < 50: # increase this if you think it takes performance
            return
        self.cooldown_counter = 0

        data = self.modules.TruckSimAPI.run()
        status = self.globals.tags.status
        acc = False
        map = False
        if status:
            status = self.globals.tags.merge(status)
            acc = status.get("AdaptiveCruiseControl", False)
            map = status.get("Map", False)

        speed = int(float(data["truckFloat"]["speed"]))

        # print(f"[DiscordRichPresence] Autopilot: {'Enabled' if status else 'Disabled'} | Speed: {speed} km/h")

        state = f"Autopilot: {'Enabled' if status else 'Disabled'}"
        speed = f"Speed: {speed} km/h"
        
        try:
            self.rpc.update(
                speed = speed,
                state = state,
                large_text = "ETS2LA",
                start = int(current_time)
            )
        except Exception as e:
            print(f"[DiscordRichPresence] Failed to update RPC: {e}")

