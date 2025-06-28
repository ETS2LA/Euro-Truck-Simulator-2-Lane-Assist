# The map files need a full rewrite. I sympathize with anyone
# who tries to read the code. We don't have time for a rewrite
# until after release.

from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import *
from ETS2LA.Controls import ControlEvent

# Imports to fix circular imports
import Plugins.Map.utils.prefab_helpers as ph
import Plugins.Map.utils.road_helpers as rh
import Plugins.Map.utils.math_helpers as mh

# ETS2LA imports
import Plugins.Map.utils.data_handler as data_handler
import Plugins.Map.utils.data_reader as data_reader
from Plugins.Map.ui import SettingsMenu

from Plugins.Map.utils import ui_operations as ui
from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.settings as settings
from ETS2LA.Handlers.sounds import Play
import ETS2LA.variables as variables
import Plugins.Map.classes as c

import numpy as np
import threading
import importlib
import time

navigation = importlib.import_module("Plugins.Map.navigation.navigation")
planning = importlib.import_module("Plugins.Map.route.planning")
driving = importlib.import_module("Plugins.Map.route.driving")
im = importlib.import_module("Plugins.Map.utils.internal_map")
oh = importlib.import_module("Plugins.Map.utils.offset_handler")  
last_plan_hash = hash(open(planning.__file__, encoding="utf-8").read())
last_drive_hash = hash(open(driving.__file__).read())
last_nav_hash = hash(open(navigation.__file__, encoding="utf-8").read())
last_im_hash = hash(open(im.__file__).read())
last_oh_hash = hash(open(oh.__file__, encoding="utf-8").read())  

UPDATING_OFFSET_CONFIG = False
DEVELOPER_PRINTING = False

enable_disable = ControlEvent(
    "toggle_map",
    "Toggle Steering",
    "button",
    description="When Map is running this will toggle it on/off.",
    default="n"
)

class Plugin(ETS2LAPlugin):
    author = [Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )]
    
    description = PluginDescription(
        name="plugins.map",
        description="plugins.map.description",
        version="2.0.0",
        modules=["SDKController", "TruckSimAPI", "Steering", "Route"],
        tags=["Base", "Steering"],
        ui_filename="ui.py",
        fps_cap=20
    )
    last_dest_company = None 
    
    controls = [enable_disable]
    
    pages = [SettingsMenu]
    
    steering_smoothness: float = 0.2
    MAP_INITIALIZED = False
    
    last_city_update = time.time()
    
    def imports(self):
        global json, data, time, math, sys, logging
        # General imports
        import Plugins.Map.data as data
        import logging
        import json
        import math
        import sys

        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def update_road_data(self):
        global UPDATING_OFFSET_CONFIG
        UPDATING_OFFSET_CONFIG = True
        result = ui.update_road_data()   
        UPDATING_OFFSET_CONFIG = False
        return result

    def execute_offset_update(self):
        global UPDATING_OFFSET_CONFIG
        UPDATING_OFFSET_CONFIG = True
        result = ui.execute_offset_update()   
        UPDATING_OFFSET_CONFIG = False
        return result
        
    def generate_rules(self):
        global UPDATING_OFFSET_CONFIG
        UPDATING_OFFSET_CONFIG = True
        result = ui.generate_rules()   
        UPDATING_OFFSET_CONFIG = False
        return result
        
    def clear_lane_offsets(self):
        global UPDATING_OFFSET_CONFIG
        UPDATING_OFFSET_CONFIG = True
        result = ui.clear_lane_offsets()   
        UPDATING_OFFSET_CONFIG = False
        return result
        
    def clear_rules(self):
        global UPDATING_OFFSET_CONFIG
        UPDATING_OFFSET_CONFIG = True
        result = ui.clear_rules()   
        UPDATING_OFFSET_CONFIG = False
        return result

    def trigger_data_update(self):
        return ui.trigger_data_update(self)

    def use_auto_offset(self):
        global UPDATING_OFFSET_CONFIG
        UPDATING_OFFSET_CONFIG = True
        result = ui.use_auto_offset()   
        UPDATING_OFFSET_CONFIG = False
        return result   

    def CheckHashes(self):
        global last_nav_hash, last_drive_hash, last_plan_hash, last_im_hash, last_oh_hash
        logging.info("Starting navigation module file monitor")
        while True:
            try:
                new_nav_hash = hash(open(navigation.__file__, encoding='utf-8').read())
                new_drive_hash = hash(open(driving.__file__, encoding='utf-8').read())
                new_plan_hash = hash(open(planning.__file__, encoding='utf-8').read())
                new_im_hash = hash(open(im.__file__, encoding='utf-8').read())
                new_oh_hash = hash(open(oh.__file__, encoding='utf-8').read())  
                if new_nav_hash != last_nav_hash:
                    last_nav_hash = new_nav_hash
                    logging.info("Navigation module changed, reloading...")
                    importlib.reload(navigation)
                    logging.info("Successfully reloaded navigation module")
                    if data.use_navigation:
                        logging.info("Recalculating path with reloaded module...")
                        data.update_navigation_plan = True
                        
                if new_drive_hash != last_drive_hash:
                    last_drive_hash = new_drive_hash
                    logging.info("Driving module changed, reloading...")
                    importlib.reload(driving)
                    logging.info("Successfully reloaded driving module")
                if new_plan_hash != last_plan_hash:
                    last_plan_hash = new_plan_hash
                    logging.info("Planning module changed, reloading...")
                    importlib.reload(planning)
                    data.route_plan = []
                    logging.info("Successfully reloaded planning module")
                if new_im_hash != last_im_hash:
                    last_im_hash = new_im_hash
                    logging.info("Internal map module changed, reloading...")
                    importlib.reload(im)
                    logging.info("Successfully reloaded internal map module")
                if new_oh_hash != last_oh_hash:
                    last_oh_hash = new_oh_hash
                    logging.info("Offset handler module changed, reloading...")
                    importlib.reload(oh)
                    logging.info("Successfully reloaded offset handler module")
            except Exception as e:
                logging.error(f"Error monitoring modules: {e}")
            time.sleep(1)
        
    @events.on("toggle_map")
    def on_toggle_map(self, state:bool):
        if not state:
            return # release event
        
        data.enabled = not data.enabled
        Play("start" if data.enabled else "end")
        self.globals.tags.status = {"Map": data.enabled}
        
    @events.on("JobFinished")
    def JobFinished(self, *args, **kwargs):
        data.dest_company = None
        data.route_plan = []
        data.navigation_plan = []
        data.update_navigation_plan = True
        data.last_navigation_update = 0

    def init(self):
        """Initialize the plugin"""
        try:
            self.steering_smoothness = settings.Get("Map", "SteeringSmoothTime", 0.2)

            data.controller = self.modules.SDKController.SCSController()
            data.plugin = self

            global api, steering
            api = self.modules.TruckSimAPI
            api.TRAILER = True
            steering = self.modules.Steering
            steering.OFFSET = 0
            steering.SMOOTH_TIME = self.steering_smoothness
            steering.IGNORE_SMOOTH = False
            steering.SENSITIVITY = 1.2

            settings.Listen("Map", self.UpdateSteeringSettings)

            data.plugin.globals.tags.lane_change_status = "idle"
            c.data = data  # set the classes data variable
            data_handler.plugin = self
            self.state.reset()

            self.globals.tags.status = {"Map": data.enabled}
            self.settings_menu = SettingsMenu()
            self.settings_menu.plugin = self
            
            if self.settings.downloaded_data is None:
                self.settings.downloaded_data = ""
                
            if self.settings.selected_data is None:
                self.settings.selected_data = ""

            # Start navigation file monitor
            threading.Thread(target=self.CheckHashes, daemon=True).start()
            logging.info("Map plugin initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Error initializing Map plugin: {e}", exc_info=True)
            return False
                
    def MapWindowInitialization(self):
        if not data.map_initialized and data.internal_map:
                im.InitializeMapWindow()
                self.MAP_INITIALIZED = True

        if data.map_initialized and not data.internal_map:
            im.RemoveWindow()
            self.MAP_INITIALIZED = False
            
    def UpdateNavigation(self):
        if time.perf_counter() - data.last_navigation_update > 5 or data.update_navigation_plan:
            data.update_navigation_plan = False
            navigation.get_path_to_destination()
            data.last_navigation_update = time.perf_counter()

    def UpdateSteeringSettings(self, settings: dict):
        self.steering_smoothness = self.settings.SteeringSmoothTime
        steering.SMOOTH_TIME = self.steering_smoothness

    def run(self):
        data_start_time = time.perf_counter()
        is_different_data = (self.settings.selected_data != "" and self.settings.selected_data != self.settings.downloaded_data)
        if not data.data_downloaded or is_different_data:
            data.data_downloaded = False
            
            if data_handler.IsDownloaded(data.data_path) and not is_different_data:
                self.state.text = "Preparing to load data..."
                data_reader.path = data.data_path
                del data.map
                data.map = None
                data.map = data_reader.ReadData(state=self.state)
                data.data_downloaded = True
                data.data_needs_update = True
                self.state.reset()
                return
                
            if self.settings.selected_data and self.settings.selected_data != "":
                data_handler.UpdateData(self.settings.selected_data)
                return
            
            self.state.text = "Waiting for game selection in the Settings -> Map..."
            return
        
        data_time = time.perf_counter() - data_start_time
        
        try:
            data_update_start_time = time.perf_counter()
            api_data = api.run()
            data.UpdateData(api_data)
            data_update_time = time.perf_counter() - data_update_start_time

            if data.calculate_steering:
                # Update route plan and steering
                planning_start_time = time.perf_counter()
                planning.UpdateRoutePlan()
                planning_time = time.perf_counter() - planning_start_time
                
                steering_start_time = time.perf_counter()
                steering_value = driving.GetSteering()

                if steering_value is not None:
                    steering_value = steering_value / 180
                    if steering_value > 0.95:
                        steering_value = 0.95
                    elif steering_value < -0.95:
                        steering_value = -0.95

                    steering.run(value=steering_value, sendToGame=data.enabled, drawLine=False)
                else:
                    logging.warning("Invalid steering value received")
                    
                steering_time = time.perf_counter() - steering_start_time
            else:
                data.route_points = []

            internal_map_start_time = time.perf_counter()
            if data.internal_map:
                self.MapWindowInitialization()
                im.DrawMap()
            internal_map_time = time.perf_counter() - internal_map_start_time

            navigation_start_time = time.perf_counter()
            self.UpdateNavigation()
            navigation_time = time.perf_counter() - navigation_start_time

            external_map_start_time = time.perf_counter()
            if data.external_data_changed:
                external_data = json.dumps(data.external_data)
                self.globals.tags.map = json.loads(external_data)
                self.globals.tags.map_update_time = data.external_data_time
                data.external_data_changed = False
                
            external_map_time = time.perf_counter() - external_map_start_time

        except Exception as e:
            logging.error(f"Error in Map plugin run loop: {e}", exc_info=True)
            data.route_points = []  # Clear route points on error

        external_data_start_time = time.perf_counter()
        try:
            if data.calculate_steering and data.route_plan is not None and len(data.route_plan) > 0:
                if type(data.route_plan[0].items[0].item) == c.Road:
                    self.globals.tags.next_intersection_distance = data.route_plan[0].distance_left()
                elif len(data.route_plan) > 1 and type(data.route_plan[1].items[0].item) == c.Road:
                    self.globals.tags.next_intersection_distance = data.route_plan[0].distance_left() + data.route_plan[1].distance_left()
                else:
                    self.globals.tags.next_intersection_distance = 0
                
                if len(data.route_plan) > 1 and type(data.route_plan[1].items[0].item) == c.Prefab:
                    self.globals.tags.next_intersection_lane = data.route_plan[1].lane_index
                    self.globals.tags.next_intersection_uid = data.route_plan[1].items[0].item.uid
                    
                if type(data.route_plan[0].items[0].item) == c.Road:
                    self.globals.tags.road_type = "highway" if "hw" in data.route_plan[0].items[0].item.road_look.name else "normal"
                else:
                    self.globals.tags.road_type = "normal"

                self.globals.tags.route_information = [item.information_json() for item in data.route_plan]
            else:
                self.globals.tags.next_intersection_distance = 1
                self.globals.tags.road_type = "none"
        except:
            pass
        external_data_time = time.perf_counter() - external_data_start_time
        
        try:
            frametime = self.performance[-1][1]
            if frametime > 0.13 and not data.disable_fps_notices: # ~7.7fps
                if self.state.text == "" or "low FPS" in self.state.text: # Don't overwrite other states
                    self.state.text = f"Warning: Steering might be compromised due to low FPS. ({1/frametime:.0f}fps)"
            else:
                if "low FPS" in self.state.text:
                    self.state.text = ""
        except:
            pass

        if DEVELOPER_PRINTING and variables.DEVELOPMENT_MODE and not UPDATING_OFFSET_CONFIG:
            if (time.perf_counter() - data_start_time) * 1000 > 100:
                try:
                    print(f"Map plugin run time: {(time.perf_counter() - data_start_time) * 1000:.2f}ms")
                    print(f"- Data time: {data_time * 1000:.2f}ms")
                    print(f"- Data update time: {data_update_time * 1000:.2f}ms")
                    print(f"- Planning time: {planning_time * 1000:.2f}ms")
                    print(f"- Steering time: {steering_time * 1000:.2f}ms")
                    print(f"- Internal map time: {internal_map_time * 1000:.2f}ms")
                    print(f"- Navigation time: {navigation_time * 1000:.2f}ms")
                    print(f"- External map time: {external_map_time * 1000:.2f}ms")
                    print(f"- External data time: {external_data_time * 1000:.2f}ms")
                except:
                    pass
        
        self.globals.tags.steering_points = [point.tuple() for point in data.route_points]
        
        try:
            if self.last_city_update + 5 < time.time():
                self.last_city_update = time.time()
                
                # Find the closest city to the truck
                cities = data.map.cities
                closest = None
                closest_distance = math.inf
                for city in cities:
                    distance = math.sqrt((data.truck_x - city.x) ** 2 + (data.truck_z - city.y) ** 2)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest = city
                        
                if closest:
                    self.globals.tags.closest_city = closest.name
                    self.globals.tags.closest_city_distance = closest_distance
                    self.globals.tags.closest_country = closest.country_token.capitalize()
        except:
            pass
        
        # Update angle and distance to the closest road.
        try:
            roads = data.current_sector_roads
            prefabs = data.current_sector_prefabs
            if roads and prefabs:
                found = False
                xy_position = c.Position(data.truck_x, data.truck_z, data.truck_y)
                for road in roads:
                    if road.bounding_box.is_in(xy_position):
                        found = True
                        break
                    
                for prefab in prefabs:
                    if prefab.bounding_box.is_in(xy_position):
                        found = True
                        break
                    
                if found:
                    self.globals.tags.closest_road_distance = 0
                    self.globals.tags.closest_road_angle = 0
                else:
                    # Distance
                    truck_position = c.Position(data.truck_x, data.truck_y, data.truck_z)
                    closest_road = min(roads, key=lambda r: r.distance_to(truck_position))
                    self.globals.tags.closest_road_distance = closest_road.distance_to(xy_position)
                    
                    # Angle
                    closest_point = min(closest_road.points, key=lambda p: p.distance_to(truck_position))
                    closest_point = closest_point - truck_position
                    
                    forward_vector = [-math.sin(data.truck_rotation), -math.cos(data.truck_rotation)]
                    to_road = closest_point.tuple(xz=True)
                    forward_vector = np.array(forward_vector) / np.linalg.norm(forward_vector)
                    to_road = np.array(to_road) / np.linalg.norm(to_road)

                    dot = np.dot(forward_vector, to_road)
                    angle = np.arccos(dot) * (180 / np.pi)
                    
                    self.globals.tags.closest_road_angle = angle
            
            else:
                self.globals.tags.closest_road_distance = 0
                self.globals.tags.closest_road_angle = 0
        except:
            self.globals.tags.closest_road_distance = 0
            self.globals.tags.closest_road_angle = 0
            pass
