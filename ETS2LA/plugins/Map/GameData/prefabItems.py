import json
import logging
print = logging.info
from ETS2LA.backend.variables import *
from ETS2LA.backend.settings import *
import sys
import GameData.nodes as nodes
import math
import GameData.prefabs as prefabs
import GameData.roads as roads
import math
class PrefabItem:
    Uid = 0
    StartNodeUid = 0
    EndNodeUid = 0
    StartNode = None
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
    
class NavigationItem2:
    Uid = 0
    Type = ""
    
class Navigation:
    NavId = 0
    Item1 = 0
    Item2 = []
    

prefabItems = []
optimizedPrefabItems = {}

prefabItemsFileName = PATH + "ETS2LA/plugins/Map/GameData/prefab_items.json"

itemsMinX = 0
itemsMaxX = 0
itemsMinZ = 0
itemsMaxZ = 0
itemsTotalWidth = 0
itemsTotalHeight = 0
itemsAreaCountX = 0
itemsAreaCountZ = 0

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
    
    sys.stdout.write(f"\nLoading {jsonLength} prefab items...\n")
    
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
        
        if count % int(jsonLength/100) == 0:
            sys.stdout.write(f" > {count} ({round(count/jsonLength*100)}%)...\r")
    
    sys.stdout.write(f" > {count} ({round(count/jsonLength*100)}%)... done!\n")
    count = 0
    
    
    # TODO: FIX THIS CODE
    # Original C# code in TsMapRenderer.cs -> lines 393-417
    
    prefabItemCount = len(prefabItems)
    sys.stdout.write(f" > Matching prefabs and prefab items...\n")
    prefabItemMatchStartTime = time.time()
    for prefabItem in prefabItems:
        prefabItem.Prefab = prefabs.GetPrefabByToken(prefabItem.Prefab)
        
        if prefabItem.Prefab == None:
            # sys.stdout.write(f"Prefab item {prefabItem.Uid} has no prefab!")
            pass 
        
        # try:
        #     if not prefabItem.Prefab.ValidRoad:
        #         # sys.stdout.write(f"Prefab item {prefabItem.Uid} has an invalid prefab!")
        #         prefabItems.remove(prefabItem)
        #         continue
        # except:
        #     prefabItems.remove(prefabItem)
        #     continue
        
        prefabItem.StartNode = nodes.GetNodeByUid(prefabItem.StartNodeUid)
        prefabItem.EndNode = nodes.GetNodeByUid(prefabItem.EndNodeUid)
        
        originNode = prefabItem.Nodes[0]
        mapPointOrigin = prefabItem.Prefab.PrefabNodes[prefabItem.Origin]
        
        # rot = originNode.Rotation - math.pi - math.atan2(mapPointOrigin.RotZ, mapPointOrigin.RotX) + math.pi / 2
        
        prefabStartX = originNode.X - mapPointOrigin.X
        prefabStartZ = originNode.Z - mapPointOrigin.Z
        
        prefabItem.X = prefabStartX
        prefabItem.Z = prefabStartZ
        
        # Rotate the prefab curves to match the road.
        # They are rotated around the origin node location by an amount of pi.
        prefabItem.NavigationLanes = []
        for curvePoints in prefabItem.CurvePoints:
            # def rotate_point(x, z, angle, rot_x, rot_z):
            #     s = math.sin(angle)
            #     c = math.cos(angle)
            #     new_x = x - rot_x
            #     new_z = z - rot_z
            #     return (new_x * c - new_z * s + rot_x, new_x * s + new_z * c + rot_z)
            # 
            # newPointStart = rotate_point(prefabStartX + curve.startX, prefabStartZ + curve.startZ, rot, originNode.X, originNode.Z)
            # newPointEnd = rotate_point(prefabStartX + curve.endX, prefabStartZ + curve.endZ, rot, originNode.X, originNode.Z)
            
            curveStartX = curvePoints[0]
            curveStartZ = curvePoints[1]
            curveEndX = curvePoints[2]
            curveEndZ = curvePoints[3]
            
            prefabItem.NavigationLanes.append((curveStartX, curveStartZ, curveEndX, curveEndZ))
            
        
        # Set the prefab item as a reference to the road
        for nav in prefabItem.Navigation:
            for item in nav.Item2:
                if item.Type == "Road":
                    try:
                        road = roads.GetRoadByUid(item.Uid)
                    except:
                        road = None
                        
                    if road != None:
                        road.ConnectedPrefabItems.append(prefabItem.Uid)
                        # print(f"Added prefab item {prefabItem.Uid} to road {road.Uid}")
        
        
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
            itemsLeft = prefabItemCount - count
            timeLeft = (time.time() - prefabItemMatchStartTime) / count * itemsLeft
            sys.stdout.write(f"  > {count} ({round(count/prefabItemCount*100)}%)... {round(timeLeft)}s left...   \r")
    
    sys.stdout.write(f"  > {count} ({round(count/prefabItemCount*100)}%)... done!              \n")
    
    sys.stdout.write(f" > Optimizing prefab items...\r")
    
    for item in prefabItems:
        if item.X < itemsMinX:
            itemsMinX = item.X
        if item.X > itemsMaxX:
            itemsMaxX = item.X
        if item.Z < itemsMinZ:
            itemsMinZ = item.Z
        if item.Z > itemsMaxZ:
            itemsMaxZ = item.Z
            
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
    
    sys.stdout.write(f" > Optimizing prefab items... done!\n\n")
    
    print("Prefab Items parsing done!")
    

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