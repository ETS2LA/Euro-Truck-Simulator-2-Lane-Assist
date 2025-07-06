from Modules.Semaphores.classes import TrafficLight
from Plugins.NGHUD.classes import HUDRenderer
from Plugins.AR.classes import *
from ETS2LA.UI import *

class Renderer(HUDRenderer):
    name = "Steering Line"
    description = "Draw steering line from Map."
    fps = 2
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
        
    def draw(self):
        if not self.plugin.data:
            return

        try:
            points = self.plugin.globals.tags.steering_points
            points = self.plugin.globals.tags.merge(points)
            
            status = self.plugin.globals.tags.status
            if status:
                map_status = self.plugin.globals.tags.merge(status)["Map"]
            else:
                map_status = None

            steering_data = []
            for i, point in enumerate(points):
                if i == 0:
                    continue
                line = Line(
                    Coordinate(*point),
                    Coordinate(*points[i - 1]),
                    thickness=5,
                    color=Color(100, 100, 100, 120) if not map_status else Color(255, 255, 255, 80),
                    fade=Fade(prox_fade_end=10, prox_fade_start=20, dist_fade_start=50, dist_fade_end=150)
                )
                steering_data.append(line)
            self.data = steering_data
        except:
            self.data = []
            pass