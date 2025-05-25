import json
import math
import os
import logging
import time
from Plugins.Map.utils import prefab_helpers, road_helpers
from Plugins.Map import data
from Plugins.Map import main as map_main
from ETS2LA import variables

# Add logging configuration
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

# Configure logger
logger = logging.getLogger("offset_handler")
logger.setLevel(logging.INFO)

# Create file handler
log_file = os.path.join(LOG_PATH, "offset_handler.log")
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Set log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)

CONFIG_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), 
    '../data/config.json'
))

if variables.DEVELOPMENT_MODE:
    logger.info("Offset configuration path: %s", CONFIG_PATH)

# Key parameters!!!
# distance_threshold: Distance threshold in meters
distance_threshold = 0.25

# Add cache dictionaries
_distance_cache = {}
_processed_roads = set()

# Add global skip list for roads that don't need override
_skip_roads = set()

def _is_valid_offset(offset):
    """Validate if offset value is valid"""
    return (isinstance(offset, (int, float)) 
            and not math.isnan(offset) 
            and not math.isinf(offset)
            and -1000 < offset < 1000)  # Add reasonable range limit

def _clean_invalid_offsets(config):
    """Clean invalid offset values from configuration"""
    per_name = config['offsets']['per_name']
    # Filter invalid offset values
    valid_offsets = {
        name: offset for name, offset in per_name.items()
        if _is_valid_offset(offset)
    }
    
    removed = len(per_name) - len(valid_offsets)
    if removed > 0:
        logger.warning(f"Removed {removed} invalid offsets from config")
        
    config['offsets']['per_name'] = valid_offsets
    return config

def update_offset_config_generic(operation="add", allow_override=False):
    """Generic offset configuration updater for both add/sub operations"""
    prefix = "Sub: " if operation == "sub" else "Add: "
    
    # Clear caches
    _distance_cache.clear()
    _processed_roads.clear()
    if operation == "add":  # Only clear skip list when starting a new add/sub cycle
        _skip_roads.clear()
    
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump({"offsets": {"per_name": {}}}, f)

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    logger.warning(f"{prefix}Configuration content: %s", config)
    updated = False
    per_name = config['offsets']['per_name']

    # Preprocess all road data
    total_roads = len(data.map.roads)
    batch_size = 100  # Batch processing size
    
    for i in range(0, total_roads, batch_size):
        batch = data.map.roads[i:i+batch_size]
        if i % (batch_size * 10) == 0:  # Log progress every 10 batches
            logging.warning(f"{prefix}Processing batch {i//batch_size + 1}: {i}/{total_roads} roads ({(i/total_roads*100):.1f}%)")
        
        # Batch process roads
        for road in batch:
            if not _is_valid_road(road):
                continue
                
            if road.road_look.name in _processed_roads or road.road_look.name in _skip_roads:
                # logger.warning(f"{prefix}Skipping road {road.road_look.name} (in skip list)")
                continue
                
            _processed_roads.add(road.road_look.name)
            
            # Get items connected to the road
            connected_items = _get_connected_items(road, data.map)
            if not connected_items:
                continue

            # Calculate distances
            min_distance, sorted_distances, dist0 = _calculate_distances(road, connected_items)
            
            # Handle offset
            if _should_update_offset(min_distance, sorted_distances):
                updated |= _update_road_offset(road, min_distance, dist0, per_name, operation, allow_override, prefix)

    # Save configuration
    if updated:
        config = _clean_invalid_offsets(config)
        generate_rules(config)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
            
    logger.warning(f"{prefix}Final processing complete, updated: {updated}")
    return updated

def _is_valid_road(road):
    """Validate if road object is valid"""
    return (hasattr(road, 'road_look') 
            and hasattr(road.road_look, 'name') 
            and road.road_look.name 
            and isinstance(road.road_look.name, str))

def _get_connected_items(road, map_data):
    """Get items connected to the road"""
    road.get_nodes(map=map_data)
    if not (road.start_node and road.end_node):
        return []
        
    return [
        map_data.get_item_by_uid(uid) for uid in [
            road.start_node.forward_item_uid,
            road.start_node.backward_item_uid, 
            road.end_node.forward_item_uid,
            road.end_node.backward_item_uid
        ] if uid != road.uid
    ]

def _calculate_distances(road, items):
    """Calculate road distances"""
    cache_key = (road.uid, tuple(item.uid for item in items if item))
    if cache_key in _distance_cache:
        return _distance_cache[cache_key]
        
    min_distance = math.inf
    sorted_distances = []
    dist0 = False
    
    for item in items:
        if not (item and hasattr(item, "nav_routes")):
            continue
            
        item_distances = _calculate_item_distances(road, item)
        if not item_distances:
            continue
            
        if len(road.lanes) > 1:
            current_sorted = sorted(item_distances)
            sorted_distances.extend(current_sorted)
            min_distance = min(min_distance, sum(current_sorted[:2]))
        else:
            current_min = min(item_distances)
            min_distance = min(min_distance, current_min * 2)
            
        dist0 |= any(d < distance_threshold for d in item_distances)
    
    result = (min_distance, sorted_distances, dist0)
    _distance_cache[cache_key] = result
    return result

def _calculate_item_distances(road, item):
    """Calculate distances for a single item"""
    item_distances = []
    for lane in road.lanes:
        try:
            _, start_dist = prefab_helpers.get_closest_lane(item, lane.points[0].x, lane.points[0].z, True)
            _, end_dist = prefab_helpers.get_closest_lane(item, lane.points[-1].x, lane.points[-1].z, True)
            item_distances.extend([round(start_dist, 2), round(end_dist, 2)])
        except Exception as e:
            logger.error(f"Error calculating distances for road {road.road_look.name}: {str(e)}")
    return item_distances

def _should_update_offset(min_distance, sorted_distances):
    """Determine if offset needs to be updated"""
    return (min_distance != math.inf and distance_threshold < min_distance < 50) or not all(distance_threshold < md < 50 for md in sorted_distances)

def _update_road_offset(road, min_distance, dist0, per_name, operation, allow_override, prefix):
    """Update road offset"""
    current_offset = road_helpers.GetOffset(road)
    base_offset = min_distance
    logger.warning(f"{prefix}Road: {road.road_look.name}, Base offset: {base_offset}, Current offset: {current_offset}")
    if operation == "add":
        required_offset = current_offset + base_offset
        logger.warning(f"{prefix}Road: {road.road_look.name}, Adding offset: {required_offset}")
    else:
        required_offset = current_offset - base_offset
        logger.warning(f"{prefix}Road: {road.road_look.name}, Subtracting offset: {required_offset}")

    new_offset = round(required_offset, 2)
    if dist0:
        logger.warning(f"{prefix}No override necessary for {road.road_look.name}")
        _skip_roads.add(road.road_look.name)  # Add to skip list
        return True
    elif road.road_look.name not in per_name:
        per_name[road.road_look.name] = new_offset
        return True
    elif per_name[road.road_look.name] != new_offset:
        if operation == "add" or allow_override:
            old_offset = per_name[road.road_look.name]
            per_name[road.road_look.name] = new_offset
            logger.warning(f"{prefix}Overriding existing offset: {road.road_look.name} {old_offset} -> {new_offset}")
            return True
        else:
            logger.warning(f"{prefix}Keeping existing offset for {road.road_look.name} -> {per_name[road.road_look.name]}")
    else:
        logger.warning(f"{prefix}Keeping existing offset for {road.road_look.name} -> {per_name[road.road_look.name]}")
    return False

def generate_rules(config):
    """Generate rules based on patterns in per_name offsets"""
    
    per_name = config['offsets']['per_name']
    rules = config['offsets']['rules']
    
    # 用于存储每种模式对应的偏移值
    pattern_offsets = {}
    
    # 生成 ** 和 *** 模式
    for name, offset in per_name.items():
        # 跳过无效的offset值
        if not isinstance(offset, (int, float)) or math.isnan(offset) or math.isinf(offset):
            logger.warning(f"Skipping invalid offset value for {name}: {offset}")
            continue

        # 生成 ** 模式
        words = name.split()
        for word in words:
            pattern_double_star = f"**{word}"
            if pattern_double_star not in pattern_offsets:
                pattern_offsets[pattern_double_star] = set()
            pattern_offsets[pattern_double_star].add(offset)

        # 生成 *** 模式
        for i in range(len(words)):
            end_part = " ".join(words[i:])
            pattern_triple_star = f"***{end_part}"
            if pattern_triple_star not in pattern_offsets:
                pattern_offsets[pattern_triple_star] = set()
            pattern_offsets[pattern_triple_star].add(offset)

    # 过滤出所有偏移值相同的模式
    valid_patterns = {}
    for pattern, offsets in pattern_offsets.items():
        if len(offsets) == 1:
            valid_patterns[pattern] = offsets.pop()

    # 确保 ** 和 *** 规则不冲突，优先保留 *** 规则
    final_rules = {}
    for pattern, offset in valid_patterns.items():
        if pattern.startswith("***"):
            # 检查规则是否与 per_name 完全相同
            if not any(name.endswith(pattern[3:]) and per_name[name] == offset for name in per_name):
                final_rules[pattern] = offset
        else:
            conflict = False
            for triple_star_pattern in [p for p in valid_patterns if p.startswith("***")]:
                if pattern[2:] in triple_star_pattern[3:]:
                    conflict = True
                    break
            if not conflict:
                # 检查规则是否与 per_name 完全相同
                if not any(pattern[2:] in name and per_name[name] == offset for name in per_name):
                    final_rules[pattern] = offset

    # 删除能被规则表示的 per_name 路段
    per_name_to_remove = []
    for name, offset in per_name.items():
        for pattern, rule_offset in final_rules.items():
            if pattern.startswith("**") and pattern[2:] in name and rule_offset == offset:
                per_name_to_remove.append(name)
                break
            elif pattern.startswith("***") and name.endswith(pattern[3:]) and rule_offset == offset:
                per_name_to_remove.append(name)
                break

    for name in per_name_to_remove:
        del per_name[name]

    # 更新规则
    rules.update(final_rules)
    config['offsets']['rules'] = rules

    # 打印前检查规则的有效性
    valid_rules = {k: v for k, v in rules.items() if isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v)}
    logger.warning(f"Generated valid rules: {valid_rules}")
    logging.warning(f"Generated valid rules: {valid_rules}")
    return config

def clear_lane_offsets():
    """Clear all lane offsets from the config"""
    logger.warning("Clearing all lane offsets")
    logging.warning("Clearing all lane offsets")

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
        config['offsets']['per_name'] = {}
        config['offsets']['rules'] = {}  # Clear rules as well
    
    # Ensure no invalid values before saving config
    config = _clean_invalid_offsets(config)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
    
    logger.warning("Cleared all lane offsets")
    logging.warning("Cleared all lane offsets")
    map_main.Plugin.update_road_data(self=True)

def update_offset_config_add():
    override = data.override_lane_offsets
    return update_offset_config_generic("add", override)

def update_offset_config_sub():
    override = data.override_lane_offsets
    return update_offset_config_generic("sub", override)

def update_offset_config():
    override = data.override_lane_offsets
    logger.warning("Override lane offsets: %s", override)
    logging.warning("Override lane offsets: %s", override)
    map_main.Plugin.update_road_data(self=True)
    logger.warning("Timeout for 3 seconds to allow for road data update")
    logging.warning("Timeout for 3 seconds to allow for road data update")
    time.sleep(3)
    # Perform subtraction operation and update configuration
    update_offset_config_add()
    logger.warning("Subtraction operation completed")
    logging.warning("Subtraction operation completed")
    # Call update_road_data and wait for completion
    map_main.Plugin.update_road_data(self=True)
    logger.warning("update_road_data completed")
    logging.warning("update_road_data completed")
    # Perform addition operation (at this point road_helpers.GetOffset will get the new value after subtraction)
    logger.warning("Timeout for 3 seconds to allow for road data update")
    logging.warning("Timeout for 3 seconds to allow for road data update")
    time.sleep(3)
    update_offset_config_sub()
    logger.warning("Addition operation completed")
    logging.warning("Addition operation completed")
    map_main.Plugin.update_road_data(self=True)

