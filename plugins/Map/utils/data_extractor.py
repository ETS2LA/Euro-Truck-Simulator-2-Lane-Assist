"""Data extraction utilities for map plugin."""
try:
    from ETS2LA.utils.translator import Translate
    import ETS2LA.backend.settings as settings
except ImportError:
    def Translate(text): return text
    settings = None

import logging
import zipfile
import hashlib
import shutil
import ujson
import json
import os

DATA_FILENAME = os.path.join(os.path.dirname(__file__).replace("\\utils", ""), "data.zip")
DATA_HASH = None if settings is None else settings.Get("Map", "data_hash", None)
fallback = False

def ExtractData(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path)

    if not os.path.exists(path):
        os.makedirs(path)

    with zipfile.ZipFile(DATA_FILENAME, 'r') as zip_ref:
        zip_ref.extractall(path)

def UpdateData(path: str) -> bool:
    global DATA_HASH
    new_hash = hashlib.md5(open(DATA_FILENAME, 'rb').read()).hexdigest()
    if DATA_HASH is None:
        logging.warning(Translate("map.extracting_data"))
        logging.warning("(No Hash)")
        DATA_HASH = new_hash
        if settings is not None:
            settings.Set("Map", "data_hash", DATA_HASH)
        ExtractData(path)
        return True
    if DATA_HASH != new_hash:
        logging.warning(Translate("map.extracting_data"))
        DATA_HASH = new_hash
        if settings is not None:
            settings.Set("Map", "data_hash", new_hash)
        ExtractData(path)
        return True
    return False

def ReadData(path: str) -> dict:
    global fallback
    with open(path, "r", encoding="utf-8") as f:
        if fallback: 
            data = json.load(f) 
            if not data:
                logging.error(f"Failed to load Map data JSON file: {path}")
        else: 
            data = ujson.load(f)
            if not data:
                fallback = True
                data = ReadData(path)
        return data
