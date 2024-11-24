"""Enhanced pathfinding implementation for ETS2."""
from typing import List, Optional, Tuple, Dict
from plugins.Map.classes import Node, Road, Prefab, Position
from plugins.Map.utils.data_reader import ReadRoads, ReadNodes, ReadPrefabs
from plugins.Map.utils.dlc_guard import check_dlc_access
import heapq
import logging

logger = logging.getLogger(__name__)

class RouteNode:
    """Node wrapper for A* algorithm."""
    def __init__(self, node: Node, g_score: float = float('inf'),
                 f_score: float = float('inf'), parent: Optional['RouteNode'] = None):
        self.node = node
        self.g_score = g_score
        self.f_score = f_score
        self.parent = parent

    def __lt__(self, other: 'RouteNode') -> bool:
        return self.f_score < other.f_score

class PathFinder:
    """Enhanced pathfinding implementation with DLC and hidden road awareness."""

    def __init__(self, enabled_dlcs: List[str], test_roads: List[Road] = None,
                 test_nodes: List[Node] = None, test_prefabs: List[Prefab] = None):
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
        # Only read from files if no test data is provided
        self.roads = test_roads if test_roads is not None else ReadRoads()
        self.nodes = test_nodes if test_nodes is not None else ReadNodes()
        self.prefabs = test_prefabs if test_prefabs is not None else ReadPrefabs()
        self._build_node_connections()

    def _build_node_connections(self):
        """Build node connection map for efficient pathfinding."""
        self.node_connections: Dict[str, List[Tuple[Node, Road]]] = {}
        logging.info(f"Building node connections for {len(self.nodes)} nodes and {len(self.roads)} roads")

        # Create node lookup dictionary for faster access
        self.node_lookup = {str(node.uid): node for node in self.nodes}
        logging.info(f"Created node lookup dictionary with {len(self.node_lookup)} entries")

        # Process roads
        for road in self.roads:
            if not self._is_road_allowed(road):
                continue

            start_node = self.node_lookup.get(str(road.start_node_uid))
            end_node = self.node_lookup.get(str(road.end_node_uid))

            if start_node and end_node:
                # Initialize connection lists if they don't exist
                if str(start_node.uid) not in self.node_connections:
                    self.node_connections[str(start_node.uid)] = []
                if str(end_node.uid) not in self.node_connections:
                    self.node_connections[str(end_node.uid)] = []

                # Add bidirectional connections
                self.node_connections[str(start_node.uid)].append((end_node, road))
                self.node_connections[str(end_node.uid)].append((start_node, road))

                # Set node references in road object
                road.start_node = start_node
                road.end_node = end_node

        # Process prefabs
        for prefab in self.prefabs:
            if prefab.hidden or not check_dlc_access(prefab.dlc_guard):
                continue

            # Connect all nodes in the prefab
            for i in range(len(prefab.node_uids)):
                current_node = next((n for n in self.nodes if n.uid == prefab.node_uids[i]), None)
                if not current_node:
                    continue

                # Connect to next node in prefab
                if i < len(prefab.node_uids) - 1:
                    next_node = next((n for n in self.nodes if n.uid == prefab.node_uids[i + 1]), None)
                    if next_node:
                        if str(current_node.uid) not in self.node_connections:
                            self.node_connections[str(current_node.uid)] = []
                        if str(next_node.uid) not in self.node_connections:
                            self.node_connections[str(next_node.uid)] = []

                        # Create virtual road for prefab connection
                        virtual_road = Road(
                            uid=f"prefab_{prefab.uid}_{i}",
                            x=(current_node.x + next_node.x) / 2,
                            y=(current_node.y + next_node.y) / 2,
                            sector_x=prefab.sector_x,
                            sector_y=prefab.sector_y,
                            dlc_guard=prefab.dlc_guard,
                            hidden=prefab.hidden,
                            road_look_token="prefab",
                            start_node_uid=current_node.uid,
                            end_node_uid=next_node.uid,
                            length=((next_node.x - current_node.x) ** 2 +
                                  (next_node.y - current_node.y) ** 2 +
                                  (next_node.z - current_node.z) ** 2) ** 0.5,
                            maybe_divided=False
                        )

                        self.node_connections[str(current_node.uid)].append((next_node, virtual_road))
                        self.node_connections[str(next_node.uid)].append((current_node, virtual_road))

        logging.debug(f"Built connections for {len(self.node_connections)} nodes")

    def _is_road_allowed(self, road: Road) -> bool:
        """Check if a road is allowed based on DLC and hidden status."""
        if road.hidden:
            return False

        dlc_name = self.dlc_mapping.get(road.dlc_guard, 'unknown').lower()
        if dlc_name == 'unknown':
            logging.warning(f"Unknown DLC guard value: {road.dlc_guard}")
            return False

        return dlc_name in self.enabled_dlcs

        return check_dlc_access(road.dlc_guard)

    def _calculate_cost(self, road: Road, mode: str = "fastest") -> float:
        """Calculate cost of traversing a road segment."""
        base_cost = road.length

        if mode == "fastest":
            # Prefer highways
            if "highway" in road.road_look_token.lower():
                return base_cost * 0.7  # 30% bonus for highways
            return base_cost
        else:  # smallRoads mode
            # Avoid highways, prefer small roads
            if "highway" in road.road_look_token.lower():
                return base_cost * 2.5  # 150% penalty for highways
            return base_cost * 0.7  # 30% bonus for small roads

    def _heuristic(self, node: Node, goal: Node) -> float:
        """Calculate heuristic distance between nodes."""
        return ((node.x - goal.x) ** 2 +
                (node.y - goal.y) ** 2 +
                (node.z - goal.z) ** 2) ** 0.5

    def find_path(self, start: Node, goal: Node, mode: str = "fastest", max_iterations: int = 10000) -> Optional[List[Node]]:
        """Find path between nodes using A* algorithm."""
        logging.info(f"Finding path from node {start.uid} to {goal.uid} using mode {mode}")
        logging.debug(f"Start node position: ({start.x}, {start.y}, {start.z})")
        logging.debug(f"Goal node position: ({goal.x}, {goal.y}, {goal.z})")
        logging.debug(f"Enabled DLCs: {self.enabled_dlcs}")

        open_set = []
        closed_set = set()
        iterations = 0

        start_route_node = RouteNode(start, g_score=0,
                                   f_score=self._heuristic(start, goal))
        heapq.heappush(open_set, start_route_node)

        node_lookup = {str(start.uid): start_route_node}

        while open_set:
            iterations += 1
            if iterations >= max_iterations:
                logging.warning(f"Path finding exceeded {max_iterations} iterations, aborting")
                return None

            current = heapq.heappop(open_set)
            logging.debug(f"Exploring node {current.node.uid}")

            if current.node.uid == goal.uid:
                logging.info(f"Path found in {iterations} iterations")
                path = []
                while current:
                    path.append(current.node)
                    current = current.parent
                return list(reversed(path))

            closed_set.add(str(current.node.uid))

            # Debug log available connections
            connections = self.node_connections.get(str(current.node.uid), [])
            logging.debug(f"Node {current.node.uid} has {len(connections)} connections")

            for neighbor, road in connections:
                logging.debug(f"Checking connection to node {neighbor.uid} via road {road.uid}")
                logging.debug(f"Road DLC guard: {road.dlc_guard}, hidden: {road.hidden}")

                if str(neighbor.uid) in closed_set:
                    continue

                if not self._is_road_allowed(road):
                    logging.debug(f"Road {road.uid} not allowed (DLC: {self.dlc_mapping.get(road.dlc_guard)})")
                    continue

                tentative_g_score = (current.g_score +
                                   self._calculate_cost(road, mode))

                if str(neighbor.uid) not in node_lookup:
                    neighbor_route_node = RouteNode(neighbor)
                    node_lookup[str(neighbor.uid)] = neighbor_route_node
                    heapq.heappush(open_set, neighbor_route_node)
                else:
                    neighbor_route_node = node_lookup[str(neighbor.uid)]
                    if tentative_g_score >= neighbor_route_node.g_score:
                        continue

                neighbor_route_node.parent = current
                neighbor_route_node.g_score = tentative_g_score
                neighbor_route_node.f_score = (tentative_g_score +
                                             self._heuristic(neighbor, goal))

        logging.warning(f"No path found after {iterations} iterations")
        return None  # No path found
