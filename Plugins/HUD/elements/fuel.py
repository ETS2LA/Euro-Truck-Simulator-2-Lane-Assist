from Plugins.AR.classes import Point, Rectangle, Color, Text
from Plugins.HUD.classes import HUDWidget
from ETS2LA.Utils.translator import _


class Widget(HUDWidget):
    name = _("Fuel Status")
    description = _("Draw the current fuel status of the truck.")
    fps = 2

    def __init__(self, plugin):
        super().__init__(plugin)

    def settings(self):
        return super().settings()

    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return

        fuel_capacity = self.plugin.data["configFloat"]["fuelCapacity"]

        fuel = self.plugin.data["truckFloat"]["fuel"] / fuel_capacity
        fuel_range = self.plugin.data["truckFloat"]["fuelRange"]  # km
        unit = "km"

        game = self.plugin.data["scsValues"]["game"]
        if game == "ATS":
            fuel_range *= 0.621371  # Convert km to miles for ATS
            unit = "mi"

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
                Point(width * fuel + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            Text(
                Point(7 + offset_x, 5, anchor=self.plugin.anchor),
                text=f"{fuel * 100:.0f}%",
                color=Color(255, 255, 255, 200),
                size=24,
            ),
            Text(
                Point(7 + offset_x, 30, anchor=self.plugin.anchor),
                text=f"{range:.0f} {unit}",
                color=Color(255, 255, 255, 200),
                size=14,
            ),
            Text(
                Point(width - 35 + offset_x, height - 20, anchor=self.plugin.anchor),
                text="range",
                color=Color(255, 255, 255, 200),
                size=14,
            ),
        ]
