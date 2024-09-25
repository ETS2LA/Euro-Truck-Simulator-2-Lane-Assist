from GameData import nodes, roads, prefabs, prefabItems
import ETS2LA.plugins.Map.GameData.calc as calc
from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.utils.translator import Translate
import numpy as np
import logging
import cv2
import math
import json
import time
import sys
import os

print = logging.info
runner: PluginRunner = None
LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME = 100
DEBUG_POINTS = []

# MARK: Roads
def VisualizeRoads(data, closeRoads, img=None, zoom=2, drawText=True):
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
    else:
        size = img.shape[0]
    
    # Show the x and y coordinates
    if drawText:
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
                
                try:
                    if road in data["map"]["inBoundingBox"]:
                        color = (0, 150, 0)
                    if lane in data["map"]["closestLanes"]:
                        color = (0, 255, 0)
                    if lane == data["map"]["closestLane"]:
                        color = (0, 0, 255)
                except:
                    pass
                    
                cv2.polylines(img, np.int32([newPoints]), False, color, (2 + (zoom - 1)), cv2.LINE_AA)
                
                laneCount += 1
                
            try:
                if drawText:
                    cv2.putText(img, f"Name: {road.RoadLook.name}", (firstPoint[0], firstPoint[1] + 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.putText(img, f"ID: {road.Uid}", (firstPoint[0], firstPoint[1] + 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    try:
                        lengths = road.Lengths
                        average = sum(lengths) / len(lengths)
                        cv2.putText(img, f"Length: {round(average, 1)}m", (firstPoint[0], firstPoint[1] + 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    except:
                        pass
            except: 
                pass
            
            road = None
        
        except:
            import traceback
            traceback.print_exc()
            pass
    
    if calcCount > 0:
        sys.stdout.write(f"Calculated parallel points for {calcCount} roads\n")
        
    if drawText:
        cv2.putText(img, Translate("map.visualisation.roads.text", values=[len(areaRoads), str(tileCoords), str(int(skipped))]), (10, 70), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    # Return the image    
    return img


# MARK: Prefabs
def VisualizePrefabs(data, closePrefabItems, img=None, zoom=2, drawText=True):
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
            #if item.Prefab.FilePath == "prefab/fork/road_1x_sidewalk_end_4m.ppd":
            #    logging.warning(item.CurvePoints)
            id = 0
            startTime = time.time()
            for curve in item.CurvePoints:
                max_x = -math.inf
                max_y = -math.inf
                min_x = math.inf
                min_y = math.inf
                points = []
                for i in range(len(curve)):
                    point = curve[i]
                    xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
                    xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
                    zoomedX = xy[0] * zoom
                    zoomedY = xy[1] * zoom
                    pointX = int(zoomedX + size//2)
                    pointY = int(zoomedY + size//2)
                    
                    if pointX > max_x:
                        max_x = pointX
                    if pointX < min_x:
                        min_x = pointX
                    if pointY > max_y:
                        max_y = pointY
                    if pointY < min_y:
                        min_y = pointY
                        
                    # Check if the point is within the display area (1000px x 1000px) plus a padding of 200px
                    if pointX > 1000 or pointX < 0 or pointY > 1000 or pointY < 0:
                        continue
                    
                    points.append((pointX, pointY))
                    
                
                color = (100, 100, 100)
                try:
                    if item in data["map"]["inBoundingBox"]:
                        color = (0, 100, 0)
                    if curve in data["map"]["closestLanes"]:
                        color = (0, 255, 0)
                    if curve == data["map"]["closestLane"]:
                        color = (0, 0, 255)
                except:
                    pass
                
                curveCount += 1
                if len(points) == 2:
                    cv2.line(img, points[0], points[1], color, (1 + (zoom - 1)), cv2.LINE_AA)
                else:
                    cv2.polylines(img, np.int32([points]), False, color, (1 + (zoom - 1)), cv2.LINE_AA)
            
            #sys.stdout.write(f"Visualized {len(item.CurvePoints)} curves in {round((time.time() - startTime) * 1000, 1)} ms\n")
            startTime = time.time()
            
            originNode = item.Nodes[0]
    
            if type(item.Prefab) == int:
                item.Prefab = prefabs.GetPrefabByToken(item.Prefab)
            if item.Prefab == None:
                return
            
            try:
                if type(originNode) == dict:
                    originNode = nodes.Node().fromJson(originNode)
            
                mapPointOrigin = item.Prefab.PrefabNodes[item.Origin]
        
                rot = float(originNode.Rotation - math.pi -
                    math.atan2(mapPointOrigin.RotZ, mapPointOrigin.RotX) + math.pi / 2)
            except:
                return
            
            prefabStartX = originNode.X - mapPointOrigin.X
            prefabStartZ = originNode.Z - mapPointOrigin.Z
            prefabStartY = originNode.Y - mapPointOrigin.Y
            
            drawables = []
            points_drawn = set()
            for i in range(len(item.Prefab.MapPoints)):
                map_point = item.Prefab.MapPoints[i]
                points_drawn.add(i)

                if map_point.LaneCount == -1:  # non-road Prefab
                    poly_points = {}
                    next_point = i
                    while next_point != -1:
                        if len(item.Prefab.MapPoints[next_point].Neighbours) == 0:
                            break

                        for neighbour in item.Prefab.MapPoints[next_point].Neighbours:
                            if neighbour not in poly_points:  # New Polygon Neighbour
                                next_point = neighbour
                                new_point = calc.RotatePoint(
                                    prefabStartX + item.Prefab.MapPoints[next_point].X,
                                    prefabStartZ + item.Prefab.MapPoints[next_point].Z, rot, originNode.X,
                                    originNode.Z)
                                poly_points[next_point] = new_point
                                break
                        else:
                            next_point = -1

                    if len(poly_points) < 2:
                        continue
                        
                    #logging.warning(f"First polypoint : {next(iter(poly_points))}")
                    visual_flag = item.Prefab.MapPoints[next(iter(poly_points))].PrefabColorFlags

                    def is_bit_set(number, bit):
                        return number & (1 << bit) != 0

                    fill_color = (120, 120, 120)
                    #road_over = is_bit_set(visual_flag, 0)  # Road Over flag
                    z_index = 10
                    if is_bit_set(visual_flag, 1):
                        fill_color = (120, 120, 120)
                    elif is_bit_set(visual_flag, 2):
                        fill_color = (50, 50, 50)
                        z_index = 11
                    elif is_bit_set(visual_flag, 3):
                        fill_color = (67, 90, 75)
                        z_index = 12
                    # else fill_color = palette['Error']  # Unknown

                    # Now convert the points to local coordinates
                    new_poly_points = {}
                    for key, value in poly_points.items():
                        xy = roads.GetLocalCoordinateInTile(value[0], value[1], tileCoords[0], tileCoords[1])
                        xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
                        zoomedX = xy[0] * zoom
                        zoomedY = xy[1] * zoom
                        pointX = int(zoomedX + size//2)
                        pointY = int(zoomedY + size//2)
                        new_poly_points[key] = (pointX, pointY)

                    if len(new_poly_points) > 2:
                        #logging.warning(f"Drawing polygon with {len(new_poly_points)} points")
                        #logging.warning(new_poly_points)
                        drawables.append([new_poly_points, z_index, fill_color])
                        
                    
                    #prefab_look = TsPrefabPolyLook(list(poly_points.values()), z_index=z_index, color=fill_color)
                    #prefabItem.add_look(prefab_look)
            
                # Get all drawables that are on the same z-index
                z_indexes = [10, 11, 12]
                for z_index in z_indexes:
                    # Get all drawables on the same z-index
                    drawables_z = [drawable for drawable in drawables if drawable[1] == z_index]
                    # Draw the drawables
                    for drawable in drawables_z:
                        cv2.fillPoly(img, [np.int32(list(drawable[0].values()))], drawable[2])
                    
            
            #sys.stdout.write(f"Visualized {len(item.Prefab.MapPoints)} prefab points in {round((time.time() - startTime) * 1000, 1)} ms\n")
            prefabOrigin = (item.X, item.Z)
            prefabXY = roads.GetLocalCoordinateInTile(prefabOrigin[0], prefabOrigin[1], prefabTileCoords[0], prefabTileCoords[1])
            prefabXY = (prefabXY[0] - truckXY[0], prefabXY[1] - truckXY[1])
            zoomedX = prefabXY[0] * zoom
            zoomedY = prefabXY[1] * zoom
            pointX = int(zoomedX + size//2)
            pointY = int(zoomedY + size//2)
            cv2.putText(img, f"{item.Prefab.FilePath}", (pointX, pointY), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(img, f"ID: {item.Uid}", (pointX, pointY + 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
            # Draw the bounding box
            if item.BoundingBox != None:
                boundingBox = item.BoundingBox
                newPoints = []
                #sys.stdout.write(f"Bounding box: {boundingBox}\n")
                for point in boundingBox:
                    xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
                    xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
                    zoomedX = xy[0] * zoom
                    zoomedY = xy[1] * zoom
                    pointX = int(zoomedX + size//2)
                    pointY = int(zoomedY + size//2)
                    newPoints.append((pointX, pointY))
                    
                boundingPoints = []

                boundingPoints.append(newPoints[0])
                boundingPoints.append((newPoints[0][0], newPoints[1][1]))
                boundingPoints.append(newPoints[1])
                boundingPoints.append((newPoints[1][0], newPoints[0][1]))
                    
                cv2.polylines(img, np.int32([boundingPoints]), True, (0, 0, 255), 1, cv2.LINE_AA)
        
        except: 
            #import traceback
            #traceback.print_exc()
            #logging.exception("Error drawing prefab curve")
            pass

    if drawText:
        cv2.putText(img, Translate("map.visualisation.prefabs.prefabs", values=[len(areaItems), str(prefabTileCoords)]), (10, 110), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, Translate("map.visualisation.prefabs.curves", values=[curveCount]), (10, 150), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    
    endTime = time.time()
    #sys.stdout.write(f"Visualized {len(areaItems)} prefabs in {round((endTime - startTime) * 1000, 1)} ms     \r")
    return img

# MARK: Rotate

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

# MARK: Truck

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
    cv2.line(img, rotatedPoints[0], rotatedPoints[2], (0, 255, 0), 1, cv2.LINE_AA)
    cv2.line(img, rotatedPoints[2], rotatedPoints[1], (0, 255, 0), 1, cv2.LINE_AA)
    cv2.line(img, rotatedPoints[1], rotatedPoints[3], (0, 255, 0), 1, cv2.LINE_AA)
    cv2.line(img, rotatedPoints[3], rotatedPoints[0], (0, 255, 0), 1, cv2.LINE_AA)
    # Diagonal  
    cv2.line(img, rotatedPoints[0], rotatedPoints[1], (0, 255, 0), 1, cv2.LINE_AA)
    
     
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
        cv2.line(img, rotatedPoints[0], rotatedPoints[2], (0, 255, 0), 1, cv2.LINE_AA)
        cv2.line(img, rotatedPoints[2], rotatedPoints[1], (0, 255, 0), 1, cv2.LINE_AA)
        cv2.line(img, rotatedPoints[1], rotatedPoints[3], (0, 255, 0), 1, cv2.LINE_AA)
        cv2.line(img, rotatedPoints[3], rotatedPoints[0], (0, 255, 0), 1, cv2.LINE_AA)
        # Diagonal in the opposite dir as the truck
        cv2.line(img, rotatedPoints[2], rotatedPoints[3], (0, 255, 0), 1, cv2.LINE_AA)
        
    return img

# MARK: Traffic Lights

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

def VisualizePoint(data, point, img=None, zoom=2, color=(255,0,0), distance=0, pointSize=1):
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
        #logging.warning(f"Point: {point}")
        try:
            xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
        except:
            xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
        xy = (xy[0] - truckXY[0], xy[1] - truckXY[1])
        zoomedX = xy[0] * zoom
        zoomedY = xy[1] * zoom
        pointX = int(zoomedX + size//2)
        pointY = int(zoomedY + size//2)
        cv2.circle(img, (pointX, pointY), 2 * pointSize, color, -1, cv2.LINE_AA)
        #logging.warning(f"Point: {pointX}, {pointY}")
        if distance != 0:
            # Draw a line and text from the truck to the point
            cv2.line(img, (size//2, size//2), (pointX, pointY), (100,100,100), 1, cv2.LINE_AA)
            cv2.putText(img, f"{round(distance, 1)}m", (pointX, pointY), cv2.FONT_HERSHEY_DUPLEX, 0.5, (100,100,100), 1, cv2.LINE_AA)
        
    except:
        pass
    
    return img

def SetDebugPoints(points):
    global DEBUG_POINTS
    DEBUG_POINTS = points

def VisualizeDebugPoints(data, img=None, zoom=2):
    global DEBUG_POINTS
    if img is None:
        size = 1000
        img = np.zeros((size, size, 3), np.uint8)
    else:
        size = img.shape[0]
    
    for point in DEBUG_POINTS:
        VisualizePoint(data, point, img, zoom, (0, 255, 0), pointSize=4)
    
    return img