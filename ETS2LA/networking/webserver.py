from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ETS2LA.backend.backend as backend
import threading
import logging
import sys
import os

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
    # Return as json
    plugins = backend.AVAILABLE_PLUGINS
    return plugins

def RunFrontend():
    # os.system("start msedge --app=http://localhost:3000")
    os.system("cd frontend && npm run --silent dev")

def run():
    import uvicorn
    threading.Thread(target=uvicorn.run, args=(app,), kwargs={"port": 37520, "host": "0.0.0.0", "log_level": "critical"}, daemon=True).start()
    logging.info("Webserver started on http://localhost:37520")
    threading.Thread(target=RunFrontend, daemon=True).start()
    logging.info("Frontend started on http://localhost:3000")