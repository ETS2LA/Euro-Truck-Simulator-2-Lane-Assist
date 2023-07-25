import playsound
from src.logger import print
from src.variables import PATH

def PlaySound(sound):
    try:
        dir = PATH + sound
        print("Playing sound: " + dir)
        playsound.playsound(dir, block=False)
    except Exception as ex:
        print(ex.args)
        pass
    
