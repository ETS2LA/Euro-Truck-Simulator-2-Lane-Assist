# Package Imports
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import logging
import time
import cv2
import os


# ETS2LA Imports
from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.variables as variables
import ETS2LA.backend.settings as settings
from ETS2LA.plugins.AR.main import Line
import ETS2LA.backend.sounds as sounds

# Plugin imports
from GameData import roads, nodes, prefabs, prefabItems
import Compute.compute as compute
from Visualize import visualize

runner:PluginRunner = None

# MARK: Globals
COMPUTE_STEERING_DATA = settings.Get("Map", "ComputeSteeringData", False)
STEERING_ENABLED = False

SEND_AR_DATA = settings.Get("Map", "SendARData", False)
SEND_EXTERNAL_DATA = settings.Get("Map", "SendExternalData", True)
EXTERNAL_DATA_RENDER_DISTANCE = settings.Get("Map", "ExternalDataRenderDistance", 200) # meters

LOAD_MSG = "Navigation data is loading..."
COMPLETE_MSG = "Navigation data loaded!"

INTERNAL_VISUALISATION = settings.Get("Map", "InternalVisualisation", True)
ZOOM = settings.Get("Map", "Zoom", 1)

DATA_LOADED = False
JSON_FOUND = False

SETTINGS_UPDATE_RATE = 1 # seconds

# MARK: Initialize
def Initialize():
    global RAYCASTING
    global Steering
    global toast
    global API
    global SI
    
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

# MARK: Utilities

def GetDistanceFromTruck(x, z, data):
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    
    return ((truckX - x) ** 2 + (truckZ - z) ** 2) ** 0.5

def CheckIfJSONDataIsAvailable(data):
    global JSON_FOUND
    # Check if the GameData folder has it's json files
    filesInGameData = os.listdir(variables.PATH + "ETS2LA/plugins/Map/GameData")
    for file in filesInGameData:
        if file.endswith(".json"):
            JSON_FOUND = True
            
    if not JSON_FOUND:
        toast("No JSON files found in the GameData folder, please unpack the GameData.zip file.")

def LoadGameData():
    global DATA_LOADED
    customProgress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    )
    
    with customProgress as progress:
        task1 = progress.add_task("[green]nodes[/green]", total=100)
        task2 = progress.add_task("[green]roads[/green]", total=100)
        task3 = progress.add_task("[green]prefab data[/green]", total=100)
        task4 = progress.add_task("[green]prefabs[/green]", total=100)
        task5 = progress.add_task("[green]calculations[/green]", total=100)
        
        if nodes.nodes == []:
            toast(LOAD_MSG, type="promise")
            nodes.task = task1
            nodes.progress = progress
            nodes.LoadNodes()
            progress.refresh()
            
        if roads.roads == []:
            #roads.limitToCount = 10000
            roads.task = task2
            roads.progress = progress
            roads.LoadRoads()
            progress.refresh()
            
        if prefabs.prefabs == []:
            #prefabs.limitToCount = 500
            prefabs.task = task3
            prefabs.progress = progress
            prefabs.LoadPrefabs()
            progress.refresh() 
            
        if prefabItems.prefabItems == []:
            prefabItems.task = task4
            prefabItems.progress = progress
            prefabItems.LoadPrefabItems()
            progress.refresh()
        
        if nodes.itemsCalculated == False:
            nodes.progress = progress
            nodes.task = task5
            nodes.CalculateForwardAndBackwardItemsForNodes()
            nodes.itemsCalculated = True
            toast(COMPLETE_MSG, type="success", promise=LOAD_MSG)
    
    logging.info("Data loaded")
    print("\n")
    DATA_LOADED = True

def ToggleSteering(state:bool, *args, **kwargs):
    global STEERING_ENABLED
    STEERING_ENABLED = state
    if COMPUTE_STEERING_DATA:
        sounds.Play('start' if state else 'end')

def DrawInternalVisualisation(data, closeRoads, closePrefabs):
    img = visualize.VisualizeRoads(data, closeRoads, zoom=ZOOM)
    img = visualize.VisualizePrefabs(data, closePrefabs, img=img, zoom=ZOOM)
    
    if COMPUTE_STEERING_DATA:
        img = visualize.VisualizePoint(data, data["map"]["closestPoint"], img=img, zoom=ZOOM, pointSize=3)
        allPoints = data["map"]["allPoints"]
        for point in allPoints:
            img = visualize.VisualizePoint(data, point, img=img, zoom=ZOOM, pointSize=2)
            
        cv2.putText(img, "Steering enabled (default N)" if STEERING_ENABLED else "Steering disabled (default N)", (10, 190), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
        
    img = visualize.VisualizeTruck(data, img=img, zoom=ZOOM)
    img = visualize.VisualizeTrafficLights(data, img=img, zoom=ZOOM)

    # Convert to BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    SI.run(img)

def CreateARData(data, closeRoads, closePrefabs):
    arData = {
        "lines": [],
        "circles": [],
        "boxes": [],
        "polygons": [],
        "texts": [],
        "screenLines": [],
    }
    
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateY"]
    
    # Convert each road to a line
    for road in closeRoads:
        try:
            # print(road.ParallelPoints)
            if road.ParallelPoints == [] or road.ParallelPoints == None or road.ParallelPoints == [[(0, 0), (0, 0)], [(0, 0), (0, 0)]]:
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
                        if GetDistanceFromTruck(point[0], point[1], data) < EXTERNAL_DATA_RENDER_DISTANCE:
                            arData['lines'].append(Line((startPoint[0], road.YValues[0], startPoint[1]), (point[0], road.YValues[1], point[1]), color=color, thickness=5))
                    else:
                        if GetDistanceFromTruck(point[0], point[1], data) < EXTERNAL_DATA_RENDER_DISTANCE:
                            arData['lines'].append(Line((lane[index - 1][0], road.YValues[index - 1], lane[index - 1][1]), (point[0], road.YValues[index], point[1]), color=color, thickness=5))
                    index += 1
        except:
            import traceback
            traceback.print_exc()
            continue
        
    for prefab in closePrefabs:
        try:
            try:
                originNode = prefab.Nodes[0]
                prefabY = originNode.Y
            except:
                prefabY = y
            # Draw the curves
            for curve in prefab.NavigationLanes:
                if curve == data["map"]["closestLane"]:
                    color = [0, 0, 255, 255]
                if prefab == data["map"]["closestItem"]:
                    color = [0, 255, 0, 100]
                else:
                    color = [255, 255, 255, 50]
                    
                startXY = (curve[0], prefabY, curve[1])
                endXY = (curve[2], prefabY, curve[3])
                if GetDistanceFromTruck(startXY[0], startXY[2], data) < EXTERNAL_DATA_RENDER_DISTANCE or GetDistanceFromTruck(endXY[0], endXY[2], data) < EXTERNAL_DATA_RENDER_DISTANCE:
                    arData['lines'].append(Line(startXY, endXY, color=color, thickness=5))
        except:
            import traceback
            traceback.print_exc()
            continue
        
    return arData

externalData = []
def CreateExternalData(closeRoads, closePrefabs, roadUpdate, prefabUpdate):
    global externalData
    if roadUpdate or prefabUpdate:
        dataRoads = []
        for road in closeRoads:
            dataRoads.append(road.json())
            
        dataPrefabs = []
        for prefab in closePrefabs:
            prefab.Nodes = []
            try:
                prefab.StartNode.ForwardItem = None
                prefab.StartNode.BackwardItem = None
            except: pass
            try:
                prefab.EndNode.ForwardItem = None
                prefab.EndNode.BackwardItem = None
            except: pass
            prefab.Navigation = []
            prefab.Prefab = None
            dataPrefabs.append(prefab.json())

        externalData = {
            "roads": dataRoads,
            "prefabs": dataPrefabs,
        }

lastUpdate = time.time()
def UpdateSettings():
    global COMPUTE_STEERING_DATA
    global SEND_AR_DATA
    global SEND_EXTERNAL_DATA
    global INTERNAL_VISUALISATION
    global ZOOM
    global lastUpdate
    
    if time.time() - lastUpdate < SETTINGS_UPDATE_RATE:
        return
    
    COMPUTE_STEERING_DATA = settings.Get("Map", "ComputeSteeringData", False)
    SEND_AR_DATA = settings.Get("Map", "SendARData", False)
    SEND_EXTERNAL_DATA = settings.Get("Map", "SendExternalData", True)
    INTERNAL_VISUALISATION = settings.Get("Map", "InternalVisualisation", True)
    ZOOM = settings.Get("Map", "Zoom", 1)
    
    lastUpdate = time.time()

# MARK: Plugin
def plugin():
    data = {
        "api": API.run(),
    }
    
    if not JSON_FOUND:
        CheckIfJSONDataIsAvailable(data)
        return None
    
    if not DATA_LOADED:
        LoadGameData()        
        
    UpdateSettings()
        
    closeRoads, updatedRoads = compute.GetRoads(data)
    closePrefabs, updatedPrefabs = compute.GetPrefabs(data)
    compute.CalculateParallelPointsForRoads(closeRoads) # Will slowly populate the lanes over a few frames
    
    if COMPUTE_STEERING_DATA:
        computeData = compute.GetClosestRoadOrPrefabAndLane(data)
        data.update(computeData)
        Steering.run(value=data["map"]["closestDistance"], sendToGame=STEERING_ENABLED)
        
    if INTERNAL_VISUALISATION:
        DrawInternalVisualisation(data, closeRoads, closePrefabs)
    else:
        SI.DestroyWindow("Lane Assist")
        
    if SEND_EXTERNAL_DATA:
        CreateExternalData(closeRoads, closePrefabs, updatedRoads, updatedPrefabs)
        
    arData = None
    if SEND_AR_DATA:
        arData = CreateARData(data, closeRoads, closePrefabs)
        return None, {
            "map": externalData,
            "ar": arData,
        }
    
    return None, {
        "map": externalData,
    }