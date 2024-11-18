import plugins.Map.utils.prefab_helpers as prefab_helpers
import plugins.Map.utils.road_helpers as road_helpers
import plugins.Map.utils.math_helpers as math_helpers

import plugins.Map.classes as c
import plugins.Map.data as data

from typing import Literal
import math

class RoadSection():
    roads: list[c.Road] = None
    start: c.Position = None
    end: c.Position = None
    length: float = 0
    points: list[c.Position] = None
    lanes: list[c.Lane] = None
    side: Literal["left", "right"] = None
    
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
    
    @property
    def uid(self):
        return self.roads[0].uid

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
    item: c.Prefab | RoadSection = None
    lane: c.Lane | c.PrefabNavRoute = None
    _type: type = None
    _next_lanes: list = None
    _start_node: c.Node = None
    _end_node: c.Node = None
    
    def __init__(self, lane: c.Lane | c.PrefabNavRoute, item: c.Prefab | RoadSection, start: c.Position, end: c.Position, length: float):
        self.lane = lane
        self.item = item
        self.start = start
        self.end = end
        self.length = length
        self._type = type(item)
        
    def __str__(self):
        return f"NavigationLane({type(self.item)}, {self.start}, {self.end}, {self.length})"
    
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
            print(f"Finding next lanes for {self}")
            print(f"End node: {self.end_node}")
            print(f"Forward item: {self.end_node.forward_item_uid}")
            print(f"Backward item: {self.end_node.backward_item_uid}")
            
            if self.end_node.forward_item_uid != self.item.uid:
                next_item = preprocess_item(data.map.get_item_by_uid(self.end_node.forward_item_uid))
            else:
                next_item = preprocess_item(data.map.get_item_by_uid(self.end_node.backward_item_uid))
            
            print(f"Next item: {next_item}")
            
            if next_item is None:
                return None

            if self._type == RoadSection:
                if isinstance(next_item, RoadSection):
                    next_lanes = [lane for lane in next_item.roads[0].lanes if lane.side == self.lane.side]
                    self._next_lanes = [NavigationLane(
                        lane=lane,
                        item=next_item,
                        start=next_item.start,
                        end=next_item.end,
                        length=next_item.length
                    ) for lane in next_lanes]
                    
                if isinstance(next_item, c.Prefab):
                    # Debug distances to each nav route
                    connection_threshold = 5.0
                    print(f"Current end point: {self.end}")
                    
                    next_routes = []
                    for route in next_item.nav_routes:
                        start_dist = math_helpers.DistanceBetweenPoints(route.points[0].tuple(), self.end.tuple())
                        print(f"Route distances - Start: {start_dist}")
                        
                        if start_dist < connection_threshold:
                            next_routes.append((route, start_dist))
                            
                    print(f"Found {len(next_routes)} connecting routes")
                    self._next_lanes = [NavigationLane(
                        lane=route,
                        item=next_item,
                        start=route.points[0] if forward else route.points[-1],
                        end=route.points[-1] if forward else route.points[0],
                        length=route.distance
                    ) for route, forward in next_routes]
            
            if self._type == c.Prefab:
                if isinstance(next_item, RoadSection):
                    connection_threshold = 5.0
                    print(f"Current end point (Prefab): {self.end}")
                    print(f"RoadSection start: {next_item.start}")
                    print(f"RoadSection end: {next_item.end}")
                    
                    start_dist = math_helpers.DistanceBetweenPoints(next_item.start.tuple(), self.end.tuple())
                    end_dist = math_helpers.DistanceBetweenPoints(next_item.end.tuple(), self.end.tuple())
                    print(f"RoadSection distances - Start: {start_dist}, End: {end_dist}")
                    
                    nav_lanes = []
                    if start_dist < connection_threshold or end_dist < connection_threshold:
                        forward = end_dist < start_dist 
                        for lane in next_item.lanes:
                            nav_lanes.append(NavigationLane(
                                lane=lane,
                                item=next_item,
                                start=lane.points[0] if forward else lane.points[-1],
                                end=lane.points[-1] if forward else lane.points[0],
                                length=next_item.length
                            ))
                            
                    print(f"Found {len(nav_lanes)} connecting lanes to RoadSection")
                    self._next_lanes = nav_lanes
                
                if type(next_item) == c.Prefab:
                    next_routes = [route for route in next_item.nav_routes if math_helpers.DistanceBetweenPoints(route.points[0].tuple(), self.end.tuple()) < 0.1]
                    self._next_lanes = [NavigationLane(
                        lane=route,
                        item=next_item,
                        start=route.points[0],
                        end=route.points[-1],
                        length=route.distance
                    ) for route in next_routes]
                    
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
    if not item or isinstance(item, c.Prefab):
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
    
    return RoadSection(roads)
