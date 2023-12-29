import os
import cv2
from PIL import Image
import json
import math
import random
import numpy as np
import time

from plugins.Map.Old.VisualizeRoads.Node import Node
from plugins.Map.Old.VisualizeRoads.RoadLook import RoadLook
from plugins.Map.Old.VisualizeRoads.Road import Road
import plugins.Map.Old.VisualizeRoads.utils as utils
import threading
from src.loading import LoadingWindow
import src.mainUI as mainUI
from scipy.interpolate import interp1d

roads = []

roadColor = (0, 0, 0)
shoulderColor = (25, 25, 25)
laneMarkingColor = (255, 255, 255)

GLOBAL_LANE_OFFSET = 0
PARSE_PREFABS = True
# Recommended to keep False
# if you are doing changes to the roadOffsets.json then set to True for real time updates
UPDATE_EACH_FRAME = False

parsingDone = False
def ParseJsonFile():
    global parsingDone

    
    def ParseThread():
        global parsingDone
        loading = LoadingWindow("Loading JSON file...", progress=0)
        print("Loading JSON file...")
        loading.update(progress=0, text="Loading JSON file...")
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
                    
                    # Create a bounding box with the Start and End nodes
                    roadObj.BoundingBox = [roadObj.Points[0]["X"] - 2, roadObj.Points[0]["Y"] + 2, roadObj.Points[-1]["X"] + 2, roadObj.Points[-1]["Y"] - 2]
                    
                    if roadObj.RoadLook.LanesLeft != [] or roadObj.RoadLook.LanesRight != []:
                        roads.append(roadObj)
                        
                    if counter % 1000 == 0:
                        loading.update(progress=(counter / length * 100), text=f"Parsing road {counter} of {length} ({round(counter / length * 100)}%)")
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
            roadObj.BoundingBox = [roadObj.Points[0]["X"] - 2, roadObj.Points[0]["Y"] + 2, roadObj.Points[-1]["X"] + 2, roadObj.Points[-1]["Y"] - 2]
            
            roadObj.Width = road["Width"]
            
            if roadObj.RoadLook != None:
                roads.append(roadObj)
            
            if counter % 1000 == 0:
                loading.update(progress=(counter / length * 100), text=f"Parsing road {counter} of {length} ({round(counter / length * 100)}%)")
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
        # print("Connecting roads...")
        # tiles = 255
        # for x in range(tiles):
        #     print("Connecting roads in tile " + str(x) + " of " + str(tiles), end="\r")
        #     for y in range(tiles):
        #         if "roads" in utils.data["folders"][x]["files"][y]:
        #             ConnectRoadsInTile(x, y)
        # 
        parsingDone = True
        print("Successfully parsed " + str(len(roads)) + f" roads ({round(len(roads) / length*100)}%)        ")
        loading.destroy()
    
    thread = threading.Thread(target=ParseThread)
    thread.start()
    thread.join()
    print("Done parsing")
    
     
    
def IsInsideBoundingBox(x, y, boundingBox):
    # Bounding box = [x1, y1, x2, y2]
    try:
        
        if x > boundingBox[0] and x < boundingBox[2] and y > boundingBox[1] and y < boundingBox[3]:
            return True
    
    except: pass
    return False
    
def ConnectRoadsInTile(tileX, tileY):
    tileRoads = utils.data["folders"][tileX]["files"][tileY]["roads"]
    
    
    def DistanceBetweenPoints(pointA, pointB):
        return math.sqrt((pointA[0] - pointB[0])**2 + (pointA[1] - pointB[1])**2)
    
    # Connect start and end nodes within x meters of each other
    connectDistance = 50
    counter = 0
    length = len(tileRoads)
    connectedRoads = 0
    for road in tileRoads:
        if road.Type != "Prefab":
            for otherRoad in tileRoads:
                if otherRoad.Type != "Prefab":
                    roadPoint = (road.Points[0]["X"], road.Points[0]["Y"])
                    otherRoadPoint = (otherRoad.Points[-1]["X"], otherRoad.Points[-1]["Y"])
                    
                    if DistanceBetweenPoints(roadPoint, otherRoadPoint) < connectDistance:
                        road.Points[0] = {
                            "X": otherRoadPoint[0],
                            "Y": otherRoadPoint[1],
                            "isEmpty": False    
                        }
                        connectedRoads += 1
        counter += 1
    print(f"Connected {connectedRoads} roads")
    

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
            roadSizeLeft += road.RoadLook.ShoulderSpaceLeft
        if road.RoadLook.ShoulderSpaceRight != 999:
            roadSizeRight += road.RoadLook.ShoulderSpaceRight

        # Calculate lane width
        totalRoadWidth = roadSizeRight + roadSizeLeft
        try:
            laneWidth = totalRoadWidth / (lanesRight + lanesLeft)
        except:
            laneWidth = totalRoadWidth

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
                    laneOffset += road.RoadLook.Offset / 2
                    if road.Type != "Prefab":
                        laneOffset += laneWidth
                    else:
                        laneOffset += laneWidth - (laneWidth / 3)
                else:
                    laneOffset += laneWidth
                
                laneOffset -= GLOBAL_LANE_OFFSET
                laneOffset -= roadOffset[0]
                
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
                    if road.Type != "Prefab":
                        laneOffset -= laneWidth
                    else:
                        laneOffset -= laneWidth - (laneWidth / 3)
                else: 
                    laneOffset -= laneWidth
                    
                laneOffset -= GLOBAL_LANE_OFFSET
                laneOffset -= roadOffset[1]
                
                
                newPoints.append([])
                offsetVector = laneOffset * normalVector

                newPoint = np.array([x, y]) + offsetVector.T
                newPoints[counter].append(newPoint.tolist())
                counter += 1

            pointCounter += 1

        # Calculate a new bounding box for the road using these points
        boundingBox = [999999, 999999, -999999, -999999]
        for lane in newPoints:
            for point in lane:
                if point[0] < boundingBox[0]:
                    boundingBox[0] = point[0]
                if point[1] < boundingBox[1]:
                    boundingBox[1] = point[1]
                if point[0] > boundingBox[2]:
                    boundingBox[2] = point[0]
                if point[1] > boundingBox[3]:
                    boundingBox[3] = point[1]
                    
        road.BoundingBox = boundingBox

        return newPoints, laneWidth
        
    except Exception as ex:
        return [[], []], 0

def DrawBoundingBox(x,y, img, boundingbox, mapX, mapY, ImgSize):
    # Bounding box = [x1, y1, x2, y2]
    # Convert the coordinates to pixel coordinates
    x1, y1 = OffsetPixelToBeInCenterOfTile(utils.ConvertGameXYToPixelXY(boundingbox[0], boundingbox[1]), mapX, mapY, ImgSize)
    x2, y2 = OffsetPixelToBeInCenterOfTile(utils.ConvertGameXYToPixelXY(boundingbox[2], boundingbox[3]), mapX, mapY, ImgSize)
    
    
    if IsInsideBoundingBox(x,y, boundingbox):
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 1, cv2.LINE_AA)
    else:
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 50, 0), 1, cv2.LINE_AA)
    
    
lastSteering = 0
def CalculateSteeringToCenterOfLane(x, y, lane, data, laneIndex, road):
    global lastSteering
    
    steering = 0
    
    # Get the percentage we are through the lane
    startPoint = lane[0]
    endPoint = lane[-1]
    distanceToStart = math.sqrt((startPoint[0] - x)**2 + (startPoint[1] - y)**2)
    distanceToEnd = math.sqrt((endPoint[0] - x)**2 + (endPoint[1] - y)**2)
    
    percentage = distanceToStart / (distanceToStart + distanceToEnd)
    
    # Find the two closest points that match the percentage
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
        return 0
    
    
    try:
        # Get all the xPoints and yPoints
        xPoints = np.array(lane)[:,0]
        yPoints = np.array(lane)[:,1]
        
        # Calculate distance between consecutive points
        dist = np.sqrt((np.diff(xPoints) ** 2) + (np.diff(yPoints) ** 2))
        dist = np.concatenate(([0], dist))  # Insert a distance of 0 for the first point

        # Calculate cumulative distance
        cumulative_dist = np.cumsum(dist)

        # Normalize cumulative distance between 0 and 1
        t = cumulative_dist / cumulative_dist[-1]

        # Perform cubic spline interpolation
        f = interp1d(t, np.array(lane), kind='cubic', axis=0)
        
        # Get the new point
        newPoint = f(percentage)
        
        # Find the distance between the player and the new point
    except:
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
    
    newPointDistance = math.sqrt((newPoint[0] - x)**2 + (newPoint[1] - y)**2)
    # Get the player's velocity
    try:
        velocity = data["api"]["velocity"]
        newPosition = [x + velocity[0], y + velocity[1]]
        
        # Check if this position is closer to the start or the end of the lane
        newDistanceToStart = math.sqrt((startPoint[0] - newPosition[0])**2 + (startPoint[1] - newPosition[1])**2)
        
        if newDistanceToStart < distanceToStart:
            # We want to be on the right side of the road
            # Calculate the distance to the new point
            distanceToNewPoint = math.sqrt((newPoint[0] - x)**2 + (newPoint[1] - y)**2)
            
            # Right side
            # Get a vector from the new point to the player
            vector = [x - newPoint[0], y - newPoint[1]]
            # Get the tangent of the road
            tangent = [endPoint[0] - startPoint[0], endPoint[1] - startPoint[1]]
            # Normalize both vectors
            vector = [vector[0] / math.sqrt(vector[0]**2 + vector[1]**2), vector[1] / math.sqrt(vector[0]**2 + vector[1]**2)]
            tangent = [tangent[0] / math.sqrt(tangent[0]**2 + tangent[1]**2), tangent[1] / math.sqrt(tangent[0]**2 + tangent[1]**2)]
            
            # Compare them and see if we are to the right or the left
            newCrossProduct = tangent[0] * vector[1] - tangent[1] * vector[0]
            
            # We are to the right
            if newCrossProduct > 0:
                steering = -math.pow(distanceToNewPoint, 2)
            
            # We are to the left
            elif newCrossProduct < 0:
                steering = math.pow(distanceToNewPoint, 2)

            else:
                steering = lastSteering
                
                
        else:
            # We want to be on the right side of the road
            # Calculate the distance to the new point
            distanceToNewPoint = math.sqrt((newPoint[0] - x)**2 + (newPoint[1] - y)**2)
            
            # Right side
            # Get a vector from the new point to the player
            vector = [x - newPoint[0], y - newPoint[1]]
            # Get the tangent of the road
            tangent = [endPoint[0] - startPoint[0], endPoint[1] - startPoint[1]]
            # Compare them and see if we are to the right or the left
            newCrossProduct = vector[0] * tangent[1] - vector[1] * tangent[0]
            
            # We are to the right
            if newCrossProduct < 0:
                steering = math.pow(distanceToNewPoint, 2)
            
            # We are to the left
            elif newCrossProduct > 0:
                steering = -math.pow(distanceToNewPoint, 2)
                
            else:
                steering = lastSteering
            
    
    except:
        import traceback
        traceback.print_exc()
        steering = 0
    
    lastSteering = steering
    return -steering
    
    

def FindClosestLane(x,y, lanes, road = None):
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
        
    
    # Find which index the lane is in
    if road != None:
        index = 0
        counter = 0
        for lane in road.LanePoints:
            if lane == closestLane:
                index = counter
                break
            counter += 1
            
        return closestLane, index, road
    
    else:
        return closestLane


def OffsetPixelToBeInCenterOfTile(xy, mapX, mapY, ImgSize):
    pointX = xy[0]
    pointY = xy[1]
    pointX -= mapX * 512 - 512
    pointY -= mapY * 512 - 512
    
    return pointX, pointY


def FindClosestRoad(x, y, closestRoads):
    closestRoad = None
    closestRoadDistance = 9999
    roadsIn = []
    for road in closestRoads:
        if road.Valid:
            if IsInsideBoundingBox(x, y, road.BoundingBox):
                roadsIn.append(road)
            
    for road in roadsIn:
        distance = math.sqrt((road.X - x)**2 + (road.Y - y)**2)
        if distance < closestRoadDistance:
            closestRoad = road
            closestRoadDistance = distance
    
    return closestRoad, closestRoadDistance

lastClosestRoad = None
def DrawVisualization(x, y, roadsWithin, closestRoad, closestLane):
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
                
                DrawBoundingBox(x,y,img,road.BoundingBox, mapX, mapY, 512*3)
                
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
                    print("")
                    print("Entered road type " + closestRoad.RoadLook.Name)
                    print("New width: " + str(closestRoad.Width))
                    print("Lanes left: " + str(len(closestRoad.RoadLook.LanesLeft)))
                    print("Lanes right: " + str(len(closestRoad.RoadLook.LanesRight)))
                    print("Offset: " + str(closestRoad.RoadLook.Offset))
                    print("Shoulder Space Left: " + str(closestRoad.RoadLook.ShoulderSpaceLeft))
                    print("Shoulder Space Right: " + str(closestRoad.RoadLook.ShoulderSpaceRight))
            except:
                print("")
                print("Entered road type " + closestRoad.RoadLook.Name)
                print("New width: " + str(closestRoad.Width))
                print("Lanes left: " + str(len(closestRoad.RoadLook.LanesLeft)))
                print("Lanes right: " + str(len(closestRoad.RoadLook.LanesRight)))
                print("Offset: " + str(closestRoad.RoadLook.Offset))
                print("Shoulder Space Left: " + str(closestRoad.RoadLook.ShoulderSpaceLeft))
                print("Shoulder Space Right: " + str(closestRoad.RoadLook.ShoulderSpaceRight))
                lastClosestRoad = closestRoad
                
            if lastClosestRoad != closestRoad:
                lastClosestRoad = closestRoad
                print("")
                print("New width: " + str(closestRoad.Width))
                print("Lanes left: " + str(len(closestRoad.RoadLook.LanesLeft)))
                print("Lanes right: " + str(len(closestRoad.RoadLook.LanesRight)))
                print("Offset: " + str(closestRoad.RoadLook.Offset))
                print("Shoulder Space Left: " + str(closestRoad.RoadLook.ShoulderSpaceLeft))
                print("Shoulder Space Right: " + str(closestRoad.RoadLook.ShoulderSpaceRight))
                
            
            lanePoints, laneWidth = CalculateParallelCurves(closestRoad)

            DrawBoundingBox(x,y,img,road.BoundingBox, mapX, mapY, 512*3)

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
    
    print("Took " + str(round(ms)) + "ms to draw", end="\r")
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
    
    for road in roadsWithin:
        if road.LanePoints == [] or UPDATE_EACH_FRAME:
            lanePoints, laneWidth = CalculateParallelCurves(road)

            if lanePoints == None or laneWidth == None:
                continue
            
            road.LanePoints = lanePoints
            road.LaneWidth = laneWidth
    
    return roadsWithin


        