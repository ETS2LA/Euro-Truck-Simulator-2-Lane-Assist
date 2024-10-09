from ETS2LA.modules.SDKController.main import SCSController
from classes import MapData, Road, Prefab
from route.classes import RouteSection
import math

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

# MARK: Data variables
map: MapData = None
"""This includes all of the ETS2 data that can be accessed."""
current_sector_roads: list[Road] = []
"""The roads in the current sector."""
current_sector_prefabs: list[Prefab] = []
"""The prefabs in the current sector."""
route_plan: list[RouteSection] = []

# MARK: Options
heavy_calculations_this_frame: int = 0
"""How many heavy calculations map has done this frame."""
allowed_heavy_calculations: int = 50
"""How many heavy calculations map is allowed to do per frame."""
lane_change_distance_per_kph: float = 1
"""Over how many meters distance will the truck change lanes per kph of speed. Basically at 50kph, the truck will change lanes over 25m, assuming a value of 0.5."""
minimum_lane_change_distance: float = 10
"""The minimum distance the truck will change lanes over."""
route_plan_length: int = 3
"""How many route sections the planner will plan ahead for."""

def UpdateData(api_data):
    global heavy_calculations_this_frame, truck_speed, truck_x, truck_y, truck_z, truck_rotation, current_sector_x, current_sector_y, current_sector_prefabs, current_sector_roads, truck_indicating_left, truck_indicating_right
    heavy_calculations_this_frame = 0
    
    truck_indicating_left = api_data["truckBool"]["blinkerLeftActive"]
    truck_indicating_right = api_data["truckBool"]["blinkerRightActive"]
    
    truck_speed = api_data["truckFloat"]["speed"]
    
    truck_x = api_data["truckPlacement"]["coordinateX"]
    truck_y = api_data["truckPlacement"]["coordinateY"]
    truck_z = api_data["truckPlacement"]["coordinateZ"]
    
    current_sector_x, current_sector_y = map.get_sector_from_coordinates(truck_x, truck_z)
    
    current_sector_prefabs = map.get_sector_prefabs_by_sector([current_sector_x, current_sector_y])
    current_sector_roads = map.get_sector_roads_by_sector([current_sector_x, current_sector_y])
    
    rotationX = api_data["truckPlacement"]["rotationX"]
    angle = rotationX * 360
    if angle < 0: angle = 360 + angle
    truck_rotation = math.radians(angle)