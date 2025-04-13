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
        modules=["SDKController", "TruckSimAPI", "Steering", "Route"],
        tags=["Base", "Steering"],
        ui_filename="ui.py",
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

    def update_road_data(self):
        data.map.clear_road_data()
        im.road_image = None
        data.data_needs_update = True
        
    def trigger_data_update(self):
        self.settings.downloaded_data = ""

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
                    if steering_value > 0.9 or steering_value < -0.9:
                        steering_value = 0

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
            if frametime > 0.13: # ~7.7fps
                if self.state.text == "" or "low FPS" in self.state.text: # Don't overwrite other states
                    self.state.text = f"Warning: Steering might be compromised due to low FPS. ({1/frametime:.0f}fps)"
            else:
                if "low FPS" in self.state.text:
                    self.state.text = ""
        except:
            pass

        if variables.DEVELOPMENT_MODE:
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
        
        return [point.tuple() for point in data.route_points]
