import plugins.Map.classes as c
import plugins.Map.data as data
import numpy as np
import cv2

cv2.namedWindow("Route", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Route", 1024, 1024)

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

def visualize_route(destination_item: c.Item, start_item: c.Item, route_plan: list[c.Node]) -> None:
    image = draw_map_image()
    
    # Draw a red dot at the destination
    if destination_item is not None:
        dest_x, dest_y = convert_from_world_to_map(destination_item.x, destination_item.y)
        cv2.circle(image, (dest_x, dest_y), 5, (0, 0, 255), -1)
    
    # Draw a green dot at the start
    start_x, start_y = convert_from_world_to_map(start_item.x, start_item.y)
    cv2.circle(image, (start_x, start_y), 5, (0, 255, 0), -1)
    
    cv2.imshow("Route", image)
    cv2.waitKey(1)