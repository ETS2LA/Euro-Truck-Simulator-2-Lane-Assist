# TODO:
# Make this work with the new road system once roadlook names have been added!

import classes as c
import json

offsets = {}
per_name = {}
rules = {}
rules_filename = "utils/lanes.json"

def get_rules():
    global offsets, per_name, rules
    with open(rules_filename, "r") as f:
        data = json.load(f)
        offsets = data["offset_data"]
        per_name = data["per_name"]
        rules = data["rules"]
        
get_rules()

def calculate_lanes(points, lane_width, num_left_lanes, num_right_lanes, road, custom_offset=999, next_offset=999, side=0):
    lanes = {'left': [[] for _ in range(num_left_lanes)], 
             'right': [[] for _ in range(num_right_lanes)]}
    
    #print(custom_offset)
    base_custom_offset = custom_offset
    # points = points[::-1] # This will fix some roads being the other way around (mainly 2 left 1 right with a wide gap)
    pointCount = len(points)
    for i in range(pointCount - 1):
        point1 = np.array(points[i])
        point2 = np.array(points[i + 1])
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
            point1 += middle_offset
            point2 += middle_offset
        
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
            lanes['left'][lane][i].append(road.YValues[i])
    for lane in range(num_right_lanes):
        for i in range(len(lanes['right'][lane])):
            lanes['right'][lane][i].append(road.YValues[i])

    return lanes


def GetOffset(road: c.Road):
    # Fix 999 and 0.0 offsets
    name = road.road_look.token
    
    # Check the rules
    rule_offset = 999
    for rule in rules:
        rule = rule.replace("**", "")
        if rule in name:
            rule_offset = rules["**" + rule]
    
    if name in per_name:
        custom_offset = per_name[name]
    elif rule_offset != 999:
        custom_offset = rule_offset
    elif str(road.RoadLook.offset) in offsets: 
        custom_offset = offsets[str(road.RoadLook.offset)]
    else: 
        # Check if the road name has the offset in it
        if "m offset" in road.RoadLook.name:
            roadOffset = road.RoadLook.name.split("m offset")[0]
            roadOffset = float(roadOffset.split(" ")[-1])
        else:
            roadOffset = road.RoadLook.offset
        
        # If the name has "narrow" in it, then the offset is not added to 4.5
        # These roads also need to include the shoulder space... for whatever reason
        if "narrow" in road.RoadLook.name:
            custom_offset = roadOffset
            if road.RoadLook.shoulderSpaceLeft > 0: 
                custom_offset += road.RoadLook.shoulderSpaceLeft / 2
            if road.RoadLook.shoulderSpaceRight > 0:
                custom_offset += road.RoadLook.shoulderSpaceRight / 2
        
        # No offset means that the road only wants it's custom offset
        # IBE > -36910 , 47585
        elif "no offset" in road.RoadLook.name:
            custom_offset = 4.5
        
        # If the name has "tmpl" in it, then the offset is doubled
        elif "tmpl" in road.RoadLook.name:
            custom_offset = 4.5 + roadOffset * 2
        
        # Assume that the offset is actually correct
        else:
            custom_offset = 4.5 + roadOffset

    return custom_offset

# MARK: Parallel Curves
def CalculateParallelCurves(road):
    try:
        
        custom_offset = GetOffset(road)

        # Get the offset of the next road
        try:
            roadNext = road.EndNode.ForwardItem
            custom_offset_next = GetOffset(roadNext)
        except:
            custom_offset_next = custom_offset
            
        # Get the offset of the last road
        try:
            roadPrev = road.StartNode.BackwardItem
            custom_offset_prev = GetOffset(roadPrev)
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

        lanes = calc.calculate_lanes(road.Points, 4.5, len(road.RoadLook.lanesLeft), len(road.RoadLook.lanesRight), road, custom_offset=custom_offset, next_offset=next_offset, side=side)
        # Invert the left lane array
        lanes['left'] = lanes['left'][::-1]
        newPoints = lanes['left'] + lanes['right']
        
        boundingBox = [[999999, 999999], [-999999, -999999]]
        for lane in newPoints:
            for point in lane:
                if point[0] < boundingBox[0][0]:
                    boundingBox[0][0] = point[0]
                if point[0] > boundingBox[1][0]:
                    boundingBox[1][0] = point[0]
                if point[1] < boundingBox[0][1]:
                    boundingBox[0][1] = point[1]
                if point[1] > boundingBox[1][1]:
                    boundingBox[1][1] = point[1]
        # Add 5m of padding
        boundingBox[0][0] -= 5
        boundingBox[0][1] -= 5
        boundingBox[1][0] += 5
        boundingBox[1][1] += 5            
        
        return boundingBox, newPoints, 4.5
    
    except:
        import traceback
        traceback.print_exc()
        return [], [], 0