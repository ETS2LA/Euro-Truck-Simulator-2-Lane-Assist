import Plugins.Map.utils.math_helpers as math_helpers
import Plugins.Map.utils.prefab_helpers as ph
import Plugins.Map.utils.road_helpers as rh
import Plugins.Map.utils.node_helpers as nh
import ETS2LA.Handlers.sounds as sounds
import Plugins.Map.route.classes as rc
import Plugins.Map.data as data
import Plugins.Map.classes as c
import logging
import math
import time

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
    if (lane_index > len(route_section.items[0].item.lanes) - 1):
        return None
    route_section.lane_index = lane_index
    return route_section
                
def GetClosestRouteSection() -> rc.RouteSection:
    items: list[c.Prefab | c.Road] = []
    items += data.current_sector_prefabs
    items += data.current_sector_roads

    closest_item, closest_lane_id = get_closest_route_item(items)
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
        
        if forward_item is None or backward_item is None:
            return None
        
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
                road_closest_lane, distance = rh.get_closest_lane(item, data.truck_x, data.truck_z, return_distance=True)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_lane = road_closest_lane
                    closest_item = item
                    
            if type(item) == c.Prefab:
                closest_lanes = GetClosestLanesForPrefab(item, c.Position(data.truck_x, data.truck_y, data.truck_z))
                if len(closest_lanes) == 0:
                    return None
                prefab_closest_lane = closest_lanes[0]
                closest_point_distance = math.inf
                
                for point in item.nav_routes[prefab_closest_lane].points:
                    distance = math_helpers.DistanceBetweenPoints((data.truck_x, data.truck_y, data.truck_z), point.tuple())
                    if distance < closest_point_distance:
                        closest_point_distance = distance
                        
                if closest_point_distance < closest_distance:
                    closest_distance = closest_point_distance
                    closest_item = item
                    closest_lane = prefab_closest_lane
                    
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
    elif last.backward_item_uid == next.backward_item_uid:
        next_item = data.map.get_item_by_uid(last.backward_item_uid)
    elif last.forward_item_uid == next.forward_item_uid:
        next_item = data.map.get_item_by_uid(last.forward_item_uid)
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
    end_node = last_item.end_node
    start_node = last_item.start_node
    
    start_in_front = math_helpers.IsInFront((start_node.x, start_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
    end_in_front = math_helpers.IsInFront((end_node.x, end_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
    
    selected_node = None
    
    if start_in_front and not end_in_front:
        selected_node = start_node
        last_points = last_points[::-1]
    elif end_in_front and not start_in_front:
        selected_node = end_node
        
    if start_in_front and end_in_front:
        return None
    
    path = data.navigation_plan
    try: index = path.index(selected_node)
    except:
        #logging.warning("Failed to find selected node in path")
        return None
    
    try: next = path[index + 1]
    except:
        logging.warning("Failed to get next node in path (probably because the navigation has ended)")
        return None
    
    closest = path[index]
    
    if closest.forward_item_uid == next.backward_item_uid:
        next_item = data.map.get_item_by_uid(closest.forward_item_uid)
    elif closest.backward_item_uid == next.forward_item_uid:
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
    
def UpdateNavigatedLanes():
    if len(data.route_plan) == 0:
        return
    
    lookahead = 6 # how many nodes ahead should we plan.
    
    if len(data.route_plan) == 2:
        last_item = data.route_plan[0]
    else:
        last_item = data.route_plan[-1]
    last_points = last_item.lane_points
    end_node = last_item.end_node
    start_node = last_item.start_node
    
    start_in_front = math_helpers.IsInFront((start_node.x, start_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
    end_in_front = math_helpers.IsInFront((end_node.x, end_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
    
    selected_node = None
    
    if start_in_front and not end_in_front:
        selected_node = start_node
        last_points = last_points[::-1]
    elif end_in_front and not start_in_front:
        selected_node = end_node
        
    if start_in_front and end_in_front:
        return None
    
    path = data.navigation_plan
    try: 
        index = path.index(selected_node)
    except:
        #logging.warning("Failed to find selected node in path")
        return None
    
    end_index = min(index + lookahead, len(path))
    selected_path = path[index:end_index]
    selected_items = []
    for i in range(len(selected_path) - 1):
        node = selected_path[i]
        next_node = selected_path[i + 1]
        if node.forward_item_uid == next_node.backward_item_uid:
            selected_items.append(data.map.get_item_by_uid(node.forward_item_uid))
        elif node.backward_item_uid == next_node.forward_item_uid:
            selected_items.append(data.map.get_item_by_uid(node.backward_item_uid))
        elif node.backward_item_uid == next_node.backward_item_uid:
            selected_items.append(data.map.get_item_by_uid(node.backward_item_uid))
        elif node.forward_item_uid == next_node.forward_item_uid:
            selected_items.append(data.map.get_item_by_uid(node.forward_item_uid))
        else:
            #logging.warning("No connection between nodes")
            return None
        
    last_type = type(last_item.items[-1].item)
    route = []
    for i, node in enumerate(selected_path):
        if i == len(selected_path) - 1:
            continue
        # Roads get combined into one route section, there's no reason
        # to give them as separate items.
        if last_type == c.Road and type(selected_items[i]) == c.Road:
            last_type = type(selected_items[i])
            continue
        last_type = type(selected_items[i])
        
        navigation = data.map.get_node_navigation(node.uid)
        if navigation is None:
            logging.warning(f"Navigation is none for node: {node.uid}")
            return None
        
        next_node = selected_path[i + 1]
        nav_node = nh.get_nav_node_for_entry_and_node(navigation, next_node)[0]
        #print(nav_node.item_uid)
        indices = nav_node.lane_indices
        #print(indices)
        if len(indices) == 0:
            logging.warning(f"No lane indices found for node {node.uid} to {next_node.uid} ({last_type})")
            return None

        if last_type == c.Prefab:
            if len(route) == 0:
                start = data.route_plan[0].lane_points[0]
                end = last_item.lane_points[-1]
                last_point = start if math_helpers.DistanceBetweenPoints((start.x, start.z), (node.x, node.y)) < \
                                      math_helpers.DistanceBetweenPoints((end.x, end.z), (node.x, node.y)) else end
            else:
                start = route[-1].lane_points[0]
                end = route[-1].lane_points[-1]
                last_point = start if math_helpers.DistanceBetweenPoints((start.x, start.z), (node.x, node.y)) < \
                                      math_helpers.DistanceBetweenPoints((end.x, end.z), (node.x, node.y)) else end
            if len(indices) == 1:
                route.append(PrefabToRouteSection(selected_items[i], indices[0]))
            else:
                #try:
                #    next_next_node = selected_path[i + 2]
                #    possible = ph.get_closest_lanes_from_indices(selected_items[i], last_point.x, last_point.z, indices)
                #    closest = ph.get_closest_lane_from_indices(selected_items[i], next_next_node.x, next_next_node.y, possible)
                #except:
                closest = ph.get_closest_lane_from_indices(selected_items[i], last_point.x, last_point.z, indices)
                if closest == -1:
                    closest = indices[0]
                route.append(PrefabToRouteSection(selected_items[i], closest))
        elif last_type == c.Road:
            if len(route) == 0:
                start = data.route_plan[0].lane_points[0]
                end = last_item.lane_points[-1]
                last_point = start if math_helpers.DistanceBetweenPoints((start.x, start.z), (node.x, node.y)) < \
                                      math_helpers.DistanceBetweenPoints((end.x, end.z), (node.x, node.y)) else end
            else:
                start = route[-1].lane_points[0]
                end = route[-1].lane_points[-1]
                last_point = start if math_helpers.DistanceBetweenPoints((start.x, start.z), (node.x, node.y)) < \
                                      math_helpers.DistanceBetweenPoints((end.x, end.z), (node.x, node.y)) else end
            closest_lane = rh.get_closest_lane(selected_items[i], last_point.x, last_point.z)
            route.append(RoadToRouteSection(selected_items[i], closest_lane))
        else:
            logging.warning(f"Unknown item type: {last_type}")
            return None
        
    data.route_plan = [data.route_plan[0], *route]
    
def ResetState():
    if "indicate" in data.plugin.state.text:
        data.plugin.state.text = ""
    
was_indicating = False
def CheckForLaneChangeManual():
    global was_indicating
    if type(data.route_plan[0].items[0].item) == c.Prefab:
        was_indicating = False
        return
    
    current_index = data.route_plan[0].lane_index
    lanes = data.route_plan[0].items[0].item.lanes
    side = lanes[current_index].side
    left_lanes = len([lane for lane in lanes if lane.side == "left"])
    # lanes = left_lanes + right_lanes
    
    if (data.truck_indicating_right or data.truck_indicating_left) and not was_indicating:
        was_indicating = True
        current_index = data.route_plan[0].lane_index
        side = lanes[current_index].side
        
        target_index = current_index
        change = 1 if data.truck_indicating_right else -1

        closest_item, closest_lane = get_closest_route_item(data.route_plan[0].items)
        end_node_in_front = math_helpers.IsInFront((closest_item.end_node.x, closest_item.end_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
            
        if side == "left":    
            if end_node_in_front: # Normal lane change
                target_index += change
                if change == 1 and target_index >= left_lanes:
                    target_index = left_lanes - 1
            else: # Inverted lane change
                target_index -= change
                if change == -1 and target_index >= left_lanes:
                    target_index = left_lanes - 1
        else:
            if end_node_in_front:
                target_index += change
                if change == -1 and target_index < left_lanes:
                    target_index = left_lanes
            else:
                target_index -= change
                if change == 1 and target_index < left_lanes:
                    target_index = left_lanes
                    
        if target_index < 0:
            target_index = 0
        if target_index >= len(lanes):
            target_index = len(lanes) - 1
                    
        data.route_plan[0].lane_index = target_index
        data.route_plan = [data.route_plan[0]]
        
    elif not data.truck_indicating_left and not data.truck_indicating_right:
        was_indicating = False  
    
def CheckForLaneChange():
    if len(data.route_plan) < 2:
        ResetState()
        return
    
    current = data.route_plan[0]
    if type(current.items[0].item) != c.Road:
        ResetState()
        return
    if current.is_lane_changing:
        ResetState()
        return
    
    next = data.route_plan[1]
    next_point = next.get_points()[0]
    next_end = next.get_points()[-1]
    next_length = math_helpers.DistanceBetweenPoints((next_point.x, next_point.z), (next_end.x, next_end.z))
    if next_length < 10:
        next = data.route_plan[2]
        next_point = next.get_points()[0]
    
    current_point = current.get_points()[-1]
    distance = math_helpers.DistanceBetweenPoints((current_point.x, current_point.z), (next_point.x, next_point.z))
    if distance > 4:
        current_index = current.lane_index
        lanes = current.items[0].item.lanes
        side = lanes[current_index].side
        left_lanes = len([lane for lane in lanes if lane.side == "left"])
        
        # Check the closest lane
        closest = rh.get_closest_lane(current.items[0].item, next_point.x, next_point.z)
        if closest == -1:
            ResetState()
            return
        
        # Go to the lane closest to the closest lane on our side of the road
        if side == "left":
            if closest < left_lanes:
                target = closest
            else:
                target = left_lanes - 1
        else:
            if closest >= left_lanes:
                target = closest
            else:
                target = left_lanes
                
        if target > len(lanes) - 1:
            target = len(lanes) - 1

        closest_item, closest_lane = get_closest_route_item(current.items)
        end_node_in_front = math_helpers.IsInFront((closest_item.end_node.x, closest_item.end_node.y), data.truck_rotation, (data.truck_x, data.truck_z))
        if end_node_in_front:
            indicate_side = "right" if target > current_index else "left"
        else:
            indicate_side = "left" if target > current_index else "right"
            
        if target != current_index:
            planned = current.get_planned_lane_change_distance()
            left = current.distance_left()
            if left > planned and not (data.truck_indicating_right or data.truck_indicating_left):
                data.plugin.state.text = f"Please indicate to confirm lane change {indicate_side}."
                if time.time() - data.last_sound_played > data.sound_play_interval:
                    sounds.Play("info")
                    data.last_sound_played = time.time()
                return
            else:
                data.plugin.state.text = ""
                data.plugin.notify(f"Lane changing {indicate_side}.", type="warning")
                logging.info(f"Changing lane from {current_index} to {target}")
                current.force_lane_change = True
                current.lane_index = target
                data.route_plan = [current]
        else:
            CheckForLaneChangeManual()
            ResetState()
    else:
        CheckForLaneChangeManual()
        ResetState()
        
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
        update = False
        if len(data.route_plan) == 0:
            data.route_plan.append(GetCurrentNavigationPlan())
            
        if data.route_plan[0] is None:
            data.route_plan = []
            return
        
        if data.route_plan[0].is_ended:
            update = True
            data.route_plan.pop(0)
            
        if len(data.route_plan) == 0:
            return
   
        if update or len(data.route_plan) <= 2:
            UpdateNavigatedLanes()
        
        try:
            CheckForLaneChange()
        except:
            pass

def get_closest_route_item(items: list[c.Prefab | c.Road] | list[rc.RouteItem]):
    in_bounding_box = []
    for item in items:
        if isinstance(item, rc.RouteItem):
            item = item.item

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

    return closest_item, closest_lane_id
