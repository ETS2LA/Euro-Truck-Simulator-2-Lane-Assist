from ETS2LA.UI import * 

from ETS2LA.Window.window import set_on_top, get_on_top, set_transparency, get_transparency
from ETS2LA.Window.utils import ColorTitleBar
from ETS2LA.Networking.Servers.notifications import sonner, page
from ETS2LA.Window.utils import CheckIfWindowOpen
from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.translator as translator
from ETS2LA.Networking.Servers.data_models import *
from ETS2LA.Utils.Values.dictionaries import merge
from ETS2LA.Utils.shell import ExecuteCommand
import ETS2LA.Utils.settings as settings
import ETS2LA.Handlers.controls as controls
import ETS2LA.Handlers.plugins as plugins
import ETS2LA.Handlers.sounds as sounds
import ETS2LA.Handlers.pages as pages
import ETS2LA.variables as variables
import ETS2LA.Utils.version as git

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body
from typing import Union
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
import sys
import os

mainThreadQueue = []
sessionToken = ""

FRONTEND_PORT = settings.Get("global", "frontend_port", 3005)

app = FastAPI(
    title="ETS2LA",
    description="Backend API for the ETS2 Lane Assist app",
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
    return {"ETS2LA": "1.0.0"}

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
    page("updater")
    return True

@app.get("/api/sounds/play/{sound}")
def play_sound(sound: str):
    sounds.Play(sound)
    return True

@app.get("/api/git/history")
def get_git_history():
    return git.GetHistory()

@app.get("/api/ui/theme/{theme}")
def set_theme(theme: str):
    try:
        ColorTitleBar(theme)
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
    return CheckIfWindowOpen(name)

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
        logging.exception("Failed to set transparency")
        return False

@app.get("/window/transparency")
def get_transparency_state():
    return get_transparency()

# endregion
# region Plugins

@app.get("/backend/plugins")
def get_plugins():
    try:
        # Get data
        available_plugins = plugins.AVAILABLE_PLUGINS
        enabled_plugins = plugins.RUNNING_PLUGINS
        plugin_settings = plugins.get_plugin_settings()
            
        # Create the json
        return_data = {}
        for plugin in available_plugins:
            name, description, authors, _ = plugin
            if type(authors) != list:
                authors = [authors]
                
            return_data[name] = {
                "authors": [author.__dict__ for author in authors],
                "description": description.__dict__,
                "settings": plugin_settings[name],
            }
            if name in [enabled_plugin.plugin_name for enabled_plugin in enabled_plugins]:
                return_data[name]["enabled"] = True
                return_data[name]["frametimes"] = plugins.get_latest_frametime(name)
            else:
                return_data[name]["enabled"] = False
                return_data[name]["frametimes"] = 0
        
        return return_data
    except:
        logging.exception("Failed to get plugins")
        return False

@app.get("/backend/plugins/{plugin}/enable")
def enable_plugin(plugin: str):
    logging.info(Translate(f"webserver.enabling_plugin", values=[plugin]))
    return plugins.enable_plugin(plugin)

@app.get("/backend/plugins/{plugin}/disable")
def disable_plugin(plugin: str):
    logging.info(Translate(f"webserver.disabling_plugin", values=[plugin]))
    return plugins.disable_plugin(plugin)

@app.get("/backend/plugins/performance")
def get_performance():
    return plugins.get_performances()

@app.get("/backend/plugins/states")
def get_states():
    return plugins.get_states()

@app.post("/backend/plugins/{plugin}/relieve")
def relieve_plugin(plugin: str, data: RelieveData = None):
    if data is None:
        data = RelieveData()
        data.map = {}
        
    return plugins.RelieveWaitForFrontend(plugin, data.map)

@app.post("/backend/plugins/{plugin}/function/call")
def call_plugin_function(plugin: str, data: PluginCallData = None):
    try:
        if data is None:
            data = PluginCallData()
        
        running_plugins = [plugin.plugin_name for plugin in plugins.RUNNING_PLUGINS]
        available_plugins = [plugin[1].name for plugin in plugins.AVAILABLE_PLUGINS]
        
        if plugin in running_plugins:
            index = running_plugins.index(plugin)
            plugin = plugins.RUNNING_PLUGINS[index]
            return plugin.call_function(data.target, data.args, data.kwargs)
        
        elif plugin in available_plugins:
            index = available_plugins.index(plugin)
            ui = plugins.AVAILABLE_PLUGINS[index][3]
            return ui.call_function(data.target, data.args, data.kwargs)
        
        else:
            index = pages.get_page_names().index(plugin)
            return pages.page_function_call(plugin, data.target, data.args, data.kwargs)
        
        logging.warning("Plugin not found")
        return {"status": "error", "message": "Plugin not found"}
    except:
        logging.exception("Failed to call plugin function")
        return {"status": "error", "message": "Plugin not found"}

# endregion
# region Language

@app.get("/api/language")
def get_language():
    translator.CheckForLanguageUpdates()
    return translator.LANGUAGE

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
    mainThreadQueue.append([controls.ChangeKeybind, [control], {}])
    while [controls.ChangeKeybind, [control], {}] in mainThreadQueue:
        pass
    return {"status": "ok"}

@app.post("/api/controls/{control}/unbind")
def unbind_control(control: str):
    mainThreadQueue.append([controls.UnbindKeybind, [control], {}])
    while [controls.UnbindKeybind, [control], {}] in mainThreadQueue:
        pass
    return {"status": "ok"}

# endregion
# region Tags

@app.get("/api/tags/data")
def get_tags_data():
    return plugins.get_all_tag_data()

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
        logging.exception("Failed to get tag data")
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
        return pages.get_pages()
    except:
        logging.exception("Failed to get pages")
        return {}

# endregion
# region Session

def BuildFrontend():
    result = ExecuteCommand(f"npm run build", cwd="Interface")
    if result != 0:
        ExecuteCommand(f"npm install", cwd="Interface")
        result = ExecuteCommand(f"npm run build", cwd="Interface")
        if result != 0:
            logging.error("Failed to build frontend")

def RunFrontendDev():
    ExecuteCommand(f"npm run dev -- -p {FRONTEND_PORT}", cwd="Interface")

def RunFrontend():
    result = ExecuteCommand(f"npm start -- -p {FRONTEND_PORT}", cwd="Interface")
    if result != 0:
        logging.info("Building frontend... please wait...")
        BuildFrontend()
        result = ExecuteCommand(f"npm start -- -p {FRONTEND_PORT}", cwd="Interface")
        if result != 0:
            logging.error("Failed to start frontend")
        
def ExtractIP():
    global IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()
    
def run():
    ExtractIP()
    hostname = "0.0.0.0"

    threading.Thread(target=uvicorn.run, args=(app,), kwargs={"port": 37520, "host": hostname, "log_level": "critical"}, daemon=True).start()
    logging.info(Translate("webserver.webserver_started", values=[f"http://{IP}:37520", "http://localhost:37520"]))

    if variables.LOCAL_MODE:
        p = multiprocessing.Process(target=RunFrontend if not variables.DEVELOPMENT_MODE else RunFrontendDev, daemon=True)
        p.start()
        logging.info(Translate("webserver.frontend_started", values=[f"http://{IP}:{FRONTEND_PORT}", f"http://localhost:{FRONTEND_PORT}"]))
    
# endregion