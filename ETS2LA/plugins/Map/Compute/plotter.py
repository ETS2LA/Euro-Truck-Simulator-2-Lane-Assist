from ETS2LA.plugins.Map.GameData.prefabItems import PrefabItem, GetPrefabItemByUid
from ETS2LA.plugins.Map.GameData.roads import Road, GetRoadByUid
import Compute.compute as compute
from typing import cast
import numpy as np
import logging
import math
import json
import time
class RouteItem:
    item: PrefabItem | Road
    points: list[list[float]]
    lane: int
    length: float
    endPosition: list[float]
    startPosition: list[float]
    
    def __init__(self, item, points, lane, length, endPosition, startPosition):
        self.item = item
        self.points = points
        self.lane = lane
        self.length = length
        self.endPosition = endPosition
        self.startPosition = startPosition
        
    def DiscardPointsBehindTheTruck(self, truckX, truckZ, rotation):
        newPoints = []
        truckForwardVector = [-math.sin(rotation), -math.cos(rotation)]
        for point in self.points:
            pointForwardVector = [point[0] - truckX, point[1] - truckZ]
            angle = np.arccos(np.dot(truckForwardVector, pointForwardVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(pointForwardVector)))
            angle = math.degrees(angle)
            if angle > 90:
                continue
            newPoints.append(point)      
        
        return newPoints
        
Route : list[RouteItem] = []
RouteLength = 3

def GetItemAndLaneReferences(closestData, MapUtils):
    global Route
    closestItem = closestData["closestItem"]
    if closestItem is None:
        return None
    
    if type(closestItem) == Road:
        closestItem = GetRoadByUid(closestItem.Uid)
        if closestItem is None: return None
        length = 0
        for i in range(len(closestItem.ParallelPoints)):
            length += np.linalg.norm(np.array(closestItem.ParallelPoints[i][1]) - np.array(closestItem.ParallelPoints[i][0]))
        lane = closestItem.ParallelPoints.index(closestData["closestLane"])
        routeItem = RouteItem(
            item = closestItem,
            points = closestItem.ParallelPoints[lane],
            lane = lane,
            length = length,
            endPosition = closestItem.ParallelPoints[lane][-1],
            startPosition = closestItem.ParallelPoints[lane][0]
        )
        Route.append(routeItem)
        
    # elif type(closestItem) == PrefabItem:
    #     closestItem = GetPrefabItemByUid(closestItem.Uid)
    #     CurrentItem = closestItem
    #     ClosestLane = closestItem.CurvePoints.index(closestData["closestLane"])

def DiscardPointsBehindTheTruck(points, truckX, truckZ, rotation):
    newPoints = []
    truckForwardVector = [-math.sin(rotation), -math.cos(rotation)]
    for point in points:
        pointForwardVector = [point[0] - truckX, point[1] - truckZ]
        # angle = np.arccos(np.dot(truckForwardVector, pointforwardVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(pointforwardVector)))
        angle = np.arccos(np.dot(truckForwardVector, pointForwardVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(pointForwardVector)))
        angle = math.degrees(angle)
        if angle > 90:
            continue
        newPoints.append(point)   
        
    try:
        if DistanceBetweenPoints([truckX, truckZ], newPoints[0]) > DistanceBetweenPoints([truckX, truckZ], newPoints[-1]):
            newPoints = newPoints[::-1]
    except:
        pass
    
    return newPoints

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

def GetNextItem(data : dict, truckX, truckZ, rotation, MapUtils) -> RouteItem:
    # Check which node is to the front of the truck
    CurrentItem = Route[-1].item
    ClosestLane = Route[-1].lane
    
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
                distance = math.sqrt((points[0][0] - node.X) ** 2 + (points[0][1] - node.Z) ** 2)
                if distance < ForwardNodeDistance:
                    ForwardNodeDistance = distance
                    ForwardNode = node
                distance = math.sqrt((points[-1][0] - node.X) ** 2 + (points[-1][1] - node.Z) ** 2)
                if distance < BackwardNodeDistance:
                    BackwardNodeDistance = distance
                    BackwardNode = node
    
    BackwardPosition = [BackwardNode.X, BackwardNode.Z]
    ForwardPosition = [ForwardNode.X, ForwardNode.Z]
    
    # Calculate the angles between the truck and the nodes
    BackwardAngle = np.arccos(np.dot([BackwardPosition[0] - truckX, BackwardPosition[1] - truckZ], [math.sin(rotation), math.cos(rotation)]) / (np.linalg.norm([BackwardPosition[0] - truckX, BackwardPosition[1] - truckZ]) * np.linalg.norm([math.sin(rotation), math.cos(rotation)])))
    ForwardAngle = np.arccos(np.dot([ForwardPosition[0] - truckX, ForwardPosition[1] - truckZ], [math.sin(rotation), math.cos(rotation)]) / (np.linalg.norm([ForwardPosition[0] - truckX, ForwardPosition[1] - truckZ]) * np.linalg.norm([math.sin(rotation), math.cos(rotation)])))
    
    if BackwardAngle < ForwardAngle:
        NextNode = ForwardNode
    else:
        NextNode = BackwardNode
    
        
    ForwardItem = NextNode.ForwardItem
    BackwardItem = NextNode.BackwardItem
    
    if ForwardItem is None and BackwardItem is None:
        return []
    elif ForwardItem is None:
        NextItem = BackwardItem
    elif BackwardItem is None:
        NextItem = ForwardItem
    else:
        ForwardUid = ForwardItem.Uid
        BackwardUid = BackwardItem.Uid
        
        if ForwardUid == CurrentItem.Uid:
            NextItem = BackwardItem
        else:
            NextItem = ForwardItem
            
        if NextItem is None:
            return []
        
    if type(NextItem) == Road:
        NextItem = cast(Road, NextItem) # Get intellisense
        Lanes = NextItem.ParallelPoints
        
        if NeedInvert(Route[-1].points, truckX, truckZ):
            CurrentEndPoint = Route[-1].points[::-1][-1]
        else:
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
        
        closestPoints = Lanes[closestLaneId]
        
        if NeedInvert(Lanes[closestLaneId], truckX, truckZ):
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
            startPosition = closestPoints[0]
        )
        
        return routeItem
        
    elif type(NextItem) == PrefabItem:
        NextItem = cast(PrefabItem, NextItem) # Get intellisense
        Curves = NextItem.CurvePoints
        Lanes = NextItem.Prefab.PrefabLanes
        
        if NeedInvert(Route[-1].points, truckX, truckZ):
            CurrentEndPoint = Route[-1].points[::-1][-1]
        else:
            CurrentEndPoint = Route[-1].points[-1]
        
        #logging.warning(f"CurrentEndPoint: {CurrentEndPoint}")

        closestLaneIds = [math.inf]
        closestLaneDistance = math.inf
        
        for i in range(len(Lanes)):
            laneStart = Curves[i][0]
            #logging.warning(f"laneStart: {laneStart}")
            #logging.warning(f"CurrentEndPoint: {CurrentEndPoint}")
            distance = math.sqrt((CurrentEndPoint[0] - laneStart[0]) ** 2 + (CurrentEndPoint[1] - laneStart[1]) ** 2)
            #logging.warning(f"Distance: {distance}")
            if distance < closestLaneDistance:
                closestLaneDistance = distance
                closestLaneId = [i]
            elif distance == closestLaneDistance:
                closestLaneId.append(i)
                
        for i in range(len(Lanes)):
            laneEnd = Curves[i][-1]
            distance = math.sqrt((CurrentEndPoint[0] - laneEnd[0]) ** 2 + (CurrentEndPoint[1] - laneEnd[1]) ** 2)
            if distance < closestLaneDistance:
                closestLaneDistance = distance
                closestLaneId = [i]
            elif distance == closestLaneDistance:
                closestLaneId.append(i)
                
        # logging.warning(f"ClosestLaneId: {closestLaneId}")
        # logging.warning(f"ClosestLaneDistance: {closestLaneDistance}")
                
        if closestLaneId == [math.inf]:
            return []
        
        wantedDirection = "right" if data["api"]["truckBool"]["blinkerLeftActive"] else "left" if data["api"]["truckBool"]["blinkerRightActive"] else "forward"
        if len(closestLaneId) > 1:
            if wantedDirection == 'forward':
                # Check which of the lanes is the most forward
                forwardestLane = math.inf
                forwardestLaneDot = math.inf
                for i in closestLaneId:
                    laneEnd = Curves[i][-1]
                    vector = [laneEnd[0] - CurrentEndPoint[0], laneEnd[1] - CurrentEndPoint[1]]
                    dot = np.dot([math.sin(rotation), math.cos(rotation)], vector)
                    if dot < forwardestLaneDot:
                        forwardestLaneDot = dot
                        forwardestLane = i
                
                closestLaneId = forwardestLane
            if wantedDirection == "right":
                # Check which of the lanes is the most right
                rightestLane = math.inf
                rightestLaneDot = math.inf
                for i in closestLaneId:
                    laneEnd = Curves[i][-1]
                    vector = [laneEnd[0] - CurrentEndPoint[0], laneEnd[1] - CurrentEndPoint[1]]
                    dot = np.dot([math.cos(rotation), -math.sin(rotation)], vector)
                    if dot < rightestLaneDot:
                        rightestLaneDot = dot
                        rightestLane = i
                
                closestLaneId = rightestLane
            if wantedDirection == "left":
                # Check which of the lanes is the most left
                leftestLane = math.inf
                leftestLaneDot = math.inf
                for i in closestLaneId:
                    laneEnd = Curves[i][-1]
                    vector = [laneEnd[0] - CurrentEndPoint[0], laneEnd[1] - CurrentEndPoint[1]]
                    dot = np.dot([-math.cos(rotation), math.sin(rotation)], vector)
                    if dot < leftestLaneDot:
                        leftestLaneDot = dot
                        leftestLane = i
                
                closestLaneId = leftestLane
                
        else:
            closestLaneId = closestLaneId[0]
        
        closestPoints = Curves[closestLaneId]
        
        if NeedInvert(closestPoints, truckX, truckZ):
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
            startPosition = closestPoints[0]
        )
        
        return routeItem
        
def DistanceBetweenPoints(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

wasIndicating = False

def GetNextPoints(data : dict, MapUtils, Enabled):
    global Route
    global wasIndicating
    
    data["map"]["allPoints"] = []
    data["map"]["endPoints"] = []
    data["map"]["angle"] = 0
    
    if not Enabled:
        Route = []
        #return data
        
    if ((data["api"]["truckBool"]["blinkerLeftActive"] or data["api"]["truckBool"]["blinkerRightActive"]) and not wasIndicating) or ((not data["api"]["truckBool"]["blinkerLeftActive"] and not data["api"]["truckBool"]["blinkerRightActive"]) and wasIndicating):
        wasIndicating = data["api"]["truckBool"]["blinkerLeftActive"] or data["api"]["truckBool"]["blinkerRightActive"]
        Route = Route[:1] # Reset the next item
    
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    rotation = data["api"]["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
    
    startTime = time.time()
    if len(Route) == 0:
        closestData = MapUtils.run(truckX, 0, truckZ)
        try:
            GetItemAndLaneReferences(closestData, MapUtils)
        except: pass
        endTime = time.time()
    
    if Route == []:
        return data
    
    for routeItem in Route:
        routeItem.points = DiscardPointsBehindTheTruck(routeItem.points, truckX, truckZ, rotation)
        if routeItem.points == []:
            Route.remove(routeItem)
    
    tries = 0
    while len(Route) < RouteLength:
        try:
            Route.append(GetNextItem(data, truckX, truckZ, rotation, MapUtils))
        except:
            logging.exception("Failed to get next item")
            if len(Route) == 0:
                closestData = MapUtils.run(truckX, 0, truckZ)
                try:
                    GetItemAndLaneReferences(closestData, MapUtils)
                except: 
                    return data
            else:
                return data
            
        tries += 1
        if tries > 10:
            break
    
    #logging.warning(f"Route length: {len(Route)} tries: {tries}")
    
    allPoints = []
    itemsToRemove = []
    for routeItem in Route:
        try:
            allPoints.extend(routeItem.points)
        except:
            itemsToRemove.append(routeItem)
        #data["map"]["endPoints"].append(routeItem.endPosition)

    for item in itemsToRemove:
        Route.remove(item)

    data["map"]["allPoints"] = allPoints#[:5]
    data["map"]["endPoints"] = []
    
    if allPoints == []:
        CurrentItem = None
        ClosestLane = None
        return data
        
    truckForwardVector = [-math.sin(rotation), -math.cos(rotation)]
        
    if DistanceBetweenPoints([truckX, truckZ], allPoints[0]) > 1500:
        CurrentItem = None
        ClosestLane = None
        return data
        
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
        
        # Adjust angle based on lateral offset
        # This is a simplistic approach; you may need a more sophisticated control algorithm
        offsetCorrection = lateralOffset * 5  # correctionFactor is a tuning parameter
        offsetCorrection = max(-20, min(20, offsetCorrection))  # limit the correction to -10..10 degrees
        if isLeft:
            angle += offsetCorrection
        else:
            angle += offsetCorrection
        
        multiplier = 2
        if data["api"]["truckBool"]["blinkerLeftActive"] or data["api"]["truckBool"]["blinkerRightActive"]:
            multiplier = 4
        
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
        
    return data