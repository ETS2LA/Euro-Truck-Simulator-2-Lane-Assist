import Plugins.Map.utils.math_helpers as math_helpers
from ETS2LA.Utils import settings
import Plugins.Map.classes as c
import Plugins.Map.data as data
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
            else:
                print("Invalid item type")
                print(type(self.item))
            self._lane_index = value
        except:
            #logging.exception(f"Something tried to set an [red]invalid lane index of {value}[/red] when [dim]RouteItem[/dim] only has {len(self.item.lanes)} lanes.")
            pass
            
class RouteSection:
    items: list[RouteItem]
    _lane_index: int = 0
    _last_lane_index: int = 0
    lane_points: list[c.Position] = []
    lane_change_points: list[c.Position] = []
    last_lane_points: list[c.Position] = []
    lane_change_start: c.Position
    lane_change_factor: float = 0
    is_lane_changing: bool = False
    lane_change_distance: float = 0 
    is_ended: bool = False
    invert: bool = False
    last_actual_points: list[c.Position] = []
    force_lane_change: bool = False
    skip_indicate_state: bool = False
    _start_node: c.Node = None
    _end_node: c.Node = None
    _first_set_done: bool = False
    _target_lanes: list[int] = []
    """Used to override some checks in the lane_index setter until the function is run once."""
    _lane_change_progress: float = 0.0 
    _start_at_truck: bool = True
    
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
            self._last_lane_index = self._lane_index
            self._lane_index = value
            self.lane_points = self.items[0].item.nav_routes[self.lane_index].points
            return
        
        if value > len(self.items[0].item.lanes) - 1 or value < 0:
            logging.warning(f"Something tried to set an [red]invalid lane index of {value}[/red] when [dim]RouteSection[/dim] only has {len(self.items[0].item.lanes)} lanes.")
            return
        
        if self.is_lane_changing:
            logging.warning("Something tried to change the lane index while the route section is still lane changing.")
            return
        
        
        self.last_lane_points = self.lane_points.copy() if self.lane_points else []
        new_lane_points = []
        for item in self.items:
            item.lane_index = value
            new_lane_points += item.lane_points
        
        new_lane_points = new_lane_points if not self.invert else new_lane_points[::-1]
        
        if self.lane_points:
            lanes_to_move_over = abs(value - self.lane_index)
            lane_change_distance = self.get_planned_lane_change_distance(lane_count=lanes_to_move_over) * 2 # * 2 for the initial static area
            if self.skip_indicate_state:
                lane_change_distance /= 2
            
            dist_left = 0
            if not self.is_in_bounds(c.Position(data.truck_x, data.truck_y, data.truck_z)):
                dist_left = self.distance_left(from_index=0)
            else:
                dist_left = self.distance_left()

            if dist_left < lane_change_distance:
                if self.force_lane_change:
                    self.skip_indicate_state = True
                    lane_change_distance = dist_left
                else:
                    logging.warning(f"Something tried to do a lane change requiring [dim]{lane_change_distance:.0f}m[/dim], but only [dim]{dist_left:.0f}m[/dim] is left.")
                    return
            
            if self._start_at_truck:
                self.lane_change_start = c.Position(data.truck_x, data.truck_y, data.truck_z)
            else:
                start = self.last_lane_points[0]
                end = self.last_lane_points[-1]
                s_distance = math_helpers.DistanceBetweenPoints(start.tuple(), (data.truck_x, data.truck_y, data.truck_z))
                e_distance = math_helpers.DistanceBetweenPoints(end.tuple(), (data.truck_x, data.truck_y, data.truck_z))
                if s_distance < e_distance:
                    self.lane_change_start = c.Position(start.x, start.y, start.z)
                else:
                    self.lane_change_start = c.Position(end.x, end.y, end.z)
            
            self.lane_change_distance = lane_change_distance
            self.lane_change_points = self._calculate_lane_change_points(self.last_lane_points, new_lane_points)
            
            if self.lane_change_points:
                self.is_lane_changing = True
                self._lane_change_progress = 0.0
            
        self.lane_points = new_lane_points
        self._last_lane_index = self._lane_index
        self._lane_index = value
        self.skip_indicate_state = False

    def _calculate_lane_change_points(self, start_points, end_points):
        """Pre-calculate lane change points between start_points and end_points"""
        start_points = self.discard_points_behind(start_points)
        end_points = self.discard_points_behind(end_points)
        
        if not start_points or not end_points:
            return []
            
        # Ensure both lists are the same length
        while len(start_points) > len(end_points):
            start_points.pop()
        while len(end_points) > len(start_points):
            end_points.pop()
            
        if not start_points or not end_points:
            return []
            
        lane_change_points = []
        end_index = 0
        factors = []
        for i in range(len(start_points)):
            try:
                start_point = start_points[i]
                end_point = end_points[i]
                middle_point = math_helpers.TupleMiddle(start_point.tuple(), end_point.tuple())
                distance = math_helpers.DistanceBetweenPoints(middle_point, self.lane_change_start.tuple())
                
                if distance >= self.lane_change_distance - 1:
                    # After this point, we'll just use the destination lane points
                    end_index = i
                    break
                    
                # Calculate the smoothed transition factor
                s = distance / self.lane_change_distance
                if not self.skip_indicate_state:
                    if s < 0.5:
                        s = 0
                    else:
                        s = (s - 0.5) * 2
                    
                factor = math_helpers.InOut(s)
                factors.append(factor)
            except:
                continue
        
        # Lerp between the start and end points using the calculated factors
        # and add the points to the lane_change_points list
        for i in range(len(start_points)):
            if i < end_index:
                new_tuple = math_helpers.LerpTuple(start_points[i].tuple(), end_points[i].tuple(), factors[i])
                lane_change_points.append(c.Position(new_tuple[0], new_tuple[1], new_tuple[2]))
            else:
                lane_change_points.append(end_points[i])

        data.circles = lane_change_points

        return lane_change_points

    @property
    def target_lanes(self) -> list[int]:
        return self._target_lanes
    
    @target_lanes.setter
    def target_lanes(self, value: list[int]):
        if self.is_lane_changing:
            return
        if type(self.items[0].item) == c.Prefab:
            return
        if self.lane_points == []:
            return
        if value == []:
            return
        
        closest = min(value, key=lambda x: abs(x - self.lane_index))
        if closest == self.lane_index:
            return
        
        # Check if the other lane is on the wrong side of the road
        cur_lane = self.items[0].item.lanes[self.lane_index]
        other_lane = self.items[0].item.lanes[closest]
        if cur_lane.side != other_lane.side:
            logging.warning(f"Something tried to change lanes to [dim]{closest}[/dim] but the lane is on the wrong side of the road.")
            return
        
        # Call lane_index setter to update the lane index
        self.force_lane_change = True
        if not self.is_in_bounds(c.Position(data.truck_x, data.truck_y, data.truck_z)):
            self._start_at_truck = False
            self.lane_index = closest
            self._start_at_truck = True
        else:
            self.lane_index = closest
        self.force_lane_change = False

    def distance_left(self, from_index = None) -> float:
        if self.last_actual_points == []:
            self.last_actual_points = self.get_points()
        
        distance = 0
        if from_index is not None:
            for i in range(from_index, len(self.last_actual_points) - 1):
                distance += math_helpers.DistanceBetweenPoints(self.last_actual_points[i].tuple(), self.last_actual_points[i + 1].tuple())
                
        else:
            last_point = c.Position(data.truck_x, data.truck_y, data.truck_z)
            for point in self.last_actual_points:
                distance += math_helpers.DistanceBetweenPoints(last_point.tuple(), point.tuple())
                last_point = point
                
        return distance

    def get_planned_lane_change_distance(self, lane_count=1) -> float:
        speed_kph = data.truck_speed * 3.6
        lane_change_distance = speed_kph * data.lane_change_distance_per_kph
        if lane_change_distance < data.minimum_lane_change_distance: 
            lane_change_distance = data.minimum_lane_change_distance
        return lane_change_distance * lane_count

    def discard_points_behind(self, points: list[c.Position]) -> list[c.Position]:
        forward_vector = [-math.sin(data.truck_rotation), -math.cos(data.truck_rotation)]
        distances = []
        new_points = []
        for i, point in enumerate(points):
            distance = math_helpers.DistanceBetweenPoints(point.tuple(), (data.truck_x, data.truck_y, data.truck_z))
            point_forward_vector = [point.x - data.truck_x, point.z - data.truck_z]
            
            # Clip the value to ensure it's within [-1, 1] before passing to np.arccos
            dot_product = np.dot(forward_vector, point_forward_vector)
            norms_product = np.linalg.norm(forward_vector) * np.linalg.norm(point_forward_vector)
            
            # Avoid division by zero if norms_product is zero
            if norms_product == 0:
                angle = 0.0 # Or handle as appropriate for your application
            else:
                value = dot_product / norms_product
                value = np.clip(value, -1.0, 1.0) # Clip the value
                angle = np.arccos(value)

            angle = math.degrees(angle)
            if angle > 90 or angle < -90:
                continue
            
            distances.append(distance)
            new_points.append(point)
                
        if new_points == [] or distances == []:
            return []
        
        paired = list(zip(new_points, distances))
        paired.sort(key=lambda x: x[1])
        new_points, distances = zip(*paired)

        new_points = list(new_points)
        distances = list(distances)
        
        temp_points = []
        distances_to_truck = []
        distances_to_each_other = []
        for i, point in enumerate(new_points):
            index = i
            if index == 0:
                temp_points.append(point)
                distances_to_truck.append(distances[0])
                distances_to_each_other.append(0)
                continue
            
            distance = math_helpers.DistanceBetweenPoints(point.tuple(), temp_points[-1].tuple())
            if distance < 4:
                temp_points.append(point)
                distances_to_truck.append(distances[i])
                distances_to_each_other.append(distance)

        if temp_points == []:
            return []
        
        if distances_to_each_other == []:
            return []
        
        try:
            average_distance = sum(distances_to_each_other) / len(distances_to_each_other)
        except:
            average_distance = 1
        
        closest_distance = 0
        for i in range(len(temp_points) - 1):
            distance = distances_to_truck[i]
            if distance < closest_distance:
                closest_distance = distance
                
        if closest_distance > 20:
            return []
        
        new_points = []
        for i, point in enumerate(temp_points):
            if distances_to_each_other[i] < max(average_distance * 2, 1):
                new_points.append(point)
        
        return new_points
            
    def is_in_bounds(self, point: c.Position, offset: int = -5) -> bool:
        temp_y = point.y
        point.y = point.z
        point.z = temp_y
        for item in self.items:
            if type(item.item) == c.Road:
                if item.item.bounding_box.is_in(point, offset=offset):
                    return True
        return False
            
    def reset_indicators(self):
        if data.enabled and self.is_in_bounds(c.Position(data.truck_x, data.truck_y, data.truck_z)):
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
    
    def indicate_right(self):
        if data.enabled:
            if not data.truck_indicating_right:
                data.controller.rblinker = True
                time.sleep(1/20)
                data.controller.rblinker = False
                time.sleep(1/20)
            
    def indicate_left(self):
        if data.enabled:
            if not data.truck_indicating_left:
                data.controller.lblinker = True
                time.sleep(1/20)
                data.controller.lblinker = False
                time.sleep(1/20)
            
    def get_points(self):

        plugin_status = (data.plugin.globals.tags.running or {}).get('catalogueplugins.automatic blinkers', False)

        if not plugin_status:
            if not self.is_lane_changing and self.is_in_bounds(c.Position(data.truck_x, data.truck_y, data.truck_z)):
                self.reset_indicators()

        # Check the setting so the indicators work correctly in UK for example
        self._traffic_side = settings.Get("Map", "traffic_side", "")
            
        # If not lane changing, return the normal lane points
        if not self.is_lane_changing or type(self.items[0].item) == c.Prefab:
            current_lane_points = self.discard_points_behind(self.lane_points)
            if len(current_lane_points) < 2:
                self.is_ended = True
                if self.is_lane_changing:
                    self.reset_indicators()
            else:
                self.is_ended = False
                
            self.last_actual_points = current_lane_points
            return current_lane_points
        
        if self.lane_change_distance <= 0:
            self.lane_change_distance = 1
        
        # Update lane change progress based on distance traveled
        if self.is_in_bounds(c.Position(data.truck_x, data.truck_y, data.truck_z)):
            self._lane_change_progress = math_helpers.DistanceBetweenPoints(
                self.lane_change_start.tuple(), 
                (data.truck_x, data.truck_y, data.truck_z)
            ) / self.lane_change_distance
            self.lane_change_factor = math_helpers.InOut(self._lane_change_progress)
        
        if self._traffic_side == "Automatic":
            try:
                x = data.truck_x
                y = data.truck_z

                calais = [-31100, -5500]
                is_uk = x < calais[0] and y < calais[1]

                if is_uk:
                    uk_factor = 0.75
                    x = (x + calais[0]/2) * uk_factor
                    y = (y + calais[1]/2) * uk_factor

                left_hand = is_uk

            except Exception:
                left_hand = False
        else:
            left_hand = self._traffic_side == "Left"

        # Set traffic side
        self._traffic_side = "Left" if left_hand else "Right"

        # Lane-change logic
        if self.is_lane_changing and self._lane_change_progress > 0:
            side = self.items[0].item.lanes[self.lane_index].side
            if left_hand:  # reverse for left-hand traffic
                side = "left" if side == "right" else "right"

            diff = self._last_lane_index - self.lane_index

            if (side == "left" and diff > 0 and not data.truck_indicating_right) or \
            (side == "right" and diff < 0 and not data.truck_indicating_right):
                self.indicate_right()
            elif (side == "left" and diff < 0 and not data.truck_indicating_left) or \
                (side == "right" and diff > 0 and not data.truck_indicating_left):
                self.indicate_left()
        
        # Check if lane change is complete
        if self._lane_change_progress > 0.98:
            self.is_lane_changing = False
            # Turn off blinkers after lane change
            self.reset_indicators()
            
            self.lane_change_factor = 0
            self._lane_change_progress = 0
            self.lane_points = self.discard_points_behind(self.lane_points)
            self.last_actual_points = self.lane_points
            return self.lane_points
        
        # Get relevant lane change points based on current position
        current_lane_points = self.discard_points_behind(self.lane_change_points)
        
        if len(current_lane_points) < 2:
            self.is_ended = True
            # Fallback to last points if we don't have enough lane change points
            if self.last_actual_points:
                return self.last_actual_points
            return []
        else:
            self.is_ended = False
            
        self.last_actual_points = current_lane_points
        return current_lane_points
    
    def __str__(self):
        return f"RouteSection: {self.start_node.uid} ({math_helpers.DistanceBetweenPoints((self.start_node.x, self.start_node.y), (data.truck_x, data.truck_z))}) -> {self.end_node.uid} ({math_helpers.DistanceBetweenPoints((self.end_node.x, self.end_node.y), (data.truck_x, data.truck_z))})\n\
                Lane index: {self.lane_index}\n\
                Distance left: {self.distance_left():.0f}m\n\
                Lane changing: {self.is_lane_changing}\n\
                Is ended: {self.is_ended}\n\
                Type: {type(self.items[0].item)}"
                
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RouteSection):
            return False
        return self.start_node.uid == value.start_node.uid and self.end_node.uid == value.end_node.uid and self.lane_index == value.lane_index
    
    def information_json(self):
        return {
            "uids": [item.item.uid for item in self.items],
            "lane_index": self.lane_index,
            "type": type(self.items[0].item).__name__,
            "is_ended": self.is_ended,
            "is_lane_changing": self.is_lane_changing,
            "lane_points": [point.tuple() for point in self.lane_points] if self.is_lane_changing else [],
            "last_lane_points": [point.tuple() for point in self.last_lane_points] if self.is_lane_changing else [],
        }