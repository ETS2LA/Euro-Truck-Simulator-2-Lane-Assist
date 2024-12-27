from Plugins.Map.utils import prefab_helpers
from Plugins.Map.utils import math_helpers
import ETS2LA.variables as variables
from Plugins.Map import classes as c
import numpy as np
import logging
import math

def get_connecting_item_uid(node_1, node_2) -> int:
    """Will return the connecting item between two nodes, or None if they are not connected.

    :param c.Node node_1: The first node.
    :param c.Node node_2: The second node.
    
    :return: The UID of the connecting item.
    """
    node_1_forward_item = node_1.forward_item_uid
    node_1_backward_item = node_1.backward_item_uid
    node_2_forward_item = node_2.forward_item_uid
    node_2_backward_item = node_2.backward_item_uid
    
    if node_1_forward_item == node_2_backward_item:
        return node_1_forward_item
    elif node_1_backward_item == node_2_forward_item:
        return node_1_backward_item
    elif node_1_forward_item == node_2_forward_item:
        return node_1_forward_item
    elif node_1_backward_item == node_2_backward_item:
        return node_1_backward_item
    
    return None

def get_connecting_lanes_by_item(node_1, node_2, item, map_data) -> list[int]:
    if type(item) == c.Road:
        left_lanes = len(item.road_look.lanes_left)
        right_lanes = len(item.road_look.lanes_right)
        start_node = item.start_node_uid
        if start_node == node_1.uid:
            return [i for i in range(left_lanes, left_lanes + right_lanes)]
        else:
            if left_lanes > 0:
                return [i for i in range(0, left_lanes)]
            else:
                return [i for i in range(0, right_lanes)]
            
    elif type(item) == c.Prefab:
        description = item.prefab_description
        item_nodes = [map_data.get_node_by_uid(uid) for uid in item.node_uids]
        starting_curves = prefab_helpers.find_starting_curves(description)
        routes = []
        for curve in starting_curves:
            curve_routes = prefab_helpers.traverse_curve_till_end(curve, description)
            for route in curve_routes:
                routes.append(route)
        
        possible_routes = []
        for route in routes:
            start = route[0].start
            end = route[-1].end
            
            start = prefab_helpers.convert_point_to_relative(start, 
                                                             map_data.get_node_by_uid(item.node_uids[0]), 
                                                             description.nodes[item.origin_node_index])
            end = prefab_helpers.convert_point_to_relative(end,
                                                           map_data.get_node_by_uid(item.node_uids[0]),
                                                           description.nodes[item.origin_node_index])
            
            closest_start = 0
            distance = math.inf
            for node in item_nodes:
                node_distance = math_helpers.DistanceBetweenPoints([start.x, start.z], [node.x, node.y])
                if node_distance < distance:
                    distance = node_distance
                    closest_start = node.uid
            
            closest_end = 0
            distance = math.inf
            for node in item_nodes:
                node_distance = math_helpers.DistanceBetweenPoints([end.x, end.z], [node.x, node.y])
                if node_distance < distance:
                    distance = node_distance
                    closest_end = node.uid
            
            if closest_start == node_1.uid and closest_end == node_2.uid:
                possible_routes.append(route)
            elif closest_start == node_2.uid and closest_end == node_1.uid:
                possible_routes.append(route)
            elif closest_start == node_1.uid and closest_end == node_1.uid:
                possible_routes.append(route)
            elif closest_start == node_2.uid and closest_end == node_2.uid:
                possible_routes.append(route)
                
        possible_routes = [routes.index(route) for route in possible_routes]

        return possible_routes
    else:
        return []