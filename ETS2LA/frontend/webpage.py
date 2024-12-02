from ETS2LA.frontend.webpageExtras.utils import ColorTitleBar, CheckIfWindowStillOpen, get_screen_dimensions, check_valid_window_position, get_theme, window_position
from ETS2LA.frontend.webpageExtras.html import html
from ETS2LA.utils.translator import Translate
import ETS2LA.backend.settings as settings
from multiprocessing import JoinableQueue
import ETS2LA.variables as variables
import multiprocessing  
import requests
import logging
import webview
import time
import os

if os.name == 'nt':
    import win32gui
    import win32con
    import winxpgui
    import win32api

DEBUG_MODE = settings.Get("global", "debug_mode", False)
FRONTEND_PORT = settings.Get("global", "frontend_port", 3005)
FRAMELESS = settings.Get("global", "frameless", True)
WIDTH = settings.Get("global", "width", 1280)
HEIGHT = settings.Get("global", "height", 720)
IS_TRANSPARENT = False

queue:JoinableQueue = JoinableQueue()

webview.settings = {
    'ALLOW_DOWNLOADS': False,
    'ALLOW_FILE_URLS': True,
    'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
    'OPEN_DEVTOOLS_IN_DEBUG': True
}

def set_on_top(state: bool):
    queue.put({"type": "stay_on_top", "state": state})
    queue.join() # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value

def get_on_top():
    queue.put({"type": "stay_on_top", "state": None})
    queue.join() # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value

def resize_window(width:int, height:int):
    queue.put({"type": "resize", "width": width, "height": height})
    queue.join() # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value

def minimize_window():
    queue.put({"type": "minimize"})
    queue.join() # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value

def get_transparency():
    return IS_TRANSPARENT

def set_resizable(value: bool):
    if os.name == 'nt':
        HWND = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        style = win32gui.GetWindowLong(HWND, win32con.GWL_STYLE)
        
        ColorTitleBar()
        
        if value:
            new_style = style | win32con.WS_THICKFRAME
        else:
            # Reset the window style to the default
            new_style = style & ~win32con.WS_THICKFRAME
            
        win32gui.SetWindowLong(HWND, win32con.GWL_STYLE, new_style)
        # Force window to redraw
        win32gui.SetWindowPos(HWND, None, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
    else:
        logging.warning(f"Window style modification not supported on this platform. ({os.name})")

def set_transparency(value: bool):
    global IS_TRANSPARENT
    if os.name == 'nt':
        if value:
            HWND = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
            win32gui.SetWindowLong(HWND, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (HWND, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            transparency = settings.Get("global", "transparency_alpha", 0.8)
            transparency = int(transparency * 255)
            winxpgui.SetLayeredWindowAttributes(HWND, win32api.RGB(0,0,0), transparency, win32con.LWA_ALPHA)
        else:
            HWND = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
            win32gui.SetWindowLong(HWND, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (HWND, win32con.GWL_EXSTYLE) & ~win32con.WS_EX_LAYERED)
        
        IS_TRANSPARENT = value
    else:
        logging.warning(f"Transparency is not supported on this platform. ({os.name})")
    return IS_TRANSPARENT

def start_webpage(queue: JoinableQueue):
    global webview_window
    
    def load_website(window:webview.Window):
        # Wait until the server is ready
        RETRY_INTERVAL = 0.5
        HAS_STARTED = False
        while not HAS_STARTED:
            try:
                response = requests.get(
                    f'http://localhost:{FRONTEND_PORT}',
                    timeout=2
                )
                if response.ok:
                    HAS_STARTED = True
                    break
            except:
                pass  # Handle timeout
            
            time.sleep(RETRY_INTERVAL)
            
        #set_resizable(True)
        window.load_url('http://localhost:' + str(FRONTEND_PORT))
        while True:
            time.sleep(0.01)
            try:
                data = queue.get_nowait()
                
                if data["type"] == "stay_on_top":
                    if data["state"] == None:
                        queue.task_done()
                        queue.put(window.on_top)
                        continue
                    
                    window.on_top = data["state"]
                    queue.task_done()
                    queue.put(data["state"])
                    
                if data["type"] == "minimize":
                    window.minimize()
                    queue.task_done()
                    queue.put(True)
                    
                if data["type"] == "resize":
                    window.resize(data["width"], data["height"])
                    queue.task_done()
                    queue.put(True)
                    
            except:
                pass

    window_x = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - WIDTH//2, get_screen_dimensions()[3]//2 - HEIGHT//2))[0]
    window_y = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - WIDTH//2, get_screen_dimensions()[3]//2 - HEIGHT//2))[1]

    window_x, window_y = check_valid_window_position(window_x, window_y, WIDTH, HEIGHT)

    window = webview.create_window(
        f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}', 
        html=html, 
        x = window_x,
        y = window_y,
        width=WIDTH+20, 
        height=HEIGHT+40,
        background_color=get_theme(),
        resizable=True, 
        zoomable=True,
        confirm_close=True, 
        text_select=True,
        frameless=FRAMELESS, 
        easy_drag=False
    )
    
    webview_window = window
    
    webview.start(
        load_website, 
        window,
        private_mode=False, # Save cookies, local storage and cache
        debug=DEBUG_MODE, # Show developer tools
        storage_path=f"{variables.PATH}cache"
    )

def check_for_size_change(settings):
    global WIDTH, HEIGHT
    width = settings["width"]
    height = settings["height"]
    if width != WIDTH or height != HEIGHT:
        while not resize_window(width, height):
            pass
        WIDTH = width
        HEIGHT = height
    
settings.Listen("global", check_for_size_change)

def run():
    p = multiprocessing.Process(target=start_webpage, args=(queue, ), daemon=True)
    p.start()
    if os.name == 'nt':
        ColorTitleBar()
        logging.info(Translate("webpage.opened"))
