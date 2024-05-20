"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


import logging
print = logging.info

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ETS2LA.backend.variables as variables
import ETS2LA.backend.settings as settings
import os
import random
import time
import keyboard
import mouse
from typing import List
from GameData import roads, nodes, prefabs, prefabItems
import Compute.compute as compute
from Visualize import visualize
from ETS2LA.plugins.runner import PluginRunner
import sys

import cv2
from PIL import Image

USE_INTERNAL_VISUALIZATION = True
USE_EXTERNAL_VISUALIZATION = True
EXTERNAL_RENDER_DISTANCE = 200 # How far to render in meters

try:
    from ETS2LA.plugins.AR.main import Line, Circle, Box, Polygon
except:
    USE_EXTERNAL_VISUALIZATION = False # Force external off

ZOOM = 2 # How many pixels per meter
VISUALIZE_PREFABS = True

LOAD_NODES_MSG = "Loading nodes... (1/4)"
LOAD_ROADS_MSG = "Loading roads... (2/4)"
LOAD_PREFABS_MSG = "Loading prefabs... (3/4)"
LOAD_PREFAB_ITEMS_MSG = "Loading prefab items... (4/4)"

runner:PluginRunner = None

def Initialize():
    global API
    global SI
    global toast
    API = runner.modules.TruckSimAPI
    SI = runner.modules.ShowImage
    toast = runner.sonner
    pass

def GetDistanceFromTruck(x, z, data):
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    
    return ((truckX - x) ** 2 + (truckZ - z) ** 2) ** 0.5

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
framesSinceChange = 0
def plugin():
    global framesSinceChange
    global ZOOM
    
    data = {
        "api": API.run(),
    }
    
    # Bind the mouse scroll wheel to zoom
    if mouse.is_pressed("scroll_up"):
        ZOOM += 1
        print(f"ZOOM: {ZOOM}")
        time.sleep(0.2)
    if mouse.is_pressed("scroll_down"):
        ZOOM -= 1
        print(f"ZOOM: {ZOOM}")
        time.sleep(0.2)
    # Also ctrl + up and down
    if keyboard.is_pressed("ctrl") and keyboard.is_pressed("up"):
        ZOOM += 1
        print(f"ZOOM: {ZOOM}")
        time.sleep(0.2)
    if keyboard.is_pressed("ctrl") and keyboard.is_pressed("down"):
        ZOOM -= 1
        print(f"ZOOM: {ZOOM}")
        time.sleep(0.2)
    
    if ZOOM < 1:
        ZOOM = 1
        
        
    # Check if the GameData folder has it's json files
    filesInGameData = os.listdir(variables.PATH + "ETS2LA/plugins/Map/GameData")
    hasJson = False
    for file in filesInGameData:
        if file.endswith(".json"):
            hasJson = True
            break
    
    if hasJson == False:
        messagebox.showwarning("Map", "You do not have the json data from the game. The map plugin will disable.")
        settings.RemoveFromList("Plugins", "Enabled", "Map")
        variables.UpdatePlugins()
        return data
    
    startPlugin = ""
    if nodes.nodes == []:
        toast(LOAD_NODES_MSG, type="promise")
        nodes.LoadNodes()
        
    if roads.roads == []:
        toast(LOAD_ROADS_MSG, type="promise", promise=LOAD_NODES_MSG)
        roads.limitToCount = 10000
        roads.LoadRoads()
    if prefabs.prefabs == [] and VISUALIZE_PREFABS:
        toast(LOAD_PREFABS_MSG, type="promise", promise=LOAD_ROADS_MSG)
        prefabs.limitToCount = 500
        prefabs.LoadPrefabs() 
    if prefabItems.prefabItems == [] and VISUALIZE_PREFABS:
        toast(LOAD_PREFAB_ITEMS_MSG, type="promise", promise=LOAD_PREFABS_MSG)
        prefabItems.LoadPrefabItems()
        toast("Loading complete!", type="success", promise=LOAD_PREFAB_ITEMS_MSG)
    
    
    visRoads = compute.GetRoads(data)
    compute.CalculateParallelPointsForRoads(visRoads) # Will slowly populate the lanes over a few frames
    visPrefabs = compute.GetPrefabs(data)
    if USE_INTERNAL_VISUALIZATION:
        img = visualize.VisualizeRoads(data, visRoads, zoom=ZOOM)
        if VISUALIZE_PREFABS:
            img = visualize.VisualizePrefabs(data, visPrefabs, img=img, zoom=ZOOM)
            
        img = visualize.VisualizeTruck(data, img=img, zoom=ZOOM)

        img = visualize.VisualizeTrafficLights(data, img=img, zoom=ZOOM)
        
        cv2.namedWindow("Roads", cv2.WINDOW_NORMAL)
        # Make it stay on top
        cv2.setWindowProperty("Roads", cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow("Roads", img)
        # cv2.resizeWindow("Roads", 1000, 1000)
        cv2.waitKey(1)
    
    if USE_EXTERNAL_VISUALIZATION:
        x = data["api"]["truckPlacement"]["coordinateX"]
        y = -data["api"]["truckPlacement"]["coordinateZ"]
        
        areaRoads = visRoads
        
        # Save the data for the API to send to the external visualization
        arData = {
            "lines": [],
            "circles": [],
            "boxes": [],
            "polygons": [],
        }
        
        # Convert each road to a line
        for road in areaRoads:
            try:
                # print(road.ParallelPoints)
                if road.ParallelPoints == []:
                    continue
                
                if road.ParallelPoints == [[(0, 0), (0, 0)], [(0, 0), (0, 0)]]:
                    continue
                
                for lane in road.ParallelPoints: # lane is a list of multiple points forming the curve of the lane
                    startPoint = None
                    index = 0
                    for point in lane: # point is {x, y}
                        if startPoint == None:
                            startPoint = point
                            index += 1
                            continue
                        if index == 1:
                            if GetDistanceFromTruck(startPoint[0], startPoint[1], data) < EXTERNAL_RENDER_DISTANCE or GetDistanceFromTruck(point[0], point[1], data) < EXTERNAL_RENDER_DISTANCE:
                                arData['lines'].append(Line((startPoint[0], startPoint[1]), (point[0], point[1]), color=[255, 255, 255, 255], thickness=5))
                        else:
                            if GetDistanceFromTruck(startPoint[0], startPoint[1], data) < EXTERNAL_RENDER_DISTANCE or GetDistanceFromTruck(point[0], point[1], data) < EXTERNAL_RENDER_DISTANCE:
                                arData['lines'].append(Line((lane[index - 1][0], lane[index - 1][1]), (point[0], point[1]), color=[255, 255, 255, 255], thickness=5))
                        index += 1
            except:
                import traceback
                traceback.print_exc()
                continue
            
        for prefab in visPrefabs:
            try:
                if prefab.Prefab.ValidRoad:
                    # Draw the curves
                    for curve in prefab.NavigationLanes:
                        startXY = (curve[0], curve[1])
                        endXY = (curve[2], curve[3])
                        if GetDistanceFromTruck(startXY[0], startXY[1], data) < EXTERNAL_RENDER_DISTANCE or GetDistanceFromTruck(endXY[0], endXY[1], data) < EXTERNAL_RENDER_DISTANCE:
                            arData['lines'].append(Line(startXY, endXY, color=[255, 255, 255, 255], thickness=5))
            except:
                continue
      
    return data, {
        "ar": arData,
    }

