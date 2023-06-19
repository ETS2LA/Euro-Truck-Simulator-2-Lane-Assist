'''
The main file that runs the programs loop.
'''

# Load the UI framework
import src.mainUI as mainUI
import src.loading as loading # And then create a loading window
loadingWindow = loading.LoadingWindow("Please wait initializing...", mainUI.root)


# Load the rest of the modules
import os
import sys
import time
import json
import src.models as models # Finds all possible models
import src.variables as variables # Stores all main variables for the program
from src.logger import print

# REMOVE THIS BEFORE RELEASE
# try:
#     os.remove(os.path.join(variables.PATH, r"profiles\settings.json"))
# except: pass

# Load all plugins 
import src.settings as settings
enabledPlugins = settings.GetSettings("Plugins", "Enabled")
    
# Find plugins
path = os.path.join(variables.PATH, "plugins")
plugins = []
for file in os.listdir(path):
    if os.path.isdir(os.path.join(path, file)):
        # Check for main.py
        if "main.py" in os.listdir(os.path.join(path, file)):
            # Check for PluginInformation class
            try:
                pluginPath = "plugins." + file + ".main"
                plugin = __import__(pluginPath, fromlist=["PluginInformation"])
                if plugin.PluginInfo.type == "dynamic":
                    plugins.append(plugin.PluginInfo)
                    print("Found plugin: " + pluginPath)
            except Exception as ex:
                print(ex.args)
                pass

for plugin in plugins:
    if plugin.name not in enabledPlugins:
        plugins.remove(plugin)

pluginObjects = []
for plugin in plugins:
    pluginObjects.append(__import__("plugins." + plugin.name + ".main", fromlist=["plugin", "UI", "PluginInfo"]))

# We've loaded all necessary modules
loadingWindow.destroy()

def updatePlugins(dynamicOrder, data):
    try:
        for plugin in pluginObjects:
            if plugin.PluginInfo.dynamicOrder == dynamicOrder:
                name = plugin.PluginInfo.name
                startTime = time.time()
                data = plugin.plugin(data)
                endTime = time.time()
                data["executionTimes"][name] = endTime - startTime
        return data
    except Exception as ex:
        print("Error in plugins '" + dynamicOrder + "': " + ex.args[0])
        pass

data = {}
while True:
    # Main Application Loop
    try:
        data = {"last": data.pop("last", data), "executionTimes": {}}
        
        updatePlugins("before lane detection", data)
        # "before lane detection"
        
        updatePlugins("before steering", data)
        # "before steering"
        
        updatePlugins("before game", data)
        # "before game"
        
        updatePlugins("before UI", data)
        # "before UI"
        mainUI.update()
    
    except Exception as ex:
        print(ex.args)
        break