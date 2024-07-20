from ETS2LA.plugins.Map.GameData.prefabItems import PrefabItem
import Compute.compute as compute
from ETS2LA.plugins.Map.GameData.roads import Road
import numpy as np
import logging
import math

POINT_SEPARATION = 4 # Meter forward for each point
POINT_COUNT = 20
MAX_OBJECT_DISTANCE = 500 # Maximum distance to look for objects with points
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
                point1 = [curve[0], curve[1], curve[4]]
                point2 = [curve[2], curve[3], curve[5]]
                if DistanceBetweenPoints([x, y], [point1[0], point1[1]]) < MAX_POINT_DISTANCE:
                    points.append(Point(
                        x=point1[0],
                        y=point1[1],
                        z=point1[2],
                        type="item",
                        parentUid=item.Uid
                    ))
                if DistanceBetweenPoints([x, y], [point2[0], point2[1]]) < MAX_POINT_DISTANCE:
                    points.append(Point(
                        x=point2[0],
                        y=point2[1],
                        z=point2[2],
                        type="item",
                        parentUid=item.Uid
                    ))
    
    return points

def ScorePoint(x : int, y : int, firstPointUid : str, point : Point, lastPoint : Point = None):
    distance = DistanceBetweenPoints([x, y], [point.x, point.y])
    
    # Distance
    score = distance if distance > 0 else -distance
    
    # Angle
    if lastPoint == None:
        forwardVector = [point.x - x, point.y - y]
    else:
        forwardVector = [point.x - lastPoint.x, point.y - lastPoint.y]

    dot = np.dot(forwardVector, [point.x - x, point.y - y])
    
    if dot < 0:
        score += 100
    score += dot
    
    # Similarity
    if lastPoint != None:
        if lastPoint.parentUid != None and point.parentUid != lastPoint.parentUid:
            score += 2
        elif lastPoint.laneId != point.laneId:
            score += 1
    
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
    rotation += steering * 0.1
    
    
    points = []
    
    # First point is the truck
    points.append((truckX, truckY))
    
    # Next points we'll calculate
    forwardVector = [-math.sin(rotation), -math.cos(rotation)]
    forwardVector = [value * POINT_SEPARATION for value in forwardVector]
    
    addedPoints = []
    #print(f"- Calculating points for truck at {truckX}, {truckY} with rotation {rotation} and forward vector {forwardVector}")
    for i in range(1, POINT_COUNT):
        closestPoints = []
        x = points[-1][0]
        y = points[-1][1]
        count = 0
        
        while closestPoints == []:
            x += forwardVector[0]
            y += forwardVector[1]
            
            try:
                closestPoints = FindClosestPoints(x, y, closePoints)
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
                                     lastPoint=addedPoints[-1] if len(addedPoints) > 0 else None)
        
        scoredPoints = sorted(closestPoints, key=lambda point: point.score)
        
        #for point in scoredPoints:
        #    print(f" -> Point at {point.array()} with score {point.score}")
        
        points.append(scoredPoints[0].array())
        addedPoints.append(scoredPoints[0])
        closePoints.remove(scoredPoints[0])
        
        #print(f" --> Added point {i} at {points[-1]} with score {scoredPoints[0].score}")
        
        # Calculate the forward vector between the last two points
        #forwardVector = [points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]]
        #forwardVector = [value / np.linalg.norm(forwardVector) * POINT_SEPARATION for value in forwardVector]

        
    data["map"]["allPoints"] = points
        
    return points