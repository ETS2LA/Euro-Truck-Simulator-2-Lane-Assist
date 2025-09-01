"""
This module manages road offset configurations for a truck simulation map.
It provides functionality to calculate, validate, and update road offsets based on spatial relationships,
with caching mechanisms and configurable thresholds.
"""

# Caution!! Only enable dev logs if you know what you are doing, they are very verbose!
# DO NOT DELETE LOGS, THEY ARE LEFT HERE IN PURPOSE!!!
import json
import math
import os
import logging
import time
import re
from collections import defaultdict, Counter
from Plugins.Map.utils import prefab_helpers, road_helpers
from Plugins.Map import data
from Plugins.Map import main as map_main
from ETS2LA import variables

# Add logging configuration
LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs"
)
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

# Configure logger
logger = logging.getLogger("offset_handler")
logger.setLevel(logging.INFO)

# Create file handler
log_file = os.path.join(LOG_PATH, "offset_handler.log")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Set log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)

CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../data/config.json")
)

if variables.DEVELOPMENT_MODE:
    logger.info("Offset configuration path: %s", CONFIG_PATH)

# Key parameters!!!
# distance_threshold: Distance threshold in meters
distance_threshold = 0.25

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
    return (
        isinstance(offset, (int, float))
        and not math.isnan(offset)
        and not math.isinf(offset)
        and -100 < offset < 100
    )


def _clean_invalid_offsets(config):
    """Remove invalid offset values from configuration.

    Args:
        config (dict): Configuration dictionary

    Returns:
        dict: Sanitized configuration with only valid offsets
    """
    per_name = config["offsets"]["per_name"]
    # Filter invalid offset values
    valid_offsets = {
        name: offset for name, offset in per_name.items() if _is_valid_offset(offset)
    }

    removed = len(per_name) - len(valid_offsets)
    if removed > 0:
        logger.warning(f"Removed {removed} invalid offsets from config")

    config["offsets"]["per_name"] = valid_offsets
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
        with open(CONFIG_PATH, "w") as f:
            json.dump({"offsets": {"per_name": {}}}, f)

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    logger.info(f"{prefix}Configuration content: %s", config)
    updated = False
    per_name = config["offsets"]["per_name"]

    roads = []
    fail = []
    for road in data.map.roads:
        if (
            hasattr(road, "road_look")
            and road.road_look
            and (road.road_look.name not in roads)
        ):
            roads.append(road.road_look.name)
        else:
            pass
    roads = sorted(roads)
    logger.info(f"{prefix}: Roads to process: {roads}")

    # Reprocess unprocessed roads
    if roads:
        logger.warning(f"{prefix}Starting processing of {len(roads)} roads")
        reprocess_count = 0
        succeed = False

        for index, road_name in enumerate(roads, 1):
            # Find the actual road object with stricter validation
            try:
                road_uid = _road_name_to_uid.get(road_name)
                if road_uid:
                    road = data.map.get_item_by_uid(
                        road_uid
                    )  # Use cached UID if available
            except Exception as e:
                road = next(
                    (
                        r
                        for r in data.map.roads
                        if hasattr(r, "road_look")
                        and hasattr(r.road_look, "name")
                        and r.road_look.name == road_name
                    ),
                    None,
                )  # Ensure exact name match
                logger.info(
                    f"{prefix}Error finding road by name '{road_name}': {str(e)}"
                )
            if not road:
                logger.info(
                    f"{prefix}Failed: Road '{road_name}' not found in data.map.roads"
                )
                continue

            if not _is_valid_road(road):
                logger.warning(f"{prefix}Skipped: Invalid road '{road_name}'")
                continue

            # New：Collect all roads with the same name
            same_name_roads = [
                r
                for r in data.map.roads
                if hasattr(r, "road_look")
                and r.road_look
                and r.road_look.name == road_name
            ]
            logger.info(
                f"{prefix}Found {len(same_name_roads)} roads with name '{road_name}'"
            )

            # If multiple roads share the same name, process each one
            for index, same_road in enumerate(same_name_roads, 1):
                # Log progress
                # progress = (index / len(same_name_roads)) * 100
                if index % 100 == 0:
                    # Log every 100th road for performance
                    # logger.warning(f"\r{prefix}Processing same name road {index}/{len(same_name_roads)} ({progress:.2f}%): {same_road.road_look.name}, uid={same_road.uid}")
                    pass
                # Check if the road is valid
                if not _is_valid_road(same_road):
                    # logger.warning(f"\r{prefix}Skipped: Invalid road '{road_name}' (same name road)")
                    continue
                # Get connected items with fallback check
                connected_items = _get_connected_items(same_road, data.map)
                # if not connected_items:
                #     logger.warning(f"\r{prefix}Skipped: No connected items for '{road_name}'")

                # Calculate distances and check update condition
                min_distance, is_add, dist0 = _calculate_distances(
                    same_road, connected_items
                )
                # if not _should_update_offset(min_distance, sorted_distances):
                #     logger.warning(f"\r{prefix}Skipped: Distance conditions not met for '{road_name}' (min_distance={min_distance})")

                # Attempt to update the offset
                if _update_road_offset(
                    same_road,
                    min_distance,
                    dist0,
                    per_name,
                    operation,
                    allow_override,
                    prefix,
                    is_add,
                ):
                    succeed = True
                    updated = True
                    _road_name_to_uid[road_name] = (
                        same_road.uid
                    )  # Cache the UID for future use
                    logger.info(
                        f"{prefix}Successfully processed road '{road_name}', uid={same_road.uid}"
                    )
                    # time.sleep(1)
                    break  # Break out of the loop if successful
                else:
                    if index == len(same_name_roads):
                        # logger.info(f"{prefix}Failed: Offset not updated for '{road_name}', uid={same_road.uid}")
                        pass
                    succeed = False
            if succeed:
                reprocess_count += 1
                # if reprocess_count % 10 == 0:
                #     # Log every 10th road for performance
                #     pass
                logger.warning(
                    f"{prefix}Road calculation successful, total: {reprocess_count}/{len(roads)}"
                )
                logger.info(
                    f"{prefix}Road '{road_name}' successfully, total: {reprocess_count}/{len(roads)}"
                )
                continue  # Continue to next road if successful
            else:
                logger.info(f"{prefix}Failed to process road '{road_name}'")
                fail.append(road_name)

        logger.warning(
            f"{prefix}Processed {reprocess_count}/{len(roads)} roads, failed {len(fail)} roads: {fail}"
        )

    # Save configuration
    if updated:
        # Clean invalid offset values from the configuration
        config = _clean_invalid_offsets(config)

        # Filter out failed roads from per_name
        per_name = {
            name: offset for name, offset in per_name.items() if name not in fail
        }
        config["offsets"]["per_name"] = per_name

        # Sort per_name and rules before writing
        config["offsets"]["per_name"] = dict(
            sorted(config["offsets"]["per_name"].items())
        )

        # Open the configuration file in write mode and save the updated configuration
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)

    logger.warning(f"{prefix}Final processing complete, updated: {updated}")
    return updated


def _is_valid_road(road):
    """Validate if road object is valid"""
    return (
        hasattr(road, "road_look")
        and hasattr(road.road_look, "name")
        and road.road_look.name
        and isinstance(road.road_look.name, str)
    )


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
        road.end_node.backward_item_uid,
    ]
    # total_uids = len(uid_list) # Always 4 UIDs

    for index, uid in enumerate(uid_list, 1):
        # Log progress
        # progress = (index / total_uids) * 100
        # logger.warning(f"Checking connected UID {index}/{total_uids} ({progress:.1f}%): uid={uid}")

        if uid == road.uid:
            # logger.warning(f"Skipping self-reference UID: {uid}")
            continue  # Skip self-reference

        item = map_data.get_item_by_uid(uid)
        # logger.warning(f"Item is road: {item is not None and hasattr(item, 'road_look') and item.road_look is not None}, is prefab: {item is not None and isinstance(item, c.Prefab)}")
        if item and isinstance(item, c.Prefab):  # Only keep prefab items
            connected_prefabs.append(item)
            # logger.warning(f"Found valid prefab item: uid={uid}")

    return connected_prefabs


def _calculate_distances(road, items):
    """Calculate road distances (supports both prefabs and roads)"""
    cache_key = (road.uid, tuple(item.uid for item in items if item))
    if cache_key in _distance_cache:
        return _distance_cache[cache_key]

    min_distance = math.inf
    sorted_distances = []
    current_sorted = []
    filtered = []
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
            current_sorted = current_sorted[: len(road.lanes)]
            sorted_distances.extend(current_sorted)
            if all(distance < 4.5 / 2 for distance in current_sorted):
                if len(road.lanes) > 2:
                    # New: Detect the size of the first two items and filter odd/even indices
                    if len(item_distances) >= 2:
                        first = item_distances[0]
                        second = item_distances[1]
                        if first > second:
                            # Keep odd indices (1,3,5...)
                            filtered = [
                                item_distances[i]
                                for i in range(1, len(item_distances), 2)
                            ]
                        else:
                            # Keep even indices (0,2,4...)
                            filtered = [
                                item_distances[i]
                                for i in range(0, len(item_distances), 2)
                            ]
                    else:
                        filtered = item_distances  # Do not process if there are less than two items
                    if any(distance == 0 for distance in filtered):
                        filtered = filtered[:-2]
                    if filtered[0] >= filtered[-1]:
                        is_add = True
                    else:
                        is_add = False
                min_distance = min(min_distance, sum(filtered[:2]))
            else:
                min_distance = min(min_distance, sum(current_sorted[-2:]))
        else:
            current_min = min(item_distances)
            min_distance = min(min_distance, current_min * 2)
        logger.info(
            f"road: {road.road_look.name}, item_distances: {item_distances}, current_sorted: {current_sorted}, filtered: {filtered}, lane={len(road.lanes)}, is_add={is_add}"
        )

    # New: If all distances are equal to 2.25, set is_add to True
    if sorted_distances and all(distance == 2.25 for distance in sorted_distances):
        is_add = True

    # Sort distances and filter out invalid values
    if min_distance != math.inf and sorted_distances:
        logger.info(
            f"Calculated distances for road {road.road_look.name}: min_distance={min_distance}, sorted_distances={sorted_distances}, dist0={dist0}, is_add={is_add}"
        )
        pass

    # The result adds the left_lanes field (based on the current road)
    result = (min_distance, is_add, dist0)
    _distance_cache[cache_key] = result
    return result


def _calculate_item_distances(road, item):
    """Calculate distances for a single item (uses correct helper for prefabs/roads)"""
    item_distances = []
    lanes = road.lanes
    # total_lanes = len(lanes)
    for index, lane in enumerate(lanes, 1):
        # progress = (index / total_lanes) * 100
        # logger.warning(f"Calculating lane distance {index}/{total_lanes} ({progress:.1f}%): lane_uid={getattr(lane, 'uid', 'N/A')}")
        try:
            # Use prefab helper for prefabs, road helper for roads
            if hasattr(item, "nav_routes"):
                _, start_dist = prefab_helpers.get_closest_lane(
                    item, lane.points[0].x, lane.points[0].z, True
                )
                _, end_dist = prefab_helpers.get_closest_lane(
                    item, lane.points[-1].x, lane.points[-1].z, True
                )
            elif hasattr(item, "lanes"):
                # logger.warning(f"Connected to road {road.road_look.name} with item uid {item.uid}")
                pass
            else:
                continue  # Skip invalid item types

            item_distances.extend([round(start_dist, 2), round(end_dist, 2)])
        except Exception as e:
            logger.info(
                f"Error calculating distances for road {road.road_look.name}: {str(e)}"
            )
    return item_distances


def _should_update_offset(min_distance, sorted_distances):
    """Determine if offset needs to be updated"""
    return (
        min_distance != math.inf and distance_threshold < min_distance < 50
    ) or not all(distance_threshold < md < 50 for md in sorted_distances)


def _update_road_offset(
    road, min_distance, dist0, per_name, operation, allow_override, prefix, is_add
):
    """Update road offset"""
    current_offset = road_helpers.GetOffset(road)
    if min_distance == math.inf:
        # logger.error(f"{prefix}Road: {road.road_look.name}, No valid distance found, skipping offset update")
        return False
    base_offset = min_distance
    # logger.warning(f"{prefix}Road: {road.road_look.name}, Base offset: {base_offset}, Current offset: {current_offset}")
    if operation == "add":
        required_offset = current_offset + base_offset
        # logger.warning(f"{prefix}Road: {road.road_look.name}, Adding offset: {current_offset} + {base_offset} = {required_offset}")
    else:
        # New: If current offset is >4.5, use add logic
        if is_add:
            required_offset = current_offset + base_offset
            # logger.warning(f"{prefix}Road: {road.road_look.name} has offset > 4.5, using add logic: {current_offset} + {base_offset} = {required_offset}")
        else:
            # Changed from 2 * base_offset to base_offset only
            required_offset = current_offset - base_offset  # Corrected line
            # logger.warning(f"{prefix}Road: {road.road_look.name}, Subtracting offset: {current_offset} - {base_offset} = {required_offset}")

    # new_offset = round(required_offset * 4) / 4  # Round to 0.25 precision
    new_offset = round(required_offset, 2)  # Round to 0.01 precision
    if road.road_look.name not in per_name:
        per_name[road.road_look.name] = new_offset
    elif per_name[road.road_look.name] != new_offset:
        if operation == "sub" or allow_override:
            per_name[road.road_look.name] = new_offset
            # logger.warning(f"{prefix}Overriding existing offset: {road.road_look.name} {old_offset} -> {new_offset}")
        else:
            # logger.warning(f"{prefix}Keeping existing offset for {road.road_look.name} -> {per_name[road.road_look.name]}")
            pass
    else:
        # logger.warning(f"{prefix}E Keeping existing offset for {road.road_look.name} -> {per_name[road.road_look.name]}")
        pass
    return True


def generate_rules(config):
    # FULL REWRITE IS NEEDED
    """Generate pattern - based offset rules from per - name configurations.

    Args:
        config (dict): Current configuration

    Returns:
        dict: Modified configuration with generated rules
    """

    per_name = config["offsets"]["per_name"]
    rules = config["offsets"].setdefault("rules", {})

    logger.warning(
        f"Starting rule generation, current per_name entries: {len(per_name)}"
    )

    # Add all roads with their actual offsets from GetOffset
    all_road_offsets = {}
    for road in data.map.roads:
        if not hasattr(road, "road_look") or not road.road_look:
            continue

        # Create a mock road object for GetOffset
        mock_road = type(
            "Road",
            (),
            {
                "road_look": type(
                    "RoadLook",
                    (),
                    {
                        "name": road.road_look.name,
                        "offset": road.road_look.offset,  # use actual offset
                    },
                )
            },
        )()
        all_road_offsets[road.road_look.name] = road_helpers.GetOffset(mock_road)

    combined_roads = {**per_name, **all_road_offsets}
    logger.warning(f"Combined road: {combined_roads}")
    logger.warning(f"Total roads with offsets: {len(combined_roads)}")

    def _get_most_common_offset(offset_counts):
        """Get the most common offset with highest count"""
        if not offset_counts:
            return None, 0
        max_offset = max(
            offset_counts.items(), key=lambda x: (x[1], -abs(x[0]))
        )  # Prefer smaller absolute values
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

    # REWRITE 1: ATS Support
    # Generate rules based on 'offset' keyword and preceding [number]m pattern
    final_rules = defaultdict(list)
    # Regex to match [number]m pattern (supports comma-separated numbers)
    NUMBER_M_PATTERN = re.compile(r"([\d,]+)m")
    # Constants
    OFFSET_ADDITION = 4.5

    # Collect all matching patterns
    matched_patterns = set()

    for name, offset in combined_roads.items():
        words = name.split()
        if "offset" in words:
            offset_idx = words.index("offset")
            # Check preceding and following words
            for delta in [-1, 1]:
                word_idx = offset_idx + delta
                if 0 <= word_idx < len(words):
                    target_word = words[word_idx]
                    match = NUMBER_M_PATTERN.match(target_word)
                    if match:
                        # Extract number and calculate new offset
                        try:
                            # Handle comma-separated numbers by summing them
                            number_parts = match.group(1).split(",")
                            number = sum(float(part.strip()) for part in number_parts)
                            rule_offset = round(number + OFFSET_ADDITION, 1)
                        except ValueError:
                            logger.warning(
                                f"Invalid number format in '{target_word}' for road name: {name}"
                            )
                            continue
                        # Determine pattern based on position relative to offset
                    if delta == -1:
                        rule_pattern = f"**{target_word} offset"
                    else:
                        rule_pattern = f"**offset {target_word}"
                        final_rules[rule_pattern].append(rule_offset)
                        matched_patterns.add(target_word)

    # Update rules with only the new pattern-based rules
    rules.clear()
    rules.update(final_rules)
    # Sort rules alphabetically
    rules = dict(sorted(rules.items()))

    # Calculate mode for each pattern to determine the most frequent offset
    processed_rules = {}
    for pattern, offsets in final_rules.items():
        if offsets:
            offset_counter = Counter(offsets)
            max_count = max(offset_counter.values())
            # Select the first offset with maximum count
            mode_offset = next(k for k, v in offset_counter.items() if v == max_count)
            processed_rules[pattern] = mode_offset
    final_rules = processed_rules

    # Remove per_name entries that can be represented by rules
    to_remove = []
    for name in per_name:
        words = name.split()
        # Check if name contains the full rule pattern
        name_lower = " ".join(words)
        current_offset = per_name[name]
        for pattern, rule_offset in final_rules.items():
            # Remove the ** prefix and check if pattern exists in name
            if pattern[2:] in name_lower:
                # Check if offset values are within the allowed threshold
                if abs(current_offset - rule_offset) <= distance_threshold:
                    to_remove.append(name)
                    break

    for name in to_remove:
        if name in per_name:
            del per_name[name]

    logger.warning(
        f"Rule generation complete - Created {len(rules)} specialized rules, Removed {len(to_remove)} entries from per_name: {to_remove}"
    )

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
    return config


def clear_lane_offsets(clear):
    """Clear all lane offsets from the config"""
    logger.warning("Clearing all lane offsets")

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
        if clear == "rules":
            # Clear only rules
            config["offsets"]["rules"] = {}
            logger.warning("Cleared all rules")
        else:
            config["offsets"]["per_name"] = {}
            logger.warning("Cleared all per_name")

    # Ensure no invalid values before saving config
    config = _clean_invalid_offsets(config)
    with open(CONFIG_PATH, "w") as f:
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
