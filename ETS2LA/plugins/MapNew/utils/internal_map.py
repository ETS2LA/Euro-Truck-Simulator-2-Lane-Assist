import numpy as np
import math
import data
import cv2

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

ZOOM = 1

LAST_SECTOR_X = 0
LAST_SECTOR_Y = 0

DRAW_DETAILED_ROADS = True

# https://stackoverflow.com/a/71701023
def add_transparent_image(background, foreground, x_offset=None, y_offset=None):
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
    sector_x = data.current_sector_x * 4000
    sector_z = data.current_sector_y * 4000
    local_x = x - sector_x
    local_z = z - sector_z
    return (local_x*scaling, local_z*scaling)

def InitializeMapWindow() -> None:
    cv2.namedWindow("ETS2LA Map", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ETS2LA Map", WINDOW_WIDTH, WINDOW_HEIGHT)
    cv2.setWindowProperty("ETS2LA Map", cv2.WND_PROP_TOPMOST, 1)
    
def RemoveWindow() -> None:
    cv2.destroyWindow("ETS2LA Map")
    
def SectorChanged() -> bool:
    global LAST_SECTOR_X, LAST_SECTOR_Y
    if data.current_sector_x != LAST_SECTOR_X or data.current_sector_y != LAST_SECTOR_Y:
        LAST_SECTOR_X = data.current_sector_x
        LAST_SECTOR_Y = data.current_sector_y
        return True

def DrawStats(image: np.ndarray):
    cv2.putText(image, f"Truck X: {data.truck_x}", (10*4, 20*4), cv2.FONT_HERSHEY_DUPLEX, 0.5*4, (255, 255, 255), 1*4, cv2.LINE_AA)
    cv2.putText(image, f"Truck Z: {data.truck_z}", (10*4, 40*4), cv2.FONT_HERSHEY_DUPLEX, 0.5*4, (255, 255, 255), 1*4, cv2.LINE_AA)
    cv2.putText(image, f"Sector X: {data.current_sector_x}", (10*4, 60*4), cv2.FONT_HERSHEY_DUPLEX, 0.5*4, (255, 255, 255), 1*4, cv2.LINE_AA)
    cv2.putText(image, f"Sector Y: {data.current_sector_y}", (10*4, 80*4), cv2.FONT_HERSHEY_DUPLEX, 0.5*4, (255, 255, 255), 1*4, cv2.LINE_AA)
    cv2.putText(image, f"Roads: {len(data.current_sector_roads)}", (10*4, 100*4), cv2.FONT_HERSHEY_DUPLEX, 0.5*4, (255, 255, 255), 1*4, cv2.LINE_AA)
    cv2.putText(image, f"Prefabs: {len(data.current_sector_prefabs)}", (10*4, 120*4), cv2.FONT_HERSHEY_DUPLEX, 0.5*4, (255, 255, 255), 1*4, cv2.LINE_AA)

def DrawBoundingBox(item, image: np.ndarray):
    scaling_factor = 4000 / 4000 # sector size
    min_x, min_z = ToLocalSectorCoordinates(item.bounding_box.min_x, item.bounding_box.min_y, scaling_factor)
    max_x, max_z = ToLocalSectorCoordinates(item.bounding_box.max_x, item.bounding_box.max_y, scaling_factor)
    cv2.rectangle(image, (int(min_x), int(min_z)), (int(max_x), int(max_z)), (30, 30, 30), 1)

road_image = np.zeros((4000, 4000, 3), np.uint8)
roads_done = False
def DrawRoads(sector_change: bool) -> None:
    global road_image, roads_done
    if not sector_change and road_image is not None and roads_done:
        return road_image
    
    road_image = np.zeros((4000, 4000, 3), np.uint8)
    scaling_factor = 4000 / 4000 # sector size
    
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
        if not DRAW_DETAILED_ROADS:
            poly_points = np.array([ToLocalSectorCoordinates(int((point.x)), int((point.z)), scaling_factor) for point in road.points], np.int32)
            cv2.polylines(road_image, [poly_points], isClosed=False, color=(100, 100, 100), thickness=1, lineType=cv2.LINE_AA)
        else:
            for lane in road.lanes:
                color = (0, 0, 0)
                if lane.side == "left":
                    color = (110, 140, 110)
                elif lane.side == "right":
                    color = (110, 110, 140)
                poly_points = np.array([ToLocalSectorCoordinates(int((point.x)), int((point.z)), scaling_factor) for point in lane.points], np.int32)
                cv2.polylines(road_image, [poly_points], isClosed=False, color=color, thickness=1, lineType=cv2.LINE_AA)
        
        DrawBoundingBox(road, road_image)
        #road_position = ToLocalSectorCoordinates(road.x, road.y, scaling_factor)
        #cv2.putText(road_image, f"{road.road_look.name}", (int(road_position[0])+5, int(road_position[1])), cv2.FONT_HERSHEY_DUPLEX, 0.5, (50,50,50), 1, cv2.LINE_AA)
                
    return road_image

prefab_image = np.zeros((4000, 4000, 3), np.uint8)
def DrawPrefabs(sector_change: bool) -> np.ndarray:
    global prefab_image
    if not sector_change and prefab_image is not None:
        return prefab_image
    
    prefab_image = np.zeros((4000, 4000, 3), np.uint8)
    scaling_factor = 4000 / 4000 # sector size
    for prefab in data.current_sector_prefabs:
        for route in prefab.nav_routes:
            for curve in route.curves:
                points = []
                for point in curve.points:
                    x, z = ToLocalSectorCoordinates(point.x, point.z, scaling_factor)
                    points.append((int(x), int(z)))
                    
                poly_points = np.array(points, np.int32)
                cv2.polylines(prefab_image, [poly_points], isClosed=False, color=(150, 150, 150), thickness=1, lineType=cv2.LINE_AA)
        
        #prefab_position = ToLocalSectorCoordinates(prefab.x, prefab.y, scaling_factor)
        #cv2.putText(prefab_image, f"{prefab.prefab_description.token}", (int(prefab_position[0])+5, int(prefab_position[1])), cv2.FONT_HERSHEY_DUPLEX, 0.5, (50,50,50), 1, cv2.LINE_AA)
        DrawBoundingBox(prefab, prefab_image)
                
    return prefab_image

def DrawRoutePlan(image: np.ndarray) -> None:
    plan = data.route_plan
    for section in plan:
        if section is None:
            continue    
        
        start_node = section.start_node
        x, z = ToLocalSectorCoordinates(start_node.x, start_node.y)
        cv2.circle(image, (int(x), int(z)), 2, (0, 255, 0), -1)
        
        end_node = section.end_node
        x, z = ToLocalSectorCoordinates(end_node.x, end_node.y)
        cv2.circle(image, (int(x), int(z)), 2, (0, 0, 255), -1)
        
        if section.last_actual_points == []:
            section.get_points()
            
        for i, point in enumerate(section.last_actual_points):
            if i % 2 != 0:
                continue
            x, z = ToLocalSectorCoordinates(point.x, point.z)
            cv2.circle(image, (int(x), int(z)), 2, (255, 0, 0), -1)

def DrawPlayerDot(image: np.ndarray) -> None:
    scaling_factor = 4000 / 4000 # sector size
    x, z = ToLocalSectorCoordinates(data.truck_x, data.truck_z, scaling_factor)
    cv2.circle(image, (int(x), int(z)), 5, (0, 0, 255), 1)

def AddOverlayToImage(image: np.ndarray, overlay: np.ndarray) -> None:
    return cv2.addWeighted(image, 1, overlay, 1, 0)

def ZoomImage(image: np.ndarray) -> np.ndarray:
    truck_x, truck_z = ToLocalSectorCoordinates(data.truck_x, data.truck_z)
    
    x_offset = truck_x - WINDOW_WIDTH // 2
    y_offset = truck_z - WINDOW_HEIGHT // 2
    x_offset = max(0, min(x_offset, image.shape[1] - WINDOW_WIDTH))
    y_offset = max(0, min(y_offset, image.shape[0] - WINDOW_HEIGHT))
    
    y_offset = int(y_offset)
    x_offset = int(x_offset)
    cropped_image = image[y_offset:y_offset + WINDOW_HEIGHT, x_offset:x_offset + WINDOW_WIDTH]
    return cropped_image

def DrawMap(runner) -> None:
    sector_change = SectorChanged()
    image = np.zeros((4000, 4000, 3), np.uint8)
    r_image = DrawRoads(sector_change)
    p_image = DrawPrefabs(sector_change)
    image = AddOverlayToImage(image, r_image)
    image = AddOverlayToImage(image, p_image)
    DrawRoutePlan(image)
    #DrawStats(image)
    DrawPlayerDot(image)
    
    try:
        image = ZoomImage(image)
        cv2.imshow("ETS2LA Map", image)
        cv2.waitKey(1)
    except: pass