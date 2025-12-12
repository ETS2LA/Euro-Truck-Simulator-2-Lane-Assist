# TODO: This file is garbage. Rewrite it completely.
from ETS2LA.Utils.packages import DownloadLibrary
from ETS2LA.Utils.translator import _
import threading
import logging
import time
import sys
import os

try:
    path = DownloadLibrary("ffmpeg")
except Exception:
    path = None
    logging.error(
        _(
            "Failed to download the ffmpeg library, please download it manually. (ie. [code]winget install ffmpeg[/code])"
        )
    )

if path is not None:
    path = path.replace("ffmpeg.exe", "")
    sys.path.append(path)
    os.environ["PATH"] += path

from ETS2LA.Settings import GlobalSettings
from ETS2LA.variables import PATH
from pydub import AudioSegment
import sounddevice as sd
import numpy as np
import json

settings = GlobalSettings()

# Detect available sound packs
SOUNDPACKS_PATH = "ETS2LA/Assets/Sounds/"
PACK_INFO_FILE = SOUNDPACKS_PATH + "sounds.json"
SOUNDPACKS = os.listdir(SOUNDPACKS_PATH)
if "sounds.json" in SOUNDPACKS:
    SOUNDPACKS.remove("sounds.json")
SOUNDPACK_INFO = json.load(open(PACK_INFO_FILE))
ACCEPTED_FORMATS = SOUNDPACK_INFO["accepted_formats"]
REQUIRED_SOUNDS = SOUNDPACK_INFO["required_sounds"]

# Make sure all sound packs have the required files
temp = SOUNDPACKS.copy()
for i in range(len(SOUNDPACKS)):
    pack = SOUNDPACKS[i]
    sounds = [sound.split(".")[0] for sound in os.listdir(SOUNDPACKS_PATH + "/" + pack)]
    file_types = [
        sound.split(".")[1] for sound in os.listdir(SOUNDPACKS_PATH + "/" + pack)
    ]
    for sound in REQUIRED_SOUNDS:
        if sound not in sounds:
            logging.error(
                _("Soundpack '{0}' is missing the required sound '{1}'").format(
                    pack, sound
                )
            )
            temp.remove(pack)
            break
    for file_type in file_types:
        if file_type not in ACCEPTED_FORMATS:
            logging.error(
                _("Soundpack '{0}' has an invalid file type '{1}'").format(
                    pack, file_type
                )
            )
            temp.remove(pack)
            break

SOUNDPACKS = temp
SELECTED_SOUNDPACK = settings.soundpack
SELECTED_SOUNDPACK = (
    "default" if SELECTED_SOUNDPACK not in SOUNDPACKS else str(SELECTED_SOUNDPACK)
)

VOLUME = settings.volume
VOLUME = 0.5 if VOLUME is None else float(VOLUME) / 100


def UpdateSettings():
    global SELECTED_SOUNDPACK, VOLUME
    SELECTED_SOUNDPACK = settings.soundpack
    SELECTED_SOUNDPACK = (
        "default" if SELECTED_SOUNDPACK not in SOUNDPACKS else str(SELECTED_SOUNDPACK)
    )
    VOLUME = settings.volume
    VOLUME = 0.5 if VOLUME is None else float(VOLUME) / 100


settings.listen(UpdateSettings)


def GetFilenameForSound(sound: str):
    if SELECTED_SOUNDPACK is None:
        return None

    sounds = os.listdir(SOUNDPACKS_PATH + SELECTED_SOUNDPACK)
    for pack_sound in sounds:
        if pack_sound.startswith(sound + "."):
            return PATH + SOUNDPACKS_PATH + SELECTED_SOUNDPACK + "/" + pack_sound
    logging.error(
        _("Tried to play sound '{0}', but it was not found in soundpack '{1}'").format(
            sound, SELECTED_SOUNDPACK
        )
    )
    return None

def play_audio(filename, volume=0.5, blocking=False):
    """Plays an audio file with volume control using sounddevice.

    :param filename: Path to the audio file
    :param volume: Volume level (0.0 to 1.0)
    """
    if not (0.0 <= volume <= 1.0):
        raise ValueError("Volume must be between 0.0 and 1.0")

    audio = AudioSegment.from_file(filename)
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

    # Stereo handling
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))  # Stereo
    else:
        samples = samples.reshape((-1, 1))  # Mono (force 2D)

    samples /= np.iinfo(np.int16).max  # normalize -1 - 1
    samples *= volume
    sd.play(samples, samplerate=audio.frame_rate, blocking=blocking)

stop = False
is_playing = False
def continuous_play_audio(filename, volume=0.5):
    """Continuously plays an audio file in a separate thread.

    :param filename: Path to the audio file
    :param volume: Volume level (0.0 to 1.0)
    """
    global stop, is_playing
    
    def play_loop():
        global is_playing, stop
        is_playing = True
        
        if not (0.0 <= volume <= 1.0):
            raise ValueError("Volume must be between 0.0 and 1.0")

        audio = AudioSegment.from_file(filename)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

        # Stereo handling
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))  # Stereo
        else:
            samples = samples.reshape((-1, 1))  # Mono (force 2D)

        samples /= np.iinfo(np.int16).max  # normalize -1 - 1
        samples *= volume
        
        sd.play(samples, samplerate=audio.frame_rate, blocking=False, loop=True)
        while not stop:
            time.sleep(0.1)
        
        sd.stop()    
        is_playing = False

    stop = False
    thread = threading.Thread(target=play_loop, daemon=True)
    thread.start()

def StartContinuous(sound: str):
    filename = GetFilenameForSound(sound)
    if filename is None:
        return False

    try:
        if is_playing:
            return True
        
        continuous_play_audio(filename, VOLUME)  # type: ignore
    except Exception:
        return False

    return True

def StopContinuous():
    global stop
    stop = True
    return True

def Play(sound: str):
    filename = GetFilenameForSound(sound)
    if filename is None:
        return False

    try:
        play_audio(filename, VOLUME)  # type: ignore
    except Exception:
        return False

    return True
