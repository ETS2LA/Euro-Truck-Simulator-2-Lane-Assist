"""Prefab helper utilities for map plugin."""
from plugins.Map.utils import math_helpers
from collections import defaultdict
from typing import List, Tuple
import numpy as np
import math
import cv2

def find_starting_curves(prefab_description) -> list:
    """Find all starting nav curves in a prefab description."""
    from plugins.Map.classes import PrefabDescription, PrefabNavCurve
    assert isinstance(prefab_description, PrefabDescription)
    starting_curves = []
    for curve in prefab_description.nav_curves:
        if curve.prev_lines == []:
            starting_curves.append(curve)
    return starting_curves

def traverse_curve_till_end(curve, prefab_description) -> List[List]:
    """Traverse nav curves until reaching end points."""
    from plugins.Map.classes import PrefabDescription, PrefabNavCurve
    assert isinstance(prefab_description, PrefabDescription)
    assert isinstance(curve, PrefabNavCurve)
    routes: List[List[PrefabNavCurve]] = []

    def traverse(curve: PrefabNavCurve, route: List[PrefabNavCurve], depth: int):
        route.append(curve)
        if not curve.next_lines:
            routes.append(route[:])
            return

        if depth > 100:
            return

        for next_curve in curve.next_lines:
            next_curve = prefab_description.nav_curves[next_curve]
            traverse(next_curve, route[:], depth + 1)

    traverse(curve, [], 0)

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
    for start_curve in routes_by_start_curve:
        for end_curve in routes_by_end_curve:
            shortest_route = None
            shortest_route_length = math.inf
            for route in routes_by_start_curve[start_curve]:
                if route in routes_by_end_curve[end_curve] and route_lengths[route] < shortest_route_length:
                    shortest_route = route
                    shortest_route_length = route_lengths[route]
            if shortest_route is not None:
                accepted_routes.append(list(shortest_route))

    return accepted_routes

def display_prefab_routes(prefab_description) -> None:
    """Display navigation routes for a prefab."""
    from plugins.Map.classes import PrefabDescription
    assert isinstance(prefab_description, PrefabDescription)
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
            poly_points = np.array([[int((point.x*scaling_factor + offset_x)), int((point.z*scaling_factor + offset_y))] for point in curve.points], np.int32)
            cv2.polylines(img, [poly_points], isClosed=False, color=(255, 255, 255), thickness=1)

    cv2.imshow("Nav Routes", img)
    cv2.resizeWindow("Nav Routes", 1000, 1000)
    cv2.waitKey(0)
    
def get_closest_lane(item, x: float, z: float) -> int:
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
        
    return closest_lane_id
