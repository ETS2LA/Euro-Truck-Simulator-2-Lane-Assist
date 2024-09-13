from ETS2LA.plugins.Map.GameData.prefabItems import PrefabItem, GetPrefabItemByUid
from ETS2LA.plugins.Map.GameData.roads import Road, GetRoadByUid
import ETS2LA.plugins.Map.GameData.nodes as Nodes
import ETS2LA.backend.settings as settings
import Compute.compute as compute
from typing import cast
import numpy as np
import logging
import math
import json
import time

RouteLength = 3
OFFSET_MULTIPLIER = settings.Get("Map", "OffsetMultiplier", 2)
ANGLE_MULTIPLIER = settings.Get("Map", "AngleMultiplier", 1)
DISTANCE_FOR_LANE_CHANGE = settings.Get("Map", "PointsForLaneChange", 50)
visualize = None

#MARK: Classes
class RouteItem:
    item: PrefabItem | Road
    points: list[list[float]]
    removedPoints: list[list[float]]
    lane: int
    length: float
    endPosition: list[float]
    startPosition: list[float]
    inverted: bool
    
    def __init__(self, item, points, lane, length, endPosition, startPosition, inverted):
        self.item = item
        self.points = points
        self.lane = lane
        self.length = length
        self.endPosition = endPosition
        self.startPosition = startPosition
        self.inverted = inverted
        self.removedPoints = []
    
    def DiscardPointsBehindTheTruck(self, truckX, truckZ, rotation):
        newPoints = []
        truckForwardVector = [-math.sin(rotation), -math.cos(rotation)]
        for point in self.points:
            pointForwardVector = [point[0] - truckX, point[1] - truckZ]
            angle = np.arccos(np.dot(truckForwardVector, pointForwardVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(pointForwardVector)))
            angle = math.degrees(angle)
            if angle > 90 or angle < -90:
                self.removedPoints.append(point)
                continue
            newPoints.append(point)      
        
        return newPoints
    
    def __str__(self):
        return f"RouteItem: {self.item.Uid} of type {'Road' if type(self.item) == Road else 'PrefabItem'}"
        
    def __repr__(self):
        return f"RouteItem: {self.item.Uid} of type {'Road' if type(self.item) == Road else 'PrefabItem'}"

Route : list[RouteItem] = []

# MARK: Settings
def LoadSettings():
    global OFFSET_MULTIPLIER
    global ANGLE_MULTIPLIER
    
    OFFSET_MULTIPLIER = settings.Get("Map", "OffsetMultiplier", 2)
    ANGLE_MULTIPLIER = settings.Get("Map", "AngleMultiplier", 1)

settings.Listen("Map", LoadSettings)

# MARK: References
def GetItemAndLaneReferences(closestData, MapUtils, truckX, truckZ):
    global Route
    
    closestItem = closestData["closestItem"]
    closestLane = closestData["closestLane"]
    if closestItem is None:
        return None
    
    #logging.warning(closestLane)
    
    if type(closestItem) == Road:
        closestItem = GetRoadByUid(closestItem.Uid)
        closestItem = cast(Road, closestItem) # Get intellisense
        if closestItem is None: return None
        length = 0
        for i in range(len(closestItem.ParallelPoints)):
            length += np.linalg.norm(np.array(closestItem.ParallelPoints[i][1]) - np.array(closestItem.ParallelPoints[i][0]))
        lane = closestItem.ParallelPoints.index(closestData["closestLane"])
        
        points = closestItem.ParallelPoints[lane]
        needInvert = NeedInvert(closestItem.ParallelPoints[lane], truckX, truckZ)
        if needInvert:
            points = points[::-1]
            
        
        routeItem = RouteItem(
            item = closestItem,
            points = points,
            lane = lane,
            length = length,
            endPosition = closestItem.ParallelPoints[lane][-1],
            startPosition = closestItem.ParallelPoints[lane][0],
            inverted = needInvert
        )
        
        Route.append(routeItem)
        
    elif type(closestItem) == PrefabItem:
        for i, node in enumerate(closestItem.Nodes):
            if type(node) == int:
                node = Nodes.GetNodeByUid(node)
                closestItem.Nodes[i] = node
            if type(node) == dict:
                node = Nodes.GetNodeByUid(node["Uid"])
                closestItem.Nodes[i] = node
        if type(closestItem.StartNode) == int:
            closestItem.StartNode = Nodes.GetNodeByUid(closestItem.StartNode)
        if type(closestItem.EndNode) == int:
            closestItem.EndNode = Nodes.GetNodeByUid(closestItem.EndNode)
        
        closestLane = closestData["closestLane"]
        laneIndex = closestItem.CurvePoints.index(closestLane)
        
        length = 0
        for i in range(len(closestItem.CurvePoints[laneIndex])-1):
            length += np.linalg.norm(np.array(closestItem.CurvePoints[laneIndex][i+1]) - np.array(closestItem.CurvePoints[laneIndex][i]))
        
        routeItem = RouteItem(
            item = closestItem,
            points = closestItem.CurvePoints[laneIndex],
            lane = laneIndex,
            length = length,
            endPosition = closestItem.CurvePoints[laneIndex][-1],
            startPosition = closestItem.CurvePoints[laneIndex][0],
            inverted = False
        )
        
        Route.append(routeItem)
        
        #logging.warning(closestData["closestLane"])
        
        #logging.warning(closestItem.json())
        #closestItem = GetPrefabItemByUid(closestItem.Uid)
        #CurrentItem = closestItem
        #ClosestLane = closestItem.CurvePoints.index(closestData["closestLane"])

# MARK: Discard points
def DiscardPointsBehindTheTruck(points, truckX, truckZ, rotation):
    newPoints = []
    truckForwardVector = [-math.sin(rotation), -math.cos(rotation)]
    for point in points:
        pointForwardVector = [point[0] - truckX, point[1] - truckZ]
        # angle = np.arccos(np.dot(truckForwardVector, pointforwardVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(pointforwardVector)))
        angle = np.arccos(np.dot(truckForwardVector, pointForwardVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(pointForwardVector)))
        angle = math.degrees(angle)
        if angle > 90 or angle < -90:
            continue
        newPoints.append(point)   
        
    try:
        if DistanceBetweenPoints([truckX, truckZ], newPoints[0]) > DistanceBetweenPoints([truckX, truckZ], newPoints[-1]):
            newPoints = newPoints[::-1]
    except:
        logging.exception("Failed to check if the points should be inverted")
        pass
    
    return newPoints

# MARK: Check inversion
def NeedInvert(points, truckX, truckY):
    if len(points) < 2:
        return False
    
    firstPoint = points[0]
    lastPoint = points[len(points)-1]
    middlePoint = points[len(points)//2]
    
    # Check if the last point and the middle points are closer than the first point
    DistanceFirst = math.sqrt((truckX - firstPoint[0]) ** 2 + (truckY - firstPoint[1]) ** 2)
    DistanceLast = math.sqrt((truckX - lastPoint[0]) ** 2 + (truckY - lastPoint[1]) ** 2)
    DistanceMiddle = math.sqrt((truckX - middlePoint[0]) ** 2 + (truckY - middlePoint[1]) ** 2)
    
    #logging.warning(f"DistanceFirst: {DistanceFirst}, DistanceMiddle: {DistanceMiddle}, DistanceLast: {DistanceLast}")
    
    if DistanceFirst > DistanceLast:
        return True
    
    return False

# MARK: Next item
def GetNextItem(data : dict, truckX, truckZ, rotation, MapUtils, knownItem=None, nextItem=None) -> RouteItem:
    #logging.warning("Getting next item")
    # Check which node is to the front of the truck
    CurrentItem = Route[-1].item
    ClosestLane = Route[-1].lane
    
    if knownItem == None: 
        if type(CurrentItem) == Road:   
            BackwardNode = CurrentItem.EndNode
            ForwardNode = CurrentItem.StartNode
        
        
        if type(CurrentItem) == PrefabItem:
            if len(CurrentItem.Nodes) == 2:
                ForwardNode = CurrentItem.Nodes[0]
                BackwardNode = CurrentItem.Nodes[1]
            else:
                points = CurrentItem.CurvePoints[ClosestLane]
                ForwardNode = None
                ForwardNodeDistance = math.inf
                BackwardNode = None
                BackwardNodeDistance = math.inf
                for node in CurrentItem.Nodes:
                    frontDistance = math.sqrt((points[0][0] - node.X) ** 2 + (points[0][1] - node.Z) ** 2)
                    backDistance = math.sqrt((points[-1][0] - node.X) ** 2 + (points[-1][1] - node.Z) ** 2)
                    if frontDistance < backDistance:
                        if frontDistance < ForwardNodeDistance:
                            ForwardNodeDistance = frontDistance
                            ForwardNode = node
                    else:
                        if backDistance < BackwardNodeDistance:
                            BackwardNodeDistance = backDistance
                            BackwardNode = node
                                                
        
        BackwardPosition = [BackwardNode.X, BackwardNode.Z]
        ForwardPosition = [ForwardNode.X, ForwardNode.Z]
        
        #logging.warning(f"BackwardPosition: {BackwardPosition}, ForwardPosition: {ForwardPosition}")
        
        # Calculate the angles between the last 2 points of the current item and the nodes
        if len(Route[-1].points) < 2:
            return []
        if len(Route[-1].points) >= 4:
            PointVector = [Route[-1].points[-1][0] - Route[-1].points[-3][0], Route[-1].points[-1][1] - Route[-1].points[-3][1]]
        else:
            PointVector = [Route[-1].points[-1][0] - Route[-1].points[-2][0], Route[-1].points[-1][1] - Route[-1].points[-2][1]]
        BackwardAngle = np.arccos(np.dot(PointVector, [BackwardPosition[0] - Route[-1].points[-1][0], BackwardPosition[1] - Route[-1].points[-1][1]]) / (np.linalg.norm(PointVector) * np.linalg.norm([BackwardPosition[0] - Route[-1].points[-1][0], BackwardPosition[1] - Route[-1].points[-1][1]])))
        ForwardAngle = np.arccos(np.dot(PointVector, [ForwardPosition[0] - Route[-1].points[-1][0], ForwardPosition[1] - Route[-1].points[-1][1]]) / (np.linalg.norm(PointVector) * np.linalg.norm([ForwardPosition[0] - Route[-1].points[-1][0], ForwardPosition[1] - Route[-1].points[-1][1]])))
        # BackwardAngle = np.arccos(np.dot([BackwardPosition[0] - truckX, BackwardPosition[1] - truckZ], [math.sin(rotation), math.cos(rotation)]) / (np.linalg.norm([BackwardPosition[0] - truckX, BackwardPosition[1] - truckZ]) * np.linalg.norm([math.sin(rotation), math.cos(rotation)])))
        # ForwardAngle = np.arccos(np.dot([ForwardPosition[0] - truckX, ForwardPosition[1] - truckZ], [math.sin(rotation), math.cos(rotation)]) / (np.linalg.norm([ForwardPosition[0] - truckX, ForwardPosition[1] - truckZ]) * np.linalg.norm([math.sin(rotation), math.cos(rotation)])))

        if BackwardAngle > ForwardAngle:
            #logging.warning("Backward node is closer")
            NextNode = ForwardNode
        else:
            #logging.warning("Forward node is closer")
            NextNode = BackwardNode
            
        ForwardItem = NextNode.ForwardItem
        BackwardItem = NextNode.BackwardItem
        
        if ForwardItem is None and BackwardItem is None:
            return []
        elif ForwardItem is None:
            #logging.warning("Forward item is none")
            NextItem = BackwardItem
        elif BackwardItem is None:
            #logging.warning("Backward item is none")
            NextItem = ForwardItem
        else:
            ForwardUid = ForwardItem.Uid
            BackwardUid = BackwardItem.Uid
            
            #logging.warning(f"ForwardUid: {ForwardUid}, BackwardUid: {BackwardUid}")
            #logging.warning(f"CurrentItemUid: {CurrentItem.Uid}")
            #if len(Route) > 1:
            #    logging.warning(f"PreviousItemUid: {Route[-2].item.Uid}")
            
            if ForwardUid == CurrentItem.Uid:
                #logging.warning("Selecting backward item")
                NextItem = BackwardItem
            else:
                #logging.warning("Selecting forward item")
                NextItem = ForwardItem
                
            if NextItem is None:
                return []
            
        if NextItem.Uid == CurrentItem.Uid:
            return []
        
    else:
        NextItem = knownItem
        
    if type(NextItem) == Road:
        #logging.warning("Next item is a road")
        NextItem = cast(Road, NextItem) # Get intellisense
        Lanes = NextItem.ParallelPoints
        
        CurrentEndPoint = Route[-1].points[-1]
        
        closestLaneId = math.inf
        closestLaneDistance = math.inf
        
        for i in range(len(Lanes)):
            laneStart = Lanes[i][0]
            distance = math.sqrt((CurrentEndPoint[0] - laneStart[0]) ** 2 + (CurrentEndPoint[1] - laneStart[1]) ** 2)
            if distance < closestLaneDistance:
                closestLaneDistance = distance
                closestLaneId = i
                
        for i in range(len(Lanes)):
            laneEnd = Lanes[i][-1]
            distance = math.sqrt((CurrentEndPoint[0] - laneEnd[0]) ** 2 + (CurrentEndPoint[1] - laneEnd[1]) ** 2)
            if distance < closestLaneDistance:
                closestLaneDistance = distance
                closestLaneId = i
                
        if closestLaneId == math.inf:
            return []
        
        logging.warning(f"ClosestLaneId: {closestLaneId}")
        logging.warning(f"ClosestLaneDistance: {closestLaneDistance}")
        
        closestPoints = Lanes[closestLaneId]
        
        needInvert = NeedInvert(closestPoints, truckX, truckZ)
        if needInvert:
            closestPoints = closestPoints[::-1]
        
        length = 0
        for i in range(len(closestPoints)-1):
            length += np.linalg.norm(np.array(closestPoints[i+1]) - np.array(closestPoints[i]))
        
        routeItem = RouteItem(
            item = NextItem,
            points = closestPoints,
            lane = closestLaneId,
            length = length,
            endPosition = closestPoints[-1],
            startPosition = closestPoints[0],
            inverted = needInvert
        )
        
        #logging.warning(f"RouteItem created for road")
        
        return routeItem
        
    elif type(NextItem) == PrefabItem:
        followingItem = None
        followingItemStartNode = None
        followingItemEndNode = None
        if nextItem != None:
            followingItem = nextItem
            if type(followingItem) == Road:
                followingItem = cast(Road, followingItem)
                followingItemStartNode = followingItem.StartNode
                followingItemEndNode = followingItem.EndNode
            if type(followingItem) == PrefabItem:
                followingItem = cast(PrefabItem, followingItem)
                followingItemStartNode = followingItem.Nodes[0]
                followingItemEndNode = followingItem.Nodes[-1]
            
            visualize.SetDebugPoints([[followingItemStartNode.X, followingItemStartNode.Z], [followingItemEndNode.X, followingItemEndNode.Z]])
        
        #logging.warning("Next item is a prefab")
        NextItem = cast(PrefabItem, NextItem) # Get intellisense
        Curves = NextItem.CurvePoints
        Lanes = NextItem.Prefab.PrefabLanes
        
        if NeedInvert(Route[-1].points, truckX, truckZ):
            #logging.warning("Inverting last item points")
            CurrentEndPoint = Route[-1].points[::-1][-1]
        else:
            CurrentEndPoint = Route[-1].points[-1]
            
        #logging.warning(f"CurrentEndPoint: {CurrentEndPoint}")

        closestLaneIds = [math.inf]
        closestLaneDistance = math.inf
        
        for i in range(len(Lanes)):
            laneStart = Curves[i][0]
            ##logging.warning(f"laneStart: {laneStart}")
            ##logging.warning(f"CurrentEndPoint: {CurrentEndPoint}")
            distance = math.sqrt((CurrentEndPoint[0] - laneStart[0]) ** 2 + (CurrentEndPoint[1] - laneStart[1]) ** 2)
            ##logging.warning(f"Distance: {distance}")
            if distance < closestLaneDistance:
                closestLaneDistance = distance
                closestLaneIds = [i]
            elif distance == closestLaneDistance:
                closestLaneIds.append(i)
                
        for i in range(len(Lanes)):
            laneEnd = Curves[i][-1]
            distance = math.sqrt((CurrentEndPoint[0] - laneEnd[0]) ** 2 + (CurrentEndPoint[1] - laneEnd[1]) ** 2)
            if distance < closestLaneDistance:
                closestLaneDistance = distance
                closestLaneIds = [i]
            elif distance == closestLaneDistance:
                closestLaneIds.append(i)
                
        #logging.warning(f"ClosestLaneId: {closestLaneId}")
        #logging.warning(f"ClosestLaneDistance: {closestLaneDistance}")
                
        if closestLaneIds == [math.inf]:
            return [] 
        
        if followingItem == None:
            wantedDirection = "right" if data["api"]["truckBool"]["blinkerLeftActive"] else "left" if data["api"]["truckBool"]["blinkerRightActive"] else "forward"
            if len(closestLaneIds) > 1:
                #logging.warning(f"Multiple closest lanes: {closestLaneId}")
                if wantedDirection == 'forward':
                    # Check which of the lanes is the most forward
                    forwardestLane = math.inf
                    forwardestLaneDot = math.inf
                    for i in closestLaneIds:
                        laneEnd = Curves[i][-1]
                        vector = [laneEnd[0] - CurrentEndPoint[0], laneEnd[1] - CurrentEndPoint[1]]
                        dot = np.dot([math.sin(rotation), math.cos(rotation)], vector)
                        if dot < forwardestLaneDot:
                            forwardestLaneDot = dot
                            forwardestLane = i
                    
                    closestLaneIds = forwardestLane
                if wantedDirection == "right":
                    # Check which of the lanes is the most right
                    rightestLane = math.inf
                    rightestLaneDot = math.inf
                    for i in closestLaneIds:
                        laneEnd = Curves[i][-1]
                        vector = [laneEnd[0] - CurrentEndPoint[0], laneEnd[1] - CurrentEndPoint[1]]
                        dot = np.dot([math.cos(rotation), -math.sin(rotation)], vector)
                        if dot < rightestLaneDot:
                            rightestLaneDot = dot
                            rightestLane = i
                    
                    closestLaneIds = rightestLane
                if wantedDirection == "left":
                    # Check which of the lanes is the most left
                    leftestLane = math.inf
                    leftestLaneDot = math.inf
                    for i in closestLaneIds:
                        laneEnd = Curves[i][-1]
                        vector = [laneEnd[0] - CurrentEndPoint[0], laneEnd[1] - CurrentEndPoint[1]]
                        dot = np.dot([-math.cos(rotation), math.sin(rotation)], vector)
                        if dot < leftestLaneDot:
                            leftestLaneDot = dot
                            leftestLane = i
                    
                    closestLaneIds = leftestLane
                    
            else:
                closestLaneIds = closestLaneIds[0]
        else:
            if len(closestLaneIds) == 1:
                closestLaneIds = closestLaneIds[0]
            else:
                logging.warning(f"Multiple closest lanes: {closestLaneIds}")
                logging.warning(f"FollowingItemStart {followingItemStartNode.X}, {followingItemStartNode.Z}")
                logging.warning(f"FollowingItemEnd {followingItemEndNode.X}, {followingItemEndNode.Z}")
                # find the lane that brings us to the following item
                closestLaneDistance = math.inf
                for i in closestLaneIds:
                    laneEnd = Curves[i][-1]
                    
                    distance = math.sqrt((laneEnd[0] - followingItemStartNode.X) ** 2 + (laneEnd[1] - followingItemStartNode.Z) ** 2)
                    if distance < closestLaneDistance:
                        closestLaneDistance = distance
                        closestLaneIds = i
                        
                    distance = math.sqrt((laneEnd[0] - followingItemEndNode.X) ** 2 + (laneEnd[1] - followingItemEndNode.Z) ** 2)
                    if distance < closestLaneDistance:
                        closestLaneDistance = distance
                        closestLaneIds = i
                    
        
        logging.warning(f"ClosestLaneId: {closestLaneIds}")
        logging.warning(f"ClosestLaneDistance: {closestLaneDistance}")
        
        closestPoints = Curves[closestLaneIds]
        
        if NeedInvert(closestPoints, truckX, truckZ):
            closestPoints = closestPoints[::-1]
        
        length = 0
        for i in range(len(closestPoints)-1):
            length += np.linalg.norm(np.array(closestPoints[i+1]) - np.array(closestPoints[i]))
        
        routeItem = RouteItem(
            item = NextItem,
            points = closestPoints,
            lane = closestLaneIds,
            length = length,
            endPosition = closestPoints[-1],
            startPosition = closestPoints[0],
            inverted = False
        )
        
        #logging.warning(f"RouteItem created for prefab")
        
        return routeItem
    
# MARK: Path Instruct
currentPathIndex = 0
def GetPathInstruct(path, apiData):
    # Human readable instructions in json format
    # [{
    #   "direction": "left",
    #   "distance": 100 
    # }]
    data = []
    startIndex = currentPathIndex - len(Route)
    curDistance = 0
    totalDistance = 0
    lastType = Road
    for i in range(startIndex, len(path)):
        pathItem = path[i]
        if type(pathItem.item) == Road:
            curDistance += pathItem.length
            totalDistance += pathItem.length
            if i == startIndex:
                # Remove the distance from the first item
                truckX = apiData["api"]["truckPlacement"]["coordinateX"]
                truckZ = apiData["api"]["truckPlacement"]["coordinateZ"]
                curDistance -= DistanceBetweenPoints([truckX, truckZ], [pathItem.x, pathItem.z])
        elif type(pathItem.item) == PrefabItem:
            data.append({
                        "direction": "turn",
                        "distance": curDistance if curDistance > 0 else 0,
                    })
            curDistance = pathItem.length
    
    if len(data) > 0:
        data.append({
            "totalDistance": totalDistance
        })
    
    #print(data[:3])
    return data
    
        
# MARK: External
# AKA. functions that are called from the main file,
# the only reason they are here is for auto updating on code changes
def DistanceBetweenPoints(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def map_curvature_to_speed_effect(curvature):
    factor = 0.007
    min_effect, max_effect = 0.0, 0.7
    effect = min(max(curvature * factor, min_effect), max_effect)
    return effect

def CalculateCurvature(points):
    if len(points) < 3:  # Need at least 3 points to calculate curvature
        return 0
    
    curvatures = []
    try:
        for i in range(1, len(points) - 1):
            vector1 = np.array(points[i]) - np.array(points[i - 1])
            vector2 = np.array(points[i + 1]) - np.array(points[i])
            dot_product = np.dot(vector1, vector2)
            norm_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)

            if norm_product == 0:
                angle = 0
            else:
                cos_angle = dot_product / norm_product
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                if angle > math.pi/2:
                    angle = math.pi - angle

            if not np.isnan(angle) and angle != 0:
                curvatures.append(angle)

        # Filter outliers using IQR
        try:
            q1, q3 = np.percentile(curvatures, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)
            filtered_curvatures = [x for x in curvatures if lower_bound <= x <= upper_bound]
            
            total_curvature = sum(filtered_curvatures)
            total_curvature = math.degrees(total_curvature)
            #print(f"Curvature: {total_curvature}", end="\r")
        except:
            total_curvature = sum(curvatures)
            total_curvature = math.degrees(total_curvature)
            #print(f"Curvature: {total_curvature}", end="\r")

        return total_curvature
    except Exception as e:
        logging.exception("Failed to calculate curvature")
        return 0

# MARK: Lane Change
def GenerateLaneChange(routeItem, truckX, truckZ, isRight, rotation, speed):
    returnPoints = []
    
    def GetPointLaneChangeDistance(point):
        return np.linalg.norm(np.array([point[0], point[1]]) - np.array([truckX, truckZ]))
    def EasingFunction(t): # in out cubic
        return t < 0.5 and 2 * t * t or 1 - math.pow(-2 * t + 2, 2) / 2
    
    if type(routeItem.item) != Road:
        logging.warning("You can only lane change on roads")
        return routeItem.points
    
    inverted = routeItem.inverted
    
    road = cast(Road, routeItem.item)
    lanesLeft = len(road.RoadLook.lanesLeft)
    lanesRight = len(road.RoadLook.lanesRight)
    curLane = routeItem.lane
    if inverted:
        wantedLane = curLane + 1 if isRight else curLane - 1
    else:
        wantedLane = curLane - 1 if isRight else curLane + 1
    curLaneSide = 1 if curLane < lanesLeft else -1
    wantedLaneSide = 1 if wantedLane < lanesLeft else -1
    if curLaneSide != wantedLaneSide:
        return routeItem.points
    
    if wantedLane < 0 or wantedLane >= lanesLeft + lanesRight:
        return routeItem.points
    
    curPoints = routeItem.points
    parallelPoints = road.ParallelPoints[wantedLane]
    if inverted:
        parallelPoints = parallelPoints[::-1]
        
    parallelPoints = DiscardPointsBehindTheTruck(parallelPoints, truckX, truckZ, rotation)
        
    startPercentage = 0
    if startPercentage > 1:
        startPercentage = 1
        
    speedPercentage = speed / 50
        
    # Check which point is over the lane change distance
    index = 0
    for point in curPoints:
        distance = GetPointLaneChangeDistance(point)
        if distance > DISTANCE_FOR_LANE_CHANGE * speedPercentage:
            break
        index += 1
        
    if GetPointLaneChangeDistance(curPoints[index]) < DISTANCE_FOR_LANE_CHANGE * speedPercentage:
        return routeItem.points 

    # Now create the inbetween points to lane change
    if index > 0:
        for i in range(index):
            percentage = i / index + startPercentage
            percentage = EasingFunction(percentage)
            
            if percentage > 1:
                percentage = 1
            if percentage < 0:
                percentage = 0
                
            point = (curPoints[i][0] + (parallelPoints[i][0] - curPoints[i][0]) * percentage, curPoints[i][1] + (parallelPoints[i][1] - curPoints[i][1]) * percentage, curPoints[i][2] + (parallelPoints[i][2] - curPoints[i][2]) * percentage)
            returnPoints.append(point)
    else:
        returnPoints.append(curPoints[0])
        
    # Then add the rest of the points on the side we changed to
    for i in range(index, len(parallelPoints)):
        returnPoints.append(parallelPoints[i])
        
    routeItem.lane = wantedLane
    return returnPoints

# MARK: No Nav
def HandleNoNav(data, MapUtils, Enabled):
    global Route
    global wasIndicating
    global allPoints
    
    data["map"]["allPoints"] = []
    data["map"]["endPoints"] = []
    data["map"]["angle"] = 0
    
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckY = data["api"]["truckPlacement"]["coordinateY"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    speed = data["api"]["truckFloat"]["speed"] * 3.6 # m/s -> km/h
    rotation = data["api"]["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
    
    if not Enabled:
        Route = []
        #return data
        
    indicating = data["api"]["truckBool"]["blinkerLeftActive"] or data["api"]["truckBool"]["blinkerRightActive"]
    indicatingRight = data["api"]["truckBool"]["blinkerRightActive"]
    if (indicating and not wasIndicating) or (not indicating and wasIndicating):
        logging.warning("Resetting route")
        wasIndicating = data["api"]["truckBool"]["blinkerLeftActive"] or data["api"]["truckBool"]["blinkerRightActive"]
        Route = Route[:1] # Reset the next item
        if len(Route) > 0 and indicating:
            try:
                Route[0].points = GenerateLaneChange(Route[0], truckX, truckZ, indicatingRight, rotation, speed)
            except:
                pass
    
    if len(Route) == 0:
        try:
            closestData = MapUtils.run(truckX, 0, truckZ)
        except:
            logging.exception("Failed to get closest data")
            return data
        try:
            GetItemAndLaneReferences(closestData, MapUtils, truckX, truckZ)
            if indicating:
                try:
                    Route[0].points = GenerateLaneChange(Route[0], truckX, truckZ, indicatingRight, rotation, speed)
                except:
                    pass
        except: 
            logging.exception("Failed to get item and lane references")
            Route = []
            return data
    
    if Route == []:
        return data
    
    for routeItem in Route:
        newPoints = DiscardPointsBehindTheTruck(routeItem.points, truckX, truckZ, rotation)
        for point in routeItem.points:
            if point not in newPoints:
                routeItem.removedPoints.append(point)
        routeItem.points = newPoints
        if routeItem.points == []:
            Route.remove(routeItem)
        
    tries = 0
    while len(Route) < RouteLength:
        try:
            if len(Route) == 0:
                try:
                    closestData = MapUtils.run(truckX, 0, truckZ)
                except: return data
                try:
                    GetItemAndLaneReferences(closestData, MapUtils, truckX, truckZ)
                except: return data
            
            item = GetNextItem(data, truckX, truckZ, rotation, MapUtils)
            if item == []:
                tries += 1
                if tries > 10:
                    break
                continue
            Route.append(item)
            #logging.warning(f"Route length: {len(Route)}")
        except:
            logging.exception("Failed to get next item")
            
        tries += 1
        if tries > 10:
            break
    
    #logging.warning(f"Route length: {len(Route)} tries: {tries}")
    
    allPoints = []
    itemsToRemove = []
    endPoints = []
    count = 0
    for routeItem in Route:
        try:
            allPoints.extend(routeItem.points)
            endPoints.append(routeItem.points[-1])
        except:
            itemsToRemove.append(routeItem)
        #data["map"]["endPoints"].append(routeItem.endPosition)
        count += 1
        
    for item in itemsToRemove:
        Route.remove(item)

    if allPoints == [] or Route == []:
        Route = []
        return data

    acceptedPoints = []
    lastPoint = allPoints[0]
    lastVector = np.array([-math.sin(rotation), -math.cos(rotation)])
    #print("Point checks")
    #print(lastVector)
    for i in range(1, len(allPoints)):
        vector1 = [allPoints[i][0] - lastPoint[0], allPoints[i][1] - lastPoint[1]]
        vector1 = vector1 / np.linalg.norm(vector1)
        #print(lastVector)
        #print(vector1)
        angle = np.arccos(np.dot(vector1, lastVector) / (np.linalg.norm(vector1) * np.linalg.norm(lastVector)))
        angle = math.degrees(angle)
        if np.array_equal(vector1, lastVector) or (angle < 90 and angle > -90):
            acceptedPoints.append(allPoints[i])
            lastVector = vector1
            lastPoint = allPoints[i]
        else:
            #print(angle)
            ...
    allPoints = acceptedPoints
    
    #print(Route)
    
    if allPoints == []:
        Route = []
        return data

    if len(Route) > 0:
        data["map"]["allPoints"] =  allPoints
        #print(data["map"]["allPoints"])
    else:
        data["map"]["allPoints"] = allPoints

    data["map"]["endPoints"] = endPoints
        
    if DistanceBetweenPoints([truckX, truckZ], allPoints[0]) > 1500:
        Route = []
        return data
    
    return None

currentPathIndex = 0
# MARK: Navigation
def HandleNav(data, MapUtils, Enabled, path):
    global currentPathIndex, Route
    global allPoints
    
    data["map"]["allPoints"] = []
    data["map"]["endPoints"] = []
    data["map"]["angle"] = 0
    
    if not Enabled:
        Route = []
        currentPathIndex = 0
        return data
    
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckY = data["api"]["truckPlacement"]["coordinateY"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    rotation = data["api"]["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
    
    if Route == []:
        # Find the closest item to the truck.
        closeNodes = []
        for node in path:
            if node.item == None:
                continue
            distance = math.sqrt((truckX - node.x) ** 2 + (truckZ - node.z) ** 2)
            if distance < 2000:
                closeNodes.append(node)
        
        closeRoads = []
        closePrefabs = []
        for node in closeNodes:
            if type(node.item) == Road:
                closeRoads.append(node.item)
            if type(node.item) == PrefabItem:
                closePrefabs.append(node.item)
        
        closeData = MapUtils.run(truckX, 0, truckZ, closeRoads, closePrefabs)
        if closeData["closestItem"] == None:
            return data
        
        closestNode = None
        for node in closeNodes:
            if node.item == closeData["closestItem"]:
                closestNode = node
                break
            
        currentPathIndex = path.index(closestNode)
        
        # Create first route item
        GetItemAndLaneReferences(closeData, MapUtils, truckX, truckZ)
        if Route == []:
            return data
        
    while len(Route) < 4:
        currentPathIndex += 1
        if currentPathIndex >= len(path):
            logging.warning("End of path")
            return data
        nextItem = GetNextItem(data, truckX, truckZ, 0, MapUtils, knownItem=path[currentPathIndex].item, nextItem=path[currentPathIndex+1].item)
        try:
            if nextItem != []:
                if nextItem.item.Uid not in [item.item.Uid for item in Route]:
                    Route.append(nextItem)
            else:
                logging.warning("Next item is empty")
                break
        except:
            logging.exception("Failed to add next item")
    
    
    for routeItem in Route:
        newPoints = DiscardPointsBehindTheTruck(routeItem.points, truckX, truckZ, rotation)
        for point in routeItem.points:
            if point not in newPoints:
                routeItem.removedPoints.append(point)
        routeItem.points = newPoints
        if routeItem.points == []:
            Route.remove(routeItem)
        
    allPoints = []    
    for i in range(len(Route)):
        allPoints.extend(Route[i].points)
            
    acceptedPoints = []
    lastPoint = allPoints[0]
    lastVector = np.array([-math.sin(rotation), -math.cos(rotation)])
    #print("Point checks")
    #print(lastVector)
    for i in range(1, len(allPoints)):
        vector1 = [allPoints[i][0] - lastPoint[0], allPoints[i][1] - lastPoint[1]]
        vector1 = vector1 / np.linalg.norm(vector1)
        #print(lastVector)
        #print(vector1)
        angle = np.arccos(np.dot(vector1, lastVector) / (np.linalg.norm(vector1) * np.linalg.norm(lastVector)))
        angle = math.degrees(angle)
        if np.array_equal(vector1, lastVector) or (angle < 90 and angle > -90):
            acceptedPoints.append(allPoints[i])
            lastVector = vector1
            lastPoint = allPoints[i]
        else:
            #print(angle)
            ...
    allPoints = acceptedPoints
    
    if allPoints == []:
        Route = []
        currentPathIndex = 0
        return data


    if len(Route) > 0:
        data["map"]["allPoints"] =  allPoints
    else:
        data["map"]["allPoints"] = allPoints

    data["map"]["endPoints"] = []
        
    if DistanceBetweenPoints([truckX, truckZ], allPoints[0]) > 200:
        Route = []
        currentPathIndex = 0
        return data
    
    return None
    

wasIndicating = False
# MARK: Main Function
def GetSteeringPoints(data : dict, MapUtils, Enabled, navigationData):
    global allPoints
    
    if navigationData != None:
        try:
            data["map"]["instruct"] = GetPathInstruct(navigationData, data)
            navData = HandleNav(data, MapUtils, Enabled, navigationData)
            if navData != None:
                return navData
        except:
            logging.exception("Failed to handle navigation")
            noNavData = HandleNoNav(data, MapUtils, Enabled)
            if noNavData != None:
                return noNavData
        
    else:
        noNavData = HandleNoNav(data, MapUtils, Enabled)
        if noNavData != None:
            return noNavData


    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    rotation = data["api"]["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
    truckForwardVector = [-math.sin(rotation), -math.cos(rotation)]
    try:
        if len(allPoints) > 2:
            allPoints = allPoints[:5]
            # Average out the first 4 points
            x = 0
            y = 0
            for i in range(1, len(allPoints)):
                x += allPoints[i][0]
                y += allPoints[i][1]
            
            x /= 4
            y /= 4
            
            pointforwardVector = [allPoints[len(allPoints)-1][0] - allPoints[0][0], allPoints[len(allPoints)-1][1] - allPoints[0][1]]
            # Check if we are to the left or right of the forward vector (going left the angle has to be negative)
            if np.cross(truckForwardVector, pointforwardVector) < 0:
                isLeft = True
            else: isLeft = False
            
            # Calculate the centerline vector and the truck's position relative to the first point
            centerlineVector = [allPoints[-1][0] - allPoints[0][0], allPoints[-1][1] - allPoints[0][1]]
            truckPositionVector = [truckX - allPoints[0][0], truckZ - allPoints[0][1]]
            #print(centerlineVector)
            #print(truckPositionVector)
            
            # Calculate lateral offset from the centerline
            # This is a simplified approach; for more accuracy, consider each segment of the centerline
            lateralOffset = np.cross(truckPositionVector, centerlineVector) / np.linalg.norm(centerlineVector)
            
            # Calculate the angle as before
            angle = np.arccos(np.dot(truckForwardVector, centerlineVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(centerlineVector)))
            angle = math.degrees(angle)
            
            if np.cross(truckForwardVector, centerlineVector) < 0:
                angle = -angle
            
            if angle > 140:
                angle = 0
            if angle < -140:
                angle = 0
            
            angle = angle * ANGLE_MULTIPLIER
            
            # Adjust angle based on lateral offset
            # This is a simplistic approach; you may need a more sophisticated control algorithm
            offsetCorrection = lateralOffset * 5  # correctionFactor is a tuning parameter
            offsetCorrection = max(-20, min(20, offsetCorrection))  # limit the correction to -10..10 degrees
            if isLeft:
                angle += offsetCorrection * OFFSET_MULTIPLIER
            else:
                angle += offsetCorrection * OFFSET_MULTIPLIER
            
            multiplier = 2
            #if data["api"]["truckBool"]["blinkerLeftActive"] or data["api"]["truckBool"]["blinkerRightActive"]:
            #    multiplier = 4
            
            data["map"]["angle"] = angle * multiplier
            #print(f"Angle is {angle}")
        else:
            # Just home to the last point if there are less than 2
            x = allPoints[len(allPoints)-1][0]
            y = allPoints[len(allPoints)-1][1]
            
            # Create a vector from the truck to the last point
            vector = [x - truckX, y - truckZ]
            # Calculate the angle between the truck forward vector and the vector to the last point
            angle = np.arccos(np.dot(truckForwardVector, vector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(vector)))
            angle = math.degrees(angle)
            # Check if the angle is negative or positive
            if np.cross(truckForwardVector, vector) < 0:
                angle = -angle
                
            data["map"]["angle"] = angle * 2
    except:
        #logging.exception("Failed to calculate angle")
        data["map"]["angle"] = 0
        
    return data