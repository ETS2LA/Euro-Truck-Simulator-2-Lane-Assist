import time
import ETS2LA.networking.webserver as webserver
from ETS2LA.utils.logging import *

SetupLogging()
webserver.run()



logging.info("ETS2LA backend has been started successfully.")
while True:
    time.sleep(0.1)
    