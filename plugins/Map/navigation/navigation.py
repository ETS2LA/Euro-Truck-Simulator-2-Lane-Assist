import plugins.Map.classes as c
import plugins.Map.data as data

from plugins.Map.navigation.visualization import visualize_route
from plugins.Map.navigation.classes import *

last_destination_company = None
last_item = None
def get_destination_item():
    global last_destination_company, last_item
    
    if data.dest_company is None:
        return None
    if data.dest_company == last_destination_company:
        return last_item
    
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
    return closest_item

def get_start_item():
    return data.map.get_closest_item(
        data.truck_x,
        data.truck_z
    )
    
def get_start_nav_lane():
    # Get closest lane to the point.
    ...

def get_path_to_destination():
    dest_item = get_destination_item()
    start_item = get_start_item()
    visualize_route(dest_item, start_item, [])