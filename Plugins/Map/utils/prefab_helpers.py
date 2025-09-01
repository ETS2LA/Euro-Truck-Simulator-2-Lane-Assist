"""Prefab helper utilities for map plugin."""

from Plugins.Map.utils import math_helpers
from collections import defaultdict
import Plugins.Map.classes as c
from typing import List, Set
import numpy as np
import math
import cv2


def find_starting_curves(prefab_description) -> list:
    """Find all starting nav curves in a prefab description."""
    assert isinstance(prefab_description, c.PrefabDescription)

    starting_curves = []
    for curve in prefab_description.nav_curves:
        if curve.prev_lines == []:
            starting_curves.append(curve)
    return starting_curves


def traverse_curve_till_end(curve, prefab_description) -> List[List]:
    """Traverse nav curves until reaching end points."""
    assert isinstance(prefab_description, c.PrefabDescription)
    assert isinstance(curve, c.PrefabNavCurve)

    routes: List[List[c.PrefabNavCurve]] = []

    def traverse(
        curve: c.PrefabNavCurve,
        route: List[c.PrefabNavCurve],
        depth: int,
        visited: Set[int],
    ):
        # Check if the current curve is already in the route (cycle detected)
        id = prefab_description.nav_curves.index(curve)
        if id in visited:
            return

        route.append(curve)
        visited.add(id)

        if not curve.next_lines:
            routes.append(route[:])
            return

        if depth > 100:
            return

        for next_curve_id in curve.next_lines:
            next_curve = prefab_description.nav_curves[next_curve_id]
            traverse(next_curve, route[:], depth + 1, visited.copy())

    # Initialize traversal
    traverse(curve, [], 0, set())

    routes_by_start_curve = defaultdict(list)
    routes_by_end_curve = defaultdict(list)
    route_lengths = {}

    for route in routes:
        route_tuple = tuple(route)
        start_curve = route[0]
        end_curve = route[-1]
        routes_by_start_curve[start_curve].append(route_tuple)
        routes_by_end_curve[end_curve].append(route_tuple)
        route_lengths[route_tuple] = len(route)

    # Only accept the shortest route from each start curve to each end curve
    accepted_routes = []
    for start_curve, start_routes in routes_by_start_curve.items():
        for end_curve, end_routes in routes_by_end_curve.items():
            common_routes = set(start_routes) & set(end_routes)
            accepted_routes.extend(common_routes)
            # if common_routes:
            #     shortest_route = min(common_routes, key=lambda route: route_lengths[route])
            #     accepted_routes.append(list(shortest_route))

    return accepted_routes


def display_prefab_routes(prefab_description) -> None:
    """Display navigation routes for a prefab."""
    assert isinstance(prefab_description, c.PrefabDescription)
    cv2.namedWindow("Nav Routes", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Nav Routes", 1000, 1000)
    img = np.zeros((1000, 1000, 3), np.uint8)
    min_x = math.inf
    max_x = -math.inf
    min_y = math.inf
    max_y = -math.inf

    for route in prefab_description.nav_routes:
        for curve in route.curves:
            for point in curve.points:
                if point.x < min_x:
                    min_x = point.x
                if point.x > max_x:
                    max_x = point.x
                if point.y < min_y:
                    min_y = point.z
                if point.y > max_y:
                    max_y = point.z

    min_x -= 10
    max_x += 10
    min_y -= 10
    max_y += 10

    scaling_factor = 6
    offset_x = 500
    offset_y = 500

    for route in prefab_description.nav_routes:
        for curve in route.curves:
            poly_points = np.array(
                [
                    [
                        int((point.x * scaling_factor + offset_x)),
                        int((point.z * scaling_factor + offset_y)),
                    ]
                    for point in curve.points
                ],
                np.int32,
            )
            cv2.polylines(
                img, [poly_points], isClosed=False, color=(255, 255, 255), thickness=1
            )

    cv2.imshow("Nav Routes", img)
    cv2.resizeWindow("Nav Routes", 1000, 1000)
    cv2.waitKey(0)


def get_closest_lane(item, x: float, z: float, return_distance=False) -> int:
    closest_point_distance = math.inf
    closest_lane_id = -1
    for lane_id, lane in enumerate(item.nav_routes):
        for point in lane.points:
            point_tuple = point.tuple()
            point_tuple = (point_tuple[0], point_tuple[2])
            distance = math_helpers.DistanceBetweenPoints((x, z), point_tuple)
            if distance < closest_point_distance:
                closest_point_distance = distance
                closest_lane_id = lane_id

    if return_distance:
        return closest_lane_id, closest_point_distance

    return closest_lane_id


def get_closest_lanes_from_indices(
    item, x: float, z: float, lane_indices: List[int]
) -> List[int]:
    closest_point_distance = math.inf
    closest_lane_ids = []
    for lane_id in lane_indices:
        lane = item.nav_routes[lane_id]
        for point in lane.points:
            point_tuple = point.tuple()
            point_tuple = (point_tuple[0], point_tuple[2])
            distance = math_helpers.DistanceBetweenPoints((x, z), point_tuple)
            if distance < closest_point_distance:
                closest_point_distance = distance
                closest_lane_ids = [lane_id]
            elif (
                distance < closest_point_distance + 0.01
                and distance > closest_point_distance - 0.01
            ):
                closest_lane_ids.append(lane_id)

    return closest_lane_ids


def get_closest_lane_from_indices(
    item, x: float, z: float, lane_indices: List[int]
) -> int:
    closest_point_distance = math.inf
    closest_length = math.inf
    closest_lane_id = -1
    for lane_id in lane_indices:
        lane = item.nav_routes[lane_id]
        length = lane.distance
        for point in lane.points:
            point_tuple = point.tuple()
            point_tuple = (point_tuple[0], point_tuple[2])
            distance = math_helpers.DistanceBetweenPoints((x, z), point_tuple)
            if distance < closest_point_distance - 0.1 or (
                distance < closest_point_distance + 0.1 and length < closest_length
            ):  # offset to prefer shorter paths
                closest_length = length
                closest_point_distance = distance
                closest_lane_id = lane_id

    return closest_lane_id


def convert_point_to_relative(point, origin_node, map_origin):
    prefab_start_x = origin_node.x - map_origin.x
    prefab_start_y = origin_node.z - map_origin.z
    prefab_start_z = origin_node.y - map_origin.y

    rot = float(origin_node.rotation - map_origin.rotation)

    new_point_pos = math_helpers.RotateAroundPoint(
        point.x + prefab_start_x,
        point.z + prefab_start_z,
        rot,
        origin_node.x,
        origin_node.y,
    )
    return c.Transform(
        new_point_pos[0],
        point.y + prefab_start_y,
        new_point_pos[1],
        point.rotation + rot,
    )
