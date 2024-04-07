import webview
import multiprocessing    
import os
import time

def start_webpage():
    def load_website(window:webview.Window):
        time.sleep(2)
        window.load_url('http://localhost:3000')
    window = webview.create_window('ETS2LA', html="""
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
                font-family: roboto;
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
                <p>ETS2LA frontend is starting...</p>
                <div class="spinner"></div>
            </div>
        </body>
    </html>""", width=1280, height=720, resizable=True, zoomable=True, confirm_close=True)
    webview.start(load_website, window)

    
def run():
    p = multiprocessing.Process(target=start_webpage, daemon=True)
    p.start()
    time.sleep(1)
    if os.name == 'nt':
        # We can use win32gui and ctypes to get the window handle
        import win32gui
        import ctypes
        hwnd = win32gui.FindWindow(None, 'ETS2LA')
        
        def ColorTitleBar():
            from ctypes import windll, c_int, byref, sizeof
            returnCode = windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x09090b)), sizeof(c_int))
            
        ColorTitleBar()
        
def CheckIfWindowStillOpen():
    if os.name == 'nt':
        import win32gui
        hwnd = win32gui.FindWindow(None, 'ETS2LA')
        if hwnd == 0:
            return False
        else:
            return True
    else:
        return True