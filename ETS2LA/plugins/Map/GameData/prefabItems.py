from ETS2LA.backend.settings import *
from ETS2LA.variables import *

import ETS2LA.plugins.Map.GameData.prefabs as prefabs
from ETS2LA.plugins.Map.GameData.calc import Hermite
import ETS2LA.plugins.Map.GameData.roads as roads
import ETS2LA.plugins.Map.GameData.nodes as nodes
import ETS2LA.plugins.Map.GameData.calc as calc

import logging
import json
import math
import sys


uidOptimizedPrefabItems = {}
optimizedPrefabItems = {}
prefabItems = []

print = logging.info

prefabItemsFileName = PATH + "ETS2LA/plugins/Map/GameData/data/prefab_items.json"

itemsMinX = 0
itemsMaxX = 0
itemsMinZ = 0
itemsMaxZ = 0

itemsTotalHeight = 0
itemsTotalWidth = 0
itemsAreaCountX = 0
itemsAreaCountZ = 0

from rich.progress import Task, Progress

# For loading nodes progress indicator
task: Task = None
progress: Progress = None

# MARK: Classes
class PrefabItem:
    Uid = 0
    StartNodeUid = 0
    EndNodeUid = 0
    StartNode = None
    EndNode = None
    Nodes = []
    BlockSize = 0
    Valid = False
    Type = 0
    X = 0
    Y = 0
    Z = 0
    Hidden = False
    Flags = 0
    Navigation = []
    Origin = 0
    Padding = 0
    Prefab = None
    NavigationLanes = []
    LaneStartPoints = []
    LaneEndPoints = []
    IsSecret = False
    _CurvePoints = [[]]
    EndPoints = []
    BoundingBox = []
    FerryUid = 0
    
    @property
    def CurvePoints(self):
        try:
            self.getPoints()
        except:
            logging.exception("Error getting curvepoints for prefab item: " + str(self.Uid))
        return self._CurvePoints

    @CurvePoints.setter
    def CurvePoints(self, value):
        self._CurvePoints = value

    def getPoints(self):
        if self._CurvePoints is not None and self._CurvePoints != [[]] and len(self._CurvePoints) > 0:
            return self._CurvePoints  # Already processed
    
        if self.Prefab == None or self.Nodes == None or len(self.Nodes) == 0:
            return self._CurvePoints  # Some don't have a prefab or nodes
    
        originNode = self.Nodes[0]
        
        if type(self.Prefab) == int:
            self.Prefab = prefabs.GetPrefabByToken(self.Prefab)
        if self.Prefab == None:
            return self._CurvePoints
        
        try:
            if type(originNode) == dict:
                originNode = nodes.Node().fromJson(originNode)
        
            mapPointOrigin = self.Prefab.PrefabNodes[self.Origin]
    
            rot = float(originNode.Rotation - math.pi -
                math.atan2(mapPointOrigin.RotZ, mapPointOrigin.RotX) + math.pi / 2)
        except:
            return self._CurvePoints
        
        prefabStartX = originNode.X - mapPointOrigin.X
        prefabStartZ = originNode.Z - mapPointOrigin.Z
        prefabStartY = originNode.Y - mapPointOrigin.Y

        tempPoints = []
    
        for i, lane in enumerate(self.Prefab.PrefabLanes):
            tempPoints.append([])  # Adding a new list for each lane
            if len(lane.Curves) < 4:
                for k in range(len(lane.Curves)):
                    #if len(self.Nodes) == 2:
                    curveStartPoint = calc.RotatePoint(prefabStartX + lane.Curves[k].startX, prefabStartZ + lane.Curves[k].startZ, rot, originNode.X, originNode.Z)
                    curveEndPoint = calc.RotatePoint(prefabStartX + lane.Curves[k].endX, prefabStartZ + lane.Curves[k].endZ, rot, originNode.X, originNode.Z)
                    
                    StartNode = None
                    StartNodeDistance = math.inf
                    EndNode = None
                    EndNodeDistance = math.inf
                    for node in self.Nodes:
                        distance = math.sqrt(math.pow(node.X - curveStartPoint[0], 2) + math.pow(node.Z - curveStartPoint[1], 2))
                        if distance < StartNodeDistance:
                            StartNodeDistance = distance
                            StartNode = node
                        distance = math.sqrt(math.pow(node.X - curveEndPoint[0], 2) + math.pow(node.Z - curveEndPoint[1], 2))
                        if distance < EndNodeDistance:
                            EndNodeDistance = distance
                            EndNode = node
                    
                    sx = curveStartPoint[0]
                    sz = curveStartPoint[1]
                    sy = lane.Curves[k].startY + prefabStartY
                    ex = curveEndPoint[0]
                    ez = curveEndPoint[1]
                    ey = lane.Curves[k].endY + prefabStartY
                    
                    radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))

                    tanSx = math.cos(-(math.pi * 0.5 - StartNode.Rotation)) * radius
                    tanEx = math.cos(-(math.pi * 0.5 - EndNode.Rotation)) * radius
                    tanSz = math.sin(-(math.pi * 0.5 - StartNode.Rotation)) * radius
                    tanEz = math.sin(-(math.pi * 0.5 - EndNode.Rotation)) * radius
                    
                    resolution = 10
                    
                    for j in range(resolution):
                        s = j / (resolution - 1)
                        x = Hermite(s, sx, ex, tanSx, tanEx)
                        z = Hermite(s, sz, ez, tanSz, tanEz)
                        #rotatedPoint = calc.RotatePoint(x, z, rot, originNode.X, originNode.Z)
                        tempPoints[i].append((x, z, sy + (ey - sy) * s))
                    
                    #else:
                    #    curveStartPoint = calc.RotatePoint(prefabStartX + lane.Curves[k].startX, prefabStartZ + lane.Curves[k].startZ, rot, originNode.X, originNode.Z)
                    #    curveEndPoint = calc.RotatePoint(prefabStartX + lane.Curves[k].endX, prefabStartZ + lane.Curves[k].endZ, rot, originNode.X, originNode.Z)
                    #    tempPoints[i].append((curveStartPoint[0], curveStartPoint[1], lane.Curves[k].startY + prefabStartY))
                    #    tempPoints[i].append((curveEndPoint[0], curveEndPoint[1], lane.Curves[k].endY + prefabStartY))
            else:
                for j in range(len(lane.Curves)):
                    #logging.warning("Processing lanepoint: " + str(j))
                    if j == 0:
                        curveStartPoint = calc.RotatePoint(prefabStartX + lane.Curves[j].startX, prefabStartZ + lane.Curves[j].startZ, rot, originNode.X, originNode.Z)
                        tempPoints[i].append((curveStartPoint[0], curveStartPoint[1], lane.Curves[j].startY + prefabStartY))
                    elif j == len(lane.Curves) - 1:
                        curveEndPoint = calc.RotatePoint(prefabStartX + lane.Curves[j].endX, prefabStartZ + lane.Curves[j].endZ, rot, originNode.X, originNode.Z)
                        tempPoints[i].append((curveEndPoint[0], curveEndPoint[1], lane.Curves[j].endY + prefabStartY))
                    else:
                        p0 = lane.Curves[j - 1]
                        p1 = lane.Curves[j]
                        p2 = lane.Curves[j + 1] if j < len(lane.Curves) - 1 else lane.Curves[j]
                        p3 = lane.Curves[j + 2] if j < len(lane.Curves) - 2 else lane.Curves[j]
    
                        for t in [x * 0.05 for x in range(20)]:  # Generates values from 0 to 1 inclusive in steps of 0.05
                            #logging.warning("Processing curvepoint: " + str(t))
                            x = 0.5 * ((2 * p1.startX) +
                                       (-p0.startX + p2.startX) * t +
                                       (2 * p0.startX - 5 * p1.startX + 4 * p2.startX - p3.startX) * t**2 +
                                       (-p0.startX + 3 * p1.startX - 3 * p2.startX + p3.startX) * t**3)
    
                            z = 0.5 * ((2 * p1.startZ) +
                                       (-p0.startZ + p2.startZ) * t +
                                       (2 * p0.startZ - 5 * p1.startZ + 4 * p2.startZ - p3.startZ) * t**2 +
                                       (-p0.startZ + 3 * p1.startZ - 3 * p2.startZ + p3.startZ) * t**3)
                            
                            y = 0.5 * ((2 * p1.startY) +
                                       (-p0.startY + p2.startY) * t +
                                       (2 * p0.startY - 5 * p1.startY + 4 * p2.startY - p3.startY) * t**2 +
                                       (-p0.startY + 3 * p1.startY - 3 * p2.startY + p3.startY) * t**3)
    
                            rotatedPoint = calc.RotatePoint(prefabStartX + x, prefabStartZ + z, rot, originNode.X, originNode.Z)
                            #rotatedPoint = calc.RotatePoint3D(prefabStartX + x, y, prefabStartZ + z, 0, 0, 0, originNode.X, originNode.Y, originNode.Z)
                            
                            tempPoints[i].append((rotatedPoint[0], rotatedPoint[1], y + prefabStartY))
    
            LaneStartPoint = calc.RotatePoint(prefabStartX + lane.StartX, prefabStartZ + lane.StartZ, rot, originNode.X, originNode.Z)
            LaneEndPoint = calc.RotatePoint(prefabStartX + lane.EndX, prefabStartZ + lane.EndZ, rot, originNode.X, originNode.Z)
            self.LaneStartPoints.append((LaneStartPoint[0], LaneStartPoint[1], lane.StartY + prefabStartY))
            self.LaneEndPoints.append((LaneEndPoint[0], LaneEndPoint[1], lane.EndY + prefabStartY))
    
        self.CurvePoints = tempPoints
    
    def json(self):
        return {
            "Uid": self.Uid,
            "StartNodeUid": self.StartNodeUid,
            "EndNodeUid": self.EndNodeUid,
            "StartNode": self.StartNode.json() if self.StartNode != None and type(self.StartNode) != int else self.StartNode,
            "EndNode": self.EndNode.json() if self.EndNode != None and type(self.EndNode) != int else self.EndNode,
            "Nodes": [node.json() if type(node) != dict else node for node in self.Nodes],
            "BlockSize": self.BlockSize,
            "Valid": self.Valid,
            "Type": self.Type,
            "X": self.X,
            "Y": self.Y,
            "Z": self.Z,
            "Hidden": self.Hidden,
            "Flags": self.Flags,
            "Navigation": [nav.json() if type(nav) != dict else nav for nav in self.Navigation],
            "Origin": self.Origin,
            "Padding": self.Padding,
            "Prefab": self.Prefab.Token if self.Prefab != None and type(self.Prefab) != int else self.Prefab,
            "NavigationLanes": self.NavigationLanes,
            "IsSecret": self.IsSecret,
            "CurvePoints": self._CurvePoints,
            "EndPoints": self.EndPoints,
            "BoundingBox": self.BoundingBox
        }
        
    def fromJson(self, json):
        self.Uid = json["Uid"]
        self.StartNodeUid = json["StartNodeUid"]
        self.EndNodeUid = json["EndNodeUid"]
        self.StartNode = json["StartNodeUid"] # nodes.GetNodeByUid(json["StartNodeUid"])
        self.EndNode = json["EndNodeUid"] # nodes.GetNodeByUid(json["EndNodeUid"])
        try:
            self.Nodes = json["Nodes"] # [nodes.GetNodeByUid(node) for node in json["Nodes"]]
        except: self.Nodes = []
        self.BlockSize = json["BlockSize"]
        self.Valid = json["Valid"]
        self.Type = json["Type"]
        self.X = json["X"]
        self.Y = json["Y"]
        self.Z = json["Z"]
        self.Hidden = json["Hidden"]
        self.Flags = json["Flags"]
        self.Navigation = json["Navigation"]
        self.Origin = json["Origin"]
        self.Padding = json["Padding"]
        try:
            self.Prefab = json["Prefab"] # prefabs.GetPrefabByToken(json["Prefab"])
        except: self.Prefab = None
        self.NavigationLanes = json["NavigationLanes"]
        self.IsSecret = json["IsSecret"]
        self._CurvePoints = json["CurvePoints"]
        self.EndPoints = json["EndPoints"]
        self.BoundingBox = json["BoundingBox"]
        
        return self
    
class NavigationItem2:
    Uid = 0
    Type = ""
    
    def json(self):
        return {
            "Uid": self.Uid,
            "Type": self.Type
        }
    
class Navigation:
    NavId = 0
    Item1 = 0
    Item2 = []
    
    def json(self):
        return {
            "NavId": self.NavId,
            "Item1": self.Item1,
            "Item2": [item.json() for item in self.Item2]
        }
    
# MARK: Load Items
def LoadPrefabItems():
    global prefabItems
    global optimizedPrefabItems
    global itemsMinX
    global itemsMaxX
    global itemsMinZ
    global itemsMaxZ
    global itemsTotalWidth
    global itemsTotalHeight
    global itemsAreaCountX
    global itemsAreaCountZ
    
    jsonData = json.load(open(prefabItemsFileName))
    jsonLength = len(jsonData)
    
    progress.update(task, total=jsonLength, description="[green]prefabs\n[/green][dim]reading JSON...[/dim]")
    
    # sys.stdout.write(f"\nLoading {jsonLength} prefab items...\n")
    # MARK: >> Parse JSON
    count = 0
    for item in jsonData:
        item = jsonData[item]
        
        itemObj = PrefabItem()
        itemObj.Uid = item["Uid"]
        itemObj.StartNodeUid = item["StartNodeUid"]
        itemObj.EndNodeUid = item["EndNodeUid"]
        
        itemObj.Nodes = []
        for node in item["Nodes"]:
            itemObj.Nodes.append(nodes.GetNodeByUid(node))
        
        itemObj.BlockSize = item["BlockSize"]
        itemObj.Valid = item["Valid"]
        itemObj.Type = item["Type"]
        itemObj.X = item["X"]
        itemObj.Y = item["Y"]
        itemObj.Z = item["Z"]
        itemObj.Hidden = item["Hidden"]
        itemObj.Flags = item["Flags"]
        
        itemObj.Navigation = []
        for nav in item["Navigation"]:
            navObj = Navigation()
            navId = nav
            nav = item["Navigation"][nav]
            navObj.NavId = navId
            navObj.Item1 = nav["Item1"]
            navObj.Item2 = []
            for item2 in nav["Item2"]:
                item2Obj = NavigationItem2()
                item2Obj.Uid = item2["Uid"]
                item2Obj.Type = item2["Type"]
                navObj.Item2.append(item2Obj)
                
            itemObj.Navigation.append(navObj)
            navObj = None
            
        itemObj.Origin = item["Origin"]
        itemObj.Padding = item["Padding"]
        itemObj.Prefab = item["Prefab"]
        itemObj.IsSecret = item["IsSecret"]
        itemObj.FerryUid = item["FerryUid"]
        #itemObj.CurvePoints = item["curvePoints"]
        
        if itemObj.Valid:
            prefabItems.append(itemObj)
        
        count += 1
        
        progress.advance(task)
        
        if count % int(jsonLength/100) == 0:
            progress.refresh()
            # sys.stdout.write(f" > {count} ({round(count/jsonLength*100)}%)...\r")
    
    # sys.stdout.write(f" > {count} ({round(count/jsonLength*100)}%)... done!\n")
    count = 0
    
    
    # TODO: FIX THIS CODE
    # Original C# code in TsMapRenderer.cs -> lines 393-417
    # MARK: >> Match
    
    prefabItemCount = len(prefabItems)
    
    progress.update(task, total=prefabItemCount, description="[green]prefabs\n[/green][dim]solving dependencies...[/dim]", completed=0)
    # sys.stdout.write(f" > Matching prefabs and prefab items...\n")
    prefabItemMatchStartTime = time.time()
    for prefabItem in prefabItems:
        prefabItem.Prefab = prefabs.GetPrefabByToken(prefabItem.Prefab)
        if prefabItem.Prefab == None:
            logging.warning(f"Prefab item {prefabItem.Uid} has no prefab!")
        
        prefabItem.StartNode = nodes.GetNodeByUid(prefabItem.StartNodeUid)
        prefabItem.EndNode = nodes.GetNodeByUid(prefabItem.EndNodeUid)
        
        originNode = prefabItem.Nodes[0]
        try:
            mapPointOrigin = prefabItem.Prefab.PrefabNodes[prefabItem.Origin]
        except:
            pass

        # MARK: >>> Get curves
        
        prefabStartX = originNode.X - mapPointOrigin.X
        prefabStartZ = originNode.Z - mapPointOrigin.Z
        
        prefabItem.X = prefabStartX
        prefabItem.Z = prefabStartZ
        
        #prefabItem.NavigationLanes = []
        #for curvePoints in prefabItem.CurvePoints:
        #    curveStartX = curvePoints[0]
        #    curveStartZ = curvePoints[1]
        #    curveEndX = curvePoints[2]
        #    curveEndZ = curvePoints[3]
        #    
        #    prefabItem.NavigationLanes.append((curveStartX, curveStartZ, curveEndX, curveEndZ))
            

        for nav in prefabItem.Navigation:
            for item in nav.Item2:
                if item.Type == "Road":
                    try:
                        road = roads.GetRoadByUid(item.Uid)
                    except:
                        road = None
                        
                    if road != None:
                        road.ConnectedPrefabItems.append(prefabItem.Uid)
        
        
        # MARK: >>> Bounds
        
        # Calculate the bounding box of the prefab item
        minX = 1000000
        maxX = -1000000
        minZ = 1000000
        maxZ = -1000000
        for node in prefabItem.Nodes:
            if node.X < minX:
                minX = node.X
            if node.X > maxX:
                maxX = node.X
            if node.Z < minZ:
                minZ = node.Z
            if node.Z > maxZ:
                maxZ = node.Z
        
        # Add 5m of padding
        minX -= 5
        maxX += 5
        minZ -= 5
        maxZ += 5
        prefabItem.BoundingBox = [[minX, minZ], [maxX, maxZ]]
        
        count += 1
        if count % 500 == 0:
            progress.refresh()
            
        progress.advance(task)

    
    progress.update(task, description="[green]prefabs\n[/green][dim]optimizing...[/dim]", completed=0, total=3)

    # MARK: >> Optimize
    for item in prefabItems:
        if item.X < itemsMinX:
            itemsMinX = item.X
        if item.X > itemsMaxX:
            itemsMaxX = item.X
        if item.Z < itemsMinZ:
            itemsMinZ = item.Z
        if item.Z > itemsMaxZ:
            itemsMaxZ = item.Z
            
    progress.advance(task)
            
    itemsTotalWidth = itemsMaxX - itemsMinX
    itemsTotalHeight = itemsMaxZ - itemsMinZ
    
    itemsAreaCountX = math.ceil(itemsTotalWidth / 1000)
    itemsAreaCountZ = math.ceil(itemsTotalHeight / 1000)
    
    for item in prefabItems:
        x = math.floor((item.X - itemsMinX) / 1000)
        z = math.floor((item.Z - itemsMinZ) / 1000)
        
        if x not in optimizedPrefabItems:
            optimizedPrefabItems[x] = {}
        if z not in optimizedPrefabItems[x]:
            optimizedPrefabItems[x][z] = []
            
            
        optimizedPrefabItems[x][z].append(item)
        
    progress.advance(task)
        
    for item in prefabItems:
        uidParts = [str(item.Uid)[i:i+3] for i in range(0, len(str(item.Uid)), 3)]
        set_nested_item(uidOptimizedPrefabItems, uidParts, item)
        
    progress.advance(task)
    
    # sys.stdout.write(f" > Optimizing prefab items... done!\n\n")
    
    progress.update(task, description="[green]prefabs[/green]", completed=prefabItemCount)
    
    print("Prefab Items parsing done!")
    
# MARK: Getters
def GetItemsInTileByCoordinates(x, z):
    x = math.floor((x - itemsMinX) / 1000)
    z = math.floor((z - itemsMinZ) / 1000)
    
    if x in optimizedPrefabItems:
        if z in optimizedPrefabItems[x]:
            prefabItems = optimizedPrefabItems[x][z]
            return prefabItems
    
    return []

def GetLocalCoordinateInTile(x,y, tileX=-1, tileZ=-1):
    if tileX == -1:
        tileX = math.floor((x - itemsMinX) / 1000)
    if tileZ == -1:
        tileZ = math.floor((y - itemsMinZ) / 1000)
    
    localX = x - (tileX * 1000 + itemsMinX)
    localY = y - (tileZ * 1000 + itemsMinZ)
    
    return (localX, localY)

def GetTileCoordinates(x, y):
    x = math.floor((x - itemsMinX) / 1000)
    z = math.floor((y - itemsMinZ) / 1000)
    
    return (x, z)

def get_nested_item(dataDict, mapList):
    """Get item in nested dictionary"""
    for k in mapList:
        dataDict = dataDict[k]
    return dataDict

def GetPrefabItemByUid(uid):
    uidParts = [str(uid)[i:i+3] for i in range(0, len(str(uid)), 3)]
    try:
        item = get_nested_item(uidOptimizedPrefabItems, uidParts)
        if item != None:
            return item
    except:
        for item in prefabItems:
            if item.Uid == uid:
                return item
            
def FindItemsWithFerryUid(uid):
    items = []
    for item in prefabItems:
        if item.FerryUid == uid:
            items.append(item)
    return items