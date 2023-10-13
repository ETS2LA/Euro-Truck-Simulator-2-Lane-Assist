import cv2
from plugins.Map.GameData import nodes, roads, prefabs, prefabItems
import math
import numpy as np
import os
import json
import time

def VisualizeRoads(data, img=None, zoom=2, draw_lane=True):
    
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
    cv2.circle(img, (int(converted[0]), int(converted[1])), 5, (0, 0, 255), -1)    
    
    # Draw the roads on the image, 1m is 1px in the image
    # roads have their start and end positions in the global coordinate system so we need to convert them to local coordinates with roads.GetLocalCoordinateInTile()
    for road in areaRoads:
        try:
            if road.Points == None:
                roads.CreatePointsForRoad(road)
            
            newPoints = []
            for point in road.Points:
                xy = roads.GetLocalCoordinateInTile(point[0], point[1], tileCoords[0], tileCoords[1])
                x = xy[0] + 500 * (zoom - 1)
                y = xy[1] + 500 * (zoom - 1)
                newPoints.append((x, y))
            
            if draw_lane == True:
                img = VisualizeLanes(img, road, newPoints, lane_width=4.8)  # draw lane details
            else:
                cv2.polylines(img, np.int32([newPoints]), False, (255, 255, 255), len(road.RoadLook.lanesLeft) + len(road.RoadLook.lanesRight) + (zoom - 1), cv2.LINE_AA)
        except:
            pass
        
    cv2.putText(img, f"Roads: {len(areaRoads)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
    # Return the image
    return img


def VisualizeLanes(img, road, newPoints, lane_width=4.8):
    newPoints = np.array(newPoints)

    # if the road only has one direction, the lane are located in both sides of road backbone. 
    # For example, if the road has 3 lanes, two lanes on the left, one lane on the right; if road has 4 lane, each side has 2 lanes. 
    if len(road.RoadLook.lanesLeft) == 0:
        for i in range((len(road.RoadLook.lanesRight)+1) // 2):
            points_lane = parallel_curve(newPoints, lane_width * (i+1) - road.RoadLook.offset, left=True)
            cv2.polylines(img, np.int32([points_lane]), False, (255, 255, 255), 1, cv2.LINE_AA)
            i = i + 1
        for i in range((len(road.RoadLook.lanesRight)+1) - (len(road.RoadLook.lanesRight)+1) // 2):
            points_lane = parallel_curve(newPoints, lane_width * i + road.RoadLook.offset, left=False)
            cv2.polylines(img, np.int32([points_lane]), False, (255, 255, 255), 1, cv2.LINE_AA)
            i = i + 1
    elif len(road.RoadLook.lanesRight) == 0:
        for i in range((len(road.RoadLook.lanesLeft) + 1) // 2):
            points_lane = parallel_curve(newPoints, lane_width * i + road.RoadLook.offset, left=True)
            cv2.polylines(img, np.int32([points_lane]), False, (255, 255, 255), 1, cv2.LINE_AA)
            i = i + 1
        for i in range((len(road.RoadLook.lanesLeft) + 1) - (len(road.RoadLook.lanesLeft) + 1) // 2):
            points_lane = parallel_curve(newPoints, lane_width * (i+1) - road.RoadLook.offset, left=False)
            cv2.polylines(img, np.int32([points_lane]), False, (255, 255, 255), 1, cv2.LINE_AA)
            i = i + 1
    # if the road only has two directions, just daw theme on each side
    else:
        for i in range(len(road.RoadLook.lanesLeft) + 1):
            points_lane = parallel_curve(newPoints, lane_width * i + road.RoadLook.offset, left=True)
            cv2.polylines(img, np.int32([points_lane]), False, (255, 255, 255), 1, cv2.LINE_AA)
            i = i + 1
        for i in range(len(road.RoadLook.lanesRight) + 1):
            points_lane = parallel_curve(newPoints, lane_width * i + road.RoadLook.offset, left=False)
            cv2.polylines(img, np.int32([points_lane]), False, (255, 255, 255), 1, cv2.LINE_AA)
            i = i + 1
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
    
    curveCount = 0
    for item in areaItems:
        try:
            if item.Prefab.ValidRoad:
                xy = roads.GetLocalCoordinateInTile(item.X, item.Z, tileCoords[0], tileCoords[1])
                x = xy[0] + 500 * (zoom - 1)
                y = xy[1] + 500 * (zoom - 1)
                cv2.circle(img, (int(x), int(y)), 5, (0, 255, 0), -1)
                
                filename = item.Prefab.FilePath.split("/")[-1]
                # cv2.putText(img, filename, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                for curve in item.NavigationLanes:
                    curveCount += 1
                    startXY = roads.GetLocalCoordinateInTile(curve[0] + item.X, curve[1] + item.Z, tileCoords[0], tileCoords[1])
                    endXY = roads.GetLocalCoordinateInTile(curve[2] + item.X, curve[3] + item.Z, tileCoords[0], tileCoords[1])
                    startX = startXY[0] + 500 * (zoom - 1)
                    startY = startXY[1] + 500 * (zoom - 1)
                    endX = endXY[0] + 500 * (zoom - 1)
                    endY = endXY[1] + 500 * (zoom - 1)
                
                    cv2.line(img, (int(startX), int(startY)), (int(endX), int(endY)), (255, 255, 255), 1 + (zoom - 1))
        except: pass
    
    # print(f"Prefabs visualized in {round(time.time() - startTime, 2)} seconds")
    
    cv2.putText(img, f"Prefabs: {len(areaItems)}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, f"Curves: {curveCount}", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return img


def dx(dis, k):
    return np.sqrt(dis / (k**2 + 1.))


def dy(dis, k):
    return k * dx(dis, k)


def parallel_curve(pts, dis=1., left=True):
    # function to compute parallel curve
    # if left==true, compute parallel curve on left 
    if abs((pts[0, 1] - pts[-1, 1]) / (pts[0, 0] - pts[-1, 0])) >= 1:  # avoid slope to be infinitely large
        line_type = "vertical"
        xs, ys = pts[:, 1], pts[:, 0]
    else:
        line_type = "horizontal"
        xs, ys = pts[:, 0], pts[:, 1]
        
    x_t = np.gradient(xs)
    y_t = np.gradient(ys)
    ks = y_t / x_t  # compute slope of each point on curve
    
    g = np.sign(ks)
    g[g == 0] = 1
    ms = -1. / (ks + 1e-20)
    if left == True:
        pxs = xs + dx(dis ** 2, ms) * g
        pys = ys + dy(dis ** 2, ms) * g
    else:
        pxs = xs - dx(dis ** 2, ms) * g
        pys = ys - dy(dis ** 2, ms) * g
    if line_type == "vertical":
        pts_1 = np.concatenate((pys.reshape((-1, 1)), pxs.reshape((-1, 1))), axis=1)
    else:
        pts_1 = np.concatenate((pxs.reshape((-1, 1)), pys.reshape((-1, 1))), axis=1)
    return pts_1

