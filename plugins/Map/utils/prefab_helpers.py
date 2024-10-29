import plugins.Map.classes as c
import numpy as np
import math
import cv2

def find_starting_curves(prefab_description: c.PrefabDescription) -> list[c.PrefabNavCurve]:
    starting_curves = []
    for curve in prefab_description.nav_curves:
        if curve.prev_lines == []:
            starting_curves.append(curve)
    return starting_curves

def traverse_curve_till_end(curve: c.PrefabNavCurve, prefab_description: c.PrefabDescription) -> list[list[c.PrefabNavCurve]]:
    routes: list[list[c.PrefabNavCurve]] = []
    
    def traverse(curve: c.PrefabNavCurve, route: list[c.PrefabNavCurve], depth: int):
        route.append(curve)
        if curve.next_lines == []:
            routes.append(route)
            return
        
        if depth > 40:
            return
        
        for next_curve in curve.next_lines:
            next_curve = prefab_description.nav_curves[next_curve]
            traverse(next_curve, route.copy(), depth + 1)
            
    traverse(curve, [], 0)
    return routes

def display_prefab_routes(prefab_description: c.PrefabDescription) -> None:
    cv2.namedWindow("Nav Routes", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Nav Routes", 1000, 1000)
    img = np.zeros((1000, 1000, 3), np.uint8)
    min_x = math.inf
    max_x = -math.inf
    min_y = math.inf
    max_y = -math.inf
    
    for route in prefab_description.nav_routes:
        for curve in route.curves:
            for point in curve.points:
                if point.x < min_x:
                    min_x = point.x
                if point.x > max_x:
                    max_x = point.x
                if point.y < min_y:
                    min_y = point.z
                if point.y > max_y:
                    max_y = point.z
                    
    min_x -= 10
    max_x += 10
    min_y -= 10
    max_y += 10
    
    scaling_factor = 6
    offset_x = 500
    offset_y = 500
    
    for route in prefab_description.nav_routes:
        for curve in route.curves:
            poly_points = np.array([[int((point.x*scaling_factor + offset_x)), int((point.z*scaling_factor + offset_y))] for point in curve.points], np.int32)
            cv2.polylines(img, [poly_points], isClosed=False, color=(255, 255, 255), thickness=1)
                
    cv2.imshow("Nav Routes", img)
    cv2.resizeWindow("Nav Routes", 1000, 1000)
    cv2.waitKey(0)