from Plugins.NGHUD.classes import HUDWidget
from Plugins.AR.classes import *
import datetime
import time

class Widget(HUDWidget):
    name = "Navigation"
    description = "Draw navigation information."
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
    
    show_time = True
    last_switch = 0
        
    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return
        
        distance = self.plugin.data["truckFloat"]["routeDistance"] / 1000
        time_left = self.plugin.data["truckFloat"]["routeTime"]
        game = self.plugin.data["scsValues"]["game"]
        
        if time.time() - self.last_switch > 10:
            self.show_time = not self.show_time
            self.last_switch = time.time()
        
        if game == "ATS":
            distance = distance * 0.621371  # Convert km to miles for ATS

        if self.show_time:
            real_seconds = time_left / 20
            arrival_time = datetime.datetime.now() + datetime.timedelta(seconds=real_seconds)
            
            self.data = [
                Rectangle(
                    Point(offset_x, 0, anchor=self.plugin.anchor),
                    Point(width + offset_x, height, anchor=self.plugin.anchor),
                    color=Color(255, 255, 255, 20),
                    fill=Color(255, 255, 255, 10),
                    rounding=6,
                ),
                Text(
                    Point(7 + offset_x, 5, anchor=self.plugin.anchor),
                    text=f"{arrival_time.strftime('%H:%M')}",
                    color=Color(255, 255, 255, 200),
                    size=24
                ),
                Text(
                    Point(7 + offset_x, 30, anchor=self.plugin.anchor),
                    text=f"{real_seconds/60:.0f} min",
                    color=Color(255, 255, 255, 200),
                    size=14
                ),
                Text(
                    Point(width-39 + offset_x, height-20, anchor=self.plugin.anchor),
                    text="arrival",
                    color=Color(255, 255, 255, 200),
                    size=14
                )
            ]

        else:
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