"""
PLEASE NOTE:
- This file is in the process of being refactored.
- The current code has been made with no regard to the final
  structure, thus the formatting and endpoints are nonsensical.
- Proper documentation will be written once this file is refactored.
"""
from ETS2LA.UI import * 

from ETS2LA.Window.window import set_on_top, get_on_top, set_transparency, get_transparency
from ETS2LA.Networking.Servers.notifications import sonner, navigate
from ETS2LA.Networking.Servers import notifications
from ETS2LA.Utils.Values.dictionaries import merge
from ETS2LA.Window.utils import check_if_specified_window_open
from ETS2LA.Networking.Servers.models import *
from ETS2LA.Utils.shell import ExecuteCommand
from ETS2LA.Utils.translator import _
from ETS2LA.Window.utils import color_title_bar
import ETS2LA.Handlers.controls as controls
import ETS2LA.Handlers.plugins as plugins
import ETS2LA.Utils.settings as settings
import ETS2LA.Handlers.sounds as sounds
import ETS2LA.Handlers.pages as pages
import ETS2LA.variables as variables
import ETS2LA.Utils.version as git

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Body
from typing import Any
import multiprocessing
import traceback
import threading
import logging
import requests
import uvicorn
import socket
import json
import zlib

asked_plugins = False # Will trigger the "Do you want to re-enable plugins?" popup
mainThreadQueue = []
sessionToken = ""
thread = None

IP = None

FRONTEND_PORT = settings.Get("global", "frontend_port", 3005)

app = FastAPI(
    title="ETS2LA",
    description="Backend API for the ETS2LA app.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# region Backend

@app.get("/")
def read_root():
    return {"ETS2LA": variables.METADATA["version"]}

@app.get("/auth/discord/login", response_class=HTMLResponse)
def login(code):
    try:
        response = requests.get("https://api.ets2la.com/auth/discord/login", params={"code": code})
        settings.Set("global", "user_id", response.json()["user_id"])
        settings.Set("global", "token", response.json()["token"])
        return HTMLResponse(content=open("ETS2LA/Assets/auth_complete.html").read().replace("response_code", response.json()["success"]), status_code=200)
    except:
        exception = traceback.format_exc()
        logging.error(exception)
        return exception

@app.get("/backend/quit")
def quitApp():
    variables.CLOSE = True
    return {"status": "ok"}

@app.get("/backend/restart")
def restartApp():
    variables.RESTART = True
    return {"status": "ok"}

@app.get("/window/minimize")
def minimizeApp():
    variables.MINIMIZE = True
    return {"status": "ok"}

@app.get("/backend/updates")
def check_updates():
    return git.CheckForUpdate()

@app.get("/backend/update")
def update():
    navigate("updater", _("Frontend"), _("The frontend wants to perform an update."))
    return True

@app.get("/api/sounds/play/{sound}")
def play_sound(sound: str):
    sounds.Play(sound)
    return True

@app.get("/api/git/history")
def get_git_history():
    return git.GetHistory()

@app.get("/api/ui/theme/{theme}")
def set_theme(theme: Literal["dark", "light"]):
    try:
        color_title_bar(theme)
        return True
    except:
        return False

@app.get("/backend/ip")
def get_IP():
    return IP

@app.get("/backend/devmode")
def get_devmode():
    return variables.DEVELOPMENT_MODE

@app.get("/api/metadata")
def get_metadata():
    return variables.METADATA

@app.get("/backend/statistics")
def get_statistics():
    return plugins.get_statistics()

#endregion
# region Window

@app.get("/window/exists/{name}")
def check_window(name: str):
    return check_if_specified_window_open(name)

@app.get("/window/stay_on_top")
def get_stay_on_top():
    return get_on_top()

@app.get("/window/stay_on_top/{state}")
def stay_on_top(state: bool):
    newState = set_on_top(state)
    return newState

@app.get("/window/transparency/{state}")
def set_transparency_to(state: bool):
    try:
        newState = set_transparency(state)
        return newState
    except:
        logging.exception(_("Failed to set transparency"))
        return False

@app.get("/window/transparency")
def get_transparency_state():
    return get_transparency()

# endregion
# region Plugins

@app.get("/backend/plugins")
def get_plugins():
    global asked_plugins
    if not asked_plugins:
        to_enable = settings.Get("global", "running_plugins", [])
        to_enable = [] if to_enable is None else to_enable
        
        if len(to_enable) > 0:          
            answer = notifications.ask("Re-enable plugins?", ["Yes", "No"], description="Do you want to re-enable the plugins that were running before the app was closed?\n\n - " + "\n - ".join(to_enable))
            if answer["response"] == "Yes":
                notifications.sonner("Re-enabling plugins...")
                for plugin in to_enable:
                    plugins.start_plugin(name=plugin)
                    
            notifications.sonner("Plugins enabled!", "success")
                
        asked_plugins = True
    
    try:
        # Get data
        available_plugins = plugins.plugins
        enabled_plugins = [plugin for plugin in available_plugins if plugin.running]
        # plugin_settings = plugins.get_plugin_settings() # TODO: Reimplement urls
            
        # Create the json
        return_data = {}
        for plugin in available_plugins:
            id, description, authors = plugin.description.id, plugin.description, plugin.authors
            if type(authors) != list:
                authors = [authors]
                
            return_data[id] = {
                "authors": [author.__dict__ for author in authors],
                "description": description.__dict__,
                "settings": None,
            }
            if id in [enabled_plugin.description.id for enabled_plugin in enabled_plugins]:
                return_data[id]["enabled"] = True
                return_data[id]["frametimes"] = []#plugins.get_latest_frametime(id)
            else:
                return_data[id]["enabled"] = False
                return_data[id]["frametimes"] = 0
        
        return return_data
    except:
        logging.exception("Failed to get plugins")
        return False

@app.get("/backend/plugins/{plugin}/enable")
def enable_plugin(plugin: str):
    return plugins.start_plugin(name=plugin)

@app.get("/backend/plugins/{plugin}/disable")
def disable_plugin(plugin: str):
    return plugins.stop_plugin(name=plugin)

@app.get("/backend/plugins/performance")
def get_performance():
    return {} # TODO: Reimplement this

@app.get("/backend/plugins/states")
def get_states():
    return plugins.get_states()

# endregion
# region Language

@app.get("/api/language")
def get_language():
    return _.get_language()

# endregion
# region Popups
@app.post("/api/popup")
def popup(data: PopupData):
    mainThreadQueue.append([sonner, [data.text, data.type, None, ], {}])
    return {"status": "ok"}

# endregion
# region Settings

@app.post("/backend/plugins/{plugin}/settings/{key}/set")
def set_plugin_setting(plugin: str, key: str, value: Any = Body(...)):
    success = settings.Set(plugin, key, value["value"])
    return success

@app.post("/backend/plugins/{plugin}/settings/set")
def set_plugin_settings(plugin: str, data: dict = Body(...)):
    keys = data["keys"]
    setting = data["setting"]
    success = settings.Set(plugin, keys, setting)
    return success
    
@app.get("/backend/plugins/{plugin}/settings/{key}")
def get_plugin_setting(plugin: str, key: str):
    return settings.Get(plugin, key)

@app.get("/backend/plugins/{plugin}/settings")
def get_plugin_settings(plugin: str):
    return settings.GetJSON(plugin)

# endregion
# region Controls

@app.post("/api/controls/{control}/change")
def change_control(control: str):
    mainThreadQueue.append([controls.edit_event, [control], {}])
    while [controls.edit_event, [control], {}] in mainThreadQueue:
        pass
    return {"status": "ok"}

@app.post("/api/controls/{control}/unbind")
def unbind_control(control: str):
    mainThreadQueue.append([controls.unbind_event, [control], {}])
    while [controls.unbind_event, [control], {}] in mainThreadQueue:
        pass
    return {"status": "ok"}

# endregion
# region Tags

@app.get("/api/tags/data")
def get_tags_data():
    data = plugins.get_all_tag_data()
    return data

@app.post("/api/tags/data")
def get_tag_data(data: TagFetchData):
    try:
        backend_data = plugins.get_tag_data(data.tag)
        count = 0
        for plugin in backend_data:
            if data.tag in backend_data:
                count += 1

        return_data = {}
        for plugin in backend_data:
            if type(backend_data[plugin]) == dict:
                if count > 1:
                    return_data = merge(return_data, backend_data[plugin])
                else:
                    return_data = backend_data[plugin]
            else:
                return_data = backend_data[plugin]

        headers = {}
        if data.zlib:
            return_data = zlib.compress(json.dumps(return_data).encode("utf-8"), wbits=28)
            headers["Content-Encoding"] = "gzip"

        if type(return_data) != bytes:
            return return_data

        return HTMLResponse(content=return_data, status_code=200, headers=headers)
    except:
        logging.exception(_("Failed to get tag data"))
        return False

@app.get("/api/tags/{tag}")
def get_tag(tag: str):
    backend_data = plugins.get_tag_data(tag)
    count = 0
    for plugin in backend_data:
        if tag in backend_data[plugin]:
            count += 1
            
    returnData = {}
    for plugin in backend_data:
        if type(backend_data[plugin]) == dict:
            if count > 1:
                returnData = merge(returnData, backend_data[plugin])
            else:
                returnData = backend_data[plugin]
        else: 
            returnData = backend_data[plugin]
             
    return returnData

@app.get("/api/tags/list")
def get_tags_list():
    return plugins.get_tag_list()

# endregion
# region Pages

@app.get("/api/pages")
def get_list_of_pages():
    try:
        return plugins.get_page_list()
    except:
        logging.exception(_("Failed to get pages"))
        return {}
    
@app.post("/api/page")
def get_page(data: PageFetchData):
    try:
        # Plugins
        if data.page in plugins.get_page_list():
            page = plugins.get_page_data(data.page)
            return page
            
        # Pages
        return pages.get_page(data.page)
    except:
        logging.exception(_("Failed to get page data for page {0}").format(data.page))
        return []

# endregion
# region Developers

@app.get("/api/plugins/reload")
def reload_plugins():
    try:
        plugins.reload_plugins()
    except:
        logging.exception(_("Failed to reload plugins"))
        return False
    return True

# endregion
# region Session

def BuildFrontend():
    result = ExecuteCommand(f"cd Interface && npm run build")
    if result != 0:
        ExecuteCommand(f"cd Interface && npm install")
        result = ExecuteCommand(f"cd Interface && npm run build")
        if result != 0:
            logging.error(_("Failed to build frontend"))

def RunFrontendDev():
    ExecuteCommand(f"cd Interface && npm run dev -- -p {FRONTEND_PORT}")

def RunFrontend():
    result = ExecuteCommand(f"cd Interface && npm start -- -p {FRONTEND_PORT}")
    if result != 0:
        logging.info(_("Building frontend... please wait..."))
        BuildFrontend()
        result = ExecuteCommand(f"cd Interface && npm start -- -p {FRONTEND_PORT}")
        if result != 0:
            logging.error(_("Failed to start frontend"))

def ExtractIP():
    global IP
    try:
        IP = socket.gethostbyname(socket.gethostname())
    except:
        IP = "127.0.0.1"
    
def run():
    global thread
    
    ExtractIP()
    hostname = "0.0.0.0"

    thread = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"port": 37520, "host": hostname, "log_level": "critical"}, daemon=True)
    thread.start()
    
    logging.info(_("Webserver started at http://{ip}:37520").format(ip=IP))

    if variables.LOCAL_MODE:
        p = multiprocessing.Process(target=RunFrontend if not variables.DEVELOPMENT_MODE else RunFrontendDev, daemon=True)
        p.start()
        logging.info(_("Frontend started at http://{ip}:{port}").format(ip=IP, port=FRONTEND_PORT))

# endregion