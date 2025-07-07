from Plugins.NGHUD.classes import HUDWidget
from Plugins.AR.classes import *

class Widget(HUDWidget):
    name = "Navigation"
    description = "Draw navigation information."
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
        
    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return
        
        distance = self.plugin.data["configUI"]["plannedDistanceKm"]
        game = self.plugin.data["scsValues"]["game"]
        
        if game == "ATS":
            distance = distance * 0.621371  # Convert km to miles for ATS

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
                text=f"{distance:.0f}",
                color=Color(255, 255, 255, 200),
                size=32
            ),
            Text(
                Point(width-25 + offset_x, height-20, anchor=self.plugin.anchor),
                text="mi" if game == "ATS" else "km",
                color=Color(255, 255, 255, 200),
                size=14
            )
        ]