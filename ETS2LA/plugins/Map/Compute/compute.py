import GameData.roads as roads
import GameData.prefabItems as prefabItems
import sys

LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME = 10

lastCoords = None
closeRoads = []
closePrefabs = []
def GetRoads(data):
    global lastCoords, closeRoads
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]

    tileCoords = roads.GetTileCoordinates(x, y)
    
    if tileCoords != lastCoords or lastCoords == None or closeRoads == []:
        lastCoords = tileCoords
    else:
        return closeRoads
    
    # Get the roads in the current area
    areaRoads = []
    areaRoads = roads.GetRoadsInTileByCoordinates(x, y)
    
    # Also get the roads in the surrounding tiles
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y)
    areaRoads += roads.GetRoadsInTileByCoordinates(x, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x, y - 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x + 1000, y - 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y + 1000)
    areaRoads += roads.GetRoadsInTileByCoordinates(x - 1000, y - 1000)
    
    closeRoads = areaRoads
    print(f"Found {len(closeRoads)} roads")
    
    return closeRoads

def GetPrefabs(data):
    global lastCoords, closePrefabs
    # Get the current X and Y position of the truck
    x = data["api"]["truckPlacement"]["coordinateX"]
    y = data["api"]["truckPlacement"]["coordinateZ"]
    
    tileCoords = roads.GetTileCoordinates(x, y)
    
    if tileCoords != lastCoords or lastCoords == None or closePrefabs == []:
        lastCoords = tileCoords
    else:
        return closePrefabs
    
    # Get the roads in the current area
    areaItems = []
    areaItems += prefabItems.GetItemsInTileByCoordinates(x, y)
    
    # Also get the roads in the surrounding tiles
    areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x, y + 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x, y - 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y + 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x + 1000, y - 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y + 1000)
    areaItems += prefabItems.GetItemsInTileByCoordinates(x - 1000, y - 1000)
    
    closePrefabs = areaItems
    
    print(f"Found {len(closePrefabs)} prefabs")
    
    return closePrefabs

def CalculateParallelPointsForRoads(areaRoads):
    calcCount = 0
    for road in areaRoads:
        if road.Points == None:
            points = roads.CreatePointsForRoad(road)
            roads.SetRoadPoints(road, points)
            
        
        # Check for parallel points
        if road.ParallelPoints == []:
            if calcCount > LIMIT_OF_PARALLEL_LANE_CALCS_PER_FRAME:
                continue
            
            boundingBox, parallelPoints, laneWidth = roads.CalculateParallelCurves(road)
            if parallelPoints == [] or parallelPoints == None:
                parallelPoints = [[(0, 0), (0, 0)], [(0, 0), (0, 0)]]
            road.ParallelPoints = parallelPoints
            road.LaneWidth = laneWidth
            road.BoundingBox = boundingBox
            roads.SetRoadParallelData(road, parallelPoints, laneWidth, boundingBox)
            calcCount += 1
    