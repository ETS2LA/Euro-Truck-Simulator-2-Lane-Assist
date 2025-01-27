from ETS2LA.Utils.Values.numbers import SmoothedValue
import Plugins.Map.utils.math_helpers as math_helpers
import Plugins.Map.data as data
import numpy as np
import logging
import math

curvature = SmoothedValue("time", 3)

# Curvature in degrees
curvature_to_max_speed = {
    0: 110, # Max speed that ETS2LA is allowed to drive
    2.5: 100,
    5: 95,
    7.5: 90,
    10: 80,
    12.5: 70,
    15: 60,
    17.5: 50, 
    20: 40,
    22.5: 30,
    25: 25,
    30: 20,
}
def MapCurvatureToSpeed(curvature):
    curvature = abs(curvature * 4)
    # Map the curvature to a max speed
    index_below = 0
    index_above = 0
    for key in curvature_to_max_speed.keys():
        if key > curvature:
            index_above = key
            break
        index_below = key
        
    if index_below == len(curvature_to_max_speed.keys()) and index_above == 0:
        #data.plugin.state.text = f"Curvature: {curvature:.1f}°, Speed: {curvature_to_max_speed[-1]:.1f} km/h"
        return curvature_to_max_speed[-1] / 3.6 # Convert to m/s
    
    # Interpolate between the two values
    percentage = (curvature - index_below) / (index_above - index_below)
    if percentage < 0: percentage = 0
    speed = (curvature_to_max_speed[index_below] + (curvature_to_max_speed[index_above] - curvature_to_max_speed[index_below]) * percentage)
    data.plugin.state.text = f"Curvature: {curvature:.1f}°, Speed: {speed:.1f} km/h"
    return speed / 3.6 # Convert to m/s

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
                max_effect_distance = 20
                min_effect_distance = 100
                percentage = (distance - min_effect_distance) / (max_effect_distance - min_effect_distance)
                if percentage < 0:
                    percentage = 0
                curvatures.append(angle * percentage)

        try:
            # Remove anomalous curvatures
            avg = sum(curvatures) / len(curvatures)
            while max(curvatures) > avg * 4:
                curvatures.remove(max(curvatures))
                
            curvature = max(curvatures)
            curvature = abs(math.degrees(curvature))
        except:
            curvature = 0
        return MapCurvatureToSpeed(curvature)
    except Exception as e:
        logging.exception("Failed to calculate curvature")
        return MapCurvatureToSpeed(0)