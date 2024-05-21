import json
import logging
print = logging.info
from ETS2LA.backend.variables import *
from ETS2LA.backend.settings import *
import sys
import GameData.nodes as nodes
import math

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
prefabFileName = PATH + "ETS2LA/plugins/Map/GameData/prefabs.json"
limitToCount = 0

def LoadPrefabs():
    global prefabs
    global optimizedPrefabs
    
    jsonData = json.load(open(prefabFileName))
    jsonLength = len(jsonData)
    
    sys.stdout.write(f"\nLoading {jsonLength} prefabs...\n")
    
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
            sys.stdout.write(f"\r > {count} ({round(count/jsonLength*100)}%)...")
           
        if limitToCount != 0 and count >= limitToCount:
            break 
    
    sys.stdout.write(f"\r > {count} ({round(count/jsonLength*100)}%)... done!\n")
    
    # # Not needed anymore?
    # sys.stdout.write(f" > Optimizing prefabs...\n")
    # 
    # count = 0
    # removedCurves = 0
    # prefabCount = len(prefabs)
    # prefabOptimizeStartTime = time.time()
    # for prefab in prefabs:
    #     neededCurves = set()
    #     for navigationRoute in prefab.NavigationRoutes:
    #         neededCurves.update(navigationRoute.CurveIds)
    #     
    #     prefab.PrefabCurves = [curve for curve in prefab.PrefabCurves if curve.id in neededCurves]
    #     removedCurves += len(prefab.PrefabCurves)
    # 
    #     count += 1
    #     if count % 50 == 0:
    #         prefabsLeft = prefabCount - count
    #         timeLeft = (time.time() - prefabOptimizeStartTime) / count * prefabsLeft
    #         sys.stdout.write(f"  > {count} ({round(count/prefabCount*100)}%)... eta: {round(timeLeft, 1)}s   \r")
    #         
    # sys.stdout.write(f"  > {count} ({round(count/prefabCount*100)}%)... done!                    \n")
    # sys.stdout.write(f"   > Removed {removedCurves} curves.\n")

    sys.stdout.write(f" > Optimizing prefab array...\r")
    
    for prefab in prefabs:
        token = str(prefab.Token)[:3]
        if token not in optimizedPrefabs:
            optimizedPrefabs[token] = []
        optimizedPrefabs[token].append(prefab)
    
    sys.stdout.write(f" > Optimizing prefab array... done!\n")
    
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