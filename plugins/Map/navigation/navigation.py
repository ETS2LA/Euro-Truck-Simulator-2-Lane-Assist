import plugins.Map.classes as c
import plugins.Map.data as data

from plugins.Map.utils.internal_map import DrawMap
from plugins.Map.navigation.visualization import visualize_route
from plugins.Map.navigation.classes import *

import plugins.Map.utils.prefab_helpers as prefab_helpers
import plugins.Map.utils.road_helpers as road_helpers

import numpy as np
import time

last_item = None
last_position = None
last_destination_company = None
def get_destination_item() -> tuple[c.Prefab | RoadSection, c.Position]:
    global last_destination_company, last_item, last_position
    
    if data.dest_company is None:
        return None, None
    if data.dest_company == last_destination_company:
        return last_item, last_position
    
    last_destination_company = data.dest_company
    dest_node = data.map.get_node_by_uid(
        data.dest_company.node_uid
    )
    
    # TODO: Use the actual points instead of the node
    # (this is close enough though)
    position = c.Position(
        x=dest_node.x,
        y=dest_node.y,
        z=dest_node.z
    )
    
    closest_item = data.map.get_closest_item(
        position.x,
        position.y
    )
    
    closest_item = preprocess_item(closest_item)
    last_item = closest_item
    last_position = position
    return closest_item, position

def get_start_item():
    item = data.map.get_closest_item(
        data.truck_x,
        data.truck_z
    )
    return preprocess_item(item)
    
def get_nav_lanes(item: c.Prefab | RoadSection, x: float, z: float) -> list[NavigationLane]:
    if isinstance(item, c.Prefab):
        closest_lane = prefab_helpers.get_closest_lane(
            item,
            x,
            z
        )
        
        return [NavigationLane(
            lane=item.nav_routes[closest_lane],
            item=item,
            start=item.nav_routes[closest_lane].points[0],
            end=item.nav_routes[closest_lane].points[-1],
            length=item.nav_routes[closest_lane].distance
        )]
        
    elif isinstance(item, RoadSection):
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

def heuristic(lane: NavigationLane, goal_lane: NavigationLane) -> float:
    """Estimates distance between current lane and goal"""
    return math_helpers.DistanceBetweenPoints(
        lane.end.tuple(),
        goal_lane.start.tuple()
    )

def reconstruct_path(came_from: dict, current: NavigationLane) -> list[NavigationLane]:
    """Reconstructs the path from the came_from dict"""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

def find_path(start_lanes: list[NavigationLane], goal_lane: NavigationLane) -> list[NavigationLane]:
    """A* pathfinding implementation with multiple starting lanes"""
    print(f"Finding path from {len(start_lanes)} starting lanes to {goal_lane}")
    
    open_set = set(start_lanes)
    came_from = {}
    
    g_score = {lane: 0 for lane in start_lanes}
    f_score = {lane: heuristic(lane, goal_lane) for lane in start_lanes}
    
    iteration = 0
    while open_set:
        current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
        
        print(f"\nIteration {iteration}: Current lane {current}")
        
        current_path = reconstruct_path(came_from, current)
        data.navigation_points = []
        for item in current_path:
            data.navigation_points.extend([point for point in item.lane.points])
        
        if data.internal_map:
            DrawMap()
            
        visualize_route(goal_lane.item, start_lanes[0].item, current_path)
        
        if (current.item.uid == goal_lane.item.uid and 
            math_helpers.DistanceBetweenPoints(current.end.tuple(), goal_lane.end.tuple()) < 0.1):
            print("Found path!")
            return reconstruct_path(came_from, current)
            
        open_set.remove(current)
        
        # Check neighbors
        next_lanes = current.next_lanes or []
        print(f"- Found {len(next_lanes)} next lanes")
        for neighbor in next_lanes:
            tentative_g_score = g_score[current] + neighbor.length
            
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal_lane)
                open_set.add(neighbor)
                
    print("No path found!")
    return None

def get_path_to_destination():
    dest_item, dest_position = get_destination_item()
    if not dest_item or not dest_position:
        print("No destination found")
        return
        
    dest_lane = get_nav_lanes(dest_item, dest_position.x, dest_position.z)[0]  # Take first lane for destination, eventually try and find the closest available lane
    
    start_item = get_start_item()
    start_lanes = get_nav_lanes(start_item, data.truck_x, data.truck_z)
    
    path = find_path(start_lanes, dest_lane)
    if path:
        print(f"Found path with {len(path)} segments")
    
    time.sleep(2)
    
    if data.internal_map:
        DrawMap()
    visualize_route(dest_item, start_item, path)