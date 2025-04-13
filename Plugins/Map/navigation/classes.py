from Plugins.Map.classes import Node, Road, Prefab
from Modules.Route.classes import RouteItem
import Plugins.Map.utils.math_helpers as mh
import Plugins.Map.data as data

from typing import Literal
import logging

class RouteNode:
    """
    Contains computed data based on the 
    RouteItem objects we get from the game.
    """
    route_item: RouteItem
    """The RouteItem object from the game."""
    node: Node
    """Extracted from the RouteItem object."""
    item: Road | Prefab
    """The item that we need to drive on."""
    lanes: list[int]
    """The accepted lanes that we can drive on the item."""
    is_possible: bool = False
    """
    Whether this node is possible to drive on.
    Usually flagged false for ferries.
    """
    direction: Literal["forward", "backward", ""] = ""
    """The navigation direction to the next node."""
    
    def __init__(self, route_item: RouteItem):
        self.route_item = route_item
        
        node = None
        try:
            node = data.map.get_node_by_uid(route_item.uid)
        except Exception:
            logging.exception("Failed to get node by UID")
            pass
        
        self.node = node
        self.item = None
        self.lanes = []
        
    def get_item_lanes(self, item):
        """
        This function will return the lanes that are valid for the given item.
        """
        if type(item) == Road:
            return item.lanes
        elif type(item) == Prefab:
            return item.nav_routes
        return []
        
    def calculate_lanes_from(self, last, direction: Literal["forward", "backward"]):
        """
        This function will be called from the end of the route to the start.
        It will calculate the items and lanes that are needed to get to the destination.
        """
        if self.node is None:
            logging.warning("Current Node is None")
            return False
        if last.node is None:
            logging.warning("Last node is None")
            return False
        
        navigation_information = data.map.get_node_navigation(self.node.uid)
        nav_info = navigation_information.forward if direction == "forward" else navigation_information.backward
        
        item = None
        lanes = []
        for nav_node in nav_info:
            if nav_node.node_id == last.node.uid:
                try:
                    item = data.map.get_item_by_uid(nav_node.item_uid)
                    self.direction = nav_node.direction
                    lanes = nav_node.lane_indices
                except:
                    pass
            
        self.item = item
        if self.item is None:
            self.lanes = lanes
            self.is_possible = len(lanes) > 0
            logging.warning(f"Item is None: Calculated {len(lanes)} valid lanes for node {self.node.uid} ({self.direction})")
            return
        
        # Second to last node, or any nodes after ferries
        if last.item is None:
            self.lanes = lanes
            self.is_possible = len(lanes) > 0
            logging.warning(f"Last Item is None: Calculated {len(lanes)} valid lanes for node {self.node.uid} and item {item.uid} ({type(item).__name__}) ({self.direction})")
            return
        
        # If we are coming from a road to a prefab and they both have
        # the same amount of lanes, it is expected that we can drive on all of them.
        # r r r
        # r r r
        # p p p
        # r r r
        last_lanes = self.get_item_lanes(last.item)
        current_lanes = self.get_item_lanes(self.item)
        if type(last.item) == Road and type(self.item) == Prefab and len(last_lanes) == len(current_lanes):
            self.lanes = lanes
            self.is_possible = len(lanes) > 0
            return
        
        # Lanes now contains all possible lanes that we can drive on.
        # Next we need to check which of them are valid for the next (last) node.
        last_lanes = []
        all_lanes = self.get_item_lanes(last.item)
        for lane in last.lanes:
            last_lanes.append((lane, all_lanes[lane]))
        
        cur_lanes = []
        all_lanes = self.get_item_lanes(self.item)
        for lane in lanes:
            cur_lanes.append((lane, all_lanes[lane]))
            
        # Check if the distance between the current and last lane is less than 2 meters.
        # The lanes are 4.5m wide, so this should be good enough. 
        valid = []
        for last_index, last_lane in last_lanes:
            last_start_point = last_lane.points[0].tuple()
            last_end_point = last_lane.points[-1].tuple()
            for cur_index, cur_lane in cur_lanes:
                cur_start_point = cur_lane.points[0].tuple()
                cur_end_point = cur_lane.points[-1].tuple()
                
                ss_distance = mh.DistanceBetweenPoints(last_start_point, cur_start_point)
                se_distance = mh.DistanceBetweenPoints(last_start_point, cur_end_point)
                es_distance = mh.DistanceBetweenPoints(last_end_point, cur_start_point)
                ee_distance = mh.DistanceBetweenPoints(last_end_point, cur_end_point)
                
                distance = min(ss_distance, se_distance, es_distance, ee_distance)
                if distance < 2:
                    if cur_index not in valid:
                        valid.append(cur_index)
                
        if len(valid) == 0:
            # Driving to a road has to be possible.
            # It would be better to check the specific lane (to stay on the right side)
            # but if that can't be done then we can allow all.
            # r r p
            # r r r
            # r r r
            # r r p
            # ^ ^
            # Both valid lanes
            if type(last.item) == Road:
                valid = lanes
                
        self.lanes = valid
        self.is_possible = len(valid) > 0
        
        # logging.warning(f"Success: Calculated {len(valid)} valid lanes for node {self.node.uid} and item {item.uid} ({type(item).__name__}) ({self.direction})")
        
    def item_type(self):
        """
        Returns the type of the item.
        """
        return type(self.item)