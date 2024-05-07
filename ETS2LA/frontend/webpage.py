import webview
import multiprocessing    
import os
import time
import logging
import ETS2LA.variables as variables

def start_webpage():
    def load_website(window:webview.Window):
        time.sleep(2)
        window.load_url('http://localhost:3000')
    window = webview.create_window(f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}', html="""
    <html>
        <style>
            body {
                background-color: #09090b;
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
        <body>
            <div style="flex; justify-content: center; align-items: center;">
                <p>Please wait while we initialize the user interface</p>
                <div class="spinner"></div>
            </div>
        </body>
    </html>""", width=1280, height=720, 
                resizable=True, zoomable=True, 
                confirm_close=False, text_select=True
                )
    webview.start(load_website, 
                  window,
                  private_mode=False # Save cookies, local storage and cache
                  )
    
def run():
    p = multiprocessing.Process(target=start_webpage, daemon=True)
    p.start()
    if os.name == 'nt':
        # We can use win32gui and ctypes to get the window handle
        import win32gui
        import ctypes
        
        def ColorTitleBar():
            from ctypes import windll, c_int, byref, sizeof
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
        
def CheckIfWindowStillOpen():
    if os.name == 'nt':
        import win32gui
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        if hwnd == 0:
            return False
        else:
            return True
    else:
        return True