import ETS2LA.backend.settings as settings
from ETS2LA.variables import PATH
import logging
import pygame
import json
import os
    
# Detect available sound packs
SOUNDPACKS_PATH = "ETS2LA/assets/sounds/"
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
            logging.error(f"Soundpack '{pack}' is missing the required sound '{sound}'")
            temp.remove(pack)
            break
    for file_type in file_types:
        if file_type not in ACCEPTED_FORMATS:
            logging.error(f"Soundpack '{pack}' has an invalid file type '{file_type}'")
            temp.remove(pack)
            break

SOUNDPACKS = temp        
SELECTED_SOUNDPACK = settings.Get("global", "soundpack", "default")
VOLUME = settings.Get("global", "volume", 50)
        
pygame.init()

def UpdateGlobalSoundpackJson():
    settings.Set("ETS2LA/global_settings.json", ["settings", 1, "type", "options"], SOUNDPACKS)

def UpdateVolume():
    global VOLUME
    VOLUME = settings.Get("global", "volume", 50) / 100

def GetFilenameForSound(sound: str):
    sounds = os.listdir(SOUNDPACKS_PATH + "/" + SELECTED_SOUNDPACK)
    for pack_sound in sounds:
        if sound in pack_sound:
            return SOUNDPACKS_PATH + "/" + SELECTED_SOUNDPACK + "/" + pack_sound
    logging.error(f"Tried to play sound '{sound}', but it was not found in soundpack '{SELECTED_SOUNDPACK}'")
    return None

def Play(sound: str):
    filename = GetFilenameForSound(sound)
    if filename is None: return False
    
    UpdateVolume()
    
    pygame.mixer.music.set_volume(VOLUME)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    return True