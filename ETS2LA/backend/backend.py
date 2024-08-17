from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.frontend.immediate as immediate
import ETS2LA.utils.git as git
import multiprocessing.connection
import multiprocessing
import threading
import requests
import logging
import psutil
import time
import json
import sys
import os

commits_save = []

class PluginRunnerController():
    def __init__(self, pluginName, temporary=False):
        global runners
        runners[pluginName] = self
        self.pluginName = pluginName
        
        # Make the queue (comms) and start the process.
        self.queue = multiprocessing.JoinableQueue()
        self.stateQueue = multiprocessing.JoinableQueue()
        self.functionQueue = multiprocessing.JoinableQueue()
        self.eventQueue = multiprocessing.JoinableQueue()
        self.immediateQueue = multiprocessing.JoinableQueue()
        self.returnPipe, pluginReturnPipe = multiprocessing.Pipe()
        
        self.runner = multiprocessing.Process(target=PluginRunner, args=(pluginName, temporary, self.queue, self.stateQueue, self.functionQueue, pluginReturnPipe, self.eventQueue, self.immediateQueue, ), daemon=True)
        self.runner.start()
        
        self.state = "running"
        self.state_progress = -1 # no progress bar
        
        self.data = {}
        
        self.process = self.runner.pid
        self.process_info = []
        
        self.lastData = "Plugin has not returned any data yet."
        
        self.run()
    
    def immediateQueueThread(self):
        while True:
            try: 
                data = self.immediateQueue.get(timeout=0.5)
            except Exception as e: 
                time.sleep(0.00001)
                continue
            
            if type(data) == type(None):
                time.sleep(0.00001)
                continue
        
            if "data" in data: # We caught a relieve message from the frontend.
                self.immediateQueue.put(data)
                time.sleep(0.2)
        
            if "sonner" in data:
                sonnerType = data["sonner"]["type"]
                sonnerText = data["sonner"]["text"]
                sonnerPromise = data["sonner"]["promise"]
                immediate.sonner(sonnerText, sonnerType, sonnerPromise)
                
            if "page" in data:  
                page = data["page"]
                immediate.page(page)
                
            if "ask" in data:
                askText = data["ask"]["text"]
                askOptions = data["ask"]["options"]
                response = immediate.ask(askText, askOptions)
                self.immediateQueue.put(response)
                
        
    def monitor(self):
        process = psutil.Process(self.process)
        # Get the plugin folder size
        try:
            size = 0
            for root, dirs, files in os.walk(f"ETS2LA/plugins/{self.pluginName}"):
                try:
                    size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
                    size += sum([os.path.getsize(os.path.join(root, name)) for name in dirs])
                except:
                    pass 
            logging.debug(f"Plugin {self.pluginName} has a disk usage of {size} bytes.")
        except:
            size = 0
            
        while True:
            try:
                data = {
                    "cpu": 0,
                    "mem": 0,
                    "disk": size
                }
                data["cpu"] = process.cpu_percent(interval=0.5) / psutil.cpu_count()
                data["mem"] = process.memory_percent()
                self.process_info.append(data)
                if len(self.process_info) > 240: # 2 minutes of 0.5s intervals
                    self.process_info.pop(0)
            except:
                time.sleep(0.5)
                continue
        
    def stateQueueThread(self):
        while True:
            try: 
                data = self.stateQueue.get(timeout=0.5)
            except Exception as e: 
                time.sleep(0.00001)
                continue
            
            if type(data) == type(None):
                time.sleep(0.00001)
                continue
        
            try:
                if "frametimes" in data:
                    frametime = data["frametimes"]
                    if self.pluginName not in frameTimes:
                        frameTimes[self.pluginName] = []
                    frameTimes[self.pluginName].append(frametime[self.pluginName])
                    if len(frameTimes[self.pluginName]) > 240: # 120 seconds of 0.5 intervals
                        frameTimes[self.pluginName].pop(0)
            except: pass
            
            try:
                if "state" in data:
                    state = data["state"]
                    self.state = state["state"]
                    self.state_progress = state["progress"]
            except: pass
            
            try:
                if "data" in data:
                    self.data = data["data"]
            except: pass
                
        
    def start_other_threads(self):
        threading.Thread(target=self.immediateQueueThread, daemon=True).start()
        threading.Thread(target=self.monitor, daemon=True).start()
        threading.Thread(target=self.stateQueueThread, daemon=True).start()
        
    def run(self):
        global frameTimes
        global globalData
        
        self.start_other_threads()
        
        while True:
            try: 
                data = self.queue.get() # Get the data returned from the plugin runner.
            except Exception as e: 
                time.sleep(0.00001)
                continue
            
            if type(data) == type(None): # If the data is None, then we just skip this iteration.
                time.sleep(0.00001)
                continue
            
            if type(data) == dict:
                if "function" in data:
                    # Send the data back to wait for the answer.
                    self.queue.put(self.lastData)
                    time.sleep(0.01)
                    continue
                        
                if "get" in data: # If the data is a get command, then we need to get the data from another plugin.
                    plugins = data["get"]
                    for plugin in plugins:
                        if "tags." in plugin:
                            tag = plugin.split("tags.")[1]
                            try:
                                self.queue.put(globalData[tag])
                            except:
                                self.queue.put(None)
                        
                        if plugin in runners:
                            try:
                                self.queue.put(runners[plugin].lastData)
                            except:
                                logging.debug(f"Plugin ({self.pluginName}) is trying to get data from another plugin ({plugin}) that has not been initialized yet.")
                                self.queue.put(None)
                        else:
                            self.queue.put(None)
                else:
                    self.lastData = data
                        
            else: # If the data is not a dictionary, we can assume it's return data instead of a command.
                if type(data) == tuple:
                    normData = data[0]
                    tags = data[1]
                    self.lastData = normData
                    globalData.update(tags) # TODO: This is a temporary solution. We need to find a better way to handle this.
                else:
                    self.lastData = data        
        
runners = {}
frameTimes = {}
globalData = {}

AVAILABLE_PLUGINS = {}
def GetAvailablePlugins():
    global AVAILABLE_PLUGINS
    
    plugins = os.listdir("ETS2LA/plugins")
    for plugin in plugins:
        if os.path.isdir(f"ETS2LA/plugins/{plugin}"):
            AVAILABLE_PLUGINS[plugin] = {}

    AVAILABLE_PLUGINS.pop("__pycache__")

    for plugin in AVAILABLE_PLUGINS:
        try:
            with open(f"ETS2LA/plugins/{plugin}/plugin.json", "r") as f:
                AVAILABLE_PLUGINS[plugin]["file"] = json.loads(f.read())
        except:
            AVAILABLE_PLUGINS[plugin]["file"] = {
                "name": plugin,
                "authors": "Unknown",
                "version": "Unknown",
                "description": "No description provided.",
                "image": "None",
                "dependencies": "None"
            }

    AVAILABLE_PLUGINS["Global"] = {
        "file": json.loads(open("ETS2LA/global_settings.json", "r").read())
    }

    return AVAILABLE_PLUGINS

ENABLED_PLUGINS = []
def GetEnabledPlugins():
    global ENABLED_PLUGINS
    ENABLED_PLUGINS = []
    for runner in runners:
        ENABLED_PLUGINS.append(runner)
        
    return ENABLED_PLUGINS

def GetPluginStates():
    states = {}
    for runner in runners:
        try:
            states[runner] = {}
            states[runner]["state"] = runners[runner].state
            states[runner]["progress"] = runners[runner].state_progress
            states[runner]["data"] = runners[runner].data
        except:
            continue
        
    return states
    
def RelieveWaitForFrontend(plugin, data):
    runners[plugin].immediateQueue.put({"data": data})
    return True
    
# TODO: Fix this code, it's not working most of the time!
def CallPluginFunction(plugin, function, args, kwargs):
    if "timeout" in kwargs:
        timeout = kwargs["timeout"]
        kwargs.pop("timeout")
    else:
        timeout = 5
        
    def WaitQueue():
        runners[plugin].functionQueue.join()
        
    try:
        if plugin in runners:
            try:
                runners[plugin].functionQueue.put({"function": function, "args": args, "kwargs": kwargs})
            except:
                logging.error(f"Failed to call function {function} on plugin {plugin}. Most likely you are calling the function too fast, and the previous plugin instance has not been removed yet.")
                return False
            
            # Create a separate thread to call join()
            t = threading.Thread(target=WaitQueue, daemon=True)
            t.start()
            t.join(timeout=timeout)  
            
            # Check if the thread is still alive (i.e., if the join() method timed out)
            if t.is_alive():
                logging.info(f"Plugin {plugin} function call took too long to respond.")
                del t # Delete the thread
                return False
            
            try:
                if runners[plugin].returnPipe.poll(timeout=5):
                        data = runners[plugin].returnPipe.recv()
                else:
                    logging.info(f"Plugin {plugin} function call completed with no data.")
                    data = True
                return data
            except:
                logging.error(f"Failed to receive data from plugin {plugin}. Most likely you are calling the function too fast, and the previous plugin instance has not been removed yet.")
                return False
        else:
            logging.info(f"Plugin {plugin} is not enabled. Enabling temporarily to run the function.")
            AddPluginRunner(plugin, temporary=True) # Add a temp runner to load the code
            startTime = time.time()
            while True:
                try:
                    runners[plugin].functionQueue.put({"function": function, "args": args, "kwargs": kwargs})
                    break
                except:
                    if startTime - time.time() > timeout:
                        RemovePluginRunner(plugin)
                        logging.info(f"> Failed to start")
                        return False
                    
            # Create a separate thread to call join()
            t = threading.Thread(target=WaitQueue, daemon=True)
            t.start()
            t.join(timeout=timeout)  
            
            # Check if the thread is still alive (i.e., if the join() method timed out)
            if t.is_alive():
                RemovePluginRunner(plugin)
                logging.info(f"> Timeout")
                del t # Delete the thread
                return False
            
            if runners[plugin].returnPipe.poll(timeout=5):
                data = runners[plugin].returnPipe.recv()
            else:
                logging.info(f"> Success, but no data")
                data = True
            try:
                RemovePluginRunner(plugin)
            except:
                logging.warning(f"Failed to remove temporary plugin {plugin}. This might not be an issue.")
            logging.info(f"> Success")
            return data
    except:
        import traceback
        traceback.print_exc()
        RemovePluginRunner(plugin)
        return False
    
def CallEvent(event, args, kwargs):
    for runner in runners:
        try:
            runners[runner].eventQueue.put({"event": event, "args": args, "kwargs": kwargs})
        except:
            logging.exception(f"Failed to call event {event} on plugin {runner}.")
            pass

def AddPluginRunner(pluginName, temporary=False):
    if pluginName in runners: return
    # Run the plugin runner in a separate thread. This is done to avoid blocking the main thread.
    runner = threading.Thread(target=PluginRunnerController, args=(pluginName, temporary, ), daemon=True)
    runner.start()

def RemovePluginRunner(pluginName):
    if not pluginName in runners: return
    runners[pluginName].runner.terminate()
    runners.pop(pluginName)

def GetPerformance():
    try:
        array = []
        for runner in runners:
            try:
                runnerData = {
                    "name": runner,
                    "data": []
                }
                count = 0
                for data in runners[runner].process_info:
                    try:
                        currentProcessData = {
                            "name": runners[runner].pluginName,
                            "data": data
                        }
                        currentProcessData["data"]["frametime"] = frameTimes[runners[runner].pluginName][count]["frametime"] # + frameTimes[runners[runner].pluginName][count]["executiontime"]
                        runnerData["data"].append(currentProcessData)
                        count += 1
                    except:
                        count += 1
                        pass
                array.append(runnerData)
            except:
                pass
        return array
    except:
        return []

# These are run on startup.
GetAvailablePlugins()