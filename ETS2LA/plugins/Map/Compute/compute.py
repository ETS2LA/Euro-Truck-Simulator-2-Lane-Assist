from GameData.prefabItems import PrefabItem
import GameData.prefabItems as prefabItems
from GameData.roads import Road, GetOffset
import GameData.roads as roads
from GameData import calc
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

# MARK: Closest Lane
def FindClosestLane(x, y, z, item, data, lanes=None):
    try:
        if lanes != None:
            lanes = lanes
        elif type(item) == Road:
            lanes = item.ParallelPoints
        elif type(item) == PrefabItem:
            lanes = [[(lane[0], lane[1]), (lane[2], lane[3])] for lane in item.NavigationLanes]
        
        laneFirstPoints = [lane[0] for lane in lanes]
        laneLastPoints = [lane[-1] for lane in lanes]
        
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
                
                if type(item) == PrefabItem or len(lanes) == 1:
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
                    # startDistance = math.sqrt((firstPoint[0] - x)**2 + (firstPoint[1] - y)**2)
                    # endDistance = math.sqrt((secondPoint[0] - x)**2 + (secondPoint[1] - y)**2)
                    # sumDistance = startDistance + endDistance
                    # secondPointPercentage = startDistance / sumDistance
                    
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
                    
            return closestLane, negate, item, closestLaneDistance, closestPoint
        else:
            return closestLane
    except:
        return None, None, None, sys.maxsize, None
    
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
    
    
# MARK: Closest item
def GetClosestRoadOrPrefabAndLane(data):
    x, y, z = data["api"]["truckPlacement"]["coordinateX"], data["api"]["truckPlacement"]["coordinateZ"], data["api"]["truckPlacement"]["coordinateY"]
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
    closestPoint = None
    allPoints = []
    closestLanes = []
    closestDistance = sys.maxsize
    closestNegate = False
    for item in inBoundingBox:
        if SMOOTH_CURVES and type(item) == Road:
            lanes = RecalculateLanes(item, x, y)
        else:
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