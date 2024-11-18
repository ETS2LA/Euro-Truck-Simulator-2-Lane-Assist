import plugins.Map.navigation.classes as nc
import plugins.Map.classes as c
import plugins.Map.data as data
import numpy as np
import cv2
from plugins.Map.navigation.classes import RoadSection

#cv2.namedWindow("Route", cv2.WINDOW_NORMAL)
#cv2.resizeWindow("Route", 1024, 1024)

map_image = cv2.imread("plugins/Map/navigation/map.png")
map_image = cv2.resize(map_image, (1024, 1024))

x1 = -94621.8047
x2 = 79370.13
y1 = -80209.1641
y2 = 93782.77
minZoom = 0
maxZoom = 8

def convert_from_world_to_map(x: float, y: float) -> tuple[int, int]:
    x = (x - x1) / (x2 - x1) * map_image.shape[1]
    y = (y - y1) / (y2 - y1) * map_image.shape[0]
    return int(x), int(y)

def convert_from_map_to_world(x: int, y: int) -> tuple[float, float]:
    x = x / map_image.shape[1] * (x2 - x1) + x1
    y = y / map_image.shape[0] * (y2 - y1) + y1
    return x, y

def draw_map_image() -> None:
    return map_image.copy()

def visualize_route(destination_item: c.Item | RoadSection, start_item: c.Item | RoadSection, route_plan: list[nc.NavigationLane]) -> None:
    image = draw_map_image()
    
    # Draw a red dot at the destination
    if destination_item is not None:
        if isinstance(destination_item, RoadSection):
            # Use average position of first and last road for visualization
            dest_x = (destination_item.start.x + destination_item.end.x) / 2
            dest_y = (destination_item.start.y + destination_item.end.y) / 2
        else:
            dest_x, dest_y = destination_item.x, destination_item.y
            
        map_x, map_y = convert_from_world_to_map(dest_x, dest_y)
        cv2.circle(image, (map_x, map_y), 5, (0, 0, 255), -1)
    
    # Draw a green dot at the start
    if isinstance(start_item, RoadSection):
        start_x = (start_item.start.x + start_item.end.x) / 2
        start_y = (start_item.start.y + start_item.end.y) / 2
    else:
        start_x, start_y = start_item.x, start_item.y
        
    map_x, map_y = convert_from_world_to_map(start_x, start_y)
    cv2.circle(image, (map_x, map_y), 5, (0, 255, 0), -1)
    
    # Draw the route
    points = [item.start for item in route_plan]
    if route_plan:  # Add the end point of last item
        points.append(route_plan[-1].end)
    points = [(convert_from_world_to_map(point.x, point.y)) for point in points]
    if points:
        cv2.polylines(image, [np.array(points)], False, (255, 0, 0), 2)
    
    cv2.imshow("Route", image)
    cv2.waitKey(1)