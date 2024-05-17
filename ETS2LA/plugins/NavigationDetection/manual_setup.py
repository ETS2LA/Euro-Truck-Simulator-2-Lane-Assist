from tkinter import messagebox
import numpy as np
import ctypes
import mouse
import json
import cv2
import mss
import os


window_name = "NavigationDetection - Manual Setup"
example_window_name = "NavigationDetection - Example"
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) + "\\"


sct = mss.mss()

temp_frames = []
for i in range(len(sct.monitors)):
    temp_frames.append((cv2.cvtColor(np.array(sct.grab(sct.monitors[i])), cv2.COLOR_BGRA2BGR)))

monitor = sct.monitors[1]
screen_width = monitor["width"]
screen_height = monitor["height"]

all_monitors_screenshot = cv2.cvtColor(np.array(sct.grab(sct.monitors[0])), cv2.COLOR_BGRA2BGR)
empty_frame = np.zeros((screen_height, screen_width, 3), np.uint8)
frame_width = empty_frame.shape[1]
frame_height = empty_frame.shape[0]

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, round(screen_width/2), round(screen_height/2))
cv2.imshow(window_name, empty_frame)
cv2.waitKey(1)

if os.name == "nt":
    import win32gui, win32con
    from ctypes import windll, byref, sizeof, c_int
    hwnd = win32gui.FindWindow(None, window_name)
    windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    hicon = win32gui.LoadImage(None, f"{path}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)


def get_text_size(text="NONE", text_width=0.5*frame_width, max_text_height=0.5*frame_height):
    fontscale = 1
    textsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)
    width_current_text, height_current_text = textsize
    max_count_current_text = 3
    while width_current_text != text_width or height_current_text > max_text_height:
        fontscale *= min(text_width / textsize[0], max_text_height / textsize[1])
        textsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    thickness = round(fontscale * 2)
    if thickness <= 0:
        thickness = 1
    return text, fontscale, thickness, textsize[0], textsize[1]


def make_button(text="NONE", x1=0, y1=0, x2=100, y2=100, round_corners=30, allow_spam=False, buttoncolor=(100, 100, 100), buttonhovercolor=(130, 130, 130), buttonselectedcolor=(160, 160, 160), buttonselected=False, textcolor=(255, 255, 255), width_scale=0.9, height_scale=0.8):
    if x1 <= mouse_x*frame_width <= x2 and y1 <= mouse_y*frame_height <= y2:
        buttonhovered = True
    else:
        buttonhovered = False
    if buttonselected == True:
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttonselectedcolor, round_corners)
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttonselectedcolor, -1)
    elif buttonhovered == True:
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttonhovercolor, round_corners)
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttonhovercolor, -1)
    else:
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttoncolor, round_corners)
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttoncolor, -1)
    text, fontscale, thickness, width, height = get_text_size(text, round((x2-x1)*width_scale), round((y2-y1)*height_scale))
    cv2.putText(frame, text, (round(x1 + (x2-x1) / 2 - width / 2), round(y1 + (y2-y1) / 2 + height / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, textcolor, thickness, cv2.LINE_AA)
    if allow_spam == False:
        if x1 <= mouse_x*frame_width <= x2 and y1 <= mouse_y*frame_height <= y2 and left_clicked == False and last_left_clicked == True:
            return True, buttonhovered
        else:
            return False, buttonhovered
    else:
        if x1 <= mouse_x*frame_width <= x2 and y1 <= mouse_y*frame_height <= y2 and left_clicked == True:
            return True, buttonhovered
        else:
            return False, buttonhovered


def screen_selection():
    last_left_clicked = False
    while True:
        frame = empty_frame.copy()
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]

        if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, window_name):
            left_clicked = True
        else:
            left_clicked = False

        try:
            window_x, window_y, window_width, window_height = cv2.getWindowImageRect(window_name)
            mouse_x, mouse_y = mouse.get_position()
            mouse_relative_window = mouse_x-window_x, mouse_y-window_y
            last_window_size = (window_x, window_y, window_width, window_height)
            last_mouse_position = (mouse_x, mouse_y)
        except:
            try:
                window_x, window_y, window_width, window_height = last_window_size
            except:
                window_x, window_y, window_width, window_height = (0, 0, 100, 100)
            try:
                mouse_x, mouse_y = last_mouse_position
            except:
                mouse_x, mouse_y = (0, 0)
            mouse_relative_window = mouse_x-window_x, mouse_y-window_y
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))
            if os.name == "nt":
                import win32gui, win32con
                from ctypes import windll, byref, sizeof, c_int
                hwnd = win32gui.FindWindow(None, window_name)
                windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                hicon = win32gui.LoadImage(None, f"{path}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)

        if window_width != 0 and window_height != 0:
            mouse_x = mouse_relative_window[0]/window_width
            mouse_y = mouse_relative_window[1]/window_height
        else:
            mouse_x = 0
            mouse_y = 0

        text, fontscale, thickness, width, height = get_text_size("Select the screen to use:", round(0.9*frame_width), round(0.05*frame_height))

        cv2.putText(frame, text, (round(frame_width / 2 - width / 2), round(0.05*frame_height + height / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (255, 255, 255), thickness, cv2.LINE_AA)
        
        screenshot_height, screenshot_width = all_monitors_screenshot.shape[:2]
        aspect_ratio = screenshot_width / screenshot_height

        target_height = int(0.88 * frame_height)
        target_width = int(target_height * aspect_ratio)

        if target_width > frame_width * 0.98:
            target_width = int(frame_width * 0.98)
            target_height = int(target_width / aspect_ratio)

        resized_screenshot = cv2.resize(all_monitors_screenshot, (target_width, target_height))

        x_offset = (frame_width - target_width) // 2
        y_offset = int(0.11 * frame_height) + ((int(0.88 * frame_height) - target_height) // 2)

        frame[y_offset:y_offset+target_height, x_offset:x_offset+target_width] = resized_screenshot

        for index, monitor in enumerate(sct.monitors[1:], 1):
            monitor_x = monitor["left"] - sct.monitors[0]["left"]
            monitor_y = monitor["top"] - sct.monitors[0]["top"]
            monitor_width = monitor["width"]
            monitor_height = monitor["height"]

            monitor_x_frame = x_offset + int(monitor_x * (target_width / screenshot_width))
            monitor_y_frame = y_offset + int(monitor_y * (target_height / screenshot_height))
            monitor_width_frame = int(monitor_width * (target_width / screenshot_width))
            monitor_height_frame = int(monitor_height * (target_height / screenshot_height))

            top_left_corner = (monitor_x_frame, monitor_y_frame)
            bottom_right_corner = (monitor_x_frame + monitor_width_frame, monitor_y_frame + monitor_height_frame)

            text, fontscale, thickness, width, height = get_text_size(f"Monitor {index}", round(monitor_width_frame * 0.3), round(monitor_height_frame * 0.3))
            cv2.rectangle(frame, (round(monitor_x_frame + monitor_width_frame / 2 - width / 2), round(monitor_y_frame + monitor_height_frame / 2 + height)), (round(monitor_x_frame + monitor_width_frame / 2 + width / 2), round(monitor_y_frame + monitor_height_frame / 2 - height)), (0, 0, 0), height)
            cv2.rectangle(frame, (round(monitor_x_frame + monitor_width_frame / 2 - width / 2), round(monitor_y_frame + monitor_height_frame / 2 + height)), (round(monitor_x_frame + monitor_width_frame / 2 + width / 2), round(monitor_y_frame + monitor_height_frame / 2 - height)), (0, 0, 0), -1)
            cv2.putText(frame, text, (round(monitor_x_frame + monitor_width_frame / 2 - width / 2), round(monitor_y_frame + monitor_height_frame / 2 + height / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (255, 255, 255), thickness, cv2.LINE_AA)
            cv2.rectangle(frame, top_left_corner, bottom_right_corner, (0, 0, 255), thickness)

            if top_left_corner[0] < mouse_x * frame_width < bottom_right_corner[0] and top_left_corner[1] < mouse_y * frame_height < bottom_right_corner[1]:
                cv2.rectangle(frame, (round(top_left_corner[0] + round(0.008 * frame_height)), round(top_left_corner[1] + round(0.008 * frame_height))), (round(bottom_right_corner[0] - round(0.008 * frame_height)), round(bottom_right_corner[1] - round(0.008 * frame_height))), (0, 0, 255), round(0.016 * frame_height))
                if left_clicked == False and last_left_clicked == True:
                    return index
                
        last_left_clicked = left_clicked
                
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)


def take_screenshot():
    screenshot = cv2.cvtColor(np.array(sct.grab(sct.monitors[monitor])), cv2.COLOR_BGRA2BGR)
    return screenshot


if len(sct.monitors) > 2:
    monitor = screen_selection()
    switch_monitor_enabled = True
else:
    monitor = 1
    switch_monitor_enabled = False

setupframe = temp_frames[monitor]
last_temp_frame = setupframe
empty_frame = np.zeros((setupframe.shape[0], setupframe.shape[1], 3), np.uint8)
frame_width = setupframe.shape[1]
frame_height = setupframe.shape[0]
screen_width = sct.monitors[monitor]["width"]
screen_height = sct.monitors[monitor]["height"]


file_path = os.path.dirname(__file__)
exampleimage = cv2.imread(file_path + "/setupexample.png")


exampleimage_width = exampleimage.shape[1]
exampleimage_height = exampleimage.shape[0]
cv2.namedWindow(example_window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(example_window_name, round(exampleimage_width/2), round(exampleimage_height/2))
cv2.imshow(example_window_name, exampleimage)
cv2.waitKey(1)

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))
cv2.imshow(window_name, setupframe)
cv2.waitKey(1)

if os.name == "nt":
    import win32gui, win32con
    from ctypes import windll, byref, sizeof, c_int
    hwnd = win32gui.FindWindow(None, window_name)
    windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    hicon = win32gui.LoadImage(None, f"{path}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
    hwnd = win32gui.FindWindow(None, example_window_name)
    windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    hicon = win32gui.LoadImage(None, f"{path}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)


settings_path = os.path.dirname(__file__)


def EnsureFile(file:str):
    try:
        with open(file, "r") as f:
            try:
                json.load(f)
            except:
                with open(file, "w") as ff:
                    ff.write("{}")
    except:
        with open(file, "w") as f:
            f.write("{}")


def Get_Format1(name:str, value:any=None):
    try:
        EnsureFile(f"{settings_path}/settings.json")
        with open(f"{settings_path}/settings.json", "r") as f:
            settings = json.load(f)

        if settings[name] == None:
            return value
        
        return settings[name]
    except:
        if value != None:
            Set_Format1(name, value)
            return value
        else:
            pass


def Set_Format1(name:str, data:any):
    try:
        EnsureFile(f"{settings_path}/settings.json")
        with open(f"{settings_path}/settings.json", "r") as f:
            settings = json.load(f)

            settings[name] = data

        with open(f"{settings_path}/settings.json", "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
    except:
        pass


def Get_Format2(category:str, name:str, value:any=None):
    try:
        EnsureFile(f"{settings_path}/settings.json")
        with open(f"{settings_path}/settings.json", "r") as f:
            settings = json.load(f)

        if settings[category][name] == None:
            return value
        
        return settings[category][name]
    except:
        if value != None:
            Set_Format2(category, name, value)
            return value
        else:
            pass


def Set_Format2(category:str, name:str, data:any):
    try:
        EnsureFile(f"{settings_path}/settings.json")
        with open(f"{settings_path}/settings.json", "r") as f:
            settings = json.load(f)

        if not category in settings:
            settings[category] = {}
            settings[category][name] = data

        if category in settings:
            settings[category][name] = data

        with open(f"{settings_path}/settings.json", "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
    except:
        pass


map_topleft = Get_Format1("map_topleft", "unset")
map_bottomright = Get_Format1("map_bottomright", "unset")
arrow_topleft = Get_Format1("arrow_topleft", "unset")
arrow_bottomright = Get_Format1("arrow_bottomright", "unset")
if map_topleft == "unset":
    map_topleft = None
if map_bottomright == "unset":
    map_bottomright = None
if arrow_topleft == "unset":
    arrow_topleft = None
if arrow_bottomright == "unset":
    arrow_bottomright = None


minimapDistanceFromRight = 27
minimapDistanceFromBottom = 134
minimapWidth = 560
minimapHeight = 293
scale = frame_height/1440
if map_topleft == None:
    xCoord = frame_width - (minimapDistanceFromRight * scale + minimapWidth * scale)
    yCoord = frame_height - (minimapDistanceFromBottom * scale + minimapHeight * scale)
    map_topleft = (int(xCoord), int(yCoord))
    Set_Format1("map_topleft", map_topleft)
if map_bottomright == None:
    xCoord = frame_width - (minimapDistanceFromRight * scale)
    yCoord = frame_height - (minimapDistanceFromBottom * scale)
    map_bottomright = (int(xCoord), int(yCoord))
    Set_Format1("map_bottomright", map_bottomright)
if arrow_topleft == None:
    xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.57
    yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.575
    arrow_topleft = (int(xCoord), int(yCoord))
    Set_Format1("arrow_topleft", arrow_topleft)
if arrow_bottomright == None:
    xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.43
    yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.39
    arrow_bottomright = (int(xCoord), int(yCoord))
    Set_Format1("arrow_bottomright", arrow_bottomright)


zoom = 0
zoomoffsetx = 0
zoomoffsety = 0
last_left_clicked = False
get_map_topleft = False
get_map_bottomright = False
get_arrow_topleft = False
get_arrow_bottomright = False


while True:
    frame = setupframe.copy()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, window_name):
        left_clicked = True
    else:
        left_clicked = False

    try:
        _, _, _, _ = cv2.getWindowImageRect(example_window_name)
    except:
        exampleimage_width = exampleimage.shape[1]
        exampleimage_height = exampleimage.shape[0]
        cv2.namedWindow(example_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(example_window_name, round(exampleimage_width/2), round(exampleimage_height/2))
        if os.name == "nt":
            import win32gui, win32con
            from ctypes import windll, byref, sizeof, c_int
            hwnd = win32gui.FindWindow(None, example_window_name)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(None, f"{path}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)

    try:
        window_x, window_y, window_width, window_height = cv2.getWindowImageRect(window_name)
        mouse_x, mouse_y = mouse.get_position()
        mouse_relative_window = mouse_x-window_x, mouse_y-window_y
        last_window_size = (window_x, window_y, window_width, window_height)
        last_mouse_position = (mouse_x, mouse_y)
    except:
        try:
            window_x, window_y, window_width, window_height = last_window_size
        except:
            window_x, window_y, window_width, window_height = (0, 0, 100, 100)
        try:
            mouse_x, mouse_y = last_mouse_position
        except:
            mouse_x, mouse_y = (0, 0)
        mouse_relative_window = mouse_x-window_x, mouse_y-window_y
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))
        if os.name == "nt":
            import win32gui, win32con
            from ctypes import windll, byref, sizeof, c_int
            hwnd = win32gui.FindWindow(None, window_name)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(None, f"{path}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)

    if window_width != 0 and window_height != 0:
        mouse_x = mouse_relative_window[0]/window_width
        mouse_y = mouse_relative_window[1]/window_height
    else:
        mouse_x = 0
        mouse_y = 0
    

    corner1 = round(frame_height*zoom/100)+zoomoffsety
    corner2 = round(frame_height-frame_height*zoom/100)+zoomoffsety
    corner3 = round(frame_width*zoom/100)+zoomoffsetx
    corner4 = round(frame_width-frame_width*zoom/100)+zoomoffsetx

    if corner1 < 0:
        corner1 = 0
    if corner1 > frame_height:
        corner1 = frame_height

    if corner2 < 0:
        corner2 = 0
    if corner2 > frame_height:
        corner2 = frame_height

    if corner3 < 0:
        corner3 = 0
    if corner3 > frame_width:
        corner3 = frame_width

    if corner4 < 0:
        corner4 = 0
    if corner4 > frame_width:
        corner4 = frame_width

    original_pixel_x = round(corner3 + mouse_x * (corner4-corner3))
    original_pixel_y = round(corner1 + mouse_y * (corner2-corner1))

    if left_clicked == False:
        mousecoordroot = mouse_x, mouse_y

    if mousecoordroot == None:
        mousecoordroot = 0, 0


    if get_map_topleft == False:
        cv2.line(frame, (map_topleft[0], 0), (map_topleft[0], screen_height), (0, 0, 150), round(frame_height/270))
        cv2.line(frame, (0, map_topleft[1]), (screen_width, map_topleft[1]), (0, 0, 150), round(frame_height/270))
    else:
        cv2.line(frame, (round(original_pixel_x), 0), (round(original_pixel_x), screen_height), (0, 0, 150), round(frame_height/270))
        cv2.line(frame, (0, round(original_pixel_y)), (screen_width, round(original_pixel_y)), (0, 0, 150), round(frame_height/270))
        
    if get_map_bottomright == False:
        cv2.line(frame, (map_bottomright[0], 0), (map_bottomright[0], screen_height), (0, 0, 150), round(frame_height/270))
        cv2.line(frame, (0, map_bottomright[1]), (screen_width, map_bottomright[1]), (0, 0, 150), round(frame_height/270))
    else:
        cv2.line(frame, (round(original_pixel_x), 0), (round(original_pixel_x), screen_height), (0, 0, 150), round(frame_height/270))
        cv2.line(frame, (0, round(original_pixel_y)), (screen_width, round(original_pixel_y)), (0, 0, 150), round(frame_height/270))
        
    
    if get_arrow_topleft == False:
        cv2.line(frame, (arrow_topleft[0], 0), (arrow_topleft[0], screen_height), (40, 130, 210), round(frame_height/270))
        cv2.line(frame, (0, arrow_topleft[1]), (screen_width, arrow_topleft[1]), (40, 130, 210), round(frame_height/270))
    else:
        cv2.line(frame, (round(original_pixel_x), 0), (round(original_pixel_x), screen_height), (40, 130, 210), round(frame_height/270))
        cv2.line(frame, (0, round(original_pixel_y)), (screen_width, round(original_pixel_y)), (40, 130, 210), round(frame_height/270))
        
    if get_arrow_bottomright == False:
        cv2.line(frame, (arrow_bottomright[0], 0), (arrow_bottomright[0], screen_height), (40, 130, 210), round(frame_height/270))
        cv2.line(frame, (0, arrow_bottomright[1]), (screen_width, arrow_bottomright[1]), (40, 130, 210), round(frame_height/270))
    else:
        cv2.line(frame, (round(original_pixel_x), 0), (round(original_pixel_x), screen_height), (40, 130, 210), round(frame_height/270))
        cv2.line(frame, (0, round(original_pixel_y)), (screen_width, round(original_pixel_y)), (40, 130, 210), round(frame_height/270))
        
    
    if map_topleft != None and map_bottomright != None and get_map_topleft == False and get_map_bottomright == False:
        cv2.line(frame, (round(map_topleft[0]), round(map_topleft[1])), (round(map_topleft[0]), round(map_bottomright[1])), (0, 0, 255), round(frame_height/270))
        cv2.line(frame, (round(map_bottomright[0]), round(map_topleft[1])), (round(map_bottomright[0]), round(map_bottomright[1])), (0, 0, 255), round(frame_height/270))
        cv2.line(frame, (round(map_topleft[0]), round(map_topleft[1])), (round(map_bottomright[0]), round(map_topleft[1])), (0, 0, 255), round(frame_height/270))
        cv2.line(frame, (round(map_topleft[0]), round(map_bottomright[1])), (round(map_bottomright[0]), round(map_bottomright[1])), (0, 0, 255), round(frame_height/270))
    

    if arrow_topleft != None and arrow_bottomright != None and get_arrow_topleft == False and get_arrow_bottomright == False:
        cv2.line(frame, (round(arrow_topleft[0]), round(arrow_topleft[1])), (round(arrow_topleft[0]), round(arrow_bottomright[1])), (40, 255, 255), round(frame_height/270))
        cv2.line(frame, (round(arrow_bottomright[0]), round(arrow_topleft[1])), (round(arrow_bottomright[0]), round(arrow_bottomright[1])), (40, 255, 255), round(frame_height/270))
        cv2.line(frame, (round(arrow_topleft[0]), round(arrow_topleft[1])), (round(arrow_bottomright[0]), round(arrow_topleft[1])), (40, 255, 255), round(frame_height/270))
        cv2.line(frame, (round(arrow_topleft[0]), round(arrow_bottomright[1])), (round(arrow_bottomright[0]), round(arrow_bottomright[1])), (40, 255, 255), round(frame_height/270))


    if get_map_topleft == False:
        text, fontscale, thickness, width, height = get_text_size("Map Top Left", 0.15*frame_width, 0.02*frame_height)
        cv2.putText(frame, text, (round(map_topleft[0] + height * 0.2), round(map_topleft[1] + height * 1.2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 150), thickness, cv2.LINE_AA)
    else:
        text, fontscale, thickness, width, height = get_text_size("Map Top Left", 0.15*frame_width, 0.02*frame_height)
        cv2.putText(frame, text, (round(original_pixel_x + height * 0.2), round(original_pixel_y + height * 1.2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 150), thickness, cv2.LINE_AA)

    if get_map_bottomright == False:
        text, fontscale, thickness, width, height = get_text_size("Map Bottom Right", 0.15*frame_width, 0.02*frame_height)
        cv2.putText(frame, text, (round(map_bottomright[0] - width - height * 0.2), round(map_bottomright[1] - height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 150), thickness, cv2.LINE_AA)
    else:
        text, fontscale, thickness, width, height = get_text_size("Map Bottom Right", 0.15*frame_width, 0.02*frame_height)
        cv2.putText(frame, text, (round(original_pixel_x - width - height * 0.2), round(original_pixel_y - height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 150), thickness, cv2.LINE_AA)
    
    if get_arrow_topleft == False:
        text, fontscale, thickness, width, height = get_text_size("Arrow Top Left", 0.1*frame_width, 0.013*frame_height)
        cv2.putText(frame, text, (round(arrow_topleft[0] - width - height * 0.2), round(arrow_topleft[1] - height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (40, 130, 210), thickness, cv2.LINE_AA)
    else:
        text, fontscale, thickness, width, height = get_text_size("Arrow Top Left", 0.1*frame_width, 0.013*frame_height)
        cv2.putText(frame, text, (round(original_pixel_x - width - height * 0.2), round(original_pixel_y - height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (40, 130, 210), thickness, cv2.LINE_AA)

    if get_arrow_bottomright == False:
        text, fontscale, thickness, width, height = get_text_size("Arrow Bottom Right", 0.1*frame_width, 0.013*frame_height)
        cv2.putText(frame, text, (round(arrow_bottomright[0] + height * 0.2), round(arrow_bottomright[1] + height * 1.2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (40, 130, 210), thickness, cv2.LINE_AA)
    else:
        text, fontscale, thickness, width, height = get_text_size("Arrow Bottom Right", 0.1*frame_width, 0.013*frame_height)
        cv2.putText(frame, text, (round(original_pixel_x + height * 0.2), round(original_pixel_y + height * 1.2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (40, 130, 210), thickness, cv2.LINE_AA)
    
    
    if corner1 < corner2 and corner3 < corner4:
        frame = frame[corner1:corner2, corner3:corner4]
    else:
        zoom = 0
        zoomoffsetx = 0
        zoomoffsety = 0


    temp_frame = frame.copy()
    frame = empty_frame.copy()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]


    if (last_temp_frame.shape[1], last_temp_frame.shape[0]) != (temp_frame.shape[1], temp_frame.shape[0]):
        last_temp_frame = temp_frame.copy()
        temp_frame = cv2.resize(temp_frame, (frame_width, frame_height))
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_frame, 1, 255, cv2.THRESH_BINARY)
        temp_frame_masked = cv2.bitwise_and(temp_frame, temp_frame, mask=cv2.bitwise_not(mask))
        frame_masked = cv2.bitwise_and(frame, frame, mask=mask)
        frame = cv2.add(temp_frame_masked, frame_masked)
    else:
        frame = cv2.resize(temp_frame, (frame_width, frame_height))

    
    if get_map_topleft == False and get_map_bottomright == False and get_arrow_topleft == False and get_arrow_bottomright == False:

        button_zoom_in_pressed, button_zoom_in_hovered = make_button(text="Zoom In",
                        x1=0.0*frame_width,
                        y1=0.0*frame_height,
                        x2=0.15*frame_width,
                        y2=0.08*frame_height,
                        round_corners=30,
                        allow_spam=True,
                        buttoncolor=(50, 0, 0),
                        buttonhovercolor=(70, 20, 20),
                        buttonselectedcolor=(70, 20, 20),
                        textcolor=(255, 255, 255),
                        width_scale=0.9,
                        height_scale=0.9)

        button_zoom_out_pressed, button_zoom_out_hovered = make_button(text="Zoom Out",
                        x1=0.0*frame_width,
                        y1=0.09*frame_height,
                        x2=0.15*frame_width,
                        y2=0.17*frame_height,
                        round_corners=30,
                        allow_spam=True,
                        buttoncolor=(50, 0, 0),
                        buttonhovercolor=(70, 20, 20),
                        buttonselectedcolor=(70, 20, 20),
                        textcolor=(255, 255, 255),
                        width_scale=0.9,
                        height_scale=0.9)
        
        button_new_screenshot_pressed, button_new_screenshot_hovered = make_button(text="New Screenshot",
                        x1=0.0*frame_width,
                        y1=0.18*frame_height,
                        x2=0.15*frame_width,
                        y2=0.26*frame_height,
                        round_corners=30,
                        buttoncolor=(50, 0, 0),
                        buttonhovercolor=(70, 20, 20),
                        buttonselectedcolor=(70, 20, 20),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.9)
        
        button_reset_pressed, button_reset_hovered = make_button(text="Reset",
                        x1=0.0*frame_width,
                        y1=0.27*frame_height,
                        x2=0.15*frame_width,
                        y2=0.33*frame_height,
                        round_corners=30,
                        buttoncolor=(0, 0, 200),
                        buttonhovercolor=(20, 20, 220),
                        buttonselectedcolor=(20, 20, 220),
                        textcolor=(255, 255, 255),
                        width_scale=0.9,
                        height_scale=0.7)

        
        button_finish_setup_pressed, button_finish_setup_hovered = make_button(text="Finish Setup",
                        x1=0.85*frame_width,
                        y1=0.0*frame_height,
                        x2=1.0*frame_width,
                        y2=0.1*frame_height,
                        round_corners=30,
                        buttoncolor=(0, 200, 0),
                        buttonhovercolor=(20, 220, 20),
                        buttonselectedcolor=(20, 220, 20),
                        textcolor=(255, 255, 255),
                        width_scale=0.9,
                        height_scale=0.9)
        
    else:

        button_zoom_in_pressed = False
        button_zoom_in_hovered = False
        button_zoom_out_pressed = False
        button_zoom_out_hovered = False
        button_new_screenshot_pressed = False
        button_new_screenshot_hovered = False
        button_reset_pressed = False
        button_reset_hovered = False
        button_finish_setup_pressed = False
        button_finish_setup_hovered = False
    
    
    if get_map_topleft == False and get_map_bottomright == False and get_arrow_topleft == False and get_arrow_bottomright == False:
        get_map_topleft_pressed, get_map_topleft_hovered = make_button(text="Set Top Left Corner of the Map",
                    x1=0.16*frame_width,
                    y1=0.0*frame_height,
                    x2=0.495*frame_width,
                    y2=0.1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_map_topleft,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    elif get_map_topleft == True:
        get_map_topleft_pressed, get_map_topleft_hovered = make_button(text="Press on the top left corner of the map",
                    x1=0.0*frame_width,
                    y1=0.0*frame_height,
                    x2=1.0*frame_width,
                    y2=0.1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_map_topleft,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    else:
        get_map_topleft_pressed = False
        get_map_topleft_pressed = False


    if get_map_topleft == False and get_map_bottomright == False and get_arrow_topleft == False and get_arrow_bottomright == False:
        get_map_bottomright_pressed, get_map_bottomright_hovered = make_button(text="Set Bottom Right Corner of the Map",
                    x1=0.505*frame_width,
                    y1=0.0*frame_height,
                    x2=0.84*frame_width,
                    y2=0.1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_map_bottomright,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    elif get_map_bottomright == True:
        get_map_bottomright_pressed, get_map_bottomright_hovered = make_button(text="Press on the bottom right corner of the map",
                    x1=0.0*frame_width,
                    y1=0.0*frame_height,
                    x2=1.0*frame_width,
                    y2=0.1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_map_bottomright,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    else:
        get_map_bottomright_pressed = False
        get_map_bottomright_pressed = False
    

    if get_map_topleft == False and get_map_bottomright == False and get_arrow_topleft == False and get_arrow_bottomright == False:
        get_arrow_topleft_pressed, get_arrow_topleft_hovered = make_button(text="Set Top Left Corner of the Arrow",
                    x1=0.16*frame_width,
                    y1=0.11*frame_height,
                    x2=0.495*frame_width,
                    y2=0.21*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_arrow_topleft,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    elif get_arrow_topleft == True:
        get_arrow_topleft_pressed, get_arrow_topleft_hovered = make_button(text="Press on the top left corner of the arrow",
                    x1=0.0*frame_width,
                    y1=0.0*frame_height,
                    x2=1.0*frame_width,
                    y2=0.1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_arrow_topleft,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    else:
        get_arrow_topleft_pressed = False
        get_arrow_topleft_pressed = False


    if get_map_topleft == False and get_map_bottomright == False and get_arrow_topleft == False and get_arrow_bottomright == False:
        get_arrow_bottomright_pressed, get_arrow_bottomright_hovered = make_button(text="Set Bottom Right Corner of the Arrow",
                    x1=0.505*frame_width,
                    y1=0.11*frame_height,
                    x2=0.84*frame_width,
                    y2=0.21*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_arrow_bottomright,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    elif get_arrow_bottomright == True:
        get_arrow_bottomright_pressed, get_arrow_bottomright_hovered = make_button(text="Press on the bottom right corner of the arrow",
                    x1=0.0*frame_width,
                    y1=0.0*frame_height,
                    x2=1.0*frame_width,
                    y2=0.1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_arrow_bottomright,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    else:
        get_arrow_bottomright_pressed = False
        get_arrow_bottomright_pressed = False
    

    if button_zoom_in_pressed == True:
        if zoom < screen_height/50:
            zoom += 0.25
    

    if button_zoom_out_pressed == True:
        if zoom > 0:
            zoom -= 0.25

    
    if button_new_screenshot_pressed == True:
        setupframe = take_screenshot()


    if button_reset_pressed == True:
        if messagebox.askokcancel("Setup", (f"Do you really want to reset the setup to default settings?")):
            zoom = 0
            zoomoffsetx = 0
            zoomoffsety = 0
            map_topleft = None
            map_bottomright = None
            arrow_topleft = None
            arrow_bottomright = None

            frame = setupframe.copy()
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]
            
            # Code below by Tumppi066
            minimapDistanceFromRight = 27
            minimapDistanceFromBottom = 134
            minimapWidth = 560
            minimapHeight = 293
            scale = frame_height/1440
            xCoord = frame_width - (minimapDistanceFromRight * scale + minimapWidth * scale)
            yCoord = frame_height - (minimapDistanceFromBottom * scale + minimapHeight * scale)
            map_topleft = (int(xCoord), int(yCoord))
            xCoord = frame_width - (minimapDistanceFromRight * scale)
            yCoord = frame_height - (minimapDistanceFromBottom * scale)
            map_bottomright = (int(xCoord), int(yCoord))
            xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.57
            yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.575
            arrow_topleft = (int(xCoord), int(yCoord))
            xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.43
            yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.39
            arrow_bottomright = (int(xCoord), int(yCoord))
            #

            Set_Format1("map_topleft", map_topleft)
            Set_Format1("map_bottomright", map_bottomright)
            Set_Format1("arrow_topleft", arrow_topleft)
            Set_Format1("arrow_bottomright", arrow_bottomright)


    if button_finish_setup_pressed == True:
        if map_topleft == None or map_bottomright == None or arrow_topleft == None or arrow_bottomright == None:
            
            # Code below by Tumppi066
            minimapDistanceFromRight = 27
            minimapDistanceFromBottom = 134
            minimapWidth = 560
            minimapHeight = 293
            scale = frame_height/1440
            xCoord = frame_width - (minimapDistanceFromRight * scale + minimapWidth * scale)
            yCoord = frame_height - (minimapDistanceFromBottom * scale + minimapHeight * scale)
            map_topleft = (int(xCoord), int(yCoord))
            xCoord = frame_width - (minimapDistanceFromRight * scale)
            yCoord = frame_height - (minimapDistanceFromBottom * scale)
            map_bottomright = (int(xCoord), int(yCoord))
            xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.57
            yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.575
            arrow_topleft = (int(xCoord), int(yCoord))
            xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.43
            yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.39
            arrow_bottomright = (int(xCoord), int(yCoord))
            #

        Set_Format2("ScreenCapture", "display", monitor - 1)
        
        Set_Format1("map_topleft", map_topleft)
        Set_Format1("map_bottomright", map_bottomright)
        Set_Format1("arrow_topleft", arrow_topleft)
        Set_Format1("arrow_bottomright", arrow_bottomright)

        setupframe = setupframe[arrow_topleft[1]:arrow_bottomright[1], arrow_topleft[0]:arrow_bottomright[0]]
        lower_blue = np.array([120, 65, 0])
        upper_blue = np.array([255, 200, 110])
        mask_blue = cv2.inRange(setupframe, lower_blue, upper_blue)
        arrow_height, arrow_width = mask_blue.shape[:2]
        pixel_ratio = round(cv2.countNonZero(mask_blue) / (arrow_width * arrow_height), 3)

        Set_Format1("arrow_percentage", pixel_ratio)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py"), "r+") as file:
            content = file.read()
            file.seek(0)
            if "# this comment is used to reload the app after finishing the setup - 0" in content:
                content = content.replace("# this comment is used to reload the app after finishing the setup - 0", "# this comment is used to reload the app after finishing the setup - 1")
            else:
                content = content.replace("# this comment is used to reload the app after finishing the setup - 1", "# this comment is used to reload the app after finishing the setup - 0")
            file.write(content)
            file.truncate()

        try:
            cv2.destroyWindow(window_name)
        except:
            pass
        try:
            cv2.destroyWindow(example_window_name)
        except:
            pass

        break
    

    if get_map_topleft == True and left_clicked == False and last_left_clicked == True:
        map_topleft = (original_pixel_x, original_pixel_y)
        get_map_topleft = False
    if get_map_bottomright == True and left_clicked == False and last_left_clicked == True:
        map_bottomright = (original_pixel_x, original_pixel_y)
        get_map_bottomright = False
    if get_arrow_topleft == True and left_clicked == False and last_left_clicked == True:
        arrow_topleft = (original_pixel_x, original_pixel_y)
        get_arrow_topleft = False
    if get_arrow_bottomright == True and left_clicked == False and last_left_clicked == True:
        arrow_bottomright = (original_pixel_x, original_pixel_y)
        get_arrow_bottomright = False

    if get_map_topleft_pressed == True:
        get_map_topleft = True
    if get_map_bottomright_pressed == True:
        get_map_bottomright = True
    if get_arrow_topleft_pressed == True:
        get_arrow_topleft = True
    if get_arrow_bottomright_pressed == True:
        get_arrow_bottomright = True


    if button_zoom_in_hovered == False and button_zoom_out_hovered == False and button_new_screenshot_hovered == False and button_reset_hovered == False and button_finish_setup_hovered == False and get_map_topleft_hovered == False and get_map_bottomright_hovered == False and get_arrow_topleft_hovered == False and get_arrow_bottomright_hovered == False:
        any_button_hovered = False
    else:
        any_button_hovered = True
    
    if left_clicked == False:
        moverootx = zoomoffsetx + round(mouse_x * frame_width)
        moverooty = zoomoffsety + round(mouse_y * frame_height)

    if left_clicked == True and get_map_topleft == False and get_map_bottomright == False and get_arrow_topleft == False and get_arrow_bottomright == False and any_button_hovered == False:
        zoomoffsetx = moverootx - round(mouse_x * frame_width)
        zoomoffsety = moverooty - round(mouse_y * frame_height)


    last_left_clicked = left_clicked

    
    cv2.imshow(window_name, frame)
    cv2.imshow(example_window_name, exampleimage)
    cv2.waitKey(1)