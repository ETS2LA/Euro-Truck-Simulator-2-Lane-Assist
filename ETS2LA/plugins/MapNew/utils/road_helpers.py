# WARNING:
# This uses old code from the old Map plugin. This means that it isn't typed.
# You should not edit this code unless you know what you are doing.

# TODO: Clean the code and optimize road generation

import ETS2LA.variables as variables
import classes as c
import numpy as np
import math
import cv2
import json

offsets = {}
per_name = {}
rules = {}
rules_filename = "ETS2LA/plugins/MapNew/utils/lane_offsets.json"

def get_rules():
    global offsets, per_name, rules
    with open(rules_filename, "r") as f:
        data = json.load(f)
        offsets = data["offset_data"]
        per_name = data["per_name"]
        rules = data["rules"]

def perpendicular_vector(v):
    return np.array([-v[1], v[0]])

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def lerp(a, b, t):
    return a + t * (b - a)

def calculate_lanes(points, lane_width, num_left_lanes, num_right_lanes, road, custom_offset=999, next_offset=999, side=0):
    lanes = {'left': [[] for _ in range(num_left_lanes)], 
             'right': [[] for _ in range(num_right_lanes)]}
    
    base_custom_offset = custom_offset
    
    if num_left_lanes == 2 and num_right_lanes == 1:
        points = points[::-1] # This will fix some roads being the other way around (mainly 2 left 1 right with a wide gap)

    pointCount = len(points)
    for i in range(pointCount - 1):
        point1 = points[i].list()
        point1 = np.array([point1[0], point1[2]])
        point2 = points[i + 1].list()
        point2 = np.array([point2[0], point2[2]])
        if next_offset != base_custom_offset and next_offset != 999 and base_custom_offset != 999:
            if side == 0:
                custom_offset = lerp(base_custom_offset, next_offset, i / (pointCount - 1))
            elif side == 1:
                custom_offset = lerp(base_custom_offset, next_offset, 1 - i / (pointCount - 1))
        
        # Calculate the direction vector
        direction_vector = point2 - point1
        
        # Normalize the direction vector
        direction_vector = normalize(direction_vector)
        
        # Calculate the perpendicular vector
        perp_vector = perpendicular_vector(direction_vector)
        
        # Adjust the middle point if there are no lanes on one side
        if num_left_lanes == 0:
            custom_offset = 999
            # Middle point is the edge of the right lanes
            middle_offset = -perp_vector * lane_width * num_right_lanes / 2
            if num_right_lanes % 2 == 0:
                middle_offset -= perp_vector * lane_width / 2
            point1 -= middle_offset
            point2 -= middle_offset
        elif num_right_lanes == 0:
            custom_offset = 999
            # Middle point is the edge of the left lanes
            middle_offset = perp_vector * lane_width * num_left_lanes / 2
            if num_right_lanes % 2 == 0:
                middle_offset += perp_vector * lane_width / 2
            # NOTE: I changed these to - since Map V1, if it doesn't work this is probably why.
            point1 -= middle_offset
            point2 -= middle_offset
        
        # Offset to keep the lanes centered
        elif num_left_lanes > num_right_lanes:
            middle_offset = perp_vector * lane_width * (num_left_lanes + 1 - num_right_lanes) / 2
            point1 -= middle_offset
            point2 -= middle_offset
        elif num_right_lanes > num_left_lanes:
            middle_offset = -perp_vector * lane_width * (num_right_lanes + 1 - num_left_lanes) / 2
            point1 -= middle_offset
            point2 -= middle_offset
            
        
        # Calculate the lane points for each lane on the left side
        for lane in range(num_left_lanes):
            if custom_offset == 999 or (num_left_lanes == 1 and num_right_lanes == 0):
                offset = perp_vector * (lane_width * (lane + 1))
            else:
                offset = perp_vector * (lane_width * (lane) + custom_offset / 2)
            
            left_point1 = point1 + offset
            left_point2 = point2 + offset
            lanes['left'][lane].append(left_point1.tolist())
            if i == len(points) - 2:
                lanes['left'][lane].append(left_point2.tolist())
        
        # Calculate the lane points for each lane on the right side
        for lane in range(num_right_lanes):
            if custom_offset == 999 or (num_left_lanes == 0 and num_right_lanes == 1):
                offset = perp_vector * (lane_width * (lane + 1))
            else:
                offset = perp_vector * (lane_width * (lane) + custom_offset / 2)
            right_point1 = point1 - offset
            right_point2 = point2 - offset
            lanes['right'][lane].append(right_point1.tolist())
            if i == len(points) - 2:
                lanes['right'][lane].append(right_point2.tolist())

    # Add the Y values from the road. This will help with visualizing the lanes later on
    for lane in range(num_left_lanes):
        for i in range(len(lanes['left'][lane])):
            lanes['left'][lane][i].append(road.points[i].list()[1])
    for lane in range(num_right_lanes):
        for i in range(len(lanes['right'][lane])):
            lanes['right'][lane][i].append(road.points[i].list()[1])

    return lanes


def GetOffset(road):
    # Fix 999 and 0.0 offsets
    name = road.road_look.name
    
    # Check the rules
    rule_offset = 999
    for rule in rules:
        rule = rule.replace("**", "")
        if rule in name:
            rule_offset = rules["**" + rule]
        
    # Highways use m offset * 2 + 4.5 as the offset
    if "m offset" in road.road_look.name:
        custom_offset = road.road_look.name.split("m offset")[0]
        custom_offset = float(custom_offset.split(" ")[-1]) * 2
        custom_offset = 4.5 + custom_offset
    elif name in per_name:
        custom_offset = per_name[name]
    elif rule_offset != 999:
        custom_offset = rule_offset
    elif str(road.road_look.offset) in offsets: 
        custom_offset = offsets[str(road.road_look.offset)]
    else: 
        roadOffset = road.road_look.offset
        
        # If the name has "narrow" in it, then the offset is not added to 4.5
        # These roads also need to include the shoulder space... for whatever reason
        if "narrow" in road.road_look.name:
            custom_offset = roadOffset
            if road.road_look.shoulder_space_left > 0: 
                custom_offset += road.road_look.shoulder_space_left / 2
            if road.road_look.shoulder_space_right > 0:
                custom_offset += road.road_look.shoulder_space_right / 2
        
        # No offset means that the road only wants it's custom offset
        # IBE > -36910 , 47585
        elif "no offset" in road.road_look.name:
            custom_offset = 4.5
        
        # If the name has "tmpl" in it, then the offset is doubled
        elif "tmpl" in road.road_look.name:
            custom_offset = 4.5 + roadOffset * 2
        
        # Assume that the offset is actually correct
        else:
            custom_offset = 4.5 + roadOffset

    return custom_offset

# MARK: Parallel Curves
def GetRoadLanes(road, data):
    if offsets == {} and per_name == {} and rules == {}:
        get_rules()
    try:
        
        custom_offset = GetOffset(road)

        end_node = data.data.get_node_by_uid(road.end_node_uid)
        start_node = data.data.get_node_by_uid(road.start_node_uid)

        # Get the offset of the next road
        try:
            next_road = data.data.get_item_by_uid(end_node.forward_item_uid)
            custom_offset_next = GetOffset(next_road)
        except:
            custom_offset_next = custom_offset
            
        # Get the offset of the last road
        try:
            prev_road = data.data.get_item_by_uid(start_node.backward_item_uid)
            custom_offset_prev = GetOffset(prev_road)
        except:
            custom_offset_prev = custom_offset
            
        next_offset = custom_offset
        side = 0
        if custom_offset_next > custom_offset:
            next_offset = custom_offset_next
            side = 0
            
        elif custom_offset_prev > custom_offset:
            next_offset = custom_offset_prev
            side = 1

        lanes = calculate_lanes(road.points, 4.5, len(road.road_look.lanes_left), len(road.road_look.lanes_right), road, custom_offset=custom_offset, next_offset=next_offset, side=side)
        # Invert the left lane array
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
        # Add 5m of padding
        bounding_box[0][0] -= 5
        bounding_box[0][1] -= 5
        bounding_box[1][0] += 5
        bounding_box[1][1] += 5   
        
        bounding_box = c.BoundingBox(
            bounding_box[0][0], bounding_box[0][1], # min_x, min_y
            bounding_box[1][0], bounding_box[1][1]  # max_x, max_y
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
    
    except:
        import traceback
        traceback.print_exc()
        return [], c.BoundingBox(0, 0, 0, 0)
    
def display_road_lanes(road) -> None:
    cv2.namedWindow("Road Lanes", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Road Lanes", 1000, 1000)
    img = np.zeros((1000, 1000, 3), np.uint8)
    min_x = road.bounding_box.min_x - road.x - 10
    max_x = road.bounding_box.max_x - road.x + 10
    min_y = road.bounding_box.min_y - road.y - 10
    max_y = road.bounding_box.max_y - road.y + 10
    
    scaling_factor = 2
    offset_x = 500
    offset_y = 500
    
    for lane in road.lanes:
        poly_points = np.array([[int(((point.x - road.x)*scaling_factor + offset_x)), int(((point.z - road.y)*scaling_factor + offset_y))] for point in lane.points], np.int32)
        cv2.polylines(img, [poly_points], isClosed=False, color=(255, 255, 255), thickness=1)
                
    cv2.imshow("Road Lanes", img)
    cv2.resizeWindow("Road Lanes", 1000, 1000)
    cv2.waitKey(0)