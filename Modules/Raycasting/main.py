from ETS2LA.Module import *

class RaycastResponse:
    point: tuple
    distance: tuple
    relativePoint: tuple

    def __init__(self, point, distance, relativePoint):
        self.point = point
        self.distance = distance
        self.relativePoint = relativePoint

    def json(self):
        return {"point": self.point, "distance": self.distance, "relativePoint": self.relativePoint}

    def fromJson(json):
        return RaycastResponse(json["point"], json["distance"], json["relativePoint"])

class Module(ETS2LAModule):
    def imports(self):
        global settings, screeninfo, mouse, numpy, time, math, os
        import ETS2LA.Utils.settings as settings
        import screeninfo
        import mouse
        import numpy
        import time
        import math
        import os

        # Check if windows or linux and import appropriate libraries
        if os.name == "nt":
            global win32gui
            import win32gui
        else:
            global display, X, Xlib, XK
            from Xlib import X, display
            import Xlib.error
            import Xlib.ext
            import Xlib.XK

        global time
        import time

    def Initialize(self):
        global API
        global FOV
        API = self.plugin.modules.TruckSimAPI
        FOV = self.plugin.modules.Camera.run().fov

        global window_x, window_y, window_width, window_height, last_window_position
        window_x = 0
        window_y = 0
        window_width = 0
        window_height = 0
        last_window_position = (0, 0, 0, 0, 0)
        
        global screen
        screen = screeninfo.get_monitors()[0]

    def UpdateGamePosition(self):
        global window_x
        global window_y
        global window_width
        global window_height
        global last_window_position

        current_time = time.perf_counter()
        if last_window_position[0] + 3 < current_time:
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


    def RaycastToPlane(self, screen_x: float, screen_y: float, plane_height: float):
        # Assuming head_rotation_degrees_x/y/z, screen, FOV, window_width, window_height are defined elsewhere
        truck_yaw = truck_rotation_degrees_x
        truck_pitch = truck_rotation_degrees_y
        truck_roll = truck_rotation_degrees_z
        
        head_yaw = -head_rotation_degrees_x
        head_pitch = -(head_rotation_degrees_y - truck_pitch)
        head_roll = -(head_rotation_degrees_z - truck_roll)
        
        screen_y = screen.height - screen_y
        
        fov_rad = math.radians(FOV)
        
        window_distance = (window_height * (4 / 3) / 2) / math.tan(fov_rad / 2)
        
        final_x = ((screen_x - window_width / 2) / window_distance)
        final_y = ((screen_y - window_height / 2) / window_distance)
        final_z = -1
        
        cos_roll = math.cos(math.radians(-head_roll))
        sin_roll = math.sin(math.radians(-head_roll))
        
        new_x = final_x * cos_roll + final_y * sin_roll
        new_y = final_y * cos_roll - final_x * sin_roll
        final_x, final_y = new_x, new_y
        
        cos_pitch = math.cos(math.radians(head_pitch))
        sin_pitch = math.sin(math.radians(head_pitch))
        new_y = final_y * cos_pitch + final_z * sin_pitch
        new_z = final_z * cos_pitch - final_y * sin_pitch
        final_y, final_z = new_y, new_z
        
        cos_yaw = math.cos(math.radians(head_yaw))
        sin_yaw = math.sin(math.radians(head_yaw))
        new_x = final_x * cos_yaw - final_z * sin_yaw
        new_z = final_z * cos_yaw + final_x * sin_yaw
        final_x, final_z = new_x, new_z
        
        if final_y == 0:
            return None
        
        t = (plane_height - head_y) / final_y
        
        x = head_x + t * final_x
        y = plane_height
        z = head_z + t * final_z
        
        return x, y, z


    def GetValuesFromAPI(self):
        global FOV
        global truck_x
        global truck_y
        global truck_z
        global truck_rotation_x
        global truck_rotation_y
        global truck_rotation_z
        global cabin_offset_x
        global cabin_offset_y
        global cabin_offset_z
        global cabin_offset_rotation_x
        global cabin_offset_rotation_y
        global cabin_offset_rotation_z
        global head_offset_x
        global head_offset_y
        global head_offset_z
        global head_offset_rotation_x
        global head_offset_rotation_y
        global head_offset_rotation_z
        global truck_rotation_degrees_x
        global truck_rotation_degrees_y
        global truck_rotation_degrees_z
        global truck_rotation_radians_x
        global truck_rotation_radians_y
        global truck_rotation_radians_z
        global head_rotation_degrees_x
        global head_rotation_degrees_y
        global head_rotation_degrees_z
        global head_x
        global head_y
        global head_z

        data = {}
        data["api"] = API.run()
        FOV = self.plugin.modules.Camera.run().fov
        try:
            truck_x = data["api"]["truckPlacement"]["coordinateX"]
            truck_y = data["api"]["truckPlacement"]["coordinateY"]
            truck_z = data["api"]["truckPlacement"]["coordinateZ"]
            truck_rotation_x = data["api"]["truckPlacement"]["rotationX"]
            truck_rotation_y = data["api"]["truckPlacement"]["rotationY"]
            truck_rotation_z = data["api"]["truckPlacement"]["rotationZ"]

            cabin_offset_x = data["api"]["headPlacement"]["cabinOffsetX"] + data["api"]["configVector"]["cabinPositionX"]
            cabin_offset_y = data["api"]["headPlacement"]["cabinOffsetY"] + data["api"]["configVector"]["cabinPositionY"]
            cabin_offset_z = data["api"]["headPlacement"]["cabinOffsetZ"] + data["api"]["configVector"]["cabinPositionZ"]
            cabin_offset_rotation_x = data["api"]["headPlacement"]["cabinOffsetrotationX"]
            cabin_offset_rotation_y = data["api"]["headPlacement"]["cabinOffsetrotationY"]
            cabin_offset_rotation_z = data["api"]["headPlacement"]["cabinOffsetrotationZ"]

            head_offset_x = data["api"]["headPlacement"]["headOffsetX"] + data["api"]["configVector"]["headPositionX"] + cabin_offset_x
            head_offset_y = data["api"]["headPlacement"]["headOffsetY"] + data["api"]["configVector"]["headPositionY"] + cabin_offset_y
            head_offset_z = data["api"]["headPlacement"]["headOffsetZ"] + data["api"]["configVector"]["headPositionZ"] + cabin_offset_z
            head_offset_rotation_x = data["api"]["headPlacement"]["headOffsetrotationX"]
            head_offset_rotation_y = data["api"]["headPlacement"]["headOffsetrotationY"]
            head_offset_rotation_z = data["api"]["headPlacement"]["headOffsetrotationZ"]

            truck_rotation_degrees_x = truck_rotation_x * 360
            if truck_rotation_degrees_x < 0:
                truck_rotation_degrees_x = 360 + truck_rotation_degrees_x
            truck_rotation_radians_x = -math.radians(truck_rotation_degrees_x)

            truck_rotation_degrees_y = truck_rotation_y * 360
            if truck_rotation_degrees_y < 0:
                truck_rotation_degrees_y = 360 + truck_rotation_degrees_y
            truck_rotation_radians_y = -math.radians(truck_rotation_degrees_y)

            truck_rotation_degrees_z = truck_rotation_z * 360
            if truck_rotation_degrees_z < 0:
                truck_rotation_degrees_z = 360 + truck_rotation_degrees_z
            truck_rotation_radians_z = -math.radians(truck_rotation_degrees_z)

            head_rotation_degrees_x = (truck_rotation_x + cabin_offset_rotation_x + head_offset_rotation_x) * 360
            while head_rotation_degrees_x > 360:
                head_rotation_degrees_x = head_rotation_degrees_x - 360

            head_rotation_degrees_y = (truck_rotation_y + cabin_offset_rotation_y + head_offset_rotation_y) * 360

            head_rotation_degrees_z = (truck_rotation_z + cabin_offset_rotation_z + head_offset_rotation_z) * 360

            point_x = head_offset_x
            point_y = head_offset_y
            point_z = head_offset_z
            head_x = point_x * math.cos(truck_rotation_radians_x) - point_z * math.sin(truck_rotation_radians_x) + truck_x
            head_y = point_y * math.cos(math.radians(head_rotation_degrees_y)) - point_z * math.sin(math.radians(head_rotation_degrees_y)) + truck_y
            head_z = point_x * math.sin(truck_rotation_radians_x) + point_z * math.cos(truck_rotation_radians_x) + truck_z
        except:
            truck_x = 0
            truck_y = 0
            truck_z = 0
            truck_rotation_x = 0
            truck_rotation_y = 0
            truck_rotation_z = 0
            cabin_offset_x = 0
            cabin_offset_y = 0
            cabin_offset_z = 0
            cabin_offset_rotation_x = 0
            cabin_offset_rotation_y = 0
            cabin_offset_rotation_z = 0
            head_offset_x = 0
            head_offset_y = 0
            head_offset_z = 0
            head_offset_rotation_x = 0
            head_offset_rotation_y = 0
            head_offset_rotation_z = 0
            truck_rotation_degrees_x = 0
            truck_rotation_degrees_y = 0
            truck_rotation_degrees_z = 0
            truck_rotation_radians_x = 0
            truck_rotation_radians_y = 0
            truck_rotation_radians_z = 0
            head_rotation_degrees_x = 0
            head_rotation_degrees_y = 0
            head_rotation_degrees_z = 0
            head_x = 0
            head_y = 0
            head_z = 0


    def run(self, x=None, y=None):
        self.GetValuesFromAPI()
        self.UpdateGamePosition()
        if window_width == 0 or window_height == 0:
            return RaycastResponse((truck_x, truck_y, truck_z), 0, (0, 0, 0))
        if x is None and y is None:
            x, y = mouse.get_position()
        x, y, z = self.RaycastToPlane(x, y, truck_y)
        distance = math.sqrt((x - truck_x) ** 2 + (y - truck_y) ** 2 + (z - truck_z) ** 2)
        relative_x = x - truck_x
        relative_y = y - truck_y
        relative_z = z - truck_z
        return RaycastResponse((x, y, z), distance, (relative_x, relative_y, relative_z))