import utils.data_extractor as data_extractor
import ETS2LA.backend.settings as settings
import ETS2LA.plugins.MapNew.classes as c
import logging
import random
import time
import os

DATA_PATH = "ETS2LA/plugins/MapNew/data/"

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

def ReadCompanyItems() -> list[c.CompanyItem]:
    path = FindCategoryFilePath("companies")
    if path is None: return []
    companies: list[c.CompanyItem] = []
    for company in data_extractor.ReadData(path):
        companies.append(c.CompanyItem(
            company["uid"],
            company["x"],
            company["y"],
            company["z"],
            company["sectorX"],
            company["sectorY"],
            company["token"],
            company["cityToken"],
            TryReadExcept(company, "prefabUid", None),
            TryReadExcept(company, "nodeUid", None),
        ))
        
    return companies

def ReadCompanies() -> list[c.Company]:
    path = FindCategoryFilePath("companyDefs")
    if path is None: return []
    companies: list[c.Company] = []
    for company in data_extractor.ReadData(path):
        companies.append(c.Company(
            company["token"],
            company["name"],
            company["cityTokens"],
            company["cargoInTokens"],
            company["cargoOutTokens"]
        ))
        
    return companies

def ReadModels() -> list[c.Model]:
    path = FindCategoryFilePath("models")
    if path is None: return []
    models: list[c.Model] = []
    for model in data_extractor.ReadData(path):
        models.append(c.Model(
            model["uid"],
            model["x"],
            model["y"],
            model["z"],
            model["sectorX"],
            model["sectorY"],
            model["token"],
            model["nodeUid"],
            model["scale"]
        ))
    
    return models       

def ReadModelDescriptions() -> list[c.ModelDescription]:
    path = FindCategoryFilePath("modelDescriptions")
    if path is None: return []
    model_descriptions: list[c.ModelDescription] = []
    for model_description in data_extractor.ReadData(path):
        model_descriptions.append(c.ModelDescription(
            model_description["token"],
            c.Position(
                model_description["center"]["x"],
                model_description["center"]["y"],
                model_description["center"]["z"],
            ),
            c.Position(
                model_description["start"]["x"],
                model_description["start"]["y"],
                model_description["start"]["z"],
            ),
            c.Position(
                model_description["end"]["x"],
                model_description["end"]["y"],
                model_description["end"]["z"],
            ),
            model_description["height"],
        ))
        
    return model_descriptions

def ReadMapAreas() -> list[c.MapArea]:
    path = FindCategoryFilePath("mapAreas")
    if path is None: return []
    map_areas: list[c.MapArea] = []
    for map_area in data_extractor.ReadData(path):
        map_areas.append(c.MapArea(
            map_area["uid"],
            map_area["type"],
            map_area["x"],
            map_area["y"],
            map_area["z"],
            map_area["sectorX"],
            map_area["sectorY"],
        ))
        
    return map_areas

def ReadPOIs() -> list[c.POI]:
    path = FindCategoryFilePath("pois")
    if path is None: return []
    pois: list[c.POI] = []
    for poi in data_extractor.ReadData(path):
        if "label" in poi:
            if poi["type"] == c.NonFacilityPOI.LANDMARK:
                pois.append(c.LandmarkPOI(
                    TryReadExcept(poi, "uid", None),
                    poi["x"],
                    poi["y"],
                    TryReadExcept(poi, "z", 0),
                    poi["sectorX"],
                    poi["sectorY"],
                    poi["icon"],
                    poi["label"],
                    poi["dlcGuard"],
                    poi["nodeUid"],
                ))
            else:
                pois.append(c.GeneralPOI(
                    TryReadExcept(poi, "uid", None),
                    poi["x"],
                    poi["y"],
                    TryReadExcept(poi, "z", 0), # don't have z, but will have in the future
                    poi["sectorX"],
                    poi["sectorY"],
                    poi["icon"],
                    poi["label"]
                ))
        else:
            if poi["type"] == "road":
                pois.append(c.RoadPOI(
                    TryReadExcept(poi, "uid", None),
                    poi["x"],
                    poi["y"],
                    TryReadExcept(poi, "z", 0), # roads don't have z, but will have in the future
                    poi["sectorX"],
                    poi["sectorY"],
                    poi["icon"],
                    poi["dlcGuard"],
                    TryReadExcept(poi, "nodeUid", None),
                ))
            elif poi["icon"] == c.FacilityIcon.PARKING:
                pois.append(c.ParkingPOI(
                    TryReadExcept(poi, "uid", None),
                    poi["x"],
                    poi["y"],
                    TryReadExcept(poi, "z", 0),
                    poi["sectorX"],
                    poi["sectorY"],
                    poi["icon"],
                    poi["dlcGuard"],
                    poi["fromItemType"],
                    poi["itemNodeUids"],
                ))
            elif "uid" in poi:
                pois.append(c.FacilityPOI(
                    TryReadExcept(poi, "uid", None),
                    poi["x"],
                    poi["y"],
                    TryReadExcept(poi, "z", 0),
                    poi["sectorX"],
                    poi["sectorY"],
                    poi["icon"],
                    poi["prefabUid"],
                    poi["prefabPath"],
                ))
            else:
                ... # NOT IMPLEMENTED
                    
    return pois

def ReadCountries() -> list[c.Country]:
    path = FindCategoryFilePath("countries")
    if path is None: return []
    countries: list[c.Country] = []
    for country in data_extractor.ReadData(path):
        countries.append(c.Country(
            country["token"],
            country["name"],
            None, # name_localized
            country["id"],
            country["x"],
            country["y"],
            country["z"],
            country["code"],
        ))
        
    return countries

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
    
    data = c.MapData()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Nodes")
    data.nodes = ReadNodes()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Elevations")
    data.elevations = ReadElevations()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Roads")
    data.roads = ReadRoads()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> RoadLooks")
    data.road_looks = ReadRoadLooks()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Ferries")
    data.ferries = ReadFerries()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Prefabs")
    data.prefabs = ReadPrefabs()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Prefab Descriptions")
    data.prefab_descriptions = ReadPrefabDescriptions()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Company Defintions")
    data.companies = ReadCompanyItems()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Companies")
    data.company_defs = ReadCompanies()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Models")
    data.models = ReadModels()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Model Descriptions")
    data.model_descriptions = ReadModelDescriptions()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Map Areas")
    data.map_areas = ReadMapAreas()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> POIs")
    data.POIs = ReadPOIs()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Countries")
    data.countries = ReadCountries()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Cities")
    data.cities = ReadCities()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Linking objects (roads)")
    data.match_prefabs_to_descriptions()
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Linking objects (prefabs)")
    data.match_roads_to_looks()
    
    logging.warning(f"[dim]{(time.time() - start_time)*100:.0f}ms[/dim] -> Optimizing data")
    data.sort_to_sectors()
    data.build_node_dictionary()
    
    logging.warning(f"Data read in {time.time() - start_time:.2f} seconds.")
    logging.warning(f"Total counts: ")
    logging.warning(f"{len(data.nodes)} nodes (with {len(data._nodes_by_uid)} UIDs in the dictionary root)")
    logging.warning(f"{len(data.elevations)} elevations")
    logging.warning(f"{len(data.roads)} roads")
    logging.warning(f"{len(data.road_looks)} road looks")
    logging.warning(f"{len(data.prefabs)} prefabs")
    logging.warning(f"{len(data.prefab_descriptions)} prefab descriptions")
    logging.warning(f"{len(data.ferries)} ferries")
    logging.warning(f"{len(data.companies)} company items")
    logging.warning(f"{len(data.company_defs)} company definitions")
    logging.warning(f"{len(data.models)} models")
    logging.warning(f"{len(data.model_descriptions)} model descriptions")
    logging.warning(f"{len(data.map_areas)} map areas")
    logging.warning(f"{len(data.POIs)} POIs")
    logging.warning(f"{len(data.countries)} countries")
    logging.warning(f"{len(data.cities)} cities")
    
    return data