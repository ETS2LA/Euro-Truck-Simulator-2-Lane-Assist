import cv2
from GameData import nodes, roads, prefabs, prefabItems
import math
import numpy as np
import os
import json
import time
import logging
print = logging.info
import sys

LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME = 10

def VisualizeRoads(data, closeRoads, img=None, zoom=2):
    """Will draw the roads onto the image.
    data: The game data
    img: The image to draw the roads on
    """
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    z = data["api"]["truckPlacement"]["coordinateY"]
    
    
    startTime = time.time()
    
    # Get the roads in the current area
    areaRoads = closeRoads
    tileCoords = roads.GetTileCoordinates(x, y)
    
    # Make a blank image of size 1000x1000 (1km x 1km on default zoom of 1)
    if img is None:
        size = 1000
        img = np.zeros((size, size, 3), np.uint8)
    
    # Show the x and y coordinates
    cv2.putText(img, f"X: {round(x)} Y: {round(y)} Z: {round(z,1)}", (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    # Draw the roads on the image, 1m is 1px in the image
    # roads have their start and end positions in the global coordinate system so we need to convert them to local coordinates with roads.GetLocalCoordinateInTile()
    calcCount = 0
    skipped = 0
    for road in areaRoads:
        try:
            if road.Points == None:
                points = roads.CreatePointsForRoad(road)
                roads.SetRoadPoints(road, points)
            
            # newPoints = []
            # for point in road.Points:
            #     xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
            #     truckXY = roads.GetLocalCoordinateInTile(x, y, tileCoords[0], tileCoords[1])
            #     xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
            #     # Apply zoom to the local coordinates
            #     zoomedX = xy[0] * zoom
            #     zoomedY = xy[1] * zoom
            #     # Offset the zoomed coordinates by the truck's position to "move" the camera
            #     pointX = int(zoomedX + size//2)
            #     pointY = int(zoomedY + size//2)
            #     newPoints.append((pointX, pointY))
            # 
            # cv2.polylines(img, np.int32([newPoints]), False, (0, 100, 150), (1 + (zoom - 1)), cv2.LINE_AA)
            
            # Check for parallel points
            if road.ParallelPoints == []:
                if calcCount > LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME:
                    skipped += 1
                    continue
                
                boundingBox, parallelPoints, laneWidth = roads.CalculateParallelCurves(road)
                if parallelPoints == [] or parallelPoints == None:
                    parallelPoints = [[(0, 0), (0, 0)], [(0, 0), (0, 0)]]
                road.ParallelPoints = parallelPoints
                road.LaneWidth = laneWidth
                road.BoundingBox = boundingBox
                roads.SetRoadParallelData(road, parallelPoints, laneWidth, boundingBox)
                calcCount += 1
            
            if road.ParallelPoints == [[(0, 0), (0, 0)], [(0, 0), (0, 0)]]:
                continue
            
            truckXY = roads.GetLocalCoordinateInTile(x, y, tileCoords[0], tileCoords[1])
            firstPoint = []
            laneCountLeft = len(road.RoadLook.lanesLeft)
            laneCountRight = len(road.RoadLook.lanesRight)
            laneCount = 0
            for lane in road.ParallelPoints:
                newPoints = []
                for point in lane:
                    xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
                    xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
                    # Apply zoom to the local coordinates
                    zoomedX = xy[0] * zoom
                    zoomedY = xy[1] * zoom
                    # Offset the zoomed coordinates by the truck's position to "move" the camera
                    pointX = int(zoomedX + size//2)
                    pointY = int(zoomedY + size//2)
                    # Check if the points are within the display area (1000px x 1000px)
                    if pointX < 0 or pointX > 1000 or pointY < 0 or pointY > 1000:
                        continue
                    newPoints.append((pointX, pointY))
                    if firstPoint == []:
                        firstPoint = (pointX, pointY)
            
                color = (150,175,150) if laneCount < laneCountLeft else (175,150,150)
                if road in data["map"]["inBoundingBox"]:
                    color = (0, 150, 0)
                if lane in data["map"]["closestLanes"]:
                    color = (0, 255, 0)
                if lane == data["map"]["closestLane"]:
                    color = (0, 0, 255)
            
                cv2.polylines(img, np.int32([newPoints]), False, color, (2 + (zoom - 1)), cv2.LINE_AA)
                
                laneCount += 1
            
            # Convert the bounding box to local coordinates
            # boundingBox = road.BoundingBox
            # newBoundingBox = []
            # for point in boundingBox:
            #     xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
            #     xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
            #     # Apply zoom to the local coordinates
            #     zoomedX = xy[0] * zoom
            #     zoomedY = xy[1] * zoom
            #     # Offset the zoomed coordinates by the truck's position to "move" the camera
            #     pointX = int(zoomedX + size//2)
            #     pointY = int(zoomedY + size//2)
            #     newBoundingBox.append((pointX, pointY))
            # cv2.rectangle(img, newBoundingBox[0], newBoundingBox[1], (0, 150, 0), 2)
                
            
            try:
                cv2.putText(img, f"Offset: {road.RoadLook.offset}", (firstPoint[0], firstPoint[1]), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                cv2.putText(img, f"Name: {road.RoadLook.name}", (firstPoint[0], firstPoint[1] + 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            except: pass
            # Draw the original road
            # try:
            #     newPoints = []
            #     for point in road.Points:
            #         xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
            #         xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
            #         # Apply zoom to the local coordinates
            #         zoomedX = xy[0] * zoom
            #         zoomedY = xy[1] * zoom
            #         # Offset the zoomed coordinates by the truck's position to "move" the camera
            #         pointX = int(zoomedX + size//2)
            #         pointY = int(zoomedY + size//2)
            #         newPoints.append((pointX, pointY))
            #     cv2.polylines(img, np.int32([newPoints]), False, (0, 0, 255), (1 + (zoom - 1)), cv2.LINE_AA)
            # except:
            #     pass
            
            road = None
        
        except:
            import traceback
            traceback.print_exc()
            pass
    
    if calcCount > 0:
        sys.stdout.write(f"Calculated parallel points for {calcCount} roads\n")
        
    cv2.putText(img, f"Roads: {len(areaRoads)}, Tile: {str(tileCoords)}, Loading: {str(int(skipped))}", (10, 70), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    # Return the image    
    return img


def VisualizePrefabs(data, closePrefabItems, img=None, zoom=2):
    """Will draw the prefabs onto the image.

    Args:
        data (dict): data dictionary.
        img (np.array, optional): Image array. Defaults to None.
        zoom (float, optional): How many pixels is one meter in the data. Defaults to 2.

    Returns:
        np.array: image array
    """
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    
    # Get the roads in the current area
    areaItems = closePrefabItems
    tileCoords = roads.GetTileCoordinates(x, y)
    prefabTileCoords = prefabItems.GetTileCoordinates(x, y)
    
    # Make a blank image of size 1000x1000 (1km x 1km on default zoom)
    if img is None:
        size = 1000
        img = np.zeros((size, size, 3), np.uint8)
    else:
        size = img.shape[0]
    
    truckXY = roads.GetLocalCoordinateInTile(x, y, tileCoords[0], tileCoords[1])
    curveCount = 0
    for item in areaItems:
        try:
            # Draw the curves
            for curve in item.NavigationLanes:
                curveCount += 1
                startXY = roads.GetLocalCoordinateInTile(curve[0], curve[1] , tileCoords[0], tileCoords[1])
                endXY = roads.GetLocalCoordinateInTile(curve[2], curve[3], tileCoords[0], tileCoords[1])
                startXY = (startXY[0] - truckXY[0], startXY[1] - truckXY[1])
                endXY = (endXY[0] - truckXY[0], endXY[1] - truckXY[1])
                # Apply zoom to the local coordinates
                zoomedStartX = startXY[0] * zoom
                zoomedStartY = startXY[1] * zoom
                zoomedEndX = endXY[0] * zoom
                zoomedEndY = endXY[1] * zoom
                # Offset the zoomed coordinates by the truck's position to "move" the camera
                startX = int(zoomedStartX + size//2)
                startY = int(zoomedStartY + size//2)
                endX = int(zoomedEndX + size//2)
                endY = int(zoomedEndY + size//2)
                
                color = (100, 100, 100)
                if item in data["map"]["inBoundingBox"]:
                    color = (0, 100, 0)
                if curve in data["map"]["closestLanes"]:
                    color = (0, 255, 0)
                if curve == data["map"]["closestLane"]:
                    color = (0, 0, 255)
                
                cv2.line(img, (startX, startY), (endX, endY), color, 2 + (zoom - 1))
        except: 
            #import traceback
            #traceback.print_exc()
            pass

    cv2.putText(img, f"Prefabs: {len(areaItems)}, Tile: {str(prefabTileCoords)}", (10, 110), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(img, f"Curves: {curveCount}", (10, 150), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    
    return img

def RotateAroundCenter(point, center, angle):
    """Rotate a point around a center point.

    Args:
        point (tuple): Point to rotate.
        center (tuple): Center point.
        angle (float): Angle in radians.

    Returns:
        tuple: Rotated point.
    """
    pointX = point[0] - center[0]
    pointY = point[1] - center[1]
    newx = pointX * math.cos(angle) - pointY * math.sin(angle)
    newy = pointX * math.sin(angle) + pointY * math.cos(angle)
    return (int(newx + center[0]), int(newy + center[1]))

def VisualizeTruck(data, img=None, zoom=2):
    """Will draw the truck onto the image.

    Args:
        data (dict): data dictionary.
        img (np.array, optional): Image array. Defaults to None.
        zoom (float, optional): How many pixels is one meter in the data. Defaults to 2.

    Returns:
        np.array: image array
    """
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    
    # Make a blank image of size 1000x1000 (1km x 1km on default zoom)
    if img is None:
        size = 1000
        img = np.zeros((size, size, 3), np.uint8)
    else:
        size = img.shape[0]
    
    
    tileXY = roads.GetTileCoordinates(x, y)
    truckXY = roads.GetLocalCoordinateInTile(x, y, tileXY[0], tileXY[1])
    
    # Get the truck wheel positions
    truckWheelPoints = [[i for i in data["api"]["configVector"]["truckWheelPositionX"]], [i for i in data["api"]["configVector"]["truckWheelPositionZ"]]]
    if truckWheelPoints == [[], []]:
        # Draw a circle in the middle
        cv2.circle(img, (size//2, size//2), 2, (255, 0, 0), -1, cv2.LINE_AA)
        return img
    maxX = 0
    maxY = 0
    minX = 10000
    minY = 10000
    for i in range(len(truckWheelPoints[0])):
        point = (truckWheelPoints[0][i], truckWheelPoints[1][i])
        # Apply zoom to the local coordinates
        zoomedX = point[0] * zoom
        zoomedY = point[1] * zoom
        # Center the truck in the image
        pointX = int(zoomedX + size//2)
        pointY = int(zoomedY + size//2)
        # Calculate the bounding box
        if pointX > maxX:
            maxX = pointX
        if pointX < minX:
            minX = pointX
        if pointY > maxY:
            maxY = pointY
        if pointY < minY:
            minY = pointY
            
    point1 = (minX, minY)
    point2 = (maxX, maxY)
    point3 = (point1[0], point2[1])
    point4 = (point2[0], point1[1])
    
    # From -1 to 1
    rotationX = data["api"]["truckPlacement"]["rotationX"]
            
    # Rotate the points around the middle of the screen
    center = (size//2, size//2)
    angle = rotationX * 360
    if angle < 0:
        angle = 360 + angle
    angle = -math.radians(angle)
    rotatedPoints = []
    for point in [point1, point2, point3, point4]:
        rotatedPoints.append(RotateAroundCenter(point, center, angle))
            
    # Draw the truck (can't use rectangle because it doesn't support rotation)
    cv2.line(img, rotatedPoints[0], rotatedPoints[2], (0, 255, 0), 1)
    cv2.line(img, rotatedPoints[2], rotatedPoints[1], (0, 255, 0), 1)
    cv2.line(img, rotatedPoints[1], rotatedPoints[3], (0, 255, 0), 1)
    cv2.line(img, rotatedPoints[3], rotatedPoints[0], (0, 255, 0), 1)
    # Diagonal  
    cv2.line(img, rotatedPoints[0], rotatedPoints[1], (0, 255, 0), 1)
    
     
    # Draw the trailers
    try:
        trailers = data["api"]["trailers"]
    except:
        return img
    for i in range(len(trailers)):
        trailerXY = roads.GetLocalCoordinateInTile(trailers[i]["comDouble"]["worldX"], trailers[i]["comDouble"]["worldZ"], tileXY[0], tileXY[1])
        trailerX = int((trailerXY[0] - truckXY[0]) * zoom + size//2)
        trailerY = int((trailerXY[1] - truckXY[1]) * zoom + size//2)
        trailerWheelPoints = [[i for i in trailers[i]["conVector"]["wheelPositionX"]], [i for i in trailers[i]["conVector"]["wheelPositionZ"]]]
        maxX = 0
        maxY = 0
        minX = 10000
        minY = 10000
        for z in range(len(trailerWheelPoints[0]) + 1):
            if z == len(trailerWheelPoints[0]):
                point = (trailers[i]["conVector"]["hookPositionX"], trailers[i]["conVector"]["hookPositionZ"])
            else:
                point = (trailerWheelPoints[0][z], trailerWheelPoints[1][z])
            # Apply zoom to the local coordinates
            zoomedX = point[0] * zoom
            zoomedY = point[1] * zoom
            # Center the truck in the image
            pointX = int(zoomedX + trailerX)
            pointY = int(zoomedY + trailerY)
            # Calculate the bounding box
            if pointX > maxX:
                maxX = pointX
            if pointX < minX:
                minX = pointX
            if pointY > maxY:
                maxY = pointY
            if pointY < minY:
                minY = pointY
        
        # Draw the trailer
        point1 = (minX, minY)
        point2 = (maxX, maxY)
        point3 = (point1[0], point2[1])
        point4 = (point2[0], point1[1])
        
        # From -1 to 1
        rotationX = trailers[i]["comDouble"]["rotationX"]
        
        # Rotate the points around the middle of the screen
        trailerCenter = (trailerX, trailerY)
        angle = rotationX * 360
        if angle < 0:
            angle = 360 + angle
        angle = -math.radians(angle)
        rotatedPoints = []
        for point in [point1, point2, point3, point4]:
            rotatedPoints.append(RotateAroundCenter(point, trailerCenter, angle))
        
        # Draw the trailer (can't use rectangle because it doesn't support rotation)
        cv2.line(img, rotatedPoints[0], rotatedPoints[2], (0, 255, 0), 1)
        cv2.line(img, rotatedPoints[2], rotatedPoints[1], (0, 255, 0), 1)
        cv2.line(img, rotatedPoints[1], rotatedPoints[3], (0, 255, 0), 1)
        cv2.line(img, rotatedPoints[3], rotatedPoints[0], (0, 255, 0), 1)
        # Diagonal in the opposite dir as the truck
        cv2.line(img, rotatedPoints[2], rotatedPoints[3], (0, 255, 0), 1)
        
    return img


def VisualizeTrafficLights(data, img=None, zoom=2):
    if img is None:
        size = 1000
        img = np.zeros((size, size, 3), np.uint8)
    else:
        size = img.shape[0]
        
    try:
        trafficlights = data["TrafficLightDetection"]["detailed"]
    except:
        trafficlights = []
    for i in range(len(trafficlights)):
        _, ((trafficlight_x, trafficlight_z), (head_x, head_z, head_angle, head_rotation), (firsttrafficlight_x, firsttrafficlight_z, first_head_angle, first_head_rotation)), _, _ = trafficlights[i]
        x = data["api"]["truckPlacement"]["coordinateX"]
        y = data["api"]["truckPlacement"]["coordinateZ"]
        tileCoords = roads.GetTileCoordinates(x, y)
        truckXY = roads.GetLocalCoordinateInTile(x, y, tileCoords[0], tileCoords[1])
        try:
            xy = roads.GetLocalCoordinateInTile(firsttrafficlight_x, firsttrafficlight_z, tileCoords[0], tileCoords[1])
            xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
            zoomedX = xy[0] * zoom
            zoomedY = xy[1] * zoom
            pointX = int(zoomedX + size//2)
            pointY = int(zoomedY + size//2)
            cv2.circle(img, (pointX, pointY), 5, (0, 255, 0), -1, cv2.LINE_AA)
        except:
            pass
        try:
            xy = roads.GetLocalCoordinateInTile(head_x, head_z, tileCoords[0], tileCoords[1])
            xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
            zoomedX = xy[0] * zoom
            zoomedY = xy[1] * zoom
            pointX = int(zoomedX + size//2)
            pointY = int(zoomedY + size//2)
            cv2.circle(img, (pointX, pointY), 5, (255, 0, 255), -1, cv2.LINE_AA)
        except:
            pass
        try:
            xy = roads.GetLocalCoordinateInTile(trafficlight_x, trafficlight_z, tileCoords[0], tileCoords[1])
            xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
            zoomedX = xy[0] * zoom
            zoomedY = xy[1] * zoom
            pointX = int(zoomedX + size//2)
            pointY = int(zoomedY + size//2)
            cv2.circle(img, (pointX, pointY), 5, (0, 0, 255), -1, cv2.LINE_AA)
        except:
            pass
    
    return img

def VisualizePoint(data, point, img=None, zoom=2):
    if img is None:
        size = 1000
        img = np.zeros((size, size, 3), np.uint8)
    else:
        size = img.shape[0]
        
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    tileCoords = roads.GetTileCoordinates(x, y)
    truckXY = roads.GetLocalCoordinateInTile(x, y, tileCoords[0], tileCoords[1])
    try:
        xy = roads.GetLocalCoordinateInTile(point[0], point[2], tileCoords[0], tileCoords[1])
        xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
        zoomedX = xy[0] * zoom
        zoomedY = xy[1] * zoom
        pointX = int(zoomedX + size//2)
        pointY = int(zoomedY + size//2)
        cv2.circle(img, (pointX, pointY), 5, (0, 255, 0), -1, cv2.LINE_AA)
    except:
        pass
    
    return img