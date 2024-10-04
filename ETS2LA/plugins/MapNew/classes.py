from typing import Union, Literal, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum

def parse_string_to_int(string: str) -> int:
    if type(string) == int: return string
    return int(string, 16)

class FacilityIcon(Enum):
    PARKING = "parking_ico"
    GAS = "gas_ico"
    SERVICE = "service_ico"
    WEIGH = "weigh_station_ico"
    DEALER = "dealer_ico"
    GARAGE = "garage_ico"
    RECRUITMENT = "recruitment_ico"

class NonFacilityPOI(Enum):
    COMPANY = "company"
    LANDMARK = "landmark"
    VIEWPOINT = "viewpoint"
    FERRY = "ferry"
    TRAIN = "train"

class DarkColors(Enum):
    0 = (233, 235, 236)
    1 = (230, 203, 158)
    2 = (216, 166, 79)
    3 = (177, 202, 155)
    
class LightColors(Enum):
    0 = (90, 92, 94)
    1 = (112, 95, 67)
    2 = (80, 68, 48)
    3 = (51, 77, 61)

class MapColor(Enum):
    ROAD = 0
    LIGHT = 1
    DARK = 2
    GREEN = 3

class ItemType(Enum):
    Terrain = 1
    Building = 2
    Road = 3
    Prefab = 4
    Model = 5
    Company = 6
    Service = 7
    CutPlane = 8
    Mover = 9
    NoWeather = 11
    City = 12
    Hinge = 13
    MapOverlay = 18
    Ferry = 19
    Sound = 21
    Garage = 22
    CameraPoint = 23
    Trigger = 34
    FuelPump = 35 # services
    Sign = 36 # sign
    BusStop = 37
    TrafficRule = 38 # traffic_area
    BezierPatch = 39
    Compound = 40
    TrajectoryItem = 41
    MapArea = 42
    FarModel = 43
    Curve = 44
    CameraPath = 45
    Cutscene = 46
    Hookup = 47
    VisibilityArea = 48
    Gate = 49

class SpawnPointType(Enum):
    None = 0,
    TrailerPos = 1,
    UnloadEasyPos = 2,
    GasPos = 3,
    ServicePos = 4,
    TruckStopPos = 5,
    WeightStationPos = 6,
    TruckDealerPos = 7,
    Hotel = 8,
    Custom = 9,
    Parking = 10, # also shows parking in companies which don't work/show up in game
    Task = 11,
    MeetPos = 12,
    CompanyPos = 13,
    GaragePos = 14, # manage garage
    BuyPos = 15, # buy garage
    RecruitmentPos = 16,
    CameraPoint = 17,
    BusStation = 18,
    UnloadMediumPos = 19,
    UnloadHardPos = 20,
    UnloadRigidPos = 21,
    WeightCatPos = 22,
    CompanyUnloadPos = 23,
    TrailerSpawn = 24,
    LongTrailerPos = 25,

# MARK: Base Classes

@dataclass
class Node:
    uid: int | str
    x: float
    y: float
    z: float
    rotation: float
    forward_item_uid: int | str
    backward_item_uid: int | str
    sector_x: int
    sector_y: int
    forward_country_id: int | str
    backward_country_id: int | str
    
    def parse_strings(self):
        self.uid = parse_string_to_int(self.uid)
        self.forward_item_uid = parse_string_to_int(self.forward_item_uid)
        self.backward_item_uid = parse_string_to_int(self.backward_item_uid)
        self.forward_country_id = parse_string_to_int(self.forward_country_id)
        self.backward_country_id = parse_string_to_int(self.backward_country_id)
        
@dataclass
class Transform:
    x: float
    y: float
    z: float
    rotation: float
    
@dataclass
class Position:
    x: float
    y: float
    z: float
        
@dataclass
class BaseItem:
    uid: int | str
    type: ItemType
    x: float
    y: float
    z: float
    sector_x: int
    sector_y: int
    
    def parse_strings(self):
        self.uid = parse_string_to_int(self.uid)
        self.country_id = parse_string_to_int(self.country_id)
    
@dataclass    
class CityArea(BaseItem):
    token: str
    hidden: bool
    width: float
    height: float
    
    def __init__(self):
        super().parse_strings()
        self.type = ItemType.City
     
@dataclass   
class City:
    token: str
    name: str
    name_localized: str | None
    country_token: str
    population: int
    x: float
    y: float
    z: float
    areas: list[CityArea]

@dataclass
class Country:
    token: str
    name: str
    name_localized: str | None
    id: int
    x: float
    y: float
    z: float
    code: str
    
@dataclass
class Company:
    token: str
    name: str
    city_tokens: list[str]
    cargo_in_tokens: list[str]
    cargo_out_tokens: list[str]
    
@dataclass
class FerryConnection:
    token: str
    name: str
    name_localized: str | None
    x: float
    y: float
    z: float
    price: float
    time: float
    distance: float
    intermediate_points: list[Transform]
    
@dataclass
class Ferry:
    token: str
    train: bool
    name: str
    name_localized: str | None
    x: float
    y: float
    z: float
    connections: list[FerryConnection]
   
@dataclass
class RoadLook:
    lanes_left: list[str]
    lanes_right: list[str]
    offset: float | None
    lane_offset: float | None
    shoulder_space_left: float | None
    shoulder_space_right: float | None
   
@dataclass
class ModelDescription:
    center: Position
    start: Position
    end: Position
    height: float
   
# MARK: POIs
   
@dataclass 
class BasePOI:
    x: float
    y: float
    z: float
    sector_x: int
    sector_y: int
    icon: str
    
@dataclass
class GeneralPOI(BasePOI):
    type: NonFacilityPOI
    label: str
    
@dataclass
class LandmarkPOI(BasePOI):
    type: NonFacilityPOI = NonFacilityPOI.LANDMARK
    label: str
    dlc_guard: int
    node_uid: int | str
    
    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.nodeUid)
      
# This is not elegant but it is the only way to make it work in python  
LabeledPOI = Union[GeneralPOI, LandmarkPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""
    
@dataclass
class RoadPOI(BasePOI):
    type: str = "road"
    dlc_guard: int
    node_uid: int | str
    
    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.nodeUid)
        
@dataclass
class FacilityPOI(BasePOI):
    type: str = "facility"
    icon: FacilityIcon
    prefab_uid: int | str
    prefab_path: str
    
    def parse_strings(self):
        self.prefab_uid = parse_string_to_int(self.prefab_uid)
        
@dataclass
class ParkingPOI(BasePOI):
    type: str = "facility"
    icon: FacilityIcon = FacilityIcon.PARKING
    from_item_type: Literal["trigger", "mapOverlay", "prefab"]
    item_node_uids: list[int | str]
    dlc_guard: int
    
    def parse_strings(self):
        self.item_node_uids = [parse_string_to_int(node) for node in self.item_node_uids]
        
UnlabeledPOI = Union[RoadPOI, FacilityPOI, ParkingPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""
POI = Union[LabeledPOI, UnlabeledPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""

# MARK: Map Items

@dataclass 
class Road(BaseItem):
    type: ItemType = ItemType.Road
    dlc_guard: int
    hidden: bool | None
    road_look_token: str
    start_node_uid: int | str
    end_node_uid: int | str
    length: float
    maybe_divided: bool | None
    
    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)
        
@dataclass
class Prefab(BaseItem):
    type: ItemType = ItemType.Prefab
    dlc_guard: int
    hidden: bool | None
    token: str
    node_uids: list[int | str]
    origin_node_index: int
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]

@dataclass
class MapArea(BaseItem):
    type: ItemType = ItemType.MapArea
    dlc_guard: int
    draw_over: bool | None
    node_uids: list[int | str]
    color: MapColor
    
class MapOverlayType(Enum):
    ROAD = 0
    PARKING = 1
    LANDMARK = 4
    
@dataclass
class MapOverlay(BaseItem):
    type: ItemType = ItemType.MapOverlay
    dlc_guard: int
    overlay_type: MapOverlayType
    token: str
    node_uid: int | str
    
    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)
        
@dataclass
class Building(BaseItem):
    type: ItemType = ItemType.Building
    scheme: str
    start_node_uid: int | str
    end_node_uid: int | str
    
    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)
    
@dataclass
class Curve(BaseItem):
    type: ItemType = ItemType.Curve
    model: str
    look: str
    num_buildings: int
    start_node_uid: int | str
    end_node_uid: int | str
    
    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)
        
@dataclass
class FerryItem(BaseItem):
    type: ItemType = ItemType.Ferry
    token: str
    train: bool
    prefab_uid: int | str
    node_uid: int | str
    
    def parse_strings(self):
        super().parse_strings()
        self.prefab_uid = parse_string_to_int(self.prefab_uid)
        self.node_uid = parse_string_to_int(self.node_uid)
        
@dataclass
class CompanyItem(BaseItem):
    type: ItemType = ItemType.Company
    token: str
    city_token: str
    prefab_uid: int | str
    node_uid: int | str
    
    def parse_strings(self):
        super().parse_strings()
        self.prefab_uid = parse_string_to_int(self.prefab_uid)
        self.node_uid = parse_string_to_int(self.node_uid)
        
@dataclass
class Cutscene(BaseItem):
    type: ItemType = ItemType.Cutscene
    flags: int
    tags: list[str]
    node_uid: int | str
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)
        
@dataclass
class Trigger(BaseItem):
    type: ItemType = ItemType.Trigger
    dlc_guard: int
    action_tokens: list[str]
    node_uids: list[int | str]
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]
    
@dataclass
class Model(BaseItem):
    type: ItemType = ItemType.Model
    token: str
    node_uid: int | str
    scale: tuple[float, float, float]
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)
        
@dataclass
class Terrain(BaseItem):
    type: ItemType = ItemType.Terrain
    start_node_uid: int | str
    end_node_uid: int | str
    length: float
    
    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)
        
Item = Union[City, Country, Company, Ferry, POI, Road, Prefab, MapArea, MapOverlay, Building, Curve, FerryItem, CompanyItem, Cutscene, Trigger, Model, Terrain]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""
    
# MARK: Map Points
    
@dataclass
class BaseMapPoint:
    x: float
    y: float
    z: float
    neighbors: list[int | str]
    
    def parse_strings(self):
        self.neighbors = [parse_string_to_int(node) for node in self.neighbors]
        
@dataclass
class NavNode:
    node0: bool
    node1: bool
    node2: bool
    node3: bool
    node4: bool
    node5: bool
    node6: bool
    node_custom: bool
    
@dataclass
class NavFlags:
    is_start: bool
    is_base: bool
    is_end: bool
        
@dataclass
class RoadMapPoint(BaseMapPoint):
    type: str = "road"
    lanes_left: int | Literal["auto"]
    lanes_right: int | Literal["auto"]
    offset: float
    nav_node: NavNode
    nav_flags: NavFlags
    
@dataclass
class PolygonMapPoint(BaseMapPoint):
    type: str = "polygon"
    color: MapColor
    road_over: bool
    
MapPoint = Union[RoadMapPoint, PolygonMapPoint]

# MARK: Prefab Description

@dataclass
class PrefabNode:
    x: float
    y: float
    z: float
    rotation: float
    input_lanes: list[int]
    """indices into nav_curves"""
    output_lanes: list[int]
    """indices into nav_curves"""

@dataclass
class PrefabSpawnPoints:
    x: float
    y: float
    z: float
    type: SpawnPointType

@dataclass
class PrefabTriggerPoint:
    x: float
    y: float
    z: float
    action: str

@dataclass
class PrefabNavCurve:
    nav_node_index: int
    start: Transform
    end: Transform
    next_lines: list[int]
    prev_lines: list[int]

@dataclass
class NavNodeConnection:
    target_nav_node_index: int
    curve_indeces: list[int]

@dataclass
class NavNode:
    type: Literal["physical", "ai"]
    """
    **physical**: the index of the normal node (see nodes array) this navNode ends at.\n
    **ai**: the index of the AI curve this navNode ends at.
    """
    end_index: int
    connections: list[NavNodeConnection]

@dataclass
class PrefabDescription:
    nodes: list[PrefabNode]
    map_points: RoadMapPoint | PolygonMapPoint
    spawn_points: list[PrefabSpawnPoints]
    trigger_points: list[PrefabTriggerPoint]
    nav_curves: list[PrefabNavCurve]
    nav_nodes: list[NavNode]
    
# MARK: MapData

T = TypeVar('T')
@dataclass
class WithToken(Generic[T]):
    data: T
    token: str

class MapData:
    nodes: list[Node]
    elevations: list[tuple[int, int, int]]
    roads: list[Road]
    ferries: list[Ferry]
    prefabs: list[Prefab]
    companies: list[CompanyItem]
    models: list[Model]
    map_areas: list[MapArea]
    POIs: list[POI]
    dividers: list[Building | Curve]
    countries: list[Country]
    cities: list[City]
    road_looks: list[WithToken[RoadLook]]
    prefab_descriptions: list[WithToken[PrefabDescription]]
    model_description: list[WithToken[ModelDescription]]
    