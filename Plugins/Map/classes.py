"""Map plugin classes."""
from typing import Union, Literal, TypeVar, Generic, Optional, List, Any
from enum import Enum, StrEnum, IntEnum
from dataclasses import dataclass
import logging
import math

# Import dictionary utilities with fallback to mocks for testing
from ETS2LA.Utils.Values.dictionaries import get_nested_item, set_nested_item

from Plugins.Map.utils import prefab_helpers
from Plugins.Map.utils import math_helpers
from Plugins.Map.utils import road_helpers
from Plugins.Map.utils import node_helpers

# MARK: Constants

data = None
"""The data object that is used by classes here. Will be set once the MapData object is created and loaded."""


def parse_string_to_int(string: str) -> int:
    if string is None: return None
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
    FuelPump = 35  # services
    Sign = 36  # sign
    BusStop = 37
    TrafficRule = 38  # traffic_area
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
    Parking = 10,  # also shows parking in companies which don't work/show up in game
    Task = 11,
    MeetPos = 12,
    CompanyPos = 13,
    GaragePos = 14,  # manage garage
    BuyPos = 15,  # buy garage
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

class NavigationNode:
    node_id: int | str
    distance: float
    direction: Literal["forward", "backward"]
    is_one_lane_road: bool
    dlc_guard: int
    item_uid: int | str = ""
    item_type = None
    lane_indices: list[int] = []
    """This is a list of the lane indices that go through this navigation node."""
    
    def parse_strings(self):
        self.node_id = parse_string_to_int(self.node_id)
        
    def __init__(self, node_id: int | str, distance: float, direction: Literal["forward", "backward"], is_one_lane_road: bool, dlc_guard: int):
        self.node_id = node_id
        self.distance = distance
        self.direction = direction
        self.is_one_lane_road = is_one_lane_road
        self.dlc_guard = dlc_guard
        self.parse_strings()
        
    def json(self) -> dict:
        return {
            "node_id": self.node_id,
            "distance": self.distance,
            "direction": self.direction,
            "is_one_lane_road": self.is_one_lane_road,
            "dlc_guard": self.dlc_guard
        }

class NavigationEntry:
    uid: int | str
    forward: list[NavigationNode]
    backward: list[NavigationNode]
    
    def parse_strings(self):
        self.uid = parse_string_to_int(self.uid)
        
    def __init__(self, uid: int | str, forward: list[NavigationNode], backward: list[NavigationNode]):
        self.uid = uid
        self.forward = forward
        self.backward = backward
        self.parse_strings()
        
    def json(self) -> dict:
        return {
            "uid": self.uid,
            "forward": [node.json() for node in self.forward],
            "backward": [node.json() for node in self.backward]
        }
        
    def calculate_node_data(self, map_data):
        this = map_data.get_node_by_uid(self.uid)
        for node in self.forward:
            map_data.total += 1
            other = map_data.get_node_by_uid(node.node_id)
            if other == this:
                continue
            
            node.item_uid = node_helpers.get_connecting_item_uid(this, other)
            if node.item_uid is None:
                logging.debug(f"Failed to get connecting item UID for nodes {this.uid} and {other.uid}")
                map_data.not_found += 1
                continue
            
            item = map_data.get_item_by_uid(node.item_uid)
            node.item_type = type(item)
            node.lane_indices = node_helpers.get_connecting_lanes_by_item(this, other, item, map_data)
            if node.lane_indices == []:
                map_data.lanes_invalid += 1
        
        for node in self.backward:
            other = map_data.get_node_by_uid(node.node_id)
            node.item_uid = node_helpers.get_connecting_item_uid(this, other)
            if node.item_uid is None:
                logging.debug(f"Failed to get connecting item UID for nodes {this.uid} and {other.uid}")
                map_data.not_found += 1
                continue
            
            item = map_data.get_item_by_uid(node.item_uid)
            node.item_type = type(item)
            node.lane_indices = node_helpers.get_connecting_lanes_by_item(this, other, item, map_data)
            if node.lane_indices == []:
                map_data.lanes_invalid += 1
            

class Node:
    uid: int | str
    x: float
    y: float
    z: float
    rotation: float
    """NOTE: This variable is not to be used. It is only here for compatibility, please use `.euler` instead."""
    rotationQuat: list[float]
    euler: list[float]
    forward_item_uid: int | str
    backward_item_uid: int | str
    sector_x: int
    sector_y: int
    forward_country_id: int | str
    backward_country_id: int | str
    _navigation: NavigationEntry = None

    def parse_strings(self):
        self.uid = parse_string_to_int(self.uid)
        self.forward_item_uid = parse_string_to_int(self.forward_item_uid)
        self.backward_item_uid = parse_string_to_int(self.backward_item_uid)
        self.forward_country_id = parse_string_to_int(self.forward_country_id)
        self.backward_country_id = parse_string_to_int(self.backward_country_id)

    def __init__(self, uid: int | str, x: float, y: float, z: float, rotation: float, rotationQuat: list[float], 
                 forward_item_uid: int | str, backward_item_uid: int | str, sector_x: int, sector_y: int, 
                 forward_country_id: int | str, backward_country_id: int | str):
        self.uid = uid
        
        self.x = x
        self.y = y
        self.z = z
        
        self.rotation = rotation
        self.rotationQuat = rotationQuat
        self.euler = math_helpers.QuatToEuler(rotationQuat)
        
        self.forward_item_uid = forward_item_uid
        self.backward_item_uid = backward_item_uid
        
        self.sector_x = sector_x
        self.sector_y = sector_y
        
        self.forward_country_id = forward_country_id
        self.backward_country_id = backward_country_id
        
        self.parse_strings()
        
    @property
    def navigation(self) -> NavigationEntry:
        if self._navigation is None:
            self._navigation = data.map.get_navigation_entry(self.uid)
        return self._navigation

    def json(self) -> dict:
        return {
            "uid": self.uid,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rotation": self.rotation,
            "forward_item_uid": self.forward_item_uid,
            "backward_item_uid": self.backward_item_uid,
            "sector_x": self.sector_x,
            "sector_y": self.sector_y,
            "forward_country_id": self.forward_country_id,
            "backward_country_id": self.backward_country_id
        }


class Transform:
    x: float
    y: float
    z: float
    rotation: float
    euler: list[float]

    def __init__(self, x: float, y: float, z: float, rotation: float):
        self.x = x
        self.y = y
        self.z = z
        self.rotation = rotation

    def __str__(self) -> str:
        return f"Transform({self.x}, {self.y}, {self.z}, {self.rotation})"

    def __repr__(self) -> str:
        return self.__str__()

    def json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rotation": self.rotation
        }


class Position:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def tuple(self, xz=False) -> tuple[float, float, float]:
        if xz:
            return (self.x, self.z)
        return (self.x, self.y, self.z)

    def list(self) -> list[float]:
        return [self.x, self.y, self.z]

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self) -> str:
        return f"Position({self.x}, {self.y}, {self.z})"

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.z + other.z)

    def json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }


class Point:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def __str__(self) -> str:
        return f"Point({self.x}, {self.y}, {self.z})"

    def __repr__(self) -> str:
        return self.__str__()

    def json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }


class BoundingBox:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def __str__(self) -> str:
        return f"BoundingBox({self.min_x}, {self.min_y}, {self.max_x}, {self.max_y})"

    def to_start_end(self) -> tuple[Position, Position]:
        return Position(self.min_x, self.min_y, 0), Position(self.max_x, self.max_y, 0)

    def to_start_width_height(self) -> tuple[Position, float, float]:
        return Position(self.min_x, self.min_y, 0), self.max_x - self.min_x, self.max_y - self.min_y

    def __repr__(self) -> str:
        return self.__str__()

    def is_in(self, point: Position) -> bool:
        return self.min_x <= point.x <= self.max_x and self.min_y <= point.z <= self.max_y

    def json(self) -> dict:
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y
        }


class BaseItem:
    uid: int | str
    type: ItemType
    x: float
    y: float
    sector_x: int
    sector_y: int

    def parse_strings(self):
        if not str(self.uid).startswith('prefab_'):
            self.uid = parse_string_to_int(self.uid)

    def __init__(self, uid: int | str, type: ItemType, x: float, y: float, sector_x: int, sector_y: int):
        self.uid = uid
        self.type = type
        self.x = x
        self.y = y
        self.sector_x = sector_x
        self.sector_y = sector_y

    def json(self) -> dict:
        return {
            "uid": self.uid,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "sector_x": self.sector_x,
            "sector_y": self.sector_y
        }


class CityArea(BaseItem):
    token: str
    hidden: bool
    width: float
    height: float

    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, token: str, hidden: bool,
                 width: float, height: float):
        super().__init__(uid, ItemType.City, x, y, sector_x, sector_y)
        super().parse_strings()
        self.token = token
        self.hidden = hidden
        self.width = width
        self.height = height

    def json(self) -> dict:
        return {
            **super().json(),
            "token": self.token,
            "hidden": self.hidden,
            "width": self.width,
            "height": self.height
        }


class City:
    token: str
    name: str
    name_localized: str | None
    country_token: str
    population: int
    x: float
    y: float
    areas: list[CityArea]

    def __init__(self, token: str, name: str, name_localized: str | None, country_token: str, population: int, x: float,
                 y: float, areas: list[CityArea]):
        self.token = token
        self.name = name
        self.name_localized = name_localized
        self.country_token = country_token
        self.population = population
        self.x = x
        self.y = y
        self.areas = areas

    def json(self) -> dict:
        return {
            "token": self.token,
            "name": self.name,
            "name_localized": self.name_localized,
            "country_token": self.country_token,
            "population": self.population,
            "x": self.x,
            "y": self.y,
            "areas": [area.json() for area in self.areas]
        }


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

    def json(self) -> dict:
        return {
            "token": self.token,
            "name": self.name,
            "name_localized": self.name_localized,
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "code": self.code
        }


class Company:
    token: str
    name: str
    city_tokens: list[str]
    cargo_in_tokens: list[str]
    cargo_out_tokens: list[str]

    def __init__(self, token: str, name: str, city_tokens: list[str], cargo_in_tokens: list[str],
                 cargo_out_tokens: list[str]):
        self.token = token
        self.name = name
        self.city_tokens = city_tokens
        self.cargo_in_tokens = cargo_in_tokens
        self.cargo_out_tokens = cargo_out_tokens

    def json(self) -> dict:
        return {
            "token": self.token,
            "name": self.name,
            "city_tokens": self.city_tokens,
            "cargo_in_tokens": self.cargo_in_tokens,
            "cargo_out_tokens": self.cargo_out_tokens
        }


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

    def __init__(self, token: str, name: str, name_localized: str | None, x: float, y: float, z: float, price: float,
                 time: float, distance: float, intermediate_points: list[Transform]):
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

    def json(self) -> dict:
        return {
            "token": self.token,
            "name": self.name,
            "name_localized": self.name_localized,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "price": self.price,
            "time": self.time,
            "distance": self.distance,
            "intermediate_points": [point.json() for point in self.intermediate_points]
        }


class Ferry:
    token: str
    train: bool
    name: str
    name_localized: str | None
    x: float
    y: float
    z: float
    connections: list[FerryConnection]

    def __init__(self, token: str, train: bool, name: str, name_localized: str | None, x: float, y: float, z: float,
                 connections: list[FerryConnection]):
        self.token = token
        self.train = train
        self.name = name
        self.name_localized = name_localized
        self.x = x
        self.y = y
        self.z = z
        self.connections = connections

    def json(self) -> dict:
        return {
            "token": self.token,
            "train": self.train,
            "name": self.name,
            "name_localized": self.name_localized,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "connections": [connection.json() for connection in self.connections]
        }


class RoadLook:
    token: str
    name: str
    lanes_left: list[str]
    lanes_right: list[str]
    offset: float | None
    lane_offset: float | None
    shoulder_space_left: float | None
    shoulder_space_right: float | None

    def __init__(self, token: str, name: str, lanes_left: list[str], lanes_right: list[str], offset: float | None,
                 lane_offset: float | None, shoulder_space_left: float | None, shoulder_space_right: float | None):
        self.token = token
        self.name = name
        self.lanes_left = lanes_left
        self.lanes_right = lanes_right
        self.offset = offset
        self.lane_offset = lane_offset
        self.shoulder_space_left = shoulder_space_left
        self.shoulder_space_right = shoulder_space_right

    def json(self) -> dict:
        return {
            "token": self.token,
            "name": self.name,
            "lanes_left": self.lanes_left,
            "lanes_right": self.lanes_right,
            "offset": self.offset,
            "lane_offset": self.lane_offset,
            "shoulder_space_left": self.shoulder_space_left,
            "shoulder_space_right": self.shoulder_space_right
        }
        
    def __str__(self) -> str:
        return f"RoadLook({self.token}, {self.name}, {self.lanes_left}, {self.lanes_right}, {self.offset}, {self.lane_offset}, {self.shoulder_space_left}, {self.shoulder_space_right})"
    
    def __repr__(self) -> str:
        return self.__str__()


class ModelDescription:
    token: str
    center: Position
    start: Position
    end: Position
    height: float
    width: float
    length: float

    def __init__(self, token: str, center: Position, start: Position, end: Position, height: float):
        self.token = token
        self.center = center
        self.start = start
        self.end = end
        self.height = height  # z axis
        self.width = math.sqrt(math.pow(start.x - end.x, 2))  # x axis
        self.length = math.sqrt(math.pow(start.y - end.y, 2))  # y axis

    def json(self) -> dict:
        return {
            "token": self.token,
            "center": self.center.json(),
            "start": self.start.json(),
            "end": self.end.json(),
            "height": self.height,
            "width": self.width,
            "length": self.length
        }


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

    def parse_strings(self):
        self.uid = parse_string_to_int(self.uid)

    def json(self) -> dict:
        return {
            "uid": self.uid,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "sector_x": self.sector_x,
            "sector_y": self.sector_y,
            "icon": self.icon
        }


class GeneralPOI(BasePOI):
    type: NonFacilityPOI
    label: str

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str,
                 label: str):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.label = label

    def json(self) -> dict:
        return {
            **super().json(),
            "type": self.type,
            "label": self.label
        }


class LandmarkPOI(BasePOI):
    label: str
    dlc_guard: int
    node_uid: int | str
    type: NonFacilityPOI = NonFacilityPOI.LANDMARK

    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str,
                 label: str, dlc_guard: int, node_uid: int | str):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.label = label
        self.dlc_guard = dlc_guard
        self.node_uid = node_uid
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "label": self.label,
            "dlc_guard": self.dlc_guard,
            "node_uid": self.node_uid
        }


# This is not elegant but it is the only way to make it work in python  
LabeledPOI = Union[GeneralPOI, LandmarkPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""


class RoadPOI(BasePOI):
    dlc_guard: int
    node_uid: int | str
    type: str = "road"

    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str,
                 dlc_guard: int, node_uid: int | str):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.dlc_guard = dlc_guard
        self.node_uid = node_uid
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "node_uid": self.node_uid
        }


class FacilityPOI(BasePOI):
    icon: FacilityIcon
    prefab_uid: int | str
    prefab_path: str
    type: str = "facility"

    def parse_strings(self):
        self.prefab_uid = parse_string_to_int(self.prefab_uid)

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str,
                 prefab_uid: int | str, prefab_path: str):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.prefab_uid = prefab_uid
        self.prefab_path = prefab_path
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "icon": self.icon,
            "prefab_uid": self.prefab_uid,
            "prefab_path": self.prefab_path
        }


class ParkingPOI(BasePOI):
    dlc_guard: int
    from_item_type: Literal["trigger", "mapOverlay", "prefab"]
    item_node_uids: list[int | str]
    type: str = "facility"
    icon: FacilityIcon = FacilityIcon.PARKING

    def parse_strings(self):
        self.item_node_uids = [parse_string_to_int(node) for node in self.item_node_uids]

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, icon: str,
                 dlc_guard: int, from_item_type: Literal["trigger", "mapOverlay", "prefab"],
                 item_node_uids: list[int | str]):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.dlc_guard = dlc_guard
        self.from_item_type = from_item_type
        self.item_node_uids = item_node_uids
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "from_item_type": self.from_item_type,
            "item_node_uids": self.item_node_uids
        }


UnlabeledPOI = Union[RoadPOI, FacilityPOI, ParkingPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""
POI = Union[LabeledPOI, UnlabeledPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""


# MARK: Map Items

class Lane:
    points: list[Position]
    side: Literal["left", "right"]
    length: float = 0

    def __init__(self, points: list[Position], side: Literal["left", "right"]):
        self.points = points
        self.side = side
        self.length = self.calculate_length()

    def calculate_length(self) -> float:
        length = 0
        for i in range(len(self.points) - 1):
            length += math.sqrt(
                math.pow(self.points[i].x - self.points[i + 1].x, 2) + math.pow(self.points[i].z - self.points[i + 1].z,
                                                                                2))
        return length

    def json(self) -> dict:
        return {
            "points": [point.json() for point in self.points],
            "side": self.side,
            "length": self.length
        }


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

    _bounding_box: BoundingBox = None
    _lanes: list[Lane] = []
    _points: list[Position] = None

    def parse_strings(self):
        # Only parse UIDs if they don't contain 'prefab_' prefix
        if not str(self.uid).startswith('prefab_'):
            self.start_node_uid = parse_string_to_int(self.start_node_uid)
            self.end_node_uid = parse_string_to_int(self.end_node_uid)

    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, dlc_guard: int,
                 hidden: bool | None, road_look_token: str, start_node_uid: int | str, end_node_uid: int | str,
                 length: float, maybe_divided: bool | None):
        super().__init__(uid, ItemType.Road, x, y, sector_x, sector_y)
        super().parse_strings()
        # Ensure dlc_guard is an integer and hidden is a boolean
        self.dlc_guard = int(dlc_guard) if dlc_guard is not None else -1
        self.hidden = bool(hidden) if hidden is not None else False
        self.road_look_token = road_look_token
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
        self.length = length
        self.maybe_divided = maybe_divided
        self._lanes = []
        self._points = None
        self.start_node = None
        self.end_node = None
        self.parse_strings()

    def get_nodes(self):
        """Populate start_node and end_node if not already set."""
        try:
            if not hasattr(self, 'start_node_uid') or not hasattr(self, 'end_node_uid'):
                logging.error(f"Road {self.uid} missing node UIDs")
                return None, None

            if self.start_node is None:
                self.start_node = data.map.get_node_by_uid(self.start_node_uid)
            if self.end_node is None:
                self.end_node = data.map.get_node_by_uid(self.end_node_uid)

            if self.start_node is None or self.end_node is None:
                logging.error(f"Road {self.uid} failed to get nodes")
                return None, None

            return self.start_node, self.end_node
        except Exception as e:
            logging.error(f"Error getting nodes for road {self.uid}: {e}")
            return None, None

    def generate_points(self, road_quality: float = 0.5, min_quality: int = 4) -> list[Position]:
        try:
            # Get nodes using the existing method
            start_node, end_node = self.get_nodes()
            if not start_node or not end_node:
                logging.error(f"Failed to get nodes for road {self.uid}")
                return []
    
            new_points = []
    
            # Create position tuples in proper order (x,y,z)
            start_pos = (start_node.x, start_node.z, start_node.y)
            end_pos = (end_node.x, end_node.z, end_node.y)
    
            # Get euler angles from nodes
            start_euler = start_node.euler if hasattr(start_node, 'euler') else (0, 0, 0)
            end_euler = end_node.euler if hasattr(end_node, 'euler') else (0, 0, 0)
    
            # Calculate needed points based on length
            length = math.sqrt(sum((e - s) ** 2 for s, e in zip(start_pos, end_pos)))
            needed_points = max(int(length * road_quality), min_quality)
    
            # Generate points using Hermite3D
            for i in range(needed_points):
                s = i / (needed_points - 1)
                x, y, z = math_helpers.Hermite3D(s, start_pos, end_pos, start_euler, end_euler)
                new_points.append(Position(x, y, z))
    
            return new_points
        except Exception as e:
            logging.exception(f"Error generating points for road {self.uid}: {e}")
            return []

    @property
    def points(self) -> list[Position]:
        if self._points is None:
            self._points = self.generate_points()
            data.heavy_calculations_this_frame += 1

        return self._points

    @points.setter
    def points(self, value: list[Position]):
        self._points = value

    @property
    def lanes(self) -> list[Lane]:
        if self._lanes == []:
            self._lanes, self._bounding_box = road_helpers.GetRoadLanes(self, data)
            data.heavy_calculations_this_frame += 1
            data.data_needs_update = True

        return self._lanes

    @lanes.setter
    def lanes(self, value: list[Lane]):
        self._lanes = value

    @property
    def bounding_box(self) -> BoundingBox:
        if self._bounding_box is None:
            if data.heavy_calculations_this_frame >= data.allowed_heavy_calculations:
                return BoundingBox(0, 0, 0, 0)
            self._lanes, self._bounding_box = road_helpers.GetRoadLanes(self, data)
            data.heavy_calculations_this_frame += 1
            data.data_needs_update = True

        return self._bounding_box

    @bounding_box.setter
    def bounding_box(self, value: BoundingBox):
        self._bounding_box = value

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "hidden": self.hidden,
            "road_look": self.road_look.json(),
            "start_node_uid": self.start_node_uid,
            "end_node_uid": self.end_node_uid,
            "length": self.length,
            "maybe_divided": self.maybe_divided,
            "points": [point.json() for point in self.points],
            "lanes": [lane.json() for lane in self.lanes],
            "bounding_box": self.bounding_box.json()
        }


class MapArea(BaseItem):
    dlc_guard: int
    draw_over: bool | None
    node_uids: list[int | str]
    color: MapColor
    type: ItemType = ItemType.MapArea

    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]

    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, dlc_guard: int,
                 draw_over: bool | None, node_uids: list[int | str], color: MapColor):
        super().__init__(uid, ItemType.MapArea, x, y, sector_x, sector_y)
        self.dlc_guard = dlc_guard
        self.draw_over = draw_over
        self.node_uids = node_uids
        self.color = color
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "draw_over": self.draw_over,
            "node_uids": self.node_uids,
            "color": self.color
        }


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

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, dlc_guard: int,
                 overlay_type: MapOverlayType, token: str, node_uid: int | str):
        super().__init__(uid, ItemType.MapOverlay, x, y, z, sector_x, sector_y)
        self.dlc_guard = dlc_guard
        self.overlay_type = overlay_type
        self.token = token
        self.node_uid = node_uid

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "overlay_type": self.overlay_type,
            "token": self.token,
            "node_uid": self.node_uid
        }


class Building(BaseItem):
    scheme: str
    start_node_uid: int | str
    end_node_uid: int | str
    type: ItemType = ItemType.Building

    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, scheme: str,
                 start_node_uid: int | str, end_node_uid: int | str):
        super().__init__(uid, ItemType.Building, x, y, z, sector_x, sector_y)
        self.scheme = scheme
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid

    def json(self) -> dict:
        return {
            **super().json(),
            "scheme": self.scheme,
            "start_node_uid": self.start_node_uid,
            "end_node_uid": self.end_node_uid
        }


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

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, model: str,
                 look: str, num_buildings: int, start_node_uid: int | str, end_node_uid: int | str):
        super().__init__(uid, ItemType.Curve, x, y, z, sector_x, sector_y)
        self.model = model
        self.look = look
        self.num_buildings = num_buildings
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid

    def json(self) -> dict:
        return {
            **super().json(),
            "model": self.model,
            "look": self.look,
            "num_buildings": self.num_buildings,
            "start_node_uid": self.start_node_uid,
            "end_node_uid": self.end_node_uid
        }


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

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, token: str,
                 train: bool, prefab_uid: int | str, node_uid: int | str):
        super().__init__(uid, ItemType.Ferry, x, y, z, sector_x, sector_y)
        self.token = token
        self.train = train
        self.prefab_uid = prefab_uid
        self.node_uid = node_uid

    def json(self) -> dict:
        return {
            **super().json(),
            "token": self.token,
            "train": self.train,
            "prefab_uid": self.prefab_uid,
            "node_uid": self.node_uid
        }


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

    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, token: str, city_token: str,
                 prefab_uid: int | str, node_uid: int | str):
        super().__init__(uid, ItemType.Company, x, y, sector_x, sector_y)
        self.token = token
        self.city_token = city_token
        self.prefab_uid = prefab_uid
        self.node_uid = node_uid

    def json(self) -> dict:
        return {
            **super().json(),
            "token": self.token,
            "city_token": self.city_token,
            "prefab_uid": self.prefab_uid,
            "node_uid": self.node_uid
        }


class Cutscene(BaseItem):
    flags: int
    tags: list[str]
    node_uid: int | str
    type: ItemType = ItemType.Cutscene

    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, flags: int,
                 tags: list[str], node_uid: int | str):
        super().__init__(uid, ItemType.Cutscene, x, y, z, sector_x, sector_y)
        self.flags = flags
        self.tags = tags
        self.node_uid = node_uid

    def json(self) -> dict:
        return {
            **super().json(),
            "flags": self.flags,
            "tags": self.tags,
            "node_uid": self.node_uid
        }


class Trigger(BaseItem):
    dlc_guard: int
    action_tokens: list[str]
    node_uids: list[int | str]
    type: ItemType = ItemType.Trigger

    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, dlc_guard: int,
                 action_tokens: list[str], node_uids: list[int | str]):
        super().__init__(uid, ItemType.Trigger, x, y, z, sector_x, sector_y)
        self.dlc_guard = dlc_guard
        self.action_tokens = action_tokens
        self.node_uids = node_uids

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "action_tokens": self.action_tokens,
            "node_uids": self.node_uids
        }


class Model(BaseItem):
    token: str
    node_uid: int | str
    scale: tuple[float, float, float]
    type: ItemType = ItemType.Model
    vertices: list[Position] = []
    description: ModelDescription = None
    z: float = math.inf
    rotation: float = 0

    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(self, uid: int | str, x: float, y: float, sector_x: int, sector_y: int, token: str,
                 node_uid: int | str, scale: tuple[float, float, float]):
        super().__init__(uid, ItemType.Model, x, y, sector_x, sector_y)
        self.token = token
        self.node_uid = node_uid
        self.scale = scale

    def json(self) -> dict:
        node = data.map.get_node_by_uid(self.node_uid)
        if self.z == math.inf:
            self.x = node.x
            self.y = node.z
            self.z = node.y
        self.rotation = node.rotation
        self.description = data.map.get_model_description_by_token(self.token)
        return {
            **super().json(),
            "z": self.z,
            "rotation": self.rotation,
            "token": self.token,
            "node_uid": self.node_uid,
            "scale": self.scale,
            "description": self.description.json(),
        }





class Terrain(BaseItem):
    start_node_uid: int | str
    end_node_uid: int | str
    length: float
    type: ItemType = ItemType.Terrain

    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int,
                 start_node_uid: int | str, end_node_uid: int | str, length: float):
        super().__init__(uid, ItemType.Terrain, x, y, z, sector_x, sector_y)
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
        self.length = length

    def json(self) -> dict:
        return {
            **super().json(),
            "start_node_uid": self.start_node_uid,
            "end_node_uid": self.end_node_uid,
            "length": self.length
        }


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

    def json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "neighbors": self.neighbors
        }


class NavNode:
    node0: bool
    node1: bool
    node2: bool
    node3: bool
    node4: bool
    node5: bool
    node6: bool
    node_custom: bool

    def __init__(self, node0: bool, node1: bool, node2: bool, node3: bool, node4: bool, node5: bool, node6: bool,
                 node_custom: bool):
        self.node0 = node0
        self.node1 = node1
        self.node2 = node2
        self.node3 = node3
        self.node4 = node4
        self.node5 = node5
        self.node6 = node6
        self.node_custom = node_custom

    def json(self) -> dict:
        return {
            "node0": self.node0,
            "node1": self.node1,
            "node2": self.node2,
            "node3": self.node3,
            "node4": self.node4,
            "node5": self.node5,
            "node6": self.node6,
            "node_custom": self.node_custom
        }


class NavFlags:
    is_start: bool
    is_base: bool
    is_end: bool

    def __init__(self, is_start: bool, is_base: bool, is_end: bool):
        self.is_start = is_start
        self.is_base = is_base
        self.is_end = is_end

    def json(self) -> dict:
        return {
            "is_start": self.is_start,
            "is_base": self.is_base,
            "is_end": self.is_end
        }


class RoadMapPoint(BaseMapPoint):
    lanes_left: int | Literal["auto"]
    lanes_right: int | Literal["auto"]
    offset: float
    nav_node: NavNode
    nav_flags: NavFlags
    type: str = "road"

    def __init__(self, x: float, y: float, z: float, neighbors: list[int | str], lanes_left: int | Literal["auto"],
                 lanes_right: int | Literal["auto"], offset: float, nav_node: NavNode, nav_flags: NavFlags):
        super().__init__(x, y, z, neighbors)
        self.lanes_left = lanes_left
        self.lanes_right = lanes_right
        self.offset = offset
        self.nav_node = nav_node
        self.nav_flags = nav_flags

    def json(self) -> dict:
        return {
            **super().json(),
            "lanes_left": self.lanes_left,
            "lanes_right": self.lanes_right,
            "offset": self.offset,
            "nav_node": self.nav_node.json(),
            "nav_flags": self.nav_flags.json()
        }


class PolygonMapPoint(BaseMapPoint):
    color: MapColor
    road_over: bool
    type: str = "polygon"

    def __init__(self, x: float, y: float, z: float, neighbors: list[int | str], color: MapColor, road_over: bool):
        super().__init__(x, y, z, neighbors)
        self.color = color
        self.road_over = road_over

    def json(self) -> dict:
        return {
            **super().json(),
            "color": self.color,
            "road_over": self.road_over
        }


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

    def json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rotation": self.rotation,
            "input_lanes": self.input_lanes,
            "output_lanes": self.output_lanes
        }


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

    def json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "type": self.type
        }


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

    def json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "action": self.action
        }


class PrefabNavCurve:
    nav_node_index: int
    start: Transform
    end: Transform
    next_lines: list[int]
    prev_lines: list[int]
    points: list[Position] = []

    def __init__(self, nav_node_index: int, start: Transform, end: Transform, next_lines: list[int],
                 prev_lines: list[int], points: list[Position] = []):
        self.nav_node_index = nav_node_index
        self.start = start
        self.end = end
        self.next_lines = next_lines
        self.prev_lines = prev_lines
        if points != []:
            self.points = points
        else:
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

    def convert_to_relative(self, origin_node: Node, map_point_origin: PrefabNode):
        prefab_start_x = origin_node.x - map_point_origin.x
        prefab_start_y = origin_node.z - map_point_origin.z
        prefab_start_z = origin_node.y - map_point_origin.y

        rot = float(origin_node.rotation - map_point_origin.rotation)

        new_start_pos = math_helpers.RotateAroundPoint(self.start.x + prefab_start_x, self.start.z + prefab_start_z,
                                                       rot, origin_node.x, origin_node.y)
        new_start = Transform(new_start_pos[0], self.start.y + prefab_start_y, new_start_pos[1],
                              self.start.rotation + rot)

        new_end_pos = math_helpers.RotateAroundPoint(self.end.x + prefab_start_x, self.end.z + prefab_start_z, rot,
                                                     origin_node.x, origin_node.y)
        new_end = Transform(new_end_pos[0], self.end.y + prefab_start_y, new_end_pos[1], self.end.rotation + rot)

        new_points = []
        for point in self.points:
            new_point_pos = math_helpers.RotateAroundPoint(point.x + prefab_start_x, point.z + prefab_start_z, rot,
                                                           origin_node.x, origin_node.y)
            new_points.append(Position(new_point_pos[0], point.y + prefab_start_y, new_point_pos[1]))

        return PrefabNavCurve(self.nav_node_index, new_start, new_end, self.next_lines, self.prev_lines,
                              points=new_points)

    def json(self) -> dict:
        return {
            "nav_node_index": self.nav_node_index,
            "start": self.start.json(),
            "end": self.end.json(),
            "next_lines": self.next_lines,
            "prev_lines": self.prev_lines,
            "points": [point.json() for point in self.points]
        }


class NavNodeConnection:
    target_nav_node_index: int
    curve_indeces: list[int]

    def __init__(self, target_nav_node_index: int, curve_indeces: list[int]):
        self.target_nav_node_index = target_nav_node_index
        self.curve_indeces = curve_indeces

    def json(self) -> dict:
        return {
            "target_nav_node_index": self.target_nav_node_index,
            "curve_indeces": self.curve_indeces
        }


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

    def json(self) -> dict:
        return {
            "type": self.type,
            "end_index": self.end_index,
            "connections": [connection.json() for connection in self.connections]
        }


class PrefabNavRoute:
    curves: list[PrefabNavCurve]
    distance: float = 0
    _points: list[Position] = []

    def __init__(self, curves: list[PrefabNavCurve]):
        self.curves = curves
        
    @property
    def points(self):
        if self._points == []:
            self._points = self.generate_points()
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    def generate_points(self) -> list[Position]:
        new_points = []
        for curve in self.curves:
            new_points += curve.points

        min_distance = 0.25
        last_point = new_points[0]
        accepted_points = [new_points[0]]
        for point in new_points:
            if math_helpers.DistanceBetweenPoints(point.tuple(), last_point.tuple()) > min_distance:
                accepted_points.append(point)
                last_point = point

        new_points = accepted_points

        distance = 0
        for i in range(len(new_points) - 1):
            distance += math.sqrt(
                math.pow(new_points[i].x - new_points[i + 1].x, 2) + math.pow(new_points[i].z - new_points[i + 1].z, 2))
        self.distance = distance

        return new_points

    def generate_relative_curves(self, origin_node: Node, map_point_origin: PrefabNode) -> list[PrefabNavCurve]:
        new_curves = []
        for curve in self.curves:
            new_curves.append(curve.convert_to_relative(origin_node, map_point_origin))
        return new_curves

    def json(self) -> dict:
        return {
            "curves": [curve.json() for curve in self.curves],
            "points": [point.json() for point in self.points],
            "distance": self.distance
        }


class PrefabDescription:
    token: str
    nodes: list[PrefabNode]
    map_points: RoadMapPoint | PolygonMapPoint
    spawn_points: list[PrefabSpawnPoints]
    trigger_points: list[PrefabTriggerPoint]
    nav_curves: list[PrefabNavCurve]
    nav_nodes: list[PrefabNavNode]
    _nav_routes: list[PrefabNavRoute] = []

    def __init__(self, token: str, nodes: list[PrefabNode], map_points: RoadMapPoint | PolygonMapPoint,
                 spawn_points: list[PrefabSpawnPoints], trigger_points: list[PrefabTriggerPoint],
                 nav_curves: list[PrefabNavCurve], nav_nodes: list[NavNode]):
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

    def json(self) -> dict:
        return {
            "token": self.token,
            "nodes": [node.json() for node in self.nodes],
            "map_points": self.map_points.json(),
            "spawn_points": [spawn.json() for spawn in self.spawn_points],
            "trigger_points": [trigger.json() for trigger in self.trigger_points],
            "nav_curves": [curve.json() for curve in self.nav_curves],
            "nav_nodes": [node.json() for node in self.nav_nodes],
            "nav_routes": [route.json() for route in self.nav_routes]
        }


class Prefab(BaseItem):
    dlc_guard: int
    hidden: bool | None
    token: str
    node_uids: list[int | str]
    origin_node_index: int
    type: ItemType = ItemType.Prefab
    prefab_description: PrefabDescription = None
    z: float = 0
    _nav_routes: list[PrefabNavRoute] = []
    _bounding_box: BoundingBox = None

    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]

    def __init__(self, uid: int | str, x: float, y: float, z: float, sector_x: int, sector_y: int, dlc_guard: int,
                 hidden: bool | None, token: str, node_uids: list[int | str], origin_node_index: int):
        super().__init__(uid, ItemType.Prefab, x, y, sector_x, sector_y)
        self.z = z
        self.dlc_guard = dlc_guard
        self.hidden = hidden
        self.token = token
        self.node_uids = node_uids
        self.origin_node_index = origin_node_index
        self.parse_strings()

    def build_nav_routes(self):
        self._nav_routes = []
        for route in self.prefab_description.nav_routes:
            self._nav_routes.append(PrefabNavRoute(
                route.generate_relative_curves(data.map.get_node_by_uid(self.node_uids[0]),
                                               self.prefab_description.nodes[self.origin_node_index])
            ))

        for route in self._nav_routes:
            route.generate_points()

    @property
    def nav_routes(self) -> list[PrefabNavRoute]:
        """The prefab description also has nav routes, but this nav route list has the correct world space positions."""
        if self._nav_routes == []:
            self.build_nav_routes()

        return self._nav_routes

    @nav_routes.setter
    def nav_routes(self, value: list[PrefabNavRoute]):
        self._nav_routes = value

    @property
    def bounding_box(self) -> BoundingBox:
        if self._bounding_box is None:
            min_x = math.inf
            max_x = -math.inf
            min_y = math.inf
            max_y = -math.inf
            for route in self.nav_routes:
                for point in route.points:
                    if point.x < min_x:
                        min_x = point.x
                    if point.x > max_x:
                        max_x = point.x
                    if point.z < min_y:
                        min_y = point.z
                    if point.z > max_y:
                        max_y = point.z

            if min_x == math.inf:
                min_x = 0
            if max_x == -math.inf:
                max_x = 0
            if min_y == math.inf:
                min_y = 0
            if max_y == -math.inf:
                max_y = 0

            self._bounding_box = BoundingBox(min_x - 5, min_y - 5, max_x + 5, max_y + 5)

        return self._bounding_box

    @bounding_box.setter
    def bounding_box(self, value: BoundingBox):
        self._bounding_box = value

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "hidden": self.hidden,
            "token": self.token,
            "node_uids": self.node_uids,
            "origin_node_index": self.origin_node_index,
            "nav_routes": [route.json() for route in self.nav_routes],
            "bounding_box": self.bounding_box.json()
        }


Item = Union[
    City, Country, Company, Ferry, POI, Road, Prefab, MapArea, MapOverlay, Building, Curve, FerryItem, CompanyItem, Cutscene, Trigger, Model, Terrain]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""


# MARK: MapData
class MapData:
    nodes: list[Node]
    """List of all nodes in the currently loaded map data."""
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
    navigation: list[NavigationEntry]

    _nodes_by_sector: dict[dict[Node]]
    _roads_by_sector: dict[dict[Road]]
    _prefabs_by_sector: dict[dict[Prefab]]
    _models_by_sector: dict[dict[Model]]

    _min_sector_x: int = math.inf
    _max_sector_x: int = -math.inf
    _min_sector_y: int = math.inf
    _max_sector_y: int = -math.inf
    _sector_width: int = 200
    _sector_height: int = 200

    _by_uid = {}
    _model_descriptions_by_token = {}
    _prefab_descriptions_by_token = {}
    _companies_by_token = {}
    _navigation_by_node_uid = {}
    """
    Nested nodes dictionary for quick access to nodes by their UID. UID is split into 4 character strings to index into the nested dictionaries.
    Please use the get_node_by_uid method to access nodes by UID.
    """
    
    def calculate_sectors(self) -> None:
        for node in self.nodes:
            node.sector_x, node.sector_y = self.get_sector_from_coordinates(node.x, node.y)
        # elevevations don't have sectors
        for road in self.roads:
            road.sector_x, road.sector_y = self.get_sector_from_coordinates(road.x, road.y)
        # ferries don't have sectors
        for prefab in self.prefabs:
            prefab.sector_x, prefab.sector_y = self.get_sector_from_coordinates(prefab.x, prefab.y)
        for company in self.companies:
            company.sector_x, company.sector_y = self.get_sector_from_coordinates(company.x, company.y)
        for model in self.models:
            model.sector_x, model.sector_y = self.get_sector_from_coordinates(model.x, model.y)
        for area in self.map_areas:
            area.sector_x, area.sector_y = self.get_sector_from_coordinates(area.x, area.y)
        for poi in self.POIs:
            poi.sector_x, poi.sector_y = self.get_sector_from_coordinates(poi.x, poi.y)
        # dividers are not yet being loaded
        # countries don't have sectors
        # cities don't have sectors
        # company_defs don't have sectors
        # road_looks don't have sectors
        # prefab_descriptions don't have sectors
        # model_descriptions don't have sectors

    def sort_to_sectors(self) -> None:
        self._nodes_by_sector = {}
        self._roads_by_sector = {}
        self._prefabs_by_sector = {}
        self._models_by_sector = {}

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

        for model in self.models:
            sector = (model.sector_x, model.sector_y)
            if sector[0] not in self._models_by_sector:
                self._models_by_sector[sector[0]] = {}
            if sector[1] not in self._models_by_sector[sector[0]]:
                self._models_by_sector[sector[0]][sector[1]] = []
            self._models_by_sector[sector[0]][sector[1]].append(model)

    def get_node_by_uid(self, uid: str) -> Optional[Node]:
        """Get a node by its UID."""
        # Convert int to hex string if needed
        if isinstance(uid, int):
            uid = hex(uid)[2:]  # Remove '0x' prefix

        # Search through nodes
        for node in self.nodes:
            if node.uid == uid:
                return node
        return None

    def calculate_sector_dimensions(self) -> None:
        min_sector_x = self._min_sector_x
        min_sector_x_y = min([key for key in self._nodes_by_sector[min_sector_x].keys()])
        min_sector_y = self._min_sector_y
        min_sector_y_x = min([key if min_sector_y in self._nodes_by_sector[key].keys() else math.inf for key in
                              self._nodes_by_sector.keys()])
        min_x = min([node.x for node in self._nodes_by_sector[min_sector_x][min_sector_x_y]])
        min_y = min([node.y for node in self._nodes_by_sector[min_sector_y_x][min_sector_y]])

        max_sector_x = self._max_sector_x
        max_sector_x_y = max([key for key in self._nodes_by_sector[max_sector_x].keys()])
        max_sector_y = self._max_sector_y
        max_sector_y_x = max([key if max_sector_y in self._nodes_by_sector[key].keys() else -math.inf for key in
                              self._nodes_by_sector.keys()])
        max_x = max([node.x for node in self._nodes_by_sector[max_sector_x][max_sector_x_y]])
        max_y = max([node.y for node in self._nodes_by_sector[max_sector_y_x][max_sector_y]])

        self._sector_width = (max_x - min_x) / (max_sector_x - min_sector_x)
        self._sector_height = (max_y - min_y) / (max_sector_y - min_sector_y)

    def build_dictionary(self) -> None:
        self._by_uid = {}
        items = self.nodes + self.roads + self.prefabs + self.models
        for item in items:
            uid_str = str(item.uid)
            parts = [uid_str]
            #parts = [uid_str[i:i + 4] for i in range(0, len(uid_str), 4)]
            set_nested_item(self._by_uid, parts, item)

        self._model_descriptions_by_token = {}
        for model_description in self.model_descriptions:
            self._model_descriptions_by_token[model_description.token] = model_description

        self._prefab_descriptions_by_token = {}
        for prefab_description in self.prefab_descriptions:
            self._prefab_descriptions_by_token[prefab_description.token] = prefab_description

        self._companies_by_token = {}
        for company in self.companies:
            self._companies_by_token[company.token] = company
            
        self._navigation_by_node_uid = {}
        for nav in self.navigation:
            self._navigation_by_node_uid[nav.uid] = nav

    def get_node_navigation(self, uid: str) -> NavigationEntry:
        return self._navigation_by_node_uid.get(uid, None)

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

    def get_sector_items_by_sector(self, sector: tuple[int, int]) -> list[Item]:
        items = []
        items += self._prefabs_by_sector.get(sector[0], {}).get(sector[1], [])
        items += self._roads_by_sector.get(sector[0], {}).get(sector[1], [])
        return items

    def get_sector_items_by_coordinates(self, x: float, z: float) -> list[Item]:
        sector = self.get_sector_from_coordinates(x, z)
        return self.get_sector_items_by_sector(sector)

    def get_sector_models_by_coordinates(self, x: float, z: float) -> list[Model]:
        sector = self.get_sector_from_coordinates(x, z)
        return self.get_sector_models_by_sector(sector)

    def get_sector_models_by_sector(self, sector: tuple[int, int]) -> list[Model]:
        return self._models_by_sector.get(sector[0], {}).get(sector[1], [])

    def get_node_by_uid(self, uid: int | str) -> Node | None:
        try:
            if type(uid) == str:
                uid = parse_string_to_int(uid)

            uid_str = str(uid)
            parts = [uid_str]
            #parts = [uid_str[i:i + 4] for i in range(0, len(uid_str), 4)]
            return get_nested_item(self._by_uid, parts)
        except:
            return None

    def get_item_by_uid(self, uid: int | str) -> Prefab | Road:
        try:
            if type(uid) == str:
                uid = parse_string_to_int(uid)
            if uid == 0:
                return None
            if uid is None:
                return None

            uid_str = str(uid)
            parts = [uid_str]
            #parts = [uid_str[i:i + 4] for i in range(0, len(uid_str), 4)]
            return get_nested_item(self._by_uid, parts)
        except:
            logging.warning(f"Error getting item by UID: {uid}")
            #logging.exception(f"Error getting item by UID: {uid}")
            return None

    def get_company_item_by_token_and_city(self, token: str, city_token: str) -> CompanyItem:
        # TODO: Optimize this, use the dictionary and add the companies as a list based on the token
        return_item = None
        for company in self.companies:
            if company.token == token and company.city_token == city_token:
                return_item = company
                break
        return return_item

    def get_model_description_by_token(self, token: str) -> ModelDescription:
        return self._model_descriptions_by_token.get(token, None)

    def get_city_by_token(self, token: str) -> City:
        for city in self.cities:
            if city.token == token:
                return city
        return None

    def match_roads_to_looks(self) -> None:
        for road in self.roads:
            for look in self.road_looks:
                if road.road_look_token == look.token:
                    road.road_look = look
                    break

    def match_prefabs_to_descriptions(self) -> None:
        for prefab in self.prefabs:
            prefab.prefab_description = self._prefab_descriptions_by_token.get(prefab.token, None)
                
    def get_sectors_for_coordinate_and_distance(self, x: float, z: float, distance: float) -> list[tuple[int, int]]:
        sectors = []
        range_x = int(distance // self._sector_width)
        range_z = int(distance // self._sector_height)
        
        for i in range(-range_x, range_x + 1):
            for j in range(-range_z, range_z + 1):
                sector_x = int(x // self._sector_width) + i
                sector_z = int(z // self._sector_height) + j
                sectors.append((sector_x, sector_z))
        
        return sectors
    
    def get_closest_item(self, x: float, z: float) -> Item:
        # TODO: Use actual points instead of just the item position
        in_bounding_box = []
        items: list[Prefab | Road] = []
        sectors = self.get_sectors_for_coordinate_and_distance(x, z, data.load_distance)
        if sectors == data.current_sectors:
            items += data.current_sector_prefabs
            items += data.current_sector_roads
        else:
            for sector in sectors:
                items += self.get_sector_items_by_sector(sector)

            for item in items:
                if type(item) in [Road, Prefab]:
                    if item.bounding_box.is_in(Position(x, 0, z)):
                        in_bounding_box.append(item)

        if len(in_bounding_box) == 0:
            # Check all
            in_bounding_box = [item for item in items if type(item) in [Road, Prefab]]

        closest_item = None
        closest_point_distance = math.inf
        for item in in_bounding_box:
            if type(item) == Prefab:
                for lane_id, lane in enumerate(item.nav_routes):
                    for point in lane.points:
                        point_tuple = point.tuple()
                        point_tuple = (point_tuple[0], point_tuple[2])
                        distance = math_helpers.DistanceBetweenPoints((x, z), point_tuple)
                        if distance < closest_point_distance:
                            closest_point_distance = distance
                            closest_item = item

            elif type(item) == Road:
                # Initialize lanes if not already done
                if not hasattr(item, '_lanes'):
                    item._lanes = []
                if not item.lanes:  # If lanes list is empty, generate points
                    item.generate_points()
                for lane_id, lane in enumerate(item.lanes):
                    for point in lane.points:
                        point_tuple = point.tuple()
                        point_tuple = (point_tuple[0], point_tuple[2])
                        distance = math_helpers.DistanceBetweenPoints((x, z), point_tuple)
                        if distance < closest_point_distance:
                            closest_point_distance = distance
                            closest_item = item

        if closest_item == None:
            return None

        return closest_item

    def get_road_between_nodes(self, start_node_uid: int | str, end_node_uid: int | str) -> Road | None:
        """Get a road that connects two nodes, initializing its nodes if found."""
        start_node = self.get_node_by_uid(start_node_uid)
        sectors = self.get_sectors_for_coordinate_and_distance(start_node.x, start_node.y, 500)
        items = []
        for sector in sectors:
            items += self.get_sector_items_by_sector(sector)
        
        for road in items:
            if type(road) == Road:
                if (road.start_node_uid == start_node_uid and road.end_node_uid == end_node_uid) or \
                   (road.start_node_uid == end_node_uid and road.end_node_uid == start_node_uid):
                    road.get_nodes()  # Initialize nodes
                    return road
        return None

    total = 0
    not_found = 0
    lanes_invalid = 0
    def compute_navigation_data(self):
        amount = len(self.navigation)
        count = 0
        for node in self.navigation:
            node.calculate_node_data(self)
            if count % 100 == 0:
                print(f"Processed {count}/{amount} nodes ({count / amount * 100:.2f}%)", end="\r")
            count += 1
        
        print(f"> Item missing: {self.not_found} ({self.not_found / self.total * 100:.2f}%)")
        print(f"> Lanes empty: {self.lanes_invalid} ({self.lanes_invalid / self.total * 100:.2f}%)")
        print(f"> Successful: {self.total - self.not_found - self.lanes_invalid} ({(self.total - self.not_found - self.lanes_invalid) / self.total * 100:.2f}%)")