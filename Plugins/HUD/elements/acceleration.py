from Plugins.AR.classes import Point, Rectangle, Color, Text
from ETS2LA.Utils.Values.numbers import SmoothedValue
from Plugins.HUD.classes import HUDWidget
from ETS2LA.Utils.translator import _
import math


class Widget(HUDWidget):
    name = _("Acceleration")
    description = _("Draw the current acceleration of the truck.")
    fps = 10

    acceleration = SmoothedValue("time", 0.5)
    last_speed = 0

    def __init__(self, plugin):
        super().__init__(plugin)

    def settings(self):
        return super().settings()

    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return

        self.speed = self.plugin.data["truckFloat"]["speed"]

        acceleration_x = self.plugin.data["truckVector"]["accelerationX"]
        acceleration_y = self.plugin.data["truckVector"]["accelerationY"]
        acceleration_z = self.plugin.data["truckVector"]["accelerationZ"]

        total = math.sqrt(acceleration_x**2 + acceleration_y**2 + acceleration_z**2)
        if self.speed != self.last_speed:
            self.sign = 1 if self.speed > self.last_speed else -1
            self.last_speed = self.speed

        self.acceleration.smooth(total * self.sign)

        status = self.plugin.tags.status
        acc = False
        if status:
            status = self.plugin.tags.merge(status)
            acc = status.get("AdaptiveCruiseControl", False)

        if acc:
            target_acceleration = self.plugin.tags.acc_target
            if not target_acceleration:
                target_acceleration = 0
            else:
                target_acceleration = self.plugin.tags.merge(target_acceleration)

        if not acc:
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
                    text=f"{self.acceleration.get():.1f}",
                    color=Color(255, 255, 255, 200),
                    size=32,
                ),
                Text(
                    Point(
                        width - 35 + offset_x, height - 20, anchor=self.plugin.anchor
                    ),
                    text="m/s²",
                    color=Color(255, 255, 255, 200),
                    size=14,
                ),
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
                    Point(7 + offset_x, 5, anchor=self.plugin.anchor),
                    text=f"{self.acceleration.get():.1f}",
                    color=Color(255, 255, 255, 200),
                    size=24,
                ),
                Text(
                    Point(7 + offset_x, 30, anchor=self.plugin.anchor),
                    text=f"{target_acceleration:.1f} target"
                    if target_acceleration
                    else "-.-",
                    color=Color(255, 255, 255, 200),
                    size=14,
                ),
                Text(
                    Point(
                        width - 32 + offset_x, height - 20, anchor=self.plugin.anchor
                    ),
                    text="m/s²",
                    color=Color(255, 255, 255, 200),
                    size=14,
                ),
            ]
