import time
import logging
import os
import importlib
import multiprocessing

class PluginRunner():
    def __init__(self, pluginName, logger:logging.Logger, queue:multiprocessing.Queue):
        self.logger = logger
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
            ioStartTime = time.time()
            self.q.put_nowait({f"{self.plugin_name}": data})
            endTime = time.time()
            print(f"PluginRunner: {self.plugin_name} took {endTime - startTime} seconds to run, and {endTime - ioStartTime} seconds to put the data into the queue.")
            if endTime - self.timer > 1:
                self.q.put_nowait({
                    f"frametimes": {
                        f"{self.plugin_name}": 1 / (endTime - startTime)
                        }
                    })
                self.timer = endTime
                
    def GetData(self, pluginName):
        data = self.q.get(pluginName)
        if data is not None:
            return data
        else:
            return None