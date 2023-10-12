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
    Origin = 1
    Prefab = None
    NavigationLanes = []
    IsSecret = False
    
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
        
        for nav in item["Navigation"]:
            navObj = Navigation()
            navId = nav
            nav = item["Navigation"][nav]
            navObj.NavId = navId
            navObj.Item1 = nav["Item1"]
            for item2 in nav["Item2"]:
                item2Obj = NavigationItem2()
                item2Obj.Uid = item2["Uid"]
                item2Obj.Type = item2["Type"]
                navObj.Item2.append(item2Obj)
                
            itemObj.Navigation.append(navObj)
            
        itemObj.Origin = item["Origin"]
        
        # Modify the X and Y to the correct coordinates
        itemObj.X = itemObj.Nodes[itemObj.Origin].X
        itemObj.Z = itemObj.Nodes[itemObj.Origin].Z
        
        itemObj.Prefab = item["Prefab"]
        itemObj.IsSecret = item["IsSecret"]
        
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
    for prefabItem in prefabItems:
        prefabItem.StartNode = nodes.GetNodeByUid(prefabItem.StartNodeUid)
        prefabItem.EndNode = nodes.GetNodeByUid(prefabItem.EndNodeUid)
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
        
        
        # Rotate the prefab curves to match the road.
        # They are rotated around the origin node location by an amount of pi.
        prefabItem.NavigationLanes = []
        for curve in prefabItem.Prefab.PrefabCurves:
            curveStartX, curveStartZ = curve.startX, curve.startZ
            curveEndX, curveEndZ = curve.endX, curve.endZ
            
            def RotatePoints(x1, y1, x2, y2, originX, originY, pi):
                # Translate points to origin
                x1 -= originX
                y1 -= originY
                x2 -= originX
                y2 -= originY
                
                # Rotate points
                x1new = x1 * math.cos(pi) - y1 * math.sin(pi)
                y1new = x1 * math.sin(pi) + y1 * math.cos(pi)
                x2new = x2 * math.cos(pi) - y2 * math.sin(pi)
                y2new = x2 * math.sin(pi) + y2 * math.cos(pi)
                
                # Translate points back
                x1new += originX
                y1new += originY
                x2new += originX
                y2new += originY
                
                return (x1new, y1new, x2new, y2new)
            
            # Rotate the point's around 0,0
            originX = prefabItem.Prefab.PrefabNodes[int(prefabItem.Origin)].X# prefabItem.Nodes[prefabItem.Origin].X - prefabItem.X
            originZ = prefabItem.Prefab.PrefabNodes[int(prefabItem.Origin)].Z# prefabItem.Nodes[prefabItem.Origin].Z - prefabItem.Z
            curveStartX, curveStartZ, curveEndX, curveEndZ = RotatePoints(curveStartX, curveStartZ, curveEndX, curveEndZ, originX, originZ, prefabItem.Nodes[int(prefabItem.Origin)].Rotation)
            prefabItem.NavigationLanes.append((curveStartX, curveStartZ, curveEndX, curveEndZ))
            
        
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