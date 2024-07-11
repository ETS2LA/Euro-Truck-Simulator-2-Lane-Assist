import ETS2LA.backend.variables as variables
import ETS2LA.backend.settings as settings
import multiprocessing  
import colorsys  
import logging
import webview
import time
import os

if os.name == 'nt':
    import win32gui
    from ctypes import windll, c_int, byref, sizeof

def get_screen_dimensions():
    import mss
    sct = mss.mss()
    return sct.monitors[1]["left"], sct.monitors[1]["top"], sct.monitors[1]["width"], sct.monitors[1]["height"]

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

def minimize_window():
    if os.name == 'nt':
        import win32gui
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        win32gui.ShowWindow(hwnd, 6)

def start_webpage():
    webview.settings = {
        'ALLOW_DOWNLOADS': False,
        'ALLOW_FILE_URLS': True,
        'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
        'OPEN_DEVTOOLS_IN_DEBUG': True
    }

    def load_website(window:webview.Window):
        time.sleep(3)
        window.load_url('http://localhost:3000')

    window = webview.create_window(f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}', html="""
    <html>
        <style>
            body {
                background-color: get_theme();
                text-align: center;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            p {
                color: #333;
                font-size: 16px;
                font-family: sans-serif;
            }
        
        @keyframes spinner {
            to {transform: rotate(360deg);}
        }
        
        .spinner:before {
            content: '';
            box-sizing: border-box;
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            margin-top: 20px;
            margin-left: -10px;
            border-radius: 50%;
            border-top: 2px solid #333;
            border-right: 2px solid transparent;
            animation: spinner .6s linear infinite;
        }

        </style>
        <body class="pywebview-drag-region">
            <div style="flex; justify-content: center; align-items: center;">
                <p>Please wait while we initialize the user interface</p>
                <div class="spinner"></div>
            </div>
        </body>
    </html>""", x = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - 1280//2, get_screen_dimensions()[3]//2 - 720//2))[0],
                y = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - 1280//2, get_screen_dimensions()[3]//2 - 720//2))[1],
                width=1280, height=720,
                background_color=get_theme(),
                resizable=True, zoomable=True,
                confirm_close=False, text_select=True,
                frameless=True, easy_drag=False
                )
    webview.start(load_website, 
                  window,
                  private_mode=False, # Save cookies, local storage and cache
                  storage_path=variables.PATH + "/ETS2LA/frontend/web_cache"
                  )

def run():
    p = multiprocessing.Process(target=start_webpage, daemon=True)
    p.start()
    if os.name == 'nt':
        def ColorTitleBar():
            returnCode = 1
            sinceStart = time.time()
            while returnCode != 0:
                time.sleep(0.01)
                hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
                returnCode = windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x0b0909)), sizeof(c_int))
                import ETS2LA.frontend.webpageExtras.titleAndIcon as titleAndIcon
                titleAndIcon.set_window_icon('ETS2LA/frontend/webpageExtras/favicon.ico')
                if time.time() - sinceStart > 5:
                    break

        ColorTitleBar()
        logging.info('ETS2LA UI opened.')

global window_position
last_window_position_time = 0
window_position = settings.Get("global", "window_position", (get_screen_dimensions()[2]//2 - 1280//2, get_screen_dimensions()[3]//2 - 720//2))

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
                window_position = (tl[0], tl[1])
                last_window_position_time = time.time()
            return True
    else:
        return True