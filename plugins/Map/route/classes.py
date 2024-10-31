import plugins.Map.utils.math_helpers as math_helpers
import plugins.Map.classes as c
import plugins.Map.data as data
import numpy as np
import logging
import math
import time

class RouteItem:
    item: list[c.Prefab | c.Road]
    _lane_index: int = 0
    lane_points: list[c.Position]
    
    @property
    def lane_index(self) -> int:
        return self._lane_index
    
    @lane_index.setter
    def lane_index(self, value: int):
        try:
            if type(self.item) == c.Road:
                self.lane_points = self.item.lanes[value].points
            elif type(self.item) == c.Prefab:
                self.lane_points = self.item.nav_routes[value].points
            self._lane_index = value
        except:
            logging.warning(f"Something tried to set an [red]invalid lane index of {value}[/red] when [dim]RouteItem[/dim] only has {len(self.item.lanes)} lanes.")
            pass
            
class RouteSection:
    items: list[RouteItem]
    _lane_index: int = 0
    lane_points: list[c.Position] = []
    last_lane_points: list[c.Position] = []
    lane_change_start: c.Position
    is_lane_changing: bool = False
    lane_change_distance: float = 0 
    is_ended: bool = False
    last_actual_points: list[c.Position] = []
    _start_node: c.Node = None
    _end_node: c.Node = None
    _first_set_done: bool = False
    """Used to override some checks in the lane_index setter until the function is run once."""
    
    @property
    def start_node(self) -> c.Node:
        if self._start_node is not None:
            return self._start_node
        if type(self.items[0].item) == c.Prefab:
            return data.map.get_node_by_uid(self.items[0].item.node_uids[0])
        return data.map.get_node_by_uid(self.items[0].item.start_node_uid)
    
    @property
    def end_node(self) -> c.Node:
        if self._end_node is not None:
            return self._end_node
        if type(self.items[0].item) == c.Prefab:
            return data.map.get_node_by_uid(self.items[0].item.node_uids[-1])
        return data.map.get_node_by_uid(self.items[-1].item.end_node_uid)
    
    @property
    def lane_index(self) -> int:
        return self._lane_index
    
    @lane_index.setter
    def lane_index(self, value: int):
        if value == self._lane_index and self._first_set_done:
            return
        elif not self._first_set_done:
            self._first_set_done = True
        
        if type(self.items[0].item) == c.Prefab:
            self._lane_index = value
            self.lane_points = self.items[0].item.nav_routes[self.lane_index].points
            return
        
        if value > len(self.items[0].item.lanes) - 1 or value < 0:
            logging.warning(f"Something tried to set an [red]invalid lane index of {value}[/red] when [dim]RouteSection[/dim] only has {len(self.items[0].item.lanes)} lanes.")
        
        if self.lane_points != []:
            speed_kph = data.truck_speed * 3.6
            lane_change_distance = speed_kph * data.lane_change_distance_per_kph
            if lane_change_distance < data.minimum_lane_change_distance: 
                lane_change_distance = data.minimum_lane_change_distance
            
            if self.distance_left() < lane_change_distance:
                logging.warning(f"Something tried to do a lane change requiring [dim]{lane_change_distance:.0f}m[/dim], but only [dim]{self.distance_left():.0f}m[/dim] is left.")
                return
            
            self.is_lane_changing = True
            self.lane_change_distance = lane_change_distance
            self.lane_change_start = c.Position(data.truck_x, data.truck_y, data.truck_z)
        
        self.last_lane_points = self.lane_points
        self.lane_points = []
        for item in self.items:
            item.lane_index = value
            self.lane_points += item.lane_points
            
        min_distance = 0.25
        last_point = self.lane_points[0]
        accepted_points = []
        for point in self.lane_points:
            if math_helpers.DistanceBetweenPoints(point.tuple(), last_point.tuple()) > min_distance:
                accepted_points.append(point)
                last_point = point
        
        self.lane_points = accepted_points
        self._lane_index = value

    def distance_left(self) -> float:
        if self.last_actual_points == []:
            self.last_actual_points = self.get_points()
        distance = 0
        last_point = c.Position(data.truck_x, data.truck_y, data.truck_z)
        for point in self.last_actual_points:
            distance += math_helpers.DistanceBetweenPoints(last_point.tuple(), point.tuple())
            last_point = point
        return distance

    def discard_points_behind(self, points: list[c.Position]) -> list[c.Position]:
        forward_vector = [-math.sin(data.truck_rotation), -math.cos(data.truck_rotation)]
        new_points = []
        for point in points:
            point_forward_vector = [point.x - data.truck_x, point.z - data.truck_z]
            angle = np.arccos(np.dot(forward_vector, point_forward_vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(point_forward_vector)))
            angle = math.degrees(angle)
            if angle > 90 or angle < -90:
                continue
            
            new_points.append(point)
            
        new_points = sorted(new_points, key=lambda x: math_helpers.DistanceBetweenPoints(x.tuple(), (data.truck_x, data.truck_y, data.truck_z)))
        temp_points = new_points

        if temp_points == []:
            return []
        
        try:
            average_distance = sum([math_helpers.DistanceBetweenPoints(temp_points[i].tuple(), temp_points[i + 1].tuple()) for i in range(len(temp_points) - 1)]) / len(temp_points)
        except:
            average_distance = 1
        
        closest_distance = 0
        truck = c.Position(data.truck_x, data.truck_y, data.truck_z)
        closest_id = 0
        for i in range(len(temp_points) - 1):
            distance = math_helpers.DistanceBetweenPoints(truck.tuple(), temp_points[i].tuple())
            if distance < closest_distance:
                closest_distance = distance
                closest_id = i
                
        if closest_distance > 20:
            return []
        
        new_points = []
        last_point = temp_points[closest_id]
        for point in temp_points:
            if math_helpers.DistanceBetweenPoints(last_point.tuple(), point.tuple()) < average_distance * 2:
                new_points.append(point)
                last_point = point
        
        return new_points
            
    def get_points(self):
        current_lane_points = self.discard_points_behind(self.lane_points)
        if current_lane_points == []:
            self.is_ended = True
        
        if not self.is_lane_changing or type(self.items[0].item) == c.Prefab:
            self.last_actual_points = current_lane_points
            return current_lane_points
        
        lane_change_factor = math_helpers.DistanceBetweenPoints(self.lane_change_start.tuple(), (data.truck_x, data.truck_y, data.truck_z)) / self.lane_change_distance
        lane_change_factor = math_helpers.InOut(lane_change_factor)
        if lane_change_factor > 0.98:
            self.is_lane_changing = False
            if data.truck_indicating_left:
                data.controller.lblinker = True
                time.sleep(1/20)
                data.controller.lblinker = False
                time.sleep(1/20)
            elif data.truck_indicating_right:
                data.controller.rblinker = True
                time.sleep(1/20)
                data.controller.rblinker = False
                time.sleep(1/20)
            return current_lane_points
        
        last_lane_points = self.discard_points_behind(self.last_lane_points)

        end_index = 0
        factors = []
        for i in range(len(current_lane_points)):
            try:
                current_point = current_lane_points[i]
                last_lane_point = last_lane_points[i]
                middle_point = math_helpers.TupleMiddle(last_lane_point.tuple(), current_point.tuple())
                distance = math_helpers.DistanceBetweenPoints(middle_point, self.lane_change_start.tuple())
                if math_helpers.DistanceBetweenPoints(middle_point, self.lane_change_start.tuple()) > self.lane_change_distance:
                    end_index = i
                    break
                factors.append(math_helpers.InOut(distance / self.lane_change_distance))
            except: continue
           
        new_points = []
            
        for i in range(len(current_lane_points)):
            if i < end_index:
                new_tuple = math_helpers.LerpTuple(last_lane_points[i].tuple(), current_lane_points[i].tuple(), factors[i])
                new_points.append(c.Position(new_tuple[0], new_tuple[1], new_tuple[2]))
            else:
                new_points.append(current_lane_points[i])
                
        self.last_actual_points = new_points
        return new_points
    
    def __str__(self):
        return f"RouteSection: {self.start_node.uid} -> {self.end_node.uid}\n\
                Lane index: {self.lane_index}\n\
                Distance left: {self.distance_left():.0f}m\n\
                Lane changing: {self.is_lane_changing}\n\
                Is ended: {self.is_ended}\n\
                Type: {type(self.items[0].item)}"