from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings

import dearpygui.dearpygui as dpg
import ctypes
import math
import subprocess
import time
from matplotlib.patches import Polygon as mplPolygon
import platform
import mss
import sys
import os

# Detect if running on Linux
LINUX = os.path.exists("/etc/os-release")

if not LINUX:
    import win32gui
    import win32con
    import pygetwindow as gw  # This is essential
    from ctypes import windll
    dwm = windll.dwmapi

drawlist = None
sct = mss.mss()
runner: PluginRunner = None

def get_window_info():
    if platform.system() == "Linux":
        try:
            # Get the list of all windows
            output = subprocess.check_output(["wmctrl", "-lG"], text=True)
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 8:
                    window_id, desktop, x, y, width, height, title = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], ' '.join(parts[7:])
                    if "Truck Simulator" in title:
                        return (int(x), int(y), int(width), int(height))
        except subprocess.CalledProcessError as e:
            print(f"Error running wmctrl: {e}")
    return None

def normalize_color(value):
    return value / 255

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

def InitializeWindow():
    global window
    global window_x
    global window_y
    global window_width
    global window_height

    try:
        dpg.create_context()
        dpg.create_viewport(
            title='ETS2LA - AR/Overlay', 
            always_on_top=True, 
            decorated=False, 
            clear_color=[0.0, 0.0, 0.0, 0.0], 
            vsync=False, 
            x_pos=window[0], 
            y_pos=window[1], 
            width=window[2], 
            height=window[3], 
            small_icon="frontend/src/assets/favicon.ico", 
            large_icon="frontend/src/assets/favicon.ico"
        )
        dpg.set_viewport_always_top(True)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        if not LINUX:
            hwnd = win32gui.FindWindow(None, 'ETS2LA - AR/Overlay')

            class MARGINS(ctypes.Structure):
                _fields_ = [("cxLeftWidth", ctypes.c_int),
                            ("cxRightWidth", ctypes.c_int),
                            ("cyTopHeight", ctypes.c_int),
                            ("cyBottomHeight", ctypes.c_int)]

            margins = MARGINS(-1, -1, -1, -1)
            dwm.DwmExtendFrameIntoClientArea(hwnd, margins)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        else:
            # Linux alternative to making the window always on top and transparent
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk, Gdk

            window = Gtk.Window()
            window.set_title('ETS2LA - AR/Overlay')
            window.set_keep_above(True)
            window.set_app_paintable(True)
            screen = window.get_screen()
            visual = screen.get_rgba_visual()
            if visual:
                window.set_visual(visual)
            window.connect('destroy', Gtk.main_quit)
            window.show_all()

    except Exception as e:
        print(f"Error initializing window: {e}")
        import traceback
        print(traceback.format_exc())

def resize():
    dpg.set_viewport_pos([window_x, window_y])
    dpg.set_viewport_width(window_width)
    dpg.set_viewport_height(window_height)

def tryDictGet(dictionary, key, default):
    try:
        return dictionary[key]
    except KeyError:
        return default

def draw(data):
    global drawlist
    lines = tryDictGet(data["overlay"], "lines", [])
    screenLines = tryDictGet(data["overlay"], "screenLines", [])
    circles = tryDictGet(data["overlay"], "circles", [])
    boxes = tryDictGet(data["overlay"], "boxes", [])
    polygons = tryDictGet(data["overlay"], "polygons", [])
    texts = tryDictGet(data["overlay"], "texts", [])
    
    # Draw each item
    for line in lines:
        dpg.draw_line(p1=line.start, p2=line.end, color=line.color, thickness=line.thickness, parent=drawlist)
    
    for screenLine in screenLines:
        dpg.draw_line(p1=screenLine.start, p2=screenLine.end, color=screenLine.color, thickness=screenLine.thickness, parent=drawlist)
    
    for circle in circles:
        dpg.draw_circle(center=[circle.x, circle.y], radius=circle.radius, color=circle.color, thickness=circle.thickness, fill=circle.fill, parent=drawlist)
    
    for box in boxes:
        dpg.draw_rectangle(pmin=[box.x, box.y], pmax=[box.x + box.width, box.y + box.height], color=box.color, thickness=box.thickness, fill=box.fill, parent=drawlist)
    
    for polygon in polygons:
        dpg.draw_polygon(points=polygon.points, color=polygon.color, thickness=polygon.thickness, fill=polygon.fill, parent=drawlist)

    for text in texts:
        dpg.draw_text(pos=[text.position[0] + text.offset[0], text.position[1] + text.offset[1]], text=text.text, color=text.color, size=text.size, parent=drawlist)

def ConvertToScreenCoordinate(x: float, y: float, z: float):
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
    
    if data["api"] == "not connected":
        global drawlist
        if drawlist is not None:
            dpg.delete_item(drawlist)
            drawlist = None
        dpg.render_dearpygui_frame()
        time.sleep(0.1)
        return

    global window, window_x, window_y, window_width, window_height, last_window_position
    global head_x, head_y, head_z, head_rotation_degrees_x, head_rotation_degrees_y, head_rotation_degrees_z

    current_time = time.time()
    if last_window_position[0] + 3 < current_time:
        window = None
        windows = gw.getWindowsWithTitle("Truck Simulator")
        if windows:
            win = windows[0]
            rect = win._rect  # pygetwindow provides the rectangle for the window
            window = (rect.left, rect.top, rect.width, rect.height)
            window_x, window_y, window_width, window_height = window
        if window and (window[0] != last_window_position[1] or window[1] != last_window_position[2] or window[2] != last_window_position[3] or window[3] != last_window_position[4]):
            resize()
        last_window_position = (current_time, window[0], window[1], window[2], window[3])

    try:
        truck_x = data["api"].get("truckPlacement", {}).get("coordinateX", 0)
        truck_y = data["api"].get("truckPlacement", {}).get("coordinateY", 0)
        truck_z = data["api"].get("truckPlacement", {}).get("coordinateZ", 0)
        truck_rotation_x = data["api"].get("truckPlacement", {}).get("rotationX", 0)
        truck_rotation_y = data["api"].get("truckPlacement", {}).get("rotationY", 0)
        truck_rotation_z = data["api"].get("truckPlacement", {}).get("rotationZ", 0)

        cabin_offset_x = data["api"].get("headPlacement", {}).get("cabinOffsetX", 0) + data["api"].get("configVector", {}).get("cabinPositionX", 0)
        cabin_offset_y = data["api"].get("headPlacement", {}).get("cabinOffsetY", 0) + data["api"].get("configVector", {}).get("cabinPositionY", 0)
        cabin_offset_z = data["api"].get("headPlacement", {}).get("cabinOffsetZ", 0) + data["api"].get("configVector", {}).get("cabinPositionZ", 0)
        cabin_offset_rotation_x = data["api"].get("headPlacement", {}).get("cabinOffsetrotationX", 0)
        cabin_offset_rotation_y = data["api"].get("headPlacement", {}).get("cabinOffsetrotationY", 0)
        cabin_offset_rotation_z = data["api"].get("headPlacement", {}).get("cabinOffsetrotationZ", 0)

        head_offset_x = data["api"].get("headPlacement", {}).get("headOffsetX", 0) + data["api"].get("configVector", {}).get("headPositionX", 0) + cabin_offset_x
        head_offset_y = data["api"].get("headPlacement", {}).get("headOffsetY", 0) + data["api"].get("configVector", {}).get("headPositionY", 0) + cabin_offset_y
        head_offset_z = data["api"].get("headPlacement", {}).get("headOffsetZ", 0) + data["api"].get("configVector", {}).get("headPositionZ", 0) + cabin_offset_z
        head_offset_rotation_x = data["api"].get("headPlacement", {}).get("headOffsetrotationX", 0)
        head_offset_rotation_y = data["api"].get("headPlacement", {}).get("headOffsetrotationY", 0)
        head_offset_rotation_z = data["api"].get("headPlacement", {}).get("headOffsetrotationZ", 0)
        
        truck_rotation_degrees_x = truck_rotation_x * 360
        truck_rotation_radians_x = -math.radians(truck_rotation_degrees_x)

        head_rotation_degrees_x = (truck_rotation_x + cabin_offset_rotation_x + head_offset_rotation_x) * 360
        while head_rotation_degrees_x > 360:
            head_rotation_degrees_x -= 360

        head_rotation_degrees_y = (truck_rotation_y + cabin_offset_rotation_y + head_offset_rotation_y) * 360
        head_rotation_degrees_z = (truck_rotation_z + cabin_offset_rotation_z + head_offset_rotation_z) * 360

        point_x = head_offset_x
        point_y = head_offset_y
        point_z = head_offset_z
        head_x = point_x * math.cos(truck_rotation_radians_x) - point_z * math.sin(truck_rotation_radians_x) + truck_x
        head_y = point_y * math.cos(math.radians(head_rotation_degrees_y)) - point_z * math.sin(math.radians(head_rotation_degrees_y)) + truck_y
        head_z = point_x * math.sin(truck_rotation_radians_x) + point_z * math.cos(truck_rotation_radians_x) + truck_z

    except:
        truck_x = truck_y = truck_z = truck_rotation_x = truck_rotation_y = truck_rotation_z = 0
        cabin_offset_x = cabin_offset_y = cabin_offset_z = cabin_offset_rotation_x = cabin_offset_rotation_y = cabin_offset_rotation_z = 0
        head_offset_x = head_offset_y = head_offset_z = head_offset_rotation_x = head_offset_rotation_y = head_offset_rotation_z = 0
        truck_rotation_degrees_x = truck_rotation_radians_x = 0
        head_rotation_degrees_x = head_rotation_degrees_y = head_rotation_degrees_z = 0
        head_x = head_y = head_z = 0

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

    if d1 is not None and d2 is not None and d3 is not None:
        avg_d = (d1 + d2 + d3) / 3
    else:
        avg_d = 0
    alpha = calculate_alpha(avg_d)

    try:
        arData = runner.GetData(["tags.ar"])[0]
        if arData is not None:
            data["overlay"] = arData
        else:
            raise Exception("No data")
        
        for line in data["overlay"].get("lines", []):
            try:
                startDistance = math.sqrt((line.start[0] - truck_x) ** 2 + (line.start[2] - truck_z) ** 2)
                endDistance = math.sqrt((line.end[0] - truck_x) ** 2 + (line.end[2] - truck_z) ** 2)
                line.start = ConvertToScreenCoordinate(line.start[0], line.start[1], line.start[2])
                line.end = ConvertToScreenCoordinate(line.end[0], line.end[1], line.end[2])
            except:
                data["overlay"]["lines"].remove(line)
                continue
        
        for text in data["overlay"].get("texts", []):
            try:
                if len(text.position) == 3:
                    text.position = ConvertToScreenCoordinate(text.position[0], text.position[1], text.position[2])
            except:
                data["overlay"]["texts"].remove(text)
                continue
            
        lastOverlayData = data["overlay"]
    except Exception as e:
        if lastOverlayData is not None:
            data["overlay"] = lastOverlayData
        else:
            data["overlay"] = {"lines": [], "screenLines": [], "circles": [], "boxes": [], "polygons": [], "texts": []}

    # Convert colors to [0, 1] range
    fill_color = [1.0, 1.0, 1.0, alpha * 0.5]
    edge_color = [1.0, 1.0, 1.0, alpha]

    # Add polygon with normalized colors
    data["overlay"]["polygons"].append({
        "type": "polygon",
        "points": [[x1, y1], [x2, y2], [x3, y3]],
        "fill": fill_color,
        "color": edge_color,
        "closed": True
    })

    try:
        draw(data)
    except:
        import traceback
        print(traceback.format_exc())
        pass