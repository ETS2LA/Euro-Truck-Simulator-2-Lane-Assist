from ETS2LA.utils.values import SmoothedValue
import plugins.Map.utils.math_helpers as math_helpers
import plugins.Map.data as data
import numpy as np
import logging
import math

curvature = SmoothedValue("time", 3)

# Curvature in degrees
curvature_to_max_speed = {
    0: 100, # Max speed that ETS2LA is allowed to drive
    0.1: 90,
    0.2: 80,
    0.3: 70,
    0.4: 60,
    0.5: 50,
    0.6: 40,
    0.7: 35,
    0.8: 30,
    0.9: 25,
    1: 20,
}
def MapCurvatureToSpeed(curvature):
    curvature = min(curvature/5, 1)
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
                distance = math_helpers.DistanceBetweenPoints((data.truck_x, data.truck_z), (points[i].x, points[i].z))
                max_effect_distance = 2
                min_effect_distance = 80
                percentage = (distance - min_effect_distance) / (max_effect_distance - min_effect_distance)
                curvatures.append(angle * percentage)

        try:
            curvature = max(curvatures)
            curvature = abs(math.degrees(curvature))
        except:
            curvature = 0
        return MapCurvatureToSpeed(curvature)
    except Exception as e:
        logging.exception("Failed to calculate curvature")
        return MapCurvatureToSpeed(0)