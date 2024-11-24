from typing import List, Optional, Tuple
from ..classes import Node, Position
from .high_level_routing import HighLevelRouter
from ..utils.math_helpers import DistanceBetweenPoints
import plugins.Map.data as data
import logging

class PathFinder:
    def __init__(self, map_data=None):
        self.map_data = map_data or data.map
        self.router = HighLevelRouter(map_data=self.map_data)

    def find_nearest_node(self, position: Position, max_distance: float = 1000.0) -> Optional[Node]:
        """Find the nearest node to a given position within max_distance."""
        nearest_node = None
        min_distance = float('inf')

        for node in self.map_data.nodes:
            distance = DistanceBetweenPoints(
                (position.x, position.z),
                (node.x, node.z)
            )
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest_node = node

        return nearest_node

    def find_path(
        self,
        start_pos: Position,
        end_pos: Position,
        mode: str = 'shortest',
        max_search_distance: float = 1000.0
    ) -> Optional[List[Node]]:
        """Find a path between two positions in the game world.

        Args:
            start_pos: Starting position
            end_pos: Destination position
            mode: Routing mode ('shortest' or 'smallRoads')
            max_search_distance: Maximum distance to search for nearest nodes

        Returns:
            List of nodes representing the path, or None if no path found
        """
        # Find nearest nodes to start and end positions
        start_node = self.find_nearest_node(start_pos, max_search_distance)
        end_node = self.find_nearest_node(end_pos, max_search_distance)

        if not start_node or not end_node:
            logging.warning("Could not find suitable nodes near positions")
            return None

        logging.info(f"Finding path from node {start_node.uid} to {end_node.uid}")

        # Use high-level router to find path between nodes
        return self.router.find_route(start_node, end_node, mode)

    def set_enabled_dlc_guards(self, dlc_guards: set[int]) -> None:
        """Set the enabled DLC guards for routing."""
        self.router.set_enabled_dlc_guards(dlc_guards)
