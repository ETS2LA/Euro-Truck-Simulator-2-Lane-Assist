import plugins.Map.utils.prefab_helpers as prefab_helpers
import plugins.Map.utils.road_helpers as road_helpers
import plugins.Map.utils.math_helpers as math_helpers

import plugins.Map.classes as c
import plugins.Map.data as data

from typing import Literal
import math

DISTANCE_THRESHOLD = 2.25 # meters
MAX_DISTANCE_THRESHOLD = 4.5 # meters | only if above fails

class RoadSection():
    roads: list[c.Road] = None
    start: c.Position = None
    end: c.Position = None
    length: float = 0
    points: list[c.Position] = None
    lanes: list[c.Lane] = None
    side: Literal["left", "right"] = None
    x: float = None
    y: float = None
    z: float = None
    
    def __init__(self, roads: list[c.Road]):
        self.roads = roads
        self.start = roads[0].points[0]
        self.end = roads[-1].points[-1]
        self.points = [point for road in roads for point in road.points]
        self.length = sum([road.length for road in roads])
        
        lane_count = len(roads[0].lanes)
        self.lanes = []
        for i in range(lane_count):
            self.lanes.append(c.Lane(
                side=roads[0].lanes[i].side,
                points=[point for road in roads for point in road.lanes[i].points]
            ))
            
        # Calculate the center point
        self.x = sum([point.x for point in self.points]) / len(self.points)
        self.y = sum([point.y for point in self.points]) / len(self.points)
        self.z = sum([point.z for point in self.points]) / len(self.points)
    
    @property
    def uid(self):
        return self.roads[-1].uid
    
    @property
    def uids(self): 
        return [road.uid for road in self.roads]

    def __str__(self):
        return f"RoadSection({len(self.roads)} roads, start={self.start}, end={self.end})"
        
    def __eq__(self, other):
        if not isinstance(other, RoadSection):
            return False
        return self.roads[0].uid == other.roads[0].uid
        
    def __hash__(self):
        return hash(self.roads[0].uid)

class NavigationLane():
    length: float = 0
    start: c.Position = None
    end: c.Position = None
    item: c.Prefab | RoadSection | c.Road = None
    lane: c.Lane | c.PrefabNavRoute = None
    direction: Literal["forward", "backward"] = None
    _type: type = None
    _next_lanes: list = None
    _start_node: c.Node = None
    _end_node: c.Node = None
    
    def __init__(self, lane: c.Lane | c.PrefabNavRoute, item: c.Prefab | RoadSection, start: c.Position, end: c.Position, length: float, direction: Literal["forward", "backward"] = "forward"):
        self.lane = lane
        self.item = item
        self.start = start
        self.end = end
        self.length = length
        self._type = type(item)
        self.direction = direction
        
    def __str__(self):
        return f"NavigationLane({type(self.item).__name__}, {round(self.length, 1)}m)"
    
    def __repr__(self):
        return self.__str__()
    
    @property
    def start_node(self):    
        if self._start_node is None:
            if self._type == RoadSection:
                start_node = data.map.get_node_by_uid(self.item.roads[0].start_node_uid)
                end_node = data.map.get_node_by_uid(self.item.roads[-1].end_node_uid)
                start_position = self.lane.points[0]
                if math_helpers.DistanceBetweenPoints(start_position.tuple(), (start_node.x, start_node.y, start_node.z)) < math_helpers.DistanceBetweenPoints(start_position.tuple(), (end_node.x, end_node.y, end_node.z)):
                    self._start_node = start_node
                else:
                    self._start_node = end_node
            
            if self._type == c.Road:
                start_node = data.map.get_node_by_uid(self.item.start_node_uid)
                end_node = data.map.get_node_by_uid(self.item.end_node_uid)
                start_position = self.lane.points[0]
                if math_helpers.DistanceBetweenPoints(start_position.tuple(), (start_node.x, start_node.y, start_node.z)) < math_helpers.DistanceBetweenPoints(start_position.tuple(), (end_node.x, end_node.y, end_node.z)):
                    self._start_node = start_node
                else:
                    self._start_node = end_node
            
            if self._type == c.Prefab:
                nodes = [data.map.get_node_by_uid(node_uid) for node_uid in self.item.node_uids]
                start_position = self.lane.points[0]
                closest_node = None
                closest_distance = math.inf
                for node in nodes:
                    distance = math_helpers.DistanceBetweenPoints(start_position.tuple(), (node.x, node.y, node.z))
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_node = node
                        
                self._start_node = closest_node
            
        return self._start_node
    
    @property
    def end_node(self):        
        if self._end_node is None:
            if self._type == RoadSection:
                start_node = data.map.get_node_by_uid(self.item.roads[0].start_node_uid)
                end_node = data.map.get_node_by_uid(self.item.roads[-1].end_node_uid)
                end_position = self.lane.points[-1]
                if math_helpers.DistanceBetweenPoints(end_position.tuple(), (start_node.x, start_node.y, start_node.z)) > math_helpers.DistanceBetweenPoints(end_position.tuple(), (end_node.x, end_node.y, end_node.z)):
                    self._end_node = end_node
                else:
                    self._end_node = start_node
                    
            if self._type == c.Road:
                start_node = data.map.get_node_by_uid(self.item.start_node_uid)
                end_node = data.map.get_node_by_uid(self.item.end_node_uid)
                end_position = self.lane.points[-1]
                if math_helpers.DistanceBetweenPoints(end_position.tuple(), (start_node.x, start_node.y, start_node.z)) > math_helpers.DistanceBetweenPoints(end_position.tuple(), (end_node.x, end_node.y, end_node.z)):
                    self._end_node = end_node
                else:
                    self._end_node = start_node
                    
            if self._type == c.Prefab:
                nodes = [data.map.get_node_by_uid(node_uid) for node_uid in self.item.node_uids]
                end_position = self.lane.points[-1]
                closest_node = None
                closest_distance = math.inf
                for node in nodes:
                    distance = math_helpers.DistanceBetweenPoints(end_position.tuple(), (node.x, node.y, node.z))
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_node = node
                        
                self._end_node = closest_node
            
        return self._end_node
    
    @property
    def next_lanes(self) -> list | None:
        if self._next_lanes is None:
            next_item = None
            print(f"- Finding next lanes for {self}")
            
            if self._type == RoadSection: # FROM ROAD
                forward = True
                if self.end_node.forward_item_uid not in self.item.uids:
                    forward = True
                    next_item = preprocess_item(data.map.get_item_by_uid(self.end_node.forward_item_uid))
                elif self.end_node.backward_item_uid not in self.item.uids:
                    forward = False
                    next_item = preprocess_item(data.map.get_item_by_uid(self.end_node.backward_item_uid))
                
                print(f" -> Next item: {next_item}")
                
                if next_item is None:
                    return None
                
                if isinstance(next_item, RoadSection): # TO ROAD
                    if len(next_item.roads[0].road_look.lanes_left) == 0 or len(next_item.roads[0].road_look.lanes_right) == 0:
                        next_lanes = [lane for lane in next_item.lanes]
                    else:
                        next_lanes = [lane for lane in next_item.lanes if lane.side == self.lane.side]
                    
                    self._next_lanes = [NavigationLane(
                        lane=lane,
                        item=next_item,
                        start=next_item.start if forward else next_item.end,
                        end=next_item.end if forward else next_item.start,
                        length=next_item.length
                    ) for lane in next_lanes]
                    
                    for lane in self._next_lanes:
                        print(f"  -> Found lane: {next_item.lanes.index(lane.lane)} ({round(lane.length)}m)")
                    
                if isinstance(next_item, c.Road): # TO PREFAB
                    if len(next_item.road_look.lanes_left) == 0 or len(next_item.road_look.lanes_right) == 0:
                        next_lanes = [lane for lane in next_item.lanes]
                    else:
                        next_lanes = [lane for lane in next_item.lanes if lane.side == self.lane.side]
                        
                    self._next_lanes = [NavigationLane(
                        lane=lane,
                        item=next_item,
                        start=next_item.points[0] if forward else next_item.points[-1],
                        end=next_item.points[-1] if forward else next_item.points[0],
                        length=next_item.length
                    ) for lane in next_lanes]
                    
                    for lane in self._next_lanes:
                        print(f"  -> Found lane: {next_item.lanes.index(lane.lane)} ({round(lane.length)}m)")
                    
                if isinstance(next_item, c.Prefab): # TO PREFAB
                    next_routes = []
                    for i, route in enumerate(next_item.nav_routes):
                        start_dist = math_helpers.DistanceBetweenPoints(route.points[0].tuple(), self.end.tuple())
                        print(f"  -> Road ({self.lane.side}) -> Prefab ({i})  -  Distance: {start_dist}")
                        
                        if start_dist < DISTANCE_THRESHOLD:
                            next_routes.append(route)
                            
                    if len(next_routes) == 0:
                        print("   -> Using backup distances as no routes were found")
                        distances = [math_helpers.DistanceBetweenPoints(route.points[0].tuple(), self.end.tuple()) for route in next_item.nav_routes]
                        min_distance = min(distances)
                        min_index = distances.index(min_distance)
                        if min_distance < MAX_DISTANCE_THRESHOLD:
                            next_routes.append(next_item.nav_routes[min_index])
                            
                    for route in next_routes:
                        print(f"  -> Found route: {next_item.nav_routes.index(route)} ({round(route.distance)}m)")
                            
                    self._next_lanes = [NavigationLane(
                        lane=route,
                        item=next_item,
                        start=route.points[0],
                        end=route.points[-1],
                        length=route.distance
                    ) for route in next_routes]
            
            if self._type == c.Prefab: # FROM PREFAB
                next_items = []
                for node_uid in self.item.node_uids:
                    node = data.map.get_node_by_uid(node_uid)
                    if node.forward_item_uid != self.item.uid:
                        next_items.append(preprocess_item(data.map.get_item_by_uid(node.forward_item_uid)))
                    elif node.backward_item_uid != self.item.uid:
                        next_items.append(preprocess_item(data.map.get_item_by_uid(node.backward_item_uid)))
                        
                if len(next_items) == 0:
                    return None
                
                next_lanes = []
                for j, next_item in enumerate(next_items):
                    if isinstance(next_item, RoadSection) or isinstance(next_item, c.Road): # TO ROAD
                        nav_lanes = []
                        side = ""
                        forward = False
                        for i, lane in enumerate(next_item.lanes):
                            if side != "":
                                print(f"  -> Prefab ({self.item.nav_routes.index(self.lane)}) -> Lane ({j})({i})  -  Already confirmed side: {side}")
                                continue
                            
                            start_dist = math_helpers.DistanceBetweenPoints(lane.points[0].tuple(), self.end.tuple())
                            end_dist = math_helpers.DistanceBetweenPoints(lane.points[-1].tuple(), self.end.tuple())
                            print(f"  -> Prefab ({self.item.nav_routes.index(self.lane)}) -> Lane ({j})({i})  -  Start: {start_dist}, End: {end_dist}")
                            if start_dist < DISTANCE_THRESHOLD or end_dist < DISTANCE_THRESHOLD:
                                forward = start_dist < end_dist
                                side = lane.side
                            
                        nav_lanes = [lane for lane in next_item.lanes if lane.side == side]
                        
                        for lane in nav_lanes:
                            print(f"  -> Found lane: {next_item.lanes.index(lane)} ({round(lane.length)}m)")
                        
                        next_lanes.append([NavigationLane(
                            lane=lane,
                            item=next_item,
                            start=lane.points[0] if forward else lane.points[-1],
                            end=lane.points[-1] if forward else lane.points[0],
                            length=lane.length
                        ) for lane in nav_lanes])
                    
                    elif type(next_item) == c.Prefab: # TO PREFAB
                        next_routes = [route for route in next_item.nav_routes if math_helpers.DistanceBetweenPoints(route.points[0].tuple(), self.end.tuple()) < DISTANCE_THRESHOLD]
                        next_lanes.append([NavigationLane(
                            lane=route,
                            item=next_item,
                            start=route.points[0],
                            end=route.points[-1],
                            length=route.distance
                        ) for route in next_routes])
                        
                        for route in next_routes:
                            print(f"  -> Found route: {next_item.nav_routes.index(route)} ({round(route.distance)}m)")
                        
                    else:
                        print(f"  -> Unknown item type: {type(next_item)}")
                        
                self._next_lanes = [lane for sublist in next_lanes for lane in sublist]
                    
        return self._next_lanes

    def __eq__(self, other):
        if not isinstance(other, NavigationLane):
            return False
        return (self.item.uid == other.item.uid and 
                math_helpers.DistanceBetweenPoints(self.start.tuple(), other.start.tuple()) < 0.1 and
                math_helpers.DistanceBetweenPoints(self.end.tuple(), other.end.tuple()) < 0.1)
                
    def __hash__(self):
        return hash((self.item.uid, self.start.tuple(), self.end.tuple()))

def preprocess_item(item: c.Road | c.Prefab | None) -> RoadSection | c.Prefab | None:
    """
    Preprocesses any map item for navigation.
    - Returns Prefabs as-is
    - Converts Roads into RoadSections by combining connected roads
    - Returns None for invalid items
    """
    if not item:    
        return None
    
    if isinstance(item, c.Prefab) or isinstance(item, RoadSection):
        return item
        
    if not isinstance(item, c.Road):
        return None
        
    roads = [item]
    current_road = item
    
    # Forward check
    while True:
        forward_node = data.map.get_node_by_uid(current_road.end_node_uid)
        if not forward_node:
            break
            
        next_item = None
        if forward_node.forward_item_uid != current_road.uid:
            next_item = data.map.get_item_by_uid(forward_node.forward_item_uid)
        else:
            next_item = data.map.get_item_by_uid(forward_node.backward_item_uid)
            
        # Make sure next_item exists and is a road
        if not next_item or not isinstance(next_item, c.Road):
            break
            
        roads.append(next_item)
        current_road = next_item
    
    if len(roads) == 0:
        return None
    
    if len(roads[0].points) == 0:
        return None
    
    try:
        return RoadSection(roads)
    except:
        return None
