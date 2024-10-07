# General imports
from typing import Union, Literal, TypeVar, Generic
from enum import Enum, StrEnum, IntEnum
from dataclasses import dataclass
import math

# ETS2LA imports
from ETS2LA.utils.dictionaries import get_nested_item, set_nested_item
import utils.prefab_helpers as prefab_helpers
import utils.math_helpers as math_helpers

# MARK: Constants

data = None
"""The data object that is used by classes here. Will be set once the MapData object is created and loaded."""

def parse_string_to_int(string: str) -> int:
    if type(string) == int: return string
    return int(string, 16)

class FacilityIcon(StrEnum):
    PARKING = "parking_ico"
    GAS = "gas_ico"
    SERVICE = "service_ico"
    WEIGH = "weigh_station_ico"
    DEALER = "dealer_ico"
    GARAGE = "garage_ico"
    RECRUITMENT = "recruitment_ico"

class NonFacilityPOI(StrEnum):
    COMPANY = "company"
    LANDMARK = "landmark"
    VIEWPOINT = "viewpoint"
    FERRY = "ferry"
    TRAIN = "train"

class DarkColors(Enum):
    0 == (233, 235, 236)
    1 == (230, 203, 158)
    2 == (216, 166, 79)
    3 == (177, 202, 155)
    
class LightColors(Enum):
    0 == (90, 92, 94)
    1 == (112, 95, 67)
    2 == (80, 68, 48)
    3 == (51, 77, 61)

class MapColor(IntEnum):
    ROAD = 0
    LIGHT = 1
    DARK = 2
    GREEN = 3

class ItemType(IntEnum):
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

class SpawnPointType(IntEnum):
    NONE = 0,
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
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, rotation: float, forward_item_uid: int | str, backward_item_uid: int | str, sector_x: int, sector_y: int, forward_country_id: int | str, backward_country_id: int | str):
        self.uid = uid
        self.x = x
        self.y = y
        self.z = z
        self.rotation = rotation
        self.forward_item_uid = forward_item_uid
        self.backward_item_uid = backward_item_uid
        self.sector_x = sector_x
        self.sector_y = sector_y
        self.forward_country_id = forward_country_id
        self.backward_country_id = backward_country_id
        self.parse_strings()
        

class Transform:
    x: float
    y: float
    z: float
    rotation: float
    
    def __init__(self, x: float, y: float, z: float, rotation: float):
        self.x = x
        self.y = y
        self.z = z
        self.rotation = rotation
        
    def __str__(self) -> str:
        return f"Transform({self.x}, {self.y}, {self.z}, {self.rotation})"
    
    def __repr__(self) -> str:
        return self.__str__()
    

class Position:
    x: float
    y: float
    z: float
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        
    def tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __str__(self) -> str:
        return f"Position({self.x}, {self.y}, {self.z})"
    
    def __repr__(self) -> str:
        return self.__str__()
        

class BaseItem:
    uid: int | str
    type: ItemType
    x: float
    y: float
    sector_x: int
    sector_y: int
    
    def parse_strings(self):
        self.uid = parse_string_to_int(self.uid)
        
    def __init__(self, uid: int | str, type: ItemType, x: float, y: float, sector_x: int, sector_y: int):
        self.uid = uid
        self.type = type
        self.x = x
        self.y = y
        self.sector_x = sector_x
        self.sector_y = sector_y
    
    
class CityArea(BaseItem):
    token: str
    hidden: bool
    width: float
    height: float
    
    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, token: str, hidden: bool, width: float, height: float):
        super().__init__(uid, ItemType.City, x, y, sector_x, sector_y)
        super().parse_strings()
        self.token = token
        self.hidden = hidden
        self.width = width
        self.height = height
     
   
class City:
    token: str
    name: str
    name_localized: str | None
    country_token: str
    population: int
    x: float
    y: float
    areas: list[CityArea]
    
    def __init__(self, token: str, name: str, name_localized: str | None, country_token: str, population: int, x: float, y: float, areas: list[CityArea]):
        self.token = token
        self.name = name
        self.name_localized = name_localized
        self.country_token = country_token
        self.population = population
        self.x = x
        self.y = y
        self.areas = areas


class Country:
    token: str
    name: str
    name_localized: str | None
    id: int
    x: float
    y: float
    code: str
    
    def __init__(self, token: str, name: str, name_localized: str | None, id: int, x: float, y: float, code: str):
        self.token = token
        self.name = name
        self.name_localized = name_localized
        self.id = id
        self.x = x
        self.y = y
        self.code = code
    

class Company:
    token: str
    name: str
    city_tokens: list[str]
    cargo_in_tokens: list[str]
    cargo_out_tokens: list[str]
    
    def __init__(self, token: str, name: str, city_tokens: list[str], cargo_in_tokens: list[str], cargo_out_tokens: list[str]):
        self.token = token
        self.name = name
        self.city_tokens = city_tokens
        self.cargo_in_tokens = cargo_in_tokens
        self.cargo_out_tokens = cargo_out_tokens
    

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
    
    def __init__(self, token: str, name: str, name_localized: str | None, x: float, y: float, z: float, price: float, time: float, distance: float, intermediate_points: list[Transform]):
        self.token = token
        self.name = name
        self.name_localized = name_localized
        self.x = x
        self.y = y
        self.z = z
        self.price = price
        self.time = time
        self.distance = distance
        self.intermediate_points = intermediate_points
    

class Ferry:
    token: str
    train: bool
    name: str
    name_localized: str | None
    x: float
    y: float
    z: float
    connections: list[FerryConnection]
    
    def __init__(self, token: str, train: bool, name: str, name_localized: str | None, x: float, y: float, z: float, connections: list[FerryConnection]):
        self.token = token
        self.train = train
        self.name = name
        self.name_localized = name_localized
        self.x = x
        self.y = y
        self.z = z
        self.connections = connections
   

class RoadLook:
    token: str
    name: str
    lanes_left: list[str]
    lanes_right: list[str]
    offset: float | None
    lane_offset: float | None
    shoulder_space_left: float | None
    shoulder_space_right: float | None
    
    def __init__(self, token: str, name:str, lanes_left: list[str], lanes_right: list[str], offset: float | None, lane_offset: float | None, shoulder_space_left: float | None, shoulder_space_right: float | None):
        self.token = token
        self.name = name
        self.lanes_left = lanes_left
        self.lanes_right = lanes_right
        self.offset = offset
        self.lane_offset = lane_offset
        self.shoulder_space_left = shoulder_space_left
        self.shoulder_space_right = shoulder_space_right
   

class ModelDescription:
    token: str
    center: Position
    start: Position
    end: Position
    height: float
    
    def __init__(self, token: str, center: Position, start: Position, end: Position, height: float):
        self.token = token
        self.center = center
        self.start = start
        self.end = end
        self.height = height
   
# MARK: POIs
 
class BasePOI:
    uid: int | str
    x: float
    y: float
    z: float
    sector_x: int
    sector_y: int
    icon: str
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str):
        self.uid = uid
        self.x = x
        self.y = y
        self.z = z
        self.sector_x = sector_x
        self.sector_y = sector_y
        self.icon = icon
    

class GeneralPOI(BasePOI):
    type: NonFacilityPOI
    label: str
    
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str, label: str):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.label = label
    

class LandmarkPOI(BasePOI):
    label: str
    dlc_guard: int
    node_uid: int | str
    type: NonFacilityPOI = NonFacilityPOI.LANDMARK
    
    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str, label: str, dlc_guard: int, node_uid: int | str):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.label = label
        self.dlc_guard = dlc_guard
        self.node_uid = node_uid
        self.parse_strings()
      
# This is not elegant but it is the only way to make it work in python  
LabeledPOI = Union[GeneralPOI, LandmarkPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""
    

class RoadPOI(BasePOI):
    dlc_guard: int
    node_uid: int | str
    type: str = "road"
    
    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str, dlc_guard: int, node_uid: int | str):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.dlc_guard = dlc_guard
        self.node_uid = node_uid
        self.parse_strings()
        

class FacilityPOI(BasePOI):
    icon: FacilityIcon
    prefab_uid: int | str
    prefab_path: str
    type: str = "facility"
    
    def parse_strings(self):
        self.prefab_uid = parse_string_to_int(self.prefab_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str, prefab_uid: int | str, prefab_path: str):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.prefab_uid = prefab_uid
        self.prefab_path = prefab_path
        self.parse_strings()
        

class ParkingPOI(BasePOI):
    dlc_guard: int
    from_item_type: Literal["trigger", "mapOverlay", "prefab"]
    item_node_uids: list[int | str]
    type: str = "facility"
    icon: FacilityIcon = FacilityIcon.PARKING

    def parse_strings(self):
        self.item_node_uids = [parse_string_to_int(node) for node in self.item_node_uids]
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str, dlc_guard: int, from_item_type: Literal["trigger", "mapOverlay", "prefab"], item_node_uids: list[int | str]):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.dlc_guard = dlc_guard
        self.from_item_type = from_item_type
        self.item_node_uids = item_node_uids
        self.parse_strings()
        
UnlabeledPOI = Union[RoadPOI, FacilityPOI, ParkingPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""
POI = Union[LabeledPOI, UnlabeledPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""

# MARK: Map Items

class Road(BaseItem):
    dlc_guard: int
    hidden: bool | None
    road_look_token: str
    start_node_uid: int | str
    end_node_uid: int | str
    length: float
    maybe_divided: bool | None
    type: ItemType = ItemType.Road
    road_look: RoadLook = None
    
    _points: list[Position] = None
    
    def parse_strings(self):
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, dlc_guard: int, hidden: bool | None, road_look_token: str, start_node_uid: int | str, end_node_uid: int | str, length: float, maybe_divided: bool | None):
        super().__init__(uid, ItemType.Road, x, y, sector_x, sector_y)
        super().parse_strings()
        self.dlc_guard = dlc_guard
        self.hidden = hidden
        self.road_look_token = road_look_token
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
        self.length = length
        self.maybe_divided = maybe_divided
        self.parse_strings()
        
    def generate_points(self, road_quality: float = 0.5, min_quality: int = 4) -> list[Position]:
        # All this code is copied from the original C# implementation of point calculations
        # ts-map-lane-assist/TsMap/TsMapRenderer.cs -> 473 (after foreach(var road in _mapper.Roads))
        
        start_node = data.get_node_by_uid(self.start_node_uid)
        end_node = data.get_node_by_uid(self.end_node_uid)
        new_points = []

        # Data has Z as the height value, but we need Y
        sx = start_node.x
        sy = start_node.z
        sz = start_node.y
        ex = end_node.x
        ey = end_node.z
        ez = end_node.y
        
        # Get the length of the road
        length = math.sqrt(math.pow(sx - ex, 2) + math.pow(sy - ey, 2) + math.pow(sz - ez, 2))
        radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))

        tan_sx = math.cos(start_node.rotation) * radius
        tan_ex = math.cos(end_node.rotation) * radius
        tan_sz = math.sin(start_node.rotation) * radius
        tan_ez = math.sin(end_node.rotation) * radius

        needed_points = int(length * road_quality)
        if needed_points < min_quality:
            needed_points = min_quality

        for i in range(needed_points):
            s = i / (needed_points - 1)
            x = math_helpers.Hermite(s, sx, ex, tan_sx, tan_ex)
            y = sy + (ey - sy) * s
            z = math_helpers.Hermite(s, sz, ez, tan_sz, tan_ez)
            new_points.append(Position(x, y, z))

        return new_points
        
    @property
    def points(self) -> list[Position]:
        if self._points is None:
            self._points = self.generate_points()
            
        return self._points
    
    @points.setter
    def points(self, value: list[Position]):
        self._points = value


class MapArea(BaseItem):
    dlc_guard: int
    draw_over: bool | None
    node_uids: list[int | str]
    color: MapColor
    type: ItemType = ItemType.MapArea
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]
        
    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, dlc_guard: int, draw_over: bool | None, node_uids: list[int | str], color: MapColor):
        super().__init__(uid, ItemType.MapArea, x, y, sector_x, sector_y)
        self.dlc_guard = dlc_guard
        self.draw_over = draw_over
        self.node_uids = node_uids
        self.color = color
        self.parse_strings()
    
class MapOverlayType(Enum):
    ROAD = 0
    PARKING = 1
    LANDMARK = 4
    

class MapOverlay(BaseItem):
    dlc_guard: int
    overlay_type: MapOverlayType
    token: str
    node_uid: int | str
    type: ItemType = ItemType.MapOverlay
    
    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, dlc_guard: int, overlay_type: MapOverlayType, token: str, node_uid: int | str):
        super().__init__(uid, ItemType.MapOverlay, x, y, z, sector_x, sector_y)
        self.dlc_guard = dlc_guard
        self.overlay_type = overlay_type
        self.token = token
        self.node_uid = node_uid
        

class Building(BaseItem):
    scheme: str
    start_node_uid: int | str
    end_node_uid: int | str
    type: ItemType = ItemType.Building
    
    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, scheme: str, start_node_uid: int | str, end_node_uid: int | str):
        super().__init__(uid, ItemType.Building, x, y, z, sector_x, sector_y)
        self.scheme = scheme
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
    

class Curve(BaseItem):
    model: str
    look: str
    num_buildings: int
    start_node_uid: int | str
    end_node_uid: int | str
    type: ItemType = ItemType.Curve
    
    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, model: str, look: str, num_buildings: int, start_node_uid: int | str, end_node_uid: int | str):
        super().__init__(uid, ItemType.Curve, x, y, z, sector_x, sector_y)
        self.model = model
        self.look = look
        self.num_buildings = num_buildings
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
        

class FerryItem(BaseItem):
    token: str
    train: bool
    prefab_uid: int | str
    node_uid: int | str
    type: ItemType = ItemType.Ferry
    
    def parse_strings(self):
        super().parse_strings()
        self.prefab_uid = parse_string_to_int(self.prefab_uid)
        self.node_uid = parse_string_to_int(self.node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, token: str, train: bool, prefab_uid: int | str, node_uid: int | str):
        super().__init__(uid, ItemType.Ferry, x, y, z, sector_x, sector_y)
        self.token = token
        self.train = train
        self.prefab_uid = prefab_uid
        self.node_uid = node_uid
        

class CompanyItem(BaseItem):
    token: str
    city_token: str
    prefab_uid: int | str
    node_uid: int | str
    type: ItemType = ItemType.Company
    
    def parse_strings(self):
        super().parse_strings()
        self.prefab_uid = parse_string_to_int(self.prefab_uid)
        self.node_uid = parse_string_to_int(self.node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, token: str, city_token: str, prefab_uid: int | str, node_uid: int | str):
        super().__init__(uid, ItemType.Company, x, y, sector_x, sector_y)
        self.token = token
        self.city_token = city_token
        self.prefab_uid = prefab_uid
        self.node_uid = node_uid
        

class Cutscene(BaseItem):
    flags: int
    tags: list[str]
    node_uid: int | str
    type: ItemType = ItemType.Cutscene
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, flags: int, tags: list[str], node_uid: int | str):
        super().__init__(uid, ItemType.Cutscene, x, y, z, sector_x, sector_y)
        self.flags = flags
        self.tags = tags
        self.node_uid = node_uid
        

class Trigger(BaseItem):
    dlc_guard: int
    action_tokens: list[str]
    node_uids: list[int | str]
    type: ItemType = ItemType.Trigger
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, dlc_guard: int, action_tokens: list[str], node_uids: list[int | str]):
        super().__init__(uid, ItemType.Trigger, x, y, z, sector_x, sector_y)
        self.dlc_guard = dlc_guard
        self.action_tokens = action_tokens
        self.node_uids = node_uids
    

class Model(BaseItem):
    token: str
    node_uid: int | str
    scale: tuple[float, float, float]
    type: ItemType = ItemType.Model
    z: float = 0
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, token: str, node_uid: int | str, scale: tuple[float, float, float]):
        super().__init__(uid, ItemType.Model, x, y, sector_x, sector_y)
        self.token = token
        self.node_uid = node_uid
        self.scale = scale
        self.z = z
        

class Terrain(BaseItem):
    start_node_uid: int | str
    end_node_uid: int | str
    length: float
    type: ItemType = ItemType.Terrain
    
    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)
        
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, start_node_uid: int | str, end_node_uid: int | str, length: float):
        super().__init__(uid, ItemType.Terrain, x, y, z, sector_x, sector_y)
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
        self.length = length
    
# MARK: Map Points
    
class BaseMapPoint:
    x: float
    y: float
    z: float
    neighbors: list[int | str]
    
    def parse_strings(self):
        self.neighbors = [parse_string_to_int(node) for node in self.neighbors]
        
    def __init__(self, x: float, y: float, z: float, neighbors: list[int | str]):
        self.x = x
        self.y = y
        self.z = z
        self.neighbors = neighbors
        

class NavNode:
    node0: bool
    node1: bool
    node2: bool
    node3: bool
    node4: bool
    node5: bool
    node6: bool
    node_custom: bool
    
    def __init__(self, node0: bool, node1: bool, node2: bool, node3: bool, node4: bool, node5: bool, node6: bool, node_custom: bool):
        self.node0 = node0
        self.node1 = node1
        self.node2 = node2
        self.node3 = node3
        self.node4 = node4
        self.node5 = node5
        self.node6 = node6
        self.node_custom = node_custom

class NavFlags:
    is_start: bool
    is_base: bool
    is_end: bool
        
    def __init__(self, is_start: bool, is_base: bool, is_end: bool):
        self.is_start = is_start
        self.is_base = is_base
        self.is_end = is_end

class RoadMapPoint(BaseMapPoint):
    lanes_left: int | Literal["auto"]
    lanes_right: int | Literal["auto"]
    offset: float
    nav_node: NavNode
    nav_flags: NavFlags
    type: str = "road"
    
    def __init__(self, x: float, y: float, z: float, neighbors: list[int | str], lanes_left: int | Literal["auto"], lanes_right: int | Literal["auto"], offset: float, nav_node: NavNode, nav_flags: NavFlags):
        super().__init__(x, y, z, neighbors)
        self.lanes_left = lanes_left
        self.lanes_right = lanes_right
        self.offset = offset
        self.nav_node = nav_node
        self.nav_flags = nav_flags
    

class PolygonMapPoint(BaseMapPoint):
    color: MapColor
    road_over: bool
    type: str = "polygon"
    
    def __init__(self, x: float, y: float, z: float, neighbors: list[int | str], color: MapColor, road_over: bool):
        super().__init__(x, y, z, neighbors)
        self.color = color
        self.road_over = road_over
    
MapPoint = Union[RoadMapPoint, PolygonMapPoint]

# MARK: Prefabs

class PrefabNode:
    x: float
    y: float
    z: float
    rotation: float
    input_lanes: list[int]
    """indices into nav_curves"""
    output_lanes: list[int]
    """indices into nav_curves"""
    
    def __init__(self, x: float, y: float, z: float, rotation: float, input_lanes: list[int], output_lanes: list[int]):
        self.x = x
        self.y = y
        self.z = z
        self.rotation = rotation
        self.input_lanes = input_lanes
        self.output_lanes = output_lanes


class PrefabSpawnPoints:
    x: float
    y: float
    z: float
    type: SpawnPointType
    
    def __init__(self, x: float, y: float, z: float, type: SpawnPointType):
        self.x = x
        self.y = y
        self.z = z
        self.type = type


class PrefabTriggerPoint:
    x: float
    y: float
    z: float
    action: str
    
    def __init__(self, x: float, y: float, z: float, action: str):
        self.x = x
        self.y = y
        self.z = z
        self.action = action


class PrefabNavCurve:
    nav_node_index: int
    start: Transform
    end: Transform
    next_lines: list[int]
    prev_lines: list[int]
    points: list[Position] = []
    
    def __init__(self, nav_node_index: int, start: Transform, end: Transform, next_lines: list[int], prev_lines: list[int]):
        self.nav_node_index = nav_node_index
        self.start = start
        self.end = end
        self.next_lines = next_lines
        self.prev_lines = prev_lines
        self.points = self.generate_points()
        
    def generate_points(self, road_quality: float = 1, min_quality: int = 4) -> list[Position]:
        new_points = []

        # Data has Z as the height value, but we need Y
        sx = self.start.x
        sy = self.start.z
        sz = self.start.y
        ex = self.end.x
        ey = self.end.z
        ez = self.end.y
                
        length = math.sqrt(math.pow(sx - ex, 2) + math.pow(sy - ey, 2) + math.pow(sz - ez, 2))
        radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))
        
        tan_sx = math.cos((self.start.rotation)) * radius
        tan_ex = math.cos((self.end.rotation)) * radius
        tan_sz = math.sin((self.start.rotation)) * radius
        tan_ez = math.sin((self.end.rotation)) * radius
        
        needed_points = int(length * road_quality)
        if needed_points < min_quality:
            needed_points = min_quality
        for i in range(needed_points):
            s = i / (needed_points - 1)
            x = math_helpers.Hermite(s, sx, ex, tan_sx, tan_ex)
            y = sy + (ey - sy) * s
            z = math_helpers.Hermite(s, sz, ez, tan_sz, tan_ez)
            new_points.append(Position(x, y, z))
        
        return new_points


class NavNodeConnection:
    target_nav_node_index: int
    curve_indeces: list[int]
    
    def __init__(self, target_nav_node_index: int, curve_indeces: list[int]):
        self.target_nav_node_index = target_nav_node_index
        self.curve_indeces = curve_indeces


class PrefabNavNode:
    type: Literal["physical", "ai"]
    """
    **physical**: the index of the normal node (see nodes array) this navNode ends at.\n
    **ai**: the index of the AI curve this navNode ends at.
    """
    end_index: int
    connections: list[NavNodeConnection]
    
    def __init__(self, type: Literal["physical", "ai"], end_index: int, connections: list[NavNodeConnection]):
        self.type = type
        self.end_index = end_index
        self.connections = connections


class PrefabNavRoute:
    curves: list[PrefabNavCurve]
    points: list[Position] = []
    
    def __init__(self, curves: list[PrefabNavCurve]):
        self.curves = curves
        self.points = self.generate_points()
        
    def generate_points(self) -> list[Position]:
        new_points = []
        for curve in self.curves:
            new_points += curve.points
        return new_points

class PrefabDescription:
    token: str
    nodes: list[PrefabNode]
    map_points: RoadMapPoint | PolygonMapPoint
    spawn_points: list[PrefabSpawnPoints]
    trigger_points: list[PrefabTriggerPoint]
    nav_curves: list[PrefabNavCurve]
    nav_nodes: list[PrefabNavNode]
    _nav_routes: list[PrefabNavRoute] = []
    
    def __init__(self, token: str,nodes: list[PrefabNode], map_points: RoadMapPoint | PolygonMapPoint, spawn_points: list[PrefabSpawnPoints], trigger_points: list[PrefabTriggerPoint], nav_curves: list[PrefabNavCurve], nav_nodes: list[NavNode]):
        self.token = token
        self.nodes = nodes
        self.map_points = map_points
        self.spawn_points = spawn_points
        self.trigger_points = trigger_points
        self.nav_curves = nav_curves
        self.nav_nodes = nav_nodes
        
    @property
    def nav_routes(self) -> list[PrefabNavRoute]:
        if self._nav_routes == []:
            self.build_nav_routes()
            
        return self._nav_routes
    
    @nav_routes.setter
    def nav_routes(self, value: list[PrefabNavRoute]):
        self._nav_routes = value
        
    def build_nav_routes(self):
        starting_curves = prefab_helpers.find_starting_curves(self)
        self._nav_routes = []
        for curve in starting_curves:
            curve_routes = prefab_helpers.traverse_curve_till_end(curve, self)
            for route in curve_routes:
                nav_route = PrefabNavRoute(route)
                self._nav_routes.append(nav_route)
        
    
class Prefab(BaseItem):
    dlc_guard: int
    hidden: bool | None
    token: str
    node_uids: list[int | str]
    origin_node_index: int
    type: ItemType = ItemType.Prefab
    prefab_description: PrefabDescription = None
    z: float = 0
    
    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]
    
    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, dlc_guard: int, hidden: bool | None, token: str, node_uids: list[int | str], origin_node_index: int):
        super().__init__(uid, ItemType.Prefab, x, y, sector_x, sector_y)
        self.z = z
        self.dlc_guard = dlc_guard
        self.hidden = hidden
        self.token = token
        self.node_uids = node_uids
        self.origin_node_index = origin_node_index
    
Item = Union[City, Country, Company, Ferry, POI, Road, Prefab, MapArea, MapOverlay, Building, Curve, FerryItem, CompanyItem, Cutscene, Trigger, Model, Terrain]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""
    
# MARK: MapData
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
    company_defs: list[Company]
    road_looks: list[RoadLook]
    prefab_descriptions: list[PrefabDescription]
    model_descriptions: list[ModelDescription]
    
    _nodes_by_sector: dict[dict[Node]]
    _roads_by_sector: dict[dict[Road]]
    _prefabs_by_sector: dict[dict[Prefab]]
    
    _min_sector_x:  int = math.inf
    _max_sector_x:  int = -math.inf
    _min_sector_y:  int = math.inf
    _max_sector_y:  int = -math.inf
    _sector_width:  int = 4000
    _sector_height: int = 4000
    
    _nodes_by_uid = {}
    """
    Nested nodes dictionary for quick access to nodes by their UID. UID is split into 4 character strings to index into the nested dictionaries.
    Please use the get_node_by_uid method to access nodes by UID.
    """
    
    def sort_to_sectors(self) -> None:
        self._nodes_by_sector = {}
        self._roads_by_sector = {}
        self._prefabs_by_sector = {}
        
        for node in self.nodes:
            sector = (node.sector_x, node.sector_y)
            
            if sector[0] < self._min_sector_x:
                self._min_sector_x = sector[0]
            if sector[0] > self._max_sector_x:
                self._max_sector_x = sector[0]
            if sector[1] < self._min_sector_y:
                self._min_sector_y = sector[1]
            if sector[1] > self._max_sector_y:
                self._max_sector_y = sector[1]
                
            if sector[0] not in self._nodes_by_sector:
                self._nodes_by_sector[sector[0]] = {}
            if sector[1] not in self._nodes_by_sector[sector[0]]:
                self._nodes_by_sector[sector[0]][sector[1]] = []
                
            self._nodes_by_sector[sector[0]][sector[1]].append(node)
        
        for road in self.roads:
            sector = (road.sector_x, road.sector_y)
            if sector[0] not in self._roads_by_sector:
                self._roads_by_sector[sector[0]] = {}
            if sector[1] not in self._roads_by_sector[sector[0]]:
                self._roads_by_sector[sector[0]][sector[1]] = []
            self._roads_by_sector[sector[0]][sector[1]].append(road)
        
        for prefab in self.prefabs:
            sector = (prefab.sector_x, prefab.sector_y)
            if sector[0] not in self._prefabs_by_sector:
                self._prefabs_by_sector[sector[0]] = {}
            if sector[1] not in self._prefabs_by_sector[sector[0]]:
                self._prefabs_by_sector[sector[0]][sector[1]] = []
            self._prefabs_by_sector[sector[0]][sector[1]].append(prefab)
            
    def calculate_sector_dimensions(self) -> None:
        min_sector_x = self._min_sector_x
        min_sector_x_y = min([key for key in self._nodes_by_sector[min_sector_x].keys()])
        min_sector_y = self._min_sector_y
        min_sector_y_x = min([key if min_sector_y in self._nodes_by_sector[key].keys() else math.inf for key in self._nodes_by_sector.keys()])
        min_x = min([node.x for node in self._nodes_by_sector[min_sector_x][min_sector_x_y]])
        min_y = min([node.y for node in self._nodes_by_sector[min_sector_y_x][min_sector_y]])
        
        max_sector_x = self._max_sector_x
        max_sector_x_y = max([key for key in self._nodes_by_sector[max_sector_x].keys()])
        max_sector_y = self._max_sector_y
        max_sector_y_x = max([key if max_sector_y in self._nodes_by_sector[key].keys() else -math.inf for key in self._nodes_by_sector.keys()])
        max_x = max([node.x for node in self._nodes_by_sector[max_sector_x][max_sector_x_y]])
        max_y = max([node.y for node in self._nodes_by_sector[max_sector_y_x][max_sector_y]])
        
        self._sector_width = (max_x - min_x) / (max_sector_x - min_sector_x)
        self._sector_height = (max_y - min_y) / (max_sector_y - min_sector_y)
          
    def build_node_dictionary(self) -> None:
        self._nodes_by_uid = {}
        for node in self.nodes:
            uid = node.uid
            uid_str = str(uid)
            parts = [uid_str[i:i+4] for i in range(0, len(uid_str), 4)]
            set_nested_item(self._nodes_by_uid, parts, node)
            
    def get_sector_from_coordinates(self, x: float, z: float) -> tuple[int, int]:
        return (int(x // self._sector_width), int(z // self._sector_height))
                
    def get_sector_nodes_by_coordinates(self, x: float, z: float) -> list[Node]:
        sector = self.get_sector_from_coordinates(x, z)
        return self.get_sector_nodes_by_sector(sector)
                
    def get_sector_nodes_by_sector(self, sector: tuple[int, int]) -> list[Node]:
        return self._nodes_by_sector.get(sector[0], {}).get(sector[1], [])
    
    def get_sector_roads_by_coordinates(self, x: float, z: float) -> list[Road]:
        print(x, z)
        sector = self.get_sector_from_coordinates(x, z)
        print(sector)
        return self.get_sector_roads_by_sector(sector)
    
    def get_sector_roads_by_sector(self, sector: tuple[int, int]) -> list[Road]:
        return self._roads_by_sector.get(sector[0], {}).get(sector[1], [])
    
    def get_sector_prefabs_by_coordinates(self, x: float, z: float) -> list[Prefab]:
        sector = self.get_sector_from_coordinates(x, z)
        return self.get_sector_prefabs_by_sector(sector)
    
    def get_sector_prefabs_by_sector(self, sector: tuple[int, int]) -> list[Prefab]:
        return self._prefabs_by_sector.get(sector[0], {}).get(sector[1], [])
            
    def get_node_by_uid(self, uid: int | str) -> Node:  
        uid_str = str(uid)
        parts = [uid_str[i:i+4] for i in range(0, len(uid_str), 4)]
        return get_nested_item(self._nodes_by_uid, parts)
            
    def match_roads_to_looks(self) -> None:
        for road in self.roads:
            for look in self.road_looks:
                if road.road_look_token == look.token:
                    road.road_look = look
                    break
                
    def match_prefabs_to_descriptions(self) -> None:
        for prefab in self.prefabs:
            for description in self.prefab_descriptions:
                if prefab.token == description.token:
                    prefab.prefab_description = description
                    break