from ETS2LA.plugins.Map.GameData.prefabItems import PrefabItem, GetPrefabItemByUid, FindItemsWithFerryUid
from ETS2LA.plugins.Map.GameData.companies import Company, GetCompanyInCity, GetCompaniesByName
from ETS2LA.plugins.Map.GameData.roads import Road, GetRoadByUid
import ETS2LA.plugins.Map.GameData.ferries as ferries
import ETS2LA.plugins.Map.GameData.roads as roads
import ETS2LA.plugins.Map.GameData.nodes as Nodes
import ETS2LA.backend.settings as settings
from ETS2LA.variables import PATH
from typing import cast, List, Tuple, Union
import numpy as np
import time
import math
import cv2

roadsMaxX = 79370.13
roadsMaxZ = 93782.77
roadsMinX = -94621.8047
roadsMinZ = -80209.1641

tilesFolder = PATH + "ETS2LA/plugins/Map/Tiles"

MAX_IMAGE_SIZE = 1000
WIDTH = MAX_IMAGE_SIZE
HEIGHT = MAX_IMAGE_SIZE

path = []

if roadsMaxX != 0 and roadsMaxZ != 0 and roadsMinX != 0 and roadsMinZ != 0:
    aspectRatio = (roadsMaxX - roadsMinX) / (roadsMaxZ - roadsMinZ)
    WIDTH = MAX_IMAGE_SIZE
    HEIGHT = int(WIDTH / aspectRatio)
    
MOUSE_X = 0
MOUSE_Y = 0
FIRST_POSITION = None
FIRST_NODE = None
SECOND_POSITION = None
SECOND_NODE = None
holdingLeft = False
holdingRight = False
CHANGED = False
FIRST_START = True

TIME_OF_LAST_UPDATE = time.time()
POSITION_AT_LAST_UPDATE = (0, 0)
LAST_TARGET_COMPANY = None
LAST_TARGET_COMPANY_CITY = None
LAST_TARGET_COMPANY_NAME = None
class AStarNode:
    def __init__(self, x, z, lenght, node, item, startOrEnd):
        self.x = x
        self.z = z
        self.length = lenght
        self.node: Nodes.Node = node
        self.g = 0
        self.h = 0 
        self.f = 0
        self.parent = None
        self.neighbours = []
        self.item = item
        self.startOrEnd = startOrEnd
        
    def __eq__(self, other):
        return self.x == other.x and self.z == other.z
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __hash__(self):
        return hash((self.x, self.z))
    
    def HeuristicDistance(self, x, z):
        return np.sqrt((self.x - x)**2 + (self.z - z)**2)
    
    def __str__(self):
        return f"AStarNode: ({self.x}, {self.z})"
    
    def __repr__(self):
        return f"AStarNode: ({self.x}, {self.z})"
    
    def _ParseRoads(self, item:Road):
        node = self.node
        if item.EndNode.Uid != node.Uid:
            self.neighbours.append(AStarNode(item.EndNode.X, item.EndNode.Z, item.Lengths[0], item.EndNode, item, "end"))
        if item.StartNode.Uid != node.Uid:
            self.neighbours.append(AStarNode(item.StartNode.X, item.StartNode.Z, item.Lengths[0], item.StartNode, item, "start"))
    
    def _ParsePrefabItems(self, item:PrefabItem, lastNode:Nodes.Node, isRecursive=True):
        for node in item.Nodes:
            if node.Uid != self.node.Uid:
                distance = np.sqrt((node.X - self.node.X)**2 + (node.Z - self.node.Z)**2)
                index = item.Nodes.index(node)
                self.neighbours.append(AStarNode(node.X, node.Z, distance, node, item, index))
        
        if item.FerryUid != 0 and isRecursive:
            ports = ferries.FindEndPortByStartUid(item.FerryUid)
            if ports != None:
                for port in ports:
                    if port.Uid != item.FerryUid:
                        items = FindItemsWithFerryUid(port.Uid)
                        for item in items:
                            self._ParsePrefabItems(item, lastNode, isRecursive=False)
                        
            ports = ferries.FindStartPortByEndUid(item.FerryUid)
            if ports != None:
                for port in ports:
                    if port.Uid != item.FerryUid:
                        items = FindItemsWithFerryUid(port.Uid)
                        for item in items:
                            self._ParsePrefabItems(item, lastNode, isRecursive=False)
    
    def CreateNeighbours(self):
        node = self.node
        if node.ForwardItem:
            if type(node.ForwardItem) == int:
                item = GetPrefabItemByUid(node.ForwardItem)
                if item == None:
                    item = GetRoadByUid(node.ForwardItem)
            else:
                item = node.ForwardItem
                
            if item and type(item) == Road:
                self._ParseRoads(item)
            elif item and type(item) == PrefabItem:
                self._ParsePrefabItems(item, node)
                
        if node.BackwardItem:
            if type(node.BackwardItem) == int:
                item = GetPrefabItemByUid(node.BackwardItem)
                if item == None:
                    item = GetRoadByUid(node.BackwardItem)
            else:
                item = node.BackwardItem
                
            if item and type(item) == Road:
                self._ParseRoads(item)
            elif item and type(item) == PrefabItem:
                self._ParsePrefabItems(item, node)

def GenerateTileImage():
    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    
    # Calculate the size of each tile to fit perfectly
    tile_height = HEIGHT // 4
    tile_width = WIDTH // 4
    
    # OSM formatted tiles with 4 in each direction (4x4)
    for x in range(4):
        for y in range(4):
            tile = cv2.imread(f"{tilesFolder}/{x}/{y}.png")
            tile = cv2.resize(tile, (tile_width, tile_height))
            
            img[y*tile_height:y*tile_height+tile_height, x*tile_width:x*tile_width+tile_width] = tile
        
    return img

def AStar(startNode:AStarNode, endNode:AStarNode):
    startNode.CreateNeighbours()
    endNode.CreateNeighbours()
    
    openList = []
    closedList = set()
    
    openList.append(startNode)
    
    counter = 0
    total = 0
    while len(openList) > 0:
        currentNode = openList[0]
        currentIndex = 0
        for index, item in enumerate(openList):
            if item.f < currentNode.f:
                currentNode = item
                currentIndex = index
                
        openList.pop(currentIndex)
        closedList.add(currentNode)
        
        if currentNode == endNode:
            path = []
            current = currentNode
            while current is not None:
                path.append(current)
                current = current.parent
            return path[::-1]
        
        for neighbour in currentNode.neighbours:
            neighbour.CreateNeighbours()
            if neighbour in closedList:
                continue
            
            neighbour.g = currentNode.g + neighbour.length
            neighbour.h = neighbour.HeuristicDistance(endNode.x, endNode.z)
            neighbour.f = neighbour.g + neighbour.h
            
            if neighbour in openList:
                continue
            
            neighbour.parent = currentNode
            openList.append(neighbour)
        
        # Find the node in openList with the lowest f value
        bestCurrentNode = min(openList, key=lambda n: n.f, default=None)
        if bestCurrentNode:
            # Construct the path to this node
            bestPath = []
            current = bestCurrentNode
            while current is not None:
                bestPath.append(current)
                current = current.parent
            bestPath = bestPath[::-1]
        else:
            bestPath = []
        
        if counter % 500 == 0:
            DrawMap((startNode.x, startNode.z), (endNode.x, endNode.z), [(node.x, node.z) for node in openList], bestPath, total=total)
            counter = 0
        
        counter += 1    
        total += 1
            
    return []


def ConvertScreenToWorld(x, y):
    # Convert the x and y to world coordinates
    worldX = (x / WIDTH) * (roadsMaxX - roadsMinX) + roadsMinX
    worldZ = (y / HEIGHT) * (roadsMaxZ - roadsMinZ) + roadsMinZ
    
    return worldX, worldZ

def ConvertWorldToScreen(x, z):
    # Convert the world coordinates to x and y
    screenX = ((x - roadsMinX) / (roadsMaxX - roadsMinX)) * WIDTH
    screenY = ((z - roadsMinZ) / (roadsMaxZ - roadsMinZ)) * HEIGHT
    
    return screenX, screenY

def MeterDistanceToString(distance: float) -> str:
    if distance < 1000:
        return f"{distance:.2f} m"
    
    if distance > 1000:
        return f"{distance/1000:.2f} km"

def ClosestNode(x, z):
    closestRoad = None
    closestDistance = 0
    for road in roads.roads:
        distance = road.HeuristicDistance(x, z)
        if closestRoad == None or distance < closestDistance:
            closestRoad = road
            closestDistance = distance
            
    closestRoad = cast(Road, closestRoad)
    
    closestNode = None
    closestDistance = 0
    startDistance = closestRoad.StartNode.HeuristicDistance(x, z)
    endDistance = closestRoad.EndNode.HeuristicDistance(x, z)
    
    if startDistance < endDistance:
        closestNode = closestRoad.StartNode
        neighbours = [closestRoad.EndNode]
        closestDistance = startDistance
    else:
        closestNode = closestRoad.EndNode
        neighbours = [closestRoad.StartNode]
        closestDistance = endDistance
            
    return closestNode, closestRoad.Lengths[0]
def MouseCallback(event, x, y, flags, param):
    global MOUSE_X, MOUSE_Y, FIRST_POSITION, SECOND_POSITION, holdingLeft, holdingRight, CHANGED
    if event == cv2.EVENT_MOUSEMOVE:
        MOUSE_X, MOUSE_Y = x, y
        
    if event == cv2.EVENT_LBUTTONDOWN or holdingLeft:
        MOUSE_X, MOUSE_Y = x, y
        FIRST_POSITION = ConvertScreenToWorld(x, y)
        holdingLeft = True
        CHANGED = True
    if event == cv2.EVENT_RBUTTONDOWN or holdingRight:
        MOUSE_X, MOUSE_Y = x, y
        SECOND_POSITION = ConvertScreenToWorld(x, y)
        holdingRight = True
        CHANGED = True
    
    if event == cv2.EVENT_LBUTTONUP:
        holdingLeft = False
        CHANGED = False
        
    if event == cv2.EVENT_RBUTTONUP:
        holdingRight = False
        CHANGED = False
        
def DrawMap(StartPoint, EndPoint, PathPoints, best, total=0):
    global WIDTH, HEIGHT, lastFrame
    img = GenerateTileImage()
    
    best = [(node.x, node.z) for node in best]
    
    if StartPoint != None:
        x, y = ConvertWorldToScreen(StartPoint[0], StartPoint[1])
        cv2.circle(img, (int(x), int(y)), 5, (0, 100, 0), -1, cv2.LINE_AA)
        
    if EndPoint != None:
        x, y = ConvertWorldToScreen(EndPoint[0], EndPoint[1])
        cv2.circle(img, (int(x), int(y)), 5, (0, 0, 100), -1, cv2.LINE_AA)
        
    if PathPoints != None:
        screenPoints = []
        length = 0
        lastPosition = None
        for point in PathPoints:
            screenPoints.append(ConvertWorldToScreen(point[0], point[1]))
            if lastPosition:
                length += np.sqrt((point[0] - lastPosition[0])**2 + (point[1] - lastPosition[1])**2)
            lastPosition = point
            
        #cv2.polylines(img, [np.array(screenPoints, np.int32)], False, (255, 255, 255), 2, cv2.LINE_AA)
        
        for point in screenPoints:
            cv2.circle(img, (int(point[0]), int(point[1])), 2, (100, 100, 0), -1, cv2.LINE_AA)
            
    if best != None:
        screenPoints = []
        length = 0
        lastPosition = None
        for point in best:
            screenPoints.append(ConvertWorldToScreen(point[0], point[1]))
            if lastPosition:
                length += np.sqrt((point[0] - lastPosition[0])**2 + (point[1] - lastPosition[1])**2)
            lastPosition = point
            
        cv2.polylines(img, [np.array(screenPoints, np.int32)], False, (100, 100, 200), 1, cv2.LINE_AA)
        
        cv2.putText(img, MeterDistanceToString(length), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, f"Nodes: {len(best)}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        if total != 0:
            cv2.putText(img, f"Calculations: {total}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
    lastFrame = img
    cv2.imshow('image', lastFrame)
    cv2.waitKey(1)

lastFrame = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
cv2.putText(lastFrame, "This will automatically load once you get a job in game.", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
cv2.putText(lastFrame, "Left click to set the start point, right click to set the end point.", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
def Update(data, closestData):
    global roadsMaxX, roadsMaxZ, roadsMinX, roadsMinZ, FIRST_POSITION, SECOND_POSITION, FIRST_NODE, SECOND_NODE, WIDTH, HEIGHT, lastFrame, FIRST_START, LAST_TARGET_COMPANY, LAST_TARGET_COMPANY_CITY, LAST_TARGET_COMPANY_NAME, CHANGED, path, TIME_OF_LAST_UPDATE, POSITION_AT_LAST_UPDATE
    
    if FIRST_START == True:
        cv2.namedWindow('image')
        cv2.setWindowProperty('image', cv2.WND_PROP_TOPMOST, 1)
        cv2.setMouseCallback('image', MouseCallback)
        FIRST_START = False
    
    target_city = data["api"]["configString"]["cityDst"]
    target_company = data["api"]["configString"]["compDstId"].lower().replace(" ", "_")
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]
    
    if target_city != LAST_TARGET_COMPANY_CITY \
        or target_company != LAST_TARGET_COMPANY_NAME \
        or (time.time() - TIME_OF_LAST_UPDATE < 20\
            and math.sqrt((truckX - POSITION_AT_LAST_UPDATE[0])**2 + (truckZ - POSITION_AT_LAST_UPDATE[1])**2) > 1000
        ): # 20 update again after load time.

        #print(target_city)
        #print(target_company)
        target_company = GetCompanyInCity(target_company, target_city)
        if target_company != None and len(target_company) > 0:
            target_company = target_company[0]
            LAST_TARGET_COMPANY = target_company
            LAST_TARGET_COMPANY_CITY = target_city
            LAST_TARGET_COMPANY_NAME = target_company.name
            SECOND_POSITION = (target_company.x, target_company.y)
            FIRST_POSITION = (truckX, truckZ)
            CHANGED = True
            TIME_OF_LAST_UPDATE = time.time()
            POSITION_AT_LAST_UPDATE = (truckX, truckZ)
        
    
    if CHANGED:
        # roadsMaxX = roads.roadsMaxX
        # roadsMaxZ = roads.roadsMaxZ
        # roadsMinX = roads.roadsMinX
        # roadsMinZ = roads.roadsMinZ
        
        # Get the game map aspect ratio
        aspectRatio = (roadsMaxX - roadsMinX) / (roadsMaxZ - roadsMinZ)
        
        # Create an image with a max size of 1000x1000
        WIDTH = MAX_IMAGE_SIZE
        HEIGHT = int(WIDTH / aspectRatio)
        img = GenerateTileImage()
        
        # Draw the first and second points
        if FIRST_POSITION != None:
            FIRST_NODE, length = ClosestNode(FIRST_POSITION[0], FIRST_POSITION[1])
            FIRST_NODE = AStarNode(FIRST_NODE.X, FIRST_NODE.Z, length, FIRST_NODE, None, "start")
            
            x, y = ConvertWorldToScreen(FIRST_POSITION[0], FIRST_POSITION[1])
            cv2.circle(img, (int(x), int(y)), 5, (0, 100, 0), -1, cv2.LINE_AA)
            
        if SECOND_POSITION != None:
            SECOND_NODE, length = ClosestNode(SECOND_POSITION[0], SECOND_POSITION[1])
            SECOND_NODE = AStarNode(SECOND_NODE.X, SECOND_NODE.Z, length, SECOND_NODE, None, "end")
            
            x, y = ConvertWorldToScreen(SECOND_POSITION[0], SECOND_POSITION[1])
            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 100), -1, cv2.LINE_AA)
    
        if FIRST_NODE:
            x, y = ConvertWorldToScreen(FIRST_NODE.x, FIRST_NODE.z)
            cv2.circle(img, (int(x), int(y)), 5, (0, 255, 0), -1, cv2.LINE_AA)
            cv2.putText(img, f"({FIRST_NODE.x:.2f}, {FIRST_NODE.z:.2f})", (int(x)+10, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
        if SECOND_NODE:
            x, y = ConvertWorldToScreen(SECOND_NODE.x, SECOND_NODE.z)
            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.putText(img, f"({SECOND_NODE.x:.2f}, {SECOND_NODE.z:.2f})", (int(x)+10, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            
        if FIRST_NODE and SECOND_NODE:
            print("Calculating path")
            startTime = time.time()
            path = AStar(FIRST_NODE, SECOND_NODE)
            coordinatePath = [(node.x, node.z) for node in path]
            screenPoints = []
            length = 0
            lastPosition = None
            for point in coordinatePath:
                if lastPosition:
                    length += np.sqrt((point[0] - lastPosition[0])**2 + (point[1] - lastPosition[1])**2)
                lastPosition = point
                screenPoints.append(ConvertWorldToScreen(point[0], point[1]))
            
            endTime = time.time()    
            print(f"Path calculated in {endTime - startTime:.2f} seconds")
            cv2.polylines(img, [np.array(screenPoints, np.int32)], False, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(img, f"{MeterDistanceToString(length)} ({MeterDistanceToString(length*19)} in game)", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(img, f"Nodes: {len(path)}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(img, f"Time: {(endTime - startTime)*1000:.2f}ms", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
        lastFrame = img
        
        CHANGED = False
        
    # Display said image
    cv2.imshow('image', lastFrame)
    cv2.waitKey(1)
    
    return path