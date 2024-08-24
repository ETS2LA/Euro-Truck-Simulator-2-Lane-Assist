from ETS2LA.plugins.Map.GameData.prefabItems import PrefabItem, GetPrefabItemByUid
from ETS2LA.plugins.Map.GameData.roads import Road, GetRoadByUid
import ETS2LA.plugins.Map.GameData.nodes as Nodes
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
    closestLane = closestData["closestLane"]
    if closestItem is None:
        return None
    
    #logging.warning(closestLane)
    
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
        
    # MARK: HERE
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
            startPosition = closestItem.CurvePoints[laneIndex][0]
        )
        
        Route.append(routeItem)
        
        #logging.warning(closestData["closestLane"])
        
        #logging.warning(closestItem.json())
        #closestItem = GetPrefabItemByUid(closestItem.Uid)
        #CurrentItem = closestItem
        #ClosestLane = closestItem.CurvePoints.index(closestData["closestLane"])

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
    #logging.warning("Getting next item")
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
        
    if type(NextItem) == Road:
        #logging.warning("Next item is a road")
        NextItem = cast(Road, NextItem) # Get intellisense
        Lanes = NextItem.ParallelPoints
        
        if NeedInvert(Route[-1].points, truckX, truckZ):
            #logging.warning("Inverting last item points")
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
        
        #logging.warning(f"ClosestLaneId: {closestLaneId}")
        #logging.warning(f"ClosestLaneDistance: {closestLaneDistance}")
        
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
        
        #logging.warning(f"RouteItem created for road")
        
        return routeItem
        
    elif type(NextItem) == PrefabItem:
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
                
        #logging.warning(f"ClosestLaneId: {closestLaneId}")
        #logging.warning(f"ClosestLaneDistance: {closestLaneDistance}")
                
        if closestLaneId == [math.inf]:
            return []
        
        wantedDirection = "right" if data["api"]["truckBool"]["blinkerLeftActive"] else "left" if data["api"]["truckBool"]["blinkerRightActive"] else "forward"
        if len(closestLaneId) > 1:
            #logging.warning(f"Multiple closest lanes: {closestLaneId}")
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
        
        #logging.warning(f"ClosestLaneId: {closestLaneId}")
        
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
        
        #logging.warning(f"RouteItem created for prefab")
        
        return routeItem
        
def DistanceBetweenPoints(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def map_curvature_to_speed_effect(curvature):
    factor = 0.01 # needs a 50 degree turn to reach max effect
    min_effect, max_effect = 0.0, 0.5
    effect = min(max(curvature * factor, min_effect), max_effect)
    return effect

def CalculateCurvature(points):
    try:
        # Calculate the dot products of the vectors between the points
        dot_products = []
        for i in range(1, len(points)-1):
            try:
                vector1 = [points[i][0] - points[i-1][0], points[i][1] - points[i-1][1]]
                vector2 = [points[i+1][0] - points[i][0], points[i+1][1] - points[i][1]]
                dot_product = np.dot(vector1, vector2)
                # Check if nan
                if dot_product != dot_product:
                    dot_product = 0
                dot_products.append(dot_product)
            except:
                dot_products.append(0)
            
        # Calculate the angles between the vectors
        angles = []
        for i in range(len(dot_products)-1):
            angle = np.arccos(dot_products[i] / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))
            # Check if nan
            if angle != angle:
                angle = 0
                
            # Check if the angle is closer to 180 degrees
            if angle > math.pi/4:
                angle = angle - math.pi/2
                
            #print(f"Angle: {angle}")
                
            angles.append(angle)
        
        # Calculate the curvature
        total_curvature = 0
        for angle in angles:
            total_curvature += abs(angle)
        
        return total_curvature
    except:
        logging.exception("Failed to calculate curvature")
        return 0

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
    
    if len(Route) == 0:
        closestData = MapUtils.run(truckX, 0, truckZ)
        try:
            GetItemAndLaneReferences(closestData, MapUtils)
        except: 
            #logging.exception("Failed to get item and lane references")
            return data
    
    if Route == []:
        return data
    
    for routeItem in Route:
        routeItem.points = DiscardPointsBehindTheTruck(routeItem.points, truckX, truckZ, rotation)
        if routeItem.points == []:
            Route.remove(routeItem)
    
    tries = 0
    while len(Route) < RouteLength:
        try:
            item = GetNextItem(data, truckX, truckZ, rotation, MapUtils)
            if item == []:
                tries += 1
                if tries > 10:
                    break
                continue
            Route.append(item)
            #logging.warning(f"Route length: {len(Route)}")
        except:
            #MARK: HERE
            #logging.exception("Failed to get next item")
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

    data["map"]["allPoints"] = allPoints # Cap to 20 points
    data["map"]["endPoints"] = endPoints
    
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
        
    return data