from ETS2LA.Utils.Values.numbers import SmoothedValue
import Plugins.Map.utils.math_helpers as math_helpers
import Plugins.Map.data as data
import numpy as np
import logging
import math

# Constants
MU = 0.6  # Coefficient of friction
G = 9.81  # Gravitational acceleration (m/s^2)

curvature = SmoothedValue("time", 3)

def CalculateCurvature(points):
    """
    Calculate the curvature for each point in the road segment.
    """
    curvatures = []
    for i in range(1, len(points) - 1):
        # Direction vectors
        v1 = np.array([points[i].x - points[i - 1].x, points[i].z - points[i - 1].z])
        v2 = np.array([points[i + 1].x - points[i].x, points[i + 1].z - points[i].z])
        
        # Angle change
        dot_product = np.dot(v1, v2)
        norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norm_product == 0:
            continue  # Skip to avoid division by zero
        cos_angle = dot_product / norm_product
        cos_angle = np.clip(cos_angle, -1, 1)  # Ensure valid arccos input
        delta_theta = np.arccos(cos_angle)
        
        # Arc length (average of the two segment lengths)
        delta_s = (np.linalg.norm(v1) + np.linalg.norm(v2)) / 2
        
        # Curvature (1/m)
        if delta_s == 0:
            continue  # Skip to avoid division by zero
        kappa = delta_theta / delta_s
        curvatures.append(kappa)
    
    return curvatures

def GetMaximumSpeed():
    """
    Calculate the maximum safe speed based on road curvature.
    """
    points = data.route_points
    
    if len(points) < 3:  # Need at least 3 points to calculate curvature
        return 999
    
    try:
        # Calculate curvatures for all points
        curvatures = CalculateCurvature(points)
        
        if not curvatures:
            return 999
        
        avg_curvature = np.mean(curvatures)
        curvatures = [k for k in curvatures if k <= 4 * avg_curvature]
        
        if not curvatures:
            return 999
        
        max_curvature = max(curvatures)
        
        # sqrt(MU * G / max_curvature) = max_speed
        max_speed = np.sqrt(MU * G / max_curvature)  # In m/s

        return max_speed
    
    except Exception as e:
        logging.exception("Failed to calculate maximum speed")
        return 999