# TODO: Fix this file, it's still using the old steering system!
import route.classes as rc
import classes as c
import numpy as np
import logging
import data
import math

OFFSET_MULTIPLIER = 1.5
ANGLE_MULTIPLIER = 1

def GetSteering():
    points = []
    for section in data.route_plan:
        if len(points) > 5:
            break
        
        if section is None:
            continue
        
        for point in section.get_points():
            if len(points) > 5:
                break
            points.append(point)
            
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
            offset_correction = max(-20, min(20, offset_correction))
            if isLeft:
                angle += offset_correction * OFFSET_MULTIPLIER
            else:
                angle += offset_correction * OFFSET_MULTIPLIER
            
            multiplier = 2
            
            return angle * multiplier
        else:
            x = points[len(points)-1].x
            z = points[len(points)-1].z
            
            vector = [x - data.truck_x, z - data.truck_z]

            angle = np.arccos(np.dot(forward_vector, vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(vector)))
            angle = math.degrees(angle)

            if np.cross(forward_vector, vector) < 0:
                angle = -angle
                
            return angle * 2
    except:
        logging.exception("Error in GetSteering")
        return 0