from Plugins.AR.classes import Point, Rectangle, Color, Text, Line
from Plugins.HUD.classes import HUDWidget
from ETS2LA.Utils.translator import _


def in_out(value, min_value, max_value):
    if value < min_value:
        return 0.0
    elif value > max_value:
        return 1.0
    else:
        return (value - min_value) / (max_value - min_value)


class Widget(HUDWidget):
    name = _("Assist Information")
    description = _("Draw ACC and Steering status information.")
    fps = 10

    def __init__(self, plugin):
        super().__init__(plugin)

    def settings(self):
        return super().settings()

    assist_alpha = 0.0

    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return

        status = self.plugin.globals.tags.status
        acc = False
        map = False
        if status:
            status = self.plugin.globals.tags.merge(status)
            acc = status.get("AdaptiveCruiseControl", False)
            map = status.get("Map", False)

        if not acc and not map and self.assist_alpha > 0.0:
            self.assist_alpha -= 0.2
        elif (acc or map) and self.assist_alpha < 1.0:
            self.assist_alpha += 0.2

        if self.assist_alpha <= 0.0:
            self.data = []
            return

        target_speed = self.plugin.globals.tags.acc
        game = self.plugin.data["scsValues"]["game"]
        if target_speed:
            target_speed = self.plugin.globals.tags.merge(target_speed)
            if game == "ATS":
                target_speed = target_speed * 3.6 * 0.621371
            else:
                target_speed = target_speed * 3.6  # Convert m/s to km/h
        else:
            target_speed = 0

        alpha = in_out(self.assist_alpha, 0.0, 1.0)
        disabled_color = Color(255, 255, 255, 100 * alpha)
        enabled_color = Color(150, 255, 150, 100 * alpha)

        # Base
        data = [
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20 * alpha),
                fill=Color(255, 255, 255, 10 * alpha),
                rounding=6,
            ),
        ]
        # ACC
        acc_color = enabled_color if acc else disabled_color
        acc_color = Color(acc_color.r, acc_color.g, acc_color.b, 160 * alpha)
        data += [
            Text(
                Point(10 + offset_x, 6, anchor=self.plugin.anchor),
                text=f"{target_speed:.0f}" if acc else "- -",
                color=acc_color,
                size=24,
            ),
            Text(
                Point(10 + offset_x, height - 20, anchor=self.plugin.anchor),
                text="SET",
                color=acc_color,
                size=14,
            ),
        ]
        # Map
        map_color = enabled_color if map else disabled_color
        lane_offset = 5
        num_lines = 5
        start_thickness = 2
        vertical_spacing = 2

        data += []

        for i in range(num_lines):
            # Calculate thickness for this line (decreasing from top to bottom)
            thickness = max(0.5, start_thickness - (i * 0.4))
            v_offset = (i - 2) * vertical_spacing

            line_alpha = 100 * alpha * (1.0 - (i * 0.1))
            line_color = Color(map_color.r, map_color.g, map_color.b, line_alpha)

            # Add first diagonal line (top-left to bottom-right)
            data.append(
                Line(
                    Point(
                        50 + offset_x + lane_offset,
                        height - 8 + v_offset,
                        anchor=self.plugin.anchor,
                    ),
                    Point(
                        width - 60 + offset_x + lane_offset,
                        8 + v_offset,
                        anchor=self.plugin.anchor,
                    ),
                    color=line_color,
                    thickness=thickness,
                )
            )

            # Add second diagonal line (top-right to bottom-left)
            data.append(
                Line(
                    Point(
                        width - 20 + offset_x + lane_offset,
                        height - 8 + v_offset,
                        anchor=self.plugin.anchor,
                    ),
                    Point(
                        90 + offset_x + lane_offset,
                        8 + v_offset,
                        anchor=self.plugin.anchor,
                    ),
                    color=line_color,
                    thickness=thickness,
                )
            )

        self.data = data
