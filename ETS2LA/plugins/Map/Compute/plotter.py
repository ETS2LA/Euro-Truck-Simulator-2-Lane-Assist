from ETS2LA.plugins.Map.GameData.prefabItems import PrefabItem, GetPrefabItemByUid
from ETS2LA.plugins.Map.GameData.roads import Road, GetRoadByUid
import Compute.compute as compute
import numpy as np
import logging
import math
from typing import cast

CurrentItem = None
ClosestLane = None

def GetItemAndLaneReferences(closestData, MapUtils):
    global CurrentItem, ClosestLane
    closestItem = closestData["closestItem"]
    if closestItem is None:
        return None
    
    if type(closestItem) == Road:
        closestItem = GetRoadByUid(closestItem.Uid)
        if closestItem is None: return None
        CurrentItem = closestItem
        ClosestLane = closestItem.ParallelPoints.index(closestData["closestLane"])
        
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
        
    return newPoints

def NeedInvert(points, truckX, truckY):
    if len(points) < 2:
        return False
    
    firstPoint = points[0]
    lastPoint = points[len(points)-1]
    middlePoint = points[len(points)//2]
    
    # Check if the last point and the middle points are closer than the first point
    distance1 = math.sqrt((truckX - firstPoint[0]) ** 2 + (truckY - firstPoint[1]) ** 2)
    distance2 = math.sqrt((truckX - lastPoint[0]) ** 2 + (truckY - lastPoint[1]) ** 2)
    distance3 = math.sqrt((truckX - middlePoint[0]) ** 2 + (truckY - middlePoint[1]) ** 2)
    
    if distance3 < distance1 and distance3 < distance2:
        return True
    
    return False

def GetNextItemPoints(data : dict, truckX, truckZ, rotation, MapUtils):
    # Check which node is to the front of the truck
    if type(CurrentItem) == Road:
        BackwardNode = CurrentItem.EndNode
        ForwardNode = CurrentItem.StartNode
        
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
            CurrentEndPoint = CurrentItem.ParallelPoints[ClosestLane][-1]
            closestLaneId = math.inf
            closestLaneDistance = math.inf
            for i in range(len(Lanes)):
                laneStart = Lanes[i][0]
                distance = math.sqrt((CurrentEndPoint[0] - laneStart[0]) ** 2 + (CurrentEndPoint[1] - laneStart[1]) ** 2)
                if distance < closestLaneDistance:
                    closestLaneDistance = distance
                    closestLaneId = i
                    
            if closestLaneId == math.inf:
                return []
            
            closestPoints = Lanes[closestLaneId]
            
            if NeedInvert(Lanes[closestLaneId], truckX, truckZ):
                closestPoints.reverse()
            
            ClosestLanePoints = closestPoints
            
            return ClosestLanePoints
            
        elif type(NextItem) == PrefabItem:
            NextItem = cast(PrefabItem, NextItem) # Get intellisense
            Curves = NextItem.CurvePoints
            Lanes = NextItem.Prefab.PrefabLanes
            LaneStartPoints = NextItem.LaneStartPoints
            LaneEndPoints = NextItem.LaneEndPoints
            
            closestLaneId = math.inf
            closestLaneDistance = math.inf
            
            for i in range(len(Lanes)):
                laneStart = LaneStartPoints[i]
                #logging.warning(f"truckX: {truckX}, truckZ: {truckZ}")
                #logging.warning(f"laneStart: {laneStart}")
                distance = math.sqrt((truckX - laneStart[0]) ** 2 + (truckZ - laneStart[1]) ** 2)
                #logging.warning(f"Distance: {distance}")
                if distance < closestLaneDistance:
                    closestLaneDistance = distance
                    closestLaneId = i
                    
            for i in range(len(Lanes)):
                laneEnd = LaneEndPoints[i]
                distance = math.sqrt((truckX - laneEnd[0]) ** 2 + (truckZ - laneEnd[1]) ** 2)
                if distance < closestLaneDistance:
                    closestLaneDistance = distance
                    closestLaneId = i
                    
            if closestLaneId == math.inf:
                return []
            
            closestPoints = Curves[closestLaneId]
            
            if NeedInvert(closestPoints, truckX, truckZ):
                closestPoints.reverse()

            ClosestLanePoints = closestPoints
            
            return ClosestLanePoints
        
def DistanceBetweenPoints(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def GetNextPoints(data : dict, MapUtils):
    global CurrentItem
    global ClosestLane
        
    data["map"]["allPoints"] = []
    data["map"]["angle"] = 0
    
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    rotation = data["api"]["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
        
    if CurrentItem is None:
        closestData = MapUtils.run(truckX, 0, truckZ)
        GetItemAndLaneReferences(closestData, MapUtils)
    
    if CurrentItem is None: # Didn't find a start item
        return data
    
    allPoints = []
    if type(CurrentItem) is Road:
        allPoints.extend(CurrentItem.ParallelPoints[ClosestLane])
        if NeedInvert(allPoints, truckX, truckZ):
            allPoints.reverse()
    
    try:
        allPoints.extend(GetNextItemPoints(data, truckX, truckZ, rotation, MapUtils))
    except: pass

    allPoints = DiscardPointsBehindTheTruck(allPoints, truckX, truckZ, rotation)
    data["map"]["allPoints"] = allPoints
    
    if allPoints == []:
        CurrentItem = None
        ClosestLane = None
        return data
        
    truckForwardVector = [-math.sin(rotation), -math.cos(rotation)]
        
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
        
        # Calculate the angle between the averaged poiunt and the forward vector of the truck
        angle = np.arccos(np.dot(truckForwardVector, pointforwardVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(pointforwardVector)))
        angle = math.degrees(angle)
        #logging.warning(f"Angle: {angle}")
        if isLeft: angle = -angle
        data["map"]["angle"] = angle * 2
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