from Plugins.Map import classes as c
from typing import List, TypeVar
import time

T = TypeVar('T')

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


def rotate_left(arr: List[T], count: int) -> List[T]:
    """Rotate an array to the left by a specified count.

    :param List[T] arr: The array to rotate.
    :param int count: The number of positions to rotate the array to the left.
    :return List[T]: The rotated array.
    """
    assert 0 <= count < len(arr), "count must be within the range of the array length"
    if count == 0:
        return arr
    return arr[count:] + arr[:count]

def rotate_right(arr: List[T], count: int) -> List[T]:
    """Rotate an array to the right by a specified count.

    :param List[T] arr: The array to rotate.
    :param int count: The number of positions to rotate the array to the right.
    :return List[T]: The rotated array.
    """
    assert 0 <= count < len(arr), "count must be within the range of the array length"
    if count == 0:
        return arr
    return arr[-count:] + arr[:-count]

def get_connecting_lanes_by_item(node_1, node_2, item, map_data) -> list[int]:
    """Get the connecting lanes between two nodes based on the item type.

    :param c.Node node_1: The starting node.
    :param c.Node node_2: The ending node.
    :param Item item: The Item instance.
    :param MapData map_data: A mapdata instance to use.
    :return list[int]: The list of connecting lane ids.
    """
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
        rotated_nodes = rotate_right( # match the nodes to the nodes in the prefab description
            item_nodes, item.origin_node_index
        )
        try:
            node_1_index = [i for i, n in enumerate(rotated_nodes) if n.uid == node_1.uid][0]
            start_prefab_node = description.nodes[node_1_index]
            node_2_index = [i for i, n in enumerate(rotated_nodes) if n.uid == node_2.uid][0]
            end_prefab_node = description.nodes[node_2_index]
        except:
            return []
        
        if node_1_index == node_2_index:
            return []
        
        routes = description.nav_routes
            
        accepted_routes = []
        for i, route in enumerate(routes):
            start_found = False
            end_found = False
            for curve in route.curves:
                index = description.nav_curves.index(curve)

                if index in start_prefab_node.input_lanes:
                    start_found = True
                if index in end_prefab_node.output_lanes and start_found:
                    end_found = True
                    break
            
            if start_found and end_found:
                accepted_routes.append(i)
     
        return accepted_routes
    else:
        return []
    
def get_nav_node_for_entry_and_node(entry, node):
    """Get a navigation node for a node in a given entry.

    :param c.NavigationEntry entry: The navigation entry to use.
    :param c.Node node: The node to look for.
    :return c.NavigationNode nav_node: The navigation node for the given node.
    """
    possibilities = []
    if isinstance(entry, c.NavigationEntry):
        for nav_node in entry.forward:
            if nav_node.node_id == node.uid:
                possibilities.append(nav_node)
        for nav_node in entry.backward:
            if nav_node.node_id == node.uid:
                possibilities.append(nav_node)
    else:
        raise ValueError("entry must be a NavigationEntry instance")
    
    return possibilities
