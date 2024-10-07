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
    cv2.putText(image, f"Truck X: {data.truck_x}", (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, f"Truck Z: {data.truck_z}", (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, f"Sector X: {data.current_sector_x}", (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, f"Sector Y: {data.current_sector_y}", (10, 80), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, f"Roads: {len(data.current_sector_roads)}", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, f"Prefabs: {len(data.current_sector_prefabs)}", (10, 120), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


def DrawRoads(sector_change: bool, image: np.ndarray ) -> None:
    scaling_factor = WINDOW_HEIGHT / 4000 # sector size
    for road in data.current_sector_roads:
        if not DRAW_DETAILED_ROADS:
            poly_points = np.array([ToLocalSectorCoordinates(int((point.x)), int((point.z)), scaling_factor) for point in road.points], np.int32)
            cv2.polylines(image, [poly_points], isClosed=False, color=(255, 255, 255), thickness=1)
        else:
            for lane in road.lanes:
                poly_points = np.array([ToLocalSectorCoordinates(int((point.x)), int((point.z)), scaling_factor) for point in lane.points], np.int32)
                cv2.polylines(image, [poly_points], isClosed=False, color=(255, 255, 255), thickness=1)

def DrawPrefabs(sector_change: bool, image: np.ndarray) -> None:
    scaling_factor = WINDOW_HEIGHT / 4000 # sector size
    for prefab in data.current_sector_prefabs:
        for route in prefab.nav_routes:
            for curve in route.curves:
                points = []
                for point in curve.points:
                    x, z = ToLocalSectorCoordinates(point.x, point.z, scaling_factor)
                    points.append((int(x), int(z)))
                    
                poly_points = np.array(points, np.int32)
                cv2.polylines(image, [poly_points], isClosed=False, color=(255, 255, 255), thickness=1)

def DrawPlayerDot(image: np.ndarray) -> None:
    scaling_factor = WINDOW_HEIGHT / 4000 # sector size
    x, z = ToLocalSectorCoordinates(data.truck_x, data.truck_z, scaling_factor)
    cv2.circle(image, (int(x), int(z)), 5, (0, 0, 255), 1)

def DrawMap() -> None:
    sector_change = SectorChanged()
    
    image = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), np.uint8)
    DrawStats(image)
    DrawRoads(sector_change, image)
    DrawPrefabs(sector_change, image)
    DrawPlayerDot(image)
    
    cv2.imshow("ETS2LA Map", image)
    cv2.waitKey(1)