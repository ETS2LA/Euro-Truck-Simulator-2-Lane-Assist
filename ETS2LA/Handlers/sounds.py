# TODO: This file is garbage. Rewrite it completely.
from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.settings as settings
from ETS2LA.variables import PATH
import logging
import pygame
import json
import os
    
# Detect available sound packs
SOUNDPACKS_PATH = "ETS2LA/Assets/Sounds/"
PACK_INFO_FILE = SOUNDPACKS_PATH + "sounds.json"
SOUNDPACKS = os.listdir(SOUNDPACKS_PATH)
if "sounds.json" in SOUNDPACKS: SOUNDPACKS.remove("sounds.json")
SOUNDPACK_INFO = json.load(open(PACK_INFO_FILE))
ACCEPTED_FORMATS = SOUNDPACK_INFO["accepted_formats"]
REQUIRED_SOUNDS = SOUNDPACK_INFO["required_sounds"]

# Make sure all sound packs have the required files
temp = SOUNDPACKS.copy()
for i in range(len(SOUNDPACKS)):
    pack = SOUNDPACKS[i]
    sounds = [sound.split(".")[0] for sound in os.listdir(SOUNDPACKS_PATH + "/" + pack)]
    file_types = [sound.split(".")[1] for sound in os.listdir(SOUNDPACKS_PATH + "/" + pack)]
    for sound in REQUIRED_SOUNDS:
        if sound not in sounds:
            logging.error(Translate("sounds.missing_sound", values=[pack, sound]))
            temp.remove(pack)
            break
    for file_type in file_types:
        if file_type not in ACCEPTED_FORMATS:
            logging.error(Translate("sounds.invalid_file_type", values=[pack, file_type]))
            temp.remove(pack)
            break

SOUNDPACKS = temp        
SELECTED_SOUNDPACK = settings.Get("global", "soundpack", "default")
SELECTED_SOUNDPACK = "default" if SELECTED_SOUNDPACK not in SOUNDPACKS else str(SELECTED_SOUNDPACK)

VOLUME = settings.Get("global", "volume", 50)
VOLUME = 0.5 if VOLUME is None else float(VOLUME) / 100
        
pygame.init()

def UpdateSettings(settings: dict):
    global SELECTED_SOUNDPACK, VOLUME
    SELECTED_SOUNDPACK = settings["soundpack"]
    SELECTED_SOUNDPACK = "default" if SELECTED_SOUNDPACK not in SOUNDPACKS else str(SELECTED_SOUNDPACK)
    VOLUME = settings["volume"]
    VOLUME = 0.5 if VOLUME is None else float(VOLUME) / 100
    
settings.Listen("global", UpdateSettings)

def GetFilenameForSound(sound: str):
    if SELECTED_SOUNDPACK is None:
        return None
    
    sounds = os.listdir(SOUNDPACKS_PATH + "/" + SELECTED_SOUNDPACK)
    for pack_sound in sounds:
        if sound in pack_sound:
            return SOUNDPACKS_PATH + "/" + SELECTED_SOUNDPACK + "/" + pack_sound
    logging.error(Translate("sounds.sound_not_found_in_soundpack", values=[sound, SELECTED_SOUNDPACK]))
    return None

def Play(sound: str):
    filename = GetFilenameForSound(sound)
    if filename is None: return False
    
    try:
        pygame.mixer.music.set_volume(VOLUME) # type: ignore
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except pygame.error as e:
        logging.error(f"No sound device available: {e}")
        return False
    
    return True