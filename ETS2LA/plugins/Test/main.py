from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import time
import cv2

runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    ...

def plugin():
    runner.data = {
        "text": "This is a test sonner whose text has been sent from python."
    }
    print("Plugin waiting for data...")
    runner.WaitForFrontend()
    print("Plugin has received data.")
    print(runner.data)
    time.sleep(60)