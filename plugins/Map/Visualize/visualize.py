import cv2
from plugins.Map.GameData import nodes, roads, prefabs, prefabItems
import math
import numpy as np
import os
import json

def VisualizeRoads(data, img=None):
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = -data["api"]["truckPlacement"]["coordinateZ"]
    
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
        img = np.zeros((1000, 1000, 3), np.uint8)
    
    # Draw the roads on the image, 1m is 1px in the image
    # roads have their start and end positions in the global coordinate system so we need to convert them to local coordinates with roads.GetLocalCoordinateInTile()
    for road in areaRoads:
        roadStartX, roadStartY = road.StartNode.X, road.StartNode.Z
        roadEndX, roadEndY = road.EndNode.X, road.EndNode.Z
        
        roadStartX, roadStartY = roads.GetLocalCoordinateInTile(roadStartX, roadStartY, tileCoords[0], tileCoords[1])
        roadEndX, roadEndY = roads.GetLocalCoordinateInTile(roadEndX, roadEndY, tileCoords[0], tileCoords[1])
        
        # Draw a line from the start to the end
        cv2.line(img, (int(roadStartX), int(roadStartY)), (int(roadEndX), int(roadEndY)), (255, 255, 255), 1)
        
    # Draw the original x and y coordinates on the image
    converted = roads.GetLocalCoordinateInTile(x, y, tileCoords[0], tileCoords[1])
    cv2.circle(img, (int(converted[0]), int(converted[1])), 5, (0, 0, 255), -1)    
        
    # Show the x and y coordinates in addition to the amount of roads
    cv2.putText(img, f"X: {x} Y: {y}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(img, f"Roads: {len(areaRoads)}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
    # Return the image
    
    return img