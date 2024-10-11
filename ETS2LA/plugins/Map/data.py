from ETS2LA.modules.SDKController.main import SCSController
from classes import MapData, Road, Prefab, Position, Model
import ETS2LA.backend.settings as settings
from route.classes import RouteSection
import math
import time

# MARK: Variables
runner = None
"""The plugin runner object."""
controller: SCSController = None
"""The controller that can be used to control the game."""
truck_indicating_right: bool = False
"""Whether the truck is indicating right or not."""
truck_indicating_left: bool = False
"""Whether the truck is indicating left or not."""
truck_speed: float = 0
"""Truck speed updated at the start of each map frame. (m/s)"""
truck_rotation: float = 0
"""Truck rotation updated at the start of each map frame."""
truck_x: float = 0
"""Truck X position updated at the start of each map frame."""
truck_y: float = 0
"""Truck Y position updated at the start of each map frame."""
truck_z: float = 0
"""Truck Z position updated at the start of each map frame."""
current_sector_x: int = 0
"""The sector X coordinate corresponding to the truck's position."""
current_sector_y: int = 0
"""The sector Y coordinate corresponding to the truck's position."""
enabled: bool = False
"""Whether the map steering is enabled or not."""
last_sector: tuple[int, int] = None
"""The last sector the truck was in."""

# MARK: Data variables
map: MapData = None
"""This includes all of the ETS2 data that can be accessed."""
current_sector_roads: list[Road] = []
"""The roads in the current sector."""
current_sector_prefabs: list[Prefab] = []
"""The prefabs in the current sector."""
current_sector_models: list[Model] = []
"""The models in the current sector."""
route_plan: list[RouteSection] = []
"""The current route plan."""
route_points: list[Position] = []

# MARK: Options
heavy_calculations_this_frame: int = -1
"""How many heavy calculations map has done this frame."""
allowed_heavy_calculations: int = 50
"""How many heavy calculations map is allowed to do per frame."""
lane_change_distance_per_kph: float = 1
"""Over how many meters distance will the truck change lanes per kph of speed. Basically at 50kph, the truck will change lanes over 25m, assuming a value of 0.5."""
minimum_lane_change_distance: float = 10
"""The minimum distance the truck will change lanes over."""
route_plan_length: int = 3
"""How many route sections the planner will plan ahead for."""
internal_map = settings.Get("Map", "InternalVisualisation", False)
"""Whether the internal map is enabled or not."""
map_initialized = False
"""Whether the map window has been initialized or not."""
calculate_steering = settings.Get("Map", "ComputeSteeringData", True)
"""Whether the map should calculate steering data or not."""

# MARK: Return values
external_data = {}
"""Data that will be sent to other plugins and the frontend."""
data_needs_update = False
"""Does the external data need to be updated?"""
external_data_changed = False
"""Flag for the main file to update the external data in the main process."""
external_data_time = 0
"""Time the external data was last updated."""
elevation_data_sent = False
"""Whether the elevation data has been sent to the main process or not."""

def UpdateData(api_data):
    global heavy_calculations_this_frame
    global truck_speed, truck_x, truck_y, truck_z, truck_rotation
    global current_sector_x, current_sector_y, current_sector_prefabs, current_sector_roads, last_sector, current_sector_models
    global truck_indicating_left, truck_indicating_right
    global external_data, data_needs_update, external_data_changed, external_data_time

    heavy_calculations_this_frame = 0
    
    truck_indicating_left = api_data["truckBool"]["blinkerLeftActive"]
    truck_indicating_right = api_data["truckBool"]["blinkerRightActive"]
    
    truck_speed = api_data["truckFloat"]["speed"]
    
    truck_x = api_data["truckPlacement"]["coordinateX"]
    truck_y = api_data["truckPlacement"]["coordinateY"]
    truck_z = api_data["truckPlacement"]["coordinateZ"]
    
    current_sector_x, current_sector_y = map.get_sector_from_coordinates(truck_x, truck_z)
    
    if (current_sector_x, current_sector_y) != last_sector:
        last_sector = (current_sector_x, current_sector_y)
        current_sector_prefabs = map.get_sector_prefabs_by_sector((current_sector_x, current_sector_y))
        current_sector_roads = map.get_sector_roads_by_sector((current_sector_x, current_sector_y))
        current_sector_models = map.get_sector_models_by_sector((current_sector_x, current_sector_y))
    
    if data_needs_update:
        external_data = {
            "prefabs": [prefab.json() for prefab in current_sector_prefabs],
            "roads": [road.json() for road in current_sector_roads],
            "models": [model.json() for model in current_sector_models],
        }
        
        external_data_changed = True
        external_data_time = time.time()
        data_needs_update = False
    
    rotationX = api_data["truckPlacement"]["rotationX"]
    angle = rotationX * 360
    if angle < 0: angle = 360 + angle
    truck_rotation = math.radians(angle)
    
def UpdateSettings(settings: dict):
    global internal_map, calculate_steering
    internal_map = settings["InternalVisualisation"]
    calculate_steering = settings["ComputeSteeringData"]
    
settings.Listen("Map", UpdateSettings)