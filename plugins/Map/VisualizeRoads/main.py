import os
import cv2
from PIL import Image
import json
import math
import random
import numpy as np
import time

from plugins.Map.VisualizeRoads.Node import Node
from plugins.Map.VisualizeRoads.RoadLook import RoadLook
from plugins.Map.VisualizeRoads.Road import Road
import plugins.Map.VisualizeRoads.getTileCoordinates as getTileCoordinates

roads = []

roadColor = (0, 0, 0)
shoulderColor = (25, 25, 25)
laneMarkingColor = (255, 255, 255)

def ParseJsonFile():
    fileName = "plugins/Map/VisualizeRoads/Roads.json"
    json.load(open(fileName))
    length = len(json.load(open(fileName)))
    counter = 0
    for road in json.load(open(fileName)):
        roadObj = Road()
        roadObj.DlcGuard = road["DlcGuard"]
        roadObj.RoadLook = ParseRoadLook(road["RoadLook"])
        roadObj.IsSecret = road["IsSecret"]
        roadObj.Uid = road["Uid"]
        # By default this object is None
        try:
            roadObj.Nodes = ParseNodes(road["Nodes"])
        except: pass
        roadObj.BlockSize = road["BlockSize"]
        roadObj.Valid = road["Valid"]
        roadObj.Type = road["Type"]
        roadObj.X = road["X"]
        roadObj.Y = road["Z"]
        roadObj.Hidden = road["Hidden"]
        roadObj.StartNode = ParseNode(road["StartNode"])
        roadObj.EndNode = ParseNode(road["EndNode"])
        roadObj.Width = road["Width"]
        roads.append(roadObj)
        print("Parsed road " + str(counter) + " of " + str(length), end="\r")
        counter += 1
    
    # Loop through the roads and append them to the correct map tile
    for road in roads:
        xy = getTileCoordinates.ConvertGameXYToPixelXY(road.X, road.Y)
        x = xy[0]
        y = xy[1]
        # The map tiles are 512x512 so we need to divide the x and y by 512
        x = math.floor(x / 512)
        y = math.floor(y / 512)
        # Append the road to the correct map tile
        try:
            getTileCoordinates.data["folders"][x]["files"][y]["roads"]
        except:
            getTileCoordinates.data["folders"][x]["files"][y]["roads"] = []
            
        getTileCoordinates.data["folders"][x]["files"][y]["roads"].append(road)
    
    
    print("Parsed " + str(length) + " roads         ")
     
def ParseRoadLook(roadLook):
    roadLookObj = RoadLook()
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
    return roadLookObj

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


def GetRoadsWithinRange(x, y, range):
    # Convert the x and y to pixel coordinates
    xy = getTileCoordinates.ConvertGameXYToPixelXY(x, y)
    mapX = xy[0]
    mapY = xy[1]
    
    # Find the map tile it's in
    mapX = math.floor(mapX / 512)
    mapY = math.floor(mapY / 512)
    
    # Get the roads in that map tile, in addition to the 8 surrounding tiles
    foundRoads = []
    try: foundRoads += getTileCoordinates.data["folders"][mapX]["files"][mapY]["roads"]
    except: pass
    try: foundRoads += getTileCoordinates.data["folders"][mapX+1]["files"][mapY]["roads"]
    except: pass
    try: foundRoads += getTileCoordinates.data["folders"][mapX-1]["files"][mapY]["roads"]
    except: pass
    try: foundRoads += getTileCoordinates.data["folders"][mapX]["files"][mapY+1]["roads"]
    except: pass
    try: foundRoads += getTileCoordinates.data["folders"][mapX]["files"][mapY-1]["roads"]
    except: pass
    try: foundRoads += getTileCoordinates.data["folders"][mapX+1]["files"][mapY+1]["roads"]
    except: pass
    try: foundRoads += getTileCoordinates.data["folders"][mapX+1]["files"][mapY-1]["roads"]
    except: pass
    try: foundRoads += getTileCoordinates.data["folders"][mapX-1]["files"][mapY+1]["roads"]
    except: pass
    try: foundRoads += getTileCoordinates.data["folders"][mapX-1]["files"][mapY-1]["roads"]
    except: pass
    
    # Loop through the roads and find the ones within the range
    roadsWithin = []
    for road in foundRoads:
        if road.X > x - range and road.X < x + range and road.Y > y - range and road.Y < y + range:
            roadsWithin.append(road)
    
    # Show the road locations on a map
    img = Image.new("RGB", (512*3, 512*3), (0, 0, 0))
    img = np.array(img)
    for road in roadsWithin:
        if road.Valid:
            xy = getTileCoordinates.ConvertGameXYToPixelXY(road.StartNode.X, road.StartNode.Y)
            startX = xy[0]
            startY = xy[1]
            startX -= mapX * 512 - 512
            startY -= mapY * 512 - 512
            
            xy = getTileCoordinates.ConvertGameXYToPixelXY(road.EndNode.X, road.EndNode.Y)
            endX = xy[0]
            endY = xy[1]
            endX -= mapX * 512 - 512
            endY -= mapY * 512 - 512
            
            cv2.line(img, (int(startX), int(startY)), (int(endX), int(endY)), (255,255,255), int(road.Width), cv2.LINE_AA)
        
    
    # Render the x and y
    xy = getTileCoordinates.ConvertGameXYToPixelXY(x, y)
    pointX = xy[0]
    pointY = xy[1]
    pointX -= mapX * 512 - 512
    pointY -= mapY * 512 - 512
    cv2.circle(img, (int(pointX), int(pointY)), 20, (255, 255, 0), -1, cv2.LINE_AA)
    
    cv2.putText(img, "Roads within " 
                + str(range) + "m of " 
                + str(x) + ", " + str(y)
                + " (" + str(len(roadsWithin)) + ")", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)    
    
    
    return roadsWithin, img


if __name__ == "__main__":
    ParseJsonFile()
    while True:
        x,y = random.randint(-100000, 100000), random.randint(-100000, 100000)
        startTime = time.time()
        roadsWithin = GetRoadsWithinRange(x, y, 1024)
        endTime = time.time()
        print("Random point: " + str(x) + ", " + str(y))
        ms = (endTime - startTime) * 1000
        print("Search took " + str(ms) + "ms")
        if len(roadsWithin) == 0:
            cv2.waitKey(1)
        else:
            cv2.waitKey(500)