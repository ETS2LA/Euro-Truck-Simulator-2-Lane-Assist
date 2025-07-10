from ETS2LA.Utils.settings import Get, Listen
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

    def __call__(self, key: str, *args) -> str:
        return self._(key).format(*args) if args else self._(key)
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """
        Get the pluralized translation based on the count.
        
        :param singular: The singular form of the string.
        :param plural: The plural form of the string.
        :param n: The count to determine which form to use.
        :return: The translated string in singular or plural form.
        """
        return self.translation.ngettext(singular, plural, n)
    
default = Get("global", "language", "English")
default = Language.find(default).language
_ = Translate("ets2la", "Translations/locales", default)  # Default to English
T_ = _
ngettext = _.ngettext  # Alias for ngettext

def set_language(language: str | Language):
    """
    Set the language for translations.
    
    :param language: The language code to set.
    """
    if isinstance(language, Language):
        language = language.language
        
    _.set_language(language)
    
def detect_change(dictionary: dict):
    language = dictionary.get("language", "English")
    language = Language.find(language).language
    if language != _.get_language():
        set_language(language)
    
Listen("global", detect_change)

# region Generation
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
            # If it doesn't exist, create a new one
            print(f"Creating new translation file for language: {lang}")
            os.system(f'msginit --no-wrap --no-translator -l {lang} -i "{target_dir}/base.pot" -o "{po_file}"')
        
        # Fix the PO file header
        with open(po_file, "r", encoding="utf-8") as file:
            po_content = file.read()
        
        po_content = po_content.replace("PACKAGE VERSION", f"{package_name} {package_version}")
        po_content = po_content.replace("PACKAGE package", f"{package_name} package")
        
        # Only replace this for new files to avoid changing customized headers
        if "Translation template for" in po_content:
            po_content = po_content.replace(f"Translation template for {package_name}.", f"ETS2LA Backend Translations for {lang.upper()}")
        
        with open(po_file, "w", encoding="utf-8") as file:
            file.write(po_content)
        
    print("Translation files have been successfully updated")