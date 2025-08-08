from Plugins.HUD.classes import HUDWidget
from ETS2LA.Utils.translator import _
from Plugins.AR.classes import *
import time

class Widget(HUDWidget):
    name = _("Speed")
    description = _("A normal speed display, will also show speed limit changes.")
    fps = 2
    
    last_speedlimit = 0
    last_limit_time = 0
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
        
    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return
        
        raw_speed = abs(self.plugin.data["truckFloat"]["speed"])
        game = self.plugin.data["scsValues"]["game"]
        if game == "ATS":
            speed = raw_speed * 3.6 * 0.621371
            unit = "mph"
        else:
            speed = raw_speed * 3.6
            unit = "km/h"

        if abs(self.plugin.data["truckFloat"]["speedLimit"]) != self.last_speedlimit:
            self.last_speedlimit = abs(self.plugin.data["truckFloat"]["speedLimit"])
            self.last_limit_time = time.time()
        
        if raw_speed > self.last_speedlimit + 10 / 3.6 and self.last_speedlimit * 3.6 >= 29:
            limit = self.last_speedlimit
            if game == "ATS":
                limit = limit * 3.6 * 0.621371
            else:
                limit = limit * 3.6
                
            self.data = [
                Rectangle(
                    Point(offset_x, 0, anchor=self.plugin.anchor),
                    Point(width + offset_x, height, anchor=self.plugin.anchor),
                    color=Color(255, 150, 150, 40),
                    fill=Color(255, 150, 150, 20),
                    rounding=6,
                ),
                Text(
                    Point(7 + offset_x, 5, anchor=self.plugin.anchor),
                    text=f"{speed:.0f}",
                    color=Color(255, 255, 255, 200),
                    size=24
                ),
                Text(
                    Point(7 + offset_x, 30, anchor=self.plugin.anchor),
                    text=f"{limit:.0f} Limit",
                    color=Color(255, 255, 255, 200),
                    size=14
                ),
                Text(
                    Point(width-35 + offset_x, height-20, anchor=self.plugin.anchor),
                    text=f"{unit}",
                    color=Color(255, 255, 255, 200),
                    size=14
                )
            ]
            return
        
        if time.time() - self.last_limit_time < 5:
            limit = self.last_speedlimit
            if game == "ATS":
                limit = limit * 3.6 * 0.621371
            else:
                limit = limit * 3.6
                
            self.data = [
                Rectangle(
                    Point(offset_x, 0, anchor=self.plugin.anchor),
                    Point(width + offset_x, height, anchor=self.plugin.anchor),
                    color=Color(255, 255, 150, 40),
                    fill=Color(255, 255, 150, 20),
                    rounding=6,
                ),
                Text(
                    Point(7 + offset_x, 5, anchor=self.plugin.anchor),
                    text=f"{speed:.0f}",
                    color=Color(255, 255, 255, 200),
                    size=24
                ),
                Text(
                    Point(7 + offset_x, 30, anchor=self.plugin.anchor),
                    text=f"{limit:.0f} Limit",
                    color=Color(255, 255, 255, 200),
                    size=14
                ),
                Text(
                    Point(width-35 + offset_x, height-20, anchor=self.plugin.anchor),
                    text=f"{unit}",
                    color=Color(255, 255, 255, 200),
                    size=14
                )
            ]
            return

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