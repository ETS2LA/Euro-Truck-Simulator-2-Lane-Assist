import Plugins.Map.utils.prefab_helpers as prefab_helpers
import Plugins.Map.utils.road_helpers as road_helpers
import Plugins.Map.data as data
import numpy as np
import subprocess
import math
import cv2

# Change These
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
LINE_THICKNESS = 1
FONT_SIZE = 0.5
ZOOM = 3

# Don't change these
LAST_SECTOR_X = 0
LAST_SECTOR_Y = 0
HIGHLIGHTED_ROAD = None
LAST_HIGHLIGHTED_ROAD = None
HIGHLIGHTED_UID = None
LAST_HIGHLIGHTED_UID = None

DRAW_DETAILED_ROADS = True
HIGHLIGHT_ROAD = True # When a bounding box is hovered, all roads with the name of the highlighted road will be highlighted
SCALING_FACTOR = 300 / 100

RESOLUTION = int(1000 * SCALING_FACTOR)
MOUSE_POSITION = (0,0,0)

def on_scroll(event, x, y, flags, param):
    global ZOOM
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            ZOOM *= 1.1
        else:
            ZOOM /= 1.1
        ZOOM = max(1, min(ZOOM, 10))  # Limit zoom level between 1 and 10

def on_mouse_move(event, x, y, flags, param):
    on_scroll(event, x, y, flags, param)
    
    global HIGHLIGHTED_ROAD, HIGHLIGHTED_UID, MOUSE_POSITION
    HIGHLIGHTED_ROAD = None
    HIGHLIGHTED_UID = None
    
    if not HIGHLIGHT_ROAD:
        return
    
    x = int(x/ZOOM + data.truck_x - RESOLUTION/2/ZOOM/SCALING_FACTOR)
    y = int(y/ZOOM + data.truck_z - RESOLUTION/2/ZOOM/SCALING_FACTOR)
    
    MOUSE_POSITION = (x, 0, y)

    closest_distance = math.inf
    for road in data.current_sector_roads:
        if road.bounding_box.min_x <= x <= road.bounding_box.max_x and road.bounding_box.min_y <= y <= road.bounding_box.max_y:
            center = road.bounding_box.center()
            distance = math.sqrt((x - center.x) ** 2 + (y - center.y) ** 2)
            if distance < closest_distance:
                HIGHLIGHTED_ROAD = road.road_look.name
                HIGHLIGHTED_UID = road.uid
                closest_distance = distance
            
    
    if event == cv2.EVENT_LBUTTONDOWN and HIGHLIGHTED_ROAD: # Copy to clipboard on left click
        subprocess.Popen(['clip'], stdin=subprocess.PIPE).communicate(HIGHLIGHTED_ROAD.encode('utf-8'))

# https://stackoverflow.com/a/71701023
def AddTransparentLayer(background, foreground, x_offset=None, y_offset=None):
    bg_h, bg_w, bg_channels = background.shape
    fg_h, fg_w, fg_channels = foreground.shape

    assert bg_channels == 3, f'background image should have exactly 3 channels (RGB). found:{bg_channels}'
    assert fg_channels == 4, f'foreground image should have exactly 4 channels (RGBA). found:{fg_channels}'

    # center by default
    if x_offset is None: x_offset = (bg_w - fg_w) // 2
    if y_offset is None: y_offset = (bg_h - fg_h) // 2

    w = min(fg_w, bg_w, fg_w + x_offset, bg_w - x_offset)
    h = min(fg_h, bg_h, fg_h + y_offset, bg_h - y_offset)

    if w < 1 or h < 1: return

    # clip foreground and background images to the overlapping regions
    bg_x = max(0, x_offset)
    bg_y = max(0, y_offset)
    fg_x = max(0, x_offset * -1)
    fg_y = max(0, y_offset * -1)
    foreground = foreground[fg_y:fg_y + h, fg_x:fg_x + w]
    background_subsection = background[bg_y:bg_y + h, bg_x:bg_x + w]

    # separate alpha and color channels from the foreground image
    foreground_colors = foreground[:, :, :3]
    alpha_channel = foreground[:, :, 3] / 255  # 0-255 => 0.0-1.0

    # construct an alpha_mask that matches the image shape
    alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

    # combine the background with the overlay image weighted by alpha
    composite = background_subsection * (1 - alpha_mask) + foreground_colors * alpha_mask

    # overwrite the section of the background image that has been updated
    background[bg_y:bg_y + h, bg_x:bg_x + w] = composite

def ToLocalSectorCoordinates(x: float, z: float, scaling: float = 1) -> tuple[int, int]:
    sector_x = (data.current_sector_x - 2) * 200
    sector_z = (data.current_sector_y - 2) * 200
    local_x = x - sector_x
    local_z = z - sector_z
    return (local_x*scaling, local_z*scaling)

def InitializeMapWindow() -> None:
    cv2.namedWindow("ETS2LA Map", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ETS2LA Map", WINDOW_WIDTH, WINDOW_HEIGHT)
    cv2.setWindowProperty("ETS2LA Map", cv2.WND_PROP_TOPMOST, 1)
    cv2.setMouseCallback("ETS2LA Map", on_mouse_move)
    
def RemoveWindow() -> None:
    cv2.destroyWindow("ETS2LA Map")
    cv2.setMouseCallback("ETS2LA Map", None)
    
def SectorChanged() -> bool:
    global LAST_SECTOR_X, LAST_SECTOR_Y
    if data.current_sector_x != LAST_SECTOR_X or data.current_sector_y != LAST_SECTOR_Y:
        LAST_SECTOR_X = data.current_sector_x
        LAST_SECTOR_Y = data.current_sector_y
        return True

def DrawStats(image: np.ndarray):
    # Top left
    cv2.putText(image, f"WARNING: This map is only indicative. Check all offsets in game!", (10, 20), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (100, 100, 220), 1, cv2.LINE_AA)
    perf = data.plugin.performance[-1][-1]
    cv2.putText(image, f"FPS: {1/perf:.1f}", (10, 40), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (220, 220, 220) if (1/perf > 15) else (100, 220, 220), 1, cv2.LINE_AA)
    
    # Bottom left
    coordinates = (data.truck_x, data.truck_y, data.truck_z)
    cv2.putText(image, f"Coordinates: {coordinates}", (10, WINDOW_HEIGHT-12), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (220, 220, 220), 1, cv2.LINE_AA)
    sector = (data.current_sector_x, data.current_sector_y)
    cv2.putText(image, f"Sector: {sector}", (10, WINDOW_HEIGHT-32), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (220, 220, 220), 1, cv2.LINE_AA)
    cities = data.map.cities
    closest = None
    closest_distance = math.inf
    for city in cities:
        distance = math.sqrt((coordinates[0] - city.x) ** 2 + (coordinates[2] - city.y) ** 2)
        if distance < closest_distance:
            closest_distance = distance
            closest = city
    cv2.putText(image, f"Closest city: {closest.token.capitalize()}, {closest.country_token.capitalize()} ({closest_distance / 1000:.1f}km)", (10, WINDOW_HEIGHT-62), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (220, 220, 220), 1, cv2.LINE_AA)
    
    # Bottom Right
    cv2.putText(image, f"Roads: {len(data.current_sector_roads)}", (WINDOW_WIDTH - 110, WINDOW_HEIGHT-12), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(image, f"Prefabs: {len(data.current_sector_prefabs)}", (WINDOW_WIDTH - 110, WINDOW_HEIGHT-32), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (220, 220, 220), 1, cv2.LINE_AA)

def DrawBoundingBox(item, image: np.ndarray):
    min_x, min_z = ToLocalSectorCoordinates(item.bounding_box.min_x, item.bounding_box.min_y, SCALING_FACTOR)
    max_x, max_z = ToLocalSectorCoordinates(item.bounding_box.max_x, item.bounding_box.max_y, SCALING_FACTOR)
    cv2.rectangle(image, (int(min_x), int(min_z)), (int(max_x), int(max_z)), (30, 30, 30), 1)

road_image = np.zeros((RESOLUTION, RESOLUTION, 3), np.uint8)
roads_done = False
def DrawRoads(sector_change: bool) -> None:
    global road_image, roads_done, LAST_HIGHLIGHTED_ROAD, LAST_HIGHLIGHTED_UID
    if not sector_change and road_image is not None and roads_done \
       and HIGHLIGHTED_ROAD == LAST_HIGHLIGHTED_ROAD and HIGHLIGHTED_UID == LAST_HIGHLIGHTED_UID:
        return road_image
    
    road_image = np.zeros((RESOLUTION, RESOLUTION, 3), np.uint8)
    
    # Check for roads done:
    for road in data.current_sector_roads:
        if data.heavy_calculations_this_frame >= data.allowed_heavy_calculations:
            break
        if not DRAW_DETAILED_ROADS:
            test = road.points
        else: 
            for lane in road.lanes:
                test = lane.points
                
    if data.heavy_calculations_this_frame >= data.allowed_heavy_calculations:
        roads_done = False
        cv2.putText(road_image, "Calculating roads...", (10*4, 140*4), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)
        return road_image
    else:
        roads_done = True
    
    for road in data.current_sector_roads:
        road_highlighted = HIGHLIGHTED_ROAD is not None and HIGHLIGHTED_ROAD == road.road_look.name
        if not DRAW_DETAILED_ROADS:
            poly_points = np.array([ToLocalSectorCoordinates(int((point.x)), int((point.z)), SCALING_FACTOR) for point in road.points], np.int32)
            cv2.polylines(road_image, [poly_points], isClosed=False, color=(100, 100, 100), thickness=LINE_THICKNESS, lineType=cv2.LINE_AA)
        else:
            for lane in road.lanes:
                if road_highlighted:
                    color = (0, 225, 255)
                elif lane.side == "left":
                    color = (110, 140, 110)
                elif lane.side == "right":
                    color = (110, 110, 140)
                else:
                    color = (0, 0, 0)
                poly_points = np.array([ToLocalSectorCoordinates(int((point.x)), int((point.z)), SCALING_FACTOR) for point in lane.points], np.int32)
                cv2.polylines(road_image, [poly_points], isClosed=False, color=color, thickness=LINE_THICKNESS, lineType=cv2.LINE_AA)
        
        if road.uid == HIGHLIGHTED_UID:    
            DrawBoundingBox(road, road_image)
            top_right = (road.bounding_box.max_x, road.bounding_box.min_y)
            road_position = ToLocalSectorCoordinates(top_right[0], top_right[1] + 5, SCALING_FACTOR)
            
            text_color = (0, 255, 255) if road_highlighted else (50, 50, 50)  # Yellow when hovered
            
            offset = road_helpers.GetOffset(road)
            has_per_name = road.road_look.name in road_helpers.per_name
            rule_offset = 999
            for rule in road_helpers.rules:
                rule = rule.replace("**", "")
                if rule in road.road_look.name:
                    rule_offset = road_helpers.rules["**" + rule]
            has_rule = rule_offset != 999
            
            cv2.putText(road_image, f"{road.road_look.name} ({road.uid})", (int(road_position[0] + 5*SCALING_FACTOR), int(road_position[1])), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, text_color, 1, cv2.LINE_AA)
            cv2.putText(road_image, f"Current offset: {offset}m", (int(road_position[0] + 5*SCALING_FACTOR), int(road_position[1] + 8*SCALING_FACTOR)), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, text_color, 1, cv2.LINE_AA)
            cv2.putText(road_image, f"Reason: {'Internal' if not has_rule and not has_per_name else 'Per Name' if has_per_name else 'Rule'}", (int(road_position[0] + 5*SCALING_FACTOR), int(road_position[1] + 16*SCALING_FACTOR)), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, text_color, 1, cv2.LINE_AA)
                
            start_node = road.start_node
            end_node = road.end_node
            if start_node and end_node:
                items = [
                    start_node.forward_item_uid, start_node.backward_item_uid,
                    end_node.forward_item_uid, end_node.backward_item_uid
                ]
                items = [
                    item for item in items if item != road.uid
                ]
                items = [
                    data.map.get_item_by_uid(item) for item in items
                ]
                for item in items:
                    if item != None:
                        try:
                            if getattr(item, "nav_routes"):
                                for lane in road.lanes:
                                    start_point = lane.points[0]
                                    end_point = lane.points[-1]
                                    route, distance = prefab_helpers.get_closest_lane(item, start_point.x, start_point.z, return_distance=True)
                                    route_end, distance_end = prefab_helpers.get_closest_lane(item, end_point.x, end_point.z, return_distance=True)
                                    if distance < distance_end:
                                        text_pos = ToLocalSectorCoordinates(start_point.x, start_point.z, SCALING_FACTOR)
                                        text_pos = (int(text_pos[0]), int(text_pos[1]))
                                        cv2.putText(road_image, f"{distance:.2f}m", (text_pos), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE/2, (255,255,255), 1, cv2.LINE_AA)
                                    else:
                                        text_pos = ToLocalSectorCoordinates(end_point.x, end_point.z, SCALING_FACTOR)
                                        text_pos = (int(text_pos[0]), int(text_pos[1]))
                                        cv2.putText(road_image, f"{distance_end:.2f}m", (text_pos), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE/2, (255,255,255), 1, cv2.LINE_AA)
                        except:
                            pass
                
                
    LAST_HIGHLIGHTED_ROAD = HIGHLIGHTED_ROAD
    LAST_HIGHLIGHTED_UID = HIGHLIGHTED_UID
    return road_image

prefab_image = np.zeros((RESOLUTION, RESOLUTION, 3), np.uint8)
def DrawPrefabs(sector_change: bool) -> np.ndarray:
    global prefab_image
    if not sector_change and prefab_image is not None:
        return prefab_image
    
    prefab_image = np.zeros((RESOLUTION, RESOLUTION, 3), np.uint8)
    for prefab in data.current_sector_prefabs:
        for route in prefab.nav_routes:
            for curve in route.curves:
                points = []
                for point in curve.points:
                    x, z = ToLocalSectorCoordinates(point.x, point.z, SCALING_FACTOR)
                    points.append((int(x), int(z)))
                    
                poly_points = np.array(points, np.int32)
                cv2.polylines(prefab_image, [poly_points], isClosed=False, color=(150, 150, 150), thickness=LINE_THICKNESS, lineType=cv2.LINE_AA)
        
        #prefab_position = ToLocalSectorCoordinates(prefab.x, prefab.y, SCALING_FACTOR)
        #cv2.putText(prefab_image, f"{prefab.prefab_description.token}", (int(prefab_position[0])+5, int(prefab_position[1])), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (50,50,50), 1, cv2.LINE_AA)
                
    return prefab_image

def DrawRoutePlan(image: np.ndarray) -> None:
    points = data.route_points
    points = [(point.x, point.z) for point in points]
    points = [(ToLocalSectorCoordinates(point[0], point[1], SCALING_FACTOR)) for point in points]
    points = [(int(point[0]), int(point[1])) for point in points]
    for point in points:
        cv2.circle(image, point, 3, (255, 100, 0), -1)

def DrawCircles(image: np.ndarray) -> None:
    circles = data.circles + [MOUSE_POSITION]
    for i, circle in enumerate(circles):
        if isinstance(circle, tuple):
            x, z = ToLocalSectorCoordinates(circle[0], circle[2], SCALING_FACTOR)   
        else:
            x, z = ToLocalSectorCoordinates(circle.x, circle.z, SCALING_FACTOR)
        if x < RESOLUTION and x > 0 and z < RESOLUTION and z > 0:
            cv2.circle(image, (int(x), int(z)), 3, (255, 255, 255), -1)
            cv2.putText(image, f"{i}", (int(x), int(z)), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, (255, 255, 255), 1, cv2.LINE_AA)

def DrawPlayerDot(image: np.ndarray) -> None:
    x, z = ToLocalSectorCoordinates(data.truck_x, data.truck_z, SCALING_FACTOR)
    cv2.circle(image, (int(x), int(z)), 5, (0, 0, 255), 1)

def AddOverlayToImage(image: np.ndarray, overlay: np.ndarray) -> None:
    return cv2.addWeighted(image, 1, overlay, 1, 0)

def ZoomImage(image: np.ndarray) -> np.ndarray:
    # Calculate view dimensions based on zoom
    view_width = int(RESOLUTION / ZOOM)
    view_height = int(RESOLUTION / ZOOM)
    
    # Get truck position
    truck_x, truck_z = ToLocalSectorCoordinates(data.truck_x, data.truck_z, SCALING_FACTOR)
    
    # Calculate offsets with zoom consideration
    x_offset = truck_x - view_width // 2
    y_offset = truck_z - view_height // 2
    
    # Ensure we don't go out of bounds
    x_offset = max(0, min(x_offset, image.shape[1] - view_width))
    y_offset = max(0, min(y_offset, image.shape[0] - view_height))
    
    # Convert to integers
    y_offset = int(y_offset)
    x_offset = int(x_offset)
    
    # Crop the image to the zoomed view size
    cropped_image = image[y_offset:y_offset + view_height, x_offset:x_offset + view_width]
    
    # Resize the cropped image back to window size
    resized_image = cv2.resize(cropped_image, (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation=cv2.INTER_LINEAR)
    
    return resized_image

def DrawMap() -> None:
    sector_change = SectorChanged()
    image = np.zeros((RESOLUTION, RESOLUTION, 3), np.uint8)
    r_image = DrawRoads(sector_change)
    p_image = DrawPrefabs(sector_change)
    image = AddOverlayToImage(image, r_image)
    image = AddOverlayToImage(image, p_image)
    DrawRoutePlan(image)
    DrawPlayerDot(image)
    DrawCircles(image)
    
    try:
        image = ZoomImage(image)
        DrawStats(image)
        cv2.imshow("ETS2LA Map", image)
        cv2.waitKey(1)
    except: pass