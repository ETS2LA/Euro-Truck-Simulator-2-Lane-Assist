import multiprocessing
from ETS2LA.plugins.runner import PluginRunner
import threading
import time

class PluginRunnerController():
    runner = None
    pluginName = None
    queue = None
    lastData = None
    def __init__(self, pluginName):
        global runners
        runners[pluginName] = self
        self.pluginName = pluginName
        self.queue = multiprocessing.Queue()
        self.runner = multiprocessing.Process(target=PluginRunner, args=(pluginName, self.queue, ), daemon=True)
        self.runner.start()
        self.run()
        
    def run(self):
        global frameTimes
        while True:
            timeStart = time.time()
            data = self.queue.get()
            timeEnd = time.time()
            if type(data) == type(None):
                time.sleep(0.00001)
                continue
            
            if type(data) != dict:
                self.lastData = data
                continue
            
            if "frametimes" in data:
                frametime = data["frametimes"]
                frameTimes[self.pluginName] = frametime[self.pluginName]
                
            elif "get" in data:
                plugins = data["get"]
                for plugin in plugins:
                    if plugin in runners:
                        self.queue.put(runners[plugin].lastData)
                    else:
                        self.queue.put(None)
            else:
                if "get" not in data:
                    self.lastData = data
        
        
runners = {}
frameTimes = {}

def AddPluginRunner(pluginName):
    runner = threading.Thread(target=PluginRunnerController, args=(pluginName, ), daemon=True)
    runner.start()