import numpy as np
import logging
import math
import data

# Curvature in degrees
curvature_to_max_speed = {
    0: 100, # Max speed that ETS2LA is allowed to drive
    20: 90,
    40: 80,
    60: 70,
    80: 60,
    100: 50,
    120: 40,
    140: 30,
    160: 25,
    180: 20,
}
def MapCurvatureToSpeed(curvature):
    # Map the curvature to a max speed
    index_below = 0
    index_above = 0
    for key in curvature_to_max_speed.keys():
        if key > curvature:
            index_above = key
            break
        index_below = key
        
    # Interpolate between the two values
    if index_below == len(curvature_to_max_speed.keys()) and index_above == 0:
        return curvature_to_max_speed[-1] / 3.6 # Convert to m/s
    
    percentage = (curvature - index_below) / (index_above - index_below)
    if percentage < 0: percentage = 0
    return (curvature_to_max_speed[index_below] + (curvature_to_max_speed[index_above] - curvature_to_max_speed[index_below]) * percentage) / 3.6 # Convert to m/s

def GetMaximumSpeed():
    points = data.route_points
    
    if len(points) < 3:  # Need at least 3 points to calculate curvature
        return 0
    
    curvatures = []
    try:
        for i in range(1, len(points) - 1):
            vector1 = np.array((points[i].x, points[i].z)) - np.array((points[i - 1].x, points[i - 1].z))
            vector2 = np.array((points[i + 1].x, points[i + 1].z)) - np.array((points[i].x, points[i].z))
            vector1 = vector1 / np.linalg.norm(vector1)
            vector2 = vector2 / np.linalg.norm(vector2)

            dot_product = np.dot(vector1, vector2)
            norm_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
            
            if norm_product == 0:
                angle = 0
            else:
                cos_angle = dot_product / norm_product
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                if angle > math.pi/2:
                    angle = math.pi - angle

            if not np.isnan(angle) and angle != 0:
                curvatures.append(angle)

        total_curvature = sum(curvatures)
        total_curvature = math.degrees(total_curvature)
        return MapCurvatureToSpeed(total_curvature)
    except Exception as e:
        logging.exception("Failed to calculate curvature")
        return MapCurvatureToSpeed(0)