import ETS2LA.variables as variables
from typing import Literal
import time
import sys
import os

start_time = time.time()

ets2_path = variables.ETS2_LOG_PATH
ats_path = variables.ATS_LOG_PATH

last_ets2_update = 0
last_ats_update = 0

ets2_lines = []
ats_lines = []

def update_logs(game: Literal["ets2", "ats"]):
    global ets2_lines, ats_lines
    if game == "ets2":
        with open(ets2_path, "r") as f:
            lines = f.readlines()
            if len(lines) < len(ets2_lines):
                ets2_lines = lines
                return lines
            
            new_lines = lines[len(ets2_lines):]
            ets2_lines = lines
            return new_lines
            
    elif game == "ats":
        with open(ats_path, "r") as f:
            lines = f.readlines()
            if len(lines) < len(ats_lines):
                ats_lines = lines
                return lines
            
            new_lines = lines[len(ats_lines):]
            ats_lines = lines
            return new_lines

def get_new_lines():
    global last_ets2_update, last_ats_update
    try: ets2_time = os.path.getmtime(ets2_path)
    except: ets2_time = 0
    
    try: ats_time = os.path.getmtime(ats_path)
    except: ats_time = 0
    
    new_lines = []
    if ets2_time > last_ets2_update:
        new_lines += update_logs("ets2")
        last_ets2_update = ets2_time
        
    if ats_time > last_ats_update:
        new_lines += update_logs("ats")
        last_ats_update = ats_time
        
    return new_lines

def update():
    # Wait for the application to start
    if time.time() - start_time > 10:
        return get_new_lines()
    else:
        return []