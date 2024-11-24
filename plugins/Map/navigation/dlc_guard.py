"""DLC guard module for filtering routes based on enabled DLCs."""

from ..classes import Node, RoadSection, Road, Prefab
from typing import List, Optional, Union
import logging

class DLCGuard:
    def __init__(self, enabled_dlcs: List[str]):
        """Initialize DLC guard with list of enabled DLCs."""
        self.enabled_dlcs = [dlc.lower() for dlc in enabled_dlcs]
        self.dlc_mapping = {
            -1: 'base',
            0: 'base',
            1: 'scandinavia',
            2: 'italia',
            3: 'baltic',
            4: 'black_sea',
            5: 'iberia'
        }
        logging.debug(f"Initialized DLC guard with enabled DLCs: {', '.join(enabled_dlcs)}")

    def is_road_allowed(self, road: Union[Road, RoadSection, Prefab]) -> bool:
        """Check if a road or prefab is allowed based on its DLC requirements."""
        # Handle integer-based dlc_guard
        if hasattr(road, 'dlc_guard'):
            if road.dlc_guard == -1 or road.dlc_guard == 0:
                return True
            dlc_name = self.dlc_mapping.get(road.dlc_guard)
            if not dlc_name:
                logging.warning(f"Unknown DLC guard value: {road.dlc_guard}")
                return False
            return dlc_name.lower() in self.enabled_dlcs

        # Handle string-based dlc property
        if hasattr(road, 'dlc') and road.dlc:
            return road.dlc.lower() in self.enabled_dlcs

        return True  # Base game content is always allowed

    def filter_route(self, route: List[Node]) -> Optional[List[Node]]:
        """Filter a route to ensure all segments use enabled DLCs."""
        if not route:
            return None

        filtered_route = []
        for i in range(len(route) - 1):
            current_node = route[i]
            next_node = route[i + 1]

            # Check if there's a road connecting these nodes
            if hasattr(current_node, 'forward_item'):
                road = current_node.forward_item
                if not self.is_road_allowed(road):
                    logging.warning(f"Route contains road requiring disabled DLC: {road.dlc}")
                    return None

            filtered_route.append(current_node)

        # Add last node
        filtered_route.append(route[-1])

        return filtered_route

    def get_allowed_roads(self, roads: List[RoadSection]) -> List[RoadSection]:
        """Filter a list of roads to only include those from enabled DLCs."""
        return [road for road in roads if self.is_road_allowed(road)]
