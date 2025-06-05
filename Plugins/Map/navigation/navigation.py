import Plugins.Map.utils.prefab_helpers as ph
import Plugins.Map.navigation.classes as nc
import Plugins.Map.utils.node_helpers as nh
import Plugins.Map.utils.road_helpers as rh
import Plugins.Map.classes as c
import Plugins.Map.data as data
from typing import Literal
import importlib
import logging
import time
import sys

nc = importlib.reload(nc)
data.last_length = 0

sys.setrecursionlimit(10**6) # Increase recursion limit

def get_direction_for_route_start(route: list[nc.RouteNode]):
    last, next = nh.get_surrounding_nav_nodes(route, data.truck_x, data.truck_z, data.truck_rotation)
    if last is None or next is None:
        logging.warning("Failed to find surrounding nodes (do you have a destination set? try driving yourself a bit?)")
        return "", 0
    
    last_entry = data.map.get_node_navigation(last.uid)
    nav_nodes = nh.get_nav_node_for_entry_and_node(last_entry, next)
    
    if len(nav_nodes) == 0:
        logging.warning("Failed to find navigation nodes")
        return "", 0
    
    direction = ""
    item = data.map.get_item_by_uid(nav_nodes[0].item_uid)
    if type(item) == c.Road:
        closest_lane = rh.get_closest_lane(item, data.truck_x, data.truck_z)
        for node in nav_nodes:
            if closest_lane in node.lane_indices:
                direction = node.direction
                break
    elif type(item) == c.Prefab:
        prefab = ph.get_closest_lane(item, data.truck_x, data.truck_z)
        for node in nav_nodes:
            if prefab in node.lane_indices:
                direction = node.direction
                break
            
    if direction == "":
        logging.warning("Failed to find direction")
        return "", 0
    
    # 左行时反转初始方向（关键修改）
    if data.left_hand_drive:
        direction = "backward" if direction == "forward" else "forward"
    
    index = 0
    for item in route:
        if item.node.uid == last.uid:
            break
        index += 1
    
    return direction, index

# Recursive function to traverse
def traverse_route_for_direction(remaining: list[nc.RouteNode], direction: Literal["forward", "backward"]):
    if len(remaining) == 2:
        return [direction]
    
    current = remaining[0]
    next_node = remaining[1]
    
    cur_entry = data.map.get_node_navigation(current.node.uid)
    
    if cur_entry is None:
        logging.warning(f"Missing navigation entry for node {current.node.uid}")
        return []
    
    # 左行时使用反向连接（关键修改）
    if data.left_hand_drive:
        in_direction = cur_entry.backward if direction == "forward" else cur_entry.forward
    else:
        in_direction = cur_entry.forward if direction == "forward" else cur_entry.backward
    
    for node in in_direction:
        if node.node_id == next_node.node.uid:
            so_far = traverse_route_for_direction(remaining[1:], node.direction)
            if so_far == []: return []
            return [direction] + so_far 
        
    so_far = traverse_route_for_direction(remaining[1:], direction)
    if so_far == []: return []
    return [direction] + so_far

def get_directions_until_route_end(route: list[nc.RouteNode], start_direction: Literal["forward", "backward", ""]):
    direction = [start_direction] + traverse_route_for_direction(route, start_direction)
    return direction

def get_path_to_destination():
    """Find a path from current position to destination"""
    game_route = data.plugin.modules.Route.run()
    
    if not game_route or len(game_route) == 0:
        return []
    
    if len(game_route) != data.last_length:
        route = []
        for item in game_route:
            route.append(nc.RouteNode(item))
            if route[-1].node is None:
                route.pop()
                
        if len(route) == 0:
            logging.warning("Failed to find route")
            return []
                
        start_direction, index = get_direction_for_route_start(route)
        if start_direction == "":
            logging.warning("Failed to find direction for route start.")
            return []
        
        route = route[index:]
        directions = get_directions_until_route_end(route, start_direction)
        if len(directions) != len(route):
            logging.warning("Failed to find direction for route, do you have ferries on your route?")
            return []
            
        # 左行时反转车道索引（关键修改）
        for i in range(1, len(route)):
            try:
                # 传递反转后的方向参数，计算反向车道
                adjusted_direction = directions[-i+1]
                if data.left_hand_drive:
                    adjusted_direction = "backward" if adjusted_direction == "forward" else "forward"
                route[-i].calculate_lanes_from(route[-i+1], adjusted_direction)
            except Exception:
                pass

        success = [node.is_possible for node in route]
        logging.warning(f"Successfully calculated lanes for {sum(success)} out of {len(success)} nodes ({sum(success) / len(success) * 100:.0f}%)")
        data.navigation_plan = route
        nodes = [nav.node for nav in route]
        data.plugin.globals.tags.navigation_plan = nodes
        data.last_length = len(game_route)
        
    return data.navigation_plan
