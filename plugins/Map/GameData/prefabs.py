import json
from src.logger import print
from src.variables import *
from src.settings import *
from src.helpers import *
from src.mainUI import *
import sys
import plugins.Map.GameData.nodes as nodes
import math
import src.mainUI as mainUI

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
    
    
class PrefabCurve:
    id = 0
    idNode = 0
    startX = 0
    startZ = 0
    endX = 0
    endZ = 0
    length = 0
    nextLines = []
    prevLines = []
    
class NavigationRoute:
    Name = ""
    CurveIds = []
    Distance = 0
    StartNode = None
    EndNode = None
    
class NavigationRouteNode:
    id = 0
    X = 0
    Z = 0
    RotX = 0
    RotZ = 0
    LaneCount = 0
    InputPoints = []
    OutputPoints = []
    
class MapPoint:
    X = 0
    Z = 0
    LaneOffset = 0
    LaneCount = 0
    Hidden = False
    PrefabColorFlags = 0
    NeighbourCount = 0
    Neighbours = []
    ControlNodeIndex = 0
    
class PrefabNode:
    id = 0
    X = 0
    Z = 0
    RotX = 0
    RotZ = 0
    LaneCount = 0
    InputPoints = []
    OutputPoints = []
    
prefabs = []
optimizedPrefabs = {}
prefabFileName = variables.PATH + "/plugins/Map/GameData/prefabs.json"
limitToCount = 0

def LoadPrefabs():
    global prefabs
    global optimizedPrefabs
    
    jsonData = json.load(open(prefabFileName))
    jsonLength = len(jsonData)
    
    count = 0
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
            nodeObj.Z = node["Z"]
            nodeObj.RotX = node["RotX"]
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
            prefabCurveObj.startZ = prefabCurve["start_Z"]
            prefabCurveObj.endX = prefabCurve["end_X"]
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
            navigationRouteObj.StartNode.Z = navigationRoute["StartNode"]["Z"]
            navigationRouteObj.StartNode.RotX = navigationRoute["StartNode"]["RotX"]
            navigationRouteObj.StartNode.RotZ = navigationRoute["StartNode"]["RotZ"]
            navigationRouteObj.StartNode.LaneCount = navigationRoute["StartNode"]["LaneCount"]
            navigationRouteObj.StartNode.InputPoints = navigationRoute["StartNode"]["InputPoints"]
            navigationRouteObj.StartNode.OutputPoints = navigationRoute["StartNode"]["OutputPoints"]
            navigationRouteObj.EndNode = NavigationRouteNode()
            navigationRouteObj.EndNode.id = navigationRoute["EndNode"]["id"]
            navigationRouteObj.EndNode.X = navigationRoute["EndNode"]["X"]
            navigationRouteObj.EndNode.Z = navigationRoute["EndNode"]["Z"]
            navigationRouteObj.EndNode.RotX = navigationRoute["EndNode"]["RotX"]
            navigationRouteObj.EndNode.RotZ = navigationRoute["EndNode"]["RotZ"]
            navigationRouteObj.EndNode.LaneCount = navigationRoute["EndNode"]["LaneCount"]
            navigationRouteObj.EndNode.InputPoints = navigationRoute["EndNode"]["InputPoints"]
            navigationRouteObj.EndNode.OutputPoints = navigationRoute["EndNode"]["OutputPoints"]
            
            prefabObj.NavigationRoutes.append(navigationRouteObj)
            
        prefabs.append(prefabObj)
        
        count += 1
        if count % int(jsonLength/100) == 0:
            sys.stdout.write(f"\rLoaded {count} prefabs.\r")
            data = {
                "state": f"Parsing prefabs... {round(count/jsonLength * 100)}%",
                "stateProgress": count/jsonLength * 100,
                "totalProgress": 50 + count/jsonLength * 5
            }
            mainUI.ui.update(data)
            mainUI.root.update()
           
        if limitToCount != 0 and count >= limitToCount:
            break 
    
    sys.stdout.write(f"\rLoaded {count} prefabs.\nNow optimizing prefabs...")  
    
    
    count = 0
    removedCurves = 0
    for prefab in prefabs:
        neededCurves = []
        for navigationRoute in prefab.NavigationRoutes:
            for curveId in navigationRoute.CurveIds:
                if curveId not in neededCurves:
                    neededCurves.append(curveId)
        
        newCurves = []
        for curve in prefab.PrefabCurves:
            if curve.id not in neededCurves:
                prefab.PrefabCurves.remove(curve)
                removedCurves += 1
                
        count += 1
        if count % 50 == 0:
            sys.stdout.write(f"\rOptimized {count} prefabs.\r")
            data = {
                "state": f"Optimizing prefabs... {round(count/len(prefabs) * 100)}%",
                "stateProgress": count/len(prefabs) * 100,
                "totalProgress": 55 + count/len(prefabs) * 20
            }
            mainUI.ui.update(data)
            mainUI.root.update()
    
    sys.stdout.write(f"\rOptimized {count} prefabs.\nRemoved {removedCurves} curves.\nNow optimizing array...\n")
    
    # Use the first 3 numbers of the prefab token to optimize the array
    data = {
        "state": f"Optimizing array...",
        "stateProgress": 100,
        "totalProgress": 75
    }
    mainUI.ui.update(data)
    mainUI.root.update()
    
    for prefab in prefabs:
        token = str(prefab.Token)[:3]
        if token not in optimizedPrefabs:
            optimizedPrefabs[token] = []
        optimizedPrefabs[token].append(prefab)
    
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