import plugins.Map.classes as c
import plugins.Map.data as data

from plugins.Map.navigation.visualization import visualize_route
from plugins.Map.navigation.classes import *

import plugins.Map.utils.prefab_helpers as prefab_helpers
import plugins.Map.utils.road_helpers as road_helpers

last_item = None
last_position = None
last_destination_company = None
def get_destination_item() -> tuple[c.Prefab | c.Road, c.Position]:
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
    position = c.Position(
        x=dest_node.x,
        y=dest_node.y,
        z=dest_node.z
    )
    
    closest_item = data.map.get_closest_item(
        position.x,
        position.y
    )
    
    last_item = closest_item
    last_position = position
    return closest_item, position

def get_start_item():
    return data.map.get_closest_item(
        data.truck_x,
        data.truck_z
    )
    
def get_nav_lane(item: c.Prefab | c.Road, x: float, z: float) -> NavigationLane:
    if type(item) == c.Prefab:
        closest_lane = prefab_helpers.get_closest_lane(
            item,
            x,
            z
        )
        return NavigationLane(
            lane=item.nav_routes[closest_lane],
            item=item,
            start=item.nav_routes[closest_lane].points[0],
            end=item.nav_routes[closest_lane].points[-1],
            length=item.nav_routes[closest_lane].distance
        )
        
    elif type(item) == c.Road:
        closest_lane = road_helpers.get_closest_lane(
            item,
            x,
            z
        )
        return NavigationLane(
            lane=item.lanes[closest_lane],
            item=item,
            start=item.lanes[closest_lane].points[0],
            end=item.lanes[closest_lane].points[-1],
            length=item.lanes[closest_lane].length
        )

def get_path_to_destination():
    dest_item, dest_position = get_destination_item()
    dest_lane = get_nav_lane(dest_item, dest_position.x, dest_position.z)
    
    start_item = get_start_item()
    start_lane = get_nav_lane(start_item, data.truck_x, data.truck_z)
    
    print(f"{start_lane.start_node.uid} -> {start_lane.end_node.uid} - distance: {start_lane.length}")
    
    visualize_route(dest_item, start_item, [])