# Package Imports
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import numpy as np
import importlib
import logging
import time
import math
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
from ETS2LA.plugins.Map.GameData import roads, nodes, prefabs, prefabItems, cities, companies
import ETS2LA.plugins.Map.GameData.extractor as extractor
import ETS2LA.plugins.Map.GameData.ferries as ferries
import ETS2LA.plugins.Map.Compute.compute as compute
plotter = importlib.import_module("Compute.plotter")
visualize = importlib.import_module("Visualize.visualize")
navigation = importlib.import_module("Compute.navigation")

runner:PluginRunner = None

# MARK: Globals
COMPUTE_STEERING_DATA = settings.Get("Map", "ComputeSteeringData", False)
STEERING_ENABLED = False

SEND_AR_DATA = settings.Get("Map", "SendARData", False)
SEND_EXTERNAL_DATA = settings.Get("Map", "SendExternalData", True)
EXTERNAL_DATA_RENDER_DISTANCE = settings.Get("Map", "ExternalDataRenderDistance", 200) # meters
NAVIGATION = settings.Get("Map", "Navigation", True) # whether to use the navigation system

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
    
    visualize.runner = runner

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
        # Update the plotter code
        try:
            importlib.reload(plotter)
            plotterHash = currentHash
        except:
            logging.exception("Failed to reload plotter")
            

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
        visualize.runner = runner
        
navigationHash = None
def UpdateNavigation():
    global navigationHash
    global navigation
    filepath = variables.PATH + "ETS2LA/plugins/Map/Compute/navigation.py"
    
    currentHash = ""
    with open(filepath, "r") as file:
        currentHash = hash(file.read())
    
    if currentHash != navigationHash:
        logging.warning("Reloading navigation")
        navigationHash = currentHash
        # Update the navigation code
        importlib.reload(navigation)
        navigation.runner = runner

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

# MARK: Load Game Data
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
        task6 = progress.add_task("[green]ferries[/green]", total=100)
        task5 = progress.add_task("[green]calculations[/green]", total=100)
        task7 = progress.add_task("[green]cities[/green]", total=100)
        task8 = progress.add_task("[green]companies[/green]", total=100)
        taskCount = 8
        
        if nodes.nodes == []:
            runner.state = Translate("map.loading.nodes")
            runner.state_progress = 1/taskCount
            time.sleep(0.1)
            nodes.task = task1
            nodes.progress = progress
            nodes.LoadNodes()
            progress.refresh()
            
        if roads.roads == []:
            #roads.limitToCount = 10000
            runner.state = Translate("map.loading.roads")
            runner.state_progress = 2/taskCount
            roads.task = task2
            roads.progress = progress
            roads.LoadRoads()
            progress.refresh()
            
        if prefabs.prefabs == []:
            #prefabs.limitToCount = 500
            runner.state = Translate("map.loading.prefab_data")
            runner.state_progress = 3/taskCount
            prefabs.task = task3
            prefabs.progress = progress
            prefabs.LoadPrefabs()
            progress.refresh() 
            
        if prefabItems.prefabItems == []:
            runner.state = Translate("map.loading.prefabs")
            runner.state_progress = 4/taskCount
            prefabItems.task = task4
            prefabItems.progress = progress
            prefabItems.LoadPrefabItems()
            progress.refresh()
            
        if ferries.ports == []:
            runner.state = Translate("map.loading.ferries")
            runner.state_progress = 5/taskCount
            ferries.task = task6
            ferries.progress = progress
            ferries.LoadFerries()
            progress.refresh()
        
        if nodes.itemsCalculated == False:
            runner.state = Translate("map.loading.final_calculations")
            runner.state_progress = 6/taskCount
            nodes.progress = progress
            nodes.task = task5
            nodes.CalculateForwardAndBackwardItemsForNodes()
            nodes.itemsCalculated = True
            
        if cities.cities == []:
            runner.state = Translate("map.loading.cities")
            runner.state_progress = 7/taskCount
            cities.task = task7
            cities.progress = progress
            cities.LoadCities()
            progress.refresh()
            
        if companies.companies == []:
            runner.state = Translate("map.loading.companies")
            runner.state_progress = 8/taskCount
            companies.task = task8
            companies.progress = progress
            companies.LoadCompanies()
            progress.refresh()
            
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
        if allPoints != None:
            for point in allPoints:
                img = visualize.VisualizePoint(data, point, img=img, zoom=ZOOM, pointSize=2)
        endPoints = data["map"]["endPoints"]
        if endPoints != None:
            for point in endPoints:
                img = visualize.VisualizePoint(data, point, img=img, zoom=ZOOM, pointSize=2, color=(0, 255, 0))
            
        #cv2.putText(img, "Steering enabled (default N)" if STEERING_ENABLED else "Steering disabled (default N)", (10, 190), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
        
    img = visualize.VisualizeTruck(data, img=img, zoom=ZOOM)
    img = visualize.VisualizeTrafficLights(data, img=img, zoom=ZOOM)

    # Convert to BGR
    runner.Profile("Visualizations")
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    SI.run(img)
    runner.Profile("Show Image")

def CreateARData(data, closeRoads, closePrefabs):
    arData = {
        "lines": []
        # "circles": [],
        # "boxes": [],
        # "polygons": [],
        # "texts": [],
        # "screenLines": [],
    }
    
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateY"]
        
    if data["map"]:
        if "allPoints" in data["map"]:
            for i in range(len(data["map"]["allPoints"]) - 2):
                if i % 2 == 0:
                    continue # Half the resolution
                point1 = data["map"]["allPoints"][i]
                point2 = data["map"]["allPoints"][i + 2]
                if GetDistanceFromTruck(point1[0], point1[1], data) < EXTERNAL_DATA_RENDER_DISTANCE or GetDistanceFromTruck(point2[0], point2[1], data) < EXTERNAL_DATA_RENDER_DISTANCE:
                    arData['lines'].append(Line((point1[0], point1[2], point1[1]), (point2[0], point2[2], point2[1]), color=[0, 94, 130, 100], thickness=5))
        
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
            _ = prefab.CurvePoints # Generate curve points for visualisation
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
    global NAVIGATION
    global lastUpdate
    global Steering
    
    if time.time() - lastUpdate < SETTINGS_UPDATE_RATE:
        return
    
    COMPUTE_STEERING_DATA = settings.Get("Map", "ComputeSteeringData", False)
    SEND_AR_DATA = settings.Get("Map", "SendARData", False)
    SEND_EXTERNAL_DATA = settings.Get("Map", "SendExternalData", True)
    INTERNAL_VISUALISATION = settings.Get("Map", "InternalVisualisation", True)
    ZOOM = settings.Get("Map", "Zoom", 1)
    NAVIGATION = settings.Get("Map", "Navigation", True)
    Steering.SMOOTH_TIME = settings.Get("Map", "SteeringSmoothTime", 0.5)
    
    lastUpdate = time.time()
    
def UpdateDataVariables(apiData):
    truckX = apiData["api"]["truckPlacement"]["coordinateX"]
    truckZ = apiData["api"]["truckPlacement"]["coordinateZ"]
    truckY = apiData["api"]["truckPlacement"]["coordinateY"]
    prefabItems.truckX = truckX
    prefabItems.truckZ = truckZ

# MARK: Plugin
def plugin():
    data = {
        "api": API.run(),
    }
    
    runner.Profile("API")
    
    if not DATA_LOADED:
        extractor.UpdateData()
        LoadGameData()        
    
    data = CreatePlaceholderMapData(data)    
    
    UpdateSettings()
    UpdatePlotter()
    UpdateVisualize()
    UpdateNavigation()
    UpdateDataVariables(data)
        
    closeRoads, updatedRoads = compute.GetRoads(data)
    closePrefabs, updatedPrefabs = compute.GetPrefabs(data)
    
    updatedRoads = compute.CalculateParallelPointsForRoads(closeRoads) # Will slowly populate the lanes over a few frames
    
    
    targetSpeed = data["api"]["truckFloat"]["speedLimit"]
    steeringPoints = []
    
    runner.Profile("Updates")
    
    if COMPUTE_STEERING_DATA:
        truckX = data["api"]["truckPlacement"]["coordinateX"]
        truckZ = data["api"]["truckPlacement"]["coordinateZ"]
        closestData = MapUtils.run(truckX, 0, truckZ, closeRoads=closeRoads, closePrefabs=closePrefabs)
        
        runner.Profile("MapUtils")
        
        if NAVIGATION:
            try:
                navigationData = navigation.Update(data, closestData)
            except:
                logging.exception("Failed to update navigation data")
                navigationData = None
        else:
            navigationData = None
            
        runner.Profile("Navigation data")
        
        steeringData = plotter.GetSteeringPoints(data, MapUtils, STEERING_ENABLED, navigationData)
        runner.Profile("Steering data")
        steeringPoints = steeringData["map"]["allPoints"]
        try: steeringAngle = steeringData["map"]["angle"]
        except: steeringAngle = 0
        data.update(steeringData)
        if steeringAngle is not None and not math.isnan(steeringAngle):
            Steering.run(value=(steeringAngle/180), sendToGame=STEERING_ENABLED)
            
        # Calculate how tight the next 50m of road is
        distance = 0
        points = []
        lastPoint = None
        for point in steeringPoints:
            if distance > 50:
                break
            if lastPoint is not None:
                distance += ((point[0] - lastPoint[0]) ** 2 + (point[1] - lastPoint[1]) ** 2) ** 0.5
            points.append(point)
            lastPoint = point
            
        runner.Profile("- doing stuff with said data")
        
        curvature = plotter.CalculateCurvature(points)
                
        # Modulate the target speed based on the curvature
        targetSpeed = targetSpeed * (1 - plotter.map_curvature_to_speed_effect(curvature))
        #logging.warning(f"Curvature: {curvature * 10e13}, Target speed: {targetSpeed}")
        
        runner.Profile("Curvature")
        
        
    if INTERNAL_VISUALISATION:
        DrawInternalVisualisation(data, closeRoads, closePrefabs)
    else:
        SI.DestroyWindow("Lane Assist")
        
    if SEND_EXTERNAL_DATA and (updatedPrefabs or updatedRoads):
        CreateExternalData(closeRoads, closePrefabs, updatedRoads, updatedPrefabs)
        
    runner.Profile("External Data")
        
    # Half the resolution of the steering points
    # if COMPUTE_STEERING_DATA:
    #     steeringPoints = steeringPoints[::2]
        
    arData = None
    if SEND_AR_DATA:
        arData = CreateARData(data, closeRoads, closePrefabs)
        return steeringPoints[:20], {
            "map": externalData,
            "ar": arData,
            "targetSpeed": targetSpeed,
        }
    
    if updatedPrefabs or updatedRoads:
        logging.warning("Map updated plugin data.")
        logging.warning(f"Roads: {len(externalData['roads'])}, Prefabs: {len(externalData['prefabs'])}")
        return steeringPoints[:20], {
            "map": externalData,
            "targetSpeed": targetSpeed,
        }
    
    return steeringPoints[:20], {
        "targetSpeed": targetSpeed
    }