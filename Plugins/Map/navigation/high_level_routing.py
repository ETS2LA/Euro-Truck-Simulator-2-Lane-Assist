import Plugins.Map.utils.prefab_helpers as prefab_helpers
from ..utils.math_helpers import DistanceBetweenPoints
from typing import List, Optional, Dict, Set, Tuple
from ..classes import Node, Position, Road, Prefab
from .enhanced_queue import EnhancedPriorityQueue
from dataclasses import dataclass
import Plugins.Map.data as data
from ETS2LA.UI import *
import logging

# High-level routing module

@dataclass
class RouteNode:
    node: Node
    g_score: float
    f_score: float
    came_from: Optional['RouteNode'] = None
    dlc_guard: int = -1
    direction: str = "unknown"

    def __hash__(self):
        return hash((self.node.uid, id(self)))

class HighLevelRouter:
    def __init__(self, map_data=None):
        """Initialize the router with default DLC settings."""
        self.map_data = map_data or data.map


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
        dir = node.direction
        processed_nodes = set()  # Track processed nodes to avoid duplicates

        def process_road(road: Road, distance: float) -> Optional[Tuple[float, int]]:
            """Process a road and return cost and DLC guard if valid."""
            if getattr(road, 'hidden', False):
                return 9999999  # Avoid hidden roads

            base_cost = distance
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

            return base_cost

        def process_prefab(prefab: Prefab, distance: float) -> Optional[Tuple[float, int]]:
            """Process a prefab and return cost and DLC guard if valid."""
            # for whatever reason, these prefabs cause the pathfinding to hang when getting nav_routes
            problem_uids = []
            problem_tokens = ["ibe276"]
            if str(prefab.uid) in problem_uids or prefab.token.lower() in problem_tokens:
                return 9999999

            base_cost = distance

            if prefab.prefab_description:
                count = len(prefab_helpers.find_starting_curves(prefab.prefab_description))
                if count > 3:  # Complex intersection
                    if mode == 'shortest':
                        base_cost *= 1.2 # Increased penalty for complex intersections 
                    else:
                        base_cost *= 1.5
                elif 'roundabout' in prefab.token.lower():
                    base_cost *= 1.2  # Penalty for roundabouts
                
            return base_cost

        navigation = data.map.get_node_navigation(node.node.uid)
        if not navigation:
            return neighbors
        
        if dir == "forward":
            for nav_node in navigation.forward:
                item = data.map.get_item_by_uid(nav_node.item_uid)
                if isinstance(item, Road):
                    cost = process_road(item, nav_node.distance)
                elif isinstance(item, Prefab):
                    cost = process_prefab(item, nav_node.distance)
                else:
                    cost = nav_node.distance
                    
                guard = nav_node.dlc_guard
                direction = nav_node.direction
                neighbors.append((data.map.get_node_by_uid(nav_node.node_id), cost, guard, direction))
                processed_nodes.add(str(nav_node.node_id))
                
        elif dir == "backward":
            for nav_node in navigation.backward:
                item = data.map.get_item_by_uid(nav_node.item_uid)
                if isinstance(item, Road):
                    cost = process_road(item, nav_node.distance)
                elif isinstance(item, Prefab):
                    cost = process_prefab(item, nav_node.distance)
                else:
                    cost = nav_node.distance
                    
                guard = nav_node.dlc_guard
                direction = nav_node.direction
                neighbors.append((data.map.get_node_by_uid(nav_node.node_id), cost, guard, direction))
                processed_nodes.add(str(nav_node.node_id))
                
        else:
            for nav_node in navigation.forward + navigation.backward:
                item = data.map.get_item_by_uid(nav_node.item_uid)
                if isinstance(item, Road):
                    cost = process_road(item, nav_node.distance)
                elif isinstance(item, Prefab):
                    cost = process_prefab(item, nav_node.distance)
                else:
                    cost = nav_node.distance
                    
                guard = nav_node.dlc_guard
                direction = nav_node.direction
                neighbors.append((data.map.get_node_by_uid(nav_node.node_id), cost, guard, direction))
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
        mode: str = 'shortest',
        dir: str = 'forward'
    ) -> Optional[List[Node]]:
        """Find a route between nodes using optimized A* pathfinding."""
        if not (start_node and end_node):
            logging.error("Invalid start or end node")
            return None

        open_set = EnhancedPriorityQueue()
        start = RouteNode(
            node=start_node,
            g_score=0,
            f_score=self._heuristic(start_node, end_node, mode),
            direction=dir
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
                
                print(f"Path found: {len(path)} nodes, {path_length:.1f}m, "
                    f"explored {nodes_explored} nodes ({(nodes_explored/len(visited))*100:.1f}% "
                    f"of visited nodes), cost: {current.g_score:.1f}")
                
                data.plugin.notify(f"Found {path_length/1000:.1f}km path to destination.")
                return path

            neighbors = self._get_neighbors(current, mode)
            for neighbor_node, cost, dlc_guard, direction in neighbors:
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
                        dlc_guard=dlc_guard,
                        direction=direction
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
                        dlc_guard=dlc_guard,
                        direction=direction
                    )
                    open_set.put(visited[neighbor_key].f_score, visited[neighbor_key])

        logging.warning(
            f"No path found after exploring {nodes_explored} nodes from "
            f"{start_node.uid} to {end_node.uid}, lowest f-score: {lowest_f_score:.1f}"
        )
        
        print(f"End score: {lowest_f_score}")
        
        if lowest_f_score < data.auto_accept_threshold:
            yes_no = "Yes"
        elif lowest_f_score < data.auto_deny_threshold:
            yes_no = data.plugin.ask("Could not find path to destination.", options=["Yes", "No"], description="Do you want to try to path to the nearest node we could get to?\nThe heuristic distance from the target is " + str(round(lowest_f_score, 1)) + ".")
        else:
            return lowest_f_score
        
        if yes_no == "Yes":
            logging.warning("Using path to the nearest node we could get to.")
            return lowest_f_score_path
        
        return None
