# TODO: Fix this file, it's still using the old steering system!
import Plugins.Map.utils.math_helpers as math_helpers
import Plugins.Map.route.classes as rc
import Plugins.Map.classes as c
import Plugins.Map.data as data
import numpy as np
import logging
import math

OFFSET_MULTIPLIER = 1.5
ANGLE_MULTIPLIER = 1


def get_closest_route_item(items: list[rc.RouteItem]):
    in_bounding_box = []
    for item in items:
        item = item.item

        if item.bounding_box.is_in(
            c.Position(data.truck_x, data.truck_z, data.truck_y)
        ):
            in_bounding_box.append(item)

    closest_item = None
    closest_point_distance = math.inf
    for item in in_bounding_box:
        if isinstance(item, c.Prefab):
            for _lane_id, lane in enumerate(item.nav_routes):
                for point in lane.points:
                    point_tuple = point.tuple()
                    point_tuple = (point_tuple[0], point_tuple[2])
                    distance = math_helpers.DistanceBetweenPoints(
                        (data.truck_x, data.truck_z), point_tuple
                    )
                    if distance < closest_point_distance:
                        closest_point_distance = distance
                        closest_item = item

        elif isinstance(item, c.Road):
            for _lane_id, lane in enumerate(item.lanes):
                for point in lane.points:
                    point_tuple = point.tuple()
                    point_tuple = (point_tuple[0], point_tuple[2])
                    distance = math_helpers.DistanceBetweenPoints(
                        (data.truck_x, data.truck_z), point_tuple
                    )
                    if distance < closest_point_distance:
                        closest_point_distance = distance
                        closest_item = item

    return closest_item


was_indicating = False


def CheckForLaneChange():
    global was_indicating
    if isinstance(data.route_plan[0].items[0].item, c.Prefab):
        was_indicating = False
        return

    current_index = data.route_plan[0].lane_index
    lanes = data.route_plan[0].items[0].item.lanes
    side = lanes[current_index].side
    left_lanes = len([lane for lane in lanes if lane.side == "left"])
    # lanes = left_lanes + right_lanes

    if (
        data.truck_indicating_right or data.truck_indicating_left
    ) and not was_indicating:
        was_indicating = True
        current_index = data.route_plan[0].lane_index
        side = lanes[current_index].side

        target_index = current_index
        change = 1 if data.truck_indicating_right else -1

        closest_item = get_closest_route_item(data.route_plan[0].items)
        end_node_in_front = math_helpers.IsInFront(
            (closest_item.end_node.x, closest_item.end_node.y),
            data.truck_rotation,
            (data.truck_x, data.truck_z),
        )

        if side == "left":
            if end_node_in_front:  # Normal lane change
                target_index += change
                if change == 1 and target_index >= left_lanes:
                    target_index = left_lanes - 1
            else:  # Inverted lane change
                target_index -= change
                if change == -1 and target_index >= left_lanes:
                    target_index = left_lanes - 1
        else:
            if end_node_in_front:
                target_index += change
                if change == -1 and target_index < left_lanes:
                    target_index = left_lanes
            else:
                target_index -= change
                if change == 1 and target_index < left_lanes:
                    target_index = left_lanes

        if target_index < 0:
            target_index = 0
        if target_index >= len(lanes):
            target_index = len(lanes) - 1

        data.route_plan[0].lane_index = target_index
        data.route_plan = [data.route_plan[0]]

    elif not data.truck_indicating_left and not data.truck_indicating_right:
        was_indicating = False


def GetPointDistance(points_so_far: int, total_points: int = 50) -> float:
    key_points = [
        (0, 0.25),
        (total_points / 5, 2),
        (total_points / 5 * 2, 4),
        (total_points / 5 * 3, 8),
        (total_points / 5 * 4, 16),
        (total_points, 16),
    ]

    # Find the segment where points_so_far lies
    for i in range(len(key_points) - 1):
        if key_points[i][0] <= points_so_far < key_points[i + 1][0]:
            x0, y0 = key_points[i]
            x1, y1 = key_points[i + 1]
            # Linear interpolation formula
            distance = y0 + (y1 - y0) * (points_so_far - x0) / (x1 - x0)
            return distance

    # If points_so_far is exactly at the last key point
    return key_points[-1][1]


def LerpTrailerAndTruck(start_speed=30, end_speed=70) -> list[float]:
    trailer_pos = [data.trailer_x, data.trailer_y, data.trailer_z]
    truck_pos = [data.truck_x, data.truck_y, data.truck_z]

    if data.truck_speed * 3.6 < start_speed:
        percentage = 0.5
        return [
            trailer_pos[0] + (truck_pos[0] - trailer_pos[0]) * percentage,
            trailer_pos[1] + (truck_pos[1] - trailer_pos[1]) * percentage,
            trailer_pos[2] + (truck_pos[2] - trailer_pos[2]) * percentage,
        ]

    if data.truck_speed * 3.6 > end_speed:
        return truck_pos

    percentage = (data.truck_speed * 3.6 - start_speed) / (end_speed - start_speed)
    percentage = max(min(percentage, 1), 0.5)
    return [
        trailer_pos[0] + (truck_pos[0] - trailer_pos[0]) * percentage,
        trailer_pos[1] + (truck_pos[1] - trailer_pos[1]) * percentage,
        trailer_pos[2] + (truck_pos[2] - trailer_pos[2]) * percentage,
    ]


def GetSteering():
    if len(data.route_plan) == 0:
        return 0

    if not data.use_navigation or len(data.navigation_plan) == 0:
        CheckForLaneChange()

        # Fix issue: Default steering to 0 when passing a Prefab and navigation is not calculated
        if isinstance(data.route_plan[0].items[0].item, c.Prefab):
            # logging.warning("Navigation not calculated, defaulting steering to 0.")
            return 0

    points = []
    for section in data.route_plan:
        if len(points) > data.amount_of_points:
            break

        if section is None:
            continue

        section_points = section.get_points()
        for point in section_points:
            if len(points) > data.amount_of_points:
                break

            if len(points) == 0:
                points.append(point)
                continue

            distance = math_helpers.DistanceBetweenPoints(
                point.tuple(), points[-1].tuple()
            )
            if distance >= GetPointDistance(len(points), data.amount_of_points):
                if distance <= 20:
                    if point not in points:
                        points.append(point)

    if len(points) == 0:
        data.route_points = []
        # if data.use_navigation and len(data.navigation_plan) != 0:
        #     data.frames_off_path += 1
        #     if data.frames_off_path > 5:
        #         #logging.warning("Recalculating navigation plan as we have no points to drive on.")
        #         data.route_plan = []
        #         data.update_navigation_plan = True
        #         data.frames_off_path = 0
        #         return 0
        return 0

    points = points
    speed = max(data.truck_speed * 3.6, 10)  # Convert to kph
    speed = min(speed, 80)
    # Multiplier is 8 at 10kph and 2 at 80kph
    multiplier = max(8 - (speed - 10) / 10, 2)

    data.route_points = points

    forward_vector = [-math.sin(data.truck_rotation), -math.cos(data.truck_rotation)]
    try:
        if len(points) > 2:
            points = points[:5]

            x = 0
            z = 0
            for i in range(1, len(points)):
                x += points[i].x
                z += points[i].z
            x /= 4
            z /= 4

            point_forward_vector = [
                points[len(points) - 1].x - points[0].x,
                points[len(points) - 1].z - points[0].z,
            ]

            if np.cross(forward_vector, point_forward_vector) < 0:
                isLeft = True
            else:
                isLeft = False

            centerline = [points[-1].x - points[0].x, points[-1].z - points[0].z]
            if data.trailer_attached:
                coords = LerpTrailerAndTruck()
                truck_position_vector = [
                    coords[0] - points[0].x,
                    coords[2] - points[0].z,
                ]
            else:
                truck_position_vector = [
                    data.truck_x - points[0].x,
                    data.truck_z - points[0].z,
                ]

            lateral_offset = np.cross(
                truck_position_vector, centerline
            ) / np.linalg.norm(centerline)
            # data.plugin.globals.tags.lateral_offset = lateral_offset

            # Calculate the dot product and the norms
            dot_product = np.dot(forward_vector, centerline)
            norm_forward = np.linalg.norm(forward_vector)
            norm_centerline = np.linalg.norm(centerline)

            # Calculate the cosine of the angle
            cos_angle = dot_product / (norm_forward * norm_centerline)

            # Clamp the value to the valid range [-1, 1] to avoid numerical inaccuracies
            cos_angle = np.clip(cos_angle, -1.0, 1.0)

            # Calculate the angle
            angle = np.arccos(cos_angle)
            angle = math.degrees(angle)

            if np.cross(forward_vector, centerline) < 0:
                angle = -angle

            if angle > 140:
                angle = 0
            if angle < -140:
                angle = 0

            angle = angle * ANGLE_MULTIPLIER

            offset_correction = lateral_offset * 5
            offset_correction = offset_correction
            if isLeft:
                angle += offset_correction * OFFSET_MULTIPLIER
            else:
                angle += offset_correction * OFFSET_MULTIPLIER

            return angle * multiplier
        elif len(points) == 2:
            x = points[len(points) - 1].x
            z = points[len(points) - 1].z

            if data.trailer_attached:
                coords = LerpTrailerAndTruck()
                vector = [x - coords[0], z - coords[2]]
            else:
                vector = [x - data.truck_x, z - data.truck_z]

            angle = np.arccos(
                np.dot(forward_vector, vector)
                / (np.linalg.norm(forward_vector) * np.linalg.norm(vector))
            )
            angle = math.degrees(angle)

            if np.cross(forward_vector, vector) < 0:
                angle = -angle

            return angle * 2 * multiplier
        else:
            return 0
    except Exception:
        logging.exception("Error in GetSteering")
        return 0
