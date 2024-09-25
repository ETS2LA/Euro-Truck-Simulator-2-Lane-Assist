from multiprocessing.connection import Connection
from ETS2LA.utils.translator import Translate
from ETS2LA.utils.values import SmoothedValue
from ETS2LA.utils.time import AccurateSleep
import ETS2LA.backend.settings as settings
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
import math
import sys
import os

class PluginRunner():
    def ReloadPlugin(self):
        try:
            importlib.reload(self.plugin)
            self.plugin.runner = self
            self.plugin.Initialize()
            logging.warning(f"PluginRunner: Reloaded plugin {self.plugin_name}")
        except Exception as e:
            logging.exception(f"PluginRunner: Could not reload plugin {self.plugin_name}")
            logging.info(traceback.format_exc())
    
    def __init__(self, pluginName, temporary, queue:multiprocessing.JoinableQueue, dataQueue:multiprocessing.JoinableQueue, stateQueue:multiprocessing.JoinableQueue, functionQueue:multiprocessing.JoinableQueue, returnPipe:Connection, eventQueue:multiprocessing.JoinableQueue, immediateQueue:multiprocessing.JoinableQueue):
        SetupProcessLogging(
            pluginName, 
            filepath=os.path.join(os.getcwd(), "logs", f"{pluginName}.log"), 
            console_level=logging.WARNING
        )
        logging.info(f"PluginRunner: Starting plugin {pluginName}")
        self.logger = logging.getLogger()

        self.q = queue
        self.dq = dataQueue
        self.sq = stateQueue
        self.fq = functionQueue
        self.frp = returnPipe
        self.eq = eventQueue
        self.iq = immediateQueue
        
        self.enableTime = time.time()
        self.profilerEnabled = settings.Get(pluginName, "profiler", False)
        self.getQueueProcessingTime = 0
        self.frametimes = []
        self.executiontimes = []
        self.temporary = temporary
        self.console = Console()
        
        self.state : str  = "running"
        self.state_progress : float = -1
        
        self.data = {}
        
        # Add the plugin filepath to path (so that the plugin can import modules from the plugin folder)
        sys.path.append(os.path.join(os.getcwd(), "ETS2LA", "plugins", pluginName))
        
        self.plugin_path_name = pluginName
        plugin_path = "ETS2LA.plugins." + pluginName + ".main"
        self.plugin_hash = hash(open(os.path.join(os.getcwd(), "ETS2LA", "plugins", pluginName, "main.py")).read())
        
        try:
            self.plugin = importlib.import_module(plugin_path)
            logging.info(f"PluginRunner: Imported plugin {plugin_path}")
        except Exception as e:
            logging.exception(f"PluginRunner: {Translate('runner.could_not_import', values=[plugin_path])}")
            logging.info(traceback.format_exc())
            return
        
        self.plugin_data = json.loads(open(os.path.join(os.getcwd(), "ETS2LA", "plugins", pluginName, "plugin.json")).read())
        self.plugin_name = Translate(self.plugin_data["name"])
        self.plugin.runner = self
        
        try: self.plugin_fps_cap = self.plugin_data["max_fps"]
        except: self.plugin_fps_cap = 60
            
        logging.info(f"PluginRunner: Plugin {self.plugin_name} has FPS cap of {self.plugin_fps_cap}")
        
        # Load modules
        self.modules = {}
        self.moduleHashes = {}
        
        if "modules" not in self.plugin_data:
            self.plugin_data["modules"] = []
        
        for module in self.plugin_data["modules"]:
            module_path = "ETS2LA.modules." + module + ".main"

            with open(os.path.join(os.getcwd(), "ETS2LA", "modules", module, "main.py"), "r") as f:
                moduleHash = hash(f.read())
            
            self.moduleHashes[module] = moduleHash
            moduleName = module
            
            try:
                module = importlib.import_module(module_path)
                module.runner = self
                self.modules[moduleName] = module
                logging.info(f"PluginRunner: Loaded module {module}")
            except Exception as e:
                logging.exception(f"PluginRunner: {Translate('runner.could_not_load_module', values=[module])}")
                logging.info(traceback.format_exc())
            
        self.modulesDict = self.modules
        self.modules = SimpleNamespace(**self.modules) # Make runner.modules.moduleName
        
        for module in self.modulesDict:
            try:
                self.modulesDict[module].Initialize()
            except Exception as e:
                logging.exception(f"PluginRunner: {Translate('runner.could_not_load_module', values=[module])}")
                logging.info(traceback.format_exc())
                continue
        
        try:
            if not self.temporary:
                self.plugin.Initialize()
            else:
                logging.info(f"PluginRunner: Plugin {self.plugin_name} is temporary, skipping Initialize(), please call it in the function manually if necessary.")
        except Exception as e:
            logging.exception(f"PluginRunner: {Translate('runner.could_not_load_module', values=[self.plugin_name])}")
            logging.info(traceback.format_exc())
            
        self.frameStartTime = time.time()
        self.profilerData = {}
            
        logging.info(f"PluginRunner: Plugin {self.plugin_name} initialized")
        self.run()

    def moduleChangeListener(self):
        # Listen for changes, and update the modules as required
        while True:
            if self.temporary:
                return

            plugin_hash = hash(open(os.path.join(os.getcwd(), "ETS2LA", "plugins", self.plugin_path_name, "main.py")).read())
            if plugin_hash != self.plugin_hash:
                self.ReloadPlugin()
                self.plugin_hash = plugin_hash
            
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
                    logging.exception(f"PluginRunner: {Translate('runner.error_calling_function', values=[function, self.plugin_name])}")

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

    def stateThread(self):
        while True:
            # Send the frametimes to the main thread twice a second
            time.sleep(0.5)
            # Calculate the avg frametime
            try:
                avgFrametime = sum(self.frametimes) / len(self.frametimes)
                avgExecTime = sum(self.executiontimes) / len(self.executiontimes)
            except:
                avgFrametime = 0
                avgExecTime = 0
                
            self.sq.put({
                "frametimes": {
                    f"{self.plugin_path_name}": {
                        "frametime": avgFrametime,
                        "executiontime": avgExecTime
                    }
                },
                "state": {
                    "state": self.state,
                    "progress": self.state_progress
                },
                "data": self.data 
            })
            logging.info(f"PluginRunner: {self.plugin_path_name} is running at {round(1 / (avgFrametime if avgFrametime != 0 else 0.001),2)} FPS")
            self.timer = time.time()
            self.frametimes = []
            self.executiontimes = []
            
    def UpdateState(self):
        try:
            avgFrametime = sum(self.frametimes) / len(self.frametimes)
            avgExecTime = sum(self.executiontimes) / len(self.executiontimes)
        except:
            avgFrametime = 0
            avgExecTime = 0
            
        self.sq.put({
            "frametimes": {
                f"{self.plugin_path_name}": {
                    "frametime": avgFrametime,
                    "executiontime": avgExecTime
                }
            },
            "state": {
                "state": self.state,
                "progress": self.state_progress
            },
            "data": self.data 
        })
        logging.info(f"PluginRunner: {self.plugin_path_name} is running at {round(1 / (avgFrametime if avgFrametime != 0 else 0.001),2)} FPS")
        self.timer = time.time()
        self.frametimes = []
        self.executiontimes = []

    def Profile(self, name):
        timeSinceStart = time.time() - self.profileStartTime
        timeSinceStart *= 1000
        if name not in self.profilerData:
            self.profilerData[name] = SmoothedValue(smoothingType="time", smoothingAmount=1)
            
        self.profilerData[name](timeSinceStart)
        self.profileStartTime = time.time()
        
    def PrintProfiler(self):
        if len(self.profilerData) == 0:
            return
        
        # Move the cursor up by the amount of lines in the profiler
        print("\033[F" * (len(self.profilerData) + 2))
        
        total = sum([self.profilerData[name].get() for name in self.profilerData])
        pendingDelete = []
        for name in self.profilerData:
            value = self.profilerData[name].get()
            print(f"{name}: {round(value, 1)}ms ({round(value / total * 100, 1)}%)                                     ")
            if value == 0:
                pendingDelete.append(name)
        
        for name in pendingDelete:
            self.profilerData.pop(name)
        
        print(f"Total: {round(total, 1)}ms                               ")

    def run(self):
        self.timer = time.time()
        threading.Thread(target=self.functionThread, daemon=True).start()
        threading.Thread(target=self.eventThread, daemon=True).start()
        threading.Thread(target=self.moduleChangeListener, daemon=True).start()
        threading.Thread(target=self.stateThread, daemon=True).start()
        while True and not self.temporary: # NOTE: This class is running in a separate process, we can thus use an infinite loop!
            self.profileStartTime = time.time()
            startTime = self.profileStartTime
            try:
                data = self.plugin.plugin()
                if self.profilerEnabled:
                    self.PrintProfiler()
            except:
                logging.exception(f"PluginRunner: {Translate('runner.plugin_crash', values=[self.plugin_name])}")
                logging.info(traceback.format_exc())
                self.q.put(None)
                return
            pluginExec = time.time()
            if data != None:
                self.q.put(data, block=True)
            
            endTime = time.time()

            # Sleep to cap the FPS
            if self.plugin_fps_cap != 0 or self.plugin_fps_cap != None or self.plugin_fps_cap != -1:
                timeTaken = time.time() - startTime
                if timeTaken < 1 / self.plugin_fps_cap:
                    timeToSleepFor = 1 / self.plugin_fps_cap - timeTaken
                    AccurateSleep(timeToSleepFor)
            
            endTime = time.time()
            
            self.frametimes.append(endTime - startTime)
            self.executiontimes.append(pluginExec - startTime)
            self.executiontimes[-1] -= self.getQueueProcessingTime
            self.getQueueProcessingTime = 0
                
    def GetData(self, plugins:list):
        """Get data from a list of plugins or the global shared data.

        Args:
            plugins (list): String list of plugin names to get data from.

        Returns:
            dict: data
        """
        startTime = time.time()
        if type(plugins) != type([]):
            logging.warning(f"PluginRunner: GetData() was called with a non-list argument, this is a non issue, but consider changing it to a list like this GetData(['{plugins}'])")
            plugins = [plugins]
        amount = len(plugins)
        # Send the get command to the main thread
        self.dq.put({"get": plugins})
        data = []
        count = 0
        lastTime = time.time()
        while count != amount: # Loop until we have all the data
            if time.time() - startTime > 1:
                break
            try:
                # Wait until we get an answer.
                queueData = self.dq.get(timeout=0.25)   
            except:
                time.sleep(0.00000001)
                if time.time() - lastTime > 0.25:
                    count += 1
                    data.append(None)
                    lastTime = time.time()
                continue
            if type(queueData) == type(None):
                data.append(None)
                count += 1
                lastTime = time.time()
                continue
            try:
                # If the data we fetched was from this plugin, we can skip the loop.
                if "get" in queueData: 
                    self.dq.put(queueData)
                    if time.time() - lastTime > 0.25:
                        count += 1
                        data.append(None)
                        lastTime = time.time()
                    continue
            except:
                if time.time() - lastTime > 0.25:
                    count += 1
                    data.append(None)
                    lastTime = time.time()
            # Append the data to the list
            lastTime = time.time()
            data.append(queueData)
            count += 1
            
        self.dq.task_done()
            
        if len(data) != amount:
            for i in range(amount - len(data)):
                data.append(None)
        
        endTime = time.time()
        self.getQueueProcessingTime += endTime - startTime
        # Return all gathered data
        self.Profile(f"GetData({plugins})")
        return data
    
    def sonner(self, text:str, type:str="info", promise:str=""):
        """Send a notification to the frontend.

        Args:
            text (str): Text to send.
            type (str, optional): Defaults to "info". Available types are "info", "warning", "error" and "success".
        """
        self.iq.put({"sonner": {"text": text, "type": type, "promise": promise}})
        
    def terminate(self):
        """Disable the plugin."""
        self.iq.put({"disable": None})
        disableStartTime = time.time()
        while True:
            time.sleep(0.1) # Wait until the plugin is disabled
            if time.time() - disableStartTime > 5:
                logging.exception(f"PluginRunner: Failed to disable plugin {self.plugin_name}")
                return
        
    def ask(self, text:str, options=["Yes", "No"], timeout=600):
        """Ask the user a question.

        Args:
            text (str): Text to ask.
            options (list, optional): Defaults to ["Yes", "No"]. Options to choose from.

        Returns:
            str: Selected option.
        """
        self.iq.put({"ask": {"text": text, "options": options}})
        response = None
        startTime = time.time()
        while response == None:
            if time.time() - startTime > timeout:
                return None
            try:
                # Wait until we get an answer.
                data = self.iq.get(timeout=0.1)    
            except:
                time.sleep(0.00000001)
                continue
            try:
                # If the data we fetched was from this plugin, we can skip the loop.
                if "response" in data:
                    response = data["response"]
                    return response
            except:
                time.sleep(0.00000001)
                pass
            
    def get_value(self, title:str, jsonData:str):
        """Get a value from the frontend.

        Args:
            title (str): Title of the value.
            json (str): JSON of the value.
        """
        self.iq.put({"value": {"title": title, "json": jsonData}})
        response = None
        startTime = time.time()
        while response == None:
            if time.time() - startTime > 30:
                return None
            try:
                # Wait until we get an answer.
                data = self.iq.get(timeout=0.1)    
            except:
                time.sleep(0.00000001)
                continue
            try:
                # If the data we fetched was from this plugin, we can skip the loop.
                if "value" in data:
                    response = data["value"]
                    return response
            except:
                time.sleep(0.00000001)
                pass
            
    def ChangePage(self, page:str):
        """Change the page in the frontend.

        Args:
            page (str): Page to change to.
        """
        self.iq.put({"page": page})
            
    def WaitForFrontend(self, timeout=math.inf):
        startTime = time.time()
        
        self.sq.put({
            "data": self.data
        })
        
        while True:
            if time.time() - startTime > timeout:
                return
            try:
                # Wait until we get an answer.
                data = self.iq.get(timeout=0.1)    
            except:
                time.sleep(0.00000001)
                continue
            try:
                # If the data we fetched was from this plugin, we can skip the loop.
                if "data" in data:
                    self.data = data["data"]
                    return
            except:
                time.sleep(0.00000001)
                pass