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
    data.ferries = ReadFerries(); logging.warning("-> Cities")
    data.cities = ReadCities(); logging.warning("Done!")
    
    logging.warning(f"Data read in {time.time() - start_time:.2f} seconds.")