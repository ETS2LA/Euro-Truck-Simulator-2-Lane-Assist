from ETS2LA.Window.utils import (
    color_title_bar,
    dont_check_window_open,
    correct_window_position,
    get_theme_color,
    resize_window,
)
from ETS2LA.Settings import GlobalSettings
from multiprocessing import JoinableQueue
import ETS2LA.variables as variables
from ETS2LA.Window.html import html
import webbrowser
import threading
import requests
import logging
import webview
import time
import os

if os.name == "nt":
    import ctypes

    # some windows magic so that the icon is also shown int the taskbar, the str needs to be a unique id
    # i dont know how fail safe this is so just run in the try block
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "Python.GitHub.App.ETS2LAv2"
        )
    except Exception:
        pass

settings = GlobalSettings()
fl = settings.frameless
dm = settings.debug_mode
fp = settings.frontend_port
w = settings.width
h = settings.height

updating_page = "ETS2LA/Assets/updating.html"

if fl is None:
    FRAMELESS = True
else:
    FRAMELESS = bool(fl)

if dm is None:
    DEBUG_MODE = False
else:
    DEBUG_MODE = bool(dm)

if fp is None:
    FRONTEND_PORT = 3005
else:
    FRONTEND_PORT = int(fp)

w = settings.width
h = settings.height

if w is None:
    WIDTH = 1280
else:
    WIDTH = int(w)

if h is None:
    HEIGHT = 720
else:
    HEIGHT = int(h)

queue: JoinableQueue = variables.WINDOW_QUEUE

webview.settings = {
    "ALLOW_DOWNLOADS": False,
    "ALLOW_FILE_URLS": True,
    "OPEN_EXTERNAL_LINKS_IN_BROWSER": True,
    "OPEN_DEVTOOLS_IN_DEBUG": True,
}


def wait_for_server(window: webview.Window):
    if variables.LOCAL_MODE:
        while True:
            try:
                response = requests.get(f"http://localhost:{FRONTEND_PORT}", timeout=2)
                if response.ok:
                    break
            except Exception:
                time.sleep(0.5)

        window.load_url("http://localhost:" + str(FRONTEND_PORT))
    else:
        while True:
            try:
                response = requests.get("http://localhost:37520", timeout=2)
                if response.ok:
                    break
            except Exception:
                time.sleep(0.1)

        window.load_url(variables.FRONTEND_URL)
        if "ets2la.com" not in variables.FRONTEND_URL:
            settings.ad_preference = 0  # disable ads if not on ets2la.com


def window_handler(window: webview.Window):
    # Wait until the server is ready
    wait_for_server(window)

    last_check = 0
    while True:
        time.sleep(0.01)
        try:
            data = queue.get_nowait()

            if data["type"] == "stay_on_top":
                if data["state"] is None:
                    queue.task_done()
                    queue.put(window.on_top)
                    continue

                window.on_top = data["state"]
                settings.stay_on_top = data["state"] is True
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

            if data["type"] == "update":
                window.load_html(
                    open(updating_page, "r", encoding="utf-8").read(),
                    base_uri=f"file://{os.path.abspath(variables.PATH)}",
                )
                queue.task_done()
                wait_for_server(window)

        except Exception:
            pass

        if last_check + 0.1 < time.time():  # Check 10x per second
            last_check = time.time()
            if variables.DEVELOPMENT_MODE:
                continue

            if not window:
                return

            try:
                if "ets2la" not in window.get_current_url():
                    if not variables.LOCAL_MODE:
                        time.sleep(0.5)  # 0.5s load time wait
                        webbrowser.open(window.get_current_url())
                        window.load_url(variables.FRONTEND_URL)
            except Exception:
                pass


def window_callback(window: webview.Window):
    threading.Thread(target=window_handler, args=(window,), daemon=True).start()


def start_window():
    if os.name != "nt":
        webbrowser.open(variables.FRONTEND_URL)
        return

    window_x = settings.window_position[0]
    window_y = settings.window_position[1]

    if window_x is None or window_y is None:
        return

    window_x = int(window_x)
    window_y = int(window_y)

    window_x, window_y = correct_window_position(window_x, window_y, WIDTH, HEIGHT)
    window = webview.create_window(
        variables.APPTITLE,
        html=html,
        x=window_x,
        y=window_y,
        width=WIDTH + 20,
        height=HEIGHT + 40,
        background_color=get_theme_color(),
        resizable=True,
        zoomable=True,
        confirm_close=True,
        text_select=True,
        frameless=FRAMELESS,
        easy_drag=False,
        on_top=settings.stay_on_top,
    )

    try:
        webview.start(
            window_callback,
            window,
            private_mode=False,  # Save cookies, local storage and cache
            debug=DEBUG_MODE,  # Show developer tools
            storage_path=f"{variables.PATH}cache",
            gui="qt"
            if os.name != "nt"
            else "edgechromium",  # Use GTK on Linux for better compatibility
        )
    except Exception as e:
        logging.error(f"Failed to start the webview window: {e}")
        logging.error("If you're on linux, try to install WebKit2GTK.")


def check_for_size_change():
    global WIDTH, HEIGHT
    width = settings.width
    height = settings.height
    if width != WIDTH or height != HEIGHT:
        while not resize_window(width, height):
            pass
        WIDTH = width
        HEIGHT = height


settings.listen(check_for_size_change)


def wait_for_window():
    if os.name == "nt":
        color_title_bar()
        if variables.NO_CONSOLE:
            from ETS2LA.Utils.Console import visibility

            visibility.HideConsole()

    if not dont_check_window_open:
        from ETS2LA.Handlers.sounds import Play

        if settings.startup_sound:
            Play("boot")


def run():
    if variables.NO_UI:
        logging.info(
            "No UI flag detected. Skipping UI startup. You can close the application by closing the console window."
        )
        return

    threading.Thread(target=wait_for_window, daemon=True).start()
    start_window()
