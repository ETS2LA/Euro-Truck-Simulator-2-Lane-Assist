import plugins.Map.navigation.classes as nc
import plugins.Map.classes as c
import plugins.Map.data as data
import numpy as np
import cv2
from plugins.Map.navigation.classes import RoadSection
import logging
import os

#cv2.namedWindow("Route", cv2.WINDOW_NORMAL)
#cv2.resizeWindow("Route", 1024, 1024)

# Create a blank map image if the file doesn't exist
MAP_PATH = "plugins/Map/navigation/map.png"
if not os.path.exists(MAP_PATH):
    map_image = np.zeros((1024, 1024, 3), dtype=np.uint8)
else:
    map_image = cv2.imread(MAP_PATH)
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

def convert_from_world_to_zoomed_map(x: float, y: float, min_x: int, min_y: int, scale_x: float, scale_y: float) -> tuple[int, int]:
    # First convert to original map coordinates
    map_x = (x - x1) / (x2 - x1) * map_image.shape[1]
    map_y = (y - y1) / (y2 - y1) * map_image.shape[0]
    
    # Then convert to zoomed coordinates
    zoomed_x = int((map_x - min_x) * scale_x)
    zoomed_y = int((map_y - min_y) * scale_y)
    
    return zoomed_x, zoomed_y

def convert_from_map_to_world(x: int, y: int) -> tuple[float, float]:
    x = x / map_image.shape[1] * (x2 - x1) + x1
    y = y / map_image.shape[0] * (y2 - y1) + y1
    return x, y

def draw_map_image() -> None:
    return map_image.copy()

def visualize_route(destination_item: c.Item | RoadSection, start_item: c.Item | RoadSection, route_plan: list[nc.NavigationLane], mock_mode: bool = False) -> None:
    """
    Visualize the route on the map.

    Args:
        destination_item: The destination item (Item or RoadSection)
        start_item: The starting item (Item or RoadSection)
        route_plan: List of navigation lanes forming the route
        mock_mode: If True, skips window creation and display (for testing)
    """
    logging.debug(f"Visualizing route with {len(route_plan) if route_plan else 0} navigation lanes")
    image = draw_map_image()

    # Get coordinates for start/end
    if isinstance(start_item, RoadSection):
        start_x = (start_item.start.x + start_item.end.x) / 2
        start_y = (start_item.start.z + start_item.end.z) / 2
    elif isinstance(start_item, c.Road):
        start_x = start_item.points[0].x
        start_y = start_item.points[0].z
    else:
        start_x, start_y = start_item.x, start_item.z

    if destination_item is not None:
        if isinstance(destination_item, RoadSection):
            dest_x = (destination_item.start.x + destination_item.end.x) / 2
            dest_y = (destination_item.start.z + destination_item.end.z) / 2
        elif isinstance(destination_item, c.Road):
            dest_x = destination_item.points[-1].x
            dest_y = destination_item.points[-1].z
        else:
            dest_x, dest_y = destination_item.x, destination_item.z

    # Get all points to consider for bounding box
    all_points = []
    padding = 100
    if route_plan:
        # Include all route points
        padding = 2
        for item in route_plan:
            all_points.extend([(point.x, point.z) for point in item.lane.points])

    else:
        all_points.append((start_x, start_y))
        if destination_item is not None:
            all_points.append((dest_x, dest_y))

    # Convert all points to map coordinates
    map_points = [convert_from_world_to_map(x, y) for x, y in all_points]

    # Calculate bounding box
    map_xs, map_ys = zip(*map_points)
    center_x = (min(map_xs) + max(map_xs)) // 2
    center_y = (min(map_ys) + max(map_ys)) // 2

    # Calculate the size needed to encompass all points
    size = max(
        max(map_xs) - min(map_xs) + 2 * padding,
        max(map_ys) - min(map_ys) + 2 * padding
    )

    # Calculate square bounds centered on the points
    min_x = max(0, int(center_x - size/2))
    max_x = min(image.shape[1], int(center_x + size/2))
    min_y = max(0, int(center_y - size/2))
    max_y = min(image.shape[0], int(center_y + size/2))

    # Ensure square crop by using the smaller dimension
    crop_size = min(max_x - min_x, max_y - min_y)
    min_x = center_x - crop_size//2
    max_x = center_x + crop_size//2
    min_y = center_y - crop_size//2
    max_y = center_y + crop_size//2

    # Adjust if out of bounds
    if min_x < 0:
        min_x = 0
        max_x = crop_size
    if min_y < 0:
        min_y = 0
        max_y = crop_size
    if max_x > image.shape[1]:
        max_x = image.shape[1]
        min_x = max_x - crop_size
    if max_y > image.shape[0]:
        max_y = image.shape[0]
        min_y = max_y - crop_size

    # Crop the base map image
    cropped_map = image[min_y:max_y, min_x:max_x]

    # Calculate zoom factor maintaining aspect ratio
    WINDOW_SIZE = 800
    crop_height, crop_width = cropped_map.shape[:2]

    # Use the larger dimension to determine scale
    scale = WINDOW_SIZE / max(crop_width, crop_height)

    # Force square dimensions using the larger scaled size
    max_scaled_size = max(int(crop_width * scale), int(crop_height * scale))
    new_width = max_scaled_size
    new_height = max_scaled_size

    # Resize the map
    zoomed_map = cv2.resize(cropped_map, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    # Draw overlays using the new conversion function
    if destination_item is not None:
        dest_zoomed_x, dest_zoomed_y = convert_from_world_to_zoomed_map(
            dest_x, dest_y, min_x, min_y, scale, scale
        )
        cv2.circle(zoomed_map, (dest_zoomed_x, dest_zoomed_y), 5, (0, 0, 255), -1)

    start_zoomed_x, start_zoomed_y = convert_from_world_to_zoomed_map(
        start_x, start_y, min_x, min_y, scale, scale
    )
    cv2.circle(zoomed_map, (start_zoomed_x, start_zoomed_y), 5, (0, 255, 0), -1)

    # Draw route with new conversion
    if route_plan:
        points = [item.lane.points for item in route_plan]
        points = [point for sublist in points for point in sublist]
        zoomed_points = [
            convert_from_world_to_zoomed_map(point.x, point.z, min_x, min_y, scale, scale)
            for point in points
        ]
        for point in zoomed_points:
            cv2.circle(zoomed_map, point, 2, (255, 0, 0), -1)
        #cv2.polylines(zoomed_map, [np.array(zoomed_points)], False, (255, 0, 0), 2)

    # Only show window if not in mock mode
    if not mock_mode:
        try:
            cv2.namedWindow("Route", cv2.WINDOW_NORMAL)
            cv2.imshow("Route", zoomed_map)
            while True:
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    break
        except Exception as e:
            logging.warning(f"Failed to display route visualization: {e}")

    return zoomed_map  # Return the image for testing purposes
