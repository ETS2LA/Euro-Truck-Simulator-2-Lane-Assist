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
    fps_cap = 20
    
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Traffic"],
        listen=["*.py"],
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )

    
    def init(self):
        ...

    def run(self):
        traffic = self.modules.Traffic.run()
        for vehicle in traffic:
            if not vehicle.is_trailer:
                logging.warning(f"Vehicle ID: {vehicle.id}, Position: {vehicle.position}, Speed: {vehicle.speed}")
        ...