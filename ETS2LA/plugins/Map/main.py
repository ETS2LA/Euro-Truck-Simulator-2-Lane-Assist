# Package Imports
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import importlib
import logging
import time
import cv2
import os


# ETS2LA Imports
from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.utils.translator import Translate
import ETS2LA.backend.settings as settings
from ETS2LA.plugins.AR.main import Line
import ETS2LA.backend.sounds as sounds
import ETS2LA.variables as variables

# Plugin imports
from ETS2LA.plugins.Map.GameData import roads, nodes, prefabs, prefabItems
import ETS2LA.plugins.Map.GameData.extractor as extractor
import ETS2LA.plugins.Map.Compute.compute as compute
plotter = importlib.import_module("Compute.plotter")
visualize = importlib.import_module("Visualize.visualize")

runner:PluginRunner = None

# MARK: Globals
COMPUTE_STEERING_DATA = settings.Get("Map", "ComputeSteeringData", False)
STEERING_ENABLED = False

SEND_AR_DATA = settings.Get("Map", "SendARData", False)
SEND_EXTERNAL_DATA = settings.Get("Map", "SendExternalData", True)
EXTERNAL_DATA_RENDER_DISTANCE = settings.Get("Map", "ExternalDataRenderDistance", 200) # meters

INTERNAL_VISUALISATION = settings.Get("Map", "InternalVisualisation", True)
ZOOM = settings.Get("Map", "Zoom", 1)

DATA_LOADED = False
JSON_FOUND = False

SETTINGS_UPDATE_RATE = 1 # seconds

# MARK: Initialize
def Initialize():
    global RAYCASTING
    global Steering
    global MapUtils
    global toast
    global API
    global SI
    
    API = runner.modules.TruckSimAPI
    API.TRAILER = True
    
    SI = runner.modules.ShowImage
    
    MapUtils = runner.modules.MapUtils
    
    Steering = runner.modules.Steering
    Steering.OFFSET = 0
    Steering.SMOOTH_TIME = 0.5
    Steering.IGNORE_SMOOTH = False
    Steering.SENSITIVITY = 1
    
    toast = runner.sonner
    
    RAYCASTING = runner.modules.Raycasting

# MARK: Utilities

plotterHash = None
def UpdatePlotter():
    global plotterHash
    global plotter
    filepath = variables.PATH + "ETS2LA/plugins/Map/Compute/plotter.py"
    
    currentHash = ""
    with open(filepath, "r") as file:
        currentHash = hash(file.read())
    
    if currentHash != plotterHash:
        logging.warning("Reloading plotter")
        plotterHash = currentHash
        # Update the plotter code
        importlib.reload(plotter)

visualizeHash = None
def UpdateVisualize():
    global visualizeHash
    global visualize
    filepath = variables.PATH + "ETS2LA/plugins/Map/Visualize/visualize.py"
    
    currentHash = ""
    with open(filepath, "r") as file:
        currentHash = hash(file.read())
    
    if currentHash != visualizeHash:
        logging.warning("Reloading visualize")
        visualizeHash = currentHash
        # Update the visualize code
        importlib.reload(visualize)

def GetDistanceFromTruck(x, z, data):
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    
    return ((truckX - x) ** 2 + (truckZ - z) ** 2) ** 0.5

SENT_JSON_ERROR = False
def CheckIfJSONDataIsAvailable(data):
    global JSON_FOUND, SENT_JSON_ERROR
    # Check if the GameData folder has it's json files
    filesInGameData = os.listdir(variables.PATH + "ETS2LA/plugins/Map/GameData")
    for file in filesInGameData:
        if file.endswith(".json"):
            JSON_FOUND = True
            
    if not JSON_FOUND:
        if not SENT_JSON_ERROR:
            toast(Translate("map.json_not_found"))
            SENT_JSON_ERROR = True

def LoadGameData():
    global DATA_LOADED
    customProgress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    )
    
    runner.state = Translate("map.loading.preparing")
    runner.state_progress = 0
    with customProgress as progress:
        task1 = progress.add_task("[green]nodes[/green]", total=100)
        task2 = progress.add_task("[green]roads[/green]", total=100)
        task3 = progress.add_task("[green]prefab data[/green]", total=100)
        task4 = progress.add_task("[green]prefabs[/green]", total=100)
        task5 = progress.add_task("[green]calculations[/green]", total=100)
        
        if nodes.nodes == []:
            runner.state = Translate("map.loading.nodes")
            runner.state_progress = 0
            time.sleep(0.1)
            nodes.task = task1
            nodes.progress = progress
            nodes.LoadNodes()
            progress.refresh()
            
        if roads.roads == []:
            #roads.limitToCount = 10000
            runner.state = Translate("map.loading.roads")
            runner.state_progress = 0.2
            roads.task = task2
            roads.progress = progress
            roads.LoadRoads()
            progress.refresh()
            
        if prefabs.prefabs == []:
            #prefabs.limitToCount = 500
            runner.state = Translate("map.loading.prefab_data")
            runner.state_progress = 0.4
            prefabs.task = task3
            prefabs.progress = progress
            prefabs.LoadPrefabs()
            progress.refresh() 
            
        if prefabItems.prefabItems == []:
            runner.state = Translate("map.loading.prefabs")
            runner.state_progress = 0.6
            prefabItems.task = task4
            prefabItems.progress = progress
            prefabItems.LoadPrefabItems()
            progress.refresh()
        
        if nodes.itemsCalculated == False:
            runner.state = Translate("map.loading.final_calculations")
            runner.state_progress = 0.8
            nodes.progress = progress
            nodes.task = task5
            nodes.CalculateForwardAndBackwardItemsForNodes()
            nodes.itemsCalculated = True
            
        runner.state = "running"
        runner.state_progress = -1
    
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
        endPoints = data["map"]["endPoints"]
        for point in endPoints:
            img = visualize.VisualizePoint(data, point, img=img, zoom=ZOOM, pointSize=2, color=(0, 255, 0))
            
        #cv2.putText(img, "Steering enabled (default N)" if STEERING_ENABLED else "Steering disabled (default N)", (10, 190), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
        
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

def CreatePlaceholderMapData(data):
    data.update({ 
        "map": {
            "closestItem": None,
            "closestLane": None,
            "closestPoint": None,
            "closestDistance": None,
            "closestType": None,
            "inBoundingBox": None,
            "closestLanes": None,
            "allPoints": None
        }
    })
    return data

externalData = {}
def CreateExternalData(closeRoads, closePrefabs, roadUpdate, prefabUpdate):
    global externalData
    if roadUpdate or prefabUpdate:
        dataRoads = []
        for road in closeRoads:
            dataRoads.append(road.json())
            
        dataPrefabs = []
        for prefab in closePrefabs:
            prefabJson = prefab.json()
            dataPrefabs.append(prefabJson)

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
    
    # No longer needed, data will always be available
    # if not JSON_FOUND:
    #     CheckIfJSONDataIsAvailable(data)
    #     return None
    
    if not DATA_LOADED:
        extractor.UpdateData()
        LoadGameData()        
    
    data = CreatePlaceholderMapData(data)    
    
    UpdateSettings()
    UpdatePlotter()
    UpdateVisualize()
        
    closeRoads, updatedRoads = compute.GetRoads(data)
    closePrefabs, updatedPrefabs = compute.GetPrefabs(data)
    
    updatedRoads = compute.CalculateParallelPointsForRoads(closeRoads) # Will slowly populate the lanes over a few frames
    
    steeringPoints = []
    if COMPUTE_STEERING_DATA:
        steeringData = plotter.GetNextPoints(data, MapUtils, STEERING_ENABLED)
        steeringPoints = steeringData["map"]["allPoints"]
        try: steeringAngle = steeringData["map"]["angle"]
        except: steeringAngle = 0
        data.update(steeringData)
        Steering.run(value=(steeringAngle/180), sendToGame=STEERING_ENABLED)
        
    if INTERNAL_VISUALISATION:
        DrawInternalVisualisation(data, closeRoads, closePrefabs)
    else:
        SI.DestroyWindow("Lane Assist")
        
    if SEND_EXTERNAL_DATA:
        CreateExternalData(closeRoads, closePrefabs, updatedRoads, updatedPrefabs)
        
    arData = None
    if SEND_AR_DATA:
        arData = CreateARData(data, closeRoads, closePrefabs)
        return steeringPoints, {
            "map": externalData,
            "ar": arData,
        }
    
    if updatedPrefabs or updatedRoads:
        return steeringPoints, {
            "map": externalData,
        }
    
    return steeringPoints