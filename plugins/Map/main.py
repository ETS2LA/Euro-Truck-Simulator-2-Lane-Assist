"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="Map", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Very experimental!",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    noUI=True
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import random

from plugins.Map.GameData import roads, nodes, prefabs, prefabItems
from plugins.Map.Visualize import visualize

import cv2
from PIL import Image

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    if nodes.nodes == []:
        nodes.LoadNodes()
    if roads.roads == []:
        roads.LoadRoads()
    if prefabs.prefabs == []:
        prefabs.LoadPrefabs()
    if prefabItems.prefabItems == []:
        prefabItems.LoadPrefabItems()
    
    img = visualize.VisualizeRoads(data)
    cv2.imshow("Roads", img)
    cv2.waitKey(1)
    
    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    nodes.LoadNodes()
    roads.LoadRoads()
    prefabs.LoadPrefabs()
    prefabItems.LoadPrefabItems()
    pass

def onDisable():
    pass
