# Framework
from ETS2LA.Events import events
from ETS2LA.Plugin import ETS2LAPlugin, PluginDescription, Author
from ETS2LA.Utils.translator import _

# Local imports
from Plugins.AdaptiveCruiseControl.controls import enable_disable, increment, decrement
from Plugins.AdaptiveCruiseControl.speed import get_maximum_speed_for_points
from Plugins.AdaptiveCruiseControl.settings import SettingsMenu, settings

# ETS2LA imports
from Plugins.AR.classes import Coordinate, Polygon, Fade, Color
from Plugins.Map.classes import Position, Prefab
from Modules.Semaphores.classes import TrafficLight, Gate
from ETS2LA.Utils.Values.numbers import SmoothedValue
from ETS2LA.Utils.Values.graphing import PIDGraph
from Modules.Traffic.classes import Vehicle

# Python imports
from typing import cast
import traceback
import logging
import math
import time


class ACCVehicle(Vehicle):
    distance = 0
    time_gap = 0

    def __init__(self, vehicle: Vehicle, distance: float, time_gap: float):
        super().__init__(
            vehicle.position,
            vehicle.rotation,
            vehicle.size,
            vehicle.speed,
            vehicle.acceleration,
            vehicle.trailer_count,
            vehicle.trailers,
            vehicle.id,
            vehicle.is_tmp,
            vehicle.is_trailer,
        )
        self.distance = distance
        self.time_gap = time_gap


class ACCTrafficLight(TrafficLight):
    distance = 0

    def __init__(self, traffic_light: TrafficLight, distance: float):
        super().__init__(
            traffic_light.position,
            traffic_light.cx,
            traffic_light.cy,
            traffic_light.quat,
            traffic_light.time_left,
            traffic_light.state,
            traffic_light.id,
        )
        self.distance = distance


class ACCGate(Gate):
    distance = 0

    def __init__(self, gate: Gate, distance: float):
        super().__init__(
            gate.position,
            gate.cx,
            gate.cy,
            gate.quat,
            gate.time_left,
            gate.state,
            gate.id,
        )
        self.distance = distance


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name=_("Adaptive Cruise Control"),
        version="1.0",
        description=_(
            "Adaptive Cruise Control (ACC) provides automatic acceleration and braking depending on road conditions and vehicles ahead."
        ),
        modules=["SDKController", "TruckSimAPI", "Traffic", "Semaphores"],
        tags=["Base", "Speed Control"],
        fps_cap=15,
    )

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4",
    )

    controls = [enable_disable, increment, decrement]

    pages = [SettingsMenu]

    # Variables
    accel = 0  # current acceleration value between -1 and 1
    speed = 0  # m/s
    last_speed = 0  # m/s
    sign = 1  # 1 or -1

    speedlimit = 0  # m/s
    acceleration = SmoothedValue("time", 0.2)  # m/s^2
    enabled = False

    api_data = None
    speed_offset_type = "Absolute"
    speed_offset = 0
    manual_speed_offset = 0

    holding_up = False
    holding_down = False
    last_change = 0

    # ACC Parameters
    overwrite_speed = 30  # km/h
    base_max_accel = 3.0  # m/s^2
    base_comfort_decel = -2.0  # m/s^2
    base_emergency_decel = -6.0  # m/s^2
    base_time_gap_seconds = 2.0  # seconds

    # These get adjusted
    max_accel = 3.0
    comfort_decel = -2.0
    emergency_decel = -6.0
    time_gap_seconds = 2.0

    # PID gains
    kp_accel = 0.30  # Proportional gain
    ki_accel = 0.08  # Integral gain
    kd_accel = 0.05  # Derivative gain

    # PID state variables
    graph = PIDGraph(history=10)
    accel_errors = []
    last_accel_error = 0.0  # For derivative term
    last_control_output = 0.0  # For smoothing changes
    last_time = time.time()

    # Control smoothing
    output_smoothing_factor = 0.6  # Lower value = smoother but slower response
    pid_sample_time = 0.05  # 50ms for PID cycle

    max_speed = SmoothedValue("time", 0.5)

    api = None
    controller = None

    map_points = None

    def imports(self):
        global Controller, np, screeninfo, json, cv2, os
        from Modules.SDKController.main import SCSController as Controller
        import numpy as np
        import screeninfo
        import json
        import cv2
        import os

    def calculate_speedlimit_constraint(self):
        speed_error = self.speedlimit - self.speed
        speed_limit_accel = speed_error * 0.5

        if speed_error * 3.6 > 10:
            speed_limit_accel = min(
                self.max_accel, max(self.emergency_decel, speed_limit_accel)
            )
        else:
            speed_limit_accel = min(
                self.max_accel, max(self.comfort_decel, speed_limit_accel)
            )

        if self.speed < self.speedlimit + 5 / 3.6:
            speed_limit_accel *= 0.75

        if self.speed > self.speedlimit + 10 / 3.6:
            speed_limit_accel *= 1.5

        return speed_limit_accel

    def calculate_leading_vehicle_constraint(self, in_front: ACCVehicle):
        if in_front.is_tmp:
            minimum_gap = 5 + in_front.size.length / 2  # meters at 0 speed
        else:
            minimum_gap = 5 + in_front.size.length * 0.8  # meters at 0 speed

        desired_gap = max(self.time_gap_seconds * self.speed, minimum_gap)
        self.tags.acc_gap = desired_gap

        relative_speed = self.speed - in_front.speed
        gap_error = (in_front.distance - desired_gap) / max((desired_gap / 30), 1)

        # Relative speed is more important at higher speeds due
        # to vehicles merging in front.
        if self.speed > 10 / 3.6:
            following_accel = 0.4 * gap_error - 2.0 * relative_speed
        else:
            following_accel = 1.0 * gap_error - 0.7 * relative_speed

        following_accel += 0.3 * in_front.acceleration

        # following_accel = gap_error / 20 if gap_error < 0 else gap_error
        # if relative_speed < 0:  # vehicle in front is faster
        #     following_accel -= relative_speed * 0.5
        #     following_accel -= in_front.acceleration * 2 * (self.speed / 80 / 3.6)
        # else:  # vehicle in front is slower
        #     if following_accel > 0:
        #         following_accel *= max(
        #             1 - (relative_speed / 50 / 3.6), 0.1
        #         )  # if the vehicle in front is stopped, then we want to be more careful
        #     following_accel -= relative_speed * 4
        #     following_accel -= in_front.acceleration * 1.5 * (self.speed / 80 / 3.6)

        following_accel = min(self.max_accel, following_accel)

        if following_accel < -5.0:
            self.tags.AEB = True
        else:
            self.tags.AEB = False

        return following_accel

    def calculate_traffic_light_constraint(
        self, distance: float, allow_acceleration: bool = False
    ):
        if distance > self.speed * 6 and (distance > 40 or allow_acceleration):
            return 999  # No need to brake yet

        if distance > 0:
            distance -= 5  # Stop 5 meters before the light

            if distance < 0:
                return self.emergency_decel  # Stop at the light

            # v²/(2*s) formula for constant deceleration to stop
            required_decel = (self.speed**2) / (2 * distance)

            red_light_accel = -required_decel * 1.2

            if distance < 50:
                red_light_accel *= 1.2

            # Limit to comfort range unless emergency
            if distance > 20:
                red_light_accel = max(self.comfort_decel, red_light_accel)
            else:
                red_light_accel = max(self.emergency_decel, red_light_accel)

            if red_light_accel < 0.02 and self.speed < 1:  # 1m/s = 4kph
                red_light_accel = min(-1, red_light_accel)

            return red_light_accel
        else:
            return self.emergency_decel

    def update_parameters(self):
        aggressiveness = settings.aggressiveness  # 'Aggressive', 'Normal', 'Eco'
        distance_setting = settings.following_distance
        if isinstance(distance_setting, str):
            distance_setting = 2

        overwrite_speed = settings.overwrite_speed
        max_speed = settings.max_speed

        speed_offset_type = settings.speed_offset_type
        speed_offset = settings.speed_offset

        ignore_traffic_lights = settings.ignore_traffic_lights
        ignore_speed_limit = settings.ignore_speed_limit

        if ignore_speed_limit is None:
            ignore_speed_limit = False
            settings.ignore_speed_limit = ignore_speed_limit

        if ignore_traffic_lights is None:
            ignore_traffic_lights = False
            settings.ignore_traffic_lights = ignore_traffic_lights

        if aggressiveness is None:
            aggressiveness = "Normal"
            settings.aggressiveness = aggressiveness

        if distance_setting is None:
            distance_setting = 2
            settings.following_distance = distance_setting

        if overwrite_speed is None:
            overwrite_speed = 30
            settings.overwrite_speed = overwrite_speed

        if max_speed is None:
            max_speed = 0
            settings.max_speed = max_speed

        if speed_offset_type is None:
            speed_offset_type = "Absolute"
            settings.speed_offset_type = speed_offset_type

        if speed_offset is None:
            speed_offset = 0
            settings.speed_offset = speed_offset

        self.overwrite_speed = overwrite_speed
        self.speed_offset = speed_offset

        self.base_time_gap_seconds = distance_setting
        if aggressiveness == "Aggressive":
            self.max_accel = self.base_max_accel * 2
            self.comfort_decel = self.base_comfort_decel * 2
            self.time_gap_seconds = self.base_time_gap_seconds * 0.75
        elif aggressiveness == "Eco":
            self.max_accel = self.base_max_accel * 0.66
            self.comfort_decel = self.base_comfort_decel * 0.66
            self.time_gap_seconds = self.base_time_gap_seconds * 1.25
        else:
            self.max_accel = self.base_max_accel
            self.comfort_decel = self.base_comfort_decel
            self.time_gap_seconds = self.base_time_gap_seconds

        self.speed_offset_type = speed_offset_type
        if self.speed_offset_type is None:
            self.speed_offset_type = "Absolute"

        if settings.unlock_pid:
            self.kp_accel = settings.pid_kp
            self.ki_accel = settings.pid_ki
            self.kd_accel = settings.pid_kd
            if self.kp_accel is None:
                self.kp_accel = 0.30
                settings.pid_kp = self.kp_accel
            if self.ki_accel is None:
                self.ki_accel = 0.08
                settings.pid_ki = self.ki_accel
            if self.kd_accel is None:
                self.kd_accel = 0.05
                settings.pid_kd = self.kd_accel

            # Increase the derivative term if no cargo is loaded.
            # This will reduce oscillations due to the higher acceleration
            # and deceleration of an empty truck.
            if self.api_data and not self.api_data["configString"]["cargo"]:
                self.kd_accel *= 2

    def calculate_target_acceleration(
        self,
        in_front: ACCVehicle | None = None,
        traffic_light: ACCTrafficLight | None = None,
        gate: ACCGate | None = None,
        stop_in: float | None = None,
    ) -> float:
        target_accelerations = []

        # Speed Limit
        speed_limit_accel = self.calculate_speedlimit_constraint()
        target_accelerations.append(speed_limit_accel)

        # Leading Vehicle
        if in_front is not None:
            following_accel = self.calculate_leading_vehicle_constraint(in_front)
            target_accelerations.append(following_accel)

        # Stop in - Works the same as traffic lights, just stops at that distance.
        if stop_in is not None and stop_in > 0:
            stop_in_accel = self.calculate_traffic_light_constraint(
                stop_in, allow_acceleration=True
            )
            target_accelerations.append(stop_in_accel)

        # Red Light - Only check if traffic lights are not ignored
        if traffic_light and not settings.ignore_traffic_lights:
            if (
                traffic_light.state == 2 or traffic_light.state == 1
            ):  # red or changing to red
                red_light_accel = self.calculate_traffic_light_constraint(
                    traffic_light.distance
                )
                target_accelerations.append(red_light_accel)

        # Gate
        if gate:
            if gate.state < 3:  # Closing, closed or opening
                # Logic is the same as the traffic lights
                gate_accel = self.calculate_traffic_light_constraint(gate.distance)
                target_accelerations.append(gate_accel)

        # Take most restrictive (minimum)
        if target_accelerations:
            return min(target_accelerations)
        else:
            # Maintain speed
            return 0.0

    def init(self):
        self.api = self.modules.TruckSimAPI
        self.controller = self.modules.SDKController.SCSController()
        self.controller = cast(Controller, self.controller)
        self.tags.status = {"AdaptiveCruiseControl": self.enabled}

        # if variables.DEVELOPMENT_MODE:
        #     self.graph.setup_plot()

    @events.on("toggle_acc")
    def on_toggle_acc(self, event_object, state: bool):
        if not state:
            return  # Callback for the lift up event

        self.enabled = not self.enabled
        self.tags.status = {"AdaptiveCruiseControl": self.enabled}

    @events.on("takeover")
    def on_takeover(self, event_object, *args, **kwargs):
        self.enabled = False
        self.tags.status = {"AdaptiveCruiseControl": self.enabled}

    @events.on("increment_speed")
    def on_increment_speed(self, event_object, state: bool):
        if not state:
            self.holding_up = False
            self.last_change = 0
            return  # Callback for the lift up event
        self.holding_up = True

    @events.on("decrement_speed")
    def on_decrement_speed(self, event_object, state: bool):
        if not state:
            self.holding_down = False
            self.last_change = 0
            return  # Callback for the lift up event
        self.holding_down = True

    def get_distance_to_point(self, point1: list, point2: list) -> float:
        if len(point1) == 2 and len(point2) == 2:
            return math.sqrt(
                (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
            )
        elif len(point1) == 3 and len(point2) == 3:
            return math.sqrt(
                (point1[0] - point2[0]) ** 2
                + (point1[1] - point2[1]) ** 2
                + (point1[2] - point2[2]) ** 2
            )

    def get_distance(self, p1: list, p2: list):
        if len(p1) == 2:
            return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        elif len(p1) == 3:
            return math.sqrt(
                (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2
            )
        return math.inf

    def get_vehicle_in_front(self, api_data: dict) -> ACCVehicle:
        # TODO: This function is ugly and unoptimized,
        #       rewrite it.
        vehicles: list[Vehicle] = self.modules.Traffic.run()

        plugin_vehicles = self.tags.vehicles
        plugin_vehicles = self.tags.merge(plugin_vehicles)

        if plugin_vehicles is not None:
            vehicles += [
                self.modules.Traffic.create_vehicle_from_dict(vehicle)
                for vehicle in plugin_vehicles
            ]

        if vehicles is None or vehicles == []:
            return None

        vehicles_in_front = []

        truck_x = api_data["truckPlacement"]["coordinateX"]
        truck_y = api_data["truckPlacement"]["coordinateZ"]
        rotation = api_data["truckPlacement"]["rotationX"] * 360
        if rotation < 0:
            rotation += 360
        rotation = math.radians(rotation)

        points = self.map_points

        if (
            not isinstance(points, list)
            or len(points) == 0
            or (not isinstance(points[0], (list, tuple)))
        ):
            return None

        if len(points) == 1:
            point = points[0]
            points = [[truck_x, truck_y], [point[0], point[1]]]

        if len(points) == 2:
            # Generate 10 points between the two points
            x1 = points[0][0]
            y1 = points[0][1]
            x2 = points[1][0]
            y2 = points[1][1]
            points = [
                [x1 + (x2 - x1) * i / 10, y1 + (y2 - y1) * i / 10] for i in range(10)
            ]

        if not isinstance(vehicles, list):
            return None

        # Expand vehicles with trailers into multiple vehicles
        expanded_vehicles = []
        for vehicle in vehicles:
            expanded_vehicles.append(vehicle)
            for trailer in vehicle.trailers:
                expanded_vehicles.append(
                    Vehicle(
                        position=trailer.position,
                        rotation=trailer.rotation,
                        size=trailer.size,
                        speed=vehicle.speed,
                        acceleration=vehicle.acceleration,
                        trailer_count=0,
                        trailers=[],
                        id=vehicle.id,
                        is_tmp=vehicle.is_tmp,
                        is_trailer=True,
                    )
                )

        for vehicle in expanded_vehicles:
            if len(vehicle.trailers) > 0:
                x = vehicle.trailers[-1].position.x
                y = vehicle.trailers[-1].position.z
                z = vehicle.trailers[-1].position.y
            else:
                x = vehicle.position.x
                y = vehicle.position.z
                z = vehicle.position.y

            closest_point_distance = math.inf
            index = 0
            for point in points:
                distance = self.get_distance_to_point(
                    [x, y, z], [point[0], point[2], point[1]]
                )
                if distance < closest_point_distance:
                    closest_point_distance = distance
                else:
                    # Make an intermediate point
                    lastPoint = points[index - 1]
                    intermediatePoint = [
                        (lastPoint[0] + point[0]) / 2,
                        (lastPoint[2] + point[1]) / 2,
                        (lastPoint[1] + point[2]) / 2,
                    ]
                    distance = self.get_distance_to_point([x, y, z], intermediatePoint)
                    if distance < closest_point_distance:
                        closest_point_distance = distance
                    break
                index += 1

            if (
                closest_point_distance < 3
            ):  # Road is 4.5m wide, want to check 3m (to allow for a little bit of error)
                self.last_vehicle_time = time.perf_counter()
                vehicles_in_front.append(
                    (self.get_distance_to_point([x, y], [truck_x, truck_y]), vehicle)
                )

        if len(vehicles_in_front) == 0:
            return None

        closest_distance = math.inf
        closest_vehicle = None
        for distance, vehicle in vehicles_in_front:
            if distance < closest_distance:
                if vehicle.is_tmp:
                    closest_distance = distance - (vehicle.size.length * 0.5)
                else:
                    # ETS2 reports the middle of the vehicle closer to the front
                    closest_distance = distance - (vehicle.size.length * 0.8)

                closest_vehicle = vehicle

        if closest_vehicle is None:
            return None

        time_to_vehicle = (
            closest_distance + (closest_vehicle.speed - self.speed)
        ) / self.speed
        self.tags.vehicle_highlights = [closest_vehicle.id]
        self.tags.vehicle_in_front_distance = closest_distance

        return ACCVehicle(closest_vehicle, closest_distance, time_to_vehicle)

    def get_valid_lights(
        self,
        api_data: dict,
        lights: list,
        check_rotation: bool = True,
        check_lateral: bool = True,
    ) -> list:
        valid_lights = []
        rotationX = api_data["truckPlacement"]["rotationX"]
        angle = rotationX * 360
        if angle < 0:
            angle = 360 + angle
        truck_rotation = math.radians(angle)
        truck_vector = [-math.sin(truck_rotation), -math.cos(truck_rotation)]
        truck_pos = [
            api_data["truckPlacement"]["coordinateX"],
            api_data["truckPlacement"]["coordinateZ"],
        ]

        for light in lights:
            yaw = light.quat.euler()[1]
            light_vector = [-math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))]

            # Check if within 45 degrees forward
            angle = math.acos(
                truck_vector[0] * light_vector[0] + truck_vector[1] * light_vector[1]
            )
            limit = math.radians(45)
            if angle < limit or not check_rotation:
                light_pos = [
                    light.position.x + 512 * light.cx,
                    light.position.z + 512 * light.cy,
                ]
                to_light_vector = [
                    light_pos[0] - truck_pos[0],
                    light_pos[1] - truck_pos[1],
                ]

                total_distance = math.sqrt(
                    to_light_vector[0] ** 2 + to_light_vector[1] ** 2
                )

                # Project to the truck's forward vector
                # (to get the forward distance to the light)
                truck_vector_normalized = [truck_vector[0], truck_vector[1]]
                vector_length = math.sqrt(
                    truck_vector_normalized[0] ** 2 + truck_vector_normalized[1] ** 2
                )
                truck_vector_normalized = [
                    truck_vector_normalized[0] / vector_length,
                    truck_vector_normalized[1] / vector_length,
                ]

                forward_distance = (
                    to_light_vector[0] * truck_vector_normalized[0]
                    + to_light_vector[1] * truck_vector_normalized[1]
                )

                if forward_distance > 0:
                    # Lateral distance (for filtering out lights too far to the side)
                    lateral_distance = (
                        abs(total_distance**2 - forward_distance**2) ** 0.5
                    )
                    if (
                        lateral_distance < 11 or not check_lateral
                    ):  # 2 * 4.5m lanes + 2m margin
                        valid_lights.append((forward_distance, light))

        return valid_lights

    def get_traffic_light_in_front(self, api_data: dict) -> ACCTrafficLight:
        try:
            lights = self.modules.Semaphores.run()
        except Exception:
            return None

        points = self.map_points

        if points is None or points == []:
            return None
        if lights is None:
            return None

        lights = [light for light in lights if light.type == "traffic_light"]
        lights = [
            light
            for light in lights
            if self.get_distance(
                [
                    api_data["truckPlacement"]["coordinateX"],
                    api_data["truckPlacement"]["coordinateZ"],
                ],
                [light.position.x + 512 * light.cx, light.position.z + 512 * light.cy],
            )
            < 150
        ]
        if len(lights) == 0:
            return None

        valid_lights = self.get_valid_lights(api_data, lights)
        if len(valid_lights) == 0:
            return None

        closest_distance = math.inf
        closest_light = None
        for distance, light in valid_lights:
            if distance < closest_distance:
                closest_light = ACCTrafficLight(light, distance)
                closest_distance = distance

        return closest_light

    def get_next_prefab_traffic_light(
        self, api_data: dict
    ) -> tuple[list[Position], ACCTrafficLight]:
        try:
            live_semaphores = self.modules.Semaphores.run()
        except Exception:
            return None, None

        prefab = self.tags.next_intersection
        prefab: Prefab = self.tags.merge(prefab)
        if not prefab:
            return None, None

        index = self.tags.next_intersection_lane
        index: int = self.tags.merge(index)
        if index is None:
            return None, None

        truck_x = api_data["truckPlacement"]["coordinateX"]
        truck_y = api_data["truckPlacement"]["coordinateY"]
        truck_z = api_data["truckPlacement"]["coordinateZ"]

        route = prefab.nav_routes[index]

        semaphores = []
        for curve in route.curves:
            if curve.semaphore_id != -1:
                possibilities = [
                    light
                    for light in live_semaphores
                    if light.id == curve.semaphore_id and light.type == "traffic_light"
                ]
                closest = min(
                    possibilities,
                    key=lambda light: self.get_distance(
                        [curve.start.x, curve.start.y, curve.start.z],
                        [
                            light.position.x + 512 * light.cx,
                            light.position.y,
                            light.position.z + 512 * light.cy,
                        ],
                    ),
                    default=None,
                )
                if closest is not None and closest not in semaphores:
                    # We can pretty much assume that any lights should be
                    # within 10m of the prefab bounds.
                    if prefab.bounding_box.is_in(
                        Position(
                            closest.position.x + 512 * closest.cx,
                            closest.position.z + 512 * closest.cy,
                            closest.position.y,
                        ),
                        offset=10,
                    ):
                        semaphores.append(closest)

        if not semaphores:
            return None, None

        closest = None
        closest_distance = math.inf
        for semaphore in semaphores:
            distance = self.get_distance(
                [truck_x, truck_y, truck_z],
                [
                    semaphore.position.x + 512 * semaphore.cx,
                    semaphore.position.y,
                    semaphore.position.z + 512 * semaphore.cy,
                ],
            )

            if distance < closest_distance:
                closest_distance = distance
                closest = semaphore

        first_distance = self.get_distance(
            [truck_x, truck_y, truck_z], route.points[0].list()
        )
        last_distance = self.get_distance(
            [truck_x, truck_y, truck_z], route.points[-1].list()
        )
        if first_distance < last_distance:
            if closest is not None:
                return route.points, ACCTrafficLight(closest, first_distance)
        else:
            if closest is not None:
                return route.points, ACCTrafficLight(closest, last_distance)

        return None, None

    def get_gate_in_front(self, api_data: dict) -> ACCGate:
        try:
            gates = self.modules.Semaphores.run()
        except Exception:
            return None

        points = self.map_points

        if points is None or points == []:
            return None
        if gates is None:
            return None

        gates = [gate for gate in gates if gate.type == "gate"]
        gates = [
            gate
            for gate in gates
            if self.get_distance(
                [
                    api_data["truckPlacement"]["coordinateX"],
                    api_data["truckPlacement"]["coordinateZ"],
                ],
                [gate.position.x + 512 * gate.cx, gate.position.z + 512 * gate.cy],
            )
            < 150
        ]
        if len(gates) == 0:
            return None

        valid_gates = []
        rotationX = api_data["truckPlacement"]["rotationX"]
        angle = rotationX * 360
        if angle < 0:
            angle = 360 + angle
        truck_rotation = math.radians(angle)
        truck_vector = [-math.sin(truck_rotation), -math.cos(truck_rotation)]
        truck_pos = [
            api_data["truckPlacement"]["coordinateX"],
            api_data["truckPlacement"]["coordinateZ"],
        ]

        for gate in gates:
            yaw = gate.quat.euler()[1]
            gate_vector = [-math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))]

            # Check if within 45 degrees forward
            angle = math.acos(
                truck_vector[0] * gate_vector[0] + truck_vector[1] * gate_vector[1]
            )
            limit = math.radians(45)
            if angle < limit:
                gate_pos = [
                    gate.position.x + 512 * gate.cx,
                    gate.position.z + 512 * gate.cy,
                ]
                to_gate_vector = [
                    gate_pos[0] - truck_pos[0],
                    gate_pos[1] - truck_pos[1],
                ]

                total_distance = math.sqrt(
                    to_gate_vector[0] ** 2 + to_gate_vector[1] ** 2
                )

                # Project to the truck's forward vector
                # (to get the forward distance to the gate)
                truck_vector_normalized = [truck_vector[0], truck_vector[1]]
                vector_length = math.sqrt(
                    truck_vector_normalized[0] ** 2 + truck_vector_normalized[1] ** 2
                )
                truck_vector_normalized = [
                    truck_vector_normalized[0] / vector_length,
                    truck_vector_normalized[1] / vector_length,
                ]

                forward_distance = (
                    to_gate_vector[0] * truck_vector_normalized[0]
                    + to_gate_vector[1] * truck_vector_normalized[1]
                )

                if forward_distance > 0:
                    # Lateral distance (for filtering out gates too far to the side)
                    lateral_distance = (
                        abs(total_distance**2 - forward_distance**2) ** 0.5
                    )
                    if lateral_distance < 11:  # 2 * 4.5m lanes + 2m margin
                        valid_gates.append((forward_distance, gate))

        if len(valid_gates) == 0:
            return None

        closest_distance = math.inf
        closest_gate = None
        for distance, gate in valid_gates:
            if distance < closest_distance:
                closest_gate = ACCGate(gate, distance)
                closest_distance = distance

        return closest_gate

    def get_target_speed(self, api_data: dict) -> float:
        points = self.map_points
        if points is not None:
            max_speed = get_maximum_speed_for_points(
                points,
                api_data["truckPlacement"]["coordinateX"],
                api_data["truckPlacement"]["coordinateZ"],
            )
            smoothed_max_speed = self.max_speed(max_speed)
        else:
            smoothed_max_speed = 999

        if settings.ignore_speed_limit:
            target_speed = 999 / 3.6  # Set highest speed to 999 km/h
        else:
            target_speed = api_data["truckFloat"]["speedLimit"]
            if target_speed < 0:
                target_speed = self.overwrite_speed / 3.6

        offset = self.speed_offset + self.manual_speed_offset
        if self.speed_offset_type == "Percentage":
            target_speed += target_speed * offset / 100
        else:
            target_speed += offset / 3.6

        if target_speed > smoothed_max_speed and smoothed_max_speed > 0:
            target_speed = smoothed_max_speed

        if settings.max_speed:
            if target_speed > settings.max_speed / 3.6:
                target_speed = settings.max_speed / 3.6

        return target_speed

    def reset(self) -> None:
        self.controller.aforward = float(0)
        self.controller.abackward = float(0)

    set_zero = False

    def set_accel_brake(self, accel: float) -> None:
        is_reversing = False
        clutch = 0.0
        speed = 0.0
        if self.api_data:
            gear = self.api_data["truckInt"]["gear"]
            clutch = self.api_data["truckFloat"]["userClutch"]
            speed = self.api_data["truckFloat"]["speed"] * 3.6
            is_reversing = gear < 0

        self.accel = min(1, max(-1, accel))
        target_accel = self.accel
        self.tags.acceleration = self.accel
        
        override = 0.0
        try:
            override_tag = self.tags.override_acceleration
            override_tag = self.tags.merge(override_tag)
            override_tag = float(override_tag)
            if override_tag != 0.0:
                override = override_tag
        except Exception:
            pass
        
        if override != 0.0:
            target_accel = override
            target_accel = min(1, max(-1, target_accel))
            self.tags.acceleration = target_accel

        if is_reversing:
            self.controller.drive = True
            time.sleep(1 / 20)
            self.controller.drive = False
            time.sleep(1 / 20)

            self.controller.aforward = float(0.0001)
            self.controller.abackward = float(0.0001)

            self.state.text = "Detected reverse gear. Please shift to drive."
            return
        elif self.state.text == "Detected reverse gear. Please shift to drive.":
            self.state.text = ""

        if target_accel > 0:
            if (
                clutch < 0.1 or speed < 10 / 3.6
            ):  # ignore clutch when low speed (at traffic lights)
                self.controller.aforward = float(target_accel)
            else:  # disable acceleration if clutch is pressed
                self.controller.aforward = float(0)

            if self.speed > 10 / 3.6 and not self.set_zero:
                self.controller.abackward = float(0)
                self.set_zero = True
            elif not self.set_zero:
                self.controller.abackward = float(0.0001)
        else:
            self.set_zero = False
            self.controller.abackward = float(-target_accel)
            self.controller.aforward = float(0)

    def apply_pid(self, target_acceleration: float) -> float:
        """Apply PID control to get smooth accelerator/brake inputs based on target acceleration.

        :param float target_acceleration: Target acceleration in m/s^2
        :return float: Control output between -1.0 (full brake) and 1.0 (full throttle)
        """
        current_time = time.time()
        dt = current_time - self.last_time

        # Ensure dt is reasonable (first run or long gap between calls)
        if dt > 0.5 or dt <= 0:
            dt = self.pid_sample_time

        current_acceleration = self.acceleration.get()
        accel_error = target_acceleration - current_acceleration

        # Proportional term
        p_term = self.kp_accel * accel_error

        if accel_error * dt > 0:
            if (
                self.accel < 0.95
            ):  # Don't add more integral if already going full throttle
                self.accel_errors.append(accel_error * dt)
        else:
            if len(self.accel_errors) != 0 and self.accel_errors[0] > 0:
                self.accel_errors = self.accel_errors[1:]
            self.accel_errors.append(accel_error * dt)

        # Clear the integral term if we're speeding
        # (dynamically adjust the number to keep at the speedlimit)
        if self.speed > self.speedlimit and len(self.accel_errors) > 5:
            if sum(self.accel_errors) > 0:
                overshoot = round((self.speed - self.speedlimit) * 3.6)
                self.accel_errors = self.accel_errors[max(1, overshoot) * 2 :]

        # Clear the integral term if we're under 10 km/h
        # (to prevent overshooting when starting from a stop)
        if self.speed < 10 / 3.6:  # 10 kph -> m/s
            self.accel_errors = [0]

        # Integral term
        accel_error_sum = sum(self.accel_errors)
        i_term = self.ki_accel * accel_error_sum

        # Derivative term without filtering
        if dt > 0:
            d_term = self.kd_accel * (accel_error - self.last_accel_error) / dt
        else:
            d_term = 0

        # Raw control output calculation
        raw_control = p_term + i_term + d_term

        # Smoothing
        control_output = (
            1 - self.output_smoothing_factor
        ) * self.last_control_output + self.output_smoothing_factor * raw_control
        control_output = max(min(control_output, 1.0), -1.0)

        self.last_accel_error = accel_error
        self.last_control_output = control_output
        self.last_time = current_time

        # if variables.DEVELOPMENT_MODE:
        #     self.graph.update(target_acceleration, control_output, p_term, i_term, d_term)

        return control_output

    def update_manual_offset(self) -> None:
        if time.time() - self.last_change > 0.2:
            if self.holding_up:
                self.manual_speed_offset += 1
                self.last_change = time.time()
                self.notify(
                    "Speed offset increased to: "
                    + str(self.manual_speed_offset)
                    + (" km/h" if self.speed_offset_type == "Absolute" else " %")
                )
            elif self.holding_down:
                self.manual_speed_offset -= 1
                self.last_change = time.time()
                self.notify(
                    "Speed offset decreased to: "
                    + str(self.manual_speed_offset)
                    + (" km/h" if self.speed_offset_type == "Absolute" else " %")
                )

    def run(self):
        self.update_parameters()
        self.update_manual_offset()
        self.tags.status = {"AdaptiveCruiseControl": self.enabled}

        points = self.tags.steering_points
        points = self.tags.merge(points)
        self.map_points = points

        if not self.enabled:
            self.accel_errors = []
            self.tags.vehicle_highlights = []
            self.tags.vehicle_in_front_distance = None
            self.tags.AR = []
            self.reset()
            return

        self.api_data = self.api.run()

        if self.api_data["pause"]:
            self.reset()
            return

        if self.api_data["truckFloat"]["speedLimit"] == 0:
            self.api_data["truckFloat"]["speedLimit"] = self.overwrite_speed / 3.6

        self.speedlimit = self.get_target_speed(self.api_data)
        self.speed = self.api_data["truckFloat"]["speed"]

        acceleration_x = self.api_data["truckVector"]["accelerationX"]
        acceleration_y = self.api_data["truckVector"]["accelerationY"]
        acceleration_z = self.api_data["truckVector"]["accelerationZ"]

        total = math.sqrt(acceleration_x**2 + acceleration_y**2 + acceleration_z**2)
        if self.speed != self.last_speed:
            self.sign = 1 if self.speed > self.last_speed else -1
            self.last_speed = self.speed

        self.acceleration.smooth(total * self.sign)

        try:
            in_front = self.get_vehicle_in_front(self.api_data)
        except Exception:
            in_front = None

        if not in_front:
            self.tags.vehicle_in_front_distance = None
            self.tags.vehicle_highlights = []

        tl_mode = settings.traffic_light_mode

        if tl_mode == "Legacy":
            try:
                traffic_light = self.get_traffic_light_in_front(self.api_data)
            except Exception:
                traffic_light = None

        else:
            try:
                points, traffic_light = self.get_next_prefab_traffic_light(
                    self.api_data
                )

                truck_x = self.api_data["truckPlacement"]["coordinateX"]
                truck_z = self.api_data["truckPlacement"]["coordinateZ"]
                point = points[0] if points else None
                if point:
                    color = traffic_light.color()
                    vector = [point.x - truck_x, point.z - truck_z]
                    distance = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
                    unit_vector = (
                        [vector[0] / distance, vector[1] / distance]
                        if distance != 0
                        else [0, 0]
                    )

                    width = 2.5
                    height = 1

                    left_point = [
                        point.x + unit_vector[0] * width - unit_vector[1] * width / 2,
                        point.y,
                        point.z + unit_vector[1] * width + unit_vector[0] * width / 2,
                    ]
                    right_point = [
                        point.x + unit_vector[0] * width + unit_vector[1] * width / 2,
                        point.y,
                        point.z + unit_vector[1] * width - unit_vector[0] * width / 2,
                    ]
                    top_left = [left_point[0], left_point[1] + height, left_point[2]]
                    top_right = [
                        right_point[0],
                        right_point[1] + height,
                        right_point[2],
                    ]

                    self.tags.light = {
                        "distance": round(distance, 1),
                        "state": traffic_light.state_text(),
                    }
                    self.tags.AR = [
                        Polygon(
                            [
                                Coordinate(left_point[0], left_point[1], left_point[2]),
                                Coordinate(
                                    right_point[0], right_point[1], right_point[2]
                                ),
                                Coordinate(top_right[0], top_right[1], top_right[2]),
                                Coordinate(top_left[0], top_left[1], top_left[2]),
                            ],
                            closed=True,
                            color=Color(*color, 70),
                            fill=Color(*color, 30),
                            fade=Fade(0, 0, 999, 999),
                        )
                    ]

            except Exception:
                traffic_light = None
                traceback.print_exc()
                self.tags.light = {"distance": 0, "state": ""}
                self.tags.AR = []

        try:
            gate = self.get_gate_in_front(self.api_data)
        except Exception:
            logging.exception("Error in gate detection")
            gate = None

        stop_in_dict = self.tags.stop_in
        stop_in = 999
        if stop_in_dict:
            for value in stop_in_dict.values():
                if isinstance(value, (int, float)) and value > 0:
                    stop_in = min(stop_in, value)

        target_acceleration = self.calculate_target_acceleration(
            in_front, traffic_light, gate, stop_in
        )
        target_throttle = self.apply_pid(target_acceleration)
        self.set_accel_brake(target_throttle)

        self.tags.acc = self.speedlimit
        self.tags.acc_target = target_acceleration

        # self.state.text = "Integral length: " + str(len(self.accel_errors)) + "\nValue: " + str(round(sum(self.accel_errors), 2))

        return None
