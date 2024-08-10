import ETS2LA.backend.settings as settings
import ETS2LA.variables as variables
import logging
import json
import ftfy
import sys
import os

DATA_FOLDER = "Translations"
FRONTEND_DATA_FOLDER = "frontend/src/translations"
LANGUAGE = settings.Get("global", "language", "en")

FILES = os.listdir(DATA_FOLDER)
FILES.remove("keys.json")
FILES.remove("comments.json")
KEYS = json.load(open(os.path.join(DATA_FOLDER, "keys.json"), "r", encoding="utf-8"))

LANGUAGE_DATA = {}
LANGUAGES = []
LANGUAGE_CODES = []

def LoadLanguageData():
    global LANGUAGE_DATA
    global LANGUAGES
    
    for file in FILES:
        LANGUAGE_DATA[file.split(".")[0]] = json.load(open(os.path.join(DATA_FOLDER, file), "r", encoding="utf-8"))
        LANGUAGES.append(LANGUAGE_DATA[file.split(".")[0]]["name"])
        LANGUAGE_CODES.append(file.split(".")[0])
        
LoadLanguageData()

def UpdateFrontendTranslations():
    # Remove old translations
    for file in os.listdir(FRONTEND_DATA_FOLDER):
        os.remove(os.path.join(FRONTEND_DATA_FOLDER, file))
        
    # Add new translations
    for language in LANGUAGE_DATA:
        with open(os.path.join(FRONTEND_DATA_FOLDER, f"{language}.json"), "w") as f:
            json.dump(LANGUAGE_DATA[language], f, indent=4)
            
def CheckLanguageDatabase():
    for language in LANGUAGE_CODES:
        for key in KEYS:
            if key not in LANGUAGE_DATA[language]:
                try:
                    logging.error(f"Did not find a value for {key} in {LANGUAGES[LANGUAGE_CODES.index(language)]}!")
                except:
                    pass # Probably encoding issue

def GetCodeForLanguage(language: str):
    if language in LANGUAGES:
        return LANGUAGE_CODES[LANGUAGES.index(language)]
    else:
        logging.error(f"{language} is not a valid language.")
        return None
    
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

def Translate(key: str, values: list = None) -> str:
    if not CheckKey(key):
        logging.error(f"{key} is not a valid key.")
        return ""
    
    if values is None:
        values = []
    
    if LANGUAGE not in LANGUAGE_DATA:
        logging.error(f"{LANGUAGE} is not a valid language.")
        return ""
    
    if key not in LANGUAGE_DATA[LANGUAGE]:
        if LANGUAGE == "en":
            logging.error(f"Did not find a value for {key} in English!")
            return ""
        if key not in LANGUAGE_DATA["en"]:
            logging.error(f"Did not find a value for {key} in English!")
            return ""
        return LANGUAGE_DATA["en"][key].format(*values)
    
    return ftfy.fix_text(LANGUAGE_DATA[LANGUAGE][key].format(*values))