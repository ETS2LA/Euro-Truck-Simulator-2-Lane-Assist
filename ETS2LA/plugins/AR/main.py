from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings

import dearpygui.dearpygui as dpg
from ctypes import c_int
import win32con
import win32gui
import ctypes
import math
import time
import mss
import sys


drawlist = None
sct = mss.mss()
dwm = ctypes.windll.dwmapi
runner:PluginRunner = None


def Initialize():
    global TruckSimAPI

    global screen_x
    global screen_y
    global screen_width
    global screen_height
    global window_x
    global window_y
    global window_width
    global window_height

    global fov
    global window
    global last_window_position
    
    TruckSimAPI = runner.modules.TruckSimAPI

    monitor = settings.Get("ScreenCapture", "display", 0)
    monitor = sct.monitors[(monitor + 1)]
    screen_x = monitor["left"]
    screen_y = monitor["top"]
    screen_width = monitor["width"]
    screen_height = monitor["height"]
    window_x = screen_x
    window_y = screen_y
    window_width = screen_width
    window_height = screen_height

    fov = settings.Get("AR", "FOV", 80)
    window = (screen_x, screen_y, screen_width, screen_height)
    last_window_position = (0, screen_x, screen_y, screen_width, screen_height)

    InitializeWindow()


class MARGINS(ctypes.Structure):
    _fields_ = [("cxLeftWidth", c_int),
                ("cxRightWidth", c_int),
                ("cyTopHeight", c_int),
                ("cyBottomHeight", c_int)
               ]

class Line:
    start: tuple
    end: tuple
    color: tuple
    thickness: int
    def __init__(self, start, end, color=[255, 255, 255, 255], thickness=1):
        self.start = start
        self.end = end
        self.color = color
        self.thickness = thickness
        
class ScreenLine:
    """Line that uses screen positions instead of 3D positions."""
    start: tuple
    end: tuple
    color: tuple
    thickness: int
    def __init__(self, start, end, color=[255, 255, 255, 255], thickness=1):
        self.start = start
        self.end = end
        self.color = color
        self.thickness = thickness
        
class Text:
    position: tuple
    text: str
    color: tuple
    size: int
    offset: tuple
    def __init__(self, text, position, color=[255, 255, 255, 255], size=10, offset=(0,0)):
        self.position = position
        self.text = text
        self.color = color
        self.size = size
        self.offset = offset

class Circle:
    x: int
    y: int
    radius: int
    fill: tuple
    color: tuple
    thickness: int
    def __init__(self, x, y, radius, fill=[0, 0, 0, 0], color=[255, 255, 255, 255], thickness=1):
        self.x = x
        self.y = y
        self.radius = radius
        self.fill = fill
        self.color = color
        self.thickness = thickness
        
class Box:
    x: int
    y: int
    width: int
    height: int
    fill: tuple
    color: tuple
    thickness: int
    def __init__(self, x, y, width, height, fill=[0, 0, 0, 0], color=[255, 255, 255, 255], thickness=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height 
        self.fill = fill
        self.color = color
        self.thickness = thickness
        
class Polygon:
    points: list
    fill: tuple
    color: tuple
    thickness: int
    closed: bool
    def __init__(self, points, fill=[0, 0, 0, 0], color=[255, 255, 255, 255], thickness=1, closed=False):
        self.points = points
        self.fill = fill
        self.color = color
        self.thickness = thickness
        self.closed = closed
        if closed:
            self.points.append(points[0])


def InitializeWindow():
    global window
    global window_x
    global window_y
    global window_width
    global window_height

    try:
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
                break

        dpg.create_context()
        dpg.create_viewport(title=f'ETS2LA - AR/Overlay', always_on_top=True, decorated=False, clear_color=[0.0,0.0,0.0,0.0], vsync=False, x_pos=window[0], y_pos=window[1], width=window[2], height=window[3], small_icon="frontend\\src\\assets\\favicon.ico", large_icon="frontend\\src\\assets\\favicon.ico")
        dpg.set_viewport_always_top(True)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        hwnd = win32gui.FindWindow(None, f'ETS2LA - AR/Overlay')

        margins = MARGINS(-1, -1,-1, -1)
        dwm.DwmExtendFrameIntoClientArea(hwnd, margins)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    except:
        import traceback
        print(traceback.format_exc())


def resize():
    dpg.set_viewport_pos([window_x, window_y])
    dpg.set_viewport_width(window_width)
    dpg.set_viewport_height(window_height)

def tryDictGet(dictionary, key, default):
    try:
        return dictionary[key]
    except:
        return default

def draw(data):
    global drawlist
    lines = tryDictGet(data["overlay"], "lines", [])
    screenLines = tryDictGet(data["overlay"], "screenLines", [])
    circles = tryDictGet(data["overlay"], "circles", [])
    boxes = tryDictGet(data["overlay"], "boxes", [])
    polygons = tryDictGet(data["overlay"], "polygons", [])
    texts = tryDictGet(data["overlay"], "texts", [])

    if drawlist is not None:
        dpg.delete_item(drawlist)

    with dpg.viewport_drawlist(label="draw") as drawlist:

        for line in lines:
            if None not in line.start and None not in line.end:
                dpg.draw_line([line.start[0], line.start[1]], [line.end[0], line.end[1]], color=line.color, thickness=line.thickness)

        for line in screenLines:
            if None not in line.start and None not in line.end:
                dpg.draw_line([line.start[0], line.start[1]], [line.end[0], line.end[1]], color=line.color, thickness=line.thickness)

        for circle in circles:
            if None not in [circle.x, circle.y, circle.radius]:
                dpg.draw_circle([circle.x, circle.y], circle.radius, fill=circle.fill, color=circle.color, thickness=circle.thickness)
    
        for box in boxes:
            if None not in [box.x, box.y, box.width, box.height]:
                dpg.draw_rectangle([box.x, box.y], [box.x + box.width, box.y + box.height], fill=box.fill, color=box.color, thickness=box.thickness)

        for polygon in polygons:
            valid_points = [(x, y) for x, y in polygon.points if None not in [x, y]]
            if len(valid_points) >= 3 if polygon.closed else len(valid_points) >= 2:
                dpg.draw_polygon(valid_points, fill=polygon.fill, color=polygon.color, thickness=polygon.thickness)
                
        try:
            for text in data["overlay"]["texts"]:
                if None not in text.position:
                    dpg.draw_text(text.position + text.offset, text.text, color=text.color, size=text.size)
        except: pass
    
    dpg.render_dearpygui_frame()


def ConvertToScreenCoordinate(x:float, y:float, z:float):

    head_yaw = head_rotation_degrees_x
    head_pitch = head_rotation_degrees_y
    head_roll = head_rotation_degrees_z

    rel_x = x - head_x
    rel_y = y - head_y
    rel_z = z - head_z

    cos_yaw = math.cos(math.radians(-head_yaw))
    sin_yaw = math.sin(math.radians(-head_yaw))
    new_x = rel_x * cos_yaw + rel_z * sin_yaw
    new_z = rel_z * cos_yaw - rel_x * sin_yaw

    cos_pitch = math.cos(math.radians(-head_pitch))
    sin_pitch = math.sin(math.radians(-head_pitch))
    new_y = rel_y * cos_pitch - new_z * sin_pitch
    final_z = new_z * cos_pitch + rel_y * sin_pitch

    cos_roll = math.cos(math.radians(head_roll))
    sin_roll = math.sin(math.radians(head_roll))
    final_x = new_x * cos_roll - new_y * sin_roll
    final_y = new_y * cos_roll + new_x * sin_roll

    if final_z >= 0:
        return None, None, None

    fov_rad = math.radians(fov)
    window_distance = (window_height * (4 / 3) / 2) / math.tan(fov_rad / 2)

    screen_x = (final_x / final_z) * window_distance + window_width / 2
    screen_y = (final_y / final_z) * window_distance + window_height / 2

    screen_x = window_width - screen_x

    distance = math.sqrt((rel_x ** 2) + (rel_y ** 2) + (rel_z ** 2))

    return screen_x, screen_y, distance


lastOverlayData = None
def plugin():
    global lastOverlayData
    data = {}
    data["api"] = TruckSimAPI.run(Fallback=False)
    if data["api"] == "not connected": # or data["api"]["pause"] == True:
        global drawlist
        if drawlist is not None:
            dpg.delete_item(drawlist)
            drawlist = None
        dpg.render_dearpygui_frame()
        time.sleep(0.1)
        return

    global window
    global window_x
    global window_y
    global window_width
    global window_height
    global last_window_position

    global head_x
    global head_y
    global head_z
    global head_rotation_degrees_x
    global head_rotation_degrees_y
    global head_rotation_degrees_z


    current_time = time.time()
    if last_window_position[0] + 3 < current_time:
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
                break
        if window[0] != last_window_position[1] or window[1] != last_window_position[2] or window[2] != last_window_position[3] or window[3] != last_window_position[4]:
            resize()
        last_window_position = (current_time, window[0], window[1], window[2], window[3])


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
        truck_rotation_radians_x = -math.radians(truck_rotation_degrees_x)

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
        truck_rotation_radians_x = 0

        head_rotation_degrees_x = 0
        head_rotation_degrees_y = 0
        head_rotation_degrees_z = 0

        head_x = 0
        head_y = 0
        head_z = 0


    x1, y1, d1 = ConvertToScreenCoordinate(x=10448.742, y=35.324, z=-10132.315)

    x2, y2, d2 = ConvertToScreenCoordinate(x=10453.237, y=36.324, z=-10130.404)

    x3, y3, d3 = ConvertToScreenCoordinate(x=10453.237, y=34.324, z=-10130.404)
    
    alpha_zones = [
        (30, 10, 255),
        (150, float('inf'), lambda x: 255 - int((x - 10) / 20 * 255))
    ]

    def calculate_alpha(avg_d):
        for zone in alpha_zones:
            if avg_d < zone[1]:
                if callable(zone[2]):
                    return zone[2](avg_d)
                else:
                    return zone[2]
        return 0

    if d1 != None and d2 != None and d3 != None:
        avg_d = (d1 + d2 + d3) / 3
    else:
        avg_d = 0
    alpha = calculate_alpha(avg_d)

    try:
        arData = runner.GetData(["tags.ar"])[0]
        if arData != None:
            data["overlay"] = arData
            
        else:
            raise Exception("No data")
        
        try:
            for line in data["overlay"]["lines"]:
                try:
                    startDistance = math.sqrt((line.start[0] - truck_x) ** 2 + (line.start[2] - truck_z) ** 2)
                    endDistance = math.sqrt((line.end[0] - truck_x) ** 2 + (line.end[2] - truck_z) ** 2)
                    line.start = ConvertToScreenCoordinate(line.start[0], line.start[1], line.start[2])
                    line.end = ConvertToScreenCoordinate(line.end[0], line.end[1], line.end[2])
                except:
                    data["overlay"]["lines"].remove(line)
                    continue
        except: pass
        
        try:
            for text in data["overlay"]["texts"]:
                try:
                    if len(text.position) == 3:
                        text.position = ConvertToScreenCoordinate(text.position[0], text.position[1], text.position[2])
                except:
                    data["overlay"]["texts"].remove(text)
                    continue
        except: pass
            
        if "overlay" in data:
            lastOverlayData = data["overlay"]
            
    except Exception as e:
        if lastOverlayData != None:
            data["overlay"] = lastOverlayData
        else:
            data["overlay"] = {}
            data["overlay"]["lines"] = []
            data["overlay"]["screenLines"] = []
            data["overlay"]["circles"] = []
            data["overlay"]["boxes"] = []
            data["overlay"]["polygons"] = []
            data["overlay"]["texts"] = []

    try:
        draw(data)
    except:
        import traceback    
        print(traceback.format_exc())
        pass