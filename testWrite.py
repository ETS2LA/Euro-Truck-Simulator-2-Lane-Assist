import ETS2LA.memory.helper as helper
import time

class Runner:
    plugin_name = "test"
    
helper.runner = Runner()
helper.Initialize()

while True:
    helper.Write({"test": time.time()})
    time.sleep(1)