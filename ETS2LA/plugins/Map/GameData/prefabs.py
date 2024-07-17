from ETS2LA.variables import *
from ETS2LA.backend.settings import *
import ETS2LA.plugins.Map.GameData.nodes as nodes
import logging
import json
import sys
import math

from rich.progress import Task, Progress

# For loading nodes progress indicator
task: Task = None
progress: Progress = None

prefabFileName = PATH + "ETS2LA/plugins/Map/GameData/prefabs.json"
optimizedPrefabs = {}
print = logging.info
limitToCount = 0
prefabs = []

# MARK: Classes
class Prefab:
    FilePath = ""
    Token = 0
    Category = ""
    ValidRoad = False
    PrefabNodes = []
    SpawnPoints = []
    MapPoints = []
    TriggerPoints = []
    PrefabCurves = []
    NavigationRoutes = []
    CalculatedLanePoints = []
    
    def json(self):
        return {
            "FilePath": self.FilePath,
            "Token": self.Token,
            "Category": self.Category,
            "ValidRoad": self.ValidRoad,
            "PrefabNodes": [node.json() for node in self.PrefabNodes],
            "SpawnPoints": self.SpawnPoints,
            "MapPoints": [mapPoint.json() for mapPoint in self.MapPoints],
            "TriggerPoints": self.TriggerPoints,
            "PrefabCurves": [curve.json() for curve in self.PrefabCurves],
            "NavigationRoutes": [route.json() for route in self.NavigationRoutes]
        }
    
    
class PrefabCurve:
    id = 0
    idNode = 0
    startX = 0
    startY = 0
    startZ = 0
    endX = 0
    endY = 0
    endZ = 0
    length = 0
    nextLines = []
    prevLines = []
    
    def json(self):
        return {
            "id": self.id,
            "idNode": self.idNode,
            "start_X": self.startX,
            "start_Y": self.startY,
            "start_Z": self.startZ,
            "end_X": self.endX,
            "end_Y": self.endY,
            "end_Z": self.endZ,
            "length": self.length,
            "nextLines": self.nextLines,
            "prevLines": self.prevLines
        }
    
class NavigationRoute:
    Name = ""
    CurveIds = []
    Distance = 0
    StartNode = None
    EndNode = None
    
    def json(self):
        return {
            "Name": self.Name,
            "CurveIds": self.CurveIds,
            "Distance": self.Distance,
            "StartNode": self.StartNode.json(),
            "EndNode": self.EndNode.json()
        }
    
class NavigationRouteNode:
    id = 0
    X = 0
    Y = 0
    Z = 0
    RotX = 0
    RotY = 0
    RotZ = 0
    LaneCount = 0
    InputPoints = []
    OutputPoints = []
    
    def json(self):
        return {
            "id": self.id,
            "X": self.X,
            "Y": self.Y,
            "Z": self.Z,
            "RotX": self.RotX,
            "RotY": self.RotY,
            "RotZ": self.RotZ,
            "LaneCount": self.LaneCount,
            "InputPoints": self.InputPoints,
            "OutputPoints": self.OutputPoints
        }
    
class MapPoint:
    X = 0
    Y = 0
    Z = 0
    LaneOffset = 0
    LaneCount = 0
    Hidden = False
    PrefabColorFlags = 0
    NeighbourCount = 0
    Neighbours = []
    ControlNodeIndex = 0
    
    def json(self):
        return {
            "X": self.X,
            "Y": self.Y, 
            "Z": self.Z,
            "LaneOffset": self.LaneOffset,
            "LaneCount": self.LaneCount,
            "Hidden": self.Hidden,
            "PrefabColorFlags": self.PrefabColorFlags,
            "NeighbourCount": self.NeighbourCount,
            "Neighbours": self.Neighbours,
            "ControlNodeIndex": self.ControlNodeIndex
        }
    
class PrefabNode:
    id = 0
    X = 0
    Y = 0
    Z = 0
    RotX = 0
    RotY = 0
    RotZ = 0
    LaneCount = 0
    InputPoints = []
    OutputPoints = []
    
    def json(self):
        return {
            "id": self.id,
            "X": self.X,
            "Y": self.Y,
            "Z": self.Z,
            "RotX": self.RotX,
            "RotY": self.RotY,
            "RotZ": self.RotZ,
            "LaneCount": self.LaneCount,
            "InputPoints": self.InputPoints,
            "OutputPoints": self.OutputPoints
        }
    
# MARK: Load Prefabs
def LoadPrefabs():
    global prefabs
    global optimizedPrefabs
    
    jsonData = json.load(open(prefabFileName))
    jsonLength = len(jsonData)
    
    # sys.stdout.write(f"\nLoading {jsonLength} prefabs...\n")
    
    progress.update(task, total=jsonLength)
    
    count = 0
    # MARK: >> Parse JSON
    for prefab in jsonData:
        
        prefab = jsonData[prefab]
        
        prefabObj = Prefab()
        prefabObj.FilePath = prefab["FilePath"]
        prefabObj.Token = prefab["Token"]
        prefabObj.Category = prefab["Category"]
        prefabObj.ValidRoad = prefab["ValidRoad"]
        
        for node in prefab["PrefabNodes"]:
            nodeObj = PrefabNode()
            nodeObj.id = node["id"]
            nodeObj.X = node["X"]
            nodeObj.Y = node["Y"]
            nodeObj.Z = node["Z"]
            nodeObj.RotX = node["RotX"]
            nodeObj.RotY = node["RotY"]
            nodeObj.RotZ = node["RotZ"]
            nodeObj.LaneCount = node["LaneCount"]
            nodeObj.InputPoints = node["InputPoints"]
            nodeObj.OutputPoints = node["OutputPoints"]
            prefabObj.PrefabNodes.append(nodeObj)
        
        for spawnPoint in prefab["SpawnPoints"]:
            prefabObj.SpawnPoints.append(spawnPoint)
        
        for mapPoint in prefab["MapPoints"]:
            mapPointObj = MapPoint()
            mapPointObj.X = mapPoint["X"]
            mapPointObj.Y = mapPoint["Y"]
            mapPointObj.Z = mapPoint["Z"]
            mapPointObj.LaneOffset = mapPoint["LaneOffset"]
            mapPointObj.LaneCount = mapPoint["LaneCount"]
            mapPointObj.Hidden = mapPoint["Hidden"]
            mapPointObj.PrefabColorFlags = mapPoint["PrefabColorFlags"]
            mapPointObj.NeighbourCount = mapPoint["NeighbourCount"]
            mapPointObj.Neighbours = mapPoint["Neighbours"]
            mapPointObj.ControlNodeIndex = mapPoint["ControlNodeIndex"]
            prefabObj.MapPoints.append(mapPointObj)
        
        for triggerPoint in prefab["TriggerPoints"]:
            prefabObj.TriggerPoints.append(triggerPoint)
        
        prefabObj.PrefabCurves = []
        for prefabCurve in prefab["PrefabCurves"]:
            prefabCurveObj = PrefabCurve()
            prefabCurveObj.id = prefabCurve["id"]
            prefabCurveObj.idNode = prefabCurve["idNode"]
            prefabCurveObj.startX = prefabCurve["start_X"]
            prefabCurveObj.startY = prefabCurve["start_Y"]
            prefabCurveObj.startZ = prefabCurve["start_Z"]
            prefabCurveObj.endX = prefabCurve["end_X"]
            prefabCurveObj.endY = prefabCurve["end_Y"]
            prefabCurveObj.endZ = prefabCurve["end_Z"]
            try: prefabCurveObj.length = prefabCurve["length"] 
            except: pass
            prefabCurveObj.nextLines = prefabCurve["nextLines"]
            prefabCurveObj.prevLines = prefabCurve["prevLines"]
            prefabObj.PrefabCurves.append(prefabCurveObj)
                    
            
        for navigationRoute in prefab["NavigationRoutes"]:
            name = navigationRoute
            navigationRoute = prefab["NavigationRoutes"][navigationRoute]
            navigationRouteObj = NavigationRoute()
            navigationRouteObj.Name = name
            navigationRouteObj.CurveIds = navigationRoute["CurveIds"]
            navigationRouteObj.Distance = navigationRoute["Distance"]
            navigationRouteObj.StartNode = NavigationRouteNode()
            navigationRouteObj.StartNode.id = navigationRoute["StartNode"]["id"]
            navigationRouteObj.StartNode.X = navigationRoute["StartNode"]["X"]
            navigationRouteObj.StartNode.Y = navigationRoute["StartNode"]["Y"]
            navigationRouteObj.StartNode.Z = navigationRoute["StartNode"]["Z"]
            navigationRouteObj.StartNode.RotX = navigationRoute["StartNode"]["RotX"]
            navigationRouteObj.StartNode.RotY = navigationRoute["StartNode"]["RotY"]
            navigationRouteObj.StartNode.RotZ = navigationRoute["StartNode"]["RotZ"]
            navigationRouteObj.StartNode.LaneCount = navigationRoute["StartNode"]["LaneCount"]
            navigationRouteObj.StartNode.InputPoints = navigationRoute["StartNode"]["InputPoints"]
            navigationRouteObj.StartNode.OutputPoints = navigationRoute["StartNode"]["OutputPoints"]
            navigationRouteObj.EndNode = NavigationRouteNode()
            navigationRouteObj.EndNode.id = navigationRoute["EndNode"]["id"]
            navigationRouteObj.EndNode.X = navigationRoute["EndNode"]["X"]
            navigationRouteObj.EndNode.Y = navigationRoute["EndNode"]["Y"]
            navigationRouteObj.EndNode.Z = navigationRoute["EndNode"]["Z"]
            navigationRouteObj.EndNode.RotX = navigationRoute["EndNode"]["RotX"]
            navigationRouteObj.EndNode.RotY = navigationRoute["EndNode"]["RotY"]
            navigationRouteObj.EndNode.RotZ = navigationRoute["EndNode"]["RotZ"]
            navigationRouteObj.EndNode.LaneCount = navigationRoute["EndNode"]["LaneCount"]
            navigationRouteObj.EndNode.InputPoints = navigationRoute["EndNode"]["InputPoints"]
            navigationRouteObj.EndNode.OutputPoints = navigationRoute["EndNode"]["OutputPoints"]
            
            prefabObj.NavigationRoutes.append(navigationRouteObj)
            
        prefabs.append(prefabObj)
        
        count += 1
        #if count % int(jsonLength/100) == 0:
            # sys.stdout.write(f"\r > {count} ({round(count/jsonLength*100)}%)...")
           
        progress.advance(task)
           
        if limitToCount != 0 and count >= limitToCount:
            break 
    
    # sys.stdout.write(f"\r > {count} ({round(count/jsonLength*100)}%)... done!\n")

    progress.update(task, total=progress._tasks[task].total + len(prefabs))

    # sys.stdout.write(f" > Optimizing prefab array...\r")
    # MARK: >> Optimize
    for prefab in prefabs:
        token = str(prefab.Token)[:3]
        if token not in optimizedPrefabs:
            optimizedPrefabs[token] = []
        optimizedPrefabs[token].append(prefab)
        progress.advance(task)
    
    progress.update(task, completed=progress._tasks[task].total)
    
    # sys.stdout.write(f" > Optimizing prefab array... done!\n")
    
    print("Prefab parsing done!")
        
        
def GetPrefabByToken(token):
    first3 = str(token)[:3]
    if first3 in optimizedPrefabs:
        for prefab in optimizedPrefabs[first3]:
            if prefab.Token == token:
                return prefab
    else:
        for prefab in prefabs:
            if prefab.Token == token:
                return prefab
    
    return None