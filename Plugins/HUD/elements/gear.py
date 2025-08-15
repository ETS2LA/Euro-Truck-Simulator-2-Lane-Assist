from ETS2LA.Utils.Values.numbers import SmoothedValue
from Plugins.HUD.classes import HUDWidget
from ETS2LA.Utils.translator import _
from Plugins.AR.classes import *
import time

class Widget(HUDWidget):
    name = _("RPM & Gear")
    description = _("Draw the current RPM and gear of the truck.")
    fps = 20
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
        
    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return
        
        gear = self.plugin.data['truckInt']['gearDashboard']
        RPM = self.plugin.data['truckFloat']['engineRpm']
        max_RPM = self.plugin.data['configFloat']['engineRpmMax']
        
        if gear < 0:
            gear = f"R{abs(gear)}"  # Reverse gear
            
        if gear == 0:
            gear = "N"

        self.data = [
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width * (RPM / max_RPM) + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            Text(
                Point(7 + offset_x, 5, anchor=self.plugin.anchor),
                text=f"{gear}",
                color=Color(255, 255, 255, 200),
                size=24
            ),
            Text(
                Point(7 + offset_x, 30, anchor=self.plugin.anchor),
                text=f"{RPM:.0f}",
                color=Color(255, 255, 255, 200),
                size=14
            ),
            Text(
                Point(width-30 + offset_x, height-20, anchor=self.plugin.anchor),
                text=f"RPM",
                color=Color(255, 255, 255, 200),
                size=14
            )
        ]