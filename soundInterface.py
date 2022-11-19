from playsound import playsound
import settingsInterface as settings
import time

enable = settings.GetSettings("soundSettings", "enableSound")
disable = settings.GetSettings("soundSettings", "disableSound")
warning = settings.GetSettings("soundSettings", "warningSound")
warningPlayInterval = 5 # Seconds
warningTimer = 0

def PlaySoundEnable():
    try:
        if(settings.GetSettings("soundSettings", "playSounds")):
            playsound(enable, block=False)
    except:
        pass

def PlaySoundDisable():
    try:
        if(settings.GetSettings("soundSettings", "playSounds")):
            playsound(disable, block=False)
    except:
        pass


def PlaySoundWarning():
    global warningTimer
    global warningPlayInterval
    try:
        if(time.time() - warningTimer > warningPlayInterval):
            if(settings.GetSettings("soundSettings", "playSounds")):
                playsound(warning, block=False)
            warningTimer = time.time()
    except Exception as e:
        print(e)
        pass
