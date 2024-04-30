"""Provides an easy to use interface to play sounds from local paths.

Usage:
```python
import src.sounds as sounds
sounds.PlaysoundFromLocalPath("assets/sounds/...") # Will play the sound.
```"""
from ETS2LA.variables import PATH

try:
    import pygame
    pygame.init()
    sounds = True
except:
    sounds = False
    print("Could not import pygame, sounds will not be played.")
    
def PlaysoundFromLocalPath(sound:str):
    """Will play a sound given a local path.

    Args:
        sound (str): Path to the sound file. (usually "assets/...")
    """
    try:
        dir = PATH + sound
        if sounds:
            print("Playing sound: " + dir)
            pygame.mixer.music.load(dir)
            pygame.mixer.music.play()
        else:
            print("Pygame not imported, could not play sound: " + dir)
    except Exception as ex:
        print(ex.args)
        pass