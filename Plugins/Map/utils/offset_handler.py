"""
This module manages road offset configurations for a truck simulation map.
It provides functionality to calculate, validate, and update road offsets based on spatial relationships,
with caching mechanisms and configurable thresholds.
"""
# Caution!! Only enable dev logs if you know what you are doing, they are very verbose!
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
file_handler = logging.FileHandler(log_file, mode="w", encoding='utf-8')
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
distance_threshold = 0.1

# Add cache dictionaries
_distance_cache = {}
_processed_roads = set()
_road_name_to_uid = {}  # Cache for road name to UID

def _is_valid_offset(offset):
    """Validate if an offset value is within acceptable parameters.
    
    Args:
        offset (int/float): Value to validate
        
    Returns:
        bool: True if valid numerical value within [-100, 100] range
    """
    return (isinstance(offset, (int, float)) 
            and not math.isnan(offset) 
            and not math.isinf(offset)
            and -100 < offset < 100)

def _clean_invalid_offsets(config):
    """Remove invalid offset values from configuration.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        dict: Sanitized configuration with only valid offsets
    """
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
    """Main entry point for updating offset configurations.
    
    Args:
        operation (str): 'add' or 'sub' for offset operations
        allow_override (bool): Allow overriding existing offsets
        
    Returns:
        bool: True if any updates were made
    """
    prefix = "Sub: " if operation == "sub" else "Add: "
    
    # Clear caches
    _distance_cache.clear()
    _processed_roads.clear()
    
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump({"offsets": {"per_name": {}}}, f)

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    logger.warning(f"{prefix}Configuration content: %s", config)
    updated = False
    per_name = config['offsets']['per_name']
    
    roads = []
    fail = []
    for road in data.map.roads:
        if hasattr(road, 'road_look') and road.road_look and (road.road_look.name not in roads):
            roads.append(road.road_look.name)
        else:
            pass
    roads = sorted(roads)
    logger.warning(f"{prefix}: Roads to process: {roads}")

    # Reprocess unprocessed roads
    if roads:
        logger.warning(f"{prefix}Starting processing of {len(roads)} roads")
        reprocess_count = 0
        succeed = False
        
        for index, road_name in enumerate(roads , 1):
            # Find the actual road object with stricter validation
            try:
                road_uid = _road_name_to_uid.get(road_name)
                if road_uid:
                    road = data.map.get_item_by_uid(road_uid)  # Use cached UID if available
            except Exception as e:
                road = next((r for r in data.map.roads 
                            if hasattr(r, 'road_look') 
                            and hasattr(r.road_look, 'name') 
                            and r.road_look.name == road_name), None)  # Ensure exact name match
                logger.warning(f"\r{prefix}Error finding road by name '{road_name}': {str(e)}" )
            if not road:
                logger.warning(f"\r{prefix}Failed: Road '{road_name}' not found in data.map.roads")
                continue
            
            if not _is_valid_road(road):
                logger.warning(f"\r{prefix}Skipped: Invalid road '{road_name}'")
                continue

            # New：Collect all roads with the same name
            same_name_roads = [
                r for r in data.map.roads
                if hasattr(r, 'road_look') and r.road_look and r.road_look.name == road_name
            ]
            logger.warning(f"\r{prefix}Found {len(same_name_roads)} roads with name '{road_name}'")

            # If multiple roads share the same name, process each one
            for index,same_road in enumerate(same_name_roads, 1):
                # Log progress
                progress = (index / len(same_name_roads)) * 100
                if index % 100 == 0:
                    # Log every 100th road for performance
                    logger.warning(f"\r{prefix}Processing same name road {index}/{len(same_name_roads)} ({progress:.2f}%): {same_road.road_look.name}, uid={same_road.uid}")
                # Check if the road is valid
                if not _is_valid_road(same_road):
                    #logger.warning(f"\r{prefix}Skipped: Invalid road '{road_name}' (same name road)")
                    continue
                # Get connected items with fallback check
                connected_items = _get_connected_items(same_road, data.map)
                # if not connected_items:
                #     logger.warning(f"\r{prefix}Skipped: No connected items for '{road_name}'")

                # Calculate distances and check update condition
                min_distance, is_add, dist0 = _calculate_distances(same_road, connected_items)
                # if not _should_update_offset(min_distance, sorted_distances):
                #     logger.warning(f"\r{prefix}Skipped: Distance conditions not met for '{road_name}' (min_distance={min_distance})")

                # Attempt to update the offset
                if _update_road_offset(same_road, min_distance, dist0, per_name, operation, allow_override, prefix, is_add):
                    succeed = True
                    updated = True
                    _road_name_to_uid[road_name] = same_road.uid  # Cache the UID for future use
                    logger.warning(f"\r{prefix}Successfully processed road '{road_name}', uid={same_road.uid}")
                    #time.sleep(1)
                    break  # Break out of the loop if successful
                else:
                    #logger.warning(f"\r{prefix}Failed: Offset not updated for '{road_name}', uid={same_road.uid}")
                    succeed = False
            if succeed:
                reprocess_count += 1
                logger.warning(f"{prefix}Road '{road_name}' successfully, total: {reprocess_count}/{len(roads)}")
                continue  # Continue to next road if successful
            else:
                logger.warning(f"{prefix}Failed to process road '{road_name}'")
                fail.append(road_name)

        logger.warning(f"{prefix}Processed {reprocess_count}/{len(roads)} roads, failed {len(fail)} roads: {fail}")

    # Save configuration
    if updated:
        # Clean invalid offset values from the configuration
        config = _clean_invalid_offsets(config)

        # Sort per_name and rules before writing
        config['offsets']['per_name'] = dict(sorted(config['offsets']['per_name'].items()))

        # Open the configuration file in write mode and save the updated configuration
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
    """Get items connected to the road (only prefab map items)"""
    # Add import for Prefab class
    from Plugins.Map import classes as c
    road.get_nodes(map=map_data)
    if not (road.start_node and road.end_node):
        return []
        
    connected_prefabs = []
    uid_list = [
        road.start_node.forward_item_uid,
        road.start_node.backward_item_uid, 
        road.end_node.forward_item_uid,
        road.end_node.backward_item_uid
    ]
    total_uids = len(uid_list) # Always 4 UIDs
    
    for index, uid in enumerate(uid_list, 1):
        # Log progress
        progress = (index / total_uids) * 100
        #logger.warning(f"Checking connected UID {index}/{total_uids} ({progress:.1f}%): uid={uid}")
        
        if uid == road.uid:
            #logger.warning(f"Skipping self-reference UID: {uid}")
            continue  # Skip self-reference
            
        item = map_data.get_item_by_uid(uid)
        # logger.warning(f"Item is road: {item is not None and hasattr(item, 'road_look') and item.road_look is not None}, is prefab: {item is not None and isinstance(item, c.Prefab)}")
        if item and isinstance(item, c.Prefab):  # Only keep prefab items
            connected_prefabs.append(item)
            #logger.warning(f"Found valid prefab item: uid={uid}")
            
    return connected_prefabs

def _calculate_distances(road, items):
    """Calculate road distances (supports both prefabs and roads)"""
    cache_key = (road.uid, tuple(item.uid for item in items if item))
    if cache_key in _distance_cache:
        return _distance_cache[cache_key]

    min_distance = math.inf
    sorted_distances = []
    dist0 = False
    is_add = False
    
    for item in items:
        if not (item and hasattr(item, "nav_routes")):
            continue

        item_distances = _calculate_item_distances(road, item)
        if not item_distances:
            continue
            
        if len(road.lanes) > 1:
            current_sorted = sorted(item_distances)
            current_sorted = current_sorted[:len(road.lanes)]
            sorted_distances.extend(current_sorted)
            if all(distance <= 4.5 for distance in current_sorted):
                if len(road.lanes) > 2:
                    item_distances = item_distances[:max((len(road.lanes) // 2), 2)]
                    if item_distances[0] > item_distances[1]:
                        is_add = True
                    else:
                        is_add = False
                min_distance = min(min_distance, sum(current_sorted[:2]))
            else:
                min_distance = min(min_distance, sum(current_sorted[-2:]))
        else:
            current_min = min(item_distances)
            min_distance = min(min_distance, current_min * 2)
            
        dist0 |= any(d < distance_threshold for d in item_distances)
    
    # Sort distances and filter out invalid values
    if min_distance != math.inf and sorted_distances:
        #logger.warning(f"Calculated distances for road {road.road_look.name}: min_distance={min_distance}, sorted_distances={sorted_distances}, dist0={dist0}, is_add={is_add}")
        pass
    
    # 结果新增left_lanes字段（基于当前road）
    result = (min_distance, is_add, dist0)
    _distance_cache[cache_key] = result
    return result


def _calculate_item_distances(road, item):
    """Calculate distances for a single item (uses correct helper for prefabs/roads)"""
    item_distances = []
    lanes = road.lanes  
    total_lanes = len(lanes)  
    for index, lane in enumerate(lanes, 1):
            progress = (index / total_lanes) * 100
            #logger.warning(f"Calculating lane distance {index}/{total_lanes} ({progress:.1f}%): lane_uid={getattr(lane, 'uid', 'N/A')}")
            try:
                # Use prefab helper for prefabs, road helper for roads
                if hasattr(item, "nav_routes"):
                    _, start_dist = prefab_helpers.get_closest_lane(item, lane.points[0].x, lane.points[0].z, True)
                    _, end_dist = prefab_helpers.get_closest_lane(item, lane.points[-1].x, lane.points[-1].z, True)
                elif hasattr(item, "lanes"):
                    logger.warning(f"Connected to road {road.road_look.name} with item uid {item.uid}")
                    pass
                else:
                    continue  # Skip invalid item types

                item_distances.extend([round(start_dist, 2), round(end_dist, 2)])
            except Exception as e:
                logger.error(f"Error calculating distances for road {road.road_look.name}: {str(e)}")
    return item_distances

def _should_update_offset(min_distance, sorted_distances):
    """Determine if offset needs to be updated"""
    return (min_distance != math.inf and distance_threshold < min_distance < 50) or not all(distance_threshold < md < 50 for md in sorted_distances)

def _update_road_offset(road, min_distance, dist0, per_name, operation, allow_override, prefix, is_add):
    """Update road offset"""
    current_offset = road_helpers.GetOffset(road)
    if min_distance == math.inf:
        #logger.warning(f"{prefix}Road: {road.road_look.name}, No valid distance found, skipping offset update")
        return False
    base_offset = min_distance
    #logger.warning(f"{prefix}Road: {road.road_look.name}, Base offset: {base_offset}, Current offset: {current_offset}")
    if operation == "add":
        required_offset = current_offset + base_offset
        #logger.warning(f"{prefix}Road: {road.road_look.name}, Adding offset: {required_offset}")
    else:
        # New: If current offset is >4.5, use add logic
        if is_add:
            required_offset = current_offset + base_offset
            logger.warning(f"{prefix}Road: {road.road_look.name} has offset > 4.5, using add logic: {current_offset} + {base_offset} = {required_offset}")
        else:
            # Changed from 2 * base_offset to base_offset only
            required_offset = current_offset - base_offset  # Corrected line
            #logger.warning(f"{prefix}Road: {road.road_look.name}, Subtracting offset: {required_offset}")

    new_offset = round(required_offset * 4) / 4  # Round to 0.25 precision
    if road.road_look.name not in per_name:
        per_name[road.road_look.name] = new_offset
    elif per_name[road.road_look.name] != new_offset:
        if operation == "sub" or allow_override:
            old_offset = per_name[road.road_look.name]
            per_name[road.road_look.name] = new_offset
            logger.warning(f"{prefix}Overriding existing offset: {road.road_look.name} {old_offset} -> {new_offset}")
        else:
            logger.warning(f"{prefix}Keeping existing offset for {road.road_look.name} -> {per_name[road.road_look.name]}")
    else:
        logger.warning(f"{prefix}E Keeping existing offset for {road.road_look.name} -> {per_name[road.road_look.name]}")
    return True

def generate_rules(config):
    """Generate pattern - based offset rules from per - name configurations.
    
    Args:
        config (dict): Current configuration
        
    Returns:
        dict: Modified configuration with generated rules
    """
    
    per_name = config['offsets']['per_name']
    rules = config['offsets'].setdefault('rules', {})
    
    logger.warning(f"Starting rule generation, current per_name entries: {len(per_name)}")
    
    # Add all roads with their actual offsets from GetOffset
    all_road_offsets = {}
    for road in data.map.roads:
        if not hasattr(road, 'road_look') or not road.road_look:
            continue
            
        # Create a mock road object for GetOffset
        mock_road = type('Road', (), {
            'road_look': type('RoadLook', (), {
                'name': road.road_look.name,
                'offset': road.road_look.offset  # use actual offset
            })
        })()
        all_road_offsets[road.road_look.name] = road_helpers.GetOffset(mock_road)
    
    combined_roads = {**per_name, **all_road_offsets}
    logger.warning(f"Combined road: {combined_roads}")
    logger.warning(f"Total roads with offsets: {len(combined_roads)}")
    
    def _get_most_common_offset(offset_counts):
        """Get the most common offset with highest count"""
        if not offset_counts:
            return None, 0
        max_offset = max(offset_counts.items(), key=lambda x: (x[1], -abs(x[0])))  # Prefer smaller absolute values
        return max_offset[0], max_offset[1]

    def generate_patterns(names_dict, word_count):
        """Create wildcard patterns from road name suffixes.
        
        Args:
            names_dict (dict): Dictionary of road names and their offsets
            word_count (int): Number of words to use from the end of road names
            
        Returns:
            dict: A mapping of patterns to their offset frequencies
        """
        pattern_map = {}
        for name, offset in names_dict.items():
            if not _is_valid_offset(offset):
                continue
            
            words = name.split()
            if len(words) >= word_count:
                # Take last 'word_count' words to create pattern
                pattern = f"**{' '.join(words[-word_count:])}"
                if pattern not in pattern_map:
                    pattern_map[pattern] = {}
                pattern_map[pattern][offset] = pattern_map[pattern].get(offset, 0) + 1
        return pattern_map

    def _is_number_only(pattern):
        """Check if pattern only contains numbers (excluding **)
        
        Args:
            pattern (str): The pattern to check
            
        Returns:
            bool: True if pattern contains only numbers after removing '**' prefix
        """
        suffix = pattern[3:]  # Remove ** prefix
        # Remove spaces and check if remaining chars are digits
        return suffix.replace(" ", "").isdigit()

    # Process rules with combined roads
    unmatched = dict(combined_roads)
    final_rules = {}
    matched_with_same_offset = set()
    
    # Generate rules in two rounds
    for word_count in [2, 3]:
        if not unmatched:
            break
            
        patterns = generate_patterns(unmatched, word_count)
        if not patterns:
            continue
            
        logger.warning(f"Round {word_count}: Generated {len(patterns)} patterns")
        
        # Find best patterns
        round_rules = {}
        for pattern, offset_counts in patterns.items():
            if _is_number_only(pattern):
                logger.warning(f"Skipping number - only pattern: {pattern}")
                continue
                
            offset, count = _get_most_common_offset(offset_counts)
            # Change to 100% match
            match_threshold = 1
            if offset is not None and count / len(offset_counts) >= match_threshold:
                round_rules[pattern] = offset
                logger.warning(f"Rule found - Pattern: {pattern}, Offset: {offset}, Count: {count}, Total: {len(offset_counts)}")
        
        # Apply rules and update unmatched
        matched = set()
        for name, offset in unmatched.items():
            name_words = set(name.split())
            for pattern, rule_offset in round_rules.items():
                # Remove ** prefix and split into word sets
                pattern_words = set(pattern[2:].split())
                # Check if all words in the rule are in the road name
                if pattern_words.issubset(name_words) and abs(rule_offset - offset) <= 0.01:
                    matched.add(name)
                    matched_with_same_offset.add(name)
                    break
        
        final_rules.update(round_rules)
        unmatched = {name: offset for name, offset in unmatched.items() if name not in matched}
        logger.warning(f"Round {word_count} complete - Matched: {len(matched)}, Same offset matches: {len(matched_with_same_offset)}")

    # Merge rules with the same offset and same words
    merged_rules = {}
    patterns_by_offset = {}
    
    # Group rules by offset
    for pattern, offset in final_rules.items():
        if offset not in patterns_by_offset:
            patterns_by_offset[offset] = []
        patterns_by_offset[offset].append(pattern)
    
    # Merge rules within each offset group
    for offset, patterns in patterns_by_offset.items():
        # Group by word set
        word_groups = {}
        for pattern in patterns:
            # Remove ** prefix and split into word list
            words = pattern[2:].split()
            # Use a tuple to store the word list to maintain order
            key = tuple(words)
            if key not in word_groups:
                word_groups[key] = []
            word_groups[key].append(pattern)
        
        # Merge rules with the same word sequence
        for words, similar_patterns in word_groups.items():
            if len(similar_patterns) > 1:
                # Find the shortest pattern as the baseline
                base_pattern = min(similar_patterns, key=len)
                # Create a test road name (remove ** prefix)
                test_name = base_pattern[2:]
                
                # Create a mock road object
                mock_road = type('Road', (), {
                    'road_look': type('RoadLook', (), {
                        'name': test_name,
                        'offset': 0  # Use default offset
                    })
                })()
                
                # Calculate offset using GetOffset
                get_offset_result = road_helpers.GetOffset(mock_road)
                
                # If the result of GetOffset is different from the rule offset, keep the rule
                if abs(get_offset_result - offset) > 0.01:
                    logger.warning(f"Merging patterns with same words and offset {offset}: {similar_patterns} -> {base_pattern}")
                    merged_rules[base_pattern] = offset
                else:
                    logger.warning(f"Skipping rule {base_pattern} as it can be represented by GetOffset")
            else:
                # Check GetOffset for single patterns
                test_name = similar_patterns[0][2:]
                mock_road = type('Road', (), {
                    'road_look': type('RoadLook', (), {
                        'name': test_name,
                        'offset': 0
                    })
                })()
                
                get_offset_result = road_helpers.GetOffset(mock_road)
                
                if abs(get_offset_result - offset) > 0.01:
                    merged_rules[similar_patterns[0]] = offset
                else:
                    logger.warning(f"Skipping rule {similar_patterns[0]} as it can be represented by GetOffset")
    
    # Update rules and sort alphabetically and by absolute value
    rules.clear()
    rules.update(merged_rules)
    rules = dict(sorted(rules.items(), key=lambda item: (item[0], abs(item[1]))))
    
    # Remove entries with the same offset that are also in per_name
    to_remove = matched_with_same_offset & set(per_name.keys())
    for name in to_remove:
        del per_name[name]
    
    logger.warning(f"Rule generation complete - Total rules after merging: {len(rules)}")
    logger.warning(f"Matched entries with same offset: {len(matched_with_same_offset)}, Removed from per_name: {len(to_remove)}")
    logger.warning(f"Entries removed from per_name: {to_remove}")
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
    return config

def clear_lane_offsets(clear):
    """Clear all lane offsets from the config"""
    logger.warning("Clearing all lane offsets")

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
        if clear == "rules":
            # Clear only rules
            config['offsets']['rules'] = {}
            logger.warning("Cleared all rules")
        else:
            config['offsets']['per_name'] = {}
            logger.warning("Cleared all per_name")
    
    # Ensure no invalid values before saving config
    config = _clean_invalid_offsets(config)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
    
    logger.warning("Cleared all lane offsets")
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
    map_main.Plugin.update_road_data(self=True)
    logger.warning("Timeout for 3 seconds to allow for road data update")
    time.sleep(3)
    # Perform addition operation and update configuration
    update_offset_config_add()
    logger.warning("Addition operation completed")
    # Call update_road_data and wait for completion
    map_main.Plugin.update_road_data(self=True)
    logger.warning("update_road_data completed")
    # Perform addition operation (at this point road_helpers.GetOffset will get the new value after addition)
    logger.warning("Timeout for 3 seconds to allow for road data update")
    time.sleep(3)
    update_offset_config_sub()
    logger.warning("Subtraction operation completed")
    map_main.Plugin.update_road_data(self=True)
