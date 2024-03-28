from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ETS2LA.backend.backend as backend
import ETS2LA.backend.settings as settings
import threading
import logging
import sys
import os
import json
from typing import Any
from fastapi import Body


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def read_root():
    return {"ETS2LA": "1.0.0"}

@app.get("/api/frametimes")
def get_frametimes():
    return backend.frameTimes

@app.get("/api/quit")
def quitApp():
    return sys.exit()

@app.get("/api/plugins")
def get_plugins():
    # Get data
    plugins = backend.GetAvailablePlugins()
    try:
        enabledPlugins = backend.GetEnabledPlugins()
    except:
        import traceback
        traceback.print_exc()
        enabledPlugins = []
        
    try:
        frametimes = backend.frameTimes
    except:
        import traceback
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
    return backend.AddPluginRunner(plugin)

@app.get("/api/plugins/{plugin}/disable")
def disable_plugin(plugin: str):
    return backend.RemovePluginRunner(plugin)

@app.post("/api/plugins/{plugin}/settings/{key}/set")
def set_plugin_setting(plugin: str, key: str, value: Any = Body(...)):
    print(f"Setting {plugin} {key} to {value}")
    success = settings.Set(plugin, key, value["value"])
    return success

@app.get("/api/plugins/{plugin}/settings/{key}")
def get_plugin_setting(plugin: str, key: str):
    return settings.Get(plugin, key)

@app.get("/api/plugins/{plugin}/settings")
def get_plugin_settings(plugin: str):
    return settings.GetJSON(plugin)

@app.get("/api/server/ip")
def get_IP():
    return IP

def RunFrontend():
    def StartWebserver():
        os.system("cd frontend && npm run dev")
        return
    def ShowWebserver():
        #os.system("start msedge --app=http://localhost:3000")
        return
    threading.Thread(target=StartWebserver, daemon=True).start()
    threading.Thread(target=ShowWebserver, daemon=True).start()
    
def run():
    global IP
    import uvicorn
    # Get current PC ip
    import socket
    IP = socket.gethostbyname(socket.gethostname())
    hostname = "0.0.0.0"
    # Start the webserver on the local IP
    threading.Thread(target=uvicorn.run, args=(app,), kwargs={"port": 37520, "host": hostname, "log_level": "critical"}, daemon=True).start()
    logging.info(f"Webserver started on http://{IP}:37520 (& localhost:37520)")
    threading.Thread(target=RunFrontend, daemon=True).start()
    logging.info("Frontend started on http://localhost:3000")