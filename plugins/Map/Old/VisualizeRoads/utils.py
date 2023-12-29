"""
Download the map from 
https://github.com/Unicor-p/ts-map#map-available

Place the levels from there to 
/Tiles

Example
/Tiles/1
/Tiles/2
/Tiles/3
etc...

Then run this script.

Each pixel at lvl8 = one meter in game
This means we can easily get the coordinates of the lanes from the map, as long as we can detect them.

Only problem is it would still be +- 1 meter, so we have to do some pretty heavy interpolation
to get usable coordinates on the app side.

"""


import os
from os import listdir
from os.path import isdir, join
import json
import time

from plugins.Map.Old.VisualizeRoads.RoadLook import RoadLook
from plugins.Map.Old.VisualizeRoads.Node import Node

# Tile settings
maxX = 131072
maxY = 131072
tileSize = 512
maxZoom = 8

# File settings
tilePath = "Tiles/8/"
folderAxis = "X"
fileAxis = "Y"

data = {
    "folders": {},
}

for folder in range(0, int(maxY/tileSize)):
    data["folders"][folder] = {}
    data["folders"][folder]["files"] = {}
    for file in range(0, int(maxY/tileSize)):
        data["folders"][folder]["files"][file] = {}
        data["folders"][folder]["files"][file]["x"] = int(folder) * tileSize
        data["folders"][folder]["files"][file]["y"] = int(file) * tileSize
        
def ConvertGameXYToPixelXY(x,y):
    # https://github.com/dariowouters/ts-map/issues/16#issuecomment-716160718
    
    xy = [x,y]
    # Values from TileMapInfo.json
    x1 = -94505.8047
    x2 = 79254.13
    y1 = -80093.17
    y2 = 93666.7656
    
    xtot = x2 - x1; # Total X length
    ytot = y2 - y1; # Total Y length

    xrel = (xy[0] - x1) / xtot; # The fraction where the X is (between 0 and 1, 0 being fully left, 1 being fully right)
    yrel = (xy[1] - y1) / ytot; # The fraction where the Y is

    return [
        xrel * maxX, # Where X actually is, so multiplied the actual width
        maxY - (yrel * maxY) # Where Y actually is, only Y is inverted
    ]
    
def ConvertPixelXYToGameXY(x,y):
    # Derived from https://github.com/dariowouters/ts-map/issues/16#issuecomment-716160718
    xy = [x,y]
    # Values from TileMapInfo.json
    x1 = -94505.8047
    x2 = 79254.13
    y1 = -80093.17
    y2 = 93666.7656
    
    xtot = x2 - x1; # Total X length
    ytot = y2 - y1; # Total Y length
    
    xrel = xy[0] / maxX
    yrel = xy[1] / maxY
    
    x = x1 + (xrel * xtot)
    y = y1 + (yrel * ytot)
    
    return [x,y]

def ParseRoadLook(roadLook):
    roadLookObj = RoadLook()
    roadLookObj.Name = roadLook["Name"] if roadLook["Name"] is not None else "Prefab"
    roadLookObj.Offset = roadLook["Offset"]
    roadLookObj.CenterLineLeftWidth = roadLook["CenterLineLeftWidth"]
    roadLookObj.CenterLineRightWidth = roadLook["CenterLineRightWidth"]
    roadLookObj.ShoulderSpaceLeft = roadLook["ShoulderSpaceLeft"]
    roadLookObj.ShoulderSpaceRight = roadLook["ShoulderSpaceRight"]
    roadLookObj.RoadSizeLeft = roadLook["RoadSizeLeft"]
    roadLookObj.RoadSizeRight = roadLook["RoadSizeRight"]
    roadLookObj.LanesLeft = roadLook["LanesLeft"]
    roadLookObj.LanesRight = roadLook["LanesRight"]
    roadLookObj.LaneOffsetsLeft = roadLook["LaneOffsetsLeft"]
    roadLookObj.LaneOffsetsRight = roadLook["LaneOffsetsRight"]
    roadLookObj.Token = roadLook["Token"]
    
    if roadLookObj.LanesLeft != [] or roadLookObj.LanesRight != []:
        return roadLookObj
    
    return None

def ParseNode(node):
    nodeObj = Node()
    nodeObj.X = node["X"]
    nodeObj.Y = node["Z"]
    nodeObj.Uid = node["Uid"]
    nodeObj.Rotation = node["Rotation"]
    return nodeObj

def ParseNodes(nodes):
    nodeObjs = []
    for node in nodes:
        nodeObj = ParseNode(node)
        nodeObjs.append(nodeObj)
        
    return nodeObjs


roadOffsetFile = "plugins/Map/VisualizeRoads/roadOffsets.json"
def GetRoadOffset(name):
    # Check if the value exits in the file
    data = ""
    with open(roadOffsetFile, "r") as f:
        data = json.load(f)
        if name in data["roads"]:
            return data["roads"][name]
        
    # It didn't exist so we create it
    with open(roadOffsetFile, "w") as f:
        data["roads"][name] = [0,0]
        f.truncate(0)
        f.write(json.dumps(data, indent=4))
        return [0,0]
    
    

def SetRoadOffset(name, value):
    data = ""
    with open(roadOffsetFile, "r") as f:
        data = json.load(f)
    
    # Set the value
    with open(roadOffsetFile, "w") as f:
        data["roads"][name] = value
        f.truncate(0)
        f.write(json.dumps(data, indent=4))