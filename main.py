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
import src.variables as variables # Stores all main variables for the program
from src.logger import print
import traceback
import src.settings as settings
import psutil

def GetEnabledPlugins():
    global enabledPlugins
    enabledPlugins = settings.GetSettings("Plugins", "Enabled")
    if enabledPlugins == None:
        enabledPlugins = [""]



def FindPlugins():
    global plugins
    global pluginObjects
    
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
                        if plugin.PluginInfo.name in enabledPlugins:
                            plugins.append(plugin.PluginInfo)
                except Exception as ex:
                    print(ex.args)
                    pass

    pluginObjects = []
    for plugin in plugins:
        pluginObjects.append(__import__("plugins." + plugin.name + ".main", fromlist=["plugin", "UI", "PluginInfo"]))
        


def UpdatePlugins(dynamicOrder, data):
    for plugin in pluginObjects:
        try:
            if plugin.PluginInfo.dynamicOrder == dynamicOrder:
                startTime = time.time()
                data = plugin.plugin(data)
                endTime = time.time()
                data["executionTimes"][plugin.PluginInfo.name] = endTime - startTime
        except Exception as ex:
            print(ex.args)
            pass
    return data


# Load all plugins 
GetEnabledPlugins()
FindPlugins()

# We've loaded all necessary modules
loadingWindow.destroy()

data = {}
uiFrameTimer = 0
while True:
    # Main Application Loop
    try:
        
        allStart = time.time()
        
        # Remove "last" from the data and set it as this frame's "last"
        try: data = data.popitem(("last", data["last"]))
        except: pass
        data = {
            "last": data, 
            "executionTimes": {}
        }
        
        # Enable / Disable the main loop
        if variables.ENABLELOOP == False:
            mainUI.update(data)
            allEnd = time.time()
            data["executionTimes"]["all"] = allEnd - allStart
            continue
        
        if variables.UPDATEPLUGINS:
            GetEnabledPlugins()
            FindPlugins()
            variables.UPDATEPLUGINS = False
        
        UpdatePlugins("before image capture", data)
        # "before image capture"
        
        UpdatePlugins("before lane detection", data)
        # "before lane detection"
        
        UpdatePlugins("before controller", data)
        # "before steering"
        
        UpdatePlugins("before game", data)
        # "before game"
        
        UpdatePlugins("before UI", data)
        # "before UI"
        
        # Calculate the execution time of the UI
        start = time.time()
        uiFrameTimer += 1
        if uiFrameTimer > 4:
            mainUI.update(data)
            uiFrameTimer = 0
        end = time.time()
        data["executionTimes"]["UI"] = end - start
        
        UpdatePlugins("last", data)
        
        # And then the entire app
        allEnd = time.time()
        data["executionTimes"]["all"] = allEnd - allStart
    
    except Exception as ex:
        print(ex.args)
        break