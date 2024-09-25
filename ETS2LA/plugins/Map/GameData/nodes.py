import json
import logging
print = logging.info
from ETS2LA.variables import *
from ETS2LA.backend.settings import *
from ETS2LA.plugins.Map.GameData import roads, prefabItems
import sys
from rich.progress import Task, Progress

# For loading nodes progress indicator
task: Task = None
progress: Progress = None

class Item:
    Uid = 0
    Type = ""
    
    def json(self):
        return {
            "Uid": self.Uid,
            "Type": self.Type
        }

class Node:
    Uid = 0
    X = 0
    Y = 0
    Z = 0
    rX = 0
    rY = 0
    rZ = 0
    Rotation = 0
    ForwardItem = None
    BackwardItem = None
    
    def json(self):
        return {
            "Uid": self.Uid,
            "X": self.X,
            "Y": self.Y,
            "Z": self.Z,
            "rX": self.rX,
            "rY": self.rY,
            "rZ": self.rZ,
            "Rotation": self.Rotation,
            "ForwardItem": str(self.ForwardItem.Uid) if self.ForwardItem != None else None,
            "BackwardItem": str(self.BackwardItem.Uid) if self.BackwardItem != None else None
        }
        
    def fromJson(self, jsonData):
        self.Uid = jsonData["Uid"]
        self.X = jsonData["X"]
        self.Y = jsonData["Y"]
        self.Z = jsonData["Z"]
        self.rX = jsonData["rX"]
        self.rY = jsonData["rY"]
        self.rZ = jsonData["rZ"]
        self.Rotation = jsonData["Rotation"]
        return self
    
    def HeuristicDistance(self, x, z):
        return abs(self.X - x) + abs(self.Z - z)
    
nodes = []
optimizedNodes = {}
nodeFileName = PATH + "ETS2LA/plugins/Map/GameData/data/nodes.json"
itemsCalculated = False

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

def LoadNodes():
    global nodes
    global optimizedNodes
    
    progress.update(task, description="[green]nodes\n[/green][dim]reading JSON...[/dim]")
    
    jsonData = json.load(open(nodeFileName))
    jsonLength = len(jsonData)
    progress.update(task, total=jsonLength, description="[green]nodes\n[/green][dim]parsing...[/dim]", completed=0)
    
    for node in jsonData:
        nodeObj = Node()
        nodeObj.Uid = node["Uid"]
        nodeObj.X = node["X"]
        nodeObj.Y = node["Y"]
        nodeObj.Z = node["Z"]
        nodeObj.rX = node["rX"]
        nodeObj.rY = node["rY"]
        nodeObj.rZ = node["rZ"]
        nodeObj.Rotation = node["Rotation"]
        try:
            nodeObj.ForwardItem = Item()
            nodeObj.ForwardItem.Uid = node["ForwardItem"]["Uid"]
            nodeObj.ForwardItem.Type = node["ForwardItem"]["Type"]
        except:
            nodeObj.ForwardItem = None
        try:
            nodeObj.BackwardItem = Item()
            nodeObj.BackwardItem.Uid = node["BackwardItem"]["Uid"]
            nodeObj.BackwardItem.Type = node["BackwardItem"]["Type"]
        except:
            nodeObj.BackwardItem = None
        
        nodes.append(nodeObj)
        progress.advance(task)
            
    del jsonData
            
    progress.update(task, total=len(nodes), description="[green]nodes\n[/green][dim]optimizing...[/dim]", completed=0)
    progress.refresh()
    
    count = 0
    for node in nodes:
        # Split the node Uid into parts of 3
        uidParts = [str(node.Uid)[i:i+3] for i in range(0, len(str(node.Uid)), 3)]
        # Build the optimizedNodes dictionary
        set_nested_item(optimizedNodes, uidParts, node)
        progress.advance(task)
        if count % 10000 == 0:
            progress.refresh()
        
        count += 1
    
    progress.update(task, total=len(nodes), description="[green]nodes[/green]")
    print(f"Node parsing done!")
    
    
def GetNodeByUid(uid):
    if uid == 0:
        return None
    if uid == None:
        return None
    
    uidParts = [str(uid)[i:i+3] for i in range(0, len(str(uid)), 3)]
    try:
        node = get_nested_item(optimizedNodes, uidParts)
        if node != None:
            return node
        sys.stdout.write(f" > Node not found in optimizedNodes, searching in nodes...\n")
        for node in nodes:
            if node.Uid == uid:
                return node
    except:
        sys.stdout.write(f" > Node not found in optimizedNodes, searching in nodes...\n")
        for node in nodes:
            if node.Uid == uid:
                return node
        
    return None

def CalculateForwardAndBackwardItemsForNodes():
    count = len(nodes)
    #sys.stdout.write(f"\nCalculating forward and backward items for nodes... (total {count})\n")
    progress.update(task, total=count, description="[green]nodes\n[/green][dim]detecting connected items...[/dim]", completed=0)
    for i, node in enumerate(nodes):
        progress.advance(task)
        try:
            uid = node.Uid
        
            if node.ForwardItem != None:
                itemType = node.ForwardItem.Type
                if itemType == "Road":
                    item = roads.GetRoadByUid(node.ForwardItem.Uid)
                    if item == None:
                        sys.stdout.write(f" > Road not found for node {uid}!\n")
                        continue
                    node.ForwardItem = item
                elif itemType == "Prefab":
                    item = prefabItems.GetPrefabItemByUid(node.ForwardItem.Uid)
                    if item == None:
                        sys.stdout.write(f" > Prefab not found for node {uid}!\n")
                        continue
                    node.ForwardItem = item
                elif itemType == "City":
                    pass
                elif itemType == "Ferry":
                    pass
                else:
                    sys.stdout.write(f" > Unknown item type for node {uid}! ({itemType})\n")
                    pass
                
            if node.BackwardItem != None:
                itemType = node.BackwardItem.Type
                if itemType == "Road":
                    item = roads.GetRoadByUid(node.BackwardItem.Uid)
                    if item == None:
                        sys.stdout.write(f" > Road not found for node {uid}!\n")
                        continue
                    node.BackwardItem = item
                elif itemType == "Prefab":
                    item = prefabItems.GetPrefabItemByUid(node.BackwardItem.Uid)
                    if item == None:
                        sys.stdout.write(f"\n > Prefab not found for node {uid}!")
                        continue
                    node.BackwardItem = item
                elif itemType == "City":
                    pass
                elif itemType == "Ferry":
                    pass
                else:
                    sys.stdout.write(f"\n > Unknown item type for node {uid}! ({itemType})")
                    continue
                
            # Save the node
            uidParts = [str(uid)[i:i+3] for i in range(0, len(str(uid)), 3)]
            set_nested_item(optimizedNodes, uidParts, node)
            
            #if i % int(count/10) == 0:
            #    sys.stdout.write(f" > {i} ({round(i/count*100)}%)...            \r")
            #    sys.stdout.flush()
        except:
            sys.stdout.write(f" > Error at node {uid}!\n")
            pass
    
    progress.update(task, total=count, description="[green]nodes[/green]")
            
    #sys.stdout.write(f" > {i} ({round(i/count*100)}%)... done!                          \n\n")
    roads.MatchRoadsToNodes()