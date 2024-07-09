from ETS2LA.backend.variables import *
from ETS2LA.backend.settings import *
import GameData.prefabs as prefabs
import GameData.roads as roads
import GameData.nodes as nodes
import logging
import json
import math
import sys


uidOptimizedPrefabItems = {}
optimizedPrefabItems = {}
prefabItems = []

print = logging.info

prefabItemsFileName = PATH + "ETS2LA/plugins/Map/GameData/prefab_items.json"

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
    Z = 0
    Hidden = False
    Flags = 0
    Navigation = []
    Origin = 0
    Padding = 0
    Prefab = None
    NavigationLanes = []
    IsSecret = False
    CurvePoints = [[]]
    EndPoints = []
    BoundingBox = []
    
    def json(self):
        return {
            "Uid": self.Uid,
            "StartNodeUid": self.StartNodeUid,
            "EndNodeUid": self.EndNodeUid,
            "StartNode": self.StartNode.json() if self.StartNode != None else None,
            "Nodes": [node.json() for node in self.Nodes],
            "BlockSize": self.BlockSize,
            "Valid": self.Valid,
            "Type": self.Type,
            "X": self.X,
            "Z": self.Z,
            "Hidden": self.Hidden,
            "Flags": self.Flags,
            "Navigation": [nav.json() for nav in self.Navigation],
            "Origin": self.Origin,
            "Padding": self.Padding,
            "Prefab": self.Prefab.json() if self.Prefab != None else None,
            "NavigationLanes": self.NavigationLanes,
            "IsSecret": self.IsSecret,
            "CurvePoints": self.CurvePoints,
            "EndPoints": self.EndPoints,
            "BoundingBox": self.BoundingBox
        }
    
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
        itemObj.CurvePoints = item["curvePoints"]
        
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
        
        prefabItem.NavigationLanes = []
        for curvePoints in prefabItem.CurvePoints:
            curveStartX = curvePoints[0]
            curveStartZ = curvePoints[1]
            curveEndX = curvePoints[2]
            curveEndZ = curvePoints[3]
            
            prefabItem.NavigationLanes.append((curveStartX, curveStartZ, curveEndX, curveEndZ))
            

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
            prefabItems = optimizedPrefabItems[x][z].copy()
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