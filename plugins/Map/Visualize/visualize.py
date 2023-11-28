import cv2
from plugins.Map.GameData import nodes, roads, prefabs, prefabItems
import math
import numpy as np
import os
import json
import time

def VisualizeRoads(data, img=None, zoom=2):
    
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = -data["api"]["truckPlacement"]["coordinateZ"]
    
    
    startTime = time.time()
    
    # Get the roads in the current area
    areaRoads = []
    areaRoads = roads.GetRoadsInTileByCoordinates(x, y)
    tileCoords = roads.GetTileCoordinates(x, y)
    
    # Also get the roads in the surrounding tiles
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y)
    areaRoads += roads.GetRoadsInTileByCoordinates(x, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x, y - 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y - 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y - 1000)
    
    # Make a blank image of size 1000x1000 (1km x 1km)
    if img is None:
        size = int(zoom * 1000)
        img = np.zeros((size, size, 3), np.uint8)
    
    # Show the x and y coordinates
    cv2.putText(img, f"X: {x} Y: {y}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Draw the original x and y coordinates on the image
    converted = roads.GetLocalCoordinateInTile(x, y, tileCoords[0], tileCoords[1])
    converted = (converted[0] + 500 * (zoom - 1), converted[1] + 500 * (zoom - 1))
    cv2.circle(img, (int(int(zoom * 1000)/2), int(int(zoom * 1000)/2)), 5, (0, 0, 255), -1)    
    
    # Draw the roads on the image, 1m is 1px in the image
    # roads have their start and end positions in the global coordinate system so we need to convert them to local coordinates with roads.GetLocalCoordinateInTile()
    for road in areaRoads:
        try:
            if road.Points == None:
                roads.CreatePointsForRoad(road)
            
            newPoints = []
            for point in road.Points:
                xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
                x = xy[0] + 500 * (zoom - 1) - converted[0]
                y = xy[1] + 500 * (zoom - 1) - converted[1]
                newPoints.append((x, y))
            
            # Draw a line from the start to the end
            cv2.polylines(img, np.int32([newPoints]), False, (255, 255, 255), len(road.RoadLook.lanesLeft) + len(road.RoadLook.lanesRight) + (zoom - 1), cv2.LINE_AA)
        except:
            pass
        
    cv2.putText(img, f"Roads: {len(areaRoads)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
    # Return the image
    
    return img


def VisualizePrefabs(data, img=None, zoom=2):
    
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = -data["api"]["truckPlacement"]["coordinateZ"]
    
    
    # Get the roads in the current area
    areaItems = []
    areaItems += prefabItems.GetItemsInTileByCoordinates(x, y)
    tileCoords = roads.GetTileCoordinates(x, y)
    
    # Also get the roads in the surrounding tiles
    areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x, y + 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x, y - 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y + 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y - 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y + 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y - 1000)
    
    # Make a blank image of size 1000x1000 (1km x 1km)
    if img is None:
        size = int(zoom * 1000)
        img = np.zeros((size, size, 3), np.uint8)
        
    startTime = time.time()
    
    converted = prefabItems.GetLocalCoordinateInTile(x, y, tileCoords[0], tileCoords[1])
    converted = (converted[0] + 500 * (zoom - 1), converted[1] + 500 * (zoom - 1))
    
    curveCount = 0
    for item in areaItems:
        try:
            if item.Prefab.ValidRoad:
                xy = prefabItems.GetLocalCoordinateInTile(item.X, item.Z, tileCoords[0], tileCoords[1])
                x = xy[0] + 500 * (zoom - 1) - converted[0]
                y = xy[1] + 500 * (zoom - 1) - converted[1]
                cv2.circle(img, (int(x), int(y)), 5, (0, 255, 0) if item.Padding == 0 else (255, 0, 0), -1)
                
                filename = item.Prefab.FilePath.split("/")[-1] #str(item.Uid)  
                # cv2.putText(img, filename, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                for curve in item.NavigationLanes:
                    curveCount += 1
                    startXY = prefabItems.GetLocalCoordinateInTile(curve[0] + item.X, curve[1] + item.Z , tileCoords[0], tileCoords[1])
                    endXY = prefabItems.GetLocalCoordinateInTile(curve[2] + item.X, curve[3] + item.Z, tileCoords[0], tileCoords[1])
                    startX = startXY[0] + 500 * (zoom - 1) - converted[0]
                    startY = startXY[1] + 500 * (zoom - 1) - converted[1]
                    endX = endXY[0] + 500 * (zoom - 1) - converted[0]
                    endY = endXY[1] + 500 * (zoom - 1) - converted[1]
                
                    cv2.line(img, (int(startX), int(startY)), (int(endX), int(endY)), (255, 255, 255), 1 + (zoom - 1))
        except: pass
    
    # print(f"Prefabs visualized in {round(time.time() - startTime, 2)} seconds")
    
    cv2.putText(img, f"Prefabs: {len(areaItems)}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, f"Curves: {curveCount}", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return img