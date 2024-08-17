from ETS2LA.variables import *
from ETS2LA.backend.settings import *

from ETS2LA.plugins.Map.GameData.calc import Hermite
import ETS2LA.plugins.Map.GameData.nodes as nodes

import sys
import logging
import json
import math

print = logging.info

ROAD_QUALITY = 0.25 # Points per meter
MIN_QUALITY = 2 # Need two points to make a line


from rich.progress import Task, Progress

# For loading nodes progress indicator
task: Task = None
progress: Progress = None

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
    
    def json(self):
        returnJson = {
            "Uid": str(self.Uid),
            "StartNodeUid": str(self.StartNodeUid),
            "EndNodeUid": str(self.EndNodeUid),
            "StartNode": self.StartNode.json(),
            "EndNode": self.EndNode.json(),
            "Nodes": self.Nodes,
            "BlockSize": self.BlockSize,
            "Valid": self.Valid,
            "Type": self.Type,
            "X": self.X,
            "Z": self.Z,
            "YValues": self.YValues,
            "Hidden": self.Hidden,
            "Flags": self.Flags,
            "Navigation": self.Navigation,
            "BoundingBox": self.BoundingBox,
            "RoadLook": self.RoadLook.json(),
            "Points": self.Points,
            "IsSecret": self.IsSecret,
            "ParallelPoints": self.ParallelPoints,
            "LaneWidth": self.LaneWidth,
        }
        return returnJson
        
    def fromJson(self, json):
        # Only load json the we also put out in the above function
        self.Uid = int(json["Uid"])
        self.StartNodeUid = int(json["StartNodeUid"])
        self.EndNodeUid = int(json["EndNodeUid"])
        self.StartNode = nodes.Node().fromJson(json["StartNode"])
        self.EndNode = nodes.Node().fromJson(json["EndNode"])
        self.Nodes = json["Nodes"]
        self.BlockSize = json["BlockSize"]
        self.Valid = json["Valid"]
        self.Type = json["Type"]
        self.X = json["X"]
        self.Z = json["Z"]
        self.YValues = json["YValues"]
        self.Hidden = json["Hidden"]
        self.Flags = json["Flags"]
        self.Navigation = json["Navigation"]
        self.BoundingBox = json["BoundingBox"]
        self.RoadLook = RoadLook().fromJson(json["RoadLook"])
        self.Points = json["Points"]
        self.IsSecret = json["IsSecret"]
        self.ParallelPoints = json["ParallelPoints"]
        self.LaneWidth = json["LaneWidth"]
        
        return self

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
    
    def json(self):
        return {
            "Name": self.name,
            "Offset": self.offset,
            "LanesLeft": self.lanesLeft,
            "LanesRight": self.lanesRight,
            "ShoulderSpaceLeft": self.shoulderSpaceLeft,
            "ShoulderSpaceRight": self.shoulderSpaceRight,
            "RoadSizeLeft": self.roadSizeLeft,
            "RoadSizeRight": self.roadSizeRight,
            "Token": self.token,
            "IsHighway": self.isHighway,
            "IsLocal": self.isLocal,
            "IsExpress": self.isExpress,
            "IsNoVehicles": self.isNoVehicles
        }
        
    def fromJson(self, json):
        self.name = json["Name"]
        self.offset = json["Offset"]
        self.lanesLeft = json["LanesLeft"]
        self.lanesRight = json["LanesRight"]
        self.shoulderSpaceLeft = json["ShoulderSpaceLeft"]
        self.shoulderSpaceRight = json["ShoulderSpaceRight"]
        self.roadSizeLeft = json["RoadSizeLeft"]
        self.roadSizeRight = json["RoadSizeRight"]
        self.token = json["Token"]
        self.isHighway = json["IsHighway"]
        self.isLocal = json["IsLocal"]
        self.isExpress = json["IsExpress"]
        self.isNoVehicles = json["IsNoVehicles"]
        
        return self

# https://stackoverflow.com/a/70377616
def set_nested_item(dataDict, mapList, val):
    """Set item in nested dictionary"""
    current_dict = dataDict
    for key in mapList[:-1]:
        current_dict = current_dict.setdefault(key, {})
    current_dict[mapList[-1]] = val
    return dataDict

def get_nested_item(dataDict, mapList):
    """Get item in nested dictionary"""
    for k in mapList:
        dataDict = dataDict[k]
    return dataDict


roads = []
"""
All roads in the game. 
WARNING: This array does not get updated, since it is so large. Please use the uidOptimizedRoads or optimizedRoads arrays instead.
"""

optimizedRoads = {}
uidOptimizedRoads = {}
roadFileName = PATH + "ETS2LA/plugins/Map/GameData/data/roads.json"

roadsMaxX = 0
roadsMaxZ = 0
roadsMinX = 0
roadsMinZ = 0
totalWidth = 0
totalHeight = 0
areaCountX = 0
areaCountZ = 0

limitToCount = 0

def CreatePointsForRoad(road):
    # All this code is copied from the original C# implementation of point calculations
    # ts-map-lane-assist/TsMap/TsMapRenderer.cs -> 473 (after foreach(var road in _mapper.Roads))
    newPoints = []

    road.YValues = [] # Clear the Y values

    sx = road.StartNode.X
    sy = road.StartNode.Y
    sz = road.StartNode.Z
    ex = road.EndNode.X
    ey = road.EndNode.Y
    ez = road.EndNode.Z
    
    # Get the length of the road
    length = math.sqrt(math.pow(sx - ex, 2) + math.pow(sy - ey, 2) + math.pow(sz - ez, 2))

    radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))

    tanSx = math.cos(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEx = math.cos(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius
    tanSz = math.sin(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEz = math.sin(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius

    neededPoints = int(length * ROAD_QUALITY)
    if neededPoints < MIN_QUALITY:
        neededPoints = MIN_QUALITY

    for i in range(neededPoints):
        s = i / (neededPoints - 1)
        x = Hermite(s, sx, ex, tanSx, tanEx)
        z = Hermite(s, sz, ez, tanSz, tanEz)
        newPoints.append((x, z))
        # Lerp the Y value between sy and ey
        y = sy + (ey - sy) * s
        road.YValues.append(y) # Add the Y value to the road but not to the points as they are 2D

    road.Points = newPoints
    
    return newPoints


def CreatePointForRoad(road, s):
    sx = road.StartNode.X
    sy = road.StartNode.Y
    sz = road.StartNode.Z
    ex = road.EndNode.X
    ey = road.EndNode.Y
    ez = road.EndNode.Z
    
    # Get the length of the road
    length = math.sqrt(math.pow(sx - ex, 2) + math.pow(sy - ey, 2) + math.pow(sz - ez, 2))

    radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))

    tanSx = math.cos(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEx = math.cos(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius
    tanSz = math.sin(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEz = math.sin(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius

    x = Hermite(s, sx, ex, tanSx, tanEx)
    z = Hermite(s, sz, ez, tanSz, tanEz)
    
    y = sy + (ey - sy) * s
    return (x, y, z)

# TODO: Make this make the lane points like the original road.
# Otherwise it's going to be very much wrong.
def CreatePointForLane(road, lane, s):
    sx = lane[0][0]
    try:
        sy = lane[0][2]
    except:
        sy = 0
    sz = lane[0][1]
    ex = lane[-1][0]
    try:
        ey = lane[-1][2]
    except:
        ey = 0
    ez = lane[-1][1]
    
    radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))

    tanSx = math.cos(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEx = math.cos(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius
    tanSz = math.sin(-(math.pi * 0.5 - road.StartNode.Rotation)) * radius
    tanEz = math.sin(-(math.pi * 0.5 - road.EndNode.Rotation)) * radius

    x = Hermite(s, sx, ex, tanSx, tanEx)
    z = Hermite(s, sz, ez, tanSz, tanEz)
    
    y = sy + (ey - sy) * s
    return (x, y, z)

def FindClosestPointOnHermiteCurve(px, py, pz, road, lane=None):
    def distance_to_point(s, lane=None):
        # Use the existing function or directly implement the Hermite curve equation here
        if lane == None:
            x, y, z = CreatePointForRoad(road, s)
        else:
            x, y, z = CreatePointForLane(road, lane, s)
            
        return math.sqrt((x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2)
    
    # Initialize the search range for s
    left, right = -0.1, 1.1
    tolerance = 1e-5  # Adjust the tolerance for more or less precision
    
    # Binary search for the minimum distance
    while right - left > tolerance:
        s1 = left + (right - left) / 3
        s2 = right - (right - left) / 3
        
        if distance_to_point(s1, lane=lane) < distance_to_point(s2, lane=lane):
            right = s2
        else:
            left = s1
    
    # Compute the final point using the optimized s
    s_optimized = (left + right) / 2
    if lane == None:
        closest_point = CreatePointForRoad(road, s_optimized)
    else:
        closest_point = CreatePointForLane(road, lane, s_optimized)
    
    return s_optimized, closest_point


# MARK: Roads to Nodes
def MatchRoadsToNodes():
    # Match the nodes to the roads
    progress.update(task, total=len(roads), description="[green]roads\n[/green][dim]solving dependencies...[/dim]")
    noLocationData = 0
    for road in roads:
        road.StartNode = nodes.GetNodeByUid(road.StartNodeUid)
        road.EndNode = nodes.GetNodeByUid(road.EndNodeUid)
        
        if road.StartNode == None or road.EndNode == None:
            noLocationData += 1
            
        progress.advance(task)
    
    if noLocationData > 0:
        progress.console.print(f" > Invalid location data for {noLocationData} roads!\n")

# MARK: Road Loading
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
    
    progress.update(task, description="[green]roads\n[/green][dim]reading JSON...[/dim]")
    
    if nodes.nodes == []:
        nodes.LoadNodes()
    
    jsonData = json.load(open(roadFileName))
    roadsInJson = len(jsonData)
    
    progress.update(task, total=roadsInJson, description="[green]roads\n[/green][dim]parsing...[/dim]", completed=0)
    
    count = 0
    # MARK: >> JSON Parse
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
        progress.advance(task)
 
        count += 1
        if limitToCount != 0 and count >= limitToCount:
            break
    
    del jsonData
    
    MatchRoadsToNodes()
    
    progress.update(task, total=len(roads), description="[green]roads\n[/green][dim]optimizing...[/dim]", completed=0)

    # MARK: >> Optimize
    # roadsMaxX etc... are global variables
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
        
    # sys.stdout.write(f" > Optimizing road array... done!\n")
    print(f"Roads optimized to {areaCountX}x{areaCountZ} areas")
        
    # Optimize roads by their IDs
    for road in roads:
        uid = str(road.Uid)
        uidParts = [uid[i:i+3] for i in range(0, len(uid), 3)]
        set_nested_item(uidOptimizedRoads, uidParts, road)
        
    progress.update(task, completed=progress._tasks[task].total, description="[green]roads[/green]")
        
    print("Road parsing done!")

# MARK: Road Getters
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
    if uid == 0:
        return None
    if uid == None:
        return None
    
    uidParts = [str(uid)[i:i+3] for i in range(0, len(str(uid)), 3)]
    try:
        road = get_nested_item(uidOptimizedRoads, uidParts)
        if road != None:
            return road
        sys.stdout.write(f" > Road not found in optimizedRoads, searching in roads...\n")
        for road in roads:
            if road.Uid == uid:
                return road
    except:
        sys.stdout.write(f" > Road not found in optimizedRoads, searching in roads...\n")
        for road in roads:
            if road.Uid == uid:
                return road
        
    return None

# MARK: Road Setters
def SetRoadParallelData(road, parallelPoints, laneWidth, boundingBox):
    # Find the road by the UID
    road = GetRoadByUid(road.Uid)
    if road == None: return # For some reason the road was not found...
    road.ParallelPoints = parallelPoints
    road.LaneWidth = laneWidth
    road.BoundingBox = boundingBox
            
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
    road = GetRoadByUid(road.Uid)
    road.Points = points
            
    # Get the area the road should be in from the START node
    x = math.floor((road.StartNode.X - roadsMinX) / 1000)
    z = math.floor((road.StartNode.Z - roadsMinZ) / 1000)
    
    # Update the optimized array
    for arrayRoad in optimizedRoads[x][z]:
        if arrayRoad.Uid == road.Uid:
            arrayRoad.Points = points

# MARK: Offset
import ETS2LA.plugins.Map.GameData.calc as calc
offsetData = { # Array of manual corrections to the offsets
    999: 4.5,
    0.0: 4.5
}
offsetPerName = {
    "Highway 2 lanes 5m offset" : 14.5,
    "Highway 2 lanes 2.5m offset" : 9.5,
    "Highway 2 lanes 2m offset" : 8.5,
    "Highway 2 lanes 1m offset" : 6.5,
    "Highway 2 lanes 10m offset" : 24.5,
    "Highway 3 lanes 2m offset" : 8.5,
    "Highway 3 lanes 5m offset" : 14.5,
    "balt hw 2 lanes 5m offset tmpl": 14.5,
}
offsetRules = {
    "***Road 2 city narrow": 6.5,
    "***Road 2 plus 1 temp": -11,
    "**road1 hw 1m offset tmpl": 8.5,
    "**road 2 narrow tmpl": 6.5,
    "**road 2 city narrow tmpl": 6.5,
    "**road 1 minim tmpl": 2.25,
    "**road 1 dirt minim tmpl": 2.25,
    "**road 1 minim village 1 tmpl": 2.25,
    "**road 1 plus 1 tmpl": 9.0,
    "**2 lanes 1m offset": 6.5,
    "**r2 tram": 2.25,
}

def GetOffset(road):
    # Fix 999 and 0.0 offsets
    name = road.RoadLook.name.replace("\"", "")
    
    # Check the rules
    rule_offset = 999
    for rule in offsetRules:
        rule = rule.replace("**", "")
        if rule in name:
            rule_offset = offsetRules["**" + rule]
    
    #print(f"Checking offset for {name}")
    if name in offsetPerName:
        custom_offset = offsetPerName[name]
        #print(f"Found offset for {name}: {custom_offset}")
    elif rule_offset != 999:
        custom_offset = rule_offset
    elif road.RoadLook.offset in offsetData: 
        custom_offset = offsetData[road.RoadLook.offset]
    else: 
        # Check if the road name has the offset in it
        if "m offset" in road.RoadLook.name:
            roadOffset = road.RoadLook.name.split("m offset")[0]
            roadOffset = float(roadOffset.split(" ")[-1])
        else:
            roadOffset = road.RoadLook.offset
        
        # NOTE: Superseded by the "tmpl" rule
        # Motorways use the offset as an addition... it's added to the existing 4.5m offset... we also have to add both sides of shoulders
        #if "traffic_lane.road.motorway" in road.RoadLook.lanesLeft or "traffic_lane.road.motorway" in road.RoadLook.lanesRight:
        #    custom_offset = 4.5 + road.RoadLook.offset
        #    custom_offset += (road.RoadLook.shoulderSpaceLeft + road.RoadLook.shoulderSpaceRight) / 2 / 2
        
        # If the name has "narrow" in it, then the offset is not added to 4.5
        # These roads also need to include the shoulder space... for whatever reason
        if "narrow" in road.RoadLook.name:
            custom_offset = roadOffset
            if road.RoadLook.shoulderSpaceLeft > 0: 
                custom_offset += road.RoadLook.shoulderSpaceLeft / 2
            if road.RoadLook.shoulderSpaceRight > 0:
                custom_offset += road.RoadLook.shoulderSpaceRight / 2
        
        # No offset means that the road only wants it's custom offset
        # IBE > -36910 , 47585
        elif "no offset" in road.RoadLook.name:
            custom_offset = 4.5
        
        # If the name has "tmpl" in it, then the offset is doubled
        elif "tmpl" in road.RoadLook.name:
            custom_offset = 4.5 + roadOffset * 2
        
        # Assume that the offset is actually correct
        else:
            custom_offset = 4.5 + roadOffset

    return custom_offset

# MARK: Parallel Curves
def CalculateParallelCurves(road):
    try:
        
        custom_offset = GetOffset(road)

        # Get the offset of the next road
        try:
            roadNext = road.EndNode.ForwardItem
            custom_offset_next = GetOffset(roadNext)
        except:
            custom_offset_next = custom_offset
            
        # Get the offset of the last road
        try:
            roadPrev = road.StartNode.BackwardItem
            custom_offset_prev = GetOffset(roadPrev)
        except:
            custom_offset_prev = custom_offset
            
        next_offset = custom_offset
        side = 0
        if custom_offset_next > custom_offset:
            next_offset = custom_offset_next
            side = 0
            
        elif custom_offset_prev > custom_offset:
            next_offset = custom_offset_prev
            side = 1

        lanes = calc.calculate_lanes(road.Points, 4.5, len(road.RoadLook.lanesLeft), len(road.RoadLook.lanesRight), custom_offset=custom_offset, next_offset=next_offset, side=side)
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
        import traceback
        traceback.print_exc()
        return [], [], 0