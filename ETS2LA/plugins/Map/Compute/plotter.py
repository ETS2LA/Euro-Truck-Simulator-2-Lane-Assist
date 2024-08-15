from ETS2LA.plugins.Map.GameData.prefabItems import PrefabItem
import Compute.compute as compute
from ETS2LA.plugins.Map.GameData.roads import Road
import numpy as np
import logging
import math

POINT_SEPARATION = 2 # Meter forward for each point
POINTS_TO_TEST = 4 # How many points to test forwards
POINT_COUNT = 20
MAX_OBJECT_DISTANCE = 1000 # Maximum distance to look for objects with points
MAX_POINT_DISTANCE = 100 # Maximum distance to add points to the calculations

class Point:
    x: float = 0
    y: float = 0
    z: float = 0 # This is the height of the point
    type: str = "road"
    parentUid: str = None
    laneId: int = 0
    squareX: int = 0 # Tells which square the point is in (10m x 10m squares) 
    squareY: int = 0 # Tells which square the point is in (10m x 10m squares)
    score: float = 0
    def __init__(self, x : float, y : float, z : float, type : str, parentUid : str, laneId : int = 0):
        self.x = x
        self.y = y
        self.z = z
        self.type = type
        self.parentUid = parentUid
        self.laneId = laneId
                
    def array(self):
        return [self.x, self.y]
        
    def json(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "type": self.type,
            "parentUID": self.parentUid,
            "squareX": self.squareX,
            "squareY": self.squareY,
            "score": self.score
        }

def DistanceBetweenPoints(point1 : list, point2 : list):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def GetAllCloseRoadPoints(data : dict, closeRoads : list[Road]):
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    points = []
    for road in closeRoads:
        if DistanceBetweenPoints([x, y], [road.X, road.Z]) < MAX_OBJECT_DISTANCE:
            for i, lane in enumerate(road.ParallelPoints):
                try:
                    for point in lane:
                        if DistanceBetweenPoints([x, y], [point[0], point[1]]) < MAX_POINT_DISTANCE:
                            points.append(Point(
                                x=point[0],
                                y=point[1],
                                z=road.YValues[i],
                                type="road",
                                parentUid=road.Uid,
                                laneId=i
                            ))
                except:
                    pass

    return points
    
def GetAllCloseItemPoints(data : dict, closeItems : list[PrefabItem]):
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    points = []
    
    for item in closeItems:
        if DistanceBetweenPoints([x, y], [item.X, item.Z]) < MAX_OBJECT_DISTANCE:
            for curve in item.CurvePoints:
                try:
                    for point in curve:
                        if DistanceBetweenPoints([x, y], [point[0], point[1]]) < MAX_POINT_DISTANCE:
                            points.append(Point(
                                x=point[0],
                                y=point[1],
                                z=point[2],
                                type="item",
                                parentUid=item.Uid
                            ))
                except:
                    logging.exception("Error in GetAllCloseItemPoints")
                    pass
    
    return points

def ScorePoint(x : int, y : int, firstPointUid : str, point : Point, lastPoint : Point = None, truckForwardVector : list = None):
    distance = DistanceBetweenPoints([x, y], [point.x, point.y]) * 1000
    
    # Distance
    score = distance if distance > 0 else -distance
    
    # Angle
    if lastPoint == None:
        forwardVector = [point.x - x, point.y - y]
    else:
        forwardVector = [point.x - lastPoint.x, point.y - lastPoint.y]

    
    # dot = np.dot(forwardVector, [point.x - x, point.y - y])
    # score += abs(dot)
    # dot = np.dot(forwardVector, truckForwardVector)
    # score += abs(dot) * 10
    
    # Similarity
    if lastPoint != None:
        if lastPoint.parentUid != None and point.parentUid != lastPoint.parentUid:
            score += 2
        if lastPoint.laneId != point.laneId:
            score += 10 # Penalize changing lanes
    
    return score

def AssignSquares(points : list[Point]):
    for point in points:
        point.squareX = int(point.x // 10)
        point.squareY = int(point.y // 10)
    return points

def GetAllClosePoints(data : dict, closeRoads : list, closeItems : list):
    closePoints = []
    closePoints.extend(GetAllCloseRoadPoints(data, closeRoads))
    closePoints.extend(GetAllCloseItemPoints(data, closeItems))
    closePoints = AssignSquares(closePoints)
    return closePoints

def FindClosestPoints(x : int, y : int, closePoints : list):
    squareX = int(x // 10)
    squareY = int(y // 10)
    arrayOfClosestPoints = []
    for point in closePoints:
        if point.squareX == squareX and point.squareY == squareY:
            arrayOfClosestPoints.append(point)
        
    return arrayOfClosestPoints

def GetNextPoints(data : dict, closeRoads : list, closeItems : list):
    closePoints = GetAllClosePoints(data, closeRoads, closeItems)
    
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckY = data["api"]["truckPlacement"]["coordinateZ"]
    rotation = data["api"]["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
    steering = data["api"]["truckFloat"]["userSteer"]
    #rotation += steering
    
    
    points = []
    
    # First point is the truck
    points.append((truckX, truckY))
    
    # Next points we'll calculate
    forwardVector = [-math.sin(rotation), -math.cos(rotation)]
    truckForwardVector = forwardVector
    forwardVector = [value * POINT_SEPARATION for value in forwardVector]
    
    addedPoints = []
    #print(f"- Calculating points for truck at {truckX}, {truckY} with rotation {rotation} and forward vector {forwardVector}")
    for i in range(1, POINT_COUNT):
        closestPoints = []
        x = points[-1][0]
        y = points[-1][1]
        
        count = 0
        while closestPoints == [] or (count < POINTS_TO_TEST and closePoints != []):
            x += forwardVector[0]
            y += forwardVector[1]
            
            try:
                newPoints = FindClosestPoints(x, y, closePoints)
                for point in newPoints:
                    if point not in closestPoints:
                        closestPoints.append(point)
            except:
                break
            
            count += 1
            if count > 30:
                break
        
        if closestPoints == []:
            break
        
        for point in closestPoints:
            point.score = ScorePoint(x, y, 
                                     addedPoints[0].parentUid if len(addedPoints) != 0 else None, 
                                     point, 
                                     lastPoint=addedPoints[-1] if len(addedPoints) > 0 else None,
                                     truckForwardVector=truckForwardVector)
        
        scoredPoints = sorted(closestPoints, key=lambda point: point.score)
        
        #print(f" --> Added point {i} at {scoredPoints[0].array()} with score {scoredPoints[0].score}")
        points.append(scoredPoints[0].array())
        addedPoints.append(scoredPoints[0])
        closePoints.remove(scoredPoints[0])
        
        for point in scoredPoints:
            #print(f"    - Point at {point.array()} with score {point.score}")
            ...
        #print(f" --> Added point {i} at {points[-1]} with score {scoredPoints[0].score}")
        
        # Calculate the forward vector between the last two points
        forwardVector = [points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]]
        forwardVector = [value / np.linalg.norm(forwardVector) * (POINT_SEPARATION * 2) for value in forwardVector]

    # only save the first 4 points
    steeringPoints = points[:3]
    
    if len(steeringPoints) > 2:
        # Average out the first 4 points
        x = 0
        y = 0
        for i in range(1, len(steeringPoints)):
            x += steeringPoints[i][0]
            y += steeringPoints[i][1]
        
        x /= 4
        y /= 4
        
        
        pointforwardVector = [steeringPoints[len(steeringPoints)-1][0] - steeringPoints[0][0], steeringPoints[len(steeringPoints)-1][1] - steeringPoints[0][1]]
        # Check if we are to the left or right of the forward vector (going left the angle has to be negative)
        if np.cross(truckForwardVector, pointforwardVector) < 0:
            isLeft = True
        else: isLeft = False
        
        # Calculate the angle between the averaged poiunt and the forward vector of the truck
        angle = np.arccos(np.dot(truckForwardVector, pointforwardVector) / (np.linalg.norm(truckForwardVector) * np.linalg.norm(pointforwardVector)))
        angle = math.degrees(angle)
        if isLeft: angle = -angle
        data["map"]["angle"] = angle * 2
        #print(f"Angle is {angle}")
    
    data["map"]["allPoints"] = points
        
    return data