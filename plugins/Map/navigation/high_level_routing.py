from ETS2LA.UI import *
from typing import List, Optional, Dict, Set, Tuple
from dataclasses import dataclass
from ..classes import Node, Position, Road, Prefab
from ..utils.math_helpers import DistanceBetweenPoints
import plugins.Map.data as data
import logging
from .dlc_guard import DLCGuard
from .enhanced_queue import EnhancedPriorityQueue

# High-level routing module

@dataclass
class RouteNode:
    node: Node
    g_score: float
    f_score: float
    came_from: Optional['RouteNode'] = None
    dlc_guard: int = -1

    def __hash__(self):
        return hash((self.node.uid, id(self)))

class HighLevelRouter:
    def __init__(self, map_data=None):
        """Initialize the router with default DLC settings."""
        self.dlc_guard = DLCGuard(['base'])  # Start with base game only
        self.enabled_dlc_guards: Set[int] = {-1}  # Default DLC guard is always enabled
        self.map_data = map_data or data.map

    def set_enabled_dlc_guards(self, dlc_guards: Set[int]) -> None:
        """Set the enabled DLC guards."""
        self.enabled_dlc_guards = dlc_guards | {-1}  # Always include default guard
        # Update DLCGuard with corresponding DLC names
        dlc_mapping = {0: 'base', 1: 'scandinavia', 2: 'italia', 3: 'baltic', 4: 'black_sea', 5: 'iberia'}
        enabled_dlcs = ['base'] + [dlc_mapping[guard] for guard in dlc_guards if guard in dlc_mapping]
        self.dlc_guard = DLCGuard(enabled_dlcs)

    def _heuristic(self, node: Node, goal: Node, mode: str = 'shortest') -> float:
        """Calculate heuristic distance between nodes."""
        distance = DistanceBetweenPoints(
            (node.x, node.z),
            (goal.x, goal.z)
        )

        # Enhanced heuristic weights based on truckermudgeon/maps
        if mode == 'shortest':
            return distance * 0.9  # Slight underestimate to encourage path finding
        elif mode == 'smallRoads':
            return distance * 0.6  # Stronger preference for exploring small roads
        else:
            return distance * 1.2  # Default case with slight penalty

    def _get_neighbors(self, node: RouteNode, mode: str = 'shortest') -> List[Tuple[Node, float, int]]:
        """Get neighboring nodes with their distances and DLC guards."""
        neighbors = []
        processed_nodes = set()  # Track processed nodes to avoid duplicates

        def process_road(road: Road, next_node: Node) -> Optional[Tuple[float, int]]:
            """Process a road and return cost and DLC guard if valid."""
            if not self.dlc_guard.is_road_allowed(road) or getattr(road, 'hidden', False):
                return None

            base_cost = road.length
            if mode == 'shortest':
                # Enhanced highway preference based on truckermudgeon/maps
                if hasattr(road, 'road_look_token') and any(
                    token in (road.road_look_token or '').lower()
                    for token in ['highway', 'motorway', 'freeway']
                ):
                    base_cost *= 0.7  # 30% bonus for highways
                elif hasattr(road, 'road_look_token') and 'ramp' in (road.road_look_token or '').lower():
                    base_cost *= 0.9  # 10% bonus for highway ramps
            elif mode == 'smallRoads':
                # Strong preference for small roads
                if hasattr(road, 'road_look_token') and any(
                    token in (road.road_look_token or '').lower()
                    for token in ['highway', 'motorway', 'freeway']
                ):
                    base_cost *= 2.5  # Stronger penalty for highways
                else:
                    base_cost *= 0.6  # 40% bonus for small roads

            return base_cost, road.dlc_guard

        def process_prefab(prefab: Prefab, next_node: Node) -> Optional[Tuple[float, int]]:
            """Process a prefab and return cost and DLC guard if valid."""
            if str(next_node.uid) in processed_nodes or getattr(prefab, 'hidden', False):
                return None
            
            # for whatever reason, these prefabs cause the pathfinding to hang when getting nav_routes
            problem_uids = []
            problem_tokens = ["ibe276"]
            if str(prefab.uid) in problem_uids or prefab.token.lower() in problem_tokens:
                return None

            base_cost = DistanceBetweenPoints((node.node.x, node.node.z), (next_node.x, next_node.z))

            # Enhanced prefab cost calculation from truckermudgeon/maps
            if prefab.prefab_description:
                if prefab.prefab_description.nav_routes == []:
                    return None  # Skip prefabs with no nav_routes
                
                route_count = len(prefab.prefab_description.nav_routes)
                if route_count > 2:  # Complex intersection
                    if mode == 'shortest':
                        base_cost *= 1.2  # Increased penalty for complex intersections
                    else:
                        base_cost *= 1.5  # Higher penalty for small roads mode
                elif 'roundabout' in prefab.token.lower():
                    base_cost *= 1.3  # Penalty for roundabouts
                
            return base_cost, prefab.dlc_guard

        navigation = data.map.get_node_navigation(node.node.uid)
        # TODO: Track the direction to fix some routing errors!
        if not navigation:
            return neighbors
        
        for nav_node in navigation.forward + navigation.backward:
            cost = nav_node.distance
            guard = nav_node.dlc_guard
            neighbors.append((data.map.get_node_by_uid(nav_node.node_id), cost, guard))
            processed_nodes.add(str(nav_node.node_id))

        return neighbors

    def _reconstruct_path(self, current: RouteNode) -> List[Node]:
        """Reconstruct the path from the end node to the start node."""
        path = []
        while current:
            path.append(current.node)
            current = current.came_from
        return list(reversed(path))

    def find_route(
        self,
        start_node: Node,
        end_node: Node,
        mode: str = 'shortest'
    ) -> Optional[List[Node]]:
        """Find a route between nodes using optimized A* pathfinding."""
        if not (start_node and end_node):
            logging.error("Invalid start or end node")
            return None

        open_set = EnhancedPriorityQueue()
        start = RouteNode(
            node=start_node,
            g_score=0,
            f_score=self._heuristic(start_node, end_node, mode)
        )
        open_set.put(start.f_score, start)

        visited: Dict[str, RouteNode] = {str(start_node.uid): start}
        nodes_explored = 0
        lowest_f_score_path = []
        lowest_f_score = float('inf')
        start_score = self._heuristic(start_node, end_node, mode)
        print(f"Start score: {start_score}")
        while not open_set.empty():
            current = open_set.get()
            nodes_explored += 1
            
            # Log progress every 100 nodes
            current_heuristic = self._heuristic(current.node, end_node, mode)
            if current_heuristic < lowest_f_score:
                lowest_f_score_path = self._reconstruct_path(current)
                lowest_f_score = current_heuristic
            
            if nodes_explored % 100 == 0:
                logging.debug(f"Explored {nodes_explored} nodes...")
                data.plugin.state.progress = 1 - lowest_f_score / start_score
                data.plugin.state.text = f"Calculating route... ({nodes_explored}, {lowest_f_score:.1f})"

            if current.node.uid == end_node.uid:
                path = self._reconstruct_path(current)
                path_length = sum(DistanceBetweenPoints(
                    (path[i].x, path[i].z),
                    (path[i+1].x, path[i+1].z)
                ) for i in range(len(path)-1))

                logging.info(
                    f"Path found: {len(path)} nodes, {path_length:.1f}m, "
                    f"explored {nodes_explored} nodes ({(nodes_explored/len(visited))*100:.1f}% "
                    f"of visited nodes), cost: {current.g_score:.1f}"
                )
                return path

            neighbors = self._get_neighbors(current, mode)
            for neighbor_node, cost, dlc_guard in neighbors:
                #if dlc_guard not in self.enabled_dlc_guards:
                #    print(f"Skipping node {neighbor_node.uid} due to DLC guard {dlc_guard}")
                #    continue

                tentative_g_score = current.g_score + cost
                neighbor_key = str(neighbor_node.uid)

                if neighbor_key not in visited:
                    neighbor = RouteNode(
                        node=neighbor_node,
                        g_score=float('inf'),
                        f_score=float('inf'),
                        dlc_guard=dlc_guard
                    )
                    visited[neighbor_key] = neighbor
                else:
                    neighbor = visited[neighbor_key]

                if tentative_g_score < neighbor.g_score:
                    # Create new RouteNode with updated scores
                    visited[neighbor_key] = RouteNode(
                        node=neighbor_node,
                        g_score=tentative_g_score,
                        f_score=tentative_g_score + self._heuristic(neighbor_node, end_node, mode),
                        came_from=current,
                        dlc_guard=dlc_guard
                    )
                    open_set.put(visited[neighbor_key].f_score, visited[neighbor_key])

        logging.warning(
            f"No path found after exploring {nodes_explored} nodes from "
            f"{start_node.uid} to {end_node.uid}"
        )
        
        yes_no = data.plugin.ask("Could not find path to destination.", options=["Yes", "No"], description="Do you want to try to path to the nearest node we could get to?\nThe heuristic distance from the target is " + str(round(lowest_f_score, 1)) + ".")
        
        if yes_no == "Yes":
            logging.warning("Using path to the nearest node we could get to.")
            return lowest_f_score_path
        
        return None
