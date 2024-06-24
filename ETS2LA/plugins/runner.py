from multiprocessing.connection import Connection
from types import SimpleNamespace
from ETS2LA.utils.logging import *
from rich.console import Console
import multiprocessing
import threading
import traceback
import importlib
import logging
import time
import json
import sys
import os
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
        self.console = Console()
        
        # Add the plugin filepath to path (so that the plugin can import modules from the plugin folder)
        sys.path.append(os.path.join(os.getcwd(), "ETS2LA", "plugins", pluginName))
        
        # Import the plugin
        self.plugin_path_name = pluginName
        plugin_path = "ETS2LA.plugins." + pluginName + ".main"
        try:
            self.plugin = importlib.import_module(plugin_path)
            logging.info(f"PluginRunner: Imported plugin {plugin_path}")
        except Exception as e:
            logging.exception(f"PluginRunner: Could not import plugin {plugin_path}")
            logging.info(traceback.format_exc())
            return
        self.plugin_data = json.loads(open(os.path.join(os.getcwd(), "ETS2LA", "plugins", pluginName, "plugin.json")).read())
        self.plugin_name = self.plugin_data["name"]
        self.plugin.runner = self
        
        # Load modules
        self.modules = {}
        self.moduleHashes = {}
        if "modules" not in self.plugin_data:
            self.plugin_data["modules"] = []
        for module in self.plugin_data["modules"]:
            module_path = "ETS2LA.modules." + module + ".main"
            # Calculate the hash of the module
            with open(os.path.join(os.getcwd(), "ETS2LA", "modules", module, "main.py"), "r") as f:
                moduleHash = hash(f.read())
            self.moduleHashes[module] = moduleHash
            moduleName = module
            try:
                module = importlib.import_module(module_path)
                module.runner = self
                logging.info(f"PluginRunner: Loaded module {module}")
            except Exception as e:
                logging.exception(f"PluginRunner: Could not load module {module}")
                logging.info(traceback.format_exc())
                continue
            self.modules[moduleName] = module
            
        self.modulesDict = self.modules
        self.modules = SimpleNamespace(**self.modules) # Will convert it to a namespace to make runner.modules.ModuleName possible
        
        # Run module and plugin initializers
        for module in self.modulesDict:
            try:
                self.modulesDict[module].Initialize()
            except Exception as e:
                logging.exception(f"PluginRunner: Error while running Initialize() for {module}")
                logging.info(traceback.format_exc())
                continue
        
        try:
            if not self.temporary:
                self.plugin.Initialize()
            else:
                logging.info(f"PluginRunner: Plugin {self.plugin_name} is temporary, skipping Initialize(), please call it in the function manually if necessary.")
        except Exception as e:
            logging.exception(f"PluginRunner: Error while running Initialize() for {self.plugin_name} with error {e}. Full traceback:")
            logging.info(traceback.format_exc())
            
        
        # Run the plugin
        logging.info(f"PluginRunner: Plugin {self.plugin_name} initialized")
        self.run()

    def moduleChangeListener(self):
        # Listen for changes, and update the modules as required
        while True:
            for module in self.moduleHashes:
                with open(os.path.join(os.getcwd(), "ETS2LA", "modules", module, "main.py"), "r") as f:
                    moduleHash = hash(f.read())
                if moduleHash != self.moduleHashes[module]:
                    logging.warning(f"PluginRunner: Module {module} has changed, reloading it.")
                    module_path = "ETS2LA.modules." + module + ".main"
                    moduleName = module
                    oldModule = self.modulesDict[moduleName]
                    try:
                        module = importlib.import_module(module_path)
                        module.runner = self
                        self.modulesDict[moduleName] = module
                        logging.info(f"PluginRunner: Loaded module {moduleName}")
                    except Exception as e:
                        logging.exception(f"PluginRunner: Could not load module {module_path} with error: {e}")
                        continue
                    
                    self.modules = SimpleNamespace(**self.modulesDict)
                    self.moduleHashes[moduleName] = moduleHash
                    try:
                        self.modulesDict[moduleName].Initialize()
                        logging.info(f"PluginRunner: Reinitialized {moduleName}")
                    except Exception as e:
                        logging.exception(f"PluginRunner: Error while running Initialize() for {module_path} with error {e}")
                        continue
                    
                    logging.warning(f"PluginRunner: Module {module_path} reloaded")
                    
                    # Reinitialize all plugins and modules to update the references
                    try:
                        for module in self.modulesDict:
                            self.modulesDict[module].Initialize()
                            logging.info(f"PluginRunner: Reinitialized {module}")
                    except Exception as e:
                        logging.exception(f"PluginRunner: Error while running Initialize() for {module} with error {e}")
                        continue
                    
                    try:
                        self.plugin.Initialize()
                        logging.info(f"PluginRunner: Reinitialized {self.plugin_name}")
                    except Exception as e:
                        logging.exception(f"PluginRunner: Error while running Initialize() for {self.plugin_name} with error {e}")
                        continue
                    
                    # Remove the old module
                    try:
                        del oldModule
                    except:
                        logging.exception(f"PluginRunner: Could not delete old module {oldModule}")
                    
            
            time.sleep(1)

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
                    logging.exception(f"PluginRunner: Error while calling function {function} in {self.plugin_name}: {e}")

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
        threading.Thread(target=self.moduleChangeListener, daemon=True).start()
        while True and not self.temporary: # NOTE: This class is running in a separate process, we can thus use an infinite loop!
            startTime = time.time()
            try:
                data = self.plugin.plugin()
            except:
                logging.exception(f"PluginRunner: Plugin {self.plugin_name} has crashed with the following error:")
                logging.info(traceback.format_exc())
                self.q.put(None)
                return 
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
                queueData = self.q.get(timeout=0.1)    
            except:
                time.sleep(0.00000001)
                data.append(None)
                count += 1
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