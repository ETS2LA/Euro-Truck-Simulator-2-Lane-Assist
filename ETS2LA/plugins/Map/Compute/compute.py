from ETS2LA.plugins.Map.GameData.prefabItems import PrefabItem
import ETS2LA.plugins.Map.GameData.prefabItems as prefabItems
from ETS2LA.plugins.Map.GameData.roads import Road, GetOffset
import ETS2LA.plugins.Map.GameData.roads as roads
from ETS2LA.plugins.Map.GameData import calc
import threading
import logging
import math
import time
import sys

LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME = 10
SMOOTH_CURVES = True

lastRoadUpdatePosition = None
lastPrefabUpdatePosition = None
closeRoads = []
closePrefabs = []
# MARK: Get Roads
def GetRoads(data, wait=False):
    global closeRoads, lastRoadUpdatePosition
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    
    def GetRoads(x, y, noWait=False):
        # Get the roads in the current area
        areaRoads = []
        areaRoads += roads.GetRoadsInTileByCoordinates(x, y)
        
        # Also get the roads in the surrounding tiles
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y)
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y)
        areaRoads += roads.GetRoadsInTileByCoordinates(x, y + 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x, y - 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y + 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y - 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y + 1000)
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y - 1000)
        
        return areaRoads
        
    if lastRoadUpdatePosition == None or calc.distance_between((x, y), lastRoadUpdatePosition) > 500 or closeRoads == []:
        closeRoads = GetRoads(x, y)
        lastRoadUpdatePosition = (x, y)
        return closeRoads, True
    else: 
        return closeRoads, False

# MARK: Get Prefabs
def GetPrefabs(data):
    global lastPrefabUpdatePosition, closePrefabs
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]

    
    def GetPrefabThread(x, y):
        # Get the roads in the current area
        areaItems = []
        areaItems += prefabItems.GetItemsInTileByCoordinates(x, y)
        
        # Also get the roads in the surrounding tiles
        areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y)
        areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y)
        areaItems += prefabItems.GetItemsInTileByCoordinates(x, y + 1000)
        areaItems += prefabItems.GetItemsInTileByCoordinates(x, y - 1000)
        areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y + 1000)
        areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y - 1000)
        areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y + 1000)
        areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y - 1000)

        return areaItems
    
    if lastPrefabUpdatePosition == None or calc.distance_between((x, y), lastPrefabUpdatePosition) > 500 or closePrefabs == []:
        closePrefabs = GetPrefabThread(x, y)
        lastPrefabUpdatePosition = (x, y)
        return closePrefabs, True
    else:
        return closePrefabs, False

# MARK: Parallel Points
def CalculateParallelPointsForRoads(areaRoads, all=False):
    calcCount = 0
    for road in areaRoads:
        if road.Points == None:
            points = roads.CreatePointsForRoad(road)
            roads.SetRoadPoints(road, points)
            
        # Check for parallel points
        if road.ParallelPoints == [] or road.ParallelPoints == None:
            if not all:
                if calcCount > LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME:
                    continue
            
            boundingBox, parallelPoints, laneWidth = roads.CalculateParallelCurves(road)
            if parallelPoints == [] or parallelPoints == None:
                parallelPoints = [[(0, 0), (0, 0)], [(0, 0), (0, 0)]]
            road.ParallelPoints = parallelPoints
            road.LaneWidth = laneWidth
            road.BoundingBox = boundingBox
            roads.SetRoadParallelData(road, parallelPoints, laneWidth, boundingBox)
            calcCount += 1

    if calcCount != 0:
        return True
    else:
        return False
    
# MARK: Bounds
def CheckIfInBoundingBox(boundingBox, x, y):
    try:
        if x >= boundingBox[0][0] and x <= boundingBox[1][0] and y >= boundingBox[0][1] and y <= boundingBox[1][1]:
            return True
        return False
    except:
        return False
    
# MARK: Distance
def GetDistanceToRoad(road, x, y):
    try:
        # Calculate the middle from the bounding box
        roadStart = [road.StartNode.X, road.StartNode.Z]
        roadEnd = [road.EndNode.X, road.EndNode.Z]
        distanceEnd = math.sqrt((roadEnd[0] - x)**2 + (roadEnd[1] - y)**2)
        distanceStart = math.sqrt((roadStart[0] - x)**2 + (roadStart[1] - y)**2)
        return min(distanceEnd, distanceStart)
    except:
        return sys.maxsize
    

def RecalculateLanes(road, x, y ):
    custom_offset = GetOffset(road)

    # Get the offset of the next road
    try:
        roadNext = road.EndNode.ForwardItem
        custom_offset_next = GetOffset(roadNext)
    except:
        custom_offset_next = custom_offset
        
    # Get the offset of the last road
    try:
        roadPrev = road.StartNode.BackwardItem
        custom_offset_prev = GetOffset(roadPrev)
    except:
        custom_offset_prev = custom_offset
        
    next_offset = custom_offset
    side = 0
    if custom_offset_next > custom_offset:
        next_offset = custom_offset_next
        side = 0
        
    elif custom_offset_prev > custom_offset:
        next_offset = custom_offset_prev
        side = 1
        
        
    # Calculate the percentage we are to the end of the road
    startPoint = road.StartNode
    endPoint = road.EndNode
    distanceToEnd = math.sqrt((endPoint.X - x)**2 + (endPoint.Z - y)**2)
    distanceToStart = math.sqrt((startPoint.X - x)**2 + (startPoint.Z - y)**2)
    percentage = distanceToStart / (distanceToStart + distanceToEnd)
    # Calculate a point on the road at the specified percentage
    point = roads.CreatePointForRoad(road, percentage)
    # Add the point to the road at the specific spot
    existingPoints = road.Points
    # Calculate the percentage of each point
    counter = 0
    for i in range(len(existingPoints)):
        existingPoint = existingPoints[i]
        distanceToEnd = math.sqrt((endPoint.X - existingPoint[0])**2 + (endPoint.Z - existingPoint[1])**2)
        distanceToStart = math.sqrt((startPoint.X - existingPoint[0])**2 + (startPoint.Z - existingPoint[1])**2)
        pointPercentage = distanceToStart / (distanceToStart + distanceToEnd)
        if pointPercentage > percentage:
            break
        counter = i
    # Insert the point
    existingPoints.insert(counter, (point[0], point[2]))
    
    lanes = calc.calculate_lanes(existingPoints, 4.5, len(road.RoadLook.lanesLeft), len(road.RoadLook.lanesRight), custom_offset=custom_offset, next_offset=next_offset, side=side)
    newPoints = lanes['left'] + lanes['right']
    return newPoints