import json
from src.logger import print
from src.variables import *
from src.settings import *
from src.helpers import *
from src.mainUI import *
import sys
import plugins.Map.GameData.nodes as nodes
import math
import plugins.Map.GameData.prefabs as prefabs
import plugins.Map.GameData.roads as roads
import src.mainUI as mainUI
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
    
class NavigationItem2:
    Uid = 0
    Type = ""
    
class Navigation:
    NavId = 0
    Item1 = 0
    Item2 = []
    

prefabItems = []
optimizedPrefabItems = {}

prefabItemsFileName = variables.PATH + "/plugins/Map/GameData/prefab_items.json"

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
            sys.stdout.write(f"\rLoaded {count} prefab items.\r")
            data = {
                "state": f"Loading prefab items... {round(count/jsonLength * 100)}%",
                "stateProgress": count/jsonLength * 100,
                "totalProgress": 75 + count/jsonLength * 5
            }
            mainUI.ui.update(data)
            mainUI.root.update()
    
    sys.stdout.write(f"Loaded {len(prefabItems)} prefab items.\nNow matching prefab items...\n")
    count = 0
    
    
    # TODO: FIX THIS CODE
    # Original C# code in TsMapRenderer.cs -> lines 393-417
    
    
    for prefabItem in prefabItems:
        prefabItem.Prefab = prefabs.GetPrefabByToken(prefabItem.Prefab)
        
        if prefabItem.Prefab == None:
            # print(f"Prefab item {prefabItem.Uid} has no prefab!")
            pass 
        
        try:
            if not prefabItem.Prefab.ValidRoad:
                prefabItems.remove(prefabItem)
                continue
        except:
            prefabItems.remove(prefabItem)
            continue
        
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
                    road = roads.GetRoadByUid(item.Uid)
                    if road != None:
                        road.ConnectedPrefabItems.append(prefabItem.Uid)
                        # print(f"Added prefab item {prefabItem.Uid} to road {road.Uid}")
        
        
        
        count += 1
        if count % 500 == 0:
            data = {
                "state": f"Matching prefabs and prefab items... {round(count/len(prefabItems) * 100)}%",
                "stateProgress": count/len(prefabItems) * 100,
                "totalProgress": 80 + count/len(prefabItems) * 20
            }
            mainUI.ui.update(data)
            mainUI.root.update()
            sys.stdout.write(f"Matched prefab items : {count}\r")
    
    sys.stdout.write(f"Matched prefab items : {count}\nNow optimizing prefab items...\n")
    
    data = {
        "state": f"Optimizing array... {round(count/len(prefabItems) * 100)}%",
        "stateProgress": 100,
        "totalProgress": 100
    }
    mainUI.ui.update(data)
    mainUI.root.update()
    
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