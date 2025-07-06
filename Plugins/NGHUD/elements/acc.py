from Modules.Traffic.classes import Vehicle
from Plugins.NGHUD.classes import HUDRenderer
from Plugins.AR.classes import *
import time

class Renderer(HUDRenderer):
    name = "ACC Information"
    description = "Draw ACC information like vehicle distance and speed."
    fps = 30
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
        
    def draw(self):
        if not self.plugin.data:
            return

        targets = self.plugin.globals.tags.vehicle_highlights
        targets = self.plugin.globals.tags.merge(targets)
        
        if targets is None:
            targets = []
        
        vehicles = self.plugin.modules.Traffic.run()
        
        if vehicles is None:
            vehicles = []
        
        highlighted_vehicle = None
        if len(targets) > 0:
            for vehicle in vehicles:
                if vehicle.id in targets:
                    highlighted_vehicle = vehicle
                    break
            
        if not highlighted_vehicle:
            self.data = []
            time.sleep(1/30)
            return
        
        if not isinstance(highlighted_vehicle, Vehicle):
            self.data = []
            time.sleep(1/30)
            return
        
        truck_x = self.plugin.data["truckPlacement"]["coordinateX"]
        truck_y = self.plugin.data["truckPlacement"]["coordinateY"]
        truck_z = self.plugin.data["truckPlacement"]["coordinateZ"]
        
        # Line under the vehicle
        front_left, front_right, back_right, back_left = highlighted_vehicle.get_corners() 
        distance = Coordinate(*front_left).get_distance_to(truck_x, truck_y, truck_z)
        center_back = [
            (back_left[0] + back_right[0]) / 2,
            (back_left[1] + back_right[1]) / 2,
            (back_left[2] + back_right[2]) / 2
        ]
        
        if distance > 120:
            return
        
        relative_front_left = self.plugin.get_relative_to_head(Coordinate(*front_left))
        relative_front_right = self.plugin.get_relative_to_head(Coordinate(*front_right))
        relative_back_right = self.plugin.get_relative_to_head(Coordinate(*back_right))
        relative_back_left = self.plugin.get_relative_to_head(Coordinate(*back_left))
        relative_center_back = self.plugin.get_relative_to_head(Coordinate(*center_back))

        # 3D box
        self.data = [
            Polygon(
                [relative_front_left, relative_front_right, relative_back_right, relative_back_left],
                color=Color(255, 255, 255, 60),
                fill=Color(255, 255, 255, 40),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_start=80, dist_fade_end=100)
            )
        ]
        
        # Rectangle and text under the vehicle
        self.data += [
            Rectangle(
                Point(-50, 20, anchor=relative_center_back),
                Point(50, 40, anchor=relative_center_back),
                rounding=6,
                custom_distance=distance,
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_start=80, dist_fade_end=100)
            ),
            Text(
                Point(-45, 22, anchor=relative_center_back),
                text=f"{highlighted_vehicle.speed:.0f} km/h",
                size=16,
                custom_distance=distance,
                color=Color(255, 255, 255, 150),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_start=80, dist_fade_end=100)
            ),
            Text(
                Point(15, 22, anchor=relative_center_back),
                text=f"{distance:.0f} m",
                size=16,
                custom_distance=distance,
                color=Color(255, 255, 255, 150),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_start=80, dist_fade_end=100)
            )
        ]