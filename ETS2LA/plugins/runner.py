import time
import logging
import os
import importlib
import multiprocessing
from ETS2LA.utils.logging import *

class PluginRunner():
    def __init__(self, pluginName, queue:multiprocessing.Queue):
        # Initialize the logger
        self.logger = CreateNewLogger(pluginName, filepath=os.path.join(os.getcwd(), "logs", f"{pluginName}.log"))
        # Save the values to the class
        self.q = queue
        self.enableTime = time.time()
        self.frametimes = []
        # Import the plugin
        module_name = "ETS2LA.plugins." + pluginName + ".main"
        self.plugin = importlib.import_module(module_name)
        self.plugin_name = self.plugin.PluginInfo.name
        self.logger.info(f"PluginRunner: Plugin {self.plugin_name} initialized")
        # Run the plugin
        self.run()

    def run(self):
        self.timer = time.time()
        while True: # NOTE: This class is running in a seperate process, we can thus use an infinite loop!
            startTime = time.time()
            data = self.plugin.plugin(self)
            self.q.put_nowait(data)
            endTime = time.time()
            self.frametimes.append(endTime - startTime)
            # Send the frametimes to the main thread once a second
            if endTime - self.timer > 1:
                # Calculate the avg frametime
                avgFrametime = sum(self.frametimes) / len(self.frametimes)
                self.q.put_nowait({
                    f"frametimes": {
                        f"{self.plugin_name}": avgFrametime
                        }
                    })
                self.logger.info(f"PluginRunner: {self.plugin_name} is running at {round(1 / (avgFrametime),2)} FPS")
                self.timer = endTime
                self.frametimes = []
                
    def GetData(self, plugins:list):
        amount = len(plugins)
        # Send the get command to the main thread
        self.q.put({"get": plugins})
        data = []
        count = 0
        while count != amount: # Loop until we have all the data
            try:
                # Wait until we get an answer.
                queueData = self.q.get(timeout=1)    
            except:
                time.sleep(0.00000001)
                continue
            if type(queueData) == type(None):
                data.append(None)
                count += 1
                continue
            try:
                # If the data we fetched was from this plugin, we can skip the loop.
                if "get" in queueData or "frametimes" in queueData: 
                    self.q.put(queueData)
                    continue
            except:
                pass
            # Append the data to the list
            data.append(queueData)
            count += 1
            
        # Return all gathered data
        return data