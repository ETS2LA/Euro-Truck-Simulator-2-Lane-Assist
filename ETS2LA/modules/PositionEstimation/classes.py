import ETS2LA.backend.settings as settings
import time
import math
import os


if os.name == "nt":
    import win32gui
else:
    from Xlib import X, display
    import Xlib.error
    import Xlib.ext
    import Xlib.XK

window_x = 0
window_y = 0
window_width = 0
window_height = 0
last_window_position = (0, 0, 0, 0, 0)
fov = settings.Get("global", "FOV", 77)

def UpdateFOV(settings): global fov ; fov = settings["FOV"]
settings.Listen("global", UpdateFOV)

# MARK: Helper functions
def ConvertToAngle(x, y):
    fov_rad = math.radians(fov)
    # 4/3 because that's what ETS2 uses to calculate the FOV
    window_distance = (window_height * (4 / 3) / 2) / math.tan(fov_rad / 2)
    angle_x = math.atan2(x - window_width / 2, window_distance) * (180 / math.pi)
    angle_y = math.atan2(y - window_height / 2, window_distance) * (180 / math.pi)
    return angle_x, angle_y

def UpdateGamePosition():
    if os.name == "nt":
        # Windows-specific code
        hwnd = None
        top_windows = []
        win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
        for hwnd, window_text in top_windows:
            if "Truck Simulator" in window_text and "Discord" not in window_text:
                rect = win32gui.GetClientRect(hwnd)
                tl = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
                br = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
                window = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
                window_x = window[0]
                window_y = window[1]
                window_width = window[2]
                window_height = window[3]
                last_window_position = (current_time, window[0], window[1], window[2], window[3])
                break
    else:
        # Linux-specific code
        d = display.Display()
        root = d.screen().root
        top_windows = root.query_tree().children
        for window in top_windows:
            try:
                window_name = window.get_wm_name()
                if window_name and "Truck Simulator" in window_name and "Discord" not in window_name:
                    geom = window.get_geometry()
                    window_attrs = window.get_attributes()
                    window_x = geom.x
                    window_y = geom.y
                    window_width = geom.width
                    window_height = geom.height
                    last_window_position = (current_time, window_x, window_y, window_width, window_height)
                    break
            except (Xlib.error.XError, AttributeError):
                continue



# MARK: Classes
class HeadTranslation:
    x: float
    y: float
    z: float
    angle: float
    rotation: float
    
    def __init__(self, x: float, y: float, z: float, angle: float, rotation: float):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.rotation = rotation
    
    def json(self):
        return {"x": self.x, "y": self.y, "z": self.z, "angle": self.angle, "rotation": self.rotation}
    
    def fromJson(json):
        return HeadTranslation(json["x"], json["y"], json["z"], json["angle"], json["rotation"])

class ObjectDetection:
    x: float
    y: float
    width: float
    height: float
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def json(self):
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height, "state": self.state}
    
    def fromJson(json):
        return ObjectDetection(json["x"], json["y"], json["width"], json["height"], json["state"])

class Position:
    x: float
    y: float
    z: float
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        
    def tuple(self) -> tuple:
        return (self.x, self.y, self.z)
    
    def json(self):
        return {"x": self.x, "y": self.y, "z": self.z}
    
    def fromJson(json):
        return Position(json["x"], json["y"], json["z"])

class ObjectTrack():
    id: str
    _detection: ObjectDetection = None
    _head_translation: HeadTranslation = None
    first_detection: ObjectDetection
    first_head_translation: HeadTranslation
    previous_detection: ObjectDetection
    previous_head_translation: HeadTranslation
    position: Position = None
    last_update_time: float = 0
    
    @property
    def detection(self):
        return self._detection
    
    @detection.setter
    def detection(self, value):
        if not self._detection:
            self._detection = value
        self.previous_detection = self._detection
        self._detection = value
        
    @property
    def head_translation(self):
        return self._head_translation
    
    @head_translation.setter
    def head_translation(self, value):
        if not self._head_translation:
            self._head_translation = value
        self.previous_head_translation = self._head_translation
        self._head_translation = value
    
    def __init__(self, id: str, detection: ObjectDetection, head_translation: HeadTranslation):
        self.id = id
        self.detection = detection
        self.first_detection = detection    
        self.head_translation = head_translation
        self.first_head_translation = head_translation
        self.position = None
        self.last_update_time = time.time()
        
    def update(self, detection: ObjectDetection, head_translation: HeadTranslation):
        # This function is originally made by Glas42 for the TLD plugin.
        # Modified and adapted by Tumppi066 for the TrafficLightDetection plugin.
        self.detection = detection
        self.head_translation = head_translation
        
        x = detection.x
        y = detection.y
        w = detection.width
        h = detection.height

        angle_offset = self.first_head_translation.rotation - self.head_translation.rotation
        head_angle = self.head_translation.angle
        first_head_angle = self.first_head_translation.angle

        angle_A = 180 - head_angle - angle_offset
        angle_B = first_head_angle
        if angle_B < 0:
            angle_B = 360 + angle_B

        position_A = head_translation.x, head_translation.z
        position_B = self.first_head_translation.x, self.first_head_translation.z
        if math.sqrt((position_B[0] - position_A[0]) ** 2 + (position_B[1] - position_A[1]) ** 2) > 0.01:
            angle_A_rad = math.radians(angle_A)
            angle_B_rad = math.radians(angle_B)
            angle_C_rad = math.pi - angle_A_rad - angle_B_rad
            distance_AB = math.sqrt((position_B[0] - position_A[0]) ** 2 + (position_B[1] - position_A[1]) ** 2)
            if math.sin(angle_C_rad) != 0:
                length_A = distance_AB * math.sin(angle_A_rad) / math.sin(angle_C_rad)
                length_B = distance_AB * math.sin(angle_B_rad) / math.sin(angle_C_rad)
            else:
                length_A = distance_AB
                length_B = distance_AB
            position_C_x = length_B * math.cos(angle_A_rad)
            position_C_y = length_B * math.sin(angle_A_rad)
            direction_AB = (position_B[0] - position_A[0], position_B[1] - position_A[1])
            length_AB = math.sqrt(direction_AB[0] ** 2 + direction_AB[1] ** 2)
            if length_AB == 0:
                length_AB = 0.0001
            direction_unit_AB = (direction_AB[0] / length_AB, direction_AB[1] / length_AB)
            direction_unit_perpendicular_ab = (-direction_unit_AB[1], direction_unit_AB[0])
            position_C = (position_A[0] + position_C_x * direction_unit_AB[0] - position_C_y * direction_unit_perpendicular_ab[0], position_A[1] + position_C_x * direction_unit_AB[1] - position_C_y * direction_unit_perpendicular_ab[1])

            object_x, object_z = position_C

            angle = ConvertToAngle(x, y)[1]
            distance = math.sqrt((object_x - head_translation.x)**2 + (object_z - head_translation.z)**2)
            object_y = head_translation.y + (math.sin(angle) / distance if distance != 0 else 0.0001)

            if self.position != None:
                previous_object_x = self.position.x
                previous_object_y = self.position.y
                previous_object_z = self.position.z
                object_x = previous_object_x + (object_x - previous_object_x)
                object_y = previous_object_y + (object_y - previous_object_y)
                object_z = previous_object_z + (object_z - previous_object_z)
                
            self.position = Position(object_x, object_y, object_z)
            self.last_update_time = time.time()
        
    def json(self):
        return {"id": self.id, "detection": self.detection.json()}
    
    def fromJson(json):
        return ObjectTrack(json["id"], ObjectDetection.fromJson(json["detection"]))