from Plugins.DataProvider.classes import Node, Road, Lane, BoundingBox, Transform, Position
from Plugins.DataProvider.classes.data_provider import DataProvider
from Plugins.DataProvider.utils import math as umath
from typing import Optional
import numpy as np
import logging
import json
import re

offsets: dict[str, float] = {}
"""Base offsets. For example '0.0' into '4.5'."""
per_name: dict[str, float] = {}
"""Per roadlook name. For example 'narrow road' into '3.5'."""
rules: dict[str, float] = {}
"""Wildcard rules. For example '**narrow' into '3.5'."""

rules_filename = "plugins/Map/data/config.json"

def get_rules():
    """Load rules from the config file."""
    global offsets, per_name, rules
    try:
        with open(rules_filename, "r") as f:
            data = json.load(f)
            offsets = data["offsets"]["base"]
            per_name = data["offsets"]["per_name"]
            rules = data["offsets"]["rules"]
    except Exception as e:
        logging.error(f"Error loading road rules: {e}. Using default values.")
        offsets = {}
        per_name = {}
        rules = {}

def get_offset_for(road: Road):
    """Get the custom offset for a road."""
    if offsets == {} and per_name == {} and rules == {}:
        get_rules()
    
    name = road.road_look.name
    rule_offset = 999
    for rule in rules:
        rule = rule.replace("**", "")
        if rule in name:
            rule_offset = rules["**" + rule]

    reg = re.search(r'(^|\s|_)([+-]?\d+(\.\d+)?)m(_|\s|$)', road.road_look.name)
    if name in per_name:
        custom_offset = per_name[name]
    elif rule_offset != 999:
        custom_offset = rule_offset        
    elif reg:
        custom_offset = 4.5 + float(reg.group(2)) * 2
    elif str(road.road_look.offset) in offsets:     
        custom_offset = offsets[str(road.road_look.offset)] 
    else:
        roadOffset = road.road_look.offset

        if "narrow" in road.road_look.name:
            custom_offset = roadOffset
            if road.road_look.shoulder_space_left > 0:
                custom_offset += road.road_look.shoulder_space_left / 2
            if road.road_look.shoulder_space_right > 0:
                custom_offset += road.road_look.shoulder_space_right / 2
        elif "no offset" in road.road_look.name:
            custom_offset = 4.5
        elif "tmpl" in road.road_look.name:
            custom_offset = 4.5 + roadOffset * 2
        else:
            custom_offset = 4.5 + roadOffset

    return custom_offset

def get_previous_offset(node: Node, data: DataProvider) -> Optional[float]:
    """Get the custom offset for the previous road if it exists."""
    if hasattr(node, 'backward_item_uid'):
        prev_road = data.get_item(node.backward_item_uid)
        if isinstance(prev_road, Road):
            return get_offset_for(prev_road) if prev_road.road_look else 0
    return None

# TODO: Refactor the math in this function into a C++ extension
def calculate_lane_points(
        points: list[Position],
        lane_width: float, num_left_lanes: int, num_right_lanes: int, 
        road: Road, offset=999, prev_offset=999
    ) -> Optional[tuple[list[Position], list[Position]]]:
    try:
        # Validate input points
        if not points or len(points) < 2:
            logging.error(f"Road {road.uid if hasattr(road, 'uid') else 'unknown'} failed to generate points: insufficient points")
            return None

        lanes = ([[] for _ in range(num_left_lanes)],
                 [[] for _ in range(num_right_lanes)])

        base_offset = offset

        pointCount = len(points)
        for i in range(pointCount - 1):
            point1 = points[i].list()
            point1 = np.array([point1[0], point1[2]])
            point2 = points[i + 1].list()
            point2 = np.array([point2[0], point2[2]])

            if base_offset != 999 and prev_offset != 999 and prev_offset != base_offset:
                custom_offset = umath.lerp(prev_offset, base_offset, i / (pointCount - 2))

            direction_vector = point2 - point1
            direction_vector = direction_vector / np.linalg.norm(direction_vector)
            perp_vector = np.array([-direction_vector[1], direction_vector[0]])

            if num_left_lanes == 0: # lanes on only right side
                middle_offset = perp_vector * lane_width * (num_right_lanes + 1) / 2
                if num_right_lanes % 2 == 0:
                    middle_offset -= perp_vector * lane_width / 2
                point1 -= middle_offset
                point2 -= middle_offset
                
            elif num_right_lanes == 0: # lanes on only left side
                middle_offset = -perp_vector * lane_width * (num_left_lanes + 1) / 2
                if num_left_lanes % 2 == 0:
                    middle_offset += perp_vector * lane_width / 2
                point1 -= middle_offset
                point2 -= middle_offset

            for lane in range(num_left_lanes): # left lanes
                offset = perp_vector * (lane_width * (lane) + custom_offset / 2)

                left_point1 = point1 - offset
                left_point2 = point2 - offset
                lanes[0][lane].append(Position(*left_point1.tolist()))
                if i == len(points) - 2:
                    lanes[0][lane].append(Position(*left_point2.tolist()))

            for lane in range(num_right_lanes): # right lanes
                offset = perp_vector * (lane_width * (lane) + custom_offset / 2)

                right_point1 = point1 + offset
                right_point2 = point2 + offset
                lanes[1][lane].append(Position(*right_point1.tolist()))
                if i == len(points) - 2:
                    lanes[1][lane].append(Position(*right_point2.tolist()))

        # This makes no sense?
        # for lane in range(num_left_lanes):
        #     for i in range(len(lanes[0][lane])):
        #         lanes[0][lane][i].append(road.points[i].list()[1])
        # for lane in range(num_right_lanes):
        #     for i in range(len(lanes[1][lane])):
        #         lanes[1][lane][i].append(road.points[i].list()[1])

        return lanes
    except Exception as e:
        logging.error(f"Error calculating lanes for road {getattr(road, 'uid', 'unknown')}: {e}")
        return None

def get_road_lanes(road: Road, data: DataProvider) -> Optional[tuple[list[Lane]]]:    
    """Parse a road into an array of lanes."""
    if not hasattr(road, 'road_look') or not road.road_look:
        logging.error(f"Road {road.uid} has no road_look")
        return None
    
    start_node = data.get_node(road.start_node_uid)
    end_node = data.get_node(road.end_node_uid)
    if not start_node or not end_node:
        logging.error(f"Road {road.uid} failed to initialize nodes")
        return None

    offset = get_offset_for(road)
    offset_prev = get_previous_offset(start_node, data)
    if not offset_prev:
        offset_prev = offset

    # try:
    #     lanes = calculate_lanes(
    #         start_node.transform, end_node.transform, 
    #         4.5, len(road.road_look.lanes_left), len(road.road_look.lanes_right),
    #         road, offset=offset, prev_offset=offset_prev
    #     )
    # except Exception as e:
    #     logging.error(f"Error calculating lanes for road {road.uid}: {e}")
    #     return [], c.BoundingBox(0, 0, 0, 0)

    lanes['left'] = lanes['left'][::-1]
    points = lanes['left'] + lanes['right']

    bounding_box = [[999999, 999999], [-999999, -999999]]
    for lane in points:
        for point in lane:
            if point[0] < bounding_box[0][0]:
                bounding_box[0][0] = point[0]
            if point[0] > bounding_box[1][0]:
                bounding_box[1][0] = point[0]
            if point[1] < bounding_box[0][1]:
                bounding_box[0][1] = point[1]
            if point[1] > bounding_box[1][1]:
                bounding_box[1][1] = point[1]

    bounding_box[0][0] -= 5
    bounding_box[0][1] -= 5
    bounding_box[1][0] += 5
    bounding_box[1][1] += 5

    bounding_box = c.BoundingBox(
        bounding_box[0][0], bounding_box[0][1],
        bounding_box[1][0], bounding_box[1][1]
    )

    lane_objects = []

    for lane in lanes['left']:
        lane_objects.append(c.Lane(
            [c.Position(point[0], point[2], point[1]) for point in lane],
            "left"
        ))
    for lane in lanes['right']:
        lane_objects.append(c.Lane(
            [c.Position(point[0], point[2], point[1]) for point in lane],
            "right"
        ))

    return lane_objects, bounding_box