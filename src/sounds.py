from src.logger import print
from src.variables import PATH

try:
    import playsound
    sounds = True
except:
    sounds = False
    print("Could not import playsound, sounds will not be played.")
    
def PlaysoundFromLocalPath(sound):
    """Will play a sound given a local path.

    Args:
        sound (str): Path to the sound file. (usually "assets/...")
    """
    try:
        dir = PATH + sound
        if sounds:
            print("Playing sound: " + dir)
            playsound.playsound(dir, block=False)
        else:
            print("Could not play sound: " + dir)
    except Exception as ex:
        print(ex.args)
        pass
    
