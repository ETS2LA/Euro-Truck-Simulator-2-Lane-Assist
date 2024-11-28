from plugins.Map.navigation.classes import RoadSection, NavigationLane
from plugins.Map.navigation.high_level_routing import HighLevelRouter
from typing import List, Optional, Union, Tuple, Dict
import plugins.Map.utils.math_helpers as math_helpers
from plugins.Map.classes import Node, Prefab
from functools import lru_cache
import plugins.Map.classes as c
import plugins.Map.data as data
import logging

class NodePathfinder:
    def __init__(self):
        self.router = HighLevelRouter()
        self.router.set_enabled_dlc_guards({0, 1, 2, 3, 4, 5})
        self._path_cache: Dict[str, List[NavigationLane]] = {}
        logging.info("Initialized NodePathfinder")

    def clear_cache(self):
        """Clear the path finding cache."""
        self._path_cache.clear()
        logging.info("Path finding cache cleared")

    def get_connected_items(self, node: Node) -> list[Union[Prefab, RoadSection]]:
        """Find the closest item connected to a node."""
        logging.debug(f"Finding connected item for node {node.uid} at position ({node.x}, {node.z})")

        items = []
        close_items = []
        sectors = data.map.get_sectors_for_coordinate_and_distance(node.x, node.y, data.load_distance)
        for sector in sectors:
            close_items += data.map.get_sector_items_by_sector(sector)
            
        # Check roads first
        for item in close_items:
            if type(item) == c.Road:
                if item.start_node_uid == node.uid or item.end_node_uid == node.uid:
                    logging.info(f"Found connected road: {item.uid}")
                    item.get_nodes()  # Initialize nodes
                    items.append(item)
                
            if type(item) == c.Prefab:
                print(node.uid)
                print(item.node_uids)
                if node.uid in item.node_uids:
                    logging.info(f"Found connected prefab: {item.uid}")
                    items.append(item)

        if len(items) == 0:
            logging.warning(f"No connected item found for node {node.uid}")
        return items

    def _find_connecting_item(
        self,
        current_node: Node,
        next_node: Node,
        dlc_guard: Optional[List[str]] = None
    ) -> Optional[Union[Prefab, RoadSection, c.Road]]:
        """Find the item (road or prefab) connecting two nodes with DLC validation."""
        # Get all connected items for both nodes
        current_items = self.get_connected_items(current_node)
        next_items = self.get_connected_items(next_node)
        
        print(f"Current items: {[item.uid for item in current_items]}\nNext items: {[item.uid for item in next_items]}")

        if current_items == [] or next_items == []:
            return None

        # If both nodes are connected to the same item, that's our connecting item
        for cur_item in current_items:
            for next_item in next_items:
                if cur_item.uid == next_item.uid:
                    # Validate DLC requirements
                    if dlc_guard is not None and hasattr(cur_item, 'dlc') and cur_item.dlc not in dlc_guard:
                        logging.debug(f"Skipping item {cur_item.uid} due to DLC restriction")
                        return None
                    return cur_item
        
        # Fallback to road search
        if current_items and next_items:
            road = data.map.get_road_between_nodes(current_node.uid, next_node.uid)
            if road and (dlc_guard is None or not hasattr(road, 'dlc') or road.dlc in dlc_guard):
                road.get_nodes()  # Initialize nodes
                return road
        
        distance = math_helpers.DistanceBetweenPoints((current_node.x, current_node.y), (next_node.x, next_node.y))
        if distance < 1:
            return True

        return None

    def get_nav_lanes_for_node(self, node: Node, item: Union[Prefab, RoadSection], x: int = None, z: int = None) -> List[NavigationLane]:
        """Get navigation lanes for a node within an item."""
        from plugins.Map.navigation.navigation import get_nav_lanes
        logging.debug(f"Getting navigation lanes for node {node.uid} in item {item.uid}")

        if x and z:
            lanes = get_nav_lanes(item, x, z)
        else:
            lanes = get_nav_lanes(item, node.x, node.y)
        logging.debug(f"Found {len(lanes)} navigation lanes")
        return lanes

    def find_path_between_nodes(
        self,
        start_node: Node,
        end_node: Node,
        mode: str = 'shortest',
        dlc_guard: Optional[List[str]] = None
    ) -> Optional[List[NavigationLane]]:
        """Find a path between two nodes using lane-level navigation.

        Args:
            start_node: Starting node
            end_node: Destination node
            mode: Routing mode ('shortest' or 'smallRoads')
            dlc_guard: List of allowed DLC names, None means all DLCs allowed
        """
        # Validate input nodes first
        if not (start_node and end_node):
            logging.error("Invalid start or end node")
            return None

        # Generate cache key
        cache_key = f"{start_node.uid}_{end_node.uid}_{mode}_{','.join(sorted(dlc_guard)) if dlc_guard else 'all'}"

        # Check cache
        if cache_key in self._path_cache:
            logging.debug(f"Cache hit for path: {cache_key}")
            return self._path_cache[cache_key]

        data.plugin.state.text = "Calculating route..."
        logging.info(f"Finding path between nodes {start_node.uid} and {end_node.uid} using {mode} mode")

        # Get high-level route
        try:
            node_path = self.router.find_route(start_node, end_node, mode)
            if not node_path:
                data.plugin.state.reset()
                data.plugin.notify("Unable to find route to the destination.", type="warning")
                logging.warning("No high-level route found between nodes")
                return None

            logging.debug(f"Found high-level route through nodes: {[n.uid for n in node_path]}")
        except Exception as e:
            data.plugin.state.reset()
            data.plugin.notify("Unable to find route to the destination.", type="warning")
            logging.error(f"Error finding high-level route: {str(e)}")
            return None

        data.plugin.state.reset()
        return node_path

    @lru_cache(maxsize=128)
    def get_path_between_positions(
        self,
        start_pos: Tuple[float, float],
        end_pos: Tuple[float, float],
        mode: str = 'shortest',
        dlc_guard: Optional[List[str]] = None,
        max_search_radius: float = 1000.0
    ) -> Optional[List[NavigationLane]]:
        """Find a path between two positions using node-based routing.

        Args:
            start_pos: Starting position (x, z)
            end_pos: Destination position (x, z)
            mode: Routing mode ('shortest' or 'smallRoads')
            dlc_guard: List of allowed DLC names
            max_search_radius: Maximum radius to search for nearest nodes
        """
        # Generate cache key for position-based path
        cache_key = f"pos_{start_pos[0]}_{start_pos[1]}_{end_pos[0]}_{end_pos[1]}_{mode}_{'-'.join(sorted(dlc_guard)) if dlc_guard else 'all'}"

        # Check cache
        if cache_key in self._path_cache:
            logging.debug(f"Cache hit for position path: {cache_key}")
            return self._path_cache[cache_key]

        logging.info(f"Finding path between positions {start_pos} and {end_pos}")

        from plugins.Map.utils.math_helpers import DistanceBetweenPoints

        # Find nearest nodes to positions within search radius
        start_candidates = []
        end_candidates = []

        for node in data.map.nodes:
            start_dist = DistanceBetweenPoints(start_pos, (node.x, node.z))
            end_dist = DistanceBetweenPoints(end_pos, (node.x, node.z))

            if start_dist <= max_search_radius:
                start_candidates.append((node, start_dist))
            if end_dist <= max_search_radius:
                end_candidates.append((node, end_dist))

        if not start_candidates or not end_candidates:
            logging.error(f"No nodes found within {max_search_radius}m of positions")
            return None

        # Sort candidates by distance
        start_candidates.sort(key=lambda x: x[1])
        end_candidates.sort(key=lambda x: x[1])

        # Try paths with closest nodes first
        for start_node, _ in start_candidates[:3]:  # Try 3 closest start nodes
            for end_node, _ in end_candidates[:3]:  # Try 3 closest end nodes
                path = self.find_path_between_nodes(start_node, end_node, mode, dlc_guard)
                if path:
                    logging.info(f"Found path using nodes {start_node.uid} -> {end_node.uid}")
                    return path

        logging.error("Could not find valid path between positions")
        return None
