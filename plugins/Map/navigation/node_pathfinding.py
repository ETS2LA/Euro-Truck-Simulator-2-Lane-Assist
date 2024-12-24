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
        logging.info("Initialized NodePathfinder")

    def find_path_between_nodes(
        self,
        start_node: Node,
        end_node: Node,
        dir: str = 'forward',
        mode: str = 'shortest'
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

        data.plugin.state.text = "Calculating route..."
        logging.info(f"Finding path between nodes {start_node.uid} and {end_node.uid} using {mode} mode")

        # Get route
        try:
            node_path = self.router.find_route(start_node, end_node, mode, dir)
            if not node_path or type(node_path) != list:
                data.plugin.state.reset()
                data.plugin.state.text = f"Finding satisfactory route... {round(node_path)}m"
                data.update_navigation_plan = True
                #logging.warning("No high-level route found between nodes")
                return None

            logging.debug(f"Found high-level route through nodes: {[n.uid for n in node_path]}")
            
        except Exception as e:
            data.plugin.state.reset()
            data.plugin.state.text = "Finding satisfactory route..."
            data.update_navigation_plan = True
            #data.plugin.notify("Unable to find route to the destination.", type="warning")
            logging.exception(f"Error finding high-level route: {str(e)}")
            return None

        data.plugin.state.reset()
        return node_path