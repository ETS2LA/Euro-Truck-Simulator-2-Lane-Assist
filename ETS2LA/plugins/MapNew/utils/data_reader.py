import utils.data_extractor as data_extractor
import ETS2LA.backend.settings as settings
import ETS2LA.plugins.MapNew.classes as c
import logging
import time
import os

DATA_PATH = "ETS2LA/plugins/MapNew/data/data/"

data_extractor.UpdateData(DATA_PATH)

def FindCategoryFilePath(category: str) -> str:
    for file in os.listdir(DATA_PATH):
        if file.endswith(f"{category}.json"):
            return DATA_PATH + file
    return None

def TryReadExcept(data: dict, key: str, default: any) -> any:
    try:
        return data[key]
    except KeyError:
        return default

def ReadNodes() -> list[c.Node]:
    path = FindCategoryFilePath("nodes")
    if path is None: return []
    nodes: list[c.Node] = []
    for node in data_extractor.ReadData(path):
        nodes.append(c.Node(
            node["uid"],
            node["x"],
            node["y"],
            node["z"],
            node["rotation"],
            node["forwardItemUid"],
            node["backwardItemUid"],
            node["sectorX"],
            node["sectorY"],
            node["forwardCountryId"],
            node["backwardCountryId"],
        ))
        
    return nodes

def ReadElevations() -> list[tuple[float, float, float]]:
    path = FindCategoryFilePath("elevation")
    if path is None: return []
    elevations: list[tuple[float, float, float]] = []
    for elevation in data_extractor.ReadData(path):
        elevations.append((
            elevation[0],
            elevation[1],
            elevation[2],
        ))
        
    return elevations

def ReadRoads() -> list[c.Road]:
    path = FindCategoryFilePath("roads")
    if path is None: return []
    roads: list[c.Road] = []
    for road in data_extractor.ReadData(path):
        roads.append(c.Road(
            road["uid"],
            road["x"],
            road["y"],
            road["z"],
            road["sectorX"],
            road["sectorY"],
            road["dlcGuard"],
            False, # hidden
            road["roadLookToken"],
            road["startNodeUid"],
            road["endNodeUid"],
            road["length"],
            False, # maybe divided
        ))
        
    return roads

def ReadRoadLooks() -> list[c.RoadLook]:
    path = FindCategoryFilePath("roadLooks")
    if path is None: return []
    road_looks: list[c.RoadLook] = []
    for road_look in data_extractor.ReadData(path):
        road_looks.append(c.RoadLook(
            road_look["token"],
            TryReadExcept(road_look, "lanesLeft", []),
            TryReadExcept(road_look, "lanesRight", []),
            TryReadExcept(road_look, "offset", 0),
            0, # lane_offset not in the files rn
            TryReadExcept(road_look, "shoulderSpaceRight", 0),
            TryReadExcept(road_look, "shoulderSpaceLeft", 0),
        ))
    
    return road_looks

def ReadPrefabs() -> list[c.Prefab]:
    path = FindCategoryFilePath("prefabs")
    if path is None: return []
    prefabs: list[c.Prefab] = []
    for prefab in data_extractor.ReadData(path):
        prefabs.append(c.Prefab(
            prefab["uid"],
            prefab["x"],
            prefab["y"],
            prefab["z"],
            prefab["sectorX"],
            prefab["sectorY"],
            prefab["dlcGuard"],
            False, # hidden
            prefab["token"],
            [uid for uid in prefab["nodeUids"]],
            prefab["originNodeIndex"]
        ))
        
    return prefabs

def ReadPrefabDescriptions() -> list[c.PrefabDescription]:
    path = FindCategoryFilePath("prefabDescriptions")
    if path is None: return []
    prefab_descriptions: list[c.PrefabDescription] = []
    for prefab_description in data_extractor.ReadData(path):
        # TODO: Read signs!
        prefab_descriptions.append(c.PrefabDescription(
            prefab_description["token"],
            [c.PrefabNode(
                node["x"],
                node["y"],
                node["z"],
                node["rotation"],
                TryReadExcept(node, "input_lanes", []),
                TryReadExcept(node, "output_lanes", []),
            ) for node in prefab_description["nodes"]],
            [c.RoadMapPoint(
                point["x"],
                point["y"],
                point["z"],
                point["neighbors"],
                point["lanesLeft"],
                point["lanesRight"],
                point["offset"],
                c.NavNode(
                    point["navNode"]["node0"],
                    point["navNode"]["node1"],
                    point["navNode"]["node2"],
                    point["navNode"]["node3"],
                    point["navNode"]["node4"],
                    point["navNode"]["node5"],
                    point["navNode"]["node6"],
                    point["navNode"]["nodeCustom"]
                ),
                c.NavFlags(
                    point["navFlags"]["isStart"],
                    point["navFlags"]["isExit"],
                    point["navFlags"]["isBase"],
                )
            ) if point["type"] == "road" else c.PolygonMapPoint(
                point["x"],
                point["y"],
                point["z"],
                point["neighbors"],
                point["color"],
                point["roadOver"]
            ) if point["type"] == "polygon" else None for point in prefab_description["mapPoints"]],
            [c.PrefabSpawnPoints(
                spawn_point["x"],
                spawn_point["y"],
                spawn_point["z"],
                spawn_point["type"],
            ) for spawn_point in prefab_description["spawnPoints"]],
            [c.PrefabTriggerPoint(
                trigger_point["x"],
                trigger_point["y"],
                trigger_point["z"],
                trigger_point["action"],
            ) for trigger_point in prefab_description["triggerPoints"]],
            [c.PrefabNavCurve(
                curve["navNodeIndex"],
                c.Transform(
                    curve["start"]["x"],
                    curve["start"]["y"],
                    curve["start"]["z"],
                    curve["start"]["rotation"],
                ),
                c.Transform(
                    curve["end"]["x"],
                    curve["end"]["y"],
                    curve["end"]["z"],
                    curve["end"]["rotation"],
                ),
                curve["nextLines"],
                curve["prevLines"],
            ) for curve in prefab_description["navCurves"]],
            [c.PrefabNavNode(
                node["type"],
                node["endIndex"],
                [c.NavNodeConnection(
                    connection["targetNavNodeIndex"],
                    connection["curveIndices"],
                ) for connection in node["connections"]],
            ) for node in prefab_description["navNodes"]],
        ))
    
    return prefab_descriptions

def ReadFerries() -> list[c.Ferry]:
    path = FindCategoryFilePath("ferries")
    if path is None: return []
    ferries: list[c.Ferry] = []
    for ferry in data_extractor.ReadData(path):
        ferries.append(c.Ferry(
            ferry["token"],
            ferry["train"],
            ferry["name"],
            None, # name_localized
            ferry["x"],
            ferry["y"],
            ferry["z"],
            [c.FerryConnection(
                connection["token"],
                connection["name"],
                None, # name_localized
                connection["x"],
                connection["y"],
                connection["z"],
                connection["price"],
                connection["time"],
                connection["distance"],
                intermediate_points=[c.Transform(
                    point["x"],
                    point["y"],
                    point["z"],
                    point["rotation"],
                ) for point in connection["intermediatePoints"]],
            ) for connection in ferry["connections"]],
        ))
        
    return ferries

def ReadCities() -> list[c.City]:
    path = FindCategoryFilePath("cities")
    if path is None: return []
    cities: list[c.City] = []
    for city in data_extractor.ReadData(path):
        cities.append(c.City(
            city["token"],
            city["name"],
            None, # name_localized
            city["countryToken"],
            city["population"],
            city["x"],
            city["y"],
            city["z"],
            [c.CityArea(
                area["uid"],
                area["x"],
                area["y"],
                area["z"],
                area["sectorX"],
                area["sectorY"],
                area["token"],
                area["hidden"],
                area["width"],
                area["height"],
            ) for area in city["areas"]]
        ))
        
    return cities


# MARK : ReadData()
def ReadData() -> c.MapData:
    start_time = time.time()
    logging.warning("Reading data...")
    
    data = c.MapData(); logging.warning("-> Nodes")
    data.nodes = ReadNodes(); logging.warning("-> Elevations")
    data.elevations = ReadElevations(); logging.warning("-> Roads")
    data.roads = ReadRoads(); logging.warning("-> RoadLooks")
    data.road_looks = ReadRoadLooks(); logging.warning("-> Ferries")
    data.ferries = ReadFerries(); logging.warning("-> Prefabs")
    data.prefabs = ReadPrefabs(); logging.warning("-> PrefabDescriptions")
    data.prefab_descriptions = ReadPrefabDescriptions(); logging.warning("-> Cities")
    data.cities = ReadCities()
    
    logging.warning(f"Data read in {time.time() - start_time:.2f} seconds.")