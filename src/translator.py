import deep_translator as dt
import src.settings as settings
import src.loading as loading
import src.mainUI as mainUI
import json
import os

# Load Language settings
origin = settings.GetSettings("User Interface", "OriginLanguage")
dest = settings.GetSettings("User Interface", "DestinationLanguage")
if origin == None:
    origin = "en"
    settings.CreateSettings("User Interface", "OriginLanguage", origin)
if dest == None:
    dest = "en"
    settings.CreateSettings("User Interface", "DestinationLanguage", dest)

# Load Translation Cache settings
enableCache = settings.GetSettings("User Interface", "EnableTranslationCache")
cachePath = settings.GetSettings("User Interface", "TranslationCachePath")
if enableCache == None:
    enableCache = True
    settings.CreateSettings("User Interface", "EnableTranslationCache", enableCache)
if cachePath == None:
    cachePath = "assets/translationCache/cache.json"
    settings.CreateSettings("User Interface", "TranslationCachePath", cachePath)

translator = None
def MakeTranslator(type):
    global translator
    if type == "google":
        translator = dt.GoogleTranslator(source=origin, target=dest)

MakeTranslator("google")
AVAILABLE_LANGUAGES = translator.get_supported_languages(as_dict=True)

def CheckCache(text, originalLanguage=None, destinationLanguage=None, language=None):
    try:
        file = open(cachePath, "r")
    except:
        try:
            os.mkdir("assets/translationCache")
        except: pass
        file = open(cachePath, "w")
        file.write("{}")
        file.close()
        return False
    
    if language == None:
        language = dest
    
    cache = json.load(file)
    file.close()
    try:
        if text in cache[language]:
            return cache[language][text]
        else:
            return False
    except KeyError:
        return False

def AddToCache(text, translation, language=None):
    file = open(cachePath, "r")
    cache = json.load(file)
    file.close()
    
    if language == None:
        language = dest
    
    try:
        cache[language][text] = translation
    except KeyError:
        cache[language] = {}
        cache[language][text] = translation
    
    file = open(cachePath, "w")
    file.truncate(0)
    json.dump(cache, file, indent=4)
    file.close()    

def Translate(text, originalLanguage=None, destinationLanguage=None):
    global origin
    global dest
    
    
    if originalLanguage == None:
        originalLanguage = origin
    else:
        origin = originalLanguage
        MakeTranslator("google")
        
    if destinationLanguage == None:
        destinationLanguage = dest
    else:
        dest = destinationLanguage
        MakeTranslator("google")
        
    if originalLanguage == destinationLanguage:
        return text
    
    
    def TranslateText(text):
        if enableCache:
            cache = CheckCache(text)
        
        if cache != False:
            return cache
        else:
            mainUI.fps.set(f"TRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING")
            mainUI.root.update()
    
            translation = translator.translate(text)
            AddToCache(text, translation)
            return translation
    
    # Check if the text is an array of strings
    if type(text) == list:
        translatedText = []
        for string in text:
            translatedText.append(TranslateText(string))
            
        return translatedText
    else:
        return TranslateText(text)
    
    
    