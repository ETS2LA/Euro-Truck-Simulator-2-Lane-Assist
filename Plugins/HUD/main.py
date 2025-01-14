# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 
from Plugins.Map.classes import *
from Plugins.AR.classes import *

# General imports
import logging
import random
import time
import math

class Settings(ETS2LASettingsMenu):
    plugin_name = "HUD"
    dynamic = False
    
    def render(self):
        Slider("Refresh Rate", "refresh_rate", 2, 1, 10, 1, description="The refresh rate of the AR elements. Default is 2.")
        
        Input("Offset X", "offset_x", type="number", description="The X offset (side to side) of the AR elements.", default=0)
        Input("Offset Y", "offset_y", type="number", description="The Y offset (top to bottom) of the AR elements.", default=0)
        Input("Offset Z", "offset_z", type="number", description="The Z offset (distance) of the AR elements.", default=0)
        
        Switch("Draw Steering", "draw_steering", False, description="Draw the steering line on the AR HUD.")
        Switch("Show Navigation", "show_navigation", True, description="Show the distance to the next intersection on the AR HUD.")
        
        return RenderUI()

class Plugin(ETS2LAPlugin):
    fps_cap = 2
    
    description = PluginDescription(
        name="HUD",
        version="1.0",
        description="Creates a heads up display on the windshield. Needs the AR plugin to work.",
        modules=["TruckSimAPI"],
        tags=["AR", "Base"],
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    settings_menu = Settings()
    
    map_data = None
    update_time = 0
    
    intersection = None
    intersection_uid = None
    
    def imports(self):
        global ScreenCapture
        import Modules.BetterScreenCapture.main as ScreenCapture
        
        self.get_start_end_time()
        
    def get_map_data(self):
        remote_update_time = self.globals.tags.map_update_time
        remote_update_time = self.globals.tags.merge(remote_update_time)
        if remote_update_time != self.update_time:
            logging.warning("Updating map data for HUD")
            self.update_time = remote_update_time
            self.map_data = self.globals.tags.map
            self.map_data = self.globals.tags.merge(self.map_data)
        
    def get_intersection(self):
        next_intersection = self.globals.tags.next_intersection_uid
        next_intersection = self.globals.tags.merge(next_intersection)
        if next_intersection != self.intersection_uid:
            if self.map_data is not None:
                # json path: prefabs (list) -> uid
                for prefab in self.map_data["prefabs"]:
                    if str(prefab["uid"]) == str(next_intersection):
                        self.intersection_uid = next_intersection
                        self.intersection = prefab
                        logging.debug(f"Intersection found: {prefab}")
                        return
                    
            self.intersection = None
                
    def create_intersection_map(self, anchor, offset: list[float] = [0, 0], data = None):
        # Top down map along the X and Z axis
        if self.intersection is None:
            return None
        
        target_lane = self.globals.tags.next_intersection_lane
        target_lane = self.globals.tags.merge(target_lane)
        
        bounding_box = self.intersection["bounding_box"]
        bounding_box = [bounding_box["min_x"], bounding_box["min_y"], bounding_box["max_x"], bounding_box["max_y"]] # y = z
        
        rotation = data["truckPlacement"]["rotationX"] * 360
        x = data["truckPlacement"]["coordinateX"]
        z = data["truckPlacement"]["coordinateZ"]
        
        def convert_to_center_aligned_coordinate(x, y):
            center = (bounding_box[2] + bounding_box[0]) / 2, (bounding_box[3] + bounding_box[1]) / 2
            return x - center[0], y - center[1]
        
        def rotate_around_center(x, y, angle):
            angle = math.radians(angle)
            x, y = x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle)
            return x, y
        
        def is_inside_bounds(x, y, expand=0):
            return x >= bounding_box[0] - expand and x <= bounding_box[2] + expand and y >= bounding_box[1] - expand and y <= bounding_box[3] + expand
        
        lanes = []
        for i, lane in enumerate(self.intersection["nav_routes"]):
            if i == target_lane:
                continue
            cur_lane = []
            for curve in lane["curves"]:
                points = curve["points"]
                points = [convert_to_center_aligned_coordinate(point["x"], point["z"]) for point in points]
                points = [rotate_around_center(point[0], point[1], rotation) for point in points]
                
                cur_lane.append((
                    Polygon(
                        [Point(point[0] + offset[0], point[1] + offset[1], anchor=anchor) for point in points],
                        thickness=2,
                        color=Color(140, 140, 140),
                        fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100)
                    )
                ))
            
            lanes.append(cur_lane)
            
        # Add target lane
        if target_lane is not None:
            target_lane = self.intersection["nav_routes"][target_lane]
            cur_lane = []
            for curve in target_lane["curves"]:
                points = curve["points"]
                points = [convert_to_center_aligned_coordinate(point["x"], point["z"]) for point in points]
                points = [rotate_around_center(point[0], point[1], rotation) for point in points]
                
                cur_lane.append((
                    Polygon(
                        [Point(point[0] + offset[0], point[1] + offset[1], anchor=anchor) for point in points],
                        thickness=2,
                        color=Color(255, 255, 255),
                        fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100)
                    )
                ))
            
            lanes.append(cur_lane)
            
        # Add truck
        if is_inside_bounds(x, z, expand=15):
            x, z = convert_to_center_aligned_coordinate(x, z)
            x, z = rotate_around_center(x, z, rotation)
            truck = Point(x + offset[0], z + offset[1])
            lanes.append([
                Line(
                    Point(truck.x, truck.y - 3, anchor=anchor),
                    Point(truck.x, truck.y + 3, anchor=anchor),
                    thickness=3,
                    color=Color(255, 100, 100)
                )  
            ])
            
        return lanes

                
    def get_offsets(self):
        offset_x = self.settings.offset_x
        if offset_x is None:
            self.settings.offset_x = 0
            offset_x = 0
        
        offset_y = self.settings.offset_y
        if offset_y is None:
            self.settings.offset_y = 0
            offset_y = 0
        
        offset_z = self.settings.offset_z
        if offset_z is None:
            self.settings.offset_z = 0
            offset_z = 0
            
        return offset_x, offset_y, offset_z
    
    def get_settings(self):
        draw_steering = self.settings.draw_steering
        if draw_steering is None:
            self.settings.draw_steering = False
            draw_steering = False
            
        show_navigation = self.settings.show_navigation
        if show_navigation is None:
            self.settings.show_navigation = True
            show_navigation = True
            
        refresh_rate = self.settings.refresh_rate
        if refresh_rate is None:
            self.settings.refresh_rate = 2
            refresh_rate = 2
        
        return draw_steering, show_navigation, refresh_rate
    
    def get_start_end_time(self):
        self.load_start_time = time.time()
        self.times = random.uniform(4, 6)
        self.load_end_time = self.load_start_time + self.times
    
    def boot_sequence(self, t: float, anchor: Coordinate, scaling: float = 1):
        t = (time.time() - self.load_start_time) / (self.load_end_time - self.load_start_time)
        if t > 1:
            return False
        
        opacity = 1
        # Smooth out the opacity above 95%
        if t > 0.95:
            opacity = 1 - (t - 0.95) * 1 / 0.05
            opacity = max(0, min(1, opacity))
        # Smooth out below 10%
        elif t < 0.1:
            opacity = t * 1 / 0.1
            opacity = max(0, min(1, opacity))
            
        t = t * (self.times/2) % 1
        
        self.fps_cap = 30
        
        slider_ets2la_pos = Point(-30 * scaling, -25 * scaling, anchor=anchor)

        def sigmoid(t):
            return 1 / (1 + math.exp(-t * 5))

        slider_start_pos = Point(-100 * scaling + ((sigmoid(t)) * 400 - 200) * scaling, 0, anchor=anchor)
        slider_progress_pos = Point(-100 * scaling + t * 200 * scaling, 0, anchor=anchor)
        
        self.globals.tags.AR = [
            # Slider progress
            Line(
                slider_start_pos,
                slider_progress_pos,
                thickness=4 * scaling,
                color=Color(255, 255, 255, 255 * opacity),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            # ETS2LA
            Text(
                slider_ets2la_pos,
                "ETS2LA",
                size=20 * scaling,
                color=Color(255, 255, 255, 255 * opacity),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            )
        ]
        
        return True
    
    def speed(self, speed: float, speed_limit: float, anchor, offset: list[float], scaling: float = 1):
        speed_pos = Point(-5 * scaling + offset[0], -20 * scaling + offset[1], anchor=anchor)
        unit_pos = Point(-5 * scaling + offset[0], 10 * scaling + offset[1], anchor=anchor) 
        
        speed_limit_base_y = 4 * scaling
        speed_limit_base_x = -35 * scaling
        speed_limit_pos = Point(speed_limit_base_x + offset[0], speed_limit_base_y + offset[1], anchor=anchor)
        speed_limit_text_pos = Point(speed_limit_base_x + offset[0] - 8 * scaling, speed_limit_base_y + offset[1] - 9 * scaling, anchor=anchor)
        
        ar_data = [
            # Speed
            Text(
                unit_pos,
                "km/h",
                size=16 * scaling,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            Text(
                speed_pos,
                f"{abs(speed):.0f}",
                size=30 * scaling,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            
            # Speedlimit
            Circle(
                speed_limit_pos,
                16 * scaling,
                color=Color(255, 255, 255),
                thickness=2,
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            Text(
                speed_limit_text_pos,
                f"{abs(speed_limit):.0f}",
                size=18 * scaling,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            )
        ]
        
        return ar_data
    
    def navigation(self, distance: float, anchor, offset: list[float], scaling: float = 1, data = None):
        
        if distance is None:
            return []
        
        if distance == 1 or distance == 0:
            return []
        
        self.get_intersection()
        
        distance -= distance % 10
        units = "m"
        if distance >= 300:
            distance /= 1000
            units = "km"
        
        distance_pos = Point(0 * scaling - offset[0], -20 * scaling + offset[1], anchor=anchor)
        unit_pos = Point(0 * scaling - offset[0], 10 * scaling + offset[1], anchor=anchor)   
        
        ar_data = [
            # Distance
            Text(
                unit_pos,
                units,
                size=16 * scaling,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            Text(
                distance_pos,
                f"{abs(distance):.0f}" if units == "m" else f"{abs(distance):.1f}",
                size=30 * scaling,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            )
        ]
        
        intersection_map = self.create_intersection_map(anchor, [150, 5], data)
        if intersection_map is not None:
            for lane in intersection_map:
                for line in lane:
                    ar_data.append(line)
        
        return ar_data

    def run(self):
        X1, Y1, X2, Y2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
        height = Y2 - Y1
        default_height = 1440
        scaling = height / default_height	# 0.75 = 1080p, 1 = 1440p, 1.25 = 1800p, 1.5 = 2160p
        
        data = self.modules.TruckSimAPI.run()
        self.get_map_data()
        
        speed_nav_offset_x = 0
        offset_x, offset_y, offset_z = self.get_offsets()
        anchor = Coordinate(0 + offset_x, -2 + offset_y, -10 + offset_z, relative=True, rotation_relative=True)
        draw_steering, show_navigation, refresh_rate = self.get_settings()
        
        
        speed = data["truckFloat"]["speed"] * 3.6
        speed_limit = data["truckFloat"]["speedLimit"] * 3.6
        engine = data["truckBool"]["engineEnabled"]
        
        distance = self.globals.tags.next_intersection_distance
        distance = self.globals.tags.merge(distance)

        if not engine:
            self.globals.tags.AR = []
            self.get_start_end_time()
            self.fps_cap = 10
            return
        
        if self.boot_sequence(time.time(), anchor, scaling=scaling):
            return
        
        self.fps_cap = refresh_rate
        
        if show_navigation and distance is not None and distance != 1 and distance != 0:
            speed_nav_offset_x -= 50 * scaling
        
        ar_data = []
        ar_data += self.speed(speed, speed_limit, anchor, [speed_nav_offset_x - 15, 0, 0], scaling=scaling)
        if show_navigation:
            ar_data += self.navigation(distance, anchor, [speed_nav_offset_x + 15, 0, 0], scaling=scaling, data=data)
        
        if draw_steering:
            try:
                data = self.plugins.Map
                for i, point in enumerate(data):
                    if i == 0:
                        continue
                    line = Line(
                        Coordinate(*point),
                        Coordinate(*data[i - 1]),
                        thickness=5 * scaling,
                        color=Color(255, 255, 255, 60),
                        fade=Fade(prox_fade_end=10, prox_fade_start=20, dist_fade_start=50, dist_fade_end=150)
                    )
                    ar_data.append(line)
            except:
                pass
        
        self.globals.tags.AR = ar_data