# Framework
from ETS2LA.Controls import ControlEvent
from ETS2LA.Events import *
from ETS2LA.Plugin import *

from ETS2LA.Utils.Values.numbers import SmoothedValue
import matplotlib
import logging
import random
import time
import sys

class Plugin(ETS2LAPlugin):
    fps_cap = 2
    
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Traffic", "TruckSimAPI"],
        listen=["*.py"],
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )

    def init(self):
        ...

    def to_gametime(self, time): # time is in minutes
        days = int(time / 1440)
        if days > 7:
            days = days % 7
            
        hours = int(time / 60)
        if hours > 23:
            hours = hours % 24
            
        minutes = int(time % 60)
        
        map_to_name = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        }
        
        return "{} {}:{}".format(
            map_to_name[days],
            str(hours).zfill(2),
            str(minutes).zfill(2)
        )

    def run(self):
        data = self.modules.TruckSimAPI.run()
        print(data["commonUI"]["timeRdbl"])