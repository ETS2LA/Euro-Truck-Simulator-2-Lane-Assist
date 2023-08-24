import deep_translator as dt
import src.settings as settings
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


translator = "google"

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
    if originalLanguage == None:
        originalLanguage = origin
    if destinationLanguage == None:
        destinationLanguage = dest
        
    if originalLanguage == destinationLanguage:
        return text
    
    if enableCache:
        cache = CheckCache(text)
        if cache != False:
            return cache
        else:
            translation = dt.GoogleTranslator(source=originalLanguage, target=destinationLanguage).translate(text)
            AddToCache(text, translation)
            return translation
    
    if translator == "google":
        return dt.GoogleTranslator(source=originalLanguage, target=destinationLanguage).translate(text)
    