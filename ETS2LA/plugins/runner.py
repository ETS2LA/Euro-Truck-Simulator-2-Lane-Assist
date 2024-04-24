import time
import logging
import os
import importlib
import multiprocessing
import threading
from ETS2LA.utils.logging import *
import json
from types import SimpleNamespace
class PluginRunner():
    def __init__(self, pluginName, queue:multiprocessing.Queue, functionQueue:multiprocessing.Queue):
        # Initialize the logger
        self.logger = CreateNewLogger(pluginName, filepath=os.path.join(os.getcwd(), "logs", f"{pluginName}.log"))
        
        # Save the values to the class
        self.q = queue
        self.fq = functionQueue
        self.enableTime = time.time()
        self.getQueueProcessingTime = 0
        self.frametimes = []
        self.executiontimes = []
        
        # Import the plugin
        self.plugin_path_name = pluginName
        plugin_path = "ETS2LA.plugins." + pluginName + ".main"
        self.plugin = importlib.import_module(plugin_path)
        self.plugin_data = json.loads(open(os.path.join(os.getcwd(), "ETS2LA", "plugins", pluginName, "plugin.json")).read())
        self.plugin_name = self.plugin_data["name"]
        self.plugin.runner = self
        
        # Load modules
        self.modules = {}
        if "modules" not in self.plugin_data:
            self.plugin_data["modules"] = []
        for module in self.plugin_data["modules"]:
            module_path = "ETS2LA.modules." + module + ".main"
            moduleName = module
            try:
                module = importlib.import_module(module_path)
                module.runner = self
                self.logger.info(f"PluginRunner: Loaded module {module}")
            except Exception as e:
                self.logger.error(f"PluginRunner: Could not load module {module} with error: {e}")
                continue
            self.modules[moduleName] = module
            
        # Run module and plugin initializers
        for module in self.modules:
            try:
                self.modules[module].Initialize()
            except Exception as e:
                self.logger.error(f"PluginRunner: Error while running Initialize() for {module} with error {e}")
                continue
        
        self.modulesDict = self.modules
        self.modules = SimpleNamespace(**self.modules) # Will convert it to a namespace to make runner.modules.ModuleName possible
        
        try:
            self.plugin.Initialize()
        except Exception as e:
            self.logger.error(f"PluginRunner: Error while running Initialize() for {self.plugin_name} with error {e}")
            
        
        # Run the plugin
        self.logger.info(f"PluginRunner: Plugin {self.plugin_name} initialized")
        self.run()

    def functionThread(self):
        while True:
            try:
                data = self.fq.get(timeout=0.5)
            except:
                time.sleep(0.00001)
                continue
            if type(data) == type(None):
                time.sleep(0.00001)
                continue
            if "function" in data:
                function = data["function"]
                args = data["args"]
                kwargs = data["kwargs"]
                # Call the function by that name in the plugin
                try:
                    function = getattr(self.plugin, function)
                    data = function(*args, **kwargs)
                    if type(data) != type(None):
                        self.fq.put(data)
                        
                except Exception as e:
                    self.logger.error(f"PluginRunner: Error while calling function {function} in {self.plugin_name}: {e}")

    def run(self):
        self.timer = time.time()
        threading.Thread(target=self.functionThread, daemon=True).start()
        while True: # NOTE: This class is running in a separate process, we can thus use an infinite loop!
            startTime = time.time()
            data = self.plugin.plugin()
            pluginExec = time.time()
            if type(data) != type(None):
                self.q.put(data)
            endTime = time.time()
            self.frametimes.append(endTime - startTime)
            self.executiontimes.append(pluginExec - startTime)
            self.executiontimes[-1] -= self.getQueueProcessingTime
            self.getQueueProcessingTime = 0
            # Send the frametimes to the main thread once a second
            if endTime - self.timer > 0.5:
                # Calculate the avg frametime
                avgFrametime = sum(self.frametimes) / len(self.frametimes)
                avgExecTime = sum(self.executiontimes) / len(self.executiontimes)
                self.q.put({
                    f"frametimes": {
                        f"{self.plugin_path_name}": {
                            "frametime": avgFrametime,
                            "executiontime": avgExecTime
                        }
                        }
                    })
                self.logger.info(f"PluginRunner: {self.plugin_path_name} is running at {round(1 / (avgFrametime),2)} FPS")
                self.timer = endTime
                self.frametimes = []
                self.executiontimes = []
                
    def GetData(self, plugins:list):
        startTime = time.time()
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
            
        endTime = time.time()
        self.getQueueProcessingTime += endTime - startTime
        # Return all gathered data
        return data
    
    def Notification(self, text:str, type:str="info"):
        """Send a notification to the frontend.

        Args:
            text (str): Text to send.
            type (str, optional): Defaults to "info". Available types are "info", "warning", "error" and "success".
        """
        self.q.put({"sonner": {"text": text, "type": type}})