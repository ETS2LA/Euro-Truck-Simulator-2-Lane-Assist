from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import *

# Imports to fix circular imports
import plugins.Map.utils.prefab_helpers as ph
import plugins.Map.utils.road_helpers as rh
import plugins.Map.utils.math_helpers as mh
import plugins.Map.utils.internal_map as im

# ETS2LA imports
from plugins.Map.utils.data_reader import ReadData
from ETS2LA.utils.translator import Translate
import ETS2LA.backend.settings as settings
import plugins.Map.utils.speed as speed
import plugins.Map.classes as c

import threading
import importlib
navigation = importlib.import_module("plugins.Map.navigation.navigation")
planning = importlib.import_module("plugins.Map.route.planning")
driving = importlib.import_module("plugins.Map.route.driving")
last_plan_hash = hash(open(planning.__file__).read())
last_drive_hash = hash(open(driving.__file__).read())
last_nav_hash = hash(open(navigation.__file__).read())

class SettingsMenu(ETS2LASettingsMenu):
    plugin_name = "Map"
    dynamic = True

    def get_value_from_data(self, key: str):
        if "data" not in globals():
            return "N/A"
        if key in data.__dict__:
            return data.__dict__[key]
        return "Not Found"

    def render(self):
        RefreshRate(0.25)
        Title("map.settings.1.title")
        Description("map.settings.1.description")
        Separator()
        with TabView():
            with Tab("Settings"):
                Title("map.settings.10.title")
                Switch("map.settings.2.name", "ComputeSteeringData", True, description="map.settings.2.description")
                Slider("map.settings.11.name", "SteeringSmoothTime", 0.2, 0, 2, 0.1, description="map.settings.11.description")
                Space(12)
                Title("map.settings.4.title")
                Switch("map.settings.6.name", "InternalVisualisation", False, description="map.settings.6.description")
                Space(12)
                Title("Navigation Settings")
                Switch("Navigate on ETS2LA", "UseNavigation", True, description="Enable the automatic navigation features of ETS2LA.")
                routing_mode = settings.Get("Map", "RoutingMode")
                if not routing_mode or routing_mode not in ["shortest", "smallRoads"]:
                    routing_mode = "shortest"
                    settings.Set("Map", "RoutingMode", routing_mode)
                Selector("Routing Mode", "RoutingMode", routing_mode, ["shortest", "smallRoads"],
                        description="Choose between fastest routes (shortest) or scenic routes avoiding highways (smallRoads)")
            with Tab("Debug Data"):
                with EnabledLock():
                    with Group("horizontal", gap=4):
                        with Group("vertical", gap=1):
                            Label("Map data:")
                            Space(0)
                            Description(f"Current coordinates: ({self.get_value_from_data('truck_x')}, {self.get_value_from_data('truck_z')})")
                            Description(f"Current sector: ({self.get_value_from_data('current_sector_x')}, {self.get_value_from_data('current_sector_y')})")
                            Description(f"Roads in sector: {len(self.get_value_from_data('current_sector_roads'))}")
                            Description(f"Prefabs in sector: {len(self.get_value_from_data('current_sector_prefabs'))}")
                            Description(f"Models in sector: {len(self.get_value_from_data('current_sector_models'))}")
                            try: Description(f"Last data update: {time.strftime('%H:%M:%S', time.localtime(self.get_value_from_data('external_data_time')))}")
                            except: Description(f"Last data update: N/A")

                        with Group("vertical", gap=1):
                            Label("Route data:")
                            Space(0)
                            Description(f"Is steering: {self.get_value_from_data('calculate_steering')}")
                            Description(f"Route points: {len(self.get_value_from_data('route_points'))}")
                            Description(f"Route plan elements: {len(self.get_value_from_data('route_plan'))}")
                            Description(f"Routing mode: {settings.Get('Map', 'RoutingMode')}")
                            Description(f"Navigation points: {len(self.get_value_from_data('navigation_points'))}")
                            Description(f"Has destination: {self.get_value_from_data('dest_company') is not None}")

                        with Group("vertical", gap=1):
                            Label("Backend data:")
                            Space(0)
                            try: Description(f"State: {self.plugin.state.text}, {self.plugin.state.progress:.0f}")
                            except: Description("State: N/A")
                            try: Description(f"FPS: {1/self.plugin.performance[-1][1]:.0f}")
                            except: Description("FPS: Still loading...")


        return RenderUI()

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
    
    fps_cap = 20
    settings_menu = SettingsMenu()
    
    steering_smoothness: float = 0.2
    MAP_INITIALIZED = False
    
    def imports(self):
        global json, data, time, math, sys, logging
        # General imports
        import plugins.Map.data as data
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
        global last_nav_hash, last_drive_hash, last_plan_hash
        logging.info("Starting navigation module file monitor")
        while True:
            try:
                new_nav_hash = hash(open(navigation.__file__).read())
                new_drive_hash = hash(open(driving.__file__).read())
                new_plan_hash = hash(open(planning.__file__).read())
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
                    logging.info("Successfully reloaded planning module")
            except Exception as e:
                logging.error(f"Error monitoring navigation module: {e}")
            time.sleep(1)
        
    @events.on("ToggleSteering")
    def ToggleSteering(self, state:bool, *args, **kwargs):
        data.enabled = state
        self.globals.tags.status = {"Map": state}

    def init(self):
        """Initialize the plugin"""
        try:
            self.steering_smoothness = settings.Get("Map", "SteeringSmoothTime", 0.3)

            data.controller = self.modules.SDKController.SCSController()
            data.plugin = self

            global api, steering
            api = self.modules.TruckSimAPI
            steering = self.modules.Steering
            steering.OFFSET = 0
            steering.SMOOTH_TIME = self.steering_smoothness
            steering.IGNORE_SMOOTH = False
            steering.SENSITIVITY = 1

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


    def UpdateSteeringSettings(self, settings: dict):
        self.steering_smoothness = self.settings.SteeringSmoothTime
        steering.SMOOTH_TIME = self.steering_smoothness

    def run(self):
        try:
            api_data = api.run()
            data.UpdateData(api_data)

            # Check if routing mode has changed
            current_routing_mode = settings.Get("Map", "RoutingMode")
            if current_routing_mode != self._last_routing_mode and data.use_navigation:
                logging.info(f"Routing mode changed from {self._last_routing_mode} to {current_routing_mode}")
                self._last_routing_mode = current_routing_mode
                if data.dest_company:
                    logging.info("Recalculating path with new routing mode...")
                    navigation.get_path_to_destination()

            max_speed = api_data["truckFloat"]["speedLimit"]
            if data.calculate_steering:
                # Update route plan and steering
                planning.UpdateRoutePlan()
                steering_value = driving.GetSteering()

                if steering_value is not None:
                    steering.run(value=steering_value/180, sendToGame=data.enabled, drawLine=False)
                else:
                    logging.warning("Invalid steering value received")

                # Update speed limits
                route_max_speed = speed.GetMaximumSpeed()
                if route_max_speed and route_max_speed < max_speed:
                    max_speed = route_max_speed
            else:
                data.route_points = []

            # Initialize map visualization if needed
            if not data.map_initialized and data.internal_map:
                im.InitializeMapWindow()
                self.MAP_INITIALIZED = True

            if data.map_initialized and not data.internal_map:
                im.RemoveWindow()
                self.MAP_INITIALIZED = False

            if data.internal_map:
                im.DrawMap()

            # Call navigation when destination company changes
            if (data.dest_company != self.last_dest_company or data.update_navigation_plan) and data.use_navigation and time.time() - data.last_navigation_update > 5:
                logging.info(f"Destination company changed to {data.dest_company.token if data.dest_company else 'None'}, recalculating path...")
                self.last_dest_company = data.dest_company
                data.update_navigation_plan = False
                navigation.get_path_to_destination()
                data.last_navigation_update = time.time()

            if data.external_data_changed:
                external_data = json.dumps(data.external_data)
                print(f"External data changed, file size: {sys.getsizeof(external_data)/1000:.0f} KB")
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
                self.globals.tags.next_intersection_distance = data.route_plan[1].distance_left()
            else:
                self.globals.tags.next_intersection_distance = 1
        else:
            self.globals.tags.next_intersection_distance = 1

        self.globals.tags.target_speed = max_speed

        #if len(data.route_points) > 0:
        #    if mh.DistanceBetweenPoints((data.truck_x, data.truck_z), (data.route_points[0].x, data.route_points[0].z)) > 10:
        #        if mh.DistanceBetweenPoints((data.truck_x, data.truck_z), (data.route_points[-1].x, data.route_points[-1].z)) > 10:
        #            data.update_navigation_plan = True

        return [point.tuple() for point in data.route_points]
