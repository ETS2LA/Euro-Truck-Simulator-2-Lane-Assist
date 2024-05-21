import json
import logging
print = logging.info
from ETS2LA.backend.variables import *
from ETS2LA.backend.settings import *
import sys
import GameData.nodes as nodes
import math

ROAD_QUALITY = 36

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
    YValues = []
    Hidden = False
    Flags = 0
    Navigation = None
    RoadLook = None
    Points = None
    IsSecret = False
    ConnectedPrefabItems = []
    ParallelPoints = []
    LaneWidth = 0
    BoundingBox = []

class RoadLook():
    name = ""
    offset = 0.0
    lanesLeft = []
    lanesRight = []
    shoulderSpaceLeft = 0
    shoulderSpaceRight = 0
    roadSizeLeft = 999
    roadSizeRight = 999
    token = 0
    isHighway = False
    isLocal = False
    isExpress = False
    isNoVehicles = False


roads = []
"""
All roads in the game. 
WARNING: This array does not get updated, since it is so large. Please use the uidOptimizedRoads or optimizedRoads arrays instead.
"""

optimizedRoads = {}
uidOptimizedRoads = {}
roadFileName = PATH + "ETS2LA/plugins/Map/GameData/roads.json"

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
    roadJson["RoadLook"]["Name"] = road.RoadLook.name
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
    sy = road.StartNode.Y
    sz = road.StartNode.Z
    ex = road.EndNode.X
    ey = road.EndNode.Y
    ez = road.EndNode.Z

    radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))

    tanSx = math.cos(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEx = math.cos(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius
    tanSz = math.sin(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEz = math.sin(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius

    for i in range(ROAD_QUALITY):
        s = i / (ROAD_QUALITY - 1)
        x = Hermite(s, sx, ex, tanSx, tanEx)
        z = Hermite(s, sz, ez, tanSz, tanEz)
        newPoints.append((x, z))
        # Lerp the Y value between sy and ey
        y = sy + (ey - sy) * s
        road.YValues.append(y) # Add the Y value to the road but not to the points as they are 2D

    road.Points = newPoints
    
    return newPoints

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
    roadsInJson = len(jsonData)
    
    sys.stdout.write(f"\nLoading {len(jsonData)} roads...\n")
    
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
        
        roadObj.RoadLook.name = road["RoadLook"]["Name"]
        roadObj.RoadLook.offset = road["RoadLook"]["Offset"]
        roadObj.RoadLook.lanesLeft = road["RoadLook"]["LanesLeft"]
        roadObj.RoadLook.lanesRight = road["RoadLook"]["LanesRight"]
        roadObj.RoadLook.token = road["RoadLook"]["Token"]
        roadObj.RoadLook.isHighway = road["RoadLook"]["IsHighway"]
        roadObj.RoadLook.isLocal = road["RoadLook"]["IsLocal"]
        roadObj.RoadLook.isExpress = road["RoadLook"]["IsExpress"]
        roadObj.RoadLook.isNoVehicles = road["RoadLook"]["IsNoVehicles"]
        roadObj.RoadLook.shoulderSpaceLeft = road["RoadLook"]["ShoulderSpaceLeft"]
        roadObj.RoadLook.shoulderSpaceRight = road["RoadLook"]["ShoulderSpaceRight"]
        roadObj.RoadLook.roadSizeLeft = road["RoadLook"]["RoadSizeLeft"]
        roadObj.RoadLook.roadSizeRight = road["RoadLook"]["RoadSizeRight"]
    
        roads.append(roadObj)
        count += 1
    
        if count % 1000 == 0:
            sys.stdout.write(f" > {count} ({round(count/roadsInJson * 100)}%)...\r")
    
        if limitToCount != 0 and count >= limitToCount:
            break
    
    sys.stdout.write(f" > {count} ({round(count/roadsInJson * 100)}%)... done!\n")
    sys.stdout.write(f" > Matching roads to nodes...\n")
    
    # Match the nodes to the roads
    count = 0
    noLocationData = 0
    roadsCount = len(roads)
    matchStartTime = time.time()
    for road in roads:
        road.StartNode = nodes.GetNodeByUid(road.StartNodeUid)
        road.EndNode = nodes.GetNodeByUid(road.EndNodeUid)
        
        if road.StartNode == None or road.EndNode == None:
            noLocationData += 1
        
        count += 1
        if count % 1000 == 0:
            roadsLeft = roadsCount - count
            timeLeft = (time.time() - matchStartTime) / count * roadsLeft
            sys.stdout.write(f"  > {count} ({round(count/roadsCount * 100)}%)... eta: {round(timeLeft, 1)}s    \r")
    
    # sys.stdout.write(f"Matched roads : {count}\nRoads with invalid location data : {noLocationData}\nNow optimizing array...\n")
    sys.stdout.write(f"  > {count} ({round(count/roadsCount * 100)}%)... done!                   \n")
    sys.stdout.write(f"   > Invalid location data : {noLocationData}\n")

    sys.stdout.write(f" > Optimizing road array...\r")
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
        
    sys.stdout.write(f" > Optimizing road array... done!\n")
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

def SetRoadParallelData(road, parallelPoints, laneWidth, boundingBox):
    # Find the road by the UID
    for arrayRoad in uidOptimizedRoads[int(str(road.Uid)[:3])]:
        if arrayRoad.Uid == road.Uid:
            arrayRoad.ParallelPoints = parallelPoints
            arrayRoad.LaneWidth = laneWidth
            arrayRoad.BoundingBox = boundingBox
            
    # Get the area the road should be in from the START node
    x = math.floor((road.StartNode.X - roadsMinX) / 1000)
    z = math.floor((road.StartNode.Z - roadsMinZ) / 1000)
    
    # Update the optimized array
    for arrayRoad in optimizedRoads[x][z]:
        if arrayRoad.Uid == road.Uid:
            arrayRoad.ParallelPoints = parallelPoints
            arrayRoad.LaneWidth = laneWidth
            arrayRoad.BoundingBox = boundingBox
    

def SetRoadPoints(road, points):
    # Find the road by the UID
    for arrayRoad in uidOptimizedRoads[int(str(road.Uid)[:3])]:
        if arrayRoad.Uid == road.Uid:
            arrayRoad.Points = points
            
    # Get the area the road should be in from the START node
    x = math.floor((road.StartNode.X - roadsMinX) / 1000)
    z = math.floor((road.StartNode.Z - roadsMinZ) / 1000)
    
    # Update the optimized array
    for arrayRoad in optimizedRoads[x][z]:
        if arrayRoad.Uid == road.Uid:
            arrayRoad.Points = points

import GameData.calc as calc
offsetData = { # Array of manual corrections to the offsets
    5.75: 5.75,
    999: 0,
    0.0: 4.5
}
offsetPerName = {
    "\"ger road 1 tmpl\"": 4.5,
    "\"invis road\"" : 4.5,
    "\"balt road 1 tmpl\"" : 4.5,
    "\"*Road 1 scan temp\"" : 4.5,
}
def CalculateParallelCurves(road):
    try:
        if road.RoadLook.offset in offsetData: 
            custom_offset = offsetData[road.RoadLook.offset]
        else: custom_offset = 999
        if road.RoadLook.name in offsetPerName:
            custom_offset = offsetPerName[road.RoadLook.name]

        lanes = calc.calculate_lanes(road.Points, 4.5, len(road.RoadLook.lanesLeft), len(road.RoadLook.lanesRight), custom_offset=custom_offset)
        newPoints = lanes['left'] + lanes['right']
        
        boundingBox = [[999999, 999999], [-999999, -999999]]
        for lane in newPoints:
            for point in lane:
                if point[0] < boundingBox[0][0]:
                    boundingBox[0][0] = point[0]
                if point[0] > boundingBox[1][0]:
                    boundingBox[1][0] = point[0]
                if point[1] < boundingBox[0][1]:
                    boundingBox[0][1] = point[1]
                if point[1] > boundingBox[1][1]:
                    boundingBox[1][1] = point[1]
        # Add 5m of padding
        boundingBox[0][0] -= 5
        boundingBox[0][1] -= 5
        boundingBox[1][0] += 5
        boundingBox[1][1] += 5            
        
        return boundingBox, newPoints, 4.5
    
    except:
        return [], [], 0