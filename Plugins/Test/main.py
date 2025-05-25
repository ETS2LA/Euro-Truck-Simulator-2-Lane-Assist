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

    def run(self):
        self.notify("Test notification", "info")
        time.sleep(5)