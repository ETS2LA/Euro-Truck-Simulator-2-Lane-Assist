import plugins.Map.utils.math_helpers as math_helpers
import plugins.Map.data as data
import plugins.Map.classes as c
import plugins.Map.route.classes as rc
import logging
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
        
def PrefabToRouteSection(prefab: c.Prefab, lane_index: int) -> rc.RouteSection:
    route_section = rc.RouteSection()
    route_item = rc.RouteItem()
    route_item.item = prefab
    route_item.lane_index = lane_index
    route_section.items = [route_item]
    route_section.lane_index = lane_index
    points = route_section.lane_points
    if len(points) == 0:
        return None
    nodes = [data.map.get_node_by_uid(node_uid) for node_uid in prefab.node_uids]
    closest_to_start = min(nodes, key=lambda n: math_helpers.DistanceBetweenPoints((n.x, n.y), (points[0].x, points[0].z)))
    closest_to_end = min(nodes, key=lambda n: math_helpers.DistanceBetweenPoints((n.x, n.y), (points[-1].x, points[-1].z)))
    route_section._start_node = closest_to_start
    route_section._end_node = closest_to_end
    return route_section

def RoadToRouteSection(road: c.Road, lane_index: int) -> rc.RouteSection:
    route_section = rc.RouteSection()
    route_section.items = []
    
    n = data.map.get_node_by_uid
    behind_roads = sorted(GetRoadsBehindRoad(road, include_self=False), \
        key=lambda r: math_helpers.DistanceBetweenPoints((n(r.start_node_uid).x, n(r.start_node_uid).y), \
                                                         (data.truck_x, data.truck_z)))
    
    forward_roads = sorted(GetRoadsInFrontOfRoad(road, include_self=False), \
        key=lambda r: math_helpers.DistanceBetweenPoints((n(r.start_node_uid).x, n(r.start_node_uid).y), \
                                                         (data.truck_x, data.truck_z)))
    
    roads = behind_roads[::-1] + [road] + forward_roads
    for list_road in roads:
        route_item = rc.RouteItem()
        route_item.item = list_road
        route_item.lane_index = lane_index
        route_section.items.append(route_item)
    
    route_section.lane_index = lane_index
    return route_section
                
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

    if closest_item == None:
        return None
    
    return PrefabToRouteSection(closest_item, closest_lane_id) if type(closest_item) == c.Prefab \
                                              else RoadToRouteSection(closest_item, closest_lane_id)
        
def GetClosestLanesForPrefab(next_item: c.Prefab, end_point: c.Position) -> list[int]:
    closest_lane_ids = []
    closest_point_distance = math.inf
    for lane_id, lane in enumerate(next_item.nav_routes):
        distance = math_helpers.DistanceBetweenPoints((end_point.x, end_point.y, end_point.z), lane.points[0].tuple())
        if distance == closest_point_distance:
            closest_lane_ids.append(lane_id)
        elif distance < closest_point_distance:
            closest_lane_ids = [lane_id]
            closest_point_distance = distance
    
    accepted_lane_ids = []      
    for closest_lane_id in closest_lane_ids:
        points = next_item.nav_routes[closest_lane_id].points
        start_node = None
        start_node_distance = math.inf
        for node in [data.map.get_node_by_uid(node_uid) for node_uid in next_item.node_uids]:
            distance = math_helpers.DistanceBetweenPoints((points[0].x, points[0].z), (node.x, node.y))
            if distance < start_node_distance:
                start_node_distance = distance
                start_node = node
        end_node = None
        end_node_distance = math.inf
        for node in [data.map.get_node_by_uid(node_uid) for node_uid in next_item.node_uids]:
            distance = math_helpers.DistanceBetweenPoints((points[-1].x, points[-1].z), (node.x, node.y))
            if distance < end_node_distance:
                end_node_distance = distance
                end_node = node
                
        if start_node != end_node:
            accepted_lane_ids.append(closest_lane_id)
            
    closest_lane_ids = accepted_lane_ids
    
    return closest_lane_ids
        
def IsRoadValid(road: c.Road) -> bool:
    if road.hidden:
        return False
    
    if road.lanes == []:
        return False
    
    if "traffic_lane.no_vehicles" in road.road_look.lanes_left or "traffic_lane.no_vehicles" in road.road_look.lanes_right:
        return False
    
    return True
        
def GetNextRouteSection(route: list[rc.RouteSection] = []) -> rc.RouteSection:
    if len(route) == 0:
        route = data.route_plan
        
    if len(route) == 0:
        return None # No route sections found
    
    current_section = route[-1]

    if type(current_section.items[0].item) == c.Road:
        end_node = current_section.end_node
        start_node = current_section.start_node
        end_node_is_in_front = math_helpers.IsInFront((end_node.x, end_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
        start_node_is_in_front = math_helpers.IsInFront((start_node.x, start_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
        
        next_item = None
        if end_node_is_in_front and start_node_is_in_front:
            return None # We don't need to plan a new route section
        elif end_node_is_in_front:
            next_item = data.map.get_item_by_uid(end_node.forward_item_uid)
        elif start_node_is_in_front:
            next_item = data.map.get_item_by_uid(start_node.backward_item_uid)
            
        if next_item is None:
            return None # No next item found
        
        if type(next_item) == c.Prefab:
            if current_section.last_actual_points == []:
                current_section.get_points()
            points = current_section.last_actual_points
            if len(points) == 0:
                return None
            
            closest_lane_ids = GetClosestLanesForPrefab(next_item, points[-1])
                    
            if len(closest_lane_ids) == 0:
                return None
            elif len(closest_lane_ids) == 1:
                return PrefabToRouteSection(next_item, closest_lane_ids[0])
            
            # Verify that the next road piece is not hidden (not drivable in game)
            candidate_sections = [PrefabToRouteSection(next_item, lane_id) for lane_id in closest_lane_ids]
            for section in candidate_sections: section.get_points()
            next_roads = [GetNextRouteSection(route + [section]) for section in candidate_sections]
            
            verified_lane_ids = []
            for i, section in enumerate(next_roads):
                if section is not None:
                    if type(section.items[0].item) != c.Prefab and not IsRoadValid(section.items[0].item):
                        continue
                    if type(section.items[0].item) == c.Prefab:
                        section.get_points()
                        next_section = GetNextRouteSection(route + [section])
                        if type(next_section.items[0].item) == c.Road:
                            if not IsRoadValid(next_section.items[0].item):
                                continue

                    verified_lane_ids.append(closest_lane_ids[i])
                    
            if len(verified_lane_ids) == 0:
                return None
            
            closest_lane_ids = verified_lane_ids
            
            # Get the lane that is most in the direction of the truck
            end_positions = [next_item.nav_routes[lane_id].points[-1].tuple() for lane_id in closest_lane_ids]
            direction = "left" if data.truck_indicating_left else "right" if data.truck_indicating_right else "straight"
            best_lane = math_helpers.GetMostInDirection(end_positions, data.truck_rotation, (data.truck_x, data.truck_y, data.truck_z), direction=direction)
            
            target_end_position = end_positions[best_lane]
            best_lane = 0
            shortest_distance = math.inf
            for i, position in enumerate(end_positions):
                if position == target_end_position:
                    distance = next_item.nav_routes[closest_lane_ids[i]].distance
                    if distance < shortest_distance:
                        best_lane = closest_lane_ids[i]
                        shortest_distance = distance
                    
            return PrefabToRouteSection(next_item, best_lane)
     
    if type(current_section.items[0].item) == c.Prefab:
        end_node = current_section.end_node
        start_node = current_section.start_node
        
        end_node_is_in_front = math_helpers.IsInFront((end_node.x, end_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
        start_node_is_in_front = math_helpers.IsInFront((start_node.x, start_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
        
        if end_node_is_in_front and start_node_is_in_front:
            distance_to_start = math_helpers.DistanceBetweenPoints((start_node.x, start_node.y), (data.truck_x, data.truck_z))
            distance_to_end = math_helpers.DistanceBetweenPoints((end_node.x, end_node.y), (data.truck_x, data.truck_z))
            if distance_to_start < distance_to_end:
                start_node_is_in_front = False
            else:
                end_node_is_in_front = False

        node = end_node if end_node_is_in_front else start_node
        next_item = None
        
        forward_item = data.map.get_item_by_uid(node.forward_item_uid)
        backward_item = data.map.get_item_by_uid(node.backward_item_uid)
        if forward_item.uid != current_section.items[-1].item.uid and forward_item.uid != current_section.items[0].item.uid:
            next_item = forward_item
        elif backward_item.uid != current_section.items[0].item.uid and backward_item.uid != current_section.items[-1].item.uid:
            next_item = backward_item
        else:
            return None
            
        if next_item is None:
            return None
        
        if current_section.last_actual_points == []:
            return None # should not happen
        
        end_point = current_section.last_actual_points[-1]
        if type(next_item) == c.Road:
            closest_lane_id = 0
            closest_point_distance = math.inf
            for lane_id, lane in enumerate(next_item.lanes):
                distance = math_helpers.DistanceBetweenPoints((end_point.x, end_point.y, end_point.z), lane.points[0].tuple())
                end_distance = math_helpers.DistanceBetweenPoints((end_point.x, end_point.y, end_point.z), lane.points[-1].tuple())
                distance = min(distance, end_distance)
                if distance < closest_point_distance:
                    closest_lane_id = lane_id
                    closest_point_distance = distance
                    
            return RoadToRouteSection(next_item, closest_lane_id)
        
        if type(next_item) == c.Prefab:
            if current_section.last_actual_points == []:
                current_section.get_points()
            points = current_section.last_actual_points
            if len(points) == 0:
                return None
            
            closest_lane_ids = GetClosestLanesForPrefab(next_item, end_point)
                    
            if len(closest_lane_ids) == 0:
                return None
            elif len(closest_lane_ids) == 1:
                return PrefabToRouteSection(next_item, closest_lane_ids[0])
            
            end_positions = [next_item.nav_routes[lane_id].points[-1].tuple() for lane_id in closest_lane_ids]
            direction = "left" if data.truck_indicating_left else "right" if data.truck_indicating_right else "straight"
            best_lane = math_helpers.GetMostInDirection(end_positions, data.truck_rotation, (data.truck_x, data.truck_y, data.truck_z), direction=direction)
            
            target_end_position = end_positions[best_lane]
            best_lane = 0
            shortest_distance = math.inf
            for i, position in enumerate(end_positions):
                if position == target_end_position:
                    distance = next_item.nav_routes[closest_lane_ids[i]].distance
                    if distance < shortest_distance:
                        best_lane = closest_lane_ids[i]
                        shortest_distance = distance
                    
            return PrefabToRouteSection(next_item, best_lane)
        
was_indicating = False
def UpdateRoutePlan():
    global was_indicating
    
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
        try:
            next_route_section = GetNextRouteSection()
        except:
            logging.exception("Failed to get next route section")
            next_route_section = None
        if next_route_section is not None:
            data.route_plan.append(next_route_section)
            
    if (data.truck_indicating_left or data.truck_indicating_right) and not was_indicating:
        if len(data.route_plan) > 1:
            data.route_plan = [data.route_plan[0]]
        was_indicating = True
    elif not (data.truck_indicating_left or data.truck_indicating_right) and was_indicating:
        if len(data.route_plan) > 1:
            data.route_plan = [data.route_plan[0]]
        was_indicating = False