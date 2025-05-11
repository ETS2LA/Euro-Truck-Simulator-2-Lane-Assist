import json
import math
import os
import logging
from Plugins.Map.utils import prefab_helpers, road_helpers
from Plugins.Map import data

CONFIG_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), 
    '../data/config.json'
))
logging.warning("Offset configuration path: %s", CONFIG_PATH)

def update_offset_config_generic(operation="add"):
    """Generic offset configuration updater for both add/sub operations"""
    prefix = "Sub: " if operation == "sub" else ""
    
    # Unified config initialization
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump({"offsets": {"per_name": {}}}, f)

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    logging.warning(f"{prefix}Configuration content: %s", config)
    updated = False
    distance_threshold = 0.1
    per_name = config['offsets']['per_name']
    updated_list = []

    # Unified road processing loop
    for road in data.current_sector_roads:
        if road.road_look.name in updated_list:
            logging.warning(f"{prefix}Already processed road: {road.road_look.name}")
            continue

        # Existing validation checks
        if not (hasattr(road, 'road_look') 
                and hasattr(road.road_look, 'name') 
                and road.road_look.name 
                and isinstance(road.road_look.name, str)):
            logging.warning(f"{prefix}Skipping invalid road object: {road}")
            continue

        # Unified item collection
        items = []
        if road.start_node and road.end_node:
            items = [
                data.map.get_item_by_uid(uid) for uid in [
                    road.start_node.forward_item_uid,
                    road.start_node.backward_item_uid,
                    road.end_node.forward_item_uid,
                    road.end_node.backward_item_uid
                ] if uid != road.uid
            ]

        # Unified distance calculation
        min_distance = math.inf
        sorted_distances = []
        for item in items:
            try:
                if item and hasattr(item, "nav_routes"):
                    item_distances = []
                    for lane in road.lanes:
                        try:
                            _, start_dist = prefab_helpers.get_closest_lane(item, lane.points[0].x, lane.points[0].z, True)
                            _, end_dist = prefab_helpers.get_closest_lane(item, lane.points[-1].x, lane.points[-1].z, True)
                            item_distances.extend([round(start_dist, 2), round(end_dist, 2)])
                            logging.warning(f"{prefix}Road: {road.road_look.name}, Distances: {start_dist}, {end_dist}")
                        except Exception as e:
                            logging.error(f"{prefix}Road: {road.road_look.name}, Distance calculation error: {str(e)}")
                    
                    if item_distances:
                        current_sorted = sorted(item_distances)
                        sorted_distances.extend(current_sorted)
                        current_min = sum(current_sorted[:2])
                        min_distance = min(min_distance, current_min)
                        logging.warning(f"{prefix}Road: {road.road_look.name}, Current min distance: {current_min}")
            except Exception as e:
                logging.error(f"{prefix}Error processing item: {str(e)}")

        # Unified offset calculation
        if (min_distance != math.inf and distance_threshold < min_distance < 1000) or not all(distance_threshold < md < 1000 for md in sorted_distances):
            current_offset = road_helpers.GetOffset(road)
            base_offset = min_distance
            logging.warning(f"{prefix}Road: {road.road_look.name}, Base offset: {base_offset}, Current offset: {current_offset}")
            if operation == "add":
                required_offset = current_offset + base_offset
                logging.warning(f"{prefix}Road: {road.road_look.name}, Adding offset: {required_offset}")
            else:
                required_offset = current_offset - base_offset
                logging.warning(f"{prefix}Road: {road.road_look.name}, Subtracting offset: {required_offset}")

            new_offset = round(required_offset, 2)
            if road.road_look.name not in per_name or per_name[road.road_look.name] != new_offset:
                per_name[road.road_look.name] = new_offset
                updated_list.append(road.road_look.name)
                logging.warning(f"{prefix}Updated offset for road: {road.road_look.name} to {new_offset}")
                updated = True

    # Unified config saving
    if updated:
        generate_rules(config)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    return updated

def generate_rules(config):
    """Generate rules based on patterns in per_name offsets"""
    
    per_name = config['offsets']['per_name']
    rules = config['offsets']['rules']
    
    pattern_stats = {}
    
    # Pattern discovery logic
    for name, offset in per_name.items():
        # Decompose road name into meaningful components
        parts = name.split()
        
        # Generate 3 types of pattern matches:
        # 1. Wildcard match for last segment (e.g. **shoulder)
        # 2. Wildcard match for last two segments (e.g. **city 0) 
        # 3. Special handling for offset roads (e.g. **offset 20m)
        patterns = [
            f"**{parts[-1]}",          # Match any road ending with last word
            f"**{' '.join(parts[-2:])}" # Match any road ending with last two words
        ]
        
        # Special case for offset measurements
        if 'offset' in name.lower():
            # Extract measurement-related terms (e.g. "offset", "20m", "3")
            offset_parts = [p for p in parts if p.lower() in ['offset', 'm']]
            if offset_parts:
                patterns.append(f"**{' '.join(offset_parts)}")
        
        # Aggregate offsets by pattern
        for pattern in patterns:
            pattern_stats.setdefault(pattern, []).append(offset)
    
    # Rule generation thresholds
    for pattern, offsets in pattern_stats.items():
        # Require at least 2 samples to create a rule
        if len(offsets) >= 2:  
            avg_offset = round(sum(offsets) / len(offsets), 2)
            existing = rules.get(pattern, 0)
            
            # Only update if difference exceeds 0.5m to avoid noise
            if abs(existing - avg_offset) > 0.5:
                rules[pattern] = avg_offset
                logging.warning(f"Updated rule: {pattern} = {avg_offset} (based on {len(offsets)} entries)")
    # Add this at the end to ensure rules get saved
    config['offsets']['rules'] = rules
    return config  # Return modified config


def update_offset_config_add():
    return update_offset_config_generic("add")

def update_offset_config_sub():
    return update_offset_config_generic("sub")

def update_offset_config():
    update_offset_config_sub()
    update_offset_config_add()
