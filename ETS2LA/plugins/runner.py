import time
import logging
import os
import importlib
import multiprocessing
from ETS2LA.utils.logging import *

class PluginRunner():
    def __init__(self, pluginName, queue:multiprocessing.Queue):
        self.logger = CreateNewLogger(pluginName, filepath=os.path.join(os.getcwd(), "logs", f"{pluginName}.log"))
        self.q = queue
        self.enableTime = time.time()
        # Import the plugin
        module_name = "ETS2LA.plugins." + pluginName + ".main"
        self.plugin = importlib.import_module(module_name)
        self.plugin_name = self.plugin.PluginInfo.name
        self.logger.info(f"PluginRunner: Plugin {self.plugin_name} initialized")
        # Run the plugin
        self.run()

    def run(self):
        self.timer = time.time()
        while True:
            startTime = time.time()
            data = self.plugin.plugin(self)
            self.q.put_nowait(data)
            endTime = time.time()
            if endTime - self.timer > 1:
                self.q.put_nowait({
                    f"frametimes": {
                        f"{self.plugin_name}": endTime - startTime
                        }
                    })
                self.logger.info(f"PluginRunner: {self.plugin_name} is running at {1 / (endTime - startTime)} FPS")
                self.timer = endTime
                
    def GetData(self, plugins:list):
        amount = len(plugins)
        self.q.put({"get": plugins})
        data = []
        count = 0
        while count != amount:
            try:
                queueData = self.q.get(timeout=1)    
            except:
                time.sleep(0.00000001)
                continue
            if type(queueData) == type(None):
                data.append(None)
                count += 1
                continue
            try:
                if "get" in queueData or "frametimes" in queueData: 
                    self.q.put(queueData)
                    continue
            except:
                pass
            data.append(queueData)
            count += 1
        return data