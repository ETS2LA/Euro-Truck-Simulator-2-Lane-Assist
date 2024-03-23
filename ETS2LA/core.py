import time
import ETS2LA.networking.webserver as webserver
import ETS2LA.networking.appserver as appserver
from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.utils.logging import *
import multiprocessing

logger = SetupLogging()
webserver.run()
appserver.run()

queue = multiprocessing.Queue()

plugin = "ScreenCapture"
# Run the plugin runner in a separate process
p = multiprocessing.Process(target=PluginRunner, args=(plugin, logger, queue, ), daemon=True)
p.start()

#plugin = "ShowImage"
# Run the plugin runner in a separate process
#p = multiprocessing.Process(target=PluginRunner, args=(plugin, logger, queue, ), daemon=True)
#p.start()

logging.info("ETS2LA backend has been started successfully.")
while True:
    data = queue.get()
    if "frametimes" in data:
        logging.info(data["frametimes"])
    else:
        import cv2
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("image", 1280, 720)
        cv2.imshow("image", data["ScreenCapture"])
        cv2.waitKey(1)
    