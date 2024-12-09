import plugins.Map.utils.math_helpers as math_helpers
import plugins.Map.utils.prefab_helpers as ph
import plugins.Map.utils.road_helpers as rh
import plugins.Map.route.classes as rc
import plugins.Map.data as data
import plugins.Map.classes as c
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
        
def PrefabToRouteSection(prefab: c.Prefab, lane_index: int, invert: bool = False) -> rc.RouteSection:
    route_section = rc.RouteSection()
    route_item = rc.RouteItem()
    route_item.item = prefab
    route_item.lane_index = lane_index
    route_section.items = [route_item]
    route_section.invert = invert
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

def RoadToRouteSection(road: c.Road, lane_index: int, invert: bool = False) -> rc.RouteSection:
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
    
    route_section.invert = invert
    if (lane_index > len(route_section.items[0].lane_points)):
        return None
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
        
def GetCurrentNavigationPlan():
    path: list[c.Node] = data.navigation_plan
    distance_ordered = sorted(path, key=lambda node: math_helpers.DistanceBetweenPoints((node.x, node.y), (data.truck_x, data.truck_z)))

    closest = distance_ordered[0]
    index = path.index(closest)
    lower_bound = max(0, index-1)   
    upper_bound = min(len(path), index+1)
    closest: list[c.Node] = path[lower_bound:upper_bound]

    in_front = [math_helpers.IsInFront((node.x, node.y), data.truck_rotation, (data.truck_x, data.truck_z)) for node in closest]
    try:
        last = closest[in_front.index(False)]
        next = closest[in_front.index(True)]
    except:
        back_item = data.map.get_item_by_uid(closest[0].backward_item_uid)
        forward_item = data.map.get_item_by_uid(closest[0].forward_item_uid)
        items = [back_item, forward_item]
        closest_item = None
        closest_lane = None
        closest_distance = math.inf
        
        for item in items:
            if type(item) == c.Road:
                closest_lane, distance = rh.get_closest_lane(item, data.truck_x, data.truck_z, return_distance=True)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_lane = closest_lane
                    closest_item = item
                    
            if type(item) == c.Prefab:
                closest_lanes = GetClosestLanesForPrefab(item, c.Position(data.truck_x, data.truck_y, data.truck_z))
                if len(closest_lanes) == 0:
                    return None
                closest_lane = closest_lanes[0]
                closest_point_distance = math.inf
                
                for point in item.nav_routes[closest_lane].points:
                    distance = math_helpers.DistanceBetweenPoints((data.truck_x, data.truck_z), point.tuple())
                    if distance < closest_point_distance:
                        closest_point_distance = distance
                        
                if closest_point_distance < closest_distance:
                    closest_distance = closest_point_distance
                    closest_item = item
                    closest_lane = closest_lane
                    
        if closest_item is None:
            return None
        
        if type(closest_item) == c.Road:
            # Check for inverting
            start_node = data.map.get_node_by_uid(closest_item.start_node_uid)
            end_node = data.map.get_node_by_uid(closest_item.end_node_uid)
            start_distance = math_helpers.DistanceBetweenPoints((start_node.x, start_node.y), (data.truck_x, data.truck_z))
            end_distance = math_helpers.DistanceBetweenPoints((end_node.x, end_node.y), (data.truck_x, data.truck_z))
            invert = start_distance > end_distance
            return RoadToRouteSection(closest_item, closest_lane, invert=invert)
        
        if type(closest_item) == c.Prefab:
            # TODO: Fix this inverting check
            start_node = data.map.get_node_by_uid(closest_item.node_uids[0])
            end_node = data.map.get_node_by_uid(closest_item.node_uids[-1])
            start_distance = math_helpers.DistanceBetweenPoints((start_node.x, start_node.y), (data.truck_x, data.truck_z))
            end_distance = math_helpers.DistanceBetweenPoints((end_node.x, end_node.y), (data.truck_x, data.truck_z))
            invert = start_distance > end_distance
            return PrefabToRouteSection(closest_item, closest_lane, invert=invert)
    

    # find the item that connects both of the nodes
    if last.forward_item_uid == next.backward_item_uid:
        next_item = data.map.get_item_by_uid(last.forward_item_uid)
    elif last.backward_item_uid == next.forward_item_uid:
        next_item = data.map.get_item_by_uid(last.backward_item_uid)
    else:
        print("No connection between nodes")
        return None
        
    # get the closest lane on that item
    if type(next_item) == c.Road:
        closest_lane = rh.get_closest_lane(next_item, data.truck_x, data.truck_z)
        return RoadToRouteSection(next_item, closest_lane)
    
    if type(next_item) == c.Prefab:
        closest_lanes = GetClosestLanesForPrefab(next_item, c.Position(data.truck_x, data.truck_y, data.truck_z))
        
        if len(closest_lanes) == 0:
            return None
        
        closest_lane = closest_lanes[0]
        return PrefabToRouteSection(next_item, closest_lane)
        
def GetNextNavigationItem():
    last_item = data.route_plan[-1]
    last_points = last_item.lane_points
    
    start_in_front = math_helpers.IsInFront((last_points[0].x, last_points[0].z), data.truck_rotation, (data.truck_x, data.truck_z))
    end_in_front = math_helpers.IsInFront((last_points[-1].x, last_points[-1].z), data.truck_rotation, (data.truck_x, data.truck_z))
    
    if start_in_front and not end_in_front:
        last_points = last_points[::-1]
        
    if start_in_front and end_in_front:
        start_distance = math_helpers.DistanceBetweenPoints((last_points[0].x, last_points[0].z), (data.truck_x, data.truck_z))
        end_distance = math_helpers.DistanceBetweenPoints((last_points[-1].x, last_points[-1].z), (data.truck_x, data.truck_z))
        if end_distance < start_distance:
            last_points = last_points[::-1]
    
    path = data.navigation_plan
    distance_ordered = sorted(path, key=lambda node: math_helpers.DistanceBetweenPoints((node.x, node.y), (last_points[-1].x, last_points[-1].z)))
    
    closest = distance_ordered[0]
    index = path.index(closest)
    
    try:
        next = path[index + 1]
    except:
        return None
    
    dir = "forward"
    if closest.forward_item_uid == next.backward_item_uid:
        next_item = data.map.get_item_by_uid(closest.forward_item_uid)
    elif closest.backward_item_uid == next.forward_item_uid:
        dir = "backward"
        next_item = data.map.get_item_by_uid(closest.backward_item_uid)
    elif closest.backward_item_uid == next.backward_item_uid:
        next_item = data.map.get_item_by_uid(closest.backward_item_uid)
    elif closest.forward_item_uid == next.forward_item_uid:
        next_item = data.map.get_item_by_uid(closest.forward_item_uid)
    else:
        print(f"No connection between nodes {closest.uid} and {next.uid}")
        print(f"Forward: {closest.forward_item_uid} {next.backward_item_uid}")
        print(f"Backward: {closest.backward_item_uid} {next.forward_item_uid}")
        return None
        
    if type(next_item) == c.Road:
        closest_lane = rh.get_closest_lane(next_item, last_points[-1].x, last_points[-1].z)
        return RoadToRouteSection(next_item, closest_lane)
    
    if type(next_item) == c.Prefab:
        closest_lanes = GetClosestLanesForPrefab(next_item, c.Position(last_points[-1].x, last_points[-1].y, last_points[-1].z))
        
        if len(closest_lanes) == 0:
            return None
        
        next_next = path[index + 2]
        
        best_lane = math.inf
        best_distance = math.inf
        for lane in closest_lanes:
            points = next_item.nav_routes[lane].points
            distance = math_helpers.DistanceBetweenPoints((points[-1].x, points[-1].z), (next_next.x, next_next.y))
            if distance < best_distance:
                best_distance = distance
                best_lane = lane
                
        if best_lane == math.inf:
            return None
        
        return PrefabToRouteSection(next_item, best_lane)
    
        
was_indicating = False
def UpdateRoutePlan():
    global was_indicating
    if not data.enabled:
        data.route_plan = []
        
    if len(data.route_plan) > 0:
        #for i, section in enumerate(data.route_plan):
        #    print(i, section)
        #print(data.route_plan[-1])
        ...
    
    if not data.use_navigation or len(data.navigation_plan) == 0: # No navigation plan / use only route planner
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
            
    else: # We have a navigation plan that we can drive on.
        if len(data.route_plan) == 0:
            data.route_plan.append(GetCurrentNavigationPlan())
            # TODO: Check if off the path (distance > 10)
            
        if data.route_plan[0] is None:
            data.route_plan = []
            return
        
        if data.route_plan[0].is_ended:
            data.route_plan.pop(0)
            
        if len(data.route_plan) == 0:
            return
            
        if len(data.route_plan) < data.route_plan_length:
            try:
                next_route_section = GetNextNavigationItem()
            except:
                logging.exception("Failed to get next navigation item")
                next_route_section = None
            if next_route_section is not None:
                data.route_plan.append(next_route_section)