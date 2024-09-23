import ETS2LA.memory.helper as helper
import time

class Runner:
    plugin_name = "test"
    
helper.runner = Runner()
helper.Initialize()

while True:
    data = helper.Read()
    print(data)
    if data == None:
        time.sleep(1)
        continue
    time.sleep(1)