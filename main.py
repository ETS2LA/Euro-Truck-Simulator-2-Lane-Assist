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
    os.remove(os.path.join(variables.PATH, "settings.json"))
except: pass

# Check if settings.json exists, if not then we can assume that this is the first time the program is running
if not os.path.exists(os.path.join(variables.PATH, "settings.json")):
    # Create that file
    with open(os.path.join(variables.PATH, "settings.json"), "w") as f:
        f.write("{\n\n}")
    

    # Then enable the first time setup
    from src.ui.firstTimeSetup import FirstTimeSetup
    loadingWindow.destroy()
    firstTimeSetup = FirstTimeSetup(mainUI.root)

    while firstTimeSetup.done == False:
        firstTimeSetup.update()

    mainUI.init()

else:
    # We've loaded all necessary modules, now we can initialize the UI
    mainUI.init()
    loadingWindow.destroy()


while True:
    mainUI.update()
    