"""Map plugin classes."""

from typing import Union, Literal, Any
from enum import Enum, StrEnum, IntEnum
import logging
import math
import time
import json

# Import dictionary utilities with fallback to mocks for testing
import ETS2LA.variables as variables
from Plugins.Map.settings import settings

from Plugins.Map.utils import prefab_helpers
from Plugins.Map.utils import math_helpers
from Plugins.Map.utils import road_helpers
from Plugins.Map.utils import node_helpers

import psutil

# MARK: Constants

data = None
"""The data object that is used by classes here. Will be set once the MapData object is created and loaded."""
auto_tolls = settings.AutoTolls
point_multiplier = settings.RoadQualityMultiplier


def settings_changed():
    global auto_tolls, point_multiplier
    auto_tolls = settings.AutoTolls
    point_multiplier = settings.RoadQualityMultiplier


settings.listen(settings_changed)


def parse_string_to_int(string: str) -> int:
    if string is None:
        return None
    if isinstance(string, int):
        return string
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


DarkColors: list[tuple[int, int, int]] = [
    (233, 235, 236),
    (230, 203, 158),
    (216, 166, 79),
    (177, 202, 155),
]

LightColors: list[tuple[int, int, int]] = [
    (90, 92, 94),
    (112, 95, 67),
    (80, 68, 48),
    (51, 77, 61),
]


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
    ShadowMap = 10
    NoWeather = 11
    City = 12
    Hinge = 13
    Parking = 14
    AnimatedModel = 15
    Hq = 16
    Lock = 17
    MapOverlay = 18
    Ferry = 19
    MissionPoint = 20
    Sound = 21
    Garage = 22
    CameraPoint = 23
    ParkingPoint = 24
    FixedCar = 25
    TrailerStart = 26
    TruckStart = 27
    Walker = 28
    YetdFinish = 29
    YetdTriplet = 30
    YetdFixable = 31
    YetdBall = 32
    YetdRod = 33
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
    NONE = (0,)
    TrailerPos = (1,)
    UnloadEasyPos = (2,)
    GasPos = (3,)
    ServicePos = (4,)
    TruckStopPos = (5,)
    WeightStationPos = (6,)
    TruckDealerPos = (7,)
    Hotel = (8,)
    Custom = (9,)
    Parking = (10,)  # also shows parking in companies which don't work/show up in game
    Task = (11,)
    MeetPos = (12,)
    CompanyPos = (13,)
    GaragePos = (14,)  # manage garage
    BuyPos = (15,)  # buy garage
    RecruitmentPos = (16,)
    CameraPoint = (17,)
    BusStation = (18,)
    UnloadMediumPos = (19,)
    UnloadHardPos = (20,)
    UnloadRigidPos = (21,)
    WeightCatPos = (22,)
    CompanyUnloadPos = (23,)
    TrailerSpawn = (24,)
    LongTrailerPos = (25,)


# MARK: Base Classes


class NavigationNode:
    __slots__ = [
        "node_id",
        "distance",
        "direction",
        "is_one_lane_road",
        "dlc_guard",
        "item_uid",
        "item_type",
        "lane_indices",
    ]

    node_id: str
    distance: float
    direction: Literal["forward", "backward"]
    is_one_lane_road: bool
    dlc_guard: int
    item_uid: str
    item_type: Any
    lane_indices: list[int]
    """This is a list of the lane indices that go through this navigation node."""

    def parse_strings(self):
        self.node_id = parse_string_to_int(self.node_id)

    def __init__(
        self,
        node_id: int | str,
        distance: float,
        direction: Literal["forward", "backward"],
        is_one_lane_road: bool,
        dlc_guard: int,
    ):
        self.node_id = node_id
        self.distance = distance
        self.direction = direction
        self.is_one_lane_road = is_one_lane_road
        self.dlc_guard = dlc_guard
        self.parse_strings()
        self.item_type = None
        self.item_uid = None
        self.lane_indices = []

    def json(self) -> dict:
        return {
            "node_id": self.node_id,
            "distance": self.distance,
            "direction": self.direction,
            "is_one_lane_road": self.is_one_lane_road,
            "dlc_guard": self.dlc_guard,
        }


class NavigationEntry:
    __slots__ = ["uid", "forward", "backward"]

    uid: int | str
    forward: list[NavigationNode]
    backward: list[NavigationNode]

    def parse_strings(self):
        self.uid = parse_string_to_int(self.uid)

    def __init__(
        self,
        uid: int | str,
        forward: list[NavigationNode],
        backward: list[NavigationNode],
    ):
        self.uid = uid
        self.forward = forward
        self.backward = backward
        self.parse_strings()

    def json(self) -> dict:
        return {
            "uid": self.uid,
            "forward": [node.json() for node in self.forward],
            "backward": [node.json() for node in self.backward],
        }

    def calculate_node_data(self, map_data):
        this = map_data.get_node_by_uid(self.uid)
        if this is None:
            return
        for node in self.forward:
            if node.node_id == self.uid:
                continue

            map_data.total += 1
            other = map_data.get_node_by_uid(node.node_id)
            if other is None or other == this:
                continue

            node.item_uid = node_helpers.get_connecting_item_uid(this, other)
            if node.item_uid is None:
                logging.debug(
                    f"Failed to get connecting item UID for nodes {this.uid} and {other.uid}"
                )
                map_data.not_found += 1
                continue

            item = map_data.get_item_by_uid(node.item_uid, warn_errors=False)
            if item is None:
                continue
            node.item_type = type(item)
            node.lane_indices = node_helpers.get_connecting_lanes_by_item(
                this, other, item, map_data
            )
            if node.lane_indices == []:
                map_data.lanes_invalid += 1

        for node in self.backward:
            if node.node_id == self.uid:
                continue

            map_data.total += 1
            other = map_data.get_node_by_uid(node.node_id)
            if other is None or other == this:
                continue

            node.item_uid = node_helpers.get_connecting_item_uid(this, other)
            if node.item_uid is None:
                logging.debug(
                    f"Failed to get connecting item UID for nodes {this.uid} and {other.uid}"
                )
                map_data.not_found += 1
                continue

            item = map_data.get_item_by_uid(node.item_uid, warn_errors=False)
            if item is None:
                continue
            node.item_type = type(item)
            node.lane_indices = node_helpers.get_connecting_lanes_by_item(
                this, other, item, map_data
            )
            if node.lane_indices == []:
                map_data.lanes_invalid += 1


class Node:
    __slots__ = [
        "uid",
        "x",
        "y",
        "z",
        "rotation",
        "rotationQuat",
        "_euler",
        "forward_item_uid",
        "backward_item_uid",
        "sector_x",
        "sector_y",
        "forward_country_id",
        "backward_country_id",
        "_navigation",
    ]

    uid: str
    x: float
    y: float
    z: float
    rotation: float
    """NOTE: This variable is not to be used. It is only here for compatibility, please use `.euler` instead."""
    rotationQuat: list[float]
    _euler: list[float]
    forward_item_uid: str
    backward_item_uid: str
    sector_x: int
    sector_y: int
    forward_country_id: str
    backward_country_id: str
    _navigation: NavigationEntry

    def parse_strings(self):
        self.uid = parse_string_to_int(self.uid)
        self.forward_item_uid = parse_string_to_int(self.forward_item_uid)
        self.backward_item_uid = parse_string_to_int(self.backward_item_uid)
        self.forward_country_id = parse_string_to_int(self.forward_country_id)
        self.backward_country_id = parse_string_to_int(self.backward_country_id)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        rotation: float,
        rotationQuat: list[float],
        forward_item_uid: int | str,
        backward_item_uid: int | str,
        sector_x: int,
        sector_y: int,
        forward_country_id: int | str,
        backward_country_id: int | str,
    ):
        self.uid = uid

        self.x = x
        self.y = y
        self.z = z

        self.rotation = rotation
        self.rotationQuat = rotationQuat
        self._euler = None

        self.forward_item_uid = forward_item_uid
        self.backward_item_uid = backward_item_uid

        self.sector_x = sector_x
        self.sector_y = sector_y

        self.forward_country_id = forward_country_id
        self.backward_country_id = backward_country_id

        self._navigation = None

        self.parse_strings()

    @property
    def euler(self) -> list[float]:
        if self._euler is None:
            self._euler = math_helpers.QuatToEuler(self.rotationQuat)
        return self._euler

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
            "rotationQuat": self.rotationQuat,
            "forward_item_uid": self.forward_item_uid,
            "backward_item_uid": self.backward_item_uid,
            "sector_x": self.sector_x,
            "sector_y": self.sector_y,
            "forward_country_id": self.forward_country_id,
            "backward_country_id": self.backward_country_id,
        }


class Transform:
    __slots__ = ["x", "y", "z", "rotation", "euler"]

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
        return {"x": self.x, "y": self.y, "z": self.z, "rotation": self.rotation}


class Position:
    __slots__ = ["x", "y", "z"]

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

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y, self.z - other.z)

    def distance_to(self, other: "Position") -> float:
        return math.sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )

    def json(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}


class Point:
    __slots__ = ["x", "y", "z"]

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
        return {"x": self.x, "y": self.y, "z": self.z}


class BoundingBox:
    __slots__ = ["min_x", "min_y", "max_x", "max_y"]

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def center(self) -> Position:
        return Position((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2, 0)

    def __str__(self) -> str:
        return f"BoundingBox({self.min_x}, {self.min_y}, {self.max_x}, {self.max_y})"

    def to_start_end(self) -> tuple[Position, Position]:
        return Position(self.min_x, self.min_y, 0), Position(self.max_x, self.max_y, 0)

    def to_start_width_height(self) -> tuple[Position, float, float]:
        return (
            Position(self.min_x, self.min_y, 0),
            self.max_x - self.min_x,
            self.max_y - self.min_y,
        )

    def __repr__(self) -> str:
        return self.__str__()

    def is_in(self, point: Position, offset: float = 0) -> bool:
        min_x = self.min_x - offset
        max_x = self.max_x + offset
        min_y = self.min_y - offset
        max_y = self.max_y + offset
        return min_x <= point.x <= max_x and min_y <= point.y <= max_y

    def json(self) -> dict:
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
        }


class BaseItem:
    __slots__ = ["uid", "type", "x", "y", "sector_x", "sector_y"]

    uid: str
    type: ItemType
    x: float
    y: float
    sector_x: int
    sector_y: int

    def parse_strings(self):
        if not str(self.uid).startswith("prefab_"):
            self.uid = parse_string_to_int(self.uid)

    def __init__(
        self,
        uid: int | str,
        type: ItemType,
        x: float,
        y: float,
        sector_x: int,
        sector_y: int,
    ):
        self.uid = uid
        self.type = type
        self.x = x
        self.y = y
        self.sector_x = sector_x
        self.sector_y = sector_y

    def json(self) -> dict:
        return {
            "uid": str(self.uid),
            "type": self.type,
            "x": self.x,
            "y": self.y,
        }


class SignDescription:
    __slots__ = ["token", "name", "model_path", "category"]

    token: str
    name: str
    model_path: str
    category: str

    def __init__(
        self,
        token: str,
        name: str,
        model_path: str,
        category: str,
    ):
        self.token = token
        self.name = name
        self.model_path = model_path
        self.category = category

    def json(self) -> dict:
        return {
            "token": self.token,
            "name": self.name,
            "model_path": self.model_path,
            "category": self.category,
        }


class SignAction(StrEnum):
    # Give way triangle
    GIVE_WAY = "give_way"
    # Stop sign
    STOP = "stop"
    # Speed limit changes
    SPEED_LIMIT = "speed_limit"
    # Pedestrian crossing sign
    PEDESTRIAN_CROSSING = "pedestrian_crossing"
    # Street lamp
    LAMP = "lamp"
    # Other props that are not lamps
    PROP = "prop"
    # General sign (with text)
    GENERAL = "general"
    # Speedcamera
    SPEEDCAMERA = "speedcamera"
    # Post
    POST = "post"
    # None
    NONE = "none"


class Sign(BaseItem):
    __slots__ = [
        "token",
        "node_uid",
        "text_items",
        "description",
        "_action",
        "_action_data",
        "_node",
    ]

    token: str
    node_uid: str
    text_items: list[str]
    description: SignDescription | None
    _action: SignAction | None
    _action_data: Any | None
    _node: Node | None

    @property
    def node(self) -> Node | None:
        if self._node is None:
            self._node = data.map.get_node_by_uid(self.node_uid)
        return self._node

    @property
    def z(self) -> float:
        return self.node.z if self.node else 0

    @property
    def euler(self) -> list[float]:
        return self.node.euler if self.node else [0, 0, 0]

    @property
    def rotation(self) -> float:
        return self.node.rotation if self.node else 0

    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)

    def parse_action(self):
        if not self.description:
            self.action = None
            self.action_data = None
            return

        for text in self.text_items:
            # matches explicit traffic rule for speedlimit
            if text.startswith("traffic_rule.limit_"):
                possible_data = text.split("traffic_rule.limit_")[1]
                if possible_data.isdigit():
                    self.action = SignAction.SPEED_LIMIT
                    self.action_data = int(possible_data)
                    return

        # matches /models/lamp <- to check for lamps
        if self.description.model_path.split("/")[2] == "lamp":
            self.action = SignAction.LAMP
            self.action_data = None
            return

        # matches /model/speedcamera
        if self.description.model_path.split("/")[2] == "speedcamera":
            self.action = SignAction.SPEEDCAMERA
            self.action_data = None
            return

        # matches "reflective post uk" etc... in the description name
        if (
            "reflective post" in self.description.name
            or "column" in self.description.name
        ):
            self.action = SignAction.POST
            self.action_data = None
            return

        # matches "speed limit 110 dk" etc... in the description name
        if "speed limit" in self.description.name:
            possible_data = self.description.name.replace("speed limit", "").strip()
            possible_data = possible_data.split(" ")[0]
            if possible_data.isdigit():
                self.action = SignAction.SPEED_LIMIT
                self.action_data = int(possible_data)
                return

        # matches "speedlimit 110 cr" etc... in the description name
        if "speedlimit" in self.description.name:
            possible_data = self.description.name.replace("speedlimit", "").strip()
            possible_data = possible_data.split(" ")[0]
            if possible_data.isdigit():
                self.action = SignAction.SPEED_LIMIT
                self.action_data = int(possible_data)
                return

        # matches "al stop"
        # doesn't match "rest stop", "bus stop" etc...
        if "stop" in self.description.name:
            words = self.description.name.split(" ")
            if "stop" in words:
                filters = [
                    "bus",
                    "stopping",
                    "tram",
                    "rest",
                    "border",
                    "kontrole",
                    "kontroll",
                ]
                has_filters = any(f in words for f in filters)
                if not has_filters:
                    self.action = SignAction.STOP
                    self.action_data = None
                    return

        # matches anything with "give" or "yield"
        if (
            " give " in self.description.name
            or "give " in self.description.name
            or "yield" in self.description.name
        ):
            self.action = SignAction.GIVE_WAY
            self.action_data = None
            return

        # matches "pedestrians dk" etc...
        if (
            "pedestrians" in self.description.name
            or "crossing" in self.description.name
        ):
            self.action = SignAction.PEDESTRIAN_CROSSING
            self.action_data = None
            return

        # matches "/model2/props/..."
        if "prop" in self.description.model_path:
            self.action = SignAction.PROP
            self.action_data = None

        if "sign" in self.description.model_path:
            self.action = SignAction.GENERAL
            self.action_data = None

        if not self._action:
            self.action = SignAction.NONE
            self.action_data = None

    @property
    def action(self) -> SignAction | None:
        if self._action is None:
            self.parse_action()
        return self._action

    @action.setter
    def action(self, value: SignAction | None):
        self._action = value

    @property
    def action_data(self) -> Any | None:
        if self._action is None:
            self.parse_action()
        return self._action_data

    @action_data.setter
    def action_data(self, value: Any | None):
        self._action_data = value

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        sector_x: int,
        sector_y: int,
        token: str,
        node_uid: int | str,
        text_items: list[str],
    ):
        super().__init__(uid, ItemType.Sign, x, y, sector_x, sector_y)
        super().parse_strings()
        self.description = None
        self.token = token
        self.node_uid = node_uid
        self.text_items = text_items
        self.action = None
        self.action_data = None
        self._node = None

    def json(self) -> dict:
        return_dict = {
            **super().json(),
        }
        # BaseItem has the Y coordinate when it should be Z
        # so we flip them here
        return_dict["z"] = return_dict.get("y", 0)
        return_dict["y"] = self.z
        return_dict = {
            **return_dict,
            "rotation": self.rotation,
            "token": self.token,
            "node_uid": self.node_uid,
            "text_items": self.text_items,
            "description": self.description.json() if self.description else None,
            "action": self.action,
            "action_data": self.action_data,
        }
        return return_dict


class CityArea(BaseItem):
    __slots__ = ["token", "hidden", "width", "height"]

    token: str
    hidden: bool
    width: float
    height: float

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        sector_x: int,
        sector_y: int,
        token: str,
        hidden: bool,
        width: float,
        height: float,
    ):
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
            "height": self.height,
        }


class City:
    __slots = [
        "token",
        "name",
        "name_localized",
        "country_token",
        "population",
        "x",
        "y",
        "areas",
    ]

    token: str
    name: str
    name_localized: str
    country_token: str
    population: int
    x: float
    y: float
    areas: list[CityArea]

    def __init__(
        self,
        token: str,
        name: str,
        name_localized: str | None,
        country_token: str,
        population: int,
        x: float,
        y: float,
        areas: list[CityArea],
    ):
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
            "areas": [area.json() for area in self.areas],
        }


class Country:
    __slots__ = ["token", "name", "name_localized", "id", "x", "y", "code"]

    token: str
    name: str
    name_localized: str | None
    id: int
    x: float
    y: float
    code: str

    def __init__(
        self,
        token: str,
        name: str,
        name_localized: str | None,
        id: int,
        x: float,
        y: float,
        code: str,
    ):
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
            "code": self.code,
        }


class Company:
    __slots__ = ["token", "name", "city_tokens", "cargo_in_tokens", "cargo_out_tokens"]

    token: str
    name: str
    city_tokens: list[str]
    cargo_in_tokens: list[str]
    cargo_out_tokens: list[str]

    def __init__(
        self,
        token: str,
        name: str,
        city_tokens: list[str],
        cargo_in_tokens: list[str],
        cargo_out_tokens: list[str],
    ):
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
            "cargo_out_tokens": self.cargo_out_tokens,
        }


class FerryConnection:
    __slots__ = [
        "token",
        "name",
        "name_localized",
        "x",
        "y",
        "z",
        "price",
        "time",
        "distance",
        "intermediate_points",
    ]

    token: str
    name: str
    name_localized: str
    x: float
    y: float
    z: float
    price: float
    time: float
    distance: float
    intermediate_points: list[Transform]

    def __init__(
        self,
        token: str,
        name: str,
        name_localized: str | None,
        x: float,
        y: float,
        z: float,
        price: float,
        time: float,
        distance: float,
        intermediate_points: list[Transform],
    ):
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
            "intermediate_points": [point.json() for point in self.intermediate_points],
        }


class Ferry:
    __slots__ = [
        "token",
        "train",
        "name",
        "name_localized",
        "x",
        "y",
        "z",
        "connections",
    ]

    token: str
    train: bool
    name: str
    name_localized: str
    x: float
    y: float
    z: float
    connections: list[FerryConnection]

    def __init__(
        self,
        token: str,
        train: bool,
        name: str,
        name_localized: str | None,
        x: float,
        y: float,
        z: float,
        connections: list[FerryConnection],
    ):
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
            "connections": [connection.json() for connection in self.connections],
        }


class RoadLook:
    __slots__ = [
        "token",
        "name",
        "lanes_left",
        "lanes_right",
        "offset",
        "lane_offset",
        "shoulder_space_left",
        "shoulder_space_right",
    ]

    token: str
    name: str
    lanes_left: list[str]
    lanes_right: list[str]
    offset: float
    lane_offset: float
    shoulder_space_left: float
    shoulder_space_right: float

    def __init__(
        self,
        token: str,
        name: str,
        lanes_left: list[str],
        lanes_right: list[str],
        offset: float | None,
        lane_offset: float | None,
        shoulder_space_left: float | None,
        shoulder_space_right: float | None,
    ):
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
            "shoulder_space_right": self.shoulder_space_right,
        }

    def __str__(self) -> str:
        return f"RoadLook({self.token}, {self.name}, {self.lanes_left}, {self.lanes_right}, {self.offset}, {self.lane_offset}, {self.shoulder_space_left}, {self.shoulder_space_right})"

    def __repr__(self) -> str:
        return self.__str__()


class ModelDescription:
    __slots__ = ["token", "center", "start", "end", "height", "width", "length"]

    token: str
    center: Position
    start: Position
    end: Position
    height: float
    width: float
    length: float

    def __init__(
        self,
        token: str,
        center: Position,
        start: Position,
        end: Position,
        height: float,
    ):
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
            "length": self.length,
        }


# MARK: POIs


class BasePOI:
    __slots__ = ["uid", "x", "y", "z", "sector_x", "sector_y", "icon"]

    uid: str
    x: float
    y: float
    z: float
    sector_x: int
    sector_y: int
    icon: str

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        icon: str,
    ):
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
            "icon": self.icon,
        }


class GeneralPOI(BasePOI):
    __slots__ = ["type", "label"]

    type: NonFacilityPOI
    label: str

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        icon: str,
        label: str,
    ):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.type = None  # General
        self.label = label

    def json(self) -> dict:
        return {**super().json(), "type": self.type, "label": self.label}


class LandmarkPOI(BasePOI):
    __slots__ = ["label", "dlc_guard", "node_uid", "type"]

    label: str
    dlc_guard: int
    node_uid: str
    type: NonFacilityPOI

    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        icon: str,
        label: str,
        dlc_guard: int,
        node_uid: int | str,
    ):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.type = NonFacilityPOI.LANDMARK
        self.label = label
        self.dlc_guard = dlc_guard
        self.node_uid = node_uid
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "label": self.label,
            "dlc_guard": self.dlc_guard,
            "node_uid": self.node_uid,
        }


# This is not elegant but it is the only way to make it work in python
LabeledPOI = Union[GeneralPOI, LandmarkPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""


class RoadPOI(BasePOI):
    __slots__ = ["dlc_guard", "node_uid", "type"]

    dlc_guard: int
    node_uid: str
    type: str

    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        icon: str,
        dlc_guard: int,
        node_uid: int | str,
    ):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.type = "road"
        self.dlc_guard = dlc_guard
        self.node_uid = node_uid
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "node_uid": self.node_uid,
        }


class FacilityPOI(BasePOI):
    __slots__ = ["prefab_uid", "prefab_path", "type"]

    icon: FacilityIcon
    prefab_uid: str
    prefab_path: str
    type: str

    def parse_strings(self):
        self.prefab_uid = parse_string_to_int(self.prefab_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        icon: str,
        prefab_uid: int | str,
        prefab_path: str,
    ):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.type = "facility"
        self.prefab_uid = prefab_uid
        self.prefab_path = prefab_path
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "icon": self.icon,
            "prefab_uid": self.prefab_uid,
            "prefab_path": self.prefab_path,
        }


class ParkingPOI(BasePOI):
    __slots__ = ["dlc_guard", "from_item_type", "item_node_uids", "type"]

    dlc_guard: int
    from_item_type: Literal["trigger", "mapOverlay", "prefab"]
    item_node_uids: list[int | str]
    type: str
    icon: FacilityIcon

    def parse_strings(self):
        self.item_node_uids = [
            parse_string_to_int(node) for node in self.item_node_uids
        ]

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        icon: str,
        dlc_guard: int,
        from_item_type: Literal["trigger", "mapOverlay", "prefab"],
        item_node_uids: list[int | str],
    ):
        super().__init__(uid, x, y, z, sector_x, sector_y, icon)
        self.dlc_guard = dlc_guard
        self.from_item_type = from_item_type
        self.item_node_uids = item_node_uids
        self.type = "facility"
        self.icon = FacilityIcon.PARKING
        self.parse_strings()

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "from_item_type": self.from_item_type,
            "item_node_uids": self.item_node_uids,
        }


UnlabeledPOI = Union[RoadPOI, FacilityPOI, ParkingPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""
POI = Union[LabeledPOI, UnlabeledPOI]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""


# MARK: Map Items


class Lane:
    __slots__ = ["points", "side", "length"]

    points: list[Position]
    side: Literal["left", "right"]
    length: float

    def __init__(self, points: list[Position], side: Literal["left", "right"]):
        self.points = points
        self.side = side
        self.length = self.calculate_length()

    def calculate_length(self) -> float:
        length = 0
        for i in range(len(self.points) - 1):
            length += math.sqrt(
                math.pow(self.points[i].x - self.points[i + 1].x, 2)
                + math.pow(self.points[i].z - self.points[i + 1].z, 2)
            )
        return length

    def json(self) -> dict:
        return {
            "points": [point.json() for point in self.points],
            "side": self.side,
            "length": self.length,
        }


class Railing:
    __slots__ = [
        "right_railing",
        "right_railing_offset",
        "left_railing",
        "left_railing_offset",
    ]

    right_railing: str
    right_railing_offset: int
    left_railing: str
    left_railing_offset: int

    def __init__(
        self,
        right_railing: str,
        right_railing_offset: int,
        left_railing: str,
        left_railing_offset: int,
    ):
        self.right_railing = right_railing
        self.right_railing_offset = right_railing_offset
        self.left_railing = left_railing
        self.left_railing_offset = left_railing_offset

    def json(self) -> dict:
        return {
            "right_railing": self.right_railing,
            "right_railing_offset": self.right_railing_offset,
            "left_railing": self.left_railing,
            "left_railing_offset": self.left_railing_offset,
        }


class Road(BaseItem):
    __slots__ = [
        "dlc_guard",
        "hidden",
        "road_look_token",
        "start_node_uid",
        "end_node_uid",
        "length",
        "maybe_divided",
        "type",
        "road_look",
        "_bounding_box",
        "_lanes",
        "_points",
        "start_node",
        "end_node",
        "railings",
    ]

    dlc_guard: int
    hidden: bool
    road_look_token: str
    start_node_uid: int
    end_node_uid: int
    length: float
    maybe_divided: bool
    type: ItemType
    road_look: RoadLook
    railings: list[Railing] | None

    _bounding_box: BoundingBox
    _lanes: list[Lane]
    _points: list[Position]

    def parse_strings(self):
        # Only parse UIDs if they don't contain 'prefab_' prefix
        if not str(self.uid).startswith("prefab_"):
            self.start_node_uid = parse_string_to_int(self.start_node_uid)
            self.end_node_uid = parse_string_to_int(self.end_node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        sector_x: int,
        sector_y: int,
        dlc_guard: int,
        hidden: bool | None,
        road_look_token: str,
        start_node_uid: int | str,
        end_node_uid: int | str,
        length: float,
        maybe_divided: bool | None,
        railings: list[Railing] | None = None,
    ):
        super().__init__(uid, ItemType.Road, x, y, sector_x, sector_y)
        super().parse_strings()

        self.type = ItemType.Road
        self.dlc_guard = int(dlc_guard) if dlc_guard is not None else -1
        self.hidden = bool(hidden) if hidden is not None else False
        self.road_look_token = road_look_token
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
        self.length = length
        self.maybe_divided = maybe_divided
        self.railings = railings if railings is not None else []

        self.road_look = None
        self.clear_data()
        self.parse_strings()

    def clear_data(self):
        self._lanes = []
        self._bounding_box = None
        self._points = None
        self.start_node = None
        self.end_node = None

    def get_nodes(self, map=None):
        """Populate start_node and end_node if not already set."""
        if map is None:
            map = data.map

        try:
            if not hasattr(self, "start_node_uid") or not hasattr(self, "end_node_uid"):
                logging.error(f"Road {self.uid} missing node UIDs")
                return None, None

            if self.start_node is None:
                self.start_node = map.get_node_by_uid(self.start_node_uid)
            if self.end_node is None:
                self.end_node = map.get_node_by_uid(self.end_node_uid)

            if self.start_node is None or self.end_node is None:
                logging.error(f"Road {self.uid} failed to get nodes")
                return None, None

            return self.start_node, self.end_node
        except Exception as e:
            logging.error(f"Error getting nodes for road {self.uid}: {e}")
            return None, None

    def generate_points(
        self, road_quality: float = 0.5, min_quality: int = 4
    ) -> list[Position]:
        try:
            start_node, end_node = self.get_nodes()
            if not start_node or not end_node:
                logging.error(f"Failed to get nodes for road {self.uid}")
                return []

            new_points = []

            start_pos = (start_node.x, start_node.z, start_node.y)
            end_pos = (end_node.x, end_node.z, end_node.y)

            start_quaternion = (
                start_node.rotationQuat
                if hasattr(start_node, "rotationQuat")
                else (0, 0, 0, 0)
            )
            end_quaternion = (
                end_node.rotationQuat
                if hasattr(end_node, "rotationQuat")
                else (0, 0, 0, 0)
            )

            length = math.sqrt(
                sum((e - s) ** 2 for s, e in zip(start_pos, end_pos, strict=False))
            )
            needed_points = max(int(length * road_quality), min_quality)

            for i in range(needed_points):
                s = i / (needed_points - 1)
                x, y, z = math_helpers.Hermite3D(
                    s, start_pos, end_pos, start_quaternion, end_quaternion, self.length
                )
                new_points.append(Position(x, y, z))

            return new_points
        except Exception as e:
            logging.exception(f"Error generating points for road {self.uid}: {e}")
            return []

    @property
    def points(self) -> list[Position]:
        if self._points is None:
            self._points = self.generate_points(
                road_quality=0.5 * max(1, point_multiplier)
            )
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

    def distance_to(self, position: Position) -> float:
        """Calculate the distance from the road to a given position."""
        if self.bounding_box.is_in(position):
            return 0.0

        min_distance = float("inf")
        for point in self.points:
            distance = math.sqrt(
                (point.x - position.x) ** 2
                + (point.y - position.y) ** 2
                + (point.z - position.z) ** 2
            )
            if distance < min_distance:
                min_distance = distance

        return min_distance

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
            "bounding_box": self.bounding_box.json(),
            "railings": [railing.json() for railing in self.railings],
        }


class MapArea(BaseItem):
    __slots__ = ["dlc_guard", "draw_over", "node_uids", "color", "type"]

    dlc_guard: int
    draw_over: bool
    node_uids: list[int | str]
    color: MapColor
    type: ItemType

    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        sector_x: int,
        sector_y: int,
        dlc_guard: int,
        draw_over: bool | None,
        node_uids: list[int | str],
        color: MapColor,
    ):
        super().__init__(uid, ItemType.MapArea, x, y, sector_x, sector_y)
        self.type = ItemType.MapArea
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
            "color": self.color,
        }


class MapOverlayType(Enum):
    ROAD = 0
    PARKING = 1
    LANDMARK = 4


class MapOverlay(BaseItem):
    __slots__ = ["dlc_guard", "overlay_type", "token", "node_uid", "type"]

    dlc_guard: int
    overlay_type: MapOverlayType
    token: str
    node_uid: str
    type: ItemType

    def parse_strings(self):
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        dlc_guard: int,
        overlay_type: MapOverlayType,
        token: str,
        node_uid: int | str,
    ):
        super().__init__(uid, ItemType.MapOverlay, x, y, z, sector_x, sector_y)
        self.type = ItemType.MapOverlay
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
            "node_uid": self.node_uid,
        }


class Building(BaseItem):
    __slots__ = ["scheme", "start_node_uid", "end_node_uid", "type"]

    scheme: str
    start_node_uid: str
    end_node_uid: str
    type: ItemType

    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        scheme: str,
        start_node_uid: int | str,
        end_node_uid: int | str,
    ):
        super().__init__(uid, ItemType.Building, x, y, z, sector_x, sector_y)
        self.type = ItemType.Building
        self.scheme = scheme
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid

    def json(self) -> dict:
        return {
            **super().json(),
            "scheme": self.scheme,
            "start_node_uid": self.start_node_uid,
            "end_node_uid": self.end_node_uid,
        }


class Curve(BaseItem):
    __slots__ = [
        "model",
        "look",
        "num_buildings",
        "start_node_uid",
        "end_node_uid",
        "type",
    ]

    model: str
    look: str
    num_buildings: int
    start_node_uid: str
    end_node_uid: str
    type: ItemType

    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        model: str,
        look: str,
        num_buildings: int,
        start_node_uid: int | str,
        end_node_uid: int | str,
    ):
        super().__init__(uid, ItemType.Curve, x, y, z, sector_x, sector_y)
        self.type = ItemType.Curve
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
            "end_node_uid": self.end_node_uid,
        }


class FerryItem(BaseItem):
    __slots__ = ["token", "train", "prefab_uid", "node_uid", "type"]

    token: str
    train: bool
    prefab_uid: str
    node_uid: str
    type: ItemType

    def parse_strings(self):
        super().parse_strings()
        self.prefab_uid = parse_string_to_int(self.prefab_uid)
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        token: str,
        train: bool,
        prefab_uid: int | str,
        node_uid: int | str,
    ):
        super().__init__(uid, ItemType.Ferry, x, y, z, sector_x, sector_y)
        self.type = ItemType.Ferry
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
            "node_uid": self.node_uid,
        }


class CompanyItem(BaseItem):
    __slots__ = ["token", "city_token", "prefab_uid", "node_uid", "type"]

    token: str
    city_token: str
    prefab_uid: str
    node_uid: str
    type: ItemType

    def parse_strings(self):
        super().parse_strings()
        self.prefab_uid = parse_string_to_int(self.prefab_uid)
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        sector_x: int,
        sector_y: int,
        token: str,
        city_token: str,
        prefab_uid: int | str,
        node_uid: int | str,
    ):
        super().__init__(uid, ItemType.Company, x, y, sector_x, sector_y)
        self.type = ItemType.Company
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
            "node_uid": self.node_uid,
        }


class Cutscene(BaseItem):
    __slots__ = ["flags", "tags", "node_uid", "type"]

    flags: int
    tags: list[str]
    node_uid: int | str
    type: ItemType

    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        flags: int,
        tags: list[str],
        node_uid: int | str,
    ):
        super().__init__(uid, ItemType.Cutscene, x, y, z, sector_x, sector_y)
        self.type = ItemType.Cutscene
        self.flags = flags
        self.tags = tags
        self.node_uid = node_uid

    def json(self) -> dict:
        return {
            **super().json(),
            "flags": self.flags,
            "tags": self.tags,
            "node_uid": self.node_uid,
        }


class Trigger(BaseItem):
    __slots__ = ["action_tokens", "node_uids", "type", "z"]

    action_tokens: list[str]
    node_uids: list[int | str]
    type: ItemType
    z: float

    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        action_tokens: list[str],
        node_uids: list[int | str],
    ):
        super().__init__(uid, ItemType.Trigger, x, y, sector_x, sector_y)
        self.z = z
        self.type = ItemType.Trigger
        self.action_tokens = action_tokens
        self.node_uids = node_uids

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "action_tokens": self.action_tokens,
            "node_uids": self.node_uids,
        }


class Model(BaseItem):
    __slots__ = [
        "token",
        "node_uid",
        "scale",
        "type",
        "vertices",
        "description",
        "z",
        "rotation",
    ]

    token: str
    node_uid: str
    scale: tuple[float, float, float]
    type: ItemType
    vertices: list[Position]
    description: ModelDescription
    z: float
    rotation: float

    def parse_strings(self):
        super().parse_strings()
        self.node_uid = parse_string_to_int(self.node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        sector_x: int,
        sector_y: int,
        token: str,
        node_uid: int | str,
        scale: tuple[float, float, float],
    ):
        super().__init__(uid, ItemType.Model, x, y, sector_x, sector_y)
        self.type = ItemType.Model
        self.vertices = []
        self.description = None
        self.z = math.inf
        self.rotation = 0
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
    __slots__ = ["start_node_uid", "end_node_uid", "length", "type"]

    start_node_uid: str
    end_node_uid: str
    length: float
    type: ItemType

    def parse_strings(self):
        super().parse_strings()
        self.start_node_uid = parse_string_to_int(self.start_node_uid)
        self.end_node_uid = parse_string_to_int(self.end_node_uid)

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        start_node_uid: int | str,
        end_node_uid: int | str,
        length: float,
    ):
        super().__init__(uid, ItemType.Terrain, x, y, z, sector_x, sector_y)
        self.type = ItemType.Terrain
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
        self.length = length

    def json(self) -> dict:
        return {
            **super().json(),
            "start_node_uid": self.start_node_uid,
            "end_node_uid": self.end_node_uid,
            "length": self.length,
        }


# MARK: Map Points


class BaseMapPoint:
    __slots__ = ["x", "y", "z", "neighbors"]

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
        return {"x": self.x, "y": self.y, "z": self.z, "neighbors": self.neighbors}


class NavNode:
    __slots__ = [
        "node0",
        "node1",
        "node2",
        "node3",
        "node4",
        "node5",
        "node6",
        "node_custom",
    ]

    node0: bool
    node1: bool
    node2: bool
    node3: bool
    node4: bool
    node5: bool
    node6: bool
    node_custom: bool

    def __init__(
        self,
        node0: bool,
        node1: bool,
        node2: bool,
        node3: bool,
        node4: bool,
        node5: bool,
        node6: bool,
        node_custom: bool,
    ):
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
            "node_custom": self.node_custom,
        }


class NavFlags:
    __slots__ = ["is_start", "is_base", "is_end"]

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
            "is_end": self.is_end,
        }


class RoadMapPoint(BaseMapPoint):
    __slots__ = ["lanes_left", "lanes_right", "offset", "nav_node", "nav_flags", "type"]

    lanes_left: Literal["auto"]
    lanes_right: Literal["auto"]
    offset: float
    nav_node: NavNode
    nav_flags: NavFlags
    type: str

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        neighbors: list[int | str],
        lanes_left: int | Literal["auto"],
        lanes_right: int | Literal["auto"],
        offset: float,
        nav_node: NavNode,
        nav_flags: NavFlags,
    ):
        super().__init__(x, y, z, neighbors)
        self.type = "road"
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
            "nav_flags": self.nav_flags.json(),
        }


class PolygonMapPoint(BaseMapPoint):
    __slots__ = ["color", "road_over", "type"]

    color: MapColor
    road_over: bool
    type: str

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        neighbors: list[int | str],
        color: MapColor,
        road_over: bool,
    ):
        super().__init__(x, y, z, neighbors)
        self.type = "polygon"
        self.color = color
        self.road_over = road_over

    def json(self) -> dict:
        return {**super().json(), "color": self.color, "road_over": self.road_over}


MapPoint = Union[RoadMapPoint, PolygonMapPoint]


# MARK: Prefabs


class PrefabNode:
    __slots__ = ["x", "y", "z", "rotation", "input_lanes", "output_lanes"]

    x: float
    y: float
    z: float
    rotation: float
    input_lanes: list[int]
    """indices into nav_curves"""
    output_lanes: list[int]
    """indices into nav_curves"""

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        rotation: float,
        input_lanes: list[int],
        output_lanes: list[int],
    ):
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
            "output_lanes": self.output_lanes,
        }


class PrefabSpawnPoints:
    __slots__ = ["x", "y", "z", "type"]

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
        return {"x": self.x, "y": self.y, "z": self.z, "type": self.type}


class PrefabTriggerPoint:
    __slots__ = ["x", "y", "z", "action"]

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
        return {"x": self.x, "y": self.y, "z": self.z, "action": self.action}


class PrefabNavCurve:
    __slots__ = [
        "nav_node_index",
        "start",
        "end",
        "next_lines",
        "prev_lines",
        "semaphore_id",
        "_points",
    ]

    nav_node_index: int
    start: Transform
    end: Transform
    next_lines: list[int]
    prev_lines: list[int]
    semaphore_id: int
    _points: list[Position]

    def __init__(
        self,
        nav_node_index: int,
        start: Transform,
        end: Transform,
        next_lines: list[int],
        prev_lines: list[int],
        semaphore_id: int,
        points: list[Position] = None,
    ):
        self.nav_node_index = nav_node_index
        self.start = start
        self.end = end
        self.next_lines = next_lines
        self.prev_lines = prev_lines
        self.semaphore_id = semaphore_id
        self._points = points if points is not None else []

    @property
    def points(self) -> list[Position]:
        if self._points == []:
            self._points = self.generate_points(road_quality=1 * point_multiplier)
        return self._points

    @points.setter
    def points(self, value: list[Position]):
        self._points = value

    def generate_points(
        self, road_quality: float = 1, min_quality: int = 4
    ) -> list[Position]:
        new_points = []

        # Data has Z as the height value, but we need Y
        sx = self.start.x
        sy = self.start.z
        sz = self.start.y
        ex = self.end.x
        ey = self.end.z
        ez = self.end.y

        length = math.sqrt(
            math.pow(sx - ex, 2) + math.pow(sy - ey, 2) + math.pow(sz - ez, 2)
        )
        radius = math.sqrt(math.pow(sx - ex, 2) + math.pow(sz - ez, 2))

        tan_sx = math.cos((self.start.rotation)) * radius
        tan_ex = math.cos((self.end.rotation)) * radius
        tan_sz = math.sin((self.start.rotation)) * radius
        tan_ez = math.sin((self.end.rotation)) * radius

        if length > 100:  # very large lanes should have less points
            road_quality *= 0.5

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

        new_start_pos = math_helpers.RotateAroundPoint(
            self.start.x + prefab_start_x,
            self.start.z + prefab_start_z,
            rot,
            origin_node.x,
            origin_node.y,
        )
        new_start = Transform(
            new_start_pos[0],
            self.start.y + prefab_start_y,
            new_start_pos[1],
            self.start.rotation + rot,
        )

        new_end_pos = math_helpers.RotateAroundPoint(
            self.end.x + prefab_start_x,
            self.end.z + prefab_start_z,
            rot,
            origin_node.x,
            origin_node.y,
        )
        new_end = Transform(
            new_end_pos[0],
            self.end.y + prefab_start_y,
            new_end_pos[1],
            self.end.rotation + rot,
        )

        new_points: list[Position] = []
        for point in self.points:
            new_point_pos = math_helpers.RotateAroundPoint(
                point.x + prefab_start_x,
                point.z + prefab_start_z,
                rot,
                origin_node.x,
                origin_node.y,
            )
            new_points.append(
                Position(new_point_pos[0], point.y + prefab_start_y, new_point_pos[1])
            )

        return PrefabNavCurve(
            self.nav_node_index,
            new_start,
            new_end,
            self.next_lines,
            self.prev_lines,
            self.semaphore_id,
            points=new_points,
        )

    def json(self) -> dict:
        return {
            "nav_node_index": self.nav_node_index,
            "start": self.start.json(),
            "end": self.end.json(),
            "next_lines": self.next_lines,
            "prev_lines": self.prev_lines,
            "semaphore_id": self.semaphore_id,
            "points": [point.json() for point in self.points],
        }


class NavNodeConnection:
    __slots__ = ["target_nav_node_index", "curve_indeces"]

    target_nav_node_index: int
    curve_indeces: list[int]

    def __init__(self, target_nav_node_index: int, curve_indeces: list[int]):
        self.target_nav_node_index = target_nav_node_index
        self.curve_indeces = curve_indeces

    def json(self) -> dict:
        return {
            "target_nav_node_index": self.target_nav_node_index,
            "curve_indeces": self.curve_indeces,
        }


class PrefabNavNode:
    __slots__ = ["type", "end_index", "connections"]

    type: Literal["physical", "ai"]
    """
    **physical**: the index of the normal node (see nodes array) this navNode ends at.\n
    **ai**: the index of the AI curve this navNode ends at.
    """
    end_index: int
    connections: list[NavNodeConnection]

    def __init__(
        self,
        type: Literal["physical", "ai"],
        end_index: int,
        connections: list[NavNodeConnection],
    ):
        self.type = type
        self.end_index = end_index
        self.connections = connections

    def json(self) -> dict:
        return {
            "type": self.type,
            "end_index": self.end_index,
            "connections": [connection.json() for connection in self.connections],
        }


class PrefabNavRoute:
    __slots__ = ["curves", "distance", "_points", "prefab"]

    curves: list[PrefabNavCurve]
    distance: float
    _points: list[Position]

    def __init__(self, curves: list[PrefabNavCurve]):
        self.distance = 0
        self._points = []
        self.curves = curves
        self.prefab = None

    @property
    def points(self):
        if self._points == []:
            self._points = self.generate_points(prefab=self.prefab)
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    def generate_points(self, prefab=None) -> list[Position]:
        self.prefab = prefab

        new_points = []
        for curve in self.curves:
            new_points += curve.points

        min_distance = 0.25 / point_multiplier
        last_point = new_points[0]
        accepted_points = [new_points[0]]
        for point in new_points:
            if (
                math_helpers.DistanceBetweenPoints(point.tuple(), last_point.tuple())
                > min_distance
            ):
                accepted_points.append(point)
                last_point = point

        new_points = accepted_points

        distance = 0
        for i in range(len(new_points) - 1):
            distance += math.sqrt(
                math.pow(new_points[i].x - new_points[i + 1].x, 2)
                + math.pow(new_points[i].z - new_points[i + 1].z, 2)
            )
        self.distance = distance

        if isinstance(prefab, Prefab):
            start_node = None
            start_distance = math.inf
            end_node = None
            end_distance = math.inf
            for node in prefab.node_uids:
                node = data.map.get_node_by_uid(node)
                node_distance_start = math_helpers.DistanceBetweenPoints(
                    (node.x, node.y), (new_points[0].x, new_points[0].z)
                )
                node_distance_end = math_helpers.DistanceBetweenPoints(
                    (node.x, node.y), (new_points[-1].x, new_points[-1].z)
                )

                if node_distance_start < start_distance:
                    start_distance = node_distance_start
                    start_node = node
                if node_distance_end < end_distance:
                    end_distance = node_distance_end
                    end_node = node

            start_offset = 0
            end_offset = 0

            if start_node is not None:
                start_offset = start_node.z - new_points[0].y
                if start_offset < 0.001 and start_offset > -0.001:
                    start_offset = 0

            if end_node is not None:
                end_offset = end_node.z - new_points[-1].y
                if end_offset < 0.001 and end_offset > -0.001:
                    end_offset = 0

            def interpolate_y(y1, y2, t):
                return y1 + (y2 - y1) * t

            if start_offset != 0 or end_offset != 0:
                accepted_points = []
                for i, point in enumerate(new_points):
                    accepted_points.append(
                        Position(
                            point.x,
                            point.y
                            + interpolate_y(
                                start_offset, end_offset, i / len(new_points)
                            ),
                            point.z,
                        )
                    )

                return accepted_points

        return new_points

    def generate_relative_curves(
        self, origin_node: Node, map_point_origin
    ) -> list[PrefabNavCurve]:
        new_curves = []
        for curve in self.curves:
            new_curves.append(curve.convert_to_relative(origin_node, map_point_origin))
        return new_curves

    def json(self) -> dict:
        return {
            # "curves": [curve.json() for curve in self.curves],
            "points": [point.json() for point in self.points],
            "distance": self.distance,
        }


class Semaphore:
    __slots__ = ["x", "y", "z", "rotation", "type", "id"]
    x: float
    y: float
    z: float
    rotation: float
    type: str
    id: int

    def __init__(
        self, x: float, y: float, z: float, rotation: float, type: str, id: int
    ):
        self.x = x
        self.y = y
        self.z = z
        self.rotation = rotation
        self.type = type
        self.id = id

    def json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rotation": self.rotation,
            "type": self.type,
            "id": self.id,
        }


class PrefabDescription:
    __slots__ = [
        "token",
        "path",
        "nodes",
        "map_points",
        "spawn_points",
        "trigger_points",
        "nav_curves",
        "nav_nodes",
        "semaphores",
        "_nav_routes",
    ]

    token: str
    path: str
    nodes: list[PrefabNode]
    map_points: RoadMapPoint  # | PolygonMapPoint
    """Can also be PolygonMapPoint"""
    spawn_points: list[PrefabSpawnPoints]
    trigger_points: list[PrefabTriggerPoint]
    nav_curves: list[PrefabNavCurve]
    nav_nodes: list[PrefabNavNode]
    semaphores: list[Semaphore]
    _nav_routes: list[PrefabNavRoute]

    def __init__(
        self,
        token: str,
        path: str,
        nodes: list[PrefabNode],
        map_points: RoadMapPoint | PolygonMapPoint,
        spawn_points: list[PrefabSpawnPoints],
        trigger_points: list[PrefabTriggerPoint],
        nav_curves: list[PrefabNavCurve],
        nav_nodes: list[NavNode],
        semaphores: list[Semaphore] | None = None,
    ):
        self._nav_routes = []
        self.token = token
        self.path = path
        self.nodes = nodes
        self.map_points = map_points
        self.spawn_points = spawn_points
        self.trigger_points = trigger_points
        self.nav_curves = nav_curves
        self.nav_nodes = nav_nodes
        self.semaphores = semaphores if semaphores is not None else []

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
            "path": self.path,
            "nodes": [node.json() for node in self.nodes],
            "map_points": self.map_points.json(),
            "spawn_points": [spawn.json() for spawn in self.spawn_points],
            "trigger_points": [trigger.json() for trigger in self.trigger_points],
            "nav_curves": [curve.json() for curve in self.nav_curves],
            "nav_nodes": [node.json() for node in self.nav_nodes],
            "nav_routes": [route.json() for route in self.nav_routes],
            # "semaphores": [semaphore.json() for semaphore in self.semaphores]
        }


class Prefab(BaseItem):
    __slots__ = [
        "dlc_guard",
        "hidden",
        "token",
        "node_uids",
        "origin_node_index",
        "type",
        "prefab_description",
        "z",
        "_nav_routes",
        "_bounding_box",
    ]

    dlc_guard: int
    hidden: bool
    token: str
    node_uids: list[int | str]
    origin_node_index: int
    type: ItemType
    prefab_description: PrefabDescription
    z: float
    _nav_routes: list[PrefabNavRoute]
    _bounding_box: BoundingBox

    def parse_strings(self):
        super().parse_strings()
        self.node_uids = [parse_string_to_int(node) for node in self.node_uids]

    def __init__(
        self,
        uid: int | str,
        x: float,
        y: float,
        z: float,
        sector_x: int,
        sector_y: int,
        dlc_guard: int,
        hidden: bool | None,
        token: str,
        node_uids: list[int | str],
        origin_node_index: int,
    ):
        super().__init__(uid, ItemType.Prefab, x, y, sector_x, sector_y)
        self.type = ItemType.Prefab
        self.prefab_description = None
        self._nav_routes = []
        self._bounding_box = None
        self.z = z
        self.dlc_guard = dlc_guard
        self.hidden = hidden
        self.token = token
        self.node_uids = node_uids
        self.origin_node_index = origin_node_index
        self.parse_strings()

    def build_nav_routes(self):
        self._nav_routes = []
        if self.prefab_description is None:
            return
        for route in self.prefab_description.nav_routes:
            self._nav_routes.append(
                PrefabNavRoute(
                    route.generate_relative_curves(
                        data.map.get_node_by_uid(self.node_uids[0]),
                        self.prefab_description.nodes[self.origin_node_index],
                    )
                )
            )

        for route in self._nav_routes:
            route.generate_points(self)

        if not auto_tolls:
            return

        if "toll" not in self.prefab_description.path:
            return

        # Get triggers and sort them to ones
        # that affect toll roads.
        triggers: list[Trigger] = data.map.get_sector_triggers_by_sector(
            [self.sector_x, self.sector_y]
        )
        valid_toll_markers = []
        for trigger in triggers:
            for action in trigger.action_tokens:
                if (
                    isinstance(action, str)
                    and "toll" in action.lower()
                    or isinstance(action, list)
                    and "toll" in action[0].lower()
                ):
                    uids = trigger.node_uids
                    for uid in uids:
                        node = data.map.get_node_by_uid(uid)
                        valid_toll_markers.append(Position(node.x, node.z, node.y))

        if not valid_toll_markers:
            return

        # Get the closest route for each marker.
        valid_routes = []
        for marker in valid_toll_markers:
            closest_route = None
            closest_distance = math.inf

            for route in self._nav_routes:
                for point in route.points:
                    distance = math_helpers.DistanceBetweenPoints(
                        (point.x, point.z), (marker.x, marker.z)
                    )
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_route = route

            if closest_distance < 8:
                if closest_route not in valid_routes:
                    valid_routes.append(closest_route)

        # Only override if we found valid routes in both directions.
        if valid_routes and len(valid_routes) > 1:
            self._nav_routes = valid_routes

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

    @property
    def starts(self) -> list[Position]:
        starts = []
        for route in self.nav_routes:
            start = route.curves[0].start
            if start not in starts:
                starts.append(start)
        return starts

    @property
    def ends(self) -> list[Position]:
        ends = []
        for route in self.nav_routes:
            end = route.curves[-1].end
            if end not in ends:
                ends.append(end)

        return ends

    def json(self) -> dict:
        return {
            **super().json(),
            "dlc_guard": self.dlc_guard,
            "hidden": self.hidden,
            "token": self.token,
            "node_uids": [str(node) for node in self.node_uids],
            "origin_node_index": self.origin_node_index,
            "origin_node": data.map.get_node_by_uid(
                self.node_uids[self.origin_node_index]
            ).json(),
            "nav_routes": [route.json() for route in self.nav_routes],
            "bounding_box": self.bounding_box.json(),
        }


Item = Union[
    City,
    Country,
    Company,
    Ferry,
    POI,
    Road,
    Prefab,
    MapArea,
    MapOverlay,
    Building,
    Curve,
    FerryItem,
    CompanyItem,
    Cutscene,
    Trigger,
    Model,
    Terrain,
]
"""NOTE: You shouldn't use this type directly, use the children types instead as they provide intellisense!"""


class Elevation:
    __slots__ = ["x", "y", "z", "sector_x", "sector_y"]

    x: float
    y: float
    z: float
    sector_x: int
    sector_y: int

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.sector_x = 0
        self.sector_y = 0

    def json(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}


# MARK: MapData
class MapData:
    nodes: list[Node]
    """List of all nodes in the currently loaded map data."""
    elevations: list[Elevation]
    roads: list[Road]
    ferries: list[Ferry]
    prefabs: list[Prefab]
    companies: list[CompanyItem]
    models: list[Model]
    # map_areas: list[MapArea]
    triggers: list[Trigger]
    POIs: list[POI]
    dividers: list[Building | Curve]
    countries: list[Country]
    cities: list[City]
    company_defs: list[Company]
    road_looks: list[RoadLook]
    prefab_descriptions: list[PrefabDescription]
    model_descriptions: list[ModelDescription]
    sign_descriptions: list[SignDescription]
    navigation: list[NavigationEntry]
    signs: list[Sign]

    _elevations_by_sector: dict[dict[Elevation]]
    _nodes_by_sector: dict[dict[Node]]
    _roads_by_sector: dict[dict[Road]]
    _prefabs_by_sector: dict[dict[Prefab]]
    _models_by_sector: dict[dict[Model]]
    _triggers_by_sector: dict[dict[Trigger]]
    _signs_by_sector: dict[dict[Sign]]

    _min_sector_x: int = math.inf
    _max_sector_x: int = -math.inf
    _min_sector_y: int = math.inf
    _max_sector_y: int = -math.inf
    _sector_width: int = 200
    _sector_height: int = 200

    _by_uid = {}
    _model_descriptions_by_token: dict[str, ModelDescription] = {}
    _prefab_descriptions_by_token: dict[str, PrefabDescription] = {}
    _sign_descriptions_by_token: dict[str, SignDescription] = {}
    _companies_by_token: dict[str, Company] = {}
    _navigation_by_node_uid: dict[int, NavigationEntry] = {}
    """
    Nested nodes dictionary for quick access to nodes by their UID. UID is split into 4 character strings to index into the nested dictionaries.
    Please use the get_node_by_uid method to access nodes by UID.
    """

    def clear_road_data(self) -> None:
        logging.warning("Clearing road data...")
        road_helpers.get_rules()
        for road in self.roads:
            road.clear_data()
        logging.warning("Road data cleared.")

    def calculate_sectors(self) -> None:
        for node in self.nodes:
            node.sector_x, node.sector_y = self.get_sector_from_coordinates(
                node.x, node.y
            )

        for elevation in self.elevations:
            elevation.sector_x, elevation.sector_y = self.get_sector_from_coordinates(
                elevation.x, elevation.z
            )

        for road in self.roads:
            road.sector_x, road.sector_y = self.get_road_sector(road)

        for prefab in self.prefabs:
            prefab.sector_x, prefab.sector_y = self.get_sector_from_center_of_nodes(
                prefab.node_uids, (prefab.x, prefab.y)
            )

        for company in self.companies:
            company.sector_x, company.sector_y = self.get_node_sector(
                company.node_uid, (company.x, company.y)
            )

        for model in self.models:
            model.sector_x, model.sector_y = self.get_node_sector(
                model.node_uid, (model.x, model.y)
            )

        for trigger in self.triggers:
            trigger.sector_x, trigger.sector_y = self.get_sector_from_center_of_nodes(
                trigger.node_uids, (trigger.x, trigger.y)
            )

        for sign in self.signs:
            sign.sector_x, sign.sector_y = self.get_sector_from_coordinates(
                sign.x, sign.y
            )

        # for area in self.map_areas:
        #    area.sector_x, area.sector_y = self.get_sector_from_center_of_nodes(area.node_uids, (area.x, area.y))

        for poi in self.POIs:
            poi.sector_x, poi.sector_y = self.get_sector_from_coordinates(poi.x, poi.y)

    def get_node_sector(self, node_uid: int | str, default: tuple[float, float]):
        if not node_uid:
            return default

        node = self.get_node_by_uid(node_uid)
        if node:
            return self.get_sector_from_coordinates(node.x, node.y)
        else:
            return self.get_sector_from_coordinates(default[0], default[1])

    def get_road_sector(self, road: Road):
        start_node = self.get_node_by_uid(road.start_node_uid)
        end_node = self.get_node_by_uid(road.end_node_uid)
        if start_node and end_node:
            center_coordinate_X = (start_node.x + end_node.x) / 2
            center_coordinate_Y = (start_node.y + end_node.y) / 2
        else:
            center_coordinate_X = road.x
            center_coordinate_Y = road.y

        return self.get_sector_from_coordinates(
            center_coordinate_X, center_coordinate_Y
        )

    def get_sector_from_center_of_nodes(
        self, node_uids: list[int | str], default: tuple[float, float]
    ):
        center_coordinate_X = 0
        center_coordinate_Y = 0
        node_num = 0
        for node_uid in node_uids:
            node = self.get_node_by_uid(node_uid)
            if node:
                node_num += 1
                center_coordinate_X += node.x
                center_coordinate_Y += node.y

        if node_num > 0:
            return self.get_sector_from_coordinates(
                center_coordinate_X / node_num, center_coordinate_Y / node_num
            )
        else:
            return self.get_sector_from_coordinates(default[0], default[1])

    def sort_to_sectors(self) -> None:
        self._elevations_by_sector = {}
        self._nodes_by_sector = {}
        self._roads_by_sector = {}
        self._prefabs_by_sector = {}
        self._models_by_sector = {}
        self._triggers_by_sector = {}
        self._signs_by_sector = {}

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

        for elevation in self.elevations:
            sector = (elevation.sector_x, elevation.sector_y)
            if sector[0] not in self._elevations_by_sector:
                self._elevations_by_sector[sector[0]] = {}
            if sector[1] not in self._elevations_by_sector[sector[0]]:
                self._elevations_by_sector[sector[0]][sector[1]] = []
            self._elevations_by_sector[sector[0]][sector[1]].append(elevation)

        for trigger in self.triggers:
            sector = (trigger.sector_x, trigger.sector_y)
            if sector[0] not in self._triggers_by_sector:
                self._triggers_by_sector[sector[0]] = {}
            if sector[1] not in self._triggers_by_sector[sector[0]]:
                self._triggers_by_sector[sector[0]][sector[1]] = []
            self._triggers_by_sector[sector[0]][sector[1]].append(trigger)

        for sign in self.signs:
            sector = (sign.sector_x, sign.sector_y)
            if sector[0] not in self._signs_by_sector:
                self._signs_by_sector[sector[0]] = {}
            if sector[1] not in self._signs_by_sector[sector[0]]:
                self._signs_by_sector[sector[0]][sector[1]] = []
            self._signs_by_sector[sector[0]][sector[1]].append(sign)

    def calculate_sector_dimensions(self) -> None:
        min_sector_x = self._min_sector_x
        min_sector_x_y = min(
            [key for key in self._nodes_by_sector[min_sector_x].keys()]
        )
        min_sector_y = self._min_sector_y
        min_sector_y_x = min(
            [
                key if min_sector_y in self._nodes_by_sector[key].keys() else math.inf
                for key in self._nodes_by_sector.keys()
            ]
        )
        min_x = min(
            [node.x for node in self._nodes_by_sector[min_sector_x][min_sector_x_y]]
        )
        min_y = min(
            [node.y for node in self._nodes_by_sector[min_sector_y_x][min_sector_y]]
        )

        max_sector_x = self._max_sector_x
        max_sector_x_y = max(
            [key for key in self._nodes_by_sector[max_sector_x].keys()]
        )
        max_sector_y = self._max_sector_y
        max_sector_y_x = max(
            [
                key if max_sector_y in self._nodes_by_sector[key].keys() else -math.inf
                for key in self._nodes_by_sector.keys()
            ]
        )
        max_x = max(
            [node.x for node in self._nodes_by_sector[max_sector_x][max_sector_x_y]]
        )
        max_y = max(
            [node.y for node in self._nodes_by_sector[max_sector_y_x][max_sector_y]]
        )

        self._sector_width = (max_x - min_x) / (max_sector_x - min_sector_x)
        self._sector_height = (max_y - min_y) / (max_sector_y - min_sector_y)

    def build_dictionary(self) -> None:
        self._by_uid = {}
        items = self.nodes + self.roads + self.prefabs + self.models
        for item in items:
            uid_str = str(item.uid)
            self._by_uid[uid_str] = item

        self._model_descriptions_by_token = {}
        for model_description in self.model_descriptions:
            self._model_descriptions_by_token[model_description.token] = (
                model_description
            )

        self._prefab_descriptions_by_token = {}
        for prefab_description in self.prefab_descriptions:
            self._prefab_descriptions_by_token[prefab_description.token] = (
                prefab_description
            )

        self._sign_descriptions_by_token = {}
        for sign_description in self.sign_descriptions:
            self._sign_descriptions_by_token[sign_description.token] = sign_description

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

    def get_sector_triggers_by_coordinates(self, x: float, z: float) -> list[Trigger]:
        sector = self.get_sector_from_coordinates(x, z)
        return self.get_sector_triggers_by_sector(sector)

    def get_sector_triggers_by_sector(self, sector: tuple[int, int]) -> list[Trigger]:
        return self._triggers_by_sector.get(sector[0], {}).get(sector[1], [])

    def get_sector_signs_by_coordinates(self, x: float, z: float) -> list[Sign]:
        sector = self.get_sector_from_coordinates(x, z)
        return self.get_sector_signs_by_sector(sector)

    def get_sector_signs_by_sector(self, sector: tuple[int, int]) -> list[Sign]:
        return self._signs_by_sector.get(sector[0], {}).get(sector[1], [])

    def get_sector_elevations_by_coordinates(
        self, x: float, z: float
    ) -> list[Elevation]:
        sector = self.get_sector_from_coordinates(x, z)
        return self.get_sector_elevations_by_sector(sector)

    def get_sector_elevations_by_sector(
        self, sector: tuple[int, int]
    ) -> list[Elevation]:
        return self._elevations_by_sector.get(sector[0], {}).get(sector[1], [])

    def get_node_by_uid(self, uid: int | str) -> Node | None:
        try:
            if isinstance(uid, str):
                uid = parse_string_to_int(uid)

            uid_str = str(uid)
            return self._by_uid.get(uid_str, None)
        except Exception:
            return None

    def get_item_by_uid(
        self, uid: int | str, warn_errors: bool = True
    ) -> Prefab | Road:
        try:
            if isinstance(uid, str):
                uid = parse_string_to_int(uid)
            if uid == 0:
                return None
            if uid is None:
                return None

            uid_str = str(uid)
            return self._by_uid.get(uid_str, None)
        except Exception:
            if warn_errors:
                logging.warning(f"Error getting item by UID: {uid}")
            # logging.exception(f"Error getting item by UID: {uid}")
            return None

    def get_company_item_by_token_and_city(
        self, token: str, city_token: str
    ) -> CompanyItem:
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
            prefab.prefab_description = self._prefab_descriptions_by_token.get(
                prefab.token, None
            )

    def match_signs_to_descriptions(self) -> None:
        remove = []
        missing_tokens = []
        for sign in self.signs:
            if sign.token in missing_tokens:
                remove.append(sign)
                continue

            sign.description = self._sign_descriptions_by_token.get(sign.token, None)
            if not sign.description:
                print(f"Missing sign description for token: {sign.token}")
                missing_tokens.append(sign.token)
                remove.append(sign)
                continue

        for sign in remove:
            self.signs.remove(sign)

    def get_world_center_for_sector(
        self, sector: tuple[int, int]
    ) -> tuple[float, float]:
        return (
            sector[0] * self._sector_width + self._sector_width / 2,
            sector[1] * self._sector_height + self._sector_height / 2,
        )

    def get_sectors_for_coordinate_and_distance(
        self, x: float, z: float, distance: float
    ) -> list[tuple[int, int]]:
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
            if isinstance(item, Prefab):
                for _lane_id, lane in enumerate(item.nav_routes):
                    for point in lane.points:
                        point_tuple = point.tuple()
                        point_tuple = (point_tuple[0], point_tuple[2])
                        distance = math_helpers.DistanceBetweenPoints(
                            (x, z), point_tuple
                        )
                        if distance < closest_point_distance:
                            closest_point_distance = distance
                            closest_item = item

            elif isinstance(item, Road):
                # Initialize lanes if not already done
                if not hasattr(item, "_lanes"):
                    item._lanes = []
                if not item.lanes:  # If lanes list is empty, generate points
                    item.generate_points(road_quality=0.5 * point_multiplier)
                for _lane_id, lane in enumerate(item.lanes):
                    for point in lane.points:
                        point_tuple = point.tuple()
                        point_tuple = (point_tuple[0], point_tuple[2])
                        distance = math_helpers.DistanceBetweenPoints(
                            (x, z), point_tuple
                        )
                        if distance < closest_point_distance:
                            closest_point_distance = distance
                            closest_item = item

        return closest_item

    total = 0
    not_found = 0
    lanes_invalid = 0

    def compute_navigation_data(self):
        amount = len(self.navigation)
        count = 0
        for node in self.navigation:
            start_time = time.time()
            node.calculate_node_data(self)
            end_time = time.time()
            if end_time - start_time > 0.1:
                print(f"Node {node.uid} took {end_time - start_time:.2f}s to calculate")
            if count % 5000 == 0:
                print(
                    f"Processed {count}/{amount} nodes ({count / amount * 100:.2f}%)",
                    end="\r",
                )
            count += 1

        print(
            f"         > Item missing: {self.not_found} ({self.not_found / self.total * 100:.2f}%)                      "
        )
        print(
            f"         > Lanes empty: {self.lanes_invalid} ({self.lanes_invalid / self.total * 100:.2f}%)"
        )
        print(
            f"         > Successful: {self.total - self.not_found - self.lanes_invalid} ({(self.total - self.not_found - self.lanes_invalid) / self.total * 100:.2f}%)"
        )

    def export_road_offsets(self):
        if not data.export_road_offsets:
            return
        if not variables.DEVELOPMENT_MODE:
            return

        logging.warning("Calculating road offsets, this will take a while.")
        export = {
            "0. Comment": "These offsets only work in the POSITIVE direction. Some roads might be too WIDE (eq. ETS2 roadlooks with minim) and for these the results will need to be negated.",
            "1. TLDR": {},
            "2. Raw Data": {},
            "3. Per Name Compatible Offsets": {},
        }

        i = 0
        start_time = time.time()
        count = len(self.roads)
        for road in self.roads:
            try:
                errors = road_helpers.get_error_for_road(road, self)

                if len(errors) == 0:
                    i += 1
                    continue

                if max(errors) > 0.25 and min(errors) > 0.1:
                    if road.road_look.name not in export["2. Raw Data"]:
                        export["2. Raw Data"][road.road_look.name] = []

                    export["2. Raw Data"][road.road_look.name].append(
                        {
                            "uid": road.uid,
                            "location": (road.x, road.y),
                            "errors": errors,
                            "object": road,
                        }
                    )

                if i % 500 == 0:
                    total_ram = psutil.virtual_memory().total
                    ram = psutil.virtual_memory().available
                    eta = ((time.time() - start_time) / (i + 1)) * (count - i)
                    eta_string = time.strftime("%H:%M:%S", time.gmtime(eta))

                    print(
                        f"Processed {i}/{count} roads ({i / count * 100:.1f}%), RAM usage: {(1 - ram / total_ram) * 100:.1f}%, ETA: {eta_string}     ",
                        end="\r",
                    )
                    if 1 - ram / total_ram < 0.05:
                        logging.warning("RAM usage at 95%, stopping calculation.")
                        break
            except Exception:
                logging.exception(
                    f"Error calculating road {road.uid} ({road.x}, {road.y})"
                )
                pass

            i += 1

        for road_name in export["2. Raw Data"]:
            average_offset = 0
            average_internal_offset = 0

            if len(export["2. Raw Data"][road_name]) < 3:
                logging.warning(
                    f"Ignoring road [dim]{road_name}[/dim] with only {len(export['2. Raw Data'][road_name])} errors found."
                )
                for road in export["2. Raw Data"][road_name]:
                    del road["object"]
                continue

            for road in export["2. Raw Data"][road_name]:
                average_offset += sum(road["errors"]) / len(road["errors"])
                average_internal_offset += road_helpers.GetOffset(road["object"])
                del road["object"]

            average_internal_offset /= len(export["2. Raw Data"][road_name])
            average_offset /= len(export["2. Raw Data"][road_name])

            # (0.00, 0.25, 0.50, 0.75 ...)
            average_offset = round(average_offset * 4) / 4
            average_internal_offset = round(average_internal_offset * 4) / 4

            export["1. TLDR"][road_name] = {
                "1. Off by around": average_offset,
                "2. Current offset": average_internal_offset,
                "3. Recommended offset (DOUBLECHECK IN GAME!)": 4.5
                + (average_internal_offset - 4.5)
                + average_offset,
                "4. Comment": "Recommended offset is calculated based on the average error. Please note that if there are a lot of offsets below that are close to 0 off, then it is likely that the current offset is fine and it is a false flag.",
            }
            export["3. Per Name Compatible Offsets"][road_name] = (
                4.5 + (average_internal_offset - 4.5) + average_offset
            )

        filename = "Plugins/Map/road_error.json"
        with open(filename, "w") as f:
            json.dump(export, f, indent=4)

        logging.warning(
            f"Found {len(export['1. TLDR'])} roadlooks with errors, saved to [dim]{filename}[/dim]."
        )
