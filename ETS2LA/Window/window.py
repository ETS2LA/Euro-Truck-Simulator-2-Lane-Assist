from ETS2LA.Window.utils import color_title_bar, dont_check_window_open, get_screen_dimensions, correct_window_position, get_theme_color
from multiprocessing import JoinableQueue
import ETS2LA.Utils.settings as settings
from ETS2LA.Handlers.sounds import Play
import ETS2LA.variables as variables
from ETS2LA.Window.html import html
import multiprocessing  
import webbrowser
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
    import ctypes

    # some windows magic so that the icon is also shown int the taskbar, the str needs to be a unique id
    # i dont know how fail safe this is so just run in the try block
    try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Python.GitHub.App.ETS2LAv2")
    except: pass

fl = settings.Get("global", "frameless", True)
dm = settings.Get("global", "debug_mode", False)
fp = settings.Get("global", "frontend_port", 3005)
w = settings.Get("global", "width", 1280)
h = settings.Get("global", "height", 720)

if fl is None: FRAMELESS = True
else: FRAMELESS = bool(fl)

if dm is None: DEBUG_MODE = False
else: DEBUG_MODE = bool(dm)

if fp is None: FRONTEND_PORT = 3005
else: FRONTEND_PORT = int(fp)

w = settings.Get("global", "width", 1280)
h = settings.Get("global", "height", 720)

if w is None: WIDTH = 1280
else: WIDTH = int(w)

if h is None: HEIGHT = 720
else: HEIGHT = int(h)

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

def toggle_fullscreen():
    queue.put({"type": "fullscreen"})
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

if os.name == 'nt':
    def get_windows_scaling_factor() -> float:
        try:
            scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            return scale_factor / 100.0
        except:
            logging.exception("Failed to get Windows scaling factor")
            return 1.0  # Fallback to no scaling

def resize_window(width: int, height: int):
    # Get system scaling and adjust dimensions
    if os.name == 'nt':
        scaling = get_windows_scaling_factor()
        scaled_width = int(width * scaling)
        scaled_height = int(height * scaling)
    else:
        scaled_width = width
        scaled_height = height

    queue.put({"type": "resize", "width": scaled_width, "height": scaled_height})
    queue.join()  # Wait for the queue to be processed
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
        HWND = win32gui.FindWindow(None, variables.APPTITLE)
        style = win32gui.GetWindowLong(HWND, win32con.GWL_STYLE)
        
        color_title_bar()
        
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
            HWND = win32gui.FindWindow(None, variables.APPTITLE)
            win32gui.SetWindowLong(HWND, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (HWND, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            
            transparency = settings.Get("global", "transparency_alpha", 0.8)
            if transparency is None:
                transparency = 0.8
                
            transparency = int(transparency * 255)
            winxpgui.SetLayeredWindowAttributes(HWND, win32api.RGB(0,0,0), transparency, win32con.LWA_ALPHA)
        else:
            HWND = win32gui.FindWindow(None, variables.APPTITLE)
            win32gui.SetWindowLong(HWND, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (HWND, win32con.GWL_EXSTYLE) & ~win32con.WS_EX_LAYERED)
        
        IS_TRANSPARENT = value
        settings.Set("global", "transparency", value)
    else:
        logging.warning(f"Transparency is not supported on this platform. ({os.name})")
    return IS_TRANSPARENT

def start_webpage(queue: JoinableQueue, local_mode: bool):
    global webview_window
    
    def load_website(window:webview.Window):
        # Wait until the server is ready
        if local_mode:
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
        else:
            window.load_url(variables.FRONTEND_URL)
            if "ets2la.com" not in variables.FRONTEND_URL:
                settings.Set("global", "ad_preference", 0) # disable ads if not on ets2la.com
        
        last_check = 0
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
                    settings.Set("global", "stay_on_top", data["state"] == True)
                    queue.task_done()
                    queue.put(data["state"])
                    
                if data["type"] == "fullscreen":
                    window.toggle_fullscreen()
                    queue.task_done()
                    queue.put(window.fullscreen)
                    
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
            
            if last_check + 0.1 < time.time():  # Check 10x per second
                last_check = time.time()
                if variables.DEVELOPMENT_MODE:
                    continue
                
                if "ets2la" not in window.get_current_url():
                    time.sleep(0.5) # 0.5s load time wait
                    webbrowser.open(window.get_current_url())
                    if variables.LOCAL_MODE:
                        window.load_url('http://localhost:' + str(FRONTEND_PORT))
                    else:
                        window.load_url(variables.FRONTEND_URL)
                

    window_x = settings.Get("global", "window_position", (
        get_screen_dimensions()[2] // 2 - WIDTH // 2, 
        get_screen_dimensions()[3] // 2 - HEIGHT // 2
    ))
    
    if window_x != None:
        window_x = int(window_x[0])
    
    window_y = settings.Get("global", "window_position", (
        get_screen_dimensions()[2] // 2 - WIDTH // 2, 
        get_screen_dimensions()[3] // 2 - HEIGHT // 2
    ))
    
    if window_y != None:
        window_y = int(window_y[1])

    if window_x is None or window_y is None:
        return

    window_x, window_y = correct_window_position(window_x, window_y, WIDTH, HEIGHT)

    window = webview.create_window(
        variables.APPTITLE, 
        html=html, 
        x = window_x,
        y = window_y,
        width=WIDTH+20, 
        height=HEIGHT+40,
        background_color=get_theme_color(),
        resizable=True, 
        zoomable=True,
        confirm_close=True, 
        text_select=True,
        frameless=FRAMELESS, 
        easy_drag=False,
        on_top=settings.Get("global", "stay_on_top", False) == True
    )
    
    webview_window = window
    
    webview.start(
        load_website, 
        window, # type: ignore
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
    if variables.NO_UI:
        logging.info("No UI flag detected. Skipping UI startup. You can close the application by closing the console window.")
        return
    
    p = multiprocessing.Process(target=start_webpage, args=(queue, variables.LOCAL_MODE, ), daemon=True)
    p.start()
    if os.name == 'nt':
        color_title_bar()
        if variables.NO_CONSOLE:
            from ETS2LA.Utils.Console import visibility
            visibility.HideConsole()

    if not dont_check_window_open:
        if settings.Get("global", "startup_sound", True):
            Play("boot")