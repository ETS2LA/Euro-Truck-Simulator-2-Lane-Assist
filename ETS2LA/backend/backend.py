import multiprocessing
import ETS2LA.frontend.immediate as immediate
from ETS2LA.plugins.runner import PluginRunner
import threading
import time
import pickle
import zlib
class PluginRunnerController():
    runner = None
    pluginName = None
    queue = None
    lastData = None
    def __init__(self, pluginName):
        # Initialize the plugin runner
        global runners
        runners[pluginName] = self # So that we can access this runner later from the main thread or other runners.
        self.pluginName = pluginName
        # Make the queue (comms) and start the process.
        self.queue = multiprocessing.JoinableQueue()
        self.runner = multiprocessing.Process(target=PluginRunner, args=(pluginName, self.queue, ), daemon=True)
        self.runner.start()
        self.run()
        
    def run(self):
        global frameTimes
        while True:
            try: data = self.queue.get(timeout=0.5) # Get the data returned from the plugin runner.
            except Exception as e: 
                time.sleep(0.00001)
                continue
            
            if type(data) == type(None): # If the data is None, then we just skip this iteration.
                time.sleep(0.00001)
                continue
            
            if type(data) != dict: # If the data is not a dictionary, we can assume it's return data, instead of a command.
                self.lastData = data
                continue
            
            if "frametimes" in data: # Save the frame times
                frametime = data["frametimes"]
                frameTimes[self.pluginName] = frametime[self.pluginName]
            elif "get" in data: # If the data is a get command, then we need to get the data from another plugin.
                plugins = data["get"]
                for plugin in plugins:
                    if plugin in runners:
                        self.queue.put(runners[plugin].lastData)
                    else:
                        self.queue.put(None)
            elif "sonner" in data:
                sonnerType = data["sonner"]["type"]
                sonnerText = data["sonner"]["text"]
                immediate.sonner(sonnerText, sonnerType)
            else:
                    self.lastData = data
        
        
runners = {}
frameTimes = {}

AVAILABLE_PLUGINS = []
def GetAvailablePlugins():
    global AVAILABLE_PLUGINS
    import os
    # Get list of everything in the plugins folder
    plugins = os.listdir("ETS2LA/plugins")
    # Check if it's a folder or a file.
    for plugin in plugins:
        if os.path.isdir(f"ETS2LA/plugins/{plugin}"):
            AVAILABLE_PLUGINS.append(plugin)
    # Remove the pycache folder.
    AVAILABLE_PLUGINS.pop(AVAILABLE_PLUGINS.index("__pycache__"))
    # Return
    return AVAILABLE_PLUGINS

ENABLED_PLUGINS = []
def GetEnabledPlugins():
    global ENABLED_PLUGINS
    ENABLED_PLUGINS = []
    for runner in runners:
        ENABLED_PLUGINS.append(runner)
        
    return ENABLED_PLUGINS
    

def AddPluginRunner(pluginName):
    # Run the plugin runner in a separate thread. This is done to avoid blocking the main thread.
    runner = threading.Thread(target=PluginRunnerController, args=(pluginName, ), daemon=True)
    runner.start()

def RemovePluginRunner(pluginName):
    # Stop the plugin runner
    runners[pluginName].runner.terminate()
    runners.pop(pluginName)

# These are run on startup.
GetAvailablePlugins()