# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 
from Plugins.AR.classes import *

# General imports
import random
import time
import math

class Settings(ETS2LASettingsMenu):
    plugin_name = "Map"
    dynamic = False
    
    def render(self):
        Slider("Refresh Rate", "refresh_rate", 2, 1, 10, 1, description="The refresh rate of the AR elements. Default is 2.")
        
        Input("Offset X", "offset_x", type="number", description="The X offset (side to side) of the AR elements.", default=0)
        Input("Offset Y", "offset_y", type="number", description="The Y offset (top to bottom) of the AR elements.", default=0)
        Input("Offset Z", "offset_z", type="number", description="The Z offset (distance) of the AR elements.", default=0)
        
        Switch("Draw Steering", "draw_steering", False, description="Draw the steering line on the AR HUD.")
        Switch("Show Navigation", "show_navigation", False, description="Show the distance to the next intersection on the AR HUD.")
        
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
    
    def imports(self):
        global ScreenCapture
        import Modules.BetterScreenCapture.main as ScreenCapture
        
        self.get_start_end_time()
        
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
            self.settings.show_navigation = False
            show_navigation = False
            
        refresh_rate = self.settings.refresh_rate
        if refresh_rate is None:
            self.settings.refresh_rate = 2
            refresh_rate = 2
        
        return draw_steering, show_navigation, refresh_rate
    
    def get_start_end_time(self):
        self.load_start_time = time.time()
        self.load_end_time = self.load_start_time + random.uniform(1, 3)
    
    def boot_sequence(self, t: float, anchor: Coordinate, scaling: float = 1):
        t = (time.time() - self.load_start_time) / (self.load_end_time - self.load_start_time)
        if t > 1:
            return False
        
        # Ease out cubic
        t -= 1
        t = t * t * t + 1
        
        self.fps_cap = 10
        
        slider_start_pos = Point(-100 * scaling, 0, anchor=anchor)
        slider_end_pos = Point(100 * scaling, 0, anchor=anchor)
        slider_progress_pos = Point(-100 * scaling + t * 200 * scaling, 0, anchor=anchor)
        slider_text_pos = Point(-100 * scaling + t * 200 * scaling, 10 * scaling, anchor=anchor)
        slider_ets2la_pos = Point(-100 * scaling, -25 * scaling, anchor=anchor)
        self.globals.tags.AR = [
            # Slider base
            Line(
                slider_start_pos,
                slider_end_pos,
                thickness=4 * scaling,
                color=Color(255, 255, 255, 100),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            # Slider progress
            Line(
                slider_start_pos,
                slider_progress_pos,
                thickness=4 * scaling,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            # Text
            Text(
                slider_text_pos,
                f"{t * 100:.0f}%",
                size=16 * scaling,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            # ETS2LA
            Text(
                slider_ets2la_pos,
                "ETS2LA",
                size=20 * scaling,
                color=Color(255, 255, 255),
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
                size=16 * scaling,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            )
        ]
        
        return ar_data
    
    def navigation(self, distance: float, anchor, offset: list[float], scaling: float = 1):
        if distance is None:
            return []
        
        if distance == 1 or distance == 0:
            return []
        
        distance -= distance % 10
        units = "m"
        if distance >= 300:
            distance /= 1000
            units = "km"
        
        distance_pos = Point(-5 * scaling - offset[0], -20 * scaling + offset[1], anchor=anchor)
        unit_pos = Point(-5 * scaling - offset[0], 10 * scaling + offset[1], anchor=anchor)   
        
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
        
        return ar_data

    def run(self):
        X1, Y1, X2, Y2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
        height = Y2 - Y1
        default_height = 1440
        scaling = height / default_height	# 0.75 = 1080p, 1 = 1440p, 1.25 = 1800p, 1.5 = 2160p
        
        data = self.modules.TruckSimAPI.run()
        
        speed_nav_offset_x = 0
        offset_x, offset_y, offset_z = self.get_offsets()
        anchor = Coordinate(0 + offset_x, -2 + offset_y, -10 + offset_z, relative=True, rotation_relative=True)
        draw_steering, show_navigation, refresh_rate = self.get_settings()
        
        self.fps_cap = refresh_rate
        
        speed = data["truckFloat"]["speed"] * 3.6
        speed_limit = data["truckFloat"]["speedLimit"] * 3.6
        engine = data["truckBool"]["engineEnabled"]
        
        distance = self.globals.tags.next_intersection_distance
        distance = self.globals.tags.merge(distance)

        if not engine:
            self.globals.tags.AR = []
            self.get_start_end_time()
            return
        
        if self.boot_sequence(time.time(), anchor, scaling=scaling):
            return
        
        if show_navigation and distance is not None and distance != 1 and distance != 0:
            speed_nav_offset_x -= 50
        
        ar_data = []
        ar_data += self.speed(speed, speed_limit, anchor, [speed_nav_offset_x, 0, 0], scaling=scaling)
        if show_navigation:
            ar_data += self.navigation(distance, anchor, [speed_nav_offset_x, 0, 0], scaling=scaling)
        
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