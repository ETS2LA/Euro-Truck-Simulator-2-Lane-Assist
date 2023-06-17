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


# We've loaded all necessary modules
loadingWindow.destroy()


while True:
    mainUI.update()
    