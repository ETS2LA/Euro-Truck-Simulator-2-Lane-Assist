import plugins.Map.utils.math_helpers as math_helpers
import plugins.Map.classes as c
import plugins.Map.data as data
import math

class NavigationLane():
    length: float = 0
    start: c.Position = None
    end: c.Position = None
    item: c.Item = None
    lane: c.Lane | c.PrefabNavRoute = None
    _type: c.Prefab | c.Road = None
    _start_node: c.Node = None
    _end_node: c.Node = None
    
    def __init__(self, lane: c.Lane | c.PrefabNavRoute, item: c.Prefab | c.Road, start: c.Position, end: c.Position, length: float):
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
            if self._type == c.Road:
                start_node = data.map.get_node_by_uid(self.item.start_node_uid)
                end_node = data.map.get_node_by_uid(self.item.end_node_uid)
                start_position = self.lane.points[0]
                if math_helpers.DistanceBetweenPoints(start_position.tuple(), (start_node.x, start_node.y, start_node.z)) < math_helpers.DistanceBetweenPoints(start_position.tuple(), (end_node.x, end_node.y, end_node.z)):
                    self._start_node = start_node
                else:
                    self._start_node = end_node
            
            if self.type == c.Prefab:
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
            if self._type == c.Road:
                start_node = data.map.get_node_by_uid(self.item.start_node_uid)
                end_node = data.map.get_node_by_uid(self.item.end_node_uid)
                start_position = self.lane.points[0]
                if math_helpers.DistanceBetweenPoints(start_position.tuple(), (start_node.x, start_node.y, start_node.z)) < math_helpers.DistanceBetweenPoints(start_position.tuple(), (end_node.x, end_node.y, end_node.z)):
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