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
from ETS2LA.backend.sounds import sounds
import sys
import numpy as np

import cv2
from PIL import Image

USE_INTERNAL_VISUALIZATION = True
USE_EXTERNAL_VISUALIZATION = True
EXTERNAL_RENDER_DISTANCE = 200 # How far to render in meters

try:
    from ETS2LA.plugins.AR.main import Line, Circle, Box, Polygon, Text, ScreenLine
except:
    USE_EXTERNAL_VISUALIZATION = False # Force external off

ZOOM = 2 # How many pixels per meter
VISUALIZE_PREFABS = True

LOAD_MSG = "Navigation data is loading..."
COMPLETE_MSG = "Navigation data loaded!"
ENABLED = False
LOAD_DATA = True

runner:PluginRunner = None

def ToggleSteering(state:bool, *args, **kwargs):
    global ENABLED
    ENABLED = state
    sounds.PlaysoundFromLocalPath(f"ETS2LA/assets/sounds/{('start' if state else 'end')}.mp3")

def Initialize():
    global API
    global SI
    global Steering
    global toast
    global RAYCASTING
    API = runner.modules.TruckSimAPI
    API.TRAILER = True
    SI = runner.modules.ShowImage
    Steering = runner.modules.Steering
    Steering.OFFSET = 0
    Steering.SMOOTH_TIME = 0.0
    Steering.IGNORE_SMOOTH = False
    Steering.SENSITIVITY = 1
    toast = runner.sonner
    RAYCASTING = runner.modules.Raycasting
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
        "vehicles": runner.GetData(["tags.vehicles"])[0] # Get the cars
    }
    
    
    drawText = []
    
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
    if LOAD_DATA:
        if nodes.nodes == []:
            toast(LOAD_MSG, type="promise")
            nodes.LoadNodes()
            
        if roads.roads == []:
            #roads.limitToCount = 10000
            roads.LoadRoads()
        if prefabs.prefabs == [] and VISUALIZE_PREFABS:
            #prefabs.limitToCount = 500
            prefabs.LoadPrefabs() 
        if prefabItems.prefabItems == [] and VISUALIZE_PREFABS:
            prefabItems.LoadPrefabItems()
        
        if nodes.itemsCalculated == False:
            nodes.CalculateForwardAndBackwardItemsForNodes()
            nodes.itemsCalculated = True
            toast(COMPLETE_MSG, type="success", promise=LOAD_MSG)
    
    if LOAD_DATA:
        visRoads = compute.GetRoads(data)
        compute.CalculateParallelPointsForRoads(visRoads) # Will slowly populate the lanes over a few frames
        computeData = compute.GetClosestRoadOrPrefabAndLane(data)
        data.update(computeData)
        Steering.run(value=data["map"]["closestDistance"], sendToGame=ENABLED)
        visPrefabs = compute.GetPrefabs(data)
    
    if compute.calculatingPrefabs: drawText.append("Loading prefabs...")
    if compute.calculatingRoads: drawText.append("Loading roads...")
    
    if USE_INTERNAL_VISUALIZATION:
        if LOAD_DATA:
            img = visualize.VisualizeRoads(data, visRoads, zoom=ZOOM)
            if VISUALIZE_PREFABS:
                img = visualize.VisualizePrefabs(data, visPrefabs, img=img, zoom=ZOOM)
        else:
            img = np.zeros((1000, 1000, 3), np.uint8)  
            
        img = visualize.VisualizeTruck(data, img=img, zoom=ZOOM)

        img = visualize.VisualizeTrafficLights(data, img=img, zoom=ZOOM)
        
        if data["vehicles"] != None:
            x, z = data["api"]["truckPlacement"]["coordinateX"], data["api"]["truckPlacement"]["coordinateZ"]
            for vehicle in data["vehicles"]:
                if vehicle == None: continue
                try:
                    #sys.stdout.write(f"{vehicle}\n")
                    #sys.stdout.flush()
                    leftPoint = vehicle.raycasts[0].relativePoint
                    rightPoint = vehicle.raycasts[1].relativePoint
                    middlePoint = ((leftPoint[0] + rightPoint[0]) / 2, (leftPoint[1] + rightPoint[1]) / 2, (leftPoint[2] + rightPoint[2]) / 2)
                    # Add the truck location to the middle point
                    middlePoint = (middlePoint[0] + x, middlePoint[1], middlePoint[2] + z)
                    leftDistance = vehicle.raycasts[0].distance
                    rightDistance = vehicle.raycasts[1].distance
                    middleDistance = (leftDistance + rightDistance) / 2
                    #sys.stdout.write(f"\r{middlePoint}")
                    #sys.stdout.flush()
                    img = visualize.VisualizePoint(data, middlePoint, img=img, zoom=ZOOM, distance=middleDistance)
                except:
                    continue
        
        drawText.append(f"Steering enabled (default N)" if ENABLED else "Steering disabled (default N)")
        
        count = 0
        for text in drawText:
            cv2.putText(img, text, (10, 190+40*count), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
            count += 1
        
        # Convert to BGR
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        SI.run(img)
        
    
    # Save the data for the API to send to the external visualization
    arData = {
        "lines": [],
        "circles": [],
        "boxes": [],
        "polygons": [],
        "texts": [],
        "screenLines": [],
    }
    if USE_EXTERNAL_VISUALIZATION and LOAD_DATA:
        x = data["api"]["truckPlacement"]["coordinateX"]
        y = data["api"]["truckPlacement"]["coordinateY"]
        
        areaRoads = visRoads
        
        
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
                    if road == data["map"]["closestItem"]:
                        color = [0, 255, 0, 100]
                        if lane == data["map"]["closestLane"]:
                            color = [0, 0, 255, 255]
                    else:
                        color = [255, 255, 255, 50]
                    for point in lane: # point is {x, y}
                        if startPoint == None:
                            startPoint = point
                            index += 1
                            continue
                        if index == 1:
                            if GetDistanceFromTruck(point[0], point[1], data) < EXTERNAL_RENDER_DISTANCE:
                                arData['lines'].append(Line((startPoint[0], y, startPoint[1]), (point[0], y, point[1]), color=color, thickness=5))
                        else:
                            if GetDistanceFromTruck(point[0], point[1], data) < EXTERNAL_RENDER_DISTANCE:
                                arData['lines'].append(Line((lane[index - 1][0], y, lane[index - 1][1]), (point[0], y, point[1]), color=color, thickness=5))
                        index += 1
            except:
                import traceback
                traceback.print_exc()
                continue
          
        for prefab in visPrefabs:
            try:
                # Draw the curves
                for curve in prefab.NavigationLanes:
                    if curve == data["map"]["closestLane"]:
                        color = [0, 0, 255, 255]
                    if prefab == data["map"]["closestItem"]:
                        color = [0, 255, 0, 100]
                    else:
                        color = [255, 255, 255, 50]
                    startXY = (curve[0], y, curve[1])
                    endXY = (curve[2], y, curve[3])
                    if GetDistanceFromTruck(startXY[0], startXY[2], data) < EXTERNAL_RENDER_DISTANCE or GetDistanceFromTruck(endXY[0], endXY[2], data) < EXTERNAL_RENDER_DISTANCE:
                        arData['lines'].append(Line(startXY, endXY, color=color, thickness=5))
            except:
                import traceback
                traceback.print_exc()
                continue

    if USE_EXTERNAL_VISUALIZATION:
        x = data["api"]["truckPlacement"]["coordinateX"]
        y = data["api"]["truckPlacement"]["coordinateY"]
        z = data["api"]["truckPlacement"]["coordinateZ"]
    
        # Add the cars to the external visualization as a line from the start point to y + 1
        if data["vehicles"] != None:
            for vehicle in data["vehicles"]:
                if vehicle == None: continue
                try:
                    leftPoint = vehicle.screenPoints[0]
                    leftPoint = (leftPoint[0], leftPoint[1] + 5)
                    rightPoint = vehicle.screenPoints[1]
                    rightPoint = (rightPoint[0], rightPoint[1] + 5)
                    middlePoint = ((leftPoint[0] + rightPoint[0]) / 2, (leftPoint[1] + rightPoint[1]) / 2)
                    # Add the truck location to the points
                    # leftPoint = (leftPoint[0] + x, leftPoint[1], leftPoint[2] + z)
                    # rightPoint = (rightPoint[0] + x, rightPoint[1], rightPoint[2] + z)
                    # middlePoint = (middlePoint[0] + x, middlePoint[1], middlePoint[2] + z)
                    # Get the distance
                    leftDistance = vehicle.raycasts[0].distance
                    rightDistance = vehicle.raycasts[1].distance
                    middleDistance = (leftDistance + rightDistance) / 2
                    # Add the lines
                    arData['screenLines'].append(ScreenLine((leftPoint[0], leftPoint[1]), (rightPoint[0], rightPoint[1]), color=[0, 255, 0, 100], thickness=2))
                    # Add the text
                    arData['texts'].append(Text(f"{round(middleDistance, 1)}m", (middlePoint[0], middlePoint[1]), color=[0, 255, 0, 255], size=15))
                except:
                    continue

    if arData == {}:
        return
    
    return None, {
        "ar": arData
    }

