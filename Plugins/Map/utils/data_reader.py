"""Data reader utilities for map plugin."""
from Plugins.Map.utils import data_handler
from Plugins.Map import classes as c
import Plugins.Map.data as data
from rich import print
import psutil
import time
import os

path = "Plugins/Map/data"

def FindCategoryFilePath(category: str) -> str:
    for file in os.listdir(path):
        if category in file and file.endswith(".json"):
            return os.path.join(path, file)
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
    file = data_handler.ReadData(path)
    for node in file:
        nodes.append(c.Node(
            node["uid"],
            node["x"],
            node["y"],
            node["z"],
            node["rotation"],
            node["rotationQuat"],
            node["forwardItemUid"],
            node["backwardItemUid"],
            0,
            0,
            node["forwardCountryId"],
            node["backwardCountryId"],
        ))

    return nodes

def ReadNodeGraph() -> list[c.NavigationEntry]: # None since this will just update the existing nodes
    path = FindCategoryFilePath("graph")
    if path is None: return []
    graph: list[c.NavigationEntry] = []
    file = data_handler.ReadData(path)
    for entry in file:
        graph.append(c.NavigationEntry(
            entry[0],
            [c.NavigationNode(
                node["nodeUid"] if "nodeUid" in node else node["nodeId"],
                node["distance"],
                node["direction"],
                bool(TryReadExcept(node, "isOneLaneRoad", False)),
                node["dlcGuard"],
            ) for node in entry[1]["forward"]],
            [c.NavigationNode(
                node["nodeUid"] if "nodeUid" in node else node["nodeId"],
                node["distance"],
                node["direction"],
                bool(TryReadExcept(node, "isOneLaneRoad", False)),
                node["dlcGuard"],
            ) for node in entry[1]["backward"]],
        ))
    
    return graph

def ReadElevations() -> list[tuple[float, float, float]]:
    path = FindCategoryFilePath("elevation")
    if path is None: return []
    elevations: list[tuple[float, float, float]] = []
    file = data_handler.ReadData(path)
    for elevation in file:
        elevations.append(
            c.Elevation(
                elevation[0],
                elevation[2],
                elevation[1]
            )
        )

    return elevations

def ReadRoads() -> list[c.Road]:
    path = FindCategoryFilePath("roads")
    if path is None: return []
    roads: list[c.Road] = []
    file = data_handler.ReadData(path)
    for road in file:
        roads.append(c.Road(
            road["uid"],
            road["x"],
            road["y"],
            0,
            0,
            int(TryReadExcept(road, "dlcGuard", -1)),
            bool(TryReadExcept(road, "hidden", False)),
            road["roadLookToken"],
            road["startNodeUid"],
            road["endNodeUid"],
            road["length"],
            TryReadExcept(road, "maybeDivided", False),
            [
                c.Railing(
                    railing["rightRailing"],
                    railing["rightRailingOffset"],
                    railing["leftRailing"],
                    railing["leftRailingOffset"]
                ) for railing in TryReadExcept(road, "railings", [])
            ]
        ))

    return roads

def ReadRoadLooks() -> list[c.RoadLook]:
    path = FindCategoryFilePath("roadLooks")
    if path is None: return []
    road_looks: list[c.RoadLook] = []
    file = data_handler.ReadData(path)
    for road_look in file:
        road_looks.append(c.RoadLook(
            road_look["token"],
            road_look["name"],
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
    file = data_handler.ReadData(path)
    for prefab in file:
        prefabs.append(c.Prefab(
            prefab["uid"],
            prefab["x"],
            prefab["y"],
            TryReadExcept(prefab, "z", 0),
            0,
            0,
            prefab["dlcGuard"],
            TryReadExcept(prefab, "hidden", False),
            prefab["token"],
            [uid for uid in prefab["nodeUids"]],
            prefab["originNodeIndex"],
        ))

    return prefabs

import concurrent.futures

def ReadPrefabDescriptions() -> list[c.PrefabDescription]:
    path = FindCategoryFilePath("prefabDescriptions")
    if path is None:
        return []

    prefab_data_list = data_handler.ReadData(path)

    def process_prefab_description(prefab_description):
        # TODO: Read signs!
        return c.PrefabDescription(
            prefab_description["token"],
            # nodes
            [
                c.PrefabNode(
                    node["x"],
                    node["y"],
                    node["z"],
                    node["rotation"],
                    TryReadExcept(node, "inputLanes", []),
                    TryReadExcept(node, "outputLanes", []),
                )
                for node in prefab_description["nodes"]
            ],
            # map points
            [
                c.RoadMapPoint(
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
                        point["navNode"]["nodeCustom"],
                    ),
                    c.NavFlags(
                        point["navFlags"]["isStart"],
                        point["navFlags"]["isExit"],
                        point["navFlags"]["isBase"],
                    ),
                )
                if point["type"] == "road"
                else c.PolygonMapPoint(
                    point["x"],
                    point["y"],
                    point["z"],
                    point["neighbors"],
                    point["color"],
                    point["roadOver"],
                )
                if point["type"] == "polygon"
                else None
                for point in prefab_description["mapPoints"]
            ],
            # spawn points
            [
                c.PrefabSpawnPoints(
                    spawn_point["x"],
                    spawn_point["y"],
                    TryReadExcept(spawn_point, "z", 0),
                    spawn_point["type"],
                )
                for spawn_point in prefab_description["spawnPoints"]
            ],
            # trigger points
            [
                c.PrefabTriggerPoint(
                    trigger_point["x"],
                    trigger_point["y"],
                    TryReadExcept(trigger_point, "z", 0),
                    trigger_point["action"],
                )
                for trigger_point in prefab_description["triggerPoints"]
            ],
            # nav curves
            [
                c.PrefabNavCurve(
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
                    TryReadExcept(curve, "semaphoreId", -1)
                )
                for curve in prefab_description["navCurves"]
            ],
            # nav nodes
            [
                c.PrefabNavNode(
                    node["type"],
                    node["endIndex"],
                    [
                        c.NavNodeConnection(
                            connection["targetNavNodeIndex"],
                            connection["curveIndices"],
                        )
                        for connection in node["connections"]
                    ],
                )
                for node in prefab_description["navNodes"]
            ],
            [
                c.Semaphore(
                    semaphore["x"],
                    semaphore["y"],
                    semaphore["z"],
                    semaphore["rotation"],
                    semaphore["type"],
                    semaphore["id"],
                )
                for semaphore in TryReadExcept(prefab_description, "semaphores", [])
            ]
        )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        prefab_descriptions = list(
            executor.map(process_prefab_description, prefab_data_list)
        )

    return prefab_descriptions

def ReadTriggers() -> list[c.Trigger]:
    path = FindCategoryFilePath("triggers")
    if path is None: return []
    triggers: list[c.Trigger] = []
    file = data_handler.ReadData(path)
    for trigger in file:
        triggers.append(c.Trigger(
            trigger["uid"],
            trigger["x"],
            trigger["y"],
            TryReadExcept(trigger, "z", 0),
            0,
            0,
            trigger["actions"],
            trigger["nodeUids"],
        ))
        
    return triggers

def ReadFerries() -> list[c.Ferry]:
    path = FindCategoryFilePath("ferries")
    if path is None: return []
    ferries: list[c.Ferry] = []
    file = data_handler.ReadData(path)
    for ferry in file:
        ferries.append(c.Ferry(
            ferry["token"],
            ferry["train"],
            ferry["name"],
            None, # name_localized
            ferry["x"],
            ferry["y"],
            TryReadExcept(ferry, "z", 0),
            [c.FerryConnection(
                connection["token"],
                connection["name"],
                None, # name_localized
                connection["x"],
                connection["y"],
                TryReadExcept(connection, "z", 0),
                connection["price"],
                connection["time"],
                connection["distance"],
                intermediate_points=[c.Transform(
                    point["x"],
                    point["y"],
                    TryReadExcept(point, "z", 0),
                    point["rotation"],
                ) for point in connection["intermediatePoints"]],
            ) for connection in ferry["connections"]],
        ))
        
    return ferries

def ReadCompanyItems() -> list[c.CompanyItem]:
    path = FindCategoryFilePath("companies")
    if path is None: return []
    companies: list[c.CompanyItem] = []
    file = data_handler.ReadData(path)
    for company in file:
        companies.append(c.CompanyItem(
            company["uid"],
            company["x"],
            company["y"],
            0,
            0,
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
    file = data_handler.ReadData(path)
    for company in file:
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
    file = data_handler.ReadData(path)
    for model in file:
        models.append(c.Model(
            model["uid"],
            model["x"],
            model["y"],
            0,
            0,
            model["token"],
            model["nodeUid"],
            model["scale"]
        ))
    
    return models       

def ReadModelDescriptions() -> list[c.ModelDescription]:
    path = FindCategoryFilePath("modelDescriptions")
    if path is None: return []
    model_descriptions: list[c.ModelDescription] = []
    file = data_handler.ReadData(path)
    for model_description in file:
        model_descriptions.append(c.ModelDescription(
            model_description["token"],
            c.Position(
                model_description["center"]["x"],
                model_description["center"]["y"],
                TryReadExcept(model_description["center"], "z", 0)
            ),
            c.Position(
                model_description["start"]["x"],
                model_description["start"]["y"],
                TryReadExcept(model_description["start"], "z", 0),
            ),
            c.Position(
                model_description["end"]["x"],
                model_description["end"]["y"],
                TryReadExcept(model_description["end"], "z", 0),
            ),
            model_description["height"],
        ))
        
    return model_descriptions

def ReadMapAreas() -> list[c.MapArea]:
    path = FindCategoryFilePath("mapAreas")
    if path is None: return []
    map_areas: list[c.MapArea] = []
    file = data_handler.ReadData(path)
    for map_area in file:
        map_areas.append(c.MapArea(
            map_area["uid"],
            map_area["x"],
            map_area["y"],
            0,
            0,
            map_area["dlcGuard"],
            False, # draw_over
            map_area["nodeUids"],
            map_area["color"]
        ))
        
    return map_areas

def ReadPOIs() -> list[c.POI]:
    path = FindCategoryFilePath("pois")
    if path is None: return []
    pois: list[c.POI] = []
    file = data_handler.ReadData(path)
    for poi in file:
        if "label" in poi:
            if poi["type"] == c.NonFacilityPOI.LANDMARK:
                pois.append(c.LandmarkPOI(
                    TryReadExcept(poi, "uid", None),
                    poi["x"],
                    poi["y"],
                    TryReadExcept(poi, "z", 0),
                    0,
                    0,
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
                    0,
                    0,
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
                    0,
                    0,
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
                    0,
                    0,
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
                    0,
                    0,
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
    file = data_handler.ReadData(path)
    for country in file:
        countries.append(c.Country(
            country["token"],
            country["name"],
            None, # name_localized
            country["id"],
            country["x"],
            country["y"],
            country["code"],
        ))
        
    return countries

def ReadCities() -> list[c.City]:
    path = FindCategoryFilePath("cities")
    if path is None: return []
    cities: list[c.City] = []
    file = data_handler.ReadData(path)
    for city in file:
        cities.append(c.City(
            city["token"],
            city["name"],
            None, # name_localized
            city["countryToken"],
            city["population"],
            city["x"],
            city["y"],
            [c.CityArea(
                area["uid"],
                area["x"],
                area["y"],
                0,
                0,
                area["token"],
                area["hidden"],
                area["width"],
                area["height"],
            ) for area in city["areas"]]
        ))
        
    return cities

progress = 0
total_steps = 21
start_ram_usage = 0
state_object = None
def PrintState(start_time: float, message: str):
    global progress, start_ram_usage
    start_ram_usage = psutil.Process(os.getpid()).memory_info().rss
    print(f" → {message}", end="\r")
    if state_object != None:
        progress += 1
        state_object.text = " > " + message
        state_object.progress = progress / total_steps
    
def UpdateState(start_time: float, message: str):
    centiseconds = (time.perf_counter() - start_time) * 100
    total_ram_usage = (psutil.Process(os.getpid()).memory_info().rss - start_ram_usage) / 1024 / 1024
    if centiseconds < 1000:
        time_string = f"{centiseconds:.0f}cs  |"
    else:
        time_string = f"{centiseconds:.0f}cs |"
        
    print(f"[dim]{time_string}[/dim] {message} [dim] used {total_ram_usage:.0f}mb of RAM [/dim]", end="\n")

# MARK : ReadData()
def ReadData(state = None) -> c.MapData:
    global progress, state_object
    progress = 0
    state_object = state
    start_time = time.perf_counter()
    print("[yellow]Please wait for map to load the necessary data.[/yellow]")
    
    map = c.MapData()
    
    
    PrintState(start_time, "Nodes")
    map.nodes = ReadNodes()
    UpdateState(start_time, f"Loaded {len(map.nodes)} nodes")
    
    PrintState(start_time, "Navigation")
    map.navigation = ReadNodeGraph()
    if map.navigation == []:
        print("[red]No navigation map found (graph.json). Map cannot proceed.[/red]")
        return
    UpdateState(start_time, f"Loaded {len(map.navigation)} navigation entries")
    
    PrintState(start_time, "Elevations")
    map.elevations = ReadElevations()
    UpdateState(start_time, f"Loaded {len(map.elevations)} elevations")
    
    PrintState(start_time, "Roads")
    map.roads = ReadRoads()
    UpdateState(start_time, f"Loaded {len(map.roads)} roads")
    
    PrintState(start_time, "RoadLooks")
    map.road_looks = ReadRoadLooks()
    UpdateState(start_time, f"Loaded {len(map.road_looks)} road looks")
    
    PrintState(start_time, "Ferries")
    map.ferries = ReadFerries()
    UpdateState(start_time, f"Loaded {len(map.ferries)} ferries")
    
    PrintState(start_time, "Prefabs")
    map.prefabs = ReadPrefabs()
    UpdateState(start_time, f"Loaded {len(map.prefabs)} prefabs")
    
    PrintState(start_time, "Prefab Descriptions")
    map.prefab_descriptions = ReadPrefabDescriptions()
    UpdateState(start_time, f"Loaded {len(map.prefab_descriptions)} prefab descriptions")
    
    PrintState(start_time, "Company Definitions")
    map.companies = ReadCompanyItems()
    UpdateState(start_time, f"Loaded {len(map.companies)} company items")
    
    PrintState(start_time, "Companies")
    map.company_defs = ReadCompanies()
    UpdateState(start_time, f"Loaded {len(map.company_defs)} company definitions")
    
    PrintState(start_time, "Models")
    map.models = ReadModels()
    UpdateState(start_time, f"Loaded {len(map.models)} models")
    
    PrintState(start_time, "Model Descriptions")
    map.model_descriptions = ReadModelDescriptions()
    UpdateState(start_time, f"Loaded {len(map.model_descriptions)} model descriptions")
    
    # PrintState(start_time, "Map Areas")
    # map.map_areas = ReadMapAreas()
    # UpdateState(start_time, f"Loaded {len(map.map_areas)} map areas")
    
    PrintState(start_time, "Triggers")
    map.triggers = ReadTriggers()
    UpdateState(start_time, f"Loaded {len(map.triggers)} triggers")
    
    PrintState(start_time, "POIs")
    map.POIs = ReadPOIs()
    UpdateState(start_time, f"Loaded {len(map.POIs)} POIs")
    
    PrintState(start_time, "Countries")
    map.countries = ReadCountries()
    UpdateState(start_time, f"Loaded {len(map.countries)} countries")
    
    PrintState(start_time, "Cities")
    map.cities = ReadCities()
    UpdateState(start_time, f"Loaded {len(map.cities)} cities")
    
    PrintState(start_time, "Calculating sectors")
    map.calculate_sectors()
    UpdateState(start_time, f"Calculated sectors")
    
    PrintState(start_time, "Optimizing map")
    map.sort_to_sectors()
    map.build_dictionary()
    UpdateState(start_time, f"Sorted data to {map._max_sector_x - map._min_sector_x} x {map._max_sector_y - map._min_sector_y} ({map._sector_width}m x {map._sector_height}m) sectors")
    
    PrintState(start_time, "Linking objects (prefabs)")
    map.match_prefabs_to_descriptions()
    UpdateState(start_time, f"Linked prefabs to descriptions")
    
    PrintState(start_time, "Linking objects (roads)")
    map.match_roads_to_looks()
    UpdateState(start_time, f"Linked roads to looks")
    
    PrintState(start_time, "Computing Navigation Graph")
    map.compute_navigation_data()
    UpdateState(start_time, f"Computed navigation graph")
    
    print(f"[green]Data read in {time.perf_counter() - start_time:.2f} seconds.[/green]")
    data.map = map
    
    map.export_road_offsets()
    
    return map
