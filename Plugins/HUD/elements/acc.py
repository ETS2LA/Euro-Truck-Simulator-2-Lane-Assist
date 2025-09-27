from Plugins.AR.classes import Point, Rectangle, Color, Text, Polygon, Fade, Coordinate
from Modules.Traffic.classes import Vehicle
from Plugins.HUD.classes import HUDRenderer
from ETS2LA.Utils.translator import _


class Renderer(HUDRenderer):
    name = _("ACC Information")
    description = _("Draw ACC information like vehicle distance and speed.")
    fps = 30

    def __init__(self, plugin):
        super().__init__(plugin)

    def settings(self):
        return super().settings()

    def render_vehicle(self, vehicle: Vehicle):
        truck_x = self.plugin.data["truckPlacement"]["coordinateX"]
        truck_y = self.plugin.data["truckPlacement"]["coordinateY"]
        truck_z = self.plugin.data["truckPlacement"]["coordinateZ"]

        return_data = []

        game = self.plugin.data["scsValues"]["game"]
        speed = vehicle.speed * 3.6 if game == "ETS2" else vehicle.speed * 2.23694
        speed_unit = "km/h" if game == "ETS2" else "mph"

        # Line under the vehicle
        front_left, front_right, back_right, back_left = vehicle.get_corners(
            correction_multiplier=-1
        )
        distance = Coordinate(*front_left.tuple()).get_distance_to(
            truck_x, truck_y, truck_z
        )

        if distance > 120:
            return []

        center_back = [
            (back_left.x + back_right.x) / 2,
            (back_left.y + back_right.y) / 2,
            (back_left.z + back_right.z) / 2,
        ]
        center_right = [
            (front_right.x + back_right.x) / 2,
            (front_right.y + back_right.y) / 2,
            (front_right.z + back_right.z) / 2,
        ]
        center_left = [
            (front_left.x + back_left.x) / 2,
            (front_left.y + back_left.y) / 2,
            (front_left.z + back_left.z) / 2,
        ]
        center_front = [
            (front_left.x + front_right.x) / 2,
            (front_left.y + front_right.y) / 2,
            (front_left.z + front_right.z) / 2,
        ]

        relative_front_left = self.plugin.get_relative_to_head(
            Coordinate(*front_left.tuple())
        )
        relative_front_right = self.plugin.get_relative_to_head(
            Coordinate(*front_right.tuple())
        )
        relative_back_right = self.plugin.get_relative_to_head(
            Coordinate(*back_right.tuple())
        )
        relative_back_left = self.plugin.get_relative_to_head(
            Coordinate(*back_left.tuple())
        )
        relative_center_back = self.plugin.get_relative_to_head(
            Coordinate(*center_back)
        )
        relative_center_right = self.plugin.get_relative_to_head(
            Coordinate(*center_right)
        )
        relative_center_left = self.plugin.get_relative_to_head(
            Coordinate(*center_left)
        )
        relative_center_front = self.plugin.get_relative_to_head(
            Coordinate(*center_front)
        )

        distance_unit = "m" if game == "ETS2" else "ft"
        distance = (
            round(distance, 1) if distance_unit == "m" else round(distance * 3.28084, 1)
        )

        color = [255, 255, 255]
        alpha = 0.5
        AEB = self.plugin.tags.AEB
        if AEB and self.plugin.tags.merge(AEB):
            color = [255, 120, 120]
            alpha = 1

        # 3D box
        return_data = [
            Polygon(
                [
                    relative_front_left,
                    relative_front_right,
                    relative_back_right,
                    relative_back_left,
                ],
                color=Color(*color, 120 * alpha),
                fill=Color(*color, 80 * alpha),
                fade=Fade(
                    prox_fade_end=0,
                    prox_fade_start=0,
                    dist_fade_start=80,
                    dist_fade_end=100,
                ),
            )
        ]

        angle = vehicle.rotation.euler()[1]
        rotationX = self.plugin.data["truckPlacement"]["rotationX"]
        truck_angle = rotationX * 360 - 360
        diff = truck_angle - angle

        closest_face = None
        if diff < 45 and diff > -45:
            closest_face = relative_center_back
        elif diff >= 45 and diff < 135:
            closest_face = relative_center_right
        elif diff <= -45 and diff > -135:
            closest_face = relative_center_left
        else:
            closest_face = relative_center_front

        # Rectangle and text under the vehicle
        return_data += [
            Rectangle(
                Point(-50, 20, anchor=closest_face),
                Point(50, 40, anchor=closest_face),
                rounding=6,
                custom_distance=distance,
                color=Color(*color, 40 * alpha),
                fill=Color(*color, 20 * alpha),
                fade=Fade(
                    prox_fade_end=0,
                    prox_fade_start=0,
                    dist_fade_start=80,
                    dist_fade_end=100,
                ),
            ),
            Text(
                Point(-45, 22, anchor=closest_face),
                text=f"{speed:.0f} {speed_unit}",
                size=16,
                custom_distance=distance,
                color=Color(*color, 255 * alpha),
                fade=Fade(
                    prox_fade_end=0,
                    prox_fade_start=0,
                    dist_fade_start=80,
                    dist_fade_end=100,
                ),
            ),
            Text(
                Point(15, 22, anchor=closest_face),
                text=f"{distance:.0f} {distance_unit}",
                size=16,
                custom_distance=distance,
                color=Color(*color, 255 * alpha),
                fade=Fade(
                    prox_fade_end=0,
                    prox_fade_start=0,
                    dist_fade_start=80,
                    dist_fade_end=100,
                ),
            ),
        ]

        return return_data

    def draw(self):
        if not self.plugin.data:
            self.data = []
            return

        targets = self.plugin.tags.vehicle_highlights
        target_ids = []
        if targets:
            for value in targets.values():
                if value:
                    target_ids.extend(value)

        if not target_ids:
            self.data = []
            return

        vehicles = self.plugin.modules.Traffic.run()
        if vehicles is None:
            vehicles = []

        highlighted_vehicles = []
        if len(targets) > 0:
            for vehicle in vehicles:
                if vehicle.id in target_ids:
                    highlighted_vehicles.append(vehicle)

        if not highlighted_vehicles:
            self.data = []
            return

        data = []
        for vehicle in highlighted_vehicles:
            if not isinstance(vehicle, Vehicle):
                continue

            if vehicle.trailers:
                trailer = vehicle.trailers[-1]
                fake_vehicle = Vehicle(
                    trailer.position,
                    trailer.rotation,
                    trailer.size,
                    vehicle.speed,
                    vehicle.acceleration,
                    0,
                    [],
                    vehicle.id,
                    vehicle.is_tmp,
                    True,
                )
                data.extend(self.render_vehicle(fake_vehicle))
            else:
                data.extend(self.render_vehicle(vehicle))

        self.data = data
