# TODO: Fix this file, it's still using the old steering system!
import Plugins.Map.utils.math_helpers as math_helpers
import Plugins.Map.route.classes as rc
import Plugins.Map.classes as c
import Plugins.Map.data as data
import numpy as np
import logging
import math

OFFSET_MULTIPLIER = 1.5
ANGLE_MULTIPLIER = 1

was_indicating = False
def CheckForLaneChange():
    global was_indicating
    if type(data.route_plan[0].items[0].item) == c.Prefab:
        was_indicating = False
        return
    
    current_index = data.route_plan[0].lane_index
    lanes = data.route_plan[0].items[0].item.lanes
    side = lanes[current_index].side
    left_lanes = len([lane for lane in lanes if lane.side == "left"])
    # lanes = left_lanes + right_lanes
    
    if (data.truck_indicating_right or data.truck_indicating_left) and not was_indicating:
        was_indicating = True
        current_index = data.route_plan[0].lane_index
        side = lanes[current_index].side
        
        target_index = current_index
        change = -1 if data.truck_indicating_right else 1
        
        end_node = data.route_plan[0].end_node
        end_node_in_front = math_helpers.IsInFront([end_node.x, end_node.y], data.truck_rotation, [data.truck_x, data.truck_z])
            
        if side == "left":    
            if end_node_in_front: # Normal lane change
                target_index += change
                if change == 1 and target_index >= left_lanes:
                    target_index = left_lanes - 1
            else: # Inverted lane change
                target_index -= change
                if change == -1 and target_index >= left_lanes:
                    target_index = left_lanes - 1
        else:
            if end_node_in_front:
                target_index += change
                if change == -1 and target_index < left_lanes:
                    target_index = left_lanes
            else:
                target_index -= change
                if change == 1 and target_index < left_lanes:
                    target_index = left_lanes
                    
        if target_index < 0:
            target_index = 0
        if target_index >= len(lanes):
            target_index = len(lanes) - 1
                    
        data.route_plan[0].lane_index = target_index
        
    elif not data.truck_indicating_left and not data.truck_indicating_right:
        was_indicating = False  

def GetPointDistance(points_so_far: int):
    if points_so_far < data.amount_of_points/5:
        return 0.25
    elif points_so_far < data.amount_of_points/5*2:
        return 4
    elif points_so_far < data.amount_of_points/5*3:
        return 8
    elif points_so_far < data.amount_of_points/5*4:
        return 16
    else:
        return 32
    

def GetSteering():
    if len(data.route_plan) == 0:
        return 0
    
    CheckForLaneChange()
    
    points = []
    for section in data.route_plan:
        if len(points) > data.amount_of_points:
            break
        
        if section is None:
            continue
        
        section_points = section.get_points()[:-1]
        for point in section_points:
            if len(points) > data.amount_of_points:
                break
            
            if len(points) == 0:
                points.append(point)
                continue
                
            if math_helpers.DistanceBetweenPoints(point.tuple(), points[-1].tuple()) >= GetPointDistance(len(points)):
                points.append(point)

    if len(points) == 0:
        return 0

    points = points
    speed = max(data.truck_speed * 3.6, 10)  # Convert to kph
    speed = min(speed, 80)
    # Multiplier is 8 at 10kph and 2 at 80kph
    multiplier = max(8 - (speed - 10) / 10, 2)

    data.route_points = points
    
    if math_helpers.DistanceBetweenPoints((data.truck_x, data.truck_z), (data.route_points[0].x, data.route_points[0].z)) > 20:
        logging.warning("Recalculating navigation plan as we are too far off the path!")
        data.route_plan = []
        data.update_navigation_plan = True
            
    forward_vector = [-math.sin(data.truck_rotation), -math.cos(data.truck_rotation)]
    try:
        if len(points) > 2:
            points = points[:5]

            x = 0
            z = 0
            for i in range(1, len(points)):
                x += points[i].x
                z += points[i].z
            x /= 4
            z /= 4
            
            point_forward_vector = [points[len(points)-1].x - points[0].x, points[len(points)-1].z - points[0].z]
            
            if np.cross(forward_vector, point_forward_vector) < 0:
                isLeft = True
            else: isLeft = False
            
            centerline = [points[-1].x - points[0].x, points[-1].z - points[0].z]
            truck_position_vector = [data.truck_x - points[0].x, data.truck_z - points[0].z]
            
            lateral_offset = np.cross(truck_position_vector, centerline) / np.linalg.norm(centerline)
            data.plugin.globals.tags.lateral_offset = lateral_offset
            
            angle = np.arccos(np.dot(forward_vector, centerline) / (np.linalg.norm(forward_vector) * np.linalg.norm(centerline)))
            angle = math.degrees(angle)
            
            if np.cross(forward_vector, centerline) < 0:
                angle = -angle
            
            if angle > 140:
                angle = 0
            if angle < -140:
                angle = 0
            
            angle = angle * ANGLE_MULTIPLIER
            
            offset_correction = lateral_offset * 5
            offset_correction = offset_correction
            if isLeft:
                angle += offset_correction * OFFSET_MULTIPLIER
            else:
                angle += offset_correction * OFFSET_MULTIPLIER
            
            return angle * multiplier
        elif len(points) == 2:
            x = points[len(points)-1].x
            z = points[len(points)-1].z
            
            vector = [x - data.truck_x, z - data.truck_z]

            angle = np.arccos(np.dot(forward_vector, vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(vector)))
            angle = math.degrees(angle)

            if np.cross(forward_vector, vector) < 0:
                angle = -angle
                
            return angle * 2 * multiplier
        else:
            return 0
    except:
        logging.exception("Error in GetSteering")
        return 0