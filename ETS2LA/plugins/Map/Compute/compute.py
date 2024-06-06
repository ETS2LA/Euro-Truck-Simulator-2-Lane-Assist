import GameData.roads as roads
from GameData.roads import Road
import GameData.prefabItems as prefabItems
from GameData.prefabItems import PrefabItem
import sys
import logging
import math
import time
import threading

LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME = 10

calculatingPrefabs = False
calculatingRoads = False
lastRoadCoords = None
lastPrefabCoords = None
closeRoads = []
closePrefabs = []
# MARK: Get Roads
def GetRoads(data, wait=False):
    global lastRoadCoords, closeRoads
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]

    tileCoords = roads.GetTileCoordinates(x, y)
    
    def GetRoadThread(x, y, noWait=False):
        global closeRoads, calculatingRoads
        # Get the roads in the current area
        areaRoads = []
        areaRoads += roads.GetRoadsInTileByCoordinates(x, y)
        
        # Also get the roads in the surrounding tiles
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaRoads += roads.GetRoadsInTileByCoordinates(x, y + 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaRoads += roads.GetRoadsInTileByCoordinates(x, y - 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y + 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y - 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y + 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y - 1000)
        
        closeRoads = areaRoads
        calculatingRoads = False
        
        #print(f"Found {len(closeRoads)} roads")
        
    if tileCoords != lastRoadCoords or lastRoadCoords == None or closeRoads == [] and calculatingRoads == False:
        tileThread = threading.Thread(target=GetRoadThread, args=(x, y), kwargs={"noWait": wait})
        tileThread.start()
        lastRoadCoords = tileCoords
        
        if wait:
            tileThread.join()
        
        return closeRoads
    else:
        return closeRoads

# MARK: Get Prefabs
def GetPrefabs(data, wait=False):
    global lastPrefabCoords, closePrefabs, calculatingPrefabs
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    
    tileCoords = prefabItems.GetTileCoordinates(x, y)
    
    def GetPrefabThread(x, y, noWait=False):
        global closePrefabs, calculatingPrefabs
        # Get the roads in the current area
        areaItems = []
        areaItems += prefabItems.GetItemsInTileByCoordinates(x, y)
        
        # Also get the roads in the surrounding tiles
        areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaItems += prefabItems.GetItemsInTileByCoordinates(x, y + 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaItems += prefabItems.GetItemsInTileByCoordinates(x, y - 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y + 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y - 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y + 1000)
        if not noWait: time.sleep(0.01) # Relieve CPU
        areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y - 1000)
        
        closePrefabs = areaItems
        calculatingPrefabs = False
        
        #print(f"Found {len(closePrefabs)} prefabs")
    
    if tileCoords != lastPrefabCoords or lastPrefabCoords == None or closePrefabs == [] and calculatingPrefabs == False:
        prefabThread = threading.Thread(target=GetPrefabThread, args=(x, y), kwargs={"noWait": wait})
        prefabThread.start()
        lastPrefabCoords = tileCoords
        
        if wait:
            prefabThread.join()
        
        return closePrefabs
    else:
        return closePrefabs

# MARK: Parallel Points
def CalculateParallelPointsForRoads(areaRoads, all=False):
    calcCount = 0
    for road in areaRoads:
        if road.Points == None:
            points = roads.CreatePointsForRoad(road)
            roads.SetRoadPoints(road, points)
            
        
        # Check for parallel points
        if road.ParallelPoints == []:
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

# MARK: Closest Lane
def FindClosestLane(x, y, item, data):
    try:
        if type(item) == Road:
            lanes = item.ParallelPoints
        elif type(item) == PrefabItem:
            lanes = [[(lane[0], lane[1]), (lane[2], lane[3])] for lane in item.NavigationLanes]
        
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
        
        closestPoint = None
        for i in range(len(interpolatedPoints)):
            point = interpolatedPoints[i]
            distance = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
            if distance < closestLaneDistance:
                closestLane = pointsLanes[i]
                closestPoint = point
                closestLaneDistance = distance
           
        if type(item) == PrefabItem:
            # Convert the closest lane back to the original format
            closestLane = (closestLane[0][0], closestLane[0][1], closestLane[1][0], closestLane[1][1])
        
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
                    
            return closestLane, negate, item, closestLaneDistance
        else:
            return closestLane
    except:
        return None, None, None, sys.maxsize
    
# MARK: Point side
def CheckIfPointIsToTheRight(data, point):
    """Will check if the point is to the right or left of the truck."""
    x, y = data["api"]["truckPlacement"]["coordinateX"], data["api"]["truckPlacement"]["coordinateZ"]
    # From -1 to 1
    rotationX = data["api"]["truckPlacement"]["rotationX"]
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

    
# MARK: Closest item
def GetClosestRoadOrPrefabAndLane(data):
    x, y = data["api"]["truckPlacement"]["coordinateX"], data["api"]["truckPlacement"]["coordinateZ"]
    inBoundingBox = []
    for road in closeRoads:
        if CheckIfInBoundingBox(road.BoundingBox, x, y):
            inBoundingBox.append(road)
    
    for prefab in closePrefabs:
        if CheckIfInBoundingBox(prefab.BoundingBox, x, y):
            inBoundingBox.append(prefab)
            
    #logging.info(f"Found {len(inBoundingBox)} items in bounding box")
            
    closestItem = None
    closestLane = None
    closestLanes = []
    closestDistance = sys.maxsize
    closestNegate = False
    for item in inBoundingBox:
        lane, negate, item, distance = FindClosestLane(x, y, item, data)
        closestLanes.append(lane)
        if distance < closestDistance:
            closestItem = item
            closestLane = lane
            closestDistance = distance
            closestNegate = negate
            
    if closestNegate: closestDistance = -closestDistance
    if closestDistance == sys.maxsize: closestDistance = 0
    closestType = type(closestItem)
    
    data = { 
        "map": {
            "closestItem": closestItem,
            "closestLane": closestLane,
            "closestDistance": closestDistance,
            "closestType": closestType,
            "inBoundingBox": inBoundingBox,
            "closestLanes": closestLanes
        }
    }
    
    return data