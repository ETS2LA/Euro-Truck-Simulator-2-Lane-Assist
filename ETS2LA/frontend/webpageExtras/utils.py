import ETS2LA.variables as variables
import ETS2LA.backend.settings as settings
import colorsys  
import time
import mss
import os

if os.name == 'nt':
    import win32gui
    import win32con
    from ctypes import windll, c_int, byref, sizeof
    
def get_screen_dimensions():
    sct = mss.mss()
    return sct.monitors[1]["left"], sct.monitors[1]["top"], sct.monitors[1]["width"], sct.monitors[1]["height"]
    
last_window_position_time = 0
window_position = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - 1280//2, get_screen_dimensions()[3]//2 - 720//2))

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
            return "#ffffff" if settings.Get("global", "theme", "dark") == "light" else "#09090b"
        except:
            return "#09090b"
    
def set_window_icon(image_path):
    hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    hicon = win32gui.LoadImage(None, image_path, win32con.IMAGE_ICON, 0, 0, icon_flags)
    
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)    

def ColorTitleBar(theme:str="dark"):
    returnCode = 1
    sinceStart = time.time()
    
    colors = {
        "dark": 0x0b0909,
        "light": 0xFFFFFF
    }
    
    while returnCode != 0:
        time.sleep(0.01)
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        returnCode = windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(colors[theme])), sizeof(c_int))
        import ETS2LA.frontend.webpageExtras.utils as utils
        utils.set_window_icon('ETS2LA/frontend/webpageExtras/favicon.ico')
        if time.time() - sinceStart > 5:
            break
        
def CheckIfWindowStillOpen():
    global last_window_position_time
    global window_position
    if os.name == 'nt':
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        if hwnd == 0:
            return False
        else:
            if last_window_position_time + 1 < time.time():
                rect = win32gui.GetClientRect(hwnd)
                tl = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
                if (tl[0], tl[1]) != window_position:
                    window_position = (tl[0], tl[1])
                    settings.Set("global", "window_position", window_position)
                last_window_position_time = time.time()
            return True
    else:
        return True