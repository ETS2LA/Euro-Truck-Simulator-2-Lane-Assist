from playsound import playsound
import settingsInterface as settings

enable = settings.GetSettings("soundSettings", "enableSound")
disable = settings.GetSettings("soundSettings", "disableSound")
warning = settings.GetSettings("soundSettings", "warningSound")

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
    try:
        if(settings.GetSettings("soundSettings", "playSounds")):
            playsound(warning, block=False)
    except:
        pass
