"""Road point generation with proper DLC and hidden road checks."""
import logging
from typing import List, Optional, Dict, Any
from plugins.Map.utils.dlc_checker import DLCChecker
from plugins.Map.utils.settings_handler import SettingsHandler

logger = logging.getLogger('Map')

def check_road_access(road_data: Dict[str, Any]) -> bool:
    """
    Check if a road is accessible based on DLC and hidden status.

    Args:
        road_data: Dictionary containing road data

    Returns:
        bool: True if road is accessible, False otherwise
    """
    try:
        # Check if road is hidden
        if road_data.get('hidden', False):
            logging.debug(f"Road {road_data.get('uid', 'unknown')} is hidden")
            return False

        # Check DLC access
        dlc_id = road_data.get('dlc')
        if dlc_id is not None:
            if not DLCChecker.has_access(dlc_id):
                logging.debug(f"No access to DLC {dlc_id} for road {road_data.get('uid', 'unknown')}")
                return False

        return True
    except Exception as e:
        logging.error(f"Error checking road access: {e}")
        return False

def generate_road_points(road_data: Dict[str, Any]) -> Optional[List[Dict[str, float]]]:
    """
    Generate road points with proper access checks.

    Args:
        road_data: Dictionary containing road data

    Returns:
        Optional[List[Dict[str, float]]]: List of points or None if road is inaccessible
    """
    try:
        if not check_road_access(road_data):
            return None

        nodes = road_data.get('nodes', [])
        if not nodes:
            logging.error(f"No nodes found for road {road_data.get('uid', 'unknown')}")
            return None

        return [{'x': node['x'], 'y': node['y'], 'z': node['z']} for node in nodes]
    except Exception as e:
        logging.error(f"Error generating road points: {e}")
        return None

def generate_lanes(road_data: Dict[str, Any]) -> Optional[List[Dict[str, List[float]]]]:
    """
    Generate lanes for a road with proper checks.

    Args:
        road_data: Dictionary containing road data

    Returns:
        Optional[List[Dict[str, List[float]]]]: List of lane points or None if generation fails
    """
    try:
        if not check_road_access(road_data):
            return None

        points = generate_road_points(road_data)
        if not points:
            return None

        num_lanes = road_data.get('lanes', 2)
        lanes = []

        for i in range(num_lanes):
            lane_points = []
            for point in points:
                # Add lane offset calculation here
                lane_points.append([point['x'], point['y'], point['z']])
            lanes.append({'points': lane_points})

        return lanes
    except Exception as e:
        logging.error(f"Error generating lanes: {e}")
        return None
