from ETS2LA.Utils.submodules import EnsureSubmoduleExists
import ETS2LA.Utils.settings as settings
import ETS2LA.variables as variables
import hashlib
import logging
import yaml
import ftfy
import os

DATA_FOLDER = "Translations"
FRONTEND_DATA_FOLDER = "Interface/translations"

EnsureSubmoduleExists("Translations", "https://github.com/ETS2LA/translations.git",
                      cdn_url="https://cdn.ets2la.com/translations", cdn_path="translations-main",
                      download_updates=not variables.DEVELOPMENT_MODE)

FILES = [file for file in os.listdir(DATA_FOLDER) if file.endswith(".yaml")]
FILES.remove("keys.yaml")
KEYS = yaml.safe_load(open(os.path.join(DATA_FOLDER, "keys.yaml"), "r", encoding="utf-8"))

LANGUAGE_DATA = {}
LANGUAGES = []
LANGUAGE_CODES = []

def LoadLanguageData():
    global LANGUAGE_DATA
    global LANGUAGES, LANGUAGE_CODES
    
    LANGUAGE_DATA = {}
    LANGUAGES = []
    LANGUAGE_CODES = []
    
    for file in FILES:
        LANGUAGE_DATA[file.split(".")[0]] = yaml.safe_load(open(os.path.join(DATA_FOLDER, file), "r", encoding="utf-8"))
        LANGUAGES.append(LANGUAGE_DATA[file.split(".")[0]]["Language"]["name"])
        LANGUAGE_CODES.append(file.split(".")[0])
        
LoadLanguageData()

try:
    # Ugly hack to get the default locale on Windows
    import locale
    default_locale = locale.getlocale()[0]
    if default_locale is None:
        default_locale = "English"
    else:
        name = default_locale.split("_")[0].split("(")[0]
        if "Taiwan" in default_locale:
            name = "Traditional Chinese (Taiwan)"
        elif "China" in default_locale:
            name = "Simplified Chinese"
        default_locale = name
    
    LANGUAGE = LANGUAGE_CODES[LANGUAGES.index(settings.Get("global", "language", default_locale))]
except ValueError:
    logging.warning(f"Language '{settings.Get('global', 'language', 'English')}' not found. Falling back to English.")
    LANGUAGE = LANGUAGE_CODES[LANGUAGES.index("English")]
    settings.Set("global", "language", "English")

def UpdateFrontendTranslations():
    try:
        if os.path.exists(FRONTEND_DATA_FOLDER):
            # Remove old translations
            for file in os.listdir(FRONTEND_DATA_FOLDER):
                os.remove(os.path.join(FRONTEND_DATA_FOLDER, file))
                
            # Add new translations
            for language in LANGUAGE_DATA:
                with open(os.path.join(FRONTEND_DATA_FOLDER, f"{language}.yaml"), "w", encoding="utf-8") as f:
                    yaml.dump(LANGUAGE_DATA[language], f, indent=4)
    except:
        pass
    
if variables.LOCAL_MODE:
    UpdateFrontendTranslations()
                
def CheckLanguageDatabase():
    for language in LANGUAGE_CODES:
        not_found = []
        for key in KEYS:
            if key not in LANGUAGE_DATA[language]["Translations"] and key not in LANGUAGE_DATA[language]["Language"]:
                try:
                    not_found.append(key)
                except:
                    pass # Probably encoding issue
                
        not_in_keys = []
        for key in LANGUAGE_DATA[language]["Translations"]:
            if key not in KEYS:
                if not key.startswith("_"):
                    not_in_keys.append(key)
        
        if len(not_found) > 0:
            if variables.DEVELOPMENT_MODE:
                logging.warning(f"Did not find values for the following keys in [dim]{LANGUAGE_DATA[language]['Language']['name_en']}[/dim]: {not_found}")
        if len(not_in_keys) > 0:
            if variables.DEVELOPMENT_MODE:
                logging.warning(f"Found keys that are not in the keys.yaml file in [dim]{LANGUAGE_DATA[language]['Language']['name_en']}[/dim]: {not_in_keys}")

def GetCodeForLanguage(language: str) -> str:
    if language in LANGUAGES:
        return LANGUAGE_CODES[LANGUAGES.index(language)]
    else:
        logging.error(f"{language} is not a valid language.")
        return ""
    
def GetLanguageForCode(code: str):
    if code in LANGUAGE_CODES:
        return LANGUAGES[LANGUAGE_CODES.index(code)]
    else:
        logging.error(f"{code} is not a valid language code.")
        return None

def CheckKey(key: str):
    if key in KEYS:
        return True
    else:
        return False
    
def SpecialCases(key: str | None, language: str | None = None) -> str:
    if language:
        if key in LANGUAGE_DATA[language]["Language"]:
            return LANGUAGE_DATA[language]["Language"][key]
        return ""
    
    if key in LANGUAGE_DATA[LANGUAGE]["Language"]:
        return LANGUAGE_DATA[LANGUAGE]["Language"][key]
    return ""

def TranslateToLanguage(key: str, language: str, values: list = None) -> str: # type: ignore
    if not CheckKey(key):
        logging.error(f"{key} is not a valid key.")
        return ""
    
    if SpecialCases(key, language=language) != "":
        return SpecialCases(key, language=language)
    
    if values is None:
        values = []
    
    if language not in LANGUAGE_DATA:
        logging.error(f"{language} is not a valid language.")
        return ""
    
    if key not in LANGUAGE_DATA[language]["Translations"]:
        if language == "en":
            logging.error(f"Did not find a value for {key} in English!")
            return ""
        if key not in LANGUAGE_DATA["en"]:
            logging.error(f"Did not find a value for {key} in English!")
            return ""
        return LANGUAGE_DATA["en"][key].format(*values)
    
    return ftfy.fix_text(LANGUAGE_DATA[language]["Translations"][key].format(*values))

def Translate(key: str, values: list = None, return_original: bool = False) -> str: # type: ignore
    if not CheckKey(key):
        if return_original:
            return key
        
        logging.error(f"{key} is not a valid key.")
        return ""
    
    if SpecialCases(key) != "":
        return SpecialCases(key)
    
    if values is None:
        values = []
    
    if LANGUAGE not in LANGUAGE_DATA:
        logging.error(f"{LANGUAGE} is not a valid language.")
        return ""
    
    if key not in LANGUAGE_DATA[LANGUAGE]["Translations"]:
        if LANGUAGE == "en":
            logging.error(f"Did not find a value for {key} in English!")
            if return_original:
                return key
            return ""
        if key not in LANGUAGE_DATA["en"]:
            logging.error(f"Did not find a value for {key} in English!")
            if return_original:
                return key
            return ""
        return LANGUAGE_DATA["en"][key].format(*values)
    
    return ftfy.fix_text(LANGUAGE_DATA[LANGUAGE]["Translations"][key].format(*values))

def UpdateLanguageData(settings_dict: dict):
    global LANGUAGE
    try:
        new_language = LANGUAGE_CODES[LANGUAGES.index(settings_dict.get("language", "English"))]
        if new_language != LANGUAGE:
            logging.info(f"Language changed to {settings_dict.get('language', 'English')}")
            LANGUAGE = new_language
            
    except ValueError:
        logging.warning(f"Language '{settings_dict.get('language', 'English')}' not found. Falling back to English.")
        LANGUAGE = LANGUAGE_CODES[LANGUAGES.index("English")]
        settings.Set("global", "language", "English")

settings.Listen("global", UpdateLanguageData)
