from Plugins.NGHUD.classes import HUDWidget
from Plugins.AR.classes import *

class Widget(HUDWidget):
    name = "Speed"
    description = "Draw speed."
    fps = 2
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
        
    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return
        
        speed = abs(self.plugin.data["truckFloat"]["speed"])
        game = self.plugin.data["scsValues"]["game"]
        if game == "ATS":
            speed = speed * 3.6 * 0.621371
            unit = "mph"
        else:
            speed = speed * 3.6
            unit = "km/h"
            
        self.data = [
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            Text(
                Point(10 + offset_x, 8, anchor=self.plugin.anchor),
                text=f"{speed:.0f}",
                color=Color(255, 255, 255, 200),
                size=32
            ),
            Text(
                Point(width-35 + offset_x, height-20, anchor=self.plugin.anchor),
                text=f"{unit}",
                color=Color(255, 255, 255, 200),
                size=14
            )
        ]