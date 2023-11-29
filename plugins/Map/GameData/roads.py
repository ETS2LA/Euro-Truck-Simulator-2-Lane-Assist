import json
from src.logger import print
from src.variables import *
from src.settings import *
from src.helpers import *
from src.mainUI import *
import src.mainUI as mainUI
import sys
import plugins.Map.GameData.nodes as nodes
import math

class Road():
    Uid = 0
    StartNodeUid = 0
    StartNode = None
    EndNodeUid = 0
    EndNode = None
    Nodes = None
    BlockSize = 0
    Valid = False
    Type = 0
    X = 0
    Z = 0
    Hidden = False
    Flags = 0
    Navigation = None
    RoadLook = None
    Points = None
    IsSecret = False
    ConnectedPrefabItems = []

class RoadLook():
    offset = 0.0
    lanesLeft = []
    lanesRight = []
    token = 0
    isHighway = False
    isLocal = False
    isExpress = False
    isNoVehicles = False


roads = []
optimizedRoads = {}
uidOptimizedRoads = {}
roadFileName = variables.PATH + "/plugins/Map/GameData/roads.json"

roadsMaxX = 0
roadsMaxZ = 0
roadsMinX = 0
roadsMinZ = 0
totalWidth = 0
totalHeight = 0
areaCountX = 0
areaCountZ = 0

limitToCount = 0

def RoadToJson(road):
    roadJson = {}
    
    roadJson["Uid"] = road.Uid
    roadJson["StartNodeUid"] = road.StartNodeUid
    roadJson["EndNodeUid"] = road.EndNodeUid
    roadJson["Nodes"] = road.Nodes
    roadJson["BlockSize"] = road.BlockSize
    roadJson["Valid"] = road.Valid
    roadJson["Type"] = road.Type
    roadJson["X"] = road.X
    roadJson["Z"] = road.Z
    roadJson["Hidden"] = road.Hidden
    roadJson["Flags"] = road.Flags
    roadJson["Navigation"] = road.Navigation
    roadJson["Points"] = []
    try:
        for point in road.Points:
            # A point is a tuple of (x, z)
            point = {
                "X": point[0],
                "Z": point[1]
            }
            roadJson["Points"].append(point)
    except:
        pass
    roadJson["IsSecret"] = road.IsSecret
    
    roadJson["RoadLook"] = {}
    roadJson["RoadLook"]["Offset"] = road.RoadLook.offset
    roadJson["RoadLook"]["LanesLeft"] = road.RoadLook.lanesLeft
    roadJson["RoadLook"]["LanesRight"] = road.RoadLook.lanesRight
    roadJson["RoadLook"]["Token"] = road.RoadLook.token
    roadJson["RoadLook"]["IsHighway"] = road.RoadLook.isHighway
    roadJson["RoadLook"]["IsLocal"] = road.RoadLook.isLocal
    roadJson["RoadLook"]["IsExpress"] = road.RoadLook.isExpress
    roadJson["RoadLook"]["IsNoVehicles"] = road.RoadLook.isNoVehicles
    
    return roadJson

def Hermite(s, x, z, tanX, tanZ):
    h1 = 2 * math.pow(s, 3) - 3 * math.pow(s, 2) + 1
    h2 = -2 * math.pow(s, 3) + 3 * math.pow(s, 2)
    h3 = math.pow(s, 3) - 2 * math.pow(s, 2) + s
    h4 = math.pow(s, 3) - math.pow(s, 2)
    return h1 * x + h2 * z + h3 * tanX + h4 * tanZ

def CreatePointsForRoad(road):
    # All this code is copied from the original C# implementation of point calculations
    # ts-map-lane-assist/TsMap/TsMapRenderer.cs -> 473 (after foreach(var road in _mapper.Roads))
    newPoints = []

    sx = road.StartNode.X
    sz = road.StartNode.Z
    ex = road.EndNode.X
    ez = road.EndNode.Z

    radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))

    tanSx = math.cos(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEx = math.cos(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius
    tanSz = math.sin(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEz = math.sin(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius

    for i in range(8):
        s = i / (8 - 1)
        x = Hermite(s, sx, ex, tanSx, tanEx)
        z = Hermite(s, sz, ez, tanSz, tanEz)
        newPoints.append((x, z))

    road.Points = newPoints

def LoadRoads():
    global roadsMaxX
    global roadsMaxZ
    global roadsMinX
    global roadsMinZ
    global totalWidth
    global totalHeight
    global areaCountX
    global areaCountZ
    global roads
    global optimizedRoads
    
    if nodes.nodes == []:
        nodes.LoadNodes()
    
    jsonData = json.load(open(roadFileName))
    
    data = {
        "state": f"Loading roads...",
        "stateProgress": 100,
        "totalProgress": 25
    }
    mainUI.ui.update(data)
    mainUI.root.update()
    
    count = 0
    for road in jsonData:
        road = jsonData[road]
        
        roadObj = Road()
        roadObj.Uid = road["Uid"]
        roadObj.StartNodeUid = road["StartNodeUid"]
        roadObj.EndNodeUid = road["EndNodeUid"]
        roadObj.Nodes = road["Nodes"]
        roadObj.BlockSize = road["BlockSize"]
        roadObj.Valid = road["Valid"]
        roadObj.Type = road["Type"]
        roadObj.X = road["X"]
        roadObj.Z = road["Z"]
        roadObj.Hidden = road["Hidden"]
        roadObj.Flags = road["Flags"]
        roadObj.Navigation = road["Navigation"]
        roadObj.Points = road["Points"]
        roadObj.IsSecret = road["IsSecret"]
    
        roadObj.RoadLook = RoadLook()
        
        roadObj.RoadLook.offset = road["RoadLook"]["Offset"]
        roadObj.RoadLook.lanesLeft = road["RoadLook"]["LanesLeft"]
        roadObj.RoadLook.lanesRight = road["RoadLook"]["LanesRight"]
        roadObj.RoadLook.token = road["RoadLook"]["Token"]
        roadObj.RoadLook.isHighway = road["RoadLook"]["IsHighway"]
        roadObj.RoadLook.isLocal = road["RoadLook"]["IsLocal"]
        roadObj.RoadLook.isExpress = road["RoadLook"]["IsExpress"]
        roadObj.RoadLook.isNoVehicles = road["RoadLook"]["IsNoVehicles"]
    
        roads.append(roadObj)
        count += 1
    
        if limitToCount != 0 and count >= limitToCount:
            break
    
    sys.stdout.write(f"Loaded roads : {count}\nNow matching roads to nodes...\n")
    
    # Match the nodes to the roads
    count = 0
    noLocationData = 0
    for road in roads:
        road.StartNode = nodes.GetNodeByUid(road.StartNodeUid)
        road.EndNode = nodes.GetNodeByUid(road.EndNodeUid)
        
        if road.StartNode == None or road.EndNode == None:
            noLocationData += 1
        
        count += 1
        if count % 1000 == 0:
            sys.stdout.write(f"Matched roads : {count}\r")
            data = {
                "state": f"Matching roads to nodes... {round(count/len(roads) * 100)}%",
                "stateProgress": count/len(roads) * 100,
                "totalProgress": 25 + (count/len(roads) * 25)
            }
            mainUI.ui.update(data)
            mainUI.root.update()
    
    sys.stdout.write(f"Matched roads : {count}\nRoads with invalid location data : {noLocationData}\nNow optimizing array...\n")
    
    
    # Make an optimized array for the roads. Do this by splitting the map into 1km / 1km areas and then adding the roads to the correct area
    data = {
        "state": f"Optimizing array...",
        "stateProgress": 100,
        "totalProgress": 50
    }
    mainUI.ui.update(data)
    mainUI.root.update()
    
    for road in roads:
        if road.StartNode.X > roadsMaxX:
            roadsMaxX = road.StartNode.X
        if road.StartNode.Z > roadsMaxZ:
            roadsMaxZ = road.StartNode.Z
        if road.StartNode.X < roadsMinX:
            roadsMinX = road.StartNode.X
        if road.StartNode.Z < roadsMinZ:
            roadsMinZ = road.StartNode.Z
        
        if road.EndNode.X > roadsMaxX:
            roadsMaxX = road.EndNode.X
        if road.EndNode.Z > roadsMaxZ:
            roadsMaxZ = road.EndNode.Z
        if road.EndNode.X < roadsMinX:
            roadsMinX = road.EndNode.X
        if road.EndNode.Z < roadsMinZ:
            roadsMinZ = road.EndNode.Z
            
    totalWidth = roadsMaxX - roadsMinX
    totalHeight = roadsMaxZ - roadsMinZ
    
    # Make the array 1km / 1km
    totalWidth = math.ceil(totalWidth / 1000)
    totalHeight = math.ceil(totalHeight / 1000)
        
    for road in roads:
        # Get the area the road should be in from the START node
        x = math.floor((road.StartNode.X - roadsMinX) / 1000)
        z = math.floor((road.StartNode.Z - roadsMinZ) / 1000)
        
        if x > areaCountX:
            areaCountX = x
        if z > areaCountZ:
            areaCountZ = z
        
        if x not in optimizedRoads:
            optimizedRoads[x] = {}
        if z not in optimizedRoads[x]:
            optimizedRoads[x][z] = []
        
        optimizedRoads[x][z].append(road)
        
    print(f"Roads optimized to {areaCountX}x{areaCountZ} areas")
        
    # Optimize roads by the three first numbers of the UID
    for road in roads:
        uid = str(road.Uid)
        uid = uid[:3]
        uid = int(uid)
        
        if uid not in uidOptimizedRoads:
            uidOptimizedRoads[uid] = []
            
        uidOptimizedRoads[uid].append(road)
        
    print("Road parsing done!")


def GetRoadsInTileByCoordinates(x, z):
    # Convert the global coordinates to tile coordinates
    x = math.floor((x - roadsMinX) / 1000)
    z = math.floor((z - roadsMinZ) / 1000)
    
    if x in optimizedRoads:
        if z in optimizedRoads[x]:
            areaRoads = optimizedRoads[x][z].copy()
            return areaRoads
    
    return []

def GetTileCoordinates(x, z):
    x = math.floor((x - roadsMinX) / 1000)
    z = math.floor((z - roadsMinZ) / 1000)
    
    return x, z

def GetLocalCoordinateInTile(x, y, tileX=-1, tileY=-1):
    if tileX == -1 or tileY == -1:
        tileX = math.floor((x - roadsMinX) / 1000)
        tileY = math.floor((y - roadsMinZ) / 1000)
        
    x = x - (tileX * 1000) - roadsMinX
    y = y - (tileY * 1000) - roadsMinZ
    
    return x, y

def GetRoadByUid(uid):
    for road in uidOptimizedRoads[int(str(uid)[:3])]:
        if road.Uid == uid:
            return road
    
    return None