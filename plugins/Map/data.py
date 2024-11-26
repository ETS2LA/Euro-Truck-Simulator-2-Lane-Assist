from plugins.Map.classes import MapData, Road, Prefab, Position, Model, City, CompanyItem, Node
from modules.SDKController.main import SCSController
from plugins.Map.route.classes import RouteSection
import ETS2LA.backend.settings as settings
import math
import time

# MARK: Variables
plugin = None
"""The plugin object."""
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
dest_city: City = None
"""The destination city."""
dest_city_token: str = None
"""The destination city token."""
dest_company: CompanyItem = None
"""The destination company."""
dest_company_token: str = None
"""The destination company token."""

# MARK: Data variables
map: MapData = None
"""This includes all of the ETS2 data that can be accessed."""
current_sector_roads: list[Road] = []
"""The roads in the current sector."""
current_sector_prefabs: list[Prefab] = []
"""The prefabs in the current sector."""
current_sector_models: list[Model] = []
"""The models in the current sector."""
current_sectors: list[tuple[int, int]] = []
"""The sectors that are currently loaded."""
route_plan: list[RouteSection] = []
"""The current route plan."""
route_points: list[Position] = []
"""The current route points."""
navigation_plan: list[Node] = []
"""List of nodes that will drive the truck to the destination."""
circles: list[Position] = []
"""Circles to draw on the map."""

# MARK: Options
amount_of_points: int = 50
"""How many points will the map calculate ahead. More points = more overhead moving data."""
heavy_calculations_this_frame: int = -1
"""How many heavy calculations map has done this frame."""
allowed_heavy_calculations: int = 500
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
sector_size = settings.Get("Map", "SectorSize", 200)
"""The size of each sector in meters."""
load_distance = settings.Get("Map", "LoadDistance", 500)
"""The radius around the truck in meters that should be loaded."""
use_navigation = settings.Get("Map", "UseNavigation", False)
"""Whether we should drive along the navigation path or just use the basic route planner."""

# MARK: Return values
external_data = {}
"""Data that will be sent to other plugins and the frontend."""
external_data_time = 0
"""Time the external data was last updated."""

# MARK: Flags
data_needs_update = False
"""Does the external data need to be updated?"""
external_data_changed = False
"""Flag for the main file to update the external data in the main process."""
elevation_data_sent = False
"""Whether the elevation data has been sent to the main process or not."""
update_navigation_plan = False
"""Whether we should calculate a new plan to drive to the destination."""


def UpdateData(api_data):
    global heavy_calculations_this_frame
    global truck_speed, truck_x, truck_y, truck_z, truck_rotation
    global current_sector_x, current_sector_y, current_sector_prefabs, current_sector_roads, last_sector, current_sector_models, current_sectors
    global truck_indicating_left, truck_indicating_right
    global external_data, data_needs_update, external_data_changed, external_data_time
    global dest_city, dest_company, dest_city_token, dest_company_token

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
        sectors_to_load = map.get_sectors_for_coordinate_and_distance(truck_x, truck_z, load_distance)
        current_sectors = sectors_to_load
        
        current_sector_prefabs = []
        current_sector_roads = []
        current_sector_models = []
        for sector in sectors_to_load:
            current_sector_prefabs += map.get_sector_prefabs_by_sector(sector)
            current_sector_roads += map.get_sector_roads_by_sector(sector)
            current_sector_models += map.get_sector_models_by_sector(sector)
        
        data_needs_update = True

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
    
    dst_city_token = api_data["configString"]["cityDstId"]
    dst_company_token = api_data["configString"]["compDstId"]
    if dst_city_token != dest_city_token:
        dest_city_token = dst_city_token
        dest_city = map.get_city_by_token(dst_city_token)

    if dst_company_token != dest_company_token:
        dest_company_token = dst_company_token
        dest_company = map.get_company_item_by_token_and_city(dst_company_token, dst_city_token)
    
    
def UpdateSettings(settings: dict):
    global internal_map, calculate_steering, sector_size, use_navigation
    internal_map = settings["InternalVisualisation"]
    calculate_steering = settings["ComputeSteeringData"]
    sector_size = settings["SectorSize"]
    load_distance = settings["LoadDistance"]
    use_navigation = settings["UseNavigation"]
    
settings.Listen("Map", UpdateSettings)