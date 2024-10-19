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
import plugins.Map.route.planning as planning
import plugins.Map.route.driving as driving
import ETS2LA.backend.settings as settings
import plugins.Map.utils.speed as speed
import plugins.Map.classes as c

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = True
    plugin_name = "Map"
    
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
                Space(1)
                Title("map.settings.10.title")
                Switch("map.settings.2.name", "ComputeSteeringData", True, description="map.settings.2.description")
                Slider("map.settings.11.name", "SteeringSmoothTime", 0.2, 0, 2, 0.1, description="map.settings.11.description")
                Space(12)
                Title("map.settings.4.title")
                Switch("map.settings.6.name", "InternalVisualisation", True, description="map.settings.6.description")
            with Tab("Debug Data"):
                with EnabledLock():
                    with Group("horizontal", gap=4):
                        with Group("vertical", gap=1):
                            Label("Map data:")
                            Space(0)
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
                            
                        with Group("vertical", gap=1):
                            Label("Backend data:")
                            Space(0)
                            try: Description(f"State: {self.plugin.state.text}, {self.plugin.state.progress:.0f}")
                            except: Description("State: N/A")
                            try: Description(f"FPS: {1/self.plugin.performance[-1][1]:.0f}")
                            except: Description("FPS: Still loading...")

                    
        return RenderUI()

class Plugin(ETS2LAPlugin):
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    description = PluginDescription(
        name="plugins.map",
        description="plugins.map.description",
        version="2.0.0",
        modules=["TruckSimAPI", "Steering", "SDKController"]
    )
    
    fps_cap = 20
    settings_menu = SettingsMenu()
    
    steering_smoothness: float = 0.2
    MAP_INITIALIZED = False
    
    def imports(self):
        global json, data, time, math, sys
        # General imports
        import plugins.Map.data as data
        import json
        import time
        import math
        import sys
        
    def ToggleSteering(self, state:bool, *args, **kwargs):
        data.enabled = state
        
    def init(self):
        self.steering_smoothness = self.settings.SteeringSmoothTime
        if self.steering_smoothness is None:
            self.steering_smoothness = 0.2
            self.settings.SteeringSmoothTime = 0.2
            
        data.controller = self.modules.SDKController.SCSController()
        
        global api, steering
        api = self.modules.TruckSimAPI
        steering = self.modules.Steering
        steering.OFFSET = 0
        steering.SMOOTH_TIME = self.steering_smoothness
        steering.IGNORE_SMOOTH = False
        steering.SENSITIVITY = 1
        
        settings.Listen("Map", self.UpdateSteeringSettings)
        
        self.state.text = "Loading data, please wait..."
        self.state.progress = 0
        time.sleep(0.1)
        data.map = ReadData(state=self.state)
        c.data = data # set the classes data variable
        self.state.reset()
    
    
    def UpdateSteeringSettings(self, settings: dict):
        self.steering_smoothness = self.settings.SteeringSmoothTime
        steering.SMOOTH_TIME = self.steering_smoothness

    def run(self):
        api_data = api.run()
        data.UpdateData(api_data)
        
        max_speed = api_data["truckFloat"]["speedLimit"]
        if data.calculate_steering:
            planning.UpdateRoutePlan()
            
            steering_value = driving.GetSteering()
            steering.run(value=steering_value/180, sendToGame=data.enabled, drawLine=False)
            
            route_max_speed = speed.GetMaximumSpeed()
            if route_max_speed < max_speed:
                max_speed = route_max_speed

        else:
            data.route_points = []
        
        if not data.map_initialized and data.internal_map:
            im.InitializeMapWindow()
            self.MAP_INITIALIZED = True
            
        if data.map_initialized and not data.internal_map:
            im.RemoveWindow()
            self.MAP_INITIALIZED = False
        
        if data.internal_map:
            im.DrawMap()
        
        if data.external_data_changed:
            external_data = json.dumps(data.external_data)
            print(f"External data changed, file size: {sys.getsizeof(external_data)/1000:.0f} KB")
            self.globals.tags.map = json.loads(external_data)
            self.globals.tags.map_update_time = data.external_data_time
            data.external_data_changed = False

        if not data.elevation_data_sent:
            self.globals.tags.elevation_data = data.map.elevations
            data.elevation_data_sent = True

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
        
        return [point.tuple() for point in data.route_points]