from plugins.Map.navigation.classes import RoadSection
from plugins.Map.utils import road_helpers
from typing import Union, Optional
import plugins.Map.classes as c
import plugins.Map.data as data
import logging

def preprocess_item(item: Union[c.Prefab, RoadSection, c.Road]) -> Optional[Union[c.Prefab, RoadSection, c.Road]]:
    """Preprocess an item before using it for navigation"""
    try:
        if not item:
            logging.error("Cannot preprocess None item")
            return None

        if not isinstance(item, (c.Prefab, RoadSection, c.Road)):
            logging.error(f"Unknown item type for preprocessing: {type(item)}")
            return None

        # For prefabs, ensure they have nav_routes
        if isinstance(item, c.Prefab) and not hasattr(item, 'nav_routes'):
            logging.error(f"Prefab {item.uid} has no nav_routes")
            return None

        # For road sections, ensure they have lanes
        if isinstance(item, RoadSection) and not hasattr(item, 'lanes'):
            logging.error(f"Road section {item.uid} has no lanes")
            return None

        # For roads, ensure they have lanes and node UIDs
        if isinstance(item, c.Road):
            if not hasattr(item, '_lanes'):
                item._lanes = []  # Initialize the private lanes list

            # Ensure road_look is properly initialized
            if not item.road_look:
                from plugins.Map.data import map
                item.road_look = map.get_road_look_by_token(item.road_look_token)
                if not item.road_look:
                    logging.error(f"Road {item.uid} failed to get road_look for token {item.road_look_token}")
                    return None

            if not hasattr(item, 'start_node_uid') or not hasattr(item, 'end_node_uid'):
                logging.error(f"Road {item.uid} missing node UIDs")
                return None

            # Initialize nodes if not already done
            nodes = item.get_nodes()  # This will populate start_node and end_node
            if not nodes or None in nodes:
                logging.error(f"Road {item.uid} failed to initialize nodes")
                return None

            # Generate points and lanes if not already done
            if len(item._lanes) == 0:
                points = item.generate_points()  # Generate points first
                if not points:
                    logging.error(f"Road {item.uid} failed to generate points")
                    return None
                item.points = points  # Set the points

                # Now generate lanes with the road_look and points
                lanes, _ = road_helpers.GetRoadLanes(item, data)
                if not lanes:
                    logging.error(f"Road {item.uid} failed to generate lanes")
                    return None
                item._lanes = lanes

        return item
    except Exception as e:
        logging.error(f"Error preprocessing item: {e}", exc_info=True)
        return None
