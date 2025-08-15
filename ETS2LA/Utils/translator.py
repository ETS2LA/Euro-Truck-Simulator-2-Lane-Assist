"""
The main translation interface for ETS2LA. Usual usage is to import the `_`
function and use it to translate strings, e.g. `_("Hello, World!")`.

Also provides a `ngettext` function for plural translations, e.g.
`ngettext("There is one apple", "There are {n} apples", n)`. This will
automatically handle pluralization for languages with more than two forms (or only one).

The `generate_translations` function should be called with the python file at the 
root of the project to update the translation files. Please lock and update the 
translations from weblate before generating, as you might hit merge conflicts otherwise.
"""

from ETS2LA.Utils.settings import Get, Listen, Set
from langcodes import Language
import datetime
import gettext
import os

# region Usage
def get_available_languages(localedir: str) -> list:
    """
    Get a list of available languages from the specified locale directory.
    
    :param localedir: The directory where the locale files are stored.
    :return: A list of available language codes.
    """
    languages = []
    for lang in os.listdir(localedir):
        if os.path.isdir(os.path.join(localedir, lang, "LC_MESSAGES")):
            languages.append(
                Language.get(lang)
            )
    return languages

languages = get_available_languages("Translations/locales")

class Translate:
    """
    A class to handle translations using gettext.
    """
    
    def __init__(self, domain: str, localedir: str, language: str):
        self.domain = domain
        self.localedir = localedir
        self.set_language(language)

    def set_language(self, language: str):
        self.translation = gettext.translation(self.domain, localedir=self.localedir, languages=[language], fallback=True)
        self.translation.install()
        self._ = self.translation.gettext
        self.language = language
        
    def get_language(self) -> str:
        """
        Get the currently set language.
        
        :return: The current language code.
        """
        return self.language
    
    def get_percentage(self) -> float:
        """
        Get the percentage of strings translated in the current language.
        """
        if self.language == "en":
            return 100.0
        
        po_file = f"{self.localedir}/{self.language}/LC_MESSAGES/{self.domain}.po"
        if not os.path.exists(po_file):
            return 0.0
        
        total_strings = -1 # Starts with one msgid that is not counted
        translated_strings = 0
        found_text = False
        
        with open(po_file, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("msgid") and not line.startswith("msgid_plural"):
                    total_strings += 1
                    if found_text:
                        translated_strings += 1
                        found_text = False
                    
                elif '"' in line and not line.startswith("#") and '""' not in line:
                    found_text = True
        
        if found_text:
            translated_strings += 1

        if total_strings > 0:
            translated_percentage = (translated_strings / total_strings) * 100
            if translated_percentage > 100.0:
                translated_percentage = 100.0
        else:
            translated_percentage = 0
        
        return translated_percentage

    def cleanup(self, string: str) -> str:
        """
        Clean up a string to remove unnecessary whitespace and
        fix common issues with foreign curly braces.
        
        :param string: The string to clean up.
        :return: The cleaned-up string.
        """
        string = string.strip()
        string = string.replace("｝", "}").replace("｛", "{")
        return string

    def __call__(self, key: str, *args) -> str:
        text = self.cleanup(self._(key))
        return text.format(*args) if args else text
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """
        Get the pluralized translation based on the count.
        
        :param singular: The singular form of the string.
        :param plural: The plural form of the string.
        :param n: The count to determine which form to use.
        :return: The translated string in singular or plural form.
        """
        return self.cleanup(
            self.translation.ngettext(singular, plural, n)
        )

def parse_language(language: Language) -> str:
    code = ""
    if language.script:
        code = language.language + "_" + language.script
    elif language.language == "zh" and not language.script:
        code = "zh_Hans"
    elif language.language == "nb":
        code = "nb_NO"
    else:
        code = language.language
        
    return code
    
default = Get("global", "language", "English")
if not default:
    Set("global", "language", "English")
    default = "English"
    
default = parse_language(Language.find(default))
_ = Translate("backend", "Translations/locales", default)  # Default to English
T_ = _
ngettext = _.ngettext  # Alias for ngettext

def set_language(language: str | Language):
    """
    Set the language for translations.
    
    :param language: The language code to set.
    """
    if not language:
        Set("global", "language", "English")
        language = "English"
    
    if isinstance(language, Language):
        language = language.language
        
    _.set_language(language)
    
def detect_change(dictionary: dict):
    language = dictionary.get("language", "English")
    if not language:
        language = "English"
    
    language = parse_language(Language.find(language))
    if language != _.get_language():
        set_language(language)
    
Listen("global", detect_change)

# region Generation
overrides = {
    "zh": "zh_Hans",
    "zh_2": "zh_Hant",
    "nb": "nb_NO"
}
count = {}

def generate_translations():
    """
    Generate translation files from the source code.
    """
    target_dir = "Translations/locales"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    package_name = "ETS2LA Backend"
    package_version = "1.0.0"
    organization = "ETS2LA Team"
    organization_email = "contact@ets2la.com"
    current_year = datetime.datetime.now().year
    
    # Generate base .pot file
    os.system(f"python ETS2LA/Assets/gettext/pygettext.py -d ets2la -w 9999 -c TRANSLATORS -o {target_dir}/base.pot .")
    
    # Header
    header_template = f'''# Translation template for {package_name}.
# Copyright (C) {current_year} {organization}
# This file is distributed under the same license as the root package.
# {organization} <{organization_email}>, {current_year}.
#

msgid ""
msgstr ""
"Project-Id-Version: {package_name} {package_version}\\n"
"POT-Creation-Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M%z')}\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: pygettext.py 1.5\\n"
'''
    
    # Replace the header in the base.pot file
    with open(f"{target_dir}/base.pot", "r", encoding="utf-8") as file:
        content = file.read()
        
    msgid_index = content.find("msgid \"\"")
    if msgid_index == -1:
        raise ValueError("msgid section not found in base.pot file.")
    
    generated_by_index = content.find("Generated-By:")
    if generated_by_index == -1:
        raise ValueError("Generated-By section not found in base.pot file.")
    
    msg_part = content[msgid_index:]
    content = header_template + msg_part[msg_part.find('\n', msg_part.find('Generated-By:')) + 1:]

    # Write back the updated content
    with open(f"{target_dir}/base.pot", "w", encoding="utf-8") as file:
        file.write(content)
    
    # Generate or update .po files for each language
    for lang in [language.language for language in languages]:
        if lang in overrides:
            count[lang] = count.get(lang, 0) + 1
            if count.get(lang, 0) >= 2:
                lang = f"{lang}_{count[lang]}"
            lang = overrides[lang]
            
        lang_dir = f"{target_dir}/{lang}/LC_MESSAGES"
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
        
        po_file = f"{lang_dir}/backend.po"
        
        # Check if the PO file already exists
        if os.path.exists(po_file):
            # If it exists, merge with the new template to preserve translations
            print(f"Updating existing translations for language: {lang}")
            os.system(f'msgmerge --update --no-wrap --backup=none --no-fuzzy-matching "{po_file}" "{target_dir}/base.pot"')
            continue
        else:
            print(f"ERROR: PO file for language {lang} does not exist.")
            print("Please add the real language code to the overrides.")
        
    print("Translation files have been successfully updated")