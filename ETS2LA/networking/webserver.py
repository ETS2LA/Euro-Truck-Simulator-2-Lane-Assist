from ETS2LA.frontend.webpageExtras.utils import ColorTitleBar
from ETS2LA.frontend.webpage import set_on_top, get_on_top
from ETS2LA.utils.translator import Translate
import ETS2LA.utils.translator as translator
from ETS2LA.networking.data_models import *
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.backend.backend as backend
import ETS2LA.backend.sounds as sounds
import ETS2LA.variables as variables
import ETS2LA.utils.git as git

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi import Body
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

@app.get("/auth/discord/login")
def login(code):
    try:
        response = requests.get("https://api.ets2la.com/auth/discord/login", params={"code": code})
        settings.Set("global", "user_id", response.json()["user_id"])
        settings.Set("global", "token", response.json()["token"])
        return response.json()["success"] + " - You can now close this window"
    except:
        exception = traceback.format_exc()
        logging.error(exception)
        return exception

@app.get("/api/quit")
def quitApp():
    variables.CLOSE = True
    return {"status": "ok"}

@app.get("/api/restart")
def restartApp():
    variables.RESTART = True
    return {"status": "ok"}

@app.get("/api/minimize")
def minimizeApp():
    variables.MINIMIZE = True
    return {"status": "ok"}

@app.get("/api/map/style")
def get_map_style():
    return json.loads(open("ETS2LA/assets/map_style.json").read())

@app.get("/api/check/updates")
def check_updates():
    return git.CheckForUpdate()

@app.get("/api/update")
def update():
    mainThreadQueue.append([git.Update, [], {}])
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

@app.get("/api/server/ip")
def get_IP():
    return IP

@app.get("/api/window/stay_on_top")
def get_stay_on_top():
    return get_on_top()

@app.get("/api/window/stay_on_top/{state}")
def stay_on_top(state: bool):
    newState = set_on_top(state)
    return newState

# endregion
# region Plugins

@app.get("/api/frametimes")
def get_frametimes():
    return backend.frameTimes

@app.get("/api/plugins")
def get_plugins():
    # Get data
    plugins = backend.GetAvailablePlugins()
    try:
        enabledPlugins = backend.GetEnabledPlugins()
    except:
        traceback.print_exc()
        enabledPlugins = []
        
    try:
        frametimes = backend.frameTimes
    except:
        traceback.print_exc()
        frametimes = {}
        
    # Create the json
    returnData = plugins.copy()
    for plugin in plugins:
        returnData[plugin]["enabled"] = False
        if plugin in enabledPlugins:
            returnData[plugin]["enabled"] = True
        
        returnData[plugin]["frametimes"] = 0
        if plugin in frametimes:
            returnData[plugin]["frametimes"] = frametimes[plugin]
    
    return returnData

@app.get("/api/plugins/{plugin}/enable")
def enable_plugin(plugin: str):
    logging.info(Translate(f"webserver.enabling_plugin", values=[plugin]))
    return backend.AddPluginRunner(plugin)

@app.get("/api/plugins/{plugin}/disable")
def disable_plugin(plugin: str):
    logging.info(Translate(f"webserver.disabling_plugin", values=[plugin]))
    return backend.RemovePluginRunner(plugin)

@app.get("/api/plugins/performance")
def get_performance():
    return backend.GetPerformance()

@app.get("/api/plugins/states")
def get_states():
    return backend.GetPluginStates()

@app.post("/api/plugins/{plugin}/relieve")
def relieve_plugin(plugin: str, data: RelieveData = None):
    if data is None:
        data = RelieveData()
        data.data = {}
        
    return backend.RelieveWaitForFrontend(plugin, data.data)

@app.post("/api/plugins/{plugin}/call/{function}")
def call_plugin_function(plugin: str, function: str, data: PluginCallData = None):
    if data is None:
        data = PluginCallData()
    
    returnData = backend.CallPluginFunction(plugin, function, data.args, data.kwargs)
    if returnData == False or returnData == None:
        return False
    else:
        return returnData

# endregion
# region Language

@app.get("/api/language")
def get_language():
    translator.CheckForLanguageUpdates()
    return translator.LANGUAGE

# endregion
# region Settings

@app.post("/api/plugins/{plugin}/settings/{key}/set")
def set_plugin_setting(plugin: str, key: str, value: Any = Body(...)):
    success = settings.Set(plugin, key, value["value"])
    return success

@app.post("/api/plugins/{plugin}/settings/set")
def set_plugin_settings(plugin: str, data: dict = Body(...)):
    keys = data["keys"]
    setting = data["setting"]
    success = settings.Set(plugin, keys, setting)
    return success
    
@app.get("/api/plugins/{plugin}/settings/{key}")
def get_plugin_setting(plugin: str, key: str):
    return settings.Get(plugin, key)

@app.get("/api/plugins/{plugin}/settings")
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
    return backend.globalData

@app.post("/api/tags/data")
def get_tag_data(data: TagFetchData):
    count = 0
    for plugin in backend.globalData:
        if data.tag in backend.globalData[plugin]:
            count += 1
    
    returnData = {}
    for plugin in backend.globalData:
        if data.tag in backend.globalData[plugin]:
            if type(backend.globalData[plugin][data.tag]) == dict:
                if count > 1:
                    returnData = backend.merge(returnData, backend.globalData[plugin][data.tag])
                else:
                    returnData = backend.globalData[plugin][data.tag]
            else: 
                returnData = backend.globalData[plugin][data.tag]
                
    return returnData

@app.get("/api/tags/list")
def get_tags_list():
    data = backend.globalData
    keys = list(data.keys())
    return keys

# endregion
# region Session

def RunFrontend():
    os.system(f"cd frontend && npm run dev -- -p {FRONTEND_PORT}")
    
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

    p = multiprocessing.Process(target=RunFrontend, daemon=True)
    p.start()
    logging.info(Translate("webserver.frontend_started", values=[f"http://{IP}:{FRONTEND_PORT}", f"http://localhost:{FRONTEND_PORT}"]))
    
# endregion