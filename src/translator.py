"""Provides a standard translation interface. All helper functions already use this interface by default.

Usage:
```python
from src.translator import Translate
print(Translate("Hello world!"))
```"""
import deep_translator as dt
import src.settings as settings
import src.loading as loading
import src.mainUI as mainUI
from src.logger import print
import json
import os

def GetOSLanguage():
    """Will get the current OS language.

    Returns:
        str: 2 letter language code.
    """
    if os.name == "nt":
        import ctypes
        import locale
        from babel import Locale
        windll = ctypes.windll.kernel32
        language = locale.windows_locale[windll.GetUserDefaultUILanguage()]
        language = Locale.parse(language)
        language = language.language
        
        # Override for simplified chinese
        if language == "zh":
            language = "zh-CN"
            
        return language
    else:
        return os.environ.get("LANG").split("_")[0]

def LoadSettings():
    """Will load the translation settings from the settings file.
    """
    global origin
    global dest
    global enableCache
    global cachePath

    # Load Language settings
    origin = settings.GetSettings("User Interface", "OriginLanguage")
    dest = settings.GetSettings("User Interface", "DestinationLanguage")
    if origin == None:
        origin = "en"
        settings.CreateSettings("User Interface", "OriginLanguage", origin)
    if dest == None:
        dest = GetOSLanguage()
        settings.CreateSettings("User Interface", "DestinationLanguage", dest)

    # Load Translation Cache settings
    enableCache = settings.GetSettings("User Interface", "EnableTranslationCache")
    print(enableCache)
    cachePath = settings.GetSettings("User Interface", "TranslationCachePath")
    if enableCache == None:
        enableCache = True
        settings.CreateSettings("User Interface", "EnableTranslationCache", enableCache)
    if cachePath == None:
        cachePath = "assets/translationCache/cache.json"
        settings.CreateSettings("User Interface", "TranslationCachePath", cachePath)

LoadSettings()

translator = None
"""The translator object. (from deep_translator)"""
def MakeTranslator(type:str):
    """Will create the translator object.

    Args:
        type (str): Translator type. (google)
    """
    global origin
    global dest
    global translator
    
    del translator
    translator = None
    
    if type == "google":
        try:
            translator = dt.GoogleTranslator(source=origin, target=dest)
        except:
            try:
                translator = dt.GoogleTranslator(source="en", target="en")
            except:
                pass

MakeTranslator("google")
AVAILABLE_LANGUAGES = translator.get_supported_languages(as_dict=True)
"""A dictionary of all available languages."""
def FindLanguageFromCode(code:str):
    """Get language from code.

    Args:
        code (str): 2 letter language code.

    Returns:
        str: Language name.
    """
    for language in AVAILABLE_LANGUAGES:
        if AVAILABLE_LANGUAGES[language] == code:
            return language
    return None

def FindCodeFromLanguage(language:str):
    """Get 2 letter language code from language.

    Args:
        language (str): Language name.

    Returns:
        str: 2 letter language code.
    """
    for lang in AVAILABLE_LANGUAGES:
        if lang == language.lower():
            return AVAILABLE_LANGUAGES[lang]
    return None

def CheckCache(text:str, language:str=None):
    """Will check the translation cache for a specific text.

    Args:
        text (str): Text to check.
        language (str, optional): Language to check. If None will get from dest. Defaults to None.

    Returns:
        str / bool: Either the translation or False.
    """
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

def AddToCache(text:str, translation:str, language:str=None):
    """Will add a translation to the cache.

    Args:
        text (str): Original text.
        translation (str): Translation to add.
        language (str, optional): Language to associate. Defaults to None.
    """
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

def Translate(text:str, originalLanguage:str=None, destinationLanguage:str=None):
    """Will translate a given text.

    Args:
        text (str): The text to translate.
        originalLanguage (str, optional): The original language, if None will infer automatically. Defaults to None.
        destinationLanguage (str, optional): The destination language, if None will get from settings. Defaults to None.

    Returns:
        str: The translated text.
    """
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
    
    if translator == None:
        return text
    
    def TranslateText(text):
        try:
            if enableCache:
                cache = CheckCache(text)
                if cache != False:
                    return cache
                else:
                    mainUI.fps.set(f"TRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING")
                    mainUI.root.update()

                    translation = translator.translate(text, max_chars=20000)
                    AddToCache(text, translation)
                    return translation
            else:
                mainUI.fps.set(f"TRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING\tTRANSLATING")
                mainUI.root.update()

                translation = translator.translate(text)
                return translation
        except:
            return text # Return the original text if the translation fails
    
    # Check if the text is an array of strings
    if type(text) == list:
        translatedText = []
        for string in text:
            translatedText.append(TranslateText(string))
            
        return translatedText
    else:
        return TranslateText(text)
    
    
    