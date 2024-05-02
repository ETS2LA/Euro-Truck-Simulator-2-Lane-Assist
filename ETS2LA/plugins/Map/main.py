"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""

# TODO: We could maybe use the direction the road is moving to rotate the prefabs the correct way?
#       Right now there are problems...

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ETS2LA.variables as variables
import ETS2LA.backend.settings as settings
import os
import random
import time
import keyboard
import sys

from ETS2LA.plugins.Map.GameData import roads, nodes, prefabs, prefabItems
from ETS2LA.plugins.Map.Visualize import visualize

import cv2
from PIL import Image

from ETS2LA.plugins.runner import PluginRunner

runner:PluginRunner = None

zoom = 1
useInternalVisualization = True
useExternalVisualization = True

def Initialize():
    global API
    global SI
    API = runner.modules.TruckSimAPI
    SI = runner.modules.ShowImage

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
framesSinceChange = 0
def plugin():
    global zoom
    global framesSinceChange
    # Check if the GameData folder has it's json files
    filesInGameData = os.listdir(variables.PATH + "/ETS2LA/plugins/Map/GameData")
    hasJson = False
    for file in filesInGameData:
        if file.endswith(".json"):
            hasJson = True
            break
    
    if hasJson == False:
        messagebox.showwarning("Map", "You do not have the json data from the game.")
        return
    
    
    if nodes.nodes == []:
        runner.sonner("Loading node data... (1/4)", type="promise")
        nodes.LoadNodes()
        
        
    if roads.roads == []:
        runner.sonner("Loaded nodes, loading roads... (2/4)", type="promise", promise="Loading node data... (1/4)")
        # roads.limitToCount = 10000
        roads.LoadRoads()
        
        
    if prefabs.prefabs == []:
        runner.sonner("Loaded roads, loading prefabs... (3/4)", type="promise", promise="Loaded nodes, loading roads... (2/4)")
        #prefabs.limitToCount = 500
        prefabs.LoadPrefabs()
        
    if prefabItems.prefabItems == []:
        runner.sonner("Loaded prefabs, loading prefab items... (4/4)", type="promise", promise="Loaded roads, loading prefabs... (3/4)")
        prefabItems.LoadPrefabItems()
        runner.sonner("Loaded prefab items, starting the plugin...", "success", promise="Loaded prefabs, loading prefab items... (4/4)")
        
    
    data = {
        "api": API.run(),
    }
    
    if data["api"] == "not connected":
        return data
    
    # Increase / Decrease the zoom with e/q
    if keyboard.is_pressed("e") and framesSinceChange > 10:
        zoom -= 1
        framesSinceChange = 0
    if keyboard.is_pressed("q") and framesSinceChange > 10:
        zoom += 1
        framesSinceChange = 0
    
    
    
    if useInternalVisualization:
        img = visualize.VisualizeRoads(data, zoom=zoom)
        img = visualize.VisualizePrefabs(data, img=img, zoom=zoom)
        cv2.namedWindow("Roads", cv2.WINDOW_NORMAL)
        cv2.imshow("Roads", img)
        cv2.resizeWindow("Roads", 1000, 1000)
        cv2.waitKey(1)
    
    if useExternalVisualization:
        x = data["api"]["truckPlacement"]["coordinateX"]
        y = -data["api"]["truckPlacement"]["coordinateZ"]
        
        areaRoads = []
        areaRoads = roads.GetRoadsInTileByCoordinates(x, y)
        tileCoords = roads.GetTileCoordinates(x, y)
        
        # Also get the roads in the surrounding tiles
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y)
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y)
        areaRoads += roads.GetRoadsInTileByCoordinates(x, y + 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x, y - 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y + 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y - 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y + 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y - 1000)
        
        # Save the data for the API to send to the external visualization
        data["GPS"] = {}
        data["GPS"]["roads"] = areaRoads
        data["GPS"]["x"] = x
        data["GPS"]["y"] = y
        data["GPS"]["tileCoordsX"] = tileCoords[0]
        data["GPS"]["tileCoordsY"] = tileCoords[1]
        
    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    # nodes.LoadNodes()
    # roads.LoadRoads()
    # prefabs.LoadPrefabs()
    # prefabItems.LoadPrefabItems()
    pass

def onDisable():
    pass

class UI:
    def __init__(self, master) -> None:
        self.master = master # "master" is the mainUI window
        self.start = time.time()
        self.loadUI()
        
    def destroy(self):
        self.done = True
        self.root.destroy()
        del self
    
    def loadUI(self):
        try:
            self.root.destroy() # Load the UI each time this plugin is called
        except: pass
            
        self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
        self.root.grid_propagate(1) # Don't fit the canvast to the widgets
        self.root.pack_propagate(1)
        
        self.state = helpers.MakeLabel(self.root, "", 0,0, padx=0, pady=10, columnspan=1, sticky="n")
        self.state.set("Parsing nodes... 0%")
        
        # First progress bar for the current phase
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=1, column=0, padx=5, pady=5)
        
        self.total = helpers.MakeLabel(self.root, "", 2,0, padx=0, pady=10, columnspan=1, sticky="n")
        self.total.set("Total progress: 0%")
        
        # Second progress bar for the total progress
        self.totalProgress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.totalProgress.grid(row=3, column=0, padx=5, pady=5)
        
        helpers.MakeLabel(self.root, " ", 4,0, padx=0, pady=10, columnspan=1, sticky="n")
        helpers.MakeLabel(self.root, "SCS games are large, and by extension they have a lot of roads.\nThis process is going to take a while depending on your PC.", 5,0, padx=0, pady=10, columnspan=1, sticky="n")
        
        self.time = helpers.MakeLabel(self.root, "", 6,0, padx=0, pady=10, columnspan=1, sticky="n")
        self.remaining = helpers.MakeLabel(self.root, "", 7,0, padx=0, pady=0, columnspan=1, sticky="n")
        
        self.root.pack(anchor="center", expand=False)
        self.root.update()
    
    def update(self, data):
        try:
            stateText = data["state"]
            stateProgress = data["stateProgress"]
            totalProgress = data["totalProgress"]
            
            self.state.set(stateText)
            self.progress["value"] = stateProgress
            self.totalProgress["value"] = (totalProgress)
            self.total.set(f"Total progress: {round(totalProgress)}%")
            
            self.time.set(f"Time elapsed: {round(time.time() - self.start)} seconds")
            timeToCurrentPercentage = (time.time() - self.start)
            timeLeft = (100 - totalProgress) / totalProgress * timeToCurrentPercentage
            self.remaining.set(f"Approximate time left: {round(timeLeft)} seconds")
        except:
            pass
