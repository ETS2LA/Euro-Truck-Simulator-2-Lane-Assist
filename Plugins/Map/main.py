from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import *
from ETS2LA.Controls import ControlEvent

# Imports to fix circular imports
import Plugins.Map.utils.prefab_helpers as ph
import Plugins.Map.utils.road_helpers as rh
import Plugins.Map.utils.math_helpers as mh

# ETS2LA imports
from Plugins.Map.utils.data_reader import ReadData
from Plugins.Map.ui import SettingsMenu

from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.settings as settings
from ETS2LA.Handlers.sounds import Play
import ETS2LA.variables as variables
import Plugins.Map.classes as c

import threading
import importlib
navigation = importlib.import_module("Plugins.Map.navigation.navigation")
planning = importlib.import_module("Plugins.Map.route.planning")
driving = importlib.import_module("Plugins.Map.route.driving")
im = importlib.import_module("Plugins.Map.utils.internal_map")
last_plan_hash = hash(open(planning.__file__).read())
last_drive_hash = hash(open(driving.__file__).read())
last_nav_hash = hash(open(navigation.__file__).read())
last_im_hash = hash(open(im.__file__).read())

enable_disable = ControlEvent(
    "toggle_map",
    "Toggle Map Steering",
    "button",
    description="When Map is running this will toggle it on/off.",
    default="n"
)

toggle_navigate = ControlEvent(
    "toggle_navigate",
    "Toggle Map Navigation",
    "button",
    description="Quickly toggle Navigate on ETS2LA on/off."
)

class Plugin(ETS2LAPlugin):
    author = [Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    ), Author(
        name="WhyTrevorWhy",
        url="",
        icon=""
    )]
    
    description = PluginDescription(
        name="plugins.map",
        description="plugins.map.description",
        version="2.0.0",
        modules=["SDKController", "TruckSimAPI", "Steering"],
        tags=["Base", "Steering"]
    )
    last_dest_company = None
    
    controls = [enable_disable, toggle_navigate]
    
    fps_cap = 20
    settings_menu = SettingsMenu()
    
    steering_smoothness: float = 0.2
    MAP_INITIALIZED = False
    
    def imports(self):
        global json, data, time, math, sys, logging
        # General imports
        import Plugins.Map.data as data
        import logging
        import json
        import time
        import math
        import sys

        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def CheckHashes(self):
        global last_nav_hash, last_drive_hash, last_plan_hash, last_im_hash
        logging.info("Starting navigation module file monitor")
        while True:
            try:
                new_nav_hash = hash(open(navigation.__file__).read())
                new_drive_hash = hash(open(driving.__file__).read())
                new_plan_hash = hash(open(planning.__file__).read())
                new_im_hash = hash(open(im.__file__).read())
                if new_nav_hash != last_nav_hash:
                    last_nav_hash = new_nav_hash
                    logging.info("Navigation module changed, reloading...")
                    importlib.reload(navigation)
                    logging.info("Successfully reloaded navigation module")
                    if data.dest_company and data.use_navigation:
                        logging.info("Recalculating path with reloaded module...")
                        navigation.get_path_to_destination()
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
            except Exception as e:
                logging.error(f"Error monitoring modules: {e}")
            time.sleep(1)
        
    @events.on("toggle_map")
    def on_toggle_map(self, state:bool):
        if not state:
            return # release event
        
        data.enabled = not state
        Play("start" if data.enabled else "end")
        self.globals.tags.status = {"Map": data.enabled}
        
    @events.on("toggle_navigate")
    def on_toggle_navigate(self, state:bool):
        if not state:
            return # release event
        
        data.use_navigation = not data.use_navigation
        self.settings.UseNavigation = data.use_navigation
        
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

            # Initialize map data
            self.state.text = "Loading map data, please wait..."
            self.state.progress = 0
            time.sleep(0.1)
            try:
                data.map = ReadData(state=self.state)
                if not data.map:
                    logging.error("Failed to initialize map data")
                    return False
            except Exception as e:
                logging.error(f"Failed to read map data: {e}", exc_info=True)
                return False

            c.data = data  # set the classes data variable
            self.state.reset()

            self.globals.tags.status = {"Map": data.enabled}

            # Initialize routing mode tracking with validation
            self._last_routing_mode = settings.Get("Map", "RoutingMode")
            if self._last_routing_mode not in ["shortest", "smallRoads"]:
                logging.warning(f"Invalid routing mode {self._last_routing_mode}, resetting to 'shortest'")
                settings.Set("Map", "RoutingMode", "shortest")
                self._last_routing_mode = "shortest"

            self.settings_menu = SettingsMenu()
            self.settings_menu.plugin = self

            # Start navigation file monitor
            threading.Thread(target=self.CheckHashes, daemon=True).start()
            logging.info("Map plugin initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Error initializing Map plugin: {e}", exc_info=True)
            return False

    def CheckForRoutingModeChange(self):
        current_routing_mode = self.settings.RoutingMode
        if current_routing_mode != self._last_routing_mode and data.use_navigation:
            logging.info(f"Routing mode changed from {self._last_routing_mode} to {current_routing_mode}")
            self._last_routing_mode = current_routing_mode
            if data.dest_company:
                logging.info("Recalculating path with new routing mode...")
                navigation.get_path_to_destination()
                
    def MapWindowInitialization(self):
        if not data.map_initialized and data.internal_map:
                im.InitializeMapWindow()
                self.MAP_INITIALIZED = True

        if data.map_initialized and not data.internal_map:
            im.RemoveWindow()
            self.MAP_INITIALIZED = False
            
    def CheckDestinationCompany(self):
        if (data.dest_company != self.last_dest_company or data.update_navigation_plan) and data.use_navigation and time.perf_counter() - data.last_navigation_update > 5:
            logging.info(f"Destination company changed to {data.dest_company.token if data.dest_company else 'None'}, recalculating path...")
            self.last_dest_company = data.dest_company
            data.update_navigation_plan = False
            navigation.get_path_to_destination()
            if data.navigation_plan and data.navigation_plan != []:
                self.globals.tags.navigation_plan = data.navigation_plan
            else:
                self.globals.tags.navigation_plan = []
            data.last_navigation_update = time.perf_counter()

    def UpdateSteeringSettings(self, settings: dict):
        self.steering_smoothness = self.settings.SteeringSmoothTime
        steering.SMOOTH_TIME = self.steering_smoothness

    def run(self):
        try:
            api_data = api.run()
            data.UpdateData(api_data)
            
            self.CheckForRoutingModeChange()

            if data.calculate_steering:
                # Update route plan and steering
                planning.UpdateRoutePlan()
                steering_value = driving.GetSteering()

                if steering_value is not None:
                    steering.run(value=steering_value/180, sendToGame=data.enabled, drawLine=False)
                else:
                    logging.warning("Invalid steering value received")
            else:
                data.route_points = []

            self.MapWindowInitialization()

            if data.internal_map:
                im.DrawMap()

            self.CheckDestinationCompany()

            if data.external_data_changed:
                external_data = json.dumps(data.external_data)
                self.globals.tags.map = json.loads(external_data)
                self.globals.tags.map_update_time = data.external_data_time
                data.external_data_changed = False

            if not data.elevation_data_sent:
                self.globals.tags.elevation_data = data.map.elevations
                data.elevation_data_sent = True

        except Exception as e:
            logging.error(f"Error in Map plugin run loop: {e}", exc_info=True)
            data.route_points = []  # Clear route points on error

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

        #if len(data.route_points) > 0:
        #    if mh.DistanceBetweenPoints((data.truck_x, data.truck_z), (data.route_points[0].x, data.route_points[0].z)) > 10:
        #        if mh.DistanceBetweenPoints((data.truck_x, data.truck_z), (data.route_points[-1].x, data.route_points[-1].z)) > 10:
        #            data.update_navigation_plan = True

        return [point.tuple() for point in data.route_points]
