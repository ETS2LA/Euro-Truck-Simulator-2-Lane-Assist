import GameData.roads as roads
from GameData.roads import Road
import GameData.prefabItems as prefabItems
from GameData.prefabItems import PrefabItem
import sys
import logging
import math

LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME = 10

lastCoords = None
closeRoads = []
closePrefabs = []
def GetRoads(data):
    global lastCoords, closeRoads
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]

    tileCoords = roads.GetTileCoordinates(x, y)
    
    if tileCoords != lastCoords or lastCoords == None or closeRoads == []:
        lastCoords = tileCoords
    else:
        return closeRoads
    
    # Get the roads in the current area
    areaRoads = []
    areaRoads = roads.GetRoadsInTileByCoordinates(x, y)
    
    # Also get the roads in the surrounding tiles
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y)
    areaRoads += roads.GetRoadsInTileByCoordinates(x, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x, y - 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y - 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y - 1000)
    
    closeRoads = areaRoads
    print(f"Found {len(closeRoads)} roads")
    
    return closeRoads

def GetPrefabs(data):
    global lastCoords, closePrefabs
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    
    tileCoords = roads.GetTileCoordinates(x, y)
    
    if tileCoords != lastCoords or lastCoords == None or closePrefabs == []:
        lastCoords = tileCoords
    else:
        return closePrefabs
    
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
    
    closePrefabs = areaItems
    
    print(f"Found {len(closePrefabs)} prefabs")
    
    return closePrefabs

def CalculateParallelPointsForRoads(areaRoads):
    calcCount = 0
    for road in areaRoads:
        if road.Points == None:
            points = roads.CreatePointsForRoad(road)
            roads.SetRoadPoints(road, points)
            
        
        # Check for parallel points
        if road.ParallelPoints == []:
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
    
def CheckIfInBoundingBox(boundingBox, x, y):
    try:
        if x >= boundingBox[0][0] and x <= boundingBox[1][0] and y >= boundingBox[0][1] and y <= boundingBox[1][1]:
            return True
        return False
    except:
        return False
    
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
    
def FindClosestLane(x, y, item):
    try:
        if type(item) == Road:
            lanes = item.ParallelPoints
        elif type(item) == PrefabItem:
            lanes = item.CurvePoints
        closestLane = None
        closestLaneDistance = 999
        # First get the players percentage of each lane
        lanePercentages = []
        for lane in lanes:
            if lane == []: continue
            
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
            
        # Now for each lane interpolate the point that maches the players percentage
        interpolatedPoints = []
        pointsLanes = []
        for lane in lanes:
            try:
                if lane == []: continue
                
                # Get the two points closest to the player
                firstPoint = None
                firstPointDistance = 999999
                secondPoint = None
                secondPointDistance = 999999
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
                
                if firstPoint == None or secondPoint == None:
                    continue
                
                # Get the percentage of the first point
                startDistance = math.sqrt((firstPoint[0] - x)**2 + (firstPoint[1] - y)**2)
                endDistance = math.sqrt((secondPoint[0] - x)**2 + (secondPoint[1] - y)**2)
                sumDistance = startDistance + endDistance
                firstPointPercentage = startDistance / sumDistance
                
                # Get the percentage of the second point
                startDistance = math.sqrt((firstPoint[0] - x)**2 + (firstPoint[1] - y)**2)
                endDistance = math.sqrt((secondPoint[0] - x)**2 + (secondPoint[1] - y)**2)
                sumDistance = startDistance + endDistance
                secondPointPercentage = startDistance / sumDistance
                
                # Interpolate the point
                newPoint = [0, 0]
                newPoint[0] = firstPoint[0] + (secondPoint[0] - firstPoint[0]) * firstPointPercentage
                newPoint[1] = firstPoint[1] + (secondPoint[1] - firstPoint[1]) * firstPointPercentage
                
                interpolatedPoints.append(newPoint)
                pointsLanes.append(lane)
            except:
                continue
        
        # Get the center of the interpolated points
        center = [0, 0]
        for i in range(len(interpolatedPoints)):
            center[0] += interpolatedPoints[i][0]
            center[1] += interpolatedPoints[i][1]
        
        center[0] = center[0] / len(interpolatedPoints)
        center[1] = center[1] / len(interpolatedPoints)
        
        closestPointDistanceToCenter = 999
        
        for i in range(len(interpolatedPoints)):
            point = interpolatedPoints[i]
            distance = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
            if distance < closestLaneDistance:
                closestLane = pointsLanes[i]
                closestLaneDistance = distance
                closestPointDistanceToCenter = math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2)
            
        
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
                    
            # Get the truck distance to the center of the interpolated points
            distance = math.sqrt((center[0] - x)**2 + (center[1] - y)**2)
            
            if distance > closestPointDistanceToCenter:
                closestLaneDistance = -closestLaneDistance
                    
            return closestLane, index, item, closestLaneDistance
        else:
            return closestLane
    except:
        return None, None, None, 999
    
def GetClosestRoadOrPrefabAndLane(data):
    x, y = data["api"]["truckPlacement"]["coordinateX"], data["api"]["truckPlacement"]["coordinateZ"]
    inBoundingBox = []
    for road in closeRoads:
        if CheckIfInBoundingBox(road.BoundingBox, x, y):
            inBoundingBox.append(road)
    
    for prefab in closePrefabs:
        if CheckIfInBoundingBox(prefab.BoundingBox, x, y):
            inBoundingBox.append(prefab)
            
    logging.info(f"Found {len(inBoundingBox)} items in bounding box")
            
    closestItem = None
    closestLane = None
    closestDistance = sys.maxsize
    for item in inBoundingBox:
        closestLane, index, item, distance = FindClosestLane(x, y, item)
        if distance < closestDistance:
            closestItem = item
            closestLane = closestLane
            closestDistance = distance
            
    closestType = type(closestItem)
    return closestItem, closestLane, closestDistance, closestType