from Modules.Semaphores.classes import TrafficLight
from Plugins.NGHUD.classes import HUDRenderer
from ETS2LA.Utils.translator import _
from Plugins.AR.classes import *

class Renderer(HUDRenderer):
    name = _("Traffic Lights")
    description = _("Draw traffic light information.")
    fps = 1
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
        
    def draw(self):
        if not self.plugin.data:
            return

        self.data = []
        semaphores = self.plugin.modules.Semaphores.run()
        traffic_lights = [semaphore for semaphore in semaphores if isinstance(semaphore, TrafficLight)]
        
        truck_x = self.plugin.data["truckPlacement"]["coordinateX"]
        truck_y = self.plugin.data["truckPlacement"]["coordinateY"]
        truck_z = self.plugin.data["truckPlacement"]["coordinateZ"]
        
        data = []
        for traffic_light in traffic_lights:
            traffic_light_anchor = Coordinate(
                traffic_light.position.x + 512 * traffic_light.cx, 
                traffic_light.position.y + 2.5, 
                traffic_light.position.z + 512 * traffic_light.cy
            )
            
            distance = traffic_light_anchor.get_distance_to(truck_x, truck_y, truck_z)
            if distance > 120:
                continue
            
            data.extend([
                Rectangle(
                    Point(40, 0, anchor=traffic_light_anchor),
                    Point(95, 26, anchor=traffic_light_anchor),
                    color=Color(*traffic_light.color(), a=100), 
                    fill=Color(*traffic_light.color(), a=50), 
                    rounding=6,
                    fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_start=20, dist_fade_end=80),
                    custom_distance=distance
                ),
                Text(
                    Point(45, 5, anchor=traffic_light_anchor),
                    f"{traffic_light.time_left:.0f}s left",
                    size=16,
                    color=Color(*traffic_light.color()), 
                    fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_start=20, dist_fade_end=80),
                    custom_distance=distance
                )
            ])
            
        self.data += data