from Plugins.HUD.classes import HUDRenderer
from ETS2LA.Utils.translator import _
from Plugins.AR.classes import Coordinate, Polygon, Color, Fade
import logging
import math


class Renderer(HUDRenderer):
    name = _("Steering Line")
    description = _("Draw steering line from Map.")
    fps = 2

    length = 0
    was_disabled = False

    def __init__(self, plugin):
        super().__init__(plugin)

    def settings(self):
        return super().settings()

    def lane_lines(self, p1, p2):
        dx = p2.x - p1.x
        dz = p2.z - p1.z

        # normalize
        length = math.sqrt(dx * dx + dz * dz)
        if length < 0.0001:
            return []

        dx /= length
        dz /= length

        # perpendicular (rotate 90 degrees in xz-plane)
        perpx = -dz
        perpz = dx
        lane_half_width = 0.25  # steering line width is double this, so 0.5

        # left lane start and end
        left_start = Coordinate(
            p1.x - perpx * lane_half_width,
            p1.y,
            p1.z - perpz * lane_half_width,
            rotation_relative=p1.rotation_relative,
            relative=p1.relative,
        )

        left_end = Coordinate(
            p2.x - perpx * lane_half_width,
            p2.y,
            p2.z - perpz * lane_half_width,
            rotation_relative=p2.rotation_relative,
            relative=p2.relative,
        )

        # right lane start and end
        right_start = Coordinate(
            p1.x + perpx * lane_half_width,
            p1.y,
            p1.z + perpz * lane_half_width,
            rotation_relative=p1.rotation_relative,
            relative=p1.relative,
        )

        right_end = Coordinate(
            p2.x + perpx * lane_half_width,
            p2.y,
            p2.z + perpz * lane_half_width,
            rotation_relative=p2.rotation_relative,
            relative=p2.relative,
        )

        return (left_start, left_end, right_end, right_start)

    def draw(self):
        if not self.plugin.data:
            return

        try:
            points = self.plugin.tags.steering_points
            points = self.plugin.tags.merge(points)

            status = self.plugin.tags.status
            if status:
                map_status = self.plugin.tags.merge(status)["Map"]
            else:
                map_status = None

            if not map_status:
                self.was_disabled = True
            elif self.was_disabled:
                self.fps = 20
                self.was_disabled = False
                self.length = 0

            if not points or len(points) < 2:
                self.data = []
                return

            if len(points) > self.length:
                self.length += 1
                self.fps = 20
            elif len(points) < self.length:
                self.length = len(points)
                self.fps = 2

            points = points[: self.length]
            steering_data = []
            for i, point in enumerate(points):
                if i == 0:
                    continue

                lane_lines = self.lane_lines(
                    Coordinate(*point), Coordinate(*points[i - 1])
                )
                if not lane_lines or len(lane_lines) < 2:
                    continue

                steering_data.append(
                    Polygon(
                        lane_lines,
                        color=Color(0, 0, 0, 0)
                        if not map_status
                        else Color(0, 0, 0, 0),
                        fill=Color(150, 150, 150, 50)
                        if not map_status
                        else Color(150, 255, 150, 50),
                        fade=Fade(
                            prox_fade_end=10,
                            prox_fade_start=20,
                            dist_fade_start=50,
                            dist_fade_end=150,
                        ),
                    )
                )

            self.data = steering_data
        except Exception:
            logging.exception("Error while drawing steering line")
            self.data = []
            pass
