from typing import List, Optional, Union, Tuple, Dict
from functools import lru_cache
import logging
from plugins.Map.classes import Node, Prefab
from plugins.Map.navigation.classes import RoadSection, NavigationLane
import plugins.Map.data as data
from plugins.Map.navigation.high_level_routing import HighLevelRouter
import plugins.Map.utils.math_helpers as math_helpers

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

    def get_connected_item(self, node: Node) -> Optional[Union[Prefab, RoadSection]]:
        """Find the closest item connected to a node."""
        logging.debug(f"Finding connected item for node {node.uid} at position ({node.x}, {node.z})")

        # Check roads first
        for road in data.map.roads:
            if road.start_node_uid == node.uid or road.end_node_uid == node.uid:
                logging.debug(f"Found connected road: {road.uid}")
                road.get_nodes()  # Initialize nodes
                return road

        # If no road found, check prefabs
        for prefab in data.map.prefabs:
            if node.uid in prefab.node_uids:
                logging.debug(f"Found connected prefab: {prefab.uid}")
                return prefab

        logging.warning(f"No connected item found for node {node.uid}")
        return None

    def _find_connecting_item(
        self,
        current_node: Node,
        next_node: Node,
        dlc_guard: Optional[List[str]] = None
    ) -> Optional[Union[Prefab, RoadSection]]:
        """Find the item (road or prefab) connecting two nodes with DLC validation."""
        # Get all connected items for both nodes
        current_item = self.get_connected_item(current_node)
        next_item = self.get_connected_item(next_node)

        if not current_item or not next_item:
            return None

        # If both nodes are connected to the same item, that's our connecting item
        if current_item.uid == next_item.uid:
            # Validate DLC requirements
            if dlc_guard is not None and hasattr(current_item, 'dlc') and current_item.dlc not in dlc_guard:
                logging.debug(f"Skipping item {current_item.uid} due to DLC restriction")
                return None
            return current_item

        # Otherwise, look for an item connecting the two nodes
        if current_node.forward_item_uid == next_node.backward_item_uid:
            item = data.map.get_item_by_uid(current_node.forward_item_uid)
            if item:
                return item
        elif current_node.backward_item_uid == next_node.forward_item_uid:
            item = data.map.get_item_by_uid(current_node.backward_item_uid)
            if item:
                return item
        
        # Fallback to road search
        if current_item and next_item:
            road = data.map.get_road_between_nodes(current_node.uid, next_node.uid)
            if road and (dlc_guard is None or not hasattr(road, 'dlc') or road.dlc in dlc_guard):
                road.get_nodes()  # Initialize nodes
                return road
        
        distance = math_helpers.DistanceBetweenPoints((current_node.x, current_node.y), (next_node.x, next_node.y))
        print(distance)
        if distance < 1:
            return True

        return None

    def get_nav_lanes_for_node(self, node: Node, item: Union[Prefab, RoadSection]) -> List[NavigationLane]:
        """Get navigation lanes for a node within an item."""
        logging.debug(f"Getting navigation lanes for node {node.uid} in item {item.uid}")

        from plugins.Map.navigation.navigation import get_nav_lanes
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
                logging.warning("No high-level route found between nodes")
                return None

            logging.debug(f"Found high-level route through nodes: {[n.uid for n in node_path]}")
        except Exception as e:
            logging.error(f"Error finding high-level route: {str(e)}")
            return None

        data.plugin.state.text = "Processing route..."
        # Convert node path to lane-level navigation
        nav_lanes: List[NavigationLane] = []
        old_path = []
        for i in range(len(node_path) - 1):
            current_node = node_path[i]
            next_node = node_path[i + 1]
            logging.debug(f"Processing segment {i}: {current_node.uid} -> {next_node.uid}")

            # Find the item connecting these nodes using optimized method
            connecting_item = self._find_connecting_item(current_node, next_node, dlc_guard)

            if not connecting_item:
                logging.error(f"Could not find valid connecting item between nodes {current_node.uid} and {next_node.uid}")
                return None

            if type(connecting_item) == bool:
                logging.info(f"Nodes {current_node.uid} and {next_node.uid} are connected already.")
                return []
            
            # Get navigation lanes for this segment
            try:
                from plugins.Map.navigation.navigation import find_path
                start_lanes = self.get_nav_lanes_for_node(current_node, connecting_item)
                end_lanes = self.get_nav_lanes_for_node(next_node, connecting_item)

                if not start_lanes or not end_lanes:
                    logging.error(f"Could not find navigation lanes for segment {current_node.uid} -> {next_node.uid}")
                    return None

                # Find path through this segment
                segment_path = []
                for lane in end_lanes:
                    tmp_segment_path, tmp_old_path = find_path(start_lanes, lane, old_path=old_path)
                    if tmp_segment_path:
                        segment_path = tmp_segment_path
                        old_path = tmp_old_path
                        break
                    
                if not segment_path:
                    logging.error(f"Could not find path through segment {current_node.uid} -> {next_node.uid}")
                    return None

                nav_lanes.extend(segment_path)
                logging.debug(f"Added {len(segment_path)} lanes for segment {current_node.uid} -> {next_node.uid}")

            except Exception as e:
                logging.error(f"Error processing segment {current_node.uid} -> {next_node.uid}: {str(e)}")
                return None

        data.plugin.state.reset()
        logging.info(f"Successfully found complete path with {len(nav_lanes)} navigation lanes")
        # Store in cache
        self._path_cache[cache_key] = nav_lanes
        return nav_lanes

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
