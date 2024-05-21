import time
import logging
import os
import importlib
import multiprocessing
from multiprocessing.connection import Connection
import threading
from ETS2LA.utils.logging import *
import json
from types import SimpleNamespace
import sys
class PluginRunner():
    def __init__(self, pluginName, temporary, queue:multiprocessing.JoinableQueue, functionQueue:multiprocessing.JoinableQueue, returnPipe:Connection, eventQueue:multiprocessing.JoinableQueue, immediateQueue:multiprocessing.JoinableQueue):
        # Initialize the logger
        SetupProcessLogging(pluginName, filepath=os.path.join(os.getcwd(), "logs", f"{pluginName}.log"), console_level=logging.WARNING)
        logging.info(f"PluginRunner: Starting plugin {pluginName}")
        self.logger = logging.getLogger()
        # Save the values to the class
        self.q = queue
        self.fq = functionQueue
        self.frp = returnPipe
        self.eq = eventQueue
        self.iq = immediateQueue
        self.enableTime = time.time()
        self.getQueueProcessingTime = 0
        self.frametimes = []
        self.executiontimes = []
        self.temporary = temporary
        
        # Add the plugin filepath to path (so that the plugin can import modules from the plugin folder)
        sys.path.append(os.path.join(os.getcwd(), "ETS2LA", "plugins", pluginName))
        
        # Import the plugin
        self.plugin_path_name = pluginName
        plugin_path = "ETS2LA.plugins." + pluginName + ".main"
        try:
            self.plugin = importlib.import_module(plugin_path)
            logging.info(f"PluginRunner: Imported plugin {plugin_path}")
        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            logging.error(f"PluginRunner: Could not import plugin {plugin_path} with trace: n{trace}")
            logging.error(f"Could not import plugin {plugin_path}, check the logs for more information. ({e})")
            return
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
                logging.info(f"PluginRunner: Loaded module {module}")
            except Exception as e:
                logging.error(f"PluginRunner: Could not load module {module} with error: {e}")
                continue
            self.modules[moduleName] = module
            
        self.modulesDict = self.modules
        self.modules = SimpleNamespace(**self.modules) # Will convert it to a namespace to make runner.modules.ModuleName possible
        
        # Run module and plugin initializers
        for module in self.modulesDict:
            try:
                self.modulesDict[module].Initialize()
            except Exception as e:
                logging.error(f"PluginRunner: Error while running Initialize() for {module} with error {e}")
                continue
        
        try:
            if not self.temporary:
                self.plugin.Initialize()
            else:
                logging.info(f"PluginRunner: Plugin {self.plugin_name} is temporary, skipping Initialize(), please call it in the function manually if necessary.")
        except Exception as e:
            logging.error(f"PluginRunner: Error while running Initialize() for {self.plugin_name} with error {e}")
            
        
        # Run the plugin
        logging.info(f"PluginRunner: Plugin {self.plugin_name} initialized")
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
            else:
                function = data["function"]
                args = data["args"]
                kwargs = data["kwargs"]
                # Call the function by that name in the plugin
                try:
                    function = getattr(self.plugin, function)
                    data = function(*args, **kwargs)
                    logging.info(f"PluginRunner: Called function {function} in {self.plugin_name} with data {data}")
                    self.frp.send(data)
                    self.fq.task_done()
                except Exception as e:
                    logging.error(f"PluginRunner: Error while calling function {function} in {self.plugin_name}: {e}")

    def eventThread(self):
        while True:
            try:
                data = self.eq.get(timeout=0.5)
            except:
                time.sleep(0.00001)
                continue
            if type(data) == type(None):
                time.sleep(0.00001)
                continue
            if "event" in data:
                event = data["event"]
                args = data["args"]
                kwargs = data["kwargs"]
                
                if type(args) != type([]):
                    args = [args]
                if type(kwargs) != type({}):
                    kwargs = {}
                
                # Call the function by that name in the plugin
                try:
                    event = getattr(self.plugin, event)
                    event(*args, **kwargs)
                        
                except Exception as e:
                    logging.info(f"PluginRunner: Error while calling event {event} in {self.plugin_name}: {e}")

    def run(self):
        self.timer = time.time()
        threading.Thread(target=self.functionThread, daemon=True).start()
        threading.Thread(target=self.eventThread, daemon=True).start()
        while True and not self.temporary: # NOTE: This class is running in a separate process, we can thus use an infinite loop!
            startTime = time.time()
            data = self.plugin.plugin()
            pluginExec = time.time()
            if data != None:
                self.q.put(data, block=True)
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
                logging.info(f"PluginRunner: {self.plugin_path_name} is running at {round(1 / (avgFrametime if avgFrametime != 0 else 0.001),2)} FPS")
                self.timer = endTime
                self.frametimes = []
                self.executiontimes = []
                
    def GetData(self, plugins:list):
        """Get data from a list of plugins or the global shared data.

        Args:
            plugins (list): String list of plugin names to get data from.

        Returns:
            dict: data
        """
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
    
    def sonner(self, text:str, type:str="info", promise:str=""):
        """Send a notification to the frontend.

        Args:
            text (str): Text to send.
            type (str, optional): Defaults to "info". Available types are "info", "warning", "error" and "success".
        """
        self.iq.put({"sonner": {"text": text, "type": type, "promise": promise}})