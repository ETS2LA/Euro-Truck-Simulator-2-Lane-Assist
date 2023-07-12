import os
import cv2
from PIL import Image
import json
import math
import random
import numpy as np
import time

from plugins.Map.VisualizeRoads.Node import Node
from plugins.Map.VisualizeRoads.RoadLook import RoadLook
from plugins.Map.VisualizeRoads.Road import Road
import plugins.Map.VisualizeRoads.utils as utils
import threading
from src.loading import LoadingWindow
import src.mainUI as mainUI

roads = []

roadColor = (0, 0, 0)
shoulderColor = (25, 25, 25)
laneMarkingColor = (255, 255, 255)

GLOBAL_LANE_OFFSET = 0
PARSE_PREFABS = True
# Recommended to keep False
# if you are doing changes to the roadOffsets.json then set to True for real time updates
UPDATE_EACH_FRAME = True

def ParseJsonFile():
    def ParseThread():
        print("Loading JSON file...")
        fileName = "plugins/Map/VisualizeRoads/Roads.json"
        length = len(json.load(open(fileName)))
        counter = 0
        for road in json.load(open(fileName)):
            
            if road["Type"] == "Prefab":
                if PARSE_PREFABS:
                    roadObj = Road()
                    roadObj.Type = road["Type"]
                    roadObj.X = (road["StartPoint"][0] + road["EndPoint"][0]) / 2
                    roadObj.Y = (road["StartPoint"][1] + road["EndPoint"][1]) / 2
                    roadObj.Width = road["Width"]
                    roadObj.RoadLook = RoadLook()
                    roadObj.RoadLook.Offset = road["Offset"]
                    roadObj.RoadLook.Name = "Prefab"
                    if road["LanesCount"] == 1:
                        roadObj.RoadLook.LanesRight = [0]
                    else:
                        # Always make sure that there are more lanes on the right than on the left
                        roadObj.RoadLook.LanesLeft = [i for i in range(math.floor(road["LanesCount"]/2))]
                        roadObj.RoadLook.LanesRight = [i for i in range(math.ceil(road["LanesCount"]/2))]
                    
                    roadObj.Points = [
                    {
                        "X": road["StartPoint"][0],
                        "Y": road["StartPoint"][1],
                        "isEmpty": False  
                    },
                    {
                        "X": road["EndPoint"][0],
                        "Y": road["EndPoint"][1],
                        "isEmpty": False
                    }
                    ]
                    
                    roads.append(roadObj)
                    print("Parsing road " + str(counter) + " of " + str(length) + f" ({round(counter / length * 100)}%)", end="\r")
                    counter += 1
                continue
            
            roadObj = Road()
            roadObj.DlcGuard = road["DlcGuard"]
            roadObj.RoadLook = utils.ParseRoadLook(road["RoadLook"])
            roadObj.IsSecret = road["IsSecret"]
            roadObj.Uid = road["Uid"]
            roadObj.Points = road["_points"]
            # By default this object is None
            try:
                roadObj.Nodes = utils.ParseNodes(road["Nodes"])
            except: pass
            roadObj.BlockSize = road["BlockSize"]
            roadObj.Valid = road["Valid"]
            roadObj.Type = road["Type"]
            
            # The default road center X and Y makes absolutely no sense so we need to calculate it ourselves
            roadCenterX = 0
            roadCenterY = 0
            
            # Average the X and Y of all the points
            for point in roadObj.Points:
                roadCenterX += point["X"]
                roadCenterY += point["Y"]
                
            roadCenterX /= len(roadObj.Points)
            roadCenterY /= len(roadObj.Points)
            
            roadObj.X = roadCenterX
            roadObj.Y = roadCenterY
            
            
            roadObj.Hidden = road["Hidden"]
            roadObj.StartNode = utils.ParseNode(road["StartNode"])
            roadObj.EndNode = utils.ParseNode(road["EndNode"])
            
            # Create a bounding box with the Start and End nodes
            roadObj.BoundingBox = [roadObj.Points[0]["X"], roadObj.Points[0]["Y"], roadObj.Points[-1]["X"], roadObj.Points[-1]["Y"]]
            
            roadObj.Width = road["Width"]
            roads.append(roadObj)
            print("Parsed road " + str(counter) + " of " + str(length), end="\r")
            counter += 1
        
        # Loop through the roads and append them to the correct map tile
        print("Calculating road positions...")
        for road in roads:
            xy = utils.ConvertGameXYToPixelXY(road.X, road.Y)
            x = xy[0]
            y = xy[1]
            # The map tiles are 512x512 so we need to divide the x and y by 512
            x = math.floor(x / 512)
            y = math.floor(y / 512)
            # Append the road to the correct map tile
            try:
                utils.data["folders"][x]["files"][y]["roads"]
            except:
                utils.data["folders"][x]["files"][y]["roads"] = []
                
            utils.data["folders"][x]["files"][y]["roads"].append(road)
        
        print("")
        print("Connecting roads...")
        tiles = 255
        for x in range(tiles):
            print("Connecting roads in tile " + str(x) + " of " + str(tiles), end="\r")
            for y in range(tiles):
                if "roads" in utils.data["folders"][x]["files"][y]:
                    ConnectRoadsInTile(x, y)
        
        print("Parsed " + str(length) + " roads         ")
    
    thread = threading.Thread(target=ParseThread)
    thread.start()
    # Wait for it to finish asynchronously
    while thread.is_alive():
        time.sleep(1)
        mainUI.root.update()
        pass
    
     
    
def IsInsideBoundingBox(x, y, boundingBox):
    # Bounding box = [x1, y1, x2, y2]
    if x > boundingBox[0] and x < boundingBox[2] and y > boundingBox[1] and y < boundingBox[3]:
        return True
    return False
    
def ConnectRoadsInTile(tileX, tileY):
    tileRoads = utils.data["folders"][tileX]["files"][tileY]["roads"]
    
    
    def DistanceBetweenPoints(pointA, pointB):
        return math.sqrt((pointA[0] - pointB[0])**2 + (pointA[1] - pointB[1])**2)
    
    # Connect start and end nodes within x meters of each other
    connectDistance = 2
    counter = 0
    length = len(tileRoads)
    for road in tileRoads:
        for otherRoad in tileRoads:
            roadPoint = (road.Points[0]["X"], road.Points[0]["Y"])
            otherRoadPoint = (otherRoad.Points[-1]["X"], otherRoad.Points[-1]["Y"])
            
            if DistanceBetweenPoints(roadPoint, otherRoadPoint) < connectDistance:
                road.Points[0] = {
                    "X": otherRoadPoint[0],
                    "Y": otherRoadPoint[1],
                    "isEmpty": False    
                }
                break
        counter += 1
    

def Get3x3Roads(x, y):
    foundRoads = []
    try: foundRoads += utils.data["folders"][x]["files"][y]["roads"]
    except: pass
    try: foundRoads += utils.data["folders"][x+1]["files"][y]["roads"]
    except: pass
    try: foundRoads += utils.data["folders"][x-1]["files"][y]["roads"]
    except: pass
    try: foundRoads += utils.data["folders"][x]["files"][y+1]["roads"]
    except: pass
    try: foundRoads += utils.data["folders"][x]["files"][y-1]["roads"]
    except: pass
    try: foundRoads += utils.data["folders"][x+1]["files"][y+1]["roads"]
    except: pass
    try: foundRoads += utils.data["folders"][x+1]["files"][y-1]["roads"]
    except: pass
    try: foundRoads += utils.data["folders"][x-1]["files"][y+1]["roads"]
    except: pass
    try: foundRoads += utils.data["folders"][x-1]["files"][y-1]["roads"]
    except: pass
    
    return foundRoads


def CalculateParallelCurves(road):
    import numpy as np
    
    try:
        points = road.Points
        lanesLeft = len(road.RoadLook.LanesLeft)
        lanesRight = len(road.RoadLook.LanesRight)
        
        if road.RoadLook.RoadSizeLeft != 999:
            roadSizeLeft = road.RoadLook.RoadSizeLeft
            roadSizeRight = road.RoadLook.RoadSizeRight
        else:
            roadSizeLeft = road.Width / 2
            roadSizeRight = road.Width / 2
          
        if road.RoadLook.ShoulderSpaceLeft != 999:
            roadSizeLeft -= road.RoadLook.ShoulderSpaceLeft
        if road.RoadLook.ShoulderSpaceRight != 999:
            roadSizeRight -= road.RoadLook.ShoulderSpaceRight

        # Calculate lane width
        totalRoadWidth = roadSizeRight + roadSizeLeft
        try:
            laneWidth = totalRoadWidth / (lanesRight + lanesLeft)
        except:
            laneWidth = totalRoadWidth / 1

        # Get the offset for the current road type
        roadOffset = utils.GetRoadOffset(road.RoadLook.Name)

        # Calculate the points for each lane
        newPoints = []

        pointCounter = 0
        for point in points:
            x = point['X']
            y = point['Y']

            # Calculate the tangent vector at the point
            tangentVector = np.array([0, 0])
            if pointCounter < len(points) - 1:
                xPoints = np.array([points[pointCounter]['X'], points[pointCounter + 1]['X']])
                yPoints = np.array([points[pointCounter]['Y'], points[pointCounter + 1]['Y']])
                # Try and not use np.gradient
                # tangentVector = np.gradient(yPoints, xPoints).T
                tangentVector = np.array([xPoints[1] - xPoints[0], yPoints[1] - yPoints[0]])
            else:
                xPoints = np.array([points[pointCounter - 1]['X'], points[pointCounter]['X']])
                yPoints = np.array([points[pointCounter - 1]['Y'], points[pointCounter]['Y']])
                tangentVector = np.array([xPoints[1] - xPoints[0], yPoints[1] - yPoints[0]])
                

            # Calculate the normal vector (perpendicular to the tangent)
            normalVector = np.array([-tangentVector[1], tangentVector[0]])

            # Normalize the normal vector
            normalVector /= np.linalg.norm(normalVector, axis=0)

            # Calculate the offset for each lane
            laneOffsetsLeft = np.arange(-lanesLeft - 1, -1) * laneWidth
            laneOffsetsRight = np.arange(1, lanesRight + 1) * laneWidth

            # Calculate the new points for each lane
            counter = 0
            for laneOffset in laneOffsetsLeft:
                
                if laneOffset == 0:
                    continue
                
                
                if lanesRight > 0:
                    if road.RoadLook.Name is not "Prefab":
                        laneOffset += road.RoadLook.Offset / 2
                        laneOffset += laneWidth / 2
                else:
                    laneOffset += laneWidth
                
                laneOffset -= GLOBAL_LANE_OFFSET
                laneOffset -= roadOffset
                
                newPoints.append([])
                offsetVector = laneOffset * normalVector

                newPoint = np.array([x, y]) + offsetVector.T
                newPoints[counter].append(newPoint.tolist())
                counter += 1

            for laneOffset in laneOffsetsRight:
                
                if laneOffset == 0:
                    continue
                
                if lanesLeft > 0:
                    laneOffset -= road.RoadLook.Offset / 2
                    laneOffset -= laneWidth / 2
                else: 
                    laneOffset -= laneWidth
                    
                laneOffset -= GLOBAL_LANE_OFFSET
                laneOffset -= roadOffset
                
                
                newPoints.append([])
                offsetVector = laneOffset * normalVector

                newPoint = np.array([x, y]) + offsetVector.T
                newPoints[counter].append(newPoint.tolist())
                counter += 1

            pointCounter += 1

        return newPoints, laneWidth
        
    except Exception as ex:
        return [[], []], 0


def FindClosestLane(x,y, lanes):
    closestLane = None
    closestLaneDistance = 999
    
    # First get the players percentage of each lane
    lanePercentages = []
    for lane in lanes:
        
        if lane == []: continue
        
        startPoint = lane[0]
        endPoint = lane[-1]
        playerPoint = [x, y]
        
        # Calculate the distance between the player and the start and end points
        startDistance = math.sqrt((startPoint[0] - playerPoint[0])**2 + (startPoint[1] - playerPoint[1])**2)
        endDistance = math.sqrt((endPoint[0] - playerPoint[0])**2 + (endPoint[1] - playerPoint[1])**2)
        sumDistance = startDistance + endDistance
        
        percentage = startDistance / sumDistance
        lanePercentages.append(percentage)
        
    # Now for each lane interpolate the point that maches the players percentage
    interpolatedPoints = []
    pointsLanes = []
    for lane in lanes:
        
        if lane == []: continue
        
        # Get the two points closest to the player
        firstPoint = None
        firstPointDistance = 999999
        secondPoint = None
        secondPointDistance = 999999
        for point in lane:
            distance = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
            if distance < firstPointDistance:
                secondPoint = firstPoint
                secondPointDistance = firstPointDistance
                firstPoint = point
                firstPointDistance = distance
            elif distance < secondPointDistance:
                secondPoint = point
                secondPointDistance = distance
        
        if firstPoint == None or secondPoint == None:
            continue
        
        # Get the percentage of the first point
        startDistance = math.sqrt((firstPoint[0] - x)**2 + (firstPoint[1] - y)**2)
        endDistance = math.sqrt((secondPoint[0] - x)**2 + (secondPoint[1] - y)**2)
        sumDistance = startDistance + endDistance
        firstPointPercentage = startDistance / sumDistance
        
        # Get the percentage of the second point
        startDistance = math.sqrt((firstPoint[0] - x)**2 + (firstPoint[1] - y)**2)
        endDistance = math.sqrt((secondPoint[0] - x)**2 + (secondPoint[1] - y)**2)
        sumDistance = startDistance + endDistance
        secondPointPercentage = startDistance / sumDistance
        
        # Interpolate the point
        newPoint = [0, 0]
        newPoint[0] = firstPoint[0] + (secondPoint[0] - firstPoint[0]) * firstPointPercentage
        newPoint[1] = firstPoint[1] + (secondPoint[1] - firstPoint[1]) * firstPointPercentage
        
        interpolatedPoints.append(newPoint)
        pointsLanes.append(lane)
    
    for i in range(len(interpolatedPoints)):
        point = interpolatedPoints[i]
        distance = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
        if distance < closestLaneDistance:
            closestLane = pointsLanes[i]
            closestLaneDistance = distance
        
                
    return closestLane


def OffsetPixelToBeInCenterOfTile(xy, mapX, mapY, ImgSize):
    pointX = xy[0]
    pointY = xy[1]
    pointX -= mapX * 512 - 512
    pointY -= mapY * 512 - 512
    
    return pointX, pointY


lastClosestRoad = None
def DrawVisualization(x, y, roadsWithin):
    global lastClosestRoad
    
    # Convert the x and y to pixel coordinates
    xy = utils.ConvertGameXYToPixelXY(x, y)
    mapX = xy[0]
    mapY = xy[1]
    
    # Find the map tile it's in
    mapX = math.floor(mapX / 512)
    mapY = math.floor(mapY / 512)
    
    
    startTime = time.time()
    # Show the road locations on a map
    # A nice dark blue for the background
    # CV2 uses BGR instead of RGB
    backgroundColor = (25, 0, 0)
    img = Image.new("RGB", (512*3, 512*3), backgroundColor)
    img = np.array(img)
    
    # Get the road closes to the x and y coordinates
    closestRoad = None
    closestRoadDistance = 9999
    for road in roadsWithin:
        if road.Valid:
            startNode = road.Points[0]
            endNode = road.Points[-1]
            distanceToStart = math.sqrt((startNode["X"] - x)**2 + (startNode["Y"] - y)**2)
            distanceToEnd = math.sqrt((endNode["X"] - x)**2 + (endNode["Y"] - y)**2)
            minDistance = min(distanceToStart, distanceToEnd)
            
            # Check if either is closer than the current closest road
            if minDistance < closestRoadDistance:
                closestRoad = road
                closestRoadDistance = minDistance
            
        
    
    #if IsInsideBoundingBox(x, y, closestRoad.BoundingBox):     
    roadsWithin.remove(closestRoad)
    #else:
    #    closestRoad = None
    
    for road in roadsWithin:
        try:
            if road.Valid:
                if road.LanePoints == [] or UPDATE_EACH_FRAME:
                    lanePoints, laneWidth = CalculateParallelCurves(road)

                    if lanePoints == None or laneWidth == None:
                        continue
                    
                    road.LanePoints = lanePoints
                    road.LaneWidth = laneWidth
                else:
                    lanePoints = road.LanePoints
                    laneWidth = road.LaneWidth
                
                # Draw the road under the lanes
                screenPoints = []
                for points in road.Points:
                    pointX, pointY = OffsetPixelToBeInCenterOfTile(utils.ConvertGameXYToPixelXY(points["X"], points["Y"]), mapX, mapY, 512*3)
                    
                    screenPoints.append([int(pointX), int(pointY)])
                
                
                cv2.polylines(img, np.int32([screenPoints]), False, (50,50,50), int(road.Width), cv2.LINE_AA)
                for lane in lanePoints:
                    screenPoints = []
                    for points in lane:
                        pointX, pointY = OffsetPixelToBeInCenterOfTile(utils.ConvertGameXYToPixelXY(points[0], points[1]), mapX, mapY, 512*3)
                        screenPoints.append([int(pointX), int(pointY)])
                        
                    cv2.polylines(img, np.int32([screenPoints]), False, (255,255,255), int(laneWidth / 4), cv2.LINE_AA)
        
        except:
            continue
            
                
    
    if closestRoad != None:
        if closestRoad.Valid:
            try:
                if lastClosestRoad.RoadLook.Name != closestRoad.RoadLook.Name:
                    lastClosestRoad = closestRoad
                    print("Entered road type " + closestRoad.RoadLook.Name)
            except:
                print("Entered road type " + closestRoad.RoadLook.Name)
                lastClosestRoad = closestRoad
            
            lanePoints, laneWidth = CalculateParallelCurves(closestRoad)

            # Draw the road under the lanes
            screenPoints = []
            for points in closestRoad.Points:
                pointX, pointY = OffsetPixelToBeInCenterOfTile(utils.ConvertGameXYToPixelXY(points["X"], points["Y"]), mapX, mapY, 512*3)
            
            cv2.polylines(img, np.int32([screenPoints]), False, (50,50,50), int(closestRoad.Width), cv2.LINE_AA)

            try:
                for lane in lanePoints:
                    screenPoints = []
                    for points in lane:
                        pointX, pointY = OffsetPixelToBeInCenterOfTile(utils.ConvertGameXYToPixelXY(points[0], points[1]), mapX, mapY, 512*3)
                        
                        screenPoints.append([int(pointX), int(pointY)])
                    
                    # print(screenPoints)
                    cv2.polylines(img, np.int32([screenPoints]), False, (255,255,255), int(laneWidth / 4), cv2.LINE_AA)
            except: pass
                
            try:
                closestLanePoints = []
                closestLane = FindClosestLane(x, y, lanePoints)
                for points in closestLane:
                    pointX, pointY = OffsetPixelToBeInCenterOfTile(utils.ConvertGameXYToPixelXY(points[0], points[1]), mapX, mapY, 512*3)
                    closestLanePoints.append([int(pointX), int(pointY)])
            
                cv2.polylines(img, np.int32([closestLanePoints]), False, (255,0,255), int(laneWidth / 4), cv2.LINE_AA)
            except Exception as ex: 
                pass
        
    # Render the target point
    pointX, pointY = OffsetPixelToBeInCenterOfTile(utils.ConvertGameXYToPixelXY(x, y), mapX, mapY, 512*3)
    cv2.circle(img, (int(pointX), int(pointY)), 2, (255, 255, 0), -1, cv2.LINE_AA)
    
    # Flip the map upside down
    img = cv2.flip(img, 0)
    
    # Zoom in onto the targe point (make it 1024x1024)
    fromX = int(pointX - 512/2)
    toX = int(pointX + 512/2)
    fromY = int(-pointY - 512/2)
    toY = int(-pointY + 512/2)
    img = img[fromY:toY, fromX:toX]
    
    
    cv2.putText(img, str(round(x)) + ", " + str(round(y)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 2, cv2.LINE_AA)    
    
    if closestRoad == None:
        cv2.putText(img, "Not on a road", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2, cv2.LINE_AA) 
    
    endTime = time.time()
    ms = (endTime - startTime) * 1000
    cv2.putText(img, "Took " + str(round(ms)) + "ms to draw", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 2, cv2.LINE_AA)
    
    return img

def GetRoadsWithinRange(x, y, range):
    
    # Convert the x and y to pixel coordinates
    xy = utils.ConvertGameXYToPixelXY(x, y)
    mapX = xy[0]
    mapY = xy[1]
    
    # Find the map tile it's in
    mapX = math.floor(mapX / 512)
    mapY = math.floor(mapY / 512)
    
    # Get the roads in that map tile, in addition to the 8 surrounding tiles
    foundRoads = Get3x3Roads(mapX, mapY)
        
    
    # Loop through the roads and find the ones within the range
    roadsWithin = []
    for road in foundRoads:
        if road.X > x - range and road.X < x + range and road.Y > y - range and road.Y < y + range:
            roadsWithin.append(road)
    
    if roadsWithin == []:
        return None
    
    return roadsWithin


        