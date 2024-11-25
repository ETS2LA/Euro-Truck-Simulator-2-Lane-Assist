from typing import List, Optional, Tuple, Union
import logging
from plugins.Map.classes import Node, Position, Road, Prefab
from plugins.Map.navigation.classes import NavigationLane
from plugins.Map.navigation.preprocessing import preprocess_item
from plugins.Map.navigation.node_pathfinding import NodePathfinder
from plugins.Map.utils.internal_map import DrawMap
from plugins.Map.navigation.visualization import visualize_route
from plugins.Map.navigation.classes import *
from plugins.Map.navigation.high_level_routing import HighLevelRouter

import plugins.Map.utils.prefab_helpers as prefab_helpers
import plugins.Map.utils.road_helpers as road_helpers
import plugins.Map.utils.math_helpers as math_helpers
import plugins.Map.data as data

import numpy as np
import time

last_item = None
last_position = None
last_destination_company = None
def get_destination_item() -> tuple[c.Prefab | RoadSection, c.Position]:
    """Get the destination item and position for navigation"""
    global last_destination_company, last_item, last_position

    try:
        if data.dest_company is None:
            logging.info("No destination company set")
            return None, None

        if data.dest_company == last_destination_company and last_item and last_position:
            logging.debug("Using cached destination")
            return last_item, last_position

        logging.info(f"Finding destination for company: {data.dest_company.token}")
        last_destination_company = data.dest_company

        dest_node = data.map.get_node_by_uid(data.dest_company.node_uid)
        if not dest_node:
            logging.error(f"Could not find node for company {data.dest_company.token}")
            return None, None

        position = c.Position(x=dest_node.x, y=dest_node.y, z=dest_node.z)

        closest_item = data.map.get_closest_item(position.x, position.y)
        if not closest_item:
            logging.error("Could not find closest item to destination")
            return None, None

        # Ensure the item is properly preprocessed before using it
        closest_item = preprocess_item(closest_item)
        if not closest_item:
            logging.error("Failed to preprocess destination item")
            return None, None

        last_item = closest_item
        last_position = position
        logging.info(f"Found destination item: {type(closest_item).__name__}")
        return closest_item, position
    except Exception as e:
        logging.error(f"Error finding destination: {e}", exc_info=True)
        return None, None

def get_start_item():
    """Get the starting item for navigation based on truck position"""
    try:
        logging.info(f"Finding start item at position ({data.truck_x}, {data.truck_z})")
        item = data.map.get_closest_item(data.truck_x, data.truck_z)
        if not item:
            logging.error("Could not find closest item to truck position")
            return None
        return preprocess_item(item)
    except Exception as e:
        logging.error(f"Error finding start item: {e}", exc_info=True)
        return None
    
def get_nav_lanes(item: c.Prefab | RoadSection, x: float, z: float) -> list[NavigationLane]:
    try:
        if not item:
            logging.error("Invalid input: item is None")
            return []

        if isinstance(item, c.Prefab):
            try:
                return [NavigationLane(
                    lane=lane,
                    item=item,
                    start=lane.points[0],
                    end=lane.points[-1],
                    length=lane.distance
                ) for lane in item.nav_routes]
                
                #closest_lane = prefab_helpers.get_closest_lane(
                #    item,
                #    x,
                #    z
                #)
#
                #return [NavigationLane(
                #    lane=item.nav_routes[closest_lane],
                #    item=item,
                #    start=item.nav_routes[closest_lane].points[0],
                #    end=item.nav_routes[closest_lane].points[-1],
                #    length=item.nav_routes[closest_lane].distance
                #)]
            except Exception as e:
                logging.error(f"Error processing prefab lanes: {e}")
                return []

        elif isinstance(item, c.Road):
            try:
                # Check if the start or end is in front of the truck
                forward_vector = [-math.sin(data.truck_rotation), -math.cos(data.truck_rotation)]
                if len(item.points) < 2:
                    logging.error(f"Road {item.uid} has less than 2 points")
                    return []
                point_forward_vector = [item.points[-1].x - data.truck_x, item.points[-1].z - data.truck_z]
                angle = np.arccos(np.dot(forward_vector, point_forward_vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(point_forward_vector)))
                end_angle = math.degrees(angle)

                point_forward_vector = [item.points[0].x - data.truck_x, item.points[0].z - data.truck_z]
                angle = np.arccos(np.dot(forward_vector, point_forward_vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(point_forward_vector)))
                start_angle = math.degrees(angle)

                # Get the closest lane id
                closest_lane = road_helpers.get_closest_lane(
                    item,
                    x,
                    z
                )

                side = item.lanes[closest_lane].side

                if abs(end_angle) < abs(start_angle):
                    # End is closer
                    return [NavigationLane(
                        lane=lane,
                        item=item,
                        start=lane.points[0],
                        end=item.points[-1],
                        length=lane.length
                    ) for lane in item.lanes if lane.side == side]

                else:
                    # Start is closer
                    return [NavigationLane(
                        lane=lane,
                        item=item,
                        start=lane.points[1],
                        end=item.points[0],
                        length=lane.length
                    ) for lane in item.lanes if lane.side == side]
            except Exception as e:
                logging.exception(f"Error processing road lanes: {e}")
                return []

        elif isinstance(item, RoadSection):
            try:
                # Check if the start or end is in front of the truck
                forward_vector = [-math.sin(data.truck_rotation), -math.cos(data.truck_rotation)]
                point_forward_vector = [item.end.x - data.truck_x, item.end.z - data.truck_z]
                angle = np.arccos(np.dot(forward_vector, point_forward_vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(point_forward_vector)))
                end_angle = math.degrees(angle)

                point_forward_vector = [item.start.x - data.truck_x, item.start.z - data.truck_z]
                angle = np.arccos(np.dot(forward_vector, point_forward_vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(point_forward_vector)))
                start_angle = math.degrees(angle)

                # Get the closest lane id
                closest_lane = road_helpers.get_closest_lane(
                    item,
                    x,
                    z
                )

                side = item.lanes[closest_lane].side

                if abs(end_angle) < abs(start_angle):
                    # End is closer
                    return [NavigationLane(
                        lane=lane,
                        item=item,
                        start=lane.points[0],
                        end=item.points[-1],
                        length=lane.length
                    ) for lane in item.lanes if lane.side == side]

                else:
                    # Start is closer
                    return [NavigationLane(
                        lane=lane,
                        item=item,
                        start=lane.points[1],
                        end=item.points[0],
                        length=lane.length
                    ) for lane in item.lanes if lane.side == side]
            except Exception as e:
                logging.error(f"Error processing road section lanes: {e}")
                return []
        else:
            logging.error(f"Unknown item type: {type(item)}")
            return []
    except Exception as e:
        logging.error(f"Critical error in get_nav_lanes: {e}", exc_info=True)
        return []

def heuristic(lane: NavigationLane, goal_lane: NavigationLane) -> float:
    """Estimates distance between current lane and goal"""
    try:
        if not lane or not goal_lane:
            logging.error("Invalid input: lane or goal_lane is None")
            return float('inf')

        if not hasattr(lane, 'end') or not hasattr(goal_lane, 'end'):
            logging.error("Invalid lane objects: missing 'end' attribute")
            return float('inf')

        return math_helpers.DistanceBetweenPoints(
            lane.end.tuple(),
            goal_lane.end.tuple()
        )
    except Exception as e:
        logging.error(f"Error calculating heuristic: {e}", exc_info=True)
        return float('inf')

def reconstruct_path(came_from: dict, current: NavigationLane) -> list[NavigationLane]:
    """Reconstructs the path from the came_from dict"""
    try:
        if current is None:
            logging.error("Invalid input: current is None")
            return []
        if not came_from:
            #logging.error("Invalid input: came_from is empty")
            return [current]

        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)

        logging.debug(f"Reconstructed path with {len(path)} segments")
        return path[::-1]
    except Exception as e:
        logging.error(f"Error reconstructing path: {e}", exc_info=True)
        return []

def find_path(start_lanes: list[NavigationLane], goal_lane: NavigationLane, old_path: list = []) -> list[NavigationLane]:
    """A* pathfinding implementation with multiple starting lanes"""
    try:
        if not isinstance(start_lanes, list) or not start_lanes:
            logging.error("Invalid start_lanes: must be non-empty list")
            return None

        if not isinstance(goal_lane, NavigationLane):
            logging.error("Invalid goal_lane: must be NavigationLane")
            return None

        logging.info(f"Finding path from {len(start_lanes)} starting lanes to {goal_lane}")

        open_set = set(start_lanes)
        print(f"Open set: {open_set}")
        came_from = {}

        g_score = {lane: 0 for lane in start_lanes}
        f_score = {lane: heuristic(lane, goal_lane) for lane in start_lanes}

        iteration = 0
        max_iterations = 1000
        while open_set and iteration < max_iterations:
            try:
                current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
                logging.info(f"Iteration {iteration}: Current lane {current}")

                current_path = reconstruct_path(came_from, current)
                data.navigation_points = []
                for item in current_path:
                    data.navigation_points.extend([point for point in item.lane.points])

                if data.internal_map:
                    DrawMap()

                visualize_route(goal_lane.item, current.item, old_path + current_path)

                if (current.item.uid == goal_lane.item.uid and math_helpers.DistanceBetweenPoints(current.end.tuple(), goal_lane.end.tuple()) < 0.1):
                    if len(old_path) > 0:
                        if (math_helpers.DistanceBetweenPoints(current.start.tuple(xz=True), old_path[-1].end.tuple(xz=True)) < 0.1):
                            logging.info("Found path!")
                            return reconstruct_path(came_from, current), old_path + current_path
                        else:
                            print("Failed to connect paths", math_helpers.DistanceBetweenPoints(current.start.tuple(xz=True), old_path[-1].end.tuple(xz=True)))
                    else:
                        logging.info("Found path!")
                        return reconstruct_path(came_from, current), old_path + current_path

                open_set.remove(current)

                # Check neighbors
                next_lanes = current.next_lanes or []
                logging.debug(f"Found {len(next_lanes)} next lanes")

                for neighbor in next_lanes:
                    try:
                        tentative_g_score = g_score[current] + neighbor.length

                        if tentative_g_score < g_score.get(neighbor, float('inf')):
                            came_from[neighbor] = current
                            print(f"Neighbor: {neighbor}")
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal_lane)
                            open_set.add(neighbor)
                    except Exception as e:
                        logging.error(f"Error processing neighbor: {e}")
                        continue

                iteration += 1
            except Exception as e:
                logging.exception(f"Error in pathfinding iteration {iteration}: {e}")
                break

        if iteration >= max_iterations:
            logging.warning("Path finding exceeded maximum iterations")
        else:
            logging.warning("No path found!")
        return None, None
    except Exception as e:
        logging.error(f"Critical error in path finding: {e}", exc_info=True)
        return None, None

def get_path_to_destination():
    """Find a path from current position to destination"""
    try:
        # Get destination information
        dest_item, dest_position = get_destination_item()
        if not dest_item or not dest_position:
            logging.info("No valid destination found")
            return None

        # Get start information
        start_item = get_start_item()
        if not start_item:
            logging.error("Could not find valid start item near truck position")
            return None

        if not start_item:
            logging.error("Start item failed preprocessing")
            return None

        # No need to preprocess dest_item again as it's already done in get_destination_item
        if not dest_item:
            logging.error("Destination item invalid")
            return None

        # Get node UIDs based on item type
        try:
            start_node_uid = start_item.roads[0].start_node_uid if isinstance(start_item, RoadSection) else start_item.uid
            end_node_uid = dest_item.roads[0].start_node_uid if isinstance(dest_item, RoadSection) else dest_item.uid

            start_node = data.map.get_node_by_uid(start_node_uid)
            end_node = data.map.get_node_by_uid(end_node_uid)

            if not start_node or not end_node:
                logging.error(f"Could not find {'start' if not start_node else 'end'} node")
                return None
        except AttributeError as e:
            logging.error(f"Missing required node attributes: {e}")
            return None

        # Initialize pathfinder and find path
        routing_mode = getattr(data.plugin.settings, 'RoutingMode', 'shortest')
        logging.info(f"Finding path from {start_node.uid} to {end_node.uid} using {routing_mode} mode")
        pathfinder = NodePathfinder()
        complete_path = pathfinder.find_path_between_nodes(start_node, end_node, mode=routing_mode)

        if not complete_path:
            logging.warning("No path found")
            return None

        logging.info(f"Found complete path with {len(complete_path)} segments")

        # Update navigation points
        data.navigation_points = []
        for item in complete_path:
            data.navigation_points.extend([point for point in item.lane.points])

        # Update visualization
        try:
            if data.internal_map:
                logging.debug("Drawing route on internal map...")
                DrawMap()

            logging.debug("Visualizing route...")
            visualize_route(dest_item, start_item, complete_path)
        except Exception as e:
            logging.error(f"Error in visualization: {e}", exc_info=True)

        return complete_path

    except Exception as e:
        logging.error(f"Error in path finding: {e}", exc_info=True)
        return None
