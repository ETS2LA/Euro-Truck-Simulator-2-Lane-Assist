import ETS2LA.variables as variables
import ETS2LA.Utils.settings as settings
import colorsys  
import logging
import time
import mss
import os

if os.name == 'nt':
    import win32gui
    import win32con
    from ctypes import windll, c_int, byref, sizeof

def get_screen_dimensions(monitor=1):
    try:
        sct = mss.mss()
        return sct.monitors[monitor]["left"], sct.monitors[monitor]["top"], sct.monitors[monitor]["width"], sct.monitors[monitor]["height"]
    except:
        return 0, 0, 1280, 720

last_window_position_time = 0
dont_check_window_open = False
window_position = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - 1280//2, get_screen_dimensions()[3]//2 - 720//2))

def check_valid_window_position(window_x, window_y, width=1280, height=720):
    with mss.mss() as sct:
        monitors = sct.monitors
    closest_screen_index = None
    closest_distance = float('inf')
    for i, monitor in enumerate(monitors[1:]):
        center_x = (monitor['left'] + monitor['left'] + monitor['width']) // 2
        center_y = (monitor['top'] + monitor['top'] + monitor['height']) // 2
        distance = ((center_x - window_x - width//2) ** 2 + (center_y - window_y - height//2) ** 2) ** 0.5
        if distance < closest_distance:
            closest_screen_index = i + 1
            closest_distance = distance

    if get_screen_dimensions(closest_screen_index)[0] > window_x + width//2 or window_x + width//2 > get_screen_dimensions(closest_screen_index)[0] + get_screen_dimensions(closest_screen_index)[2]:
        window_x = get_screen_dimensions(closest_screen_index)[0] + get_screen_dimensions(closest_screen_index)[2] - width if window_x + width//2 > get_screen_dimensions(closest_screen_index)[0] + get_screen_dimensions(closest_screen_index)[2] else get_screen_dimensions(closest_screen_index)[0]
    if get_screen_dimensions(closest_screen_index)[1] > window_y or window_y + height//2 > get_screen_dimensions(closest_screen_index)[1] + get_screen_dimensions(closest_screen_index)[3]:
        window_y = get_screen_dimensions(closest_screen_index)[1] + get_screen_dimensions(closest_screen_index)[3] - height if window_y + height//2 > get_screen_dimensions(closest_screen_index)[1] + get_screen_dimensions(closest_screen_index)[3] else get_screen_dimensions(closest_screen_index)[1]

    return window_x, window_y

def get_theme():
    try:
        theme = settings.Get("global", "theme", "dark")
        with open(f"{variables.PATH}frontend\\src\\pages\\globals.css", "r") as file:
            content = file.read().split("\n")
            for i, line in enumerate(content):
                if i > 0:
                    if content[i - 1].replace(" ", "").startswith(":root{" if theme == "light" else ".dark{") and line.replace(" ", "").startswith("--background"):
                        line = str(line.split(":")[1]).replace(";", "")
                        for i, char in enumerate(line):
                            if char == " ":
                                line = line[i+1:]
                            else:
                                break
                        line = line.split(" ")
                        line = [round(float(line[0])), round(float(line[1][:-1])), round(float(line[2][:-1]))]
                        rgb_color = colorsys.hls_to_rgb(int(line[0])/360,int(line[2])/100,int(line[1])/100)
                        hex_color = '#%02x%02x%02x'%(round(rgb_color[0]*255),round(rgb_color[1]*255),round(rgb_color[2]*255))
                        return hex_color
    except:
        try:
            return "#ffffff" if settings.Get("global", "theme", "dark") == "light" else "#18181b"
        except:
            return "#18181b"

def set_window_icon(image_path):
    hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    hicon = win32gui.LoadImage(None, image_path, win32con.IMAGE_ICON, 0, 0, icon_flags)

    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)    

def ColorTitleBar(theme:str="dark"):
    global dont_check_window_open
    
    returnCode = 1
    sinceStart = time.perf_counter()
    
    colors = {
        "dark": 0x1b1818,
        "light": 0xFFFFFF
    }

    logging.info("Looking for ETS2LA window... (10s timeout)")
    while returnCode != 0:
        time.sleep(0.01)
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        returnCode = windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(colors[theme])), sizeof(c_int))
        import ETS2LA.Window.utils as utils
        utils.set_window_icon('ETS2LA/Window/favicon.ico')
        if time.perf_counter() - sinceStart > 10:
            logging.error("Couldn't find / start the ETS2LA window. Is your PC powerful enough? Use https://app.ets2la.com if you think you should be able to run it.")
            dont_check_window_open = True
            break
    
    if returnCode == 0:
        logging.info("ETS2LA window found!")
    

def CheckIfWindowStillOpen():
    global last_window_position_time
    global window_position
    if dont_check_window_open:
        return True
    
    if os.name == 'nt':
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        if hwnd == 0:
            return False
        else:
            if last_window_position_time + 1 < time.perf_counter():
                rect = win32gui.GetClientRect(hwnd)
                tl = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
                if (tl[0], tl[1]) != window_position:
                    window_position = (tl[0], tl[1])
                    settings.Set("global", "window_position", window_position)
                last_window_position_time = time.perf_counter()
            return True
    else:
        return True
    
def CheckIfWindowOpen(name):
    if os.name == 'nt':
        top_windows = []
        win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
        for hwnd, window_text in top_windows:
            if name in window_text:
                return True
            
        return False
    else:
        # TODO: Implement for linux
        return True