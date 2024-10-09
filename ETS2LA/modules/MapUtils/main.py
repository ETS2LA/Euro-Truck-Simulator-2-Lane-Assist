from ETS2LA.plugins.OldMap.GameData.prefabItems import PrefabItem
import ETS2LA.plugins.OldMap.GameData.prefabItems as prefabItems
from ETS2LA.plugins.OldMap.GameData.roads import Road
import ETS2LA.plugins.OldMap.GameData.roads as roads
import ETS2LA.plugins.OldMap.GameData.nodes as nodes

from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings

import numpy as np
import logging
import time
import math
import json
import cv2
import sys

runner:PluginRunner = None

# MARK: Initialize
def Initialize():
    global API
    # Check if the API module is available
    try:
        API = runner.modules.TruckSimAPI
    except:
        API = None
        logging.warning("TruckSimAPI module not available, please add it to the plugin.json file.")

# MARK: Bounds
def CheckIfInBoundingBox(boundingBox, x, y):
    try:
        if x >= boundingBox[0][0] and x <= boundingBox[1][0] and y >= boundingBox[0][1] and y <= boundingBox[1][1]:
            return True
        return False
    except:
        return False

# MARK: Point side
def CheckIfPointIsToTheRight(data, point, x=None, y=None):
    """Will check if the point is to the right or left of the truck."""
    x, y = data["truckPlacement"]["coordinateX"], data["truckPlacement"]["coordinateZ"]
    # From -1 to 1
    rotationX = data["truckPlacement"]["rotationX"]
    # Convert to radians
    angle = rotationX * 360
    if angle < 0:
        angle = 360 + angle
    angle = -math.radians(angle)
    # Calculate the vector from the truck to the point
    vector = [point[0] - x, point[1] - y]
    # Calculate the vector from the truck forward
    forward = [math.cos(angle), math.sin(angle)]
    # Calculate the dot product
    dot = vector[0] * forward[0] + vector[1] * forward[1]
    # If the dot product is positive, the point is to the right
    if dot > 0:
        return True
    return False

# MARK: Closest Lane
def FindClosestLane(x, y, z, item, data, lanes=None):
    try:
        if lanes != None:
            lanes = lanes
        elif type(item) == Road:
            lanes = item.ParallelPoints
        elif type(item) == PrefabItem:
            lanes = item.CurvePoints
        
        laneFirstPoints = [lane[0] for lane in lanes]
        laneLastPoints = [lane[-1] for lane in lanes]
        
        closestLane = None
        closestLaneDistance = 999
        # First get the players percentage of each lane
        lanePercentages = []
        for lane in lanes:
            if lane == []: continue
            if type(item) == Road:
                startPoint = lane[0]
                endPoint = lane[-1]
                playerPoint = [x, y]
                
                if type(startPoint) != tuple or type(endPoint) != tuple or type(playerPoint) != list:
                    continue
                
                # Calculate the distance between the player and the start and end points
                startDistance = math.sqrt((startPoint[0] - playerPoint[0])**2 + (startPoint[1] - playerPoint[1])**2)
                endDistance = math.sqrt((endPoint[0] - playerPoint[0])**2 + (endPoint[1] - playerPoint[1])**2)
                sumDistance = startDistance + endDistance
                
                percentage = startDistance / sumDistance
                lanePercentages.append(percentage)
            
        # Now for each lane interpolate the point that matches the players percentage
        interpolatedPoints = []
        pointsLanes = []
        for lane in lanes:
            try:
                if lane == []: continue
                
                if type(item) == PrefabItem or len(lanes) == 1:
                    # Get the two points that are closest to the player.
                    firstPoint = None
                    firstPointDistance = math.inf
                    secondPoint = None
                    secondPointDistance = math.inf
                    for point in lane:
                        try:
                            distance = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
                            if distance < firstPointDistance:
                                secondPoint = firstPoint
                                secondPointDistance = firstPointDistance
                                firstPoint = point
                                firstPointDistance = distance
                            elif distance < secondPointDistance:
                                secondPoint = point
                                secondPointDistance = distance
                        except:
                            continue
                        
                    # Get the percentage of the first point
                    startDistance = math.sqrt((firstPoint[0] - x)**2 + (firstPoint[1] - y)**2)
                    endDistance = math.sqrt((secondPoint[0] - x)**2 + (secondPoint[1] - y)**2)
                    sumDistance = startDistance + endDistance
                    firstPointPercentage = startDistance / sumDistance
                    
                    # Interpolate the point
                    newPoint = [0, 0]
                    newPoint[0] = firstPoint[0] + (secondPoint[0] - firstPoint[0]) * firstPointPercentage
                    newPoint[1] = firstPoint[1] + (secondPoint[1] - firstPoint[1]) * firstPointPercentage
                    
                    interpolatedPoints.append(newPoint)
                    pointsLanes.append(lane)
                    
                elif type(item) == Road:
                    percentage, point = roads.FindClosestPointOnHermiteCurve(x, z, y, road=item, lane=lane)
                    point = (point[0], point[2])
                    interpolatedPoints.append(point)
                    pointsLanes.append(lane)
                    
            except:
                import traceback
                traceback.print_exc()
                continue
        
        closestPoint = None
        for i in range(len(interpolatedPoints)):
            point = interpolatedPoints[i]
            distance = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
            if distance < closestLaneDistance:
                closestLane = pointsLanes[i]
                closestPoint = point
                closestLaneDistance = distance
                           
        # Find which index the lane is in
        if item != None:
            index = 0
            counter = 0
            if type(item) == Road:
                for lane in item.ParallelPoints:
                    if lane == closestLane:
                        index = counter
                        break
                    counter += 1
            if type(item) == PrefabItem:
                for lane in item.CurvePoints:
                    if lane == closestLane:
                        index = counter
                        break
                    counter += 1
            
            negate = False
            if not CheckIfPointIsToTheRight(data, closestPoint):
                negate = True
                    
            return closestLane, negate, item, closestLaneDistance, closestPoint
        else:
            return closestLane
    except:
        logging.exception("Error in FindClosestLane")
        return None, None, None, sys.maxsize, None

# MARK: Closest item
def GetClosestRoadOrPrefabAndLane(x, y, z, data, closeRoads=None, closePrefabs=None):
    inBoundingBox = []
    if len(closeRoads) + len(closePrefabs) == 1:
        inBoundingBox.append(closeRoads[0] if len(closeRoads) == 1 else closePrefabs[0])
    else:
        for road in closeRoads:
            if CheckIfInBoundingBox(road.BoundingBox, x, y):
                inBoundingBox.append(road)
    
        for prefab in closePrefabs:
            if CheckIfInBoundingBox(prefab.BoundingBox, x, y):
                inBoundingBox.append(prefab)
            
    #logging.info(f"Found {len(inBoundingBox)} items in bounding box")
            
    closestItem = None
    closestLane = None
    closestPoint = None
    allPoints = []
    closestLanes = []
    closestDistance = sys.maxsize
    closestNegate = False
    for item in inBoundingBox:
        # We probably don't need to calculate the smooth lanes 
        # since this is just going to be used for other cars
        # if SMOOTH_CURVES and type(item) == Road:
        #     lanes = RecalculateLanes(item, x, y)
        # else:
        lanes = None
        lane, negate, item, distance, point = FindClosestLane(x, y, z, item, data, lanes=lanes)
        closestLanes.append(lane)
        allPoints.append(point)
        if distance < closestDistance:
            closestItem = item
            closestLane = lane
            closestDistance = distance
            closestNegate = negate
            closestPoint = point
            
    if closestNegate: closestDistance = -closestDistance
    if closestDistance == sys.maxsize: closestDistance = 0
    closestType = type(closestItem)
    
    data = { 
        "map": {
            "closestItem": closestItem,
            "closestLane": closestLane,
            "closestPoint": closestPoint,
            "closestDistance": closestDistance,
            "closestType": closestType,
            "inBoundingBox": inBoundingBox,
            "closestLanes": closestLanes,
            "allPoints": allPoints
        }
    }
    
    return data

# MARK: Load from JSON
def LoadPrefabs(mapData):
    prefabs = []
    try:
        for prefab in mapData["prefabs"]:
            prefabItem = PrefabItem()
            prefabItem.fromJson(prefab)
            prefabs.append(prefabItem)
    except:
        logging.exception("Error in LoadPrefabs")
    return prefabs

def LoadRoads(mapData):
    roads = []
    
    for road in mapData["roads"]:
        roadItem = Road()
        roadItem.fromJson(road)
        roads.append(roadItem)
    
    for road in roads:
        if road.StartNode == None and road.EndNode == None:
            logging.warning(f"Road {road.Uid} has no start or end node!")
            logging.warning(f"{json.dumps(road.json(), indent=4)}")
    
    return roads

def UpdateMapData():
    global lastMapDataUpdate
    global mapData
    if time.time() - lastMapDataUpdate > 10 or mapData == None or mapData == {}:
        mapData = runner.GetData(["tags.map"])[0]
        lastMapDataUpdate = time.time()

mapData = None
lastMapDataUpdate = time.time()

# MARK: Run
def run(x, y, z, closeRoads=None, closePrefabs=None):
    data = API.run()
    if closeRoads == None or closePrefabs == None:
        UpdateMapData()
        if mapData == None or mapData == {}:
            return None
        
        closePrefabs = LoadPrefabs(mapData)
        closeRoads = LoadRoads(mapData)
    
    return GetClosestRoadOrPrefabAndLane(x, z, y, data, closeRoads=closeRoads, closePrefabs=closePrefabs)["map"]