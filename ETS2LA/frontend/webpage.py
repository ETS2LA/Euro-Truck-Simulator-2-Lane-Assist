from ETS2LA.frontend.webpageExtras.utils import ColorTitleBar, CheckIfWindowStillOpen, get_screen_dimensions, check_valid_window_position, get_theme, window_position
from ETS2LA.frontend.webpageExtras.html import html
import ETS2LA.variables as variables
import ETS2LA.backend.settings as settings
import multiprocessing  
import logging
import webview
import time
import os

if os.name == 'nt':
    import win32gui

DEBUG_MODE = False

webview.settings = {
    'ALLOW_DOWNLOADS': False,
    'ALLOW_FILE_URLS': True,
    'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
    'OPEN_DEVTOOLS_IN_DEBUG': True
}

def minimize_window():
    if os.name == 'nt':
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        win32gui.ShowWindow(hwnd, 6)
    elif os.name == 'posix':
        # Copilot made this, no clue if it works
        os.system("xdotool getactivewindow windowminimize")
    else:
        logging.error("Could not minimize the window. OS not supported.")

def start_webpage():
    def load_website(window:webview.Window):
        time.sleep(3)
        window.load_url('http://localhost:3000')

    window_x = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - 1280//2, get_screen_dimensions()[3]//2 - 720//2))[0]
    window_y = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - 1280//2, get_screen_dimensions()[3]//2 - 720//2))[1]

    window_x, window_y = check_valid_window_position(window_x, window_y)

    window = webview.create_window(
        f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}', 
        html=html, 
        x = window_x,
        y = window_y,
        width=1280, 
        height=720,
        background_color=get_theme(),
        resizable=True, 
        zoomable=True,
        confirm_close=False, 
        text_select=True,
        frameless=True, 
        easy_drag=False
    )
    
    webview.start(
        load_website, 
        window,
        private_mode=False, # Save cookies, local storage and cache
        debug=DEBUG_MODE, # Show developer tools
        storage_path=f"{variables.PATH}cache"
    )

def run():
    p = multiprocessing.Process(target=start_webpage, daemon=True)
    p.start()
    if os.name == 'nt':
        ColorTitleBar()
        logging.info('ETS2LA UI opened.')