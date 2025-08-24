from ETS2LA.Window.utils import color_title_bar, dont_check_window_open, get_screen_dimensions, correct_window_position, get_theme_color, resize_window, set_resizable
from multiprocessing import JoinableQueue
import ETS2LA.Utils.settings as settings
import ETS2LA.variables as variables
from ETS2LA.Window.html import html
import webbrowser
import threading
import requests
import logging
import webview
import time
import os

if os.name == 'nt':
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

queue: JoinableQueue = variables.WINDOW_QUEUE

webview.settings = {
    'ALLOW_DOWNLOADS': False,
    'ALLOW_FILE_URLS': True,
    'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
    'OPEN_DEVTOOLS_IN_DEBUG': True
}

def window_handler(window: webview.Window):
    # Wait until the server is ready
    if variables.LOCAL_MODE:
        while True:
            try:
                response = requests.get(f'http://localhost:{FRONTEND_PORT}', timeout=2)
                if response.ok: break
            except: time.sleep(0.5)
            
        set_resizable(True)
        window.load_url('http://localhost:' + str(FRONTEND_PORT))
    else:
        while True:
            try:
                response = requests.get("http://localhost:37520", timeout=2)
                if response.ok: break
            except: time.sleep(0.1)

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
            
            if not window:
                return
            
            if "ets2la" not in window.get_current_url():
                if not variables.LOCAL_MODE:
                    time.sleep(0.5) # 0.5s load time wait
                    webbrowser.open(window.get_current_url())
                    window.load_url(variables.FRONTEND_URL)

def window_callback(window: webview.Window):
    threading.Thread(
        target=window_handler, 
        args=(window,), 
        daemon=True
    ).start()

def start_window():
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
    webview.start(
        window_callback, 
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
def wait_for_window():
    if os.name == 'nt':
        color_title_bar()
        if variables.NO_CONSOLE:
            from ETS2LA.Utils.Console import visibility
            visibility.HideConsole()

    if not dont_check_window_open:
        from ETS2LA.Handlers.sounds import Play
        if settings.Get("global", "startup_sound", True):
            Play("boot")

def run():
    if variables.NO_UI:
        logging.info("No UI flag detected. Skipping UI startup. You can close the application by closing the console window.")
        return
    
    threading.Thread(target=wait_for_window, daemon=True).start()
    start_window()