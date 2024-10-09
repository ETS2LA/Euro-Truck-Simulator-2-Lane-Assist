import utils.math_helpers as math_helpers
import ETS2LA.plugins.MapNew.classes as c
import route.classes as rc
import data
import math

def GetRoadsBehindRoad(road: c.Road, include_self:bool = True) -> list[c.Road]:
    if include_self: roads = [road]
    else: roads = []
    node = data.map.get_node_by_uid(road.start_node_uid)
    if node is not None:
        if node.backward_item_uid != road.uid:
            item = data.map.get_item_by_uid(node.backward_item_uid)
            if type(item) == c.Road:
                if len(item.lanes) == len(road.lanes):
                    roads += GetRoadsBehindRoad(item)
                    
    return roads

def GetRoadsInFrontOfRoad(road: c.Road, include_self:bool = True) -> list[c.Road]:
    if include_self: roads = [road]
    else: roads = []
    node = data.map.get_node_by_uid(road.end_node_uid)
    if node is not None:
        if node.forward_item_uid != road.uid:
            item = data.map.get_item_by_uid(node.forward_item_uid)
            if type(item) == c.Road:
                if len(item.lanes) == len(road.lanes):
                    roads += GetRoadsInFrontOfRoad(item)
                    
    return roads
                

def GetClosestRouteSection() -> rc.RouteSection:
    in_bounding_box = []
    items: list[c.Prefab | c.Road] = []
    items += data.current_sector_prefabs
    items += data.current_sector_roads
    for item in items:
        if item.bounding_box.is_in(c.Position(data.truck_x, data.truck_y, data.truck_z)):
            in_bounding_box.append(item)
            
    closest_lane_id = 0
    closest_item = None
    closest_point_distance = math.inf
    for item in in_bounding_box:
        if type(item) == c.Prefab:
            for lane_id, lane in enumerate(item.nav_routes):
                for point in lane.points:
                    point_tuple = point.tuple()
                    point_tuple = (point_tuple[0], point_tuple[2])
                    distance = math_helpers.DistanceBetweenPoints((data.truck_x, data.truck_z), point_tuple)
                    if distance < closest_point_distance:
                        closest_point_distance = distance
                        closest_item = item
                        closest_lane_id = lane_id
                        
        elif type(item) == c.Road:
            for lane_id, lane in enumerate(item.lanes):
                for point in lane.points:
                    point_tuple = point.tuple()
                    point_tuple = (point_tuple[0], point_tuple[2])
                    distance = math_helpers.DistanceBetweenPoints((data.truck_x, data.truck_z), point_tuple)
                    if distance < closest_point_distance:
                        closest_point_distance = distance
                        closest_item = item
                        closest_lane_id = lane_id

    if type(closest_item) == c.Prefab:
        route_section = rc.RouteSection()
        route_item = rc.RouteItem()
        route_item.item = closest_item
        route_item.lane_index = closest_lane_id
        route_section.items = [route_item]
        route_section.lane_index = closest_lane_id
        return route_section
    
    elif type(closest_item) == c.Road:
        route_section = rc.RouteSection()
        route_section.items = []
        roads = GetRoadsBehindRoad(closest_item, include_self=False)[::-1] + GetRoadsInFrontOfRoad(closest_item)
        for road in roads:
            route_item = rc.RouteItem()
            route_item.item = road
            route_item.lane_index = closest_lane_id
            route_section.items.append(route_item)
        route_section.lane_index = closest_lane_id
        return route_section
        
def UpdateRoutePlan():
    if not data.enabled:
        data.route_plan = []
    
    if len(data.route_plan) == 0:
        data.route_plan.append(GetClosestRouteSection())
        
    if data.route_plan[0] is None:
        data.route_plan = []
        return # No route sections found
        
    if data.route_plan[0].is_ended:
        data.route_plan.pop(0)
    
    if len(data.route_plan) < data.route_plan_length:
        ... # Plan more route sections