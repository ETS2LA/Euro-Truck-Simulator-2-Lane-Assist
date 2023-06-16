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

# REMOVE THIS BEFORE RELEASE
try:
    os.remove(os.path.join(variables.PATH, r"profiles\settings.json"))
except: pass


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
                print("Found plugin: " + pluginPath)
                plugin = __import__(pluginPath, fromlist=["PluginInformation"])
                plugins.append(plugin.PluginInfo)
            except Exception as ex:
                print(ex.args)
                pass


# We've loaded all necessary modules
loadingWindow.destroy()


while True:
    mainUI.update()
    