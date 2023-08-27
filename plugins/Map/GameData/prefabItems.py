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

def LoadPrefabItems():
    global prefabItems
    global optimizedPrefabItems
    
    loading = LoadingWindow("Parsing prefab items...", grab=False, progress=0)
    
    jsonData = json.load(open(prefabItemsFileName))
    
    count = 0
    for item in jsonData:
        item = jsonData[item]
        
        itemObj = PrefabItem()
        itemObj.Uid = item["Uid"]
        itemObj.StartNodeUid = item["StartNodeUid"]
        itemObj.EndNodeUid = item["EndNodeUid"]
        itemObj.Nodes = item["Nodes"]
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
        itemObj.Prefab = item["Prefab"]
        itemObj.IsSecret = item["IsSecret"]
            
        prefabItems.append(itemObj)
        count += 1
        
        if count % 1000 == 0:
            sys.stdout.write(f"\rLoaded {count} prefab items.\r")
            loading.update(text=f"Loaded {count} prefab items.", progress=count/len(jsonData) * 100)
    
    sys.stdout.write(f"Loaded {len(prefabItems)} prefab items.\nNow matching prefab items...\n")
    loading.update(text="Matching prefab items...", progress=0)
    count = 0
    for prefabItem in prefabItems:
        prefabItem.StartNode = nodes.GetNodeByUid(prefabItem.StartNodeUid)
        prefabItem.EndNode = nodes.GetNodeByUid(prefabItem.EndNodeUid)
        prefabItem.Prefab = prefabs.GetPrefabByToken(prefabItem.Prefab)
        
        if prefabItem.Prefab == None:
            print(f"Prefab item {prefabItem.Uid} has no prefab!")
        
        count += 1
        if count % 100 == 0:
            loading.update(text=f"Matched prefab items : {count} ({round(count/len(prefabItems) * 100)}%)", progress=count/len(prefabItems) * 100)
            sys.stdout.write(f"Matched prefab items : {count}\r")
            
    sys.stdout.write(f"Matched prefab items : {count}\nNow optimizing prefab items...\n")
    
    loading.destroy()
    
    print("Prefab Items parsing done!")