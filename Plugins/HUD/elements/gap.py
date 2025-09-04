from Plugins.AR.classes import Point, Rectangle, Color, Text
from Plugins.HUD.classes import HUDWidget
from ETS2LA.Utils.translator import _


class Widget(HUDWidget):
    name = _("ACC Gap")
    description = _("Shows the gap to the vehicle in front.")
    fps = 10

    def __init__(self, plugin):
        super().__init__(plugin)

    def settings(self):
        return super().settings()

    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return

        target = self.plugin.tags.acc_gap
        target = self.plugin.tags.merge(target) if target else 0
        if not target:
            target = 0

        distance = self.plugin.tags.vehicle_in_front_distance
        distance = self.plugin.tags.merge(distance) if distance else 0
        if not distance:
            distance = 0

        if distance <= 0 or distance >= 100:
            gap_text = "0"
        else:
            gap_text = f"{distance:.0f}"

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
                text=gap_text,
                color=Color(255, 255, 255, 200),
                size=24,
            ),
            Text(
                Point(7 + offset_x, 30, anchor=self.plugin.anchor),
                text=f"{target:.0f} target",
                color=Color(255, 255, 255, 200),
                size=14,
            ),
            Text(
                Point(width - 18 + offset_x, height - 20, anchor=self.plugin.anchor),
                text="m",
                color=Color(255, 255, 255, 200),
                size=14,
            ),
        ]
