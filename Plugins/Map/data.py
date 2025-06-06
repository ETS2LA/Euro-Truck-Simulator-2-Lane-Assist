from Plugins.Map.classes import MapData, Road, Prefab, Position, Model, City, CompanyItem, Node, Elevation
from Modules.SDKController.main import SCSController
from Plugins.Map.route.classes import RouteSection
import ETS2LA.Utils.settings as settings
import math
import time
import os

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
trailer_x: float = 0
"""The first trailer X position."""
trailer_y: float = 0
"""The first trailer Y position."""
trailer_z: float = 0
"""The first trailer Z position."""
trailer_attached: bool = False
"""Whether the trailer is attached or not."""
current_sector_x: int = 0
"""The sector X coordinate corresponding to the truck's position."""
current_sector_y: int = 0
"""The sector Y coordinate corresponding to the truck's position."""
sector_center_x: float = 0
"""The world coordinate X for the center of the current sector."""
sector_center_y: float = 0
"""The world coordinate Y for the center of the current sector."""
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
current_sector_elevations: list[Elevation] = []
""""The elevations in the current sector."""
current_sectors: list[tuple[int, int]] = []
"""The sectors that are currently loaded."""
route_plan: list[RouteSection] = []
"""The current route plan."""
route_points: list[Position] = []
"""The current route points."""
navigation_plan: list = []
"""List of RouteNodes that will drive the truck to the destination."""
last_length: int = 0
"""The length of the navigation route we last calculated."""
circles: list[Position] = []
"""Circles to draw on the map."""
last_navigation_update: float = 0
"""The last time the navigation plan was updated."""
last_sound_played: float = 0
"""The last time a sound was played."""
sound_play_interval: float = 10 # seconds
"""The interval between each sound play."""
frames_off_path: int = 0
"""How many frames the truck has been off the path."""
data_path = os.path.join(os.path.dirname(__file__), "data")
"""Where the app should download the data."""

# MARK: Options
amount_of_points: int = 50
"""How many points will the map calculate ahead. More points = more overhead moving data."""
heavy_calculations_this_frame: int = -1
"""How many heavy calculations map has done this frame."""
allowed_heavy_calculations: int = 500
"""How many heavy calculations map is allowed to do per frame."""
lane_change_distance_per_kph: float = 1
"""Over how many meters distance will the truck change lanes per kph of speed. Basically at 50kph, the truck will change lanes over 25m, assuming a value of 0.5."""
minimum_lane_change_distance: float = 20
"""The minimum distance the truck will change lanes over."""
route_plan_length: int = 3
"""How many route sections the planner will plan ahead for."""
internal_map = settings.Get("Map", "InternalVisualisation", False)
"""Whether the internal map is enabled or not."""
map_initialized = False
"""Whether the map window has been initialized or not."""
calculate_steering = settings.Get("Map", "ComputeSteeringData", True)
"""Whether the map should calculate steering data or not."""
sector_size = settings.Get("Map", "SectorSize", 300)
"""The size of each sector in meters."""
load_distance = settings.Get("Map", "LoadDistance", 600)
"""The radius around the truck in meters that should be loaded."""
use_navigation = settings.Get("Map", "UseNavigation", True)
"""Whether we should drive along the navigation path or just use the basic route planner."""
auto_accept_threshold = settings.Get("Map", "AutoAcceptThreshold", 100)
"""The distance in meters from the destination where the truck will automatically accept the current navigation plan."""
auto_deny_threshold = settings.Get("Map", "AutoDenyThreshold", 100)
"""The distance in meters from the destination where the truck will automatically deny the current navigation plan."""
drive_based_on_trailer = settings.Get("Map", "DriveBasedOnTrailer", True)
"""Move the steering point towards the trailer at low speeds."""
send_elevation_data = settings.Get("Map", "SendElevationData", False)
"""Whether to send elevation data or not."""
export_road_offsets = settings.Get("Map", "ExportRoadOffsets", False)
"""Whether to export the road offsets at startup. Only works in development mode."""
disable_fps_notices = settings.Get("Map", "DisableFPSNotices", False)
"""Whether to disable the FPS notices or not."""
override_lane_offsets= settings.Get("Map", "Override Lane Offsets", True)
"""Whether to override the existing lane offsets or not."""
use_auto_offset_data = settings.Get("Map", "UseAutoOffsetData", False)
"""Whether to use the auto offset data or not. This will use the offsets from the game instead of the ones calculated by the plugin."""
right_hand_drive = settings.Get("Map", "RightHandDrive", False)
"""Whether the game is in right-hand drive mode or not. This will change the direction of the steering wheel."""

# MARK: Return values
external_data = {}
"""Data that will be sent to other plugins and the frontend."""
external_data_time = 0
"""Time the external data was last updated."""

# MARK: Flags
data_downloaded = False
"""Whether the app can continue because the data has been downloaded."""
data_needs_update = False
"""Does the external data need to be updated?"""
external_data_changed = False
"""Flag for the main file to update the external data in the main process."""
update_navigation_plan = False
"""Whether we should calculate a new plan to drive to the destination."""

# MARK: Update functions
def UpdateData(api_data):
    global heavy_calculations_this_frame
    global truck_speed, truck_x, truck_y, truck_z, truck_rotation
    global current_sector_x, current_sector_y, current_sector_prefabs, current_sector_roads, last_sector, current_sector_models, current_sectors, current_sector_elevations
    global truck_indicating_left, truck_indicating_right
    global external_data, data_needs_update, external_data_changed, external_data_time
    global dest_city, dest_company, dest_city_token, dest_company_token
    global trailer_x, trailer_y, trailer_z, trailer_attached
    global sector_center_x, sector_center_y

    heavy_calculations_this_frame = 0
    
    truck_indicating_left = api_data["truckBool"]["blinkerLeftActive"]
    truck_indicating_right = api_data["truckBool"]["blinkerRightActive"]
    
    truck_speed = api_data["truckFloat"]["speed"]
    
    truck_x = api_data["truckPlacement"]["coordinateX"]
    truck_y = api_data["truckPlacement"]["coordinateY"]
    truck_z = api_data["truckPlacement"]["coordinateZ"]
    
    current_sector_x, current_sector_y = map.get_sector_from_coordinates(truck_x, truck_z)
    sector_center_x, sector_center_y = map.get_world_center_for_sector((current_sector_x, current_sector_y))
    
    plugin.globals.tags.sector_center = (sector_center_x, sector_center_y)
    
    if (current_sector_x, current_sector_y) != last_sector:
        last_sector = (current_sector_x, current_sector_y)
        sectors_to_load = map.get_sectors_for_coordinate_and_distance(truck_x, truck_z, load_distance)
        current_sectors = sectors_to_load
        
        current_sector_prefabs = []
        current_sector_roads = []
        current_sector_models = []
        current_sector_elevations = []
        for sector in sectors_to_load:
            current_sector_prefabs += map.get_sector_prefabs_by_sector(sector)
            current_sector_roads += map.get_sector_roads_by_sector(sector)
            current_sector_models += map.get_sector_models_by_sector(sector)
            current_sector_elevations += map.get_sector_elevations_by_sector(sector)
        
        data_needs_update = True

    if data_needs_update:
        external_data = {
            "prefabs": [prefab.json() for prefab in current_sector_prefabs],
            "roads": [road.json() for road in current_sector_roads],
            "models": [model.json() for model in current_sector_models],
            "elevations": [elevation.json() for elevation in current_sector_elevations] if send_elevation_data else []
        }
        
        external_data_changed = True
        external_data_time = time.perf_counter()
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
        
    if not drive_based_on_trailer:
        trailer_attached = False
    else:
        trailer = api_data["trailers"][0]
        if not trailer["comBool"]["attached"]:
            trailer_x = 0
            trailer_y = 0
            trailer_z = 0
            trailer_attached = False
        else:
            trailer_x = trailer["comDouble"]["worldX"]
            trailer_y = trailer["comDouble"]["worldY"]
            trailer_z = trailer["comDouble"]["worldZ"]
            trailer_attached = True
    
    
def UpdateSettings(settings: dict):
    global internal_map, calculate_steering, sector_size, use_navigation
    global auto_accept_threshold, auto_deny_threshold, load_distance
    global drive_based_on_trailer, send_elevation_data, export_road_offsets
    global disable_fps_notices, override_lane_offsets, use_auto_offset_data
    global right_hand_drive
    internal_map = settings["InternalVisualisation"]
    calculate_steering = settings["ComputeSteeringData"]
    sector_size = settings["SectorSize"]
    load_distance = settings["LoadDistance"]
    use_navigation = settings["UseNavigation"]
    auto_accept_threshold = settings["AutoAcceptThreshold"]
    auto_deny_threshold = settings["AutoDenyThreshold"]
    drive_based_on_trailer = settings["DriveBasedOnTrailer"]
    send_elevation_data = settings["SendElevationData"]
    export_road_offsets = settings["ExportRoadOffsets"]
    disable_fps_notices = settings["DisableFPSNotices"]
    override_lane_offsets = settings["Override Lane Offsets"]
    use_auto_offset_data = settings["UseAutoOffsetData"]
    right_hand_drive = settings["RightHandDrive"]

    global data_needs_update
    data_needs_update = True
    
settings.Listen("Map", UpdateSettings)
