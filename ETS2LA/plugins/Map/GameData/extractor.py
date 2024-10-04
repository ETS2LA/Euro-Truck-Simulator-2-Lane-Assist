from ETS2LA.utils.translator import Translate
import ETS2LA.backend.settings as settings
import logging
import zipfile
import hashlib
import shutil
import os

FILENAME = "ETS2LA/plugins/Map/GameData/GameData.zip"
DATA_DIR = "ETS2LA/plugins/Map/GameData/data"
HASH = settings.Get("Map", "data_hash", None)

def ExtractData() -> None:
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
        
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    with zipfile.ZipFile(FILENAME, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    
def UpdateData() -> bool:
    global HASH
    newHASH = hashlib.md5(open(FILENAME, 'rb').read()).hexdigest()
    if HASH is None:
        logging.warning(Translate("map.extracting_data"))
        logging.warning("(No Hash)")
        HASH = newHASH
        settings.Set("Map", "data_hash", HASH)
        ExtractData()
        return True
    if HASH != newHASH:
        logging.warning(Translate("map.extracting_data"))
        HASH = newHASH
        settings.Set("Map", "data_hash", newHASH)
        ExtractData()
        return True
    return False