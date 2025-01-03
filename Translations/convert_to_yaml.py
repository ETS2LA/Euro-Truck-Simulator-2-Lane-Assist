import yaml
import json
import os

comments = None
keys = None
languages = []

json_files = [f for f in os.listdir('.') if f.endswith('.json')]
for json_file in json_files:
    if "comments" in json_file:
        with open(json_file, encoding='utf-8') as f:
            comments = json.load(f)
    elif "keys" in json_file:
        with open(json_file, encoding='utf-8') as f:
            keys = json.load(f)
    else:
        with open(json_file, encoding='utf-8') as f:
            languages.append(json.load(f))

# Convert the keys file
with open('keys.yaml', 'w', encoding='utf-8') as yaml_file:
    yaml.dump(keys, yaml_file, allow_unicode=True)

# Go through and add the comments to each language file
for language in languages:
    just_translations = {key: value for key, value in language.items() 
                         if key not in ["name", "name_en", "iso_code", "language_credits"]}
    

    with open(language['iso_code'] + ".yaml", 'w', encoding='utf-8') as yaml_file:
        yaml_file.write("Language:\n")
        yaml_file.write(f'  name: "{language["name"]}"\n')
        yaml_file.write(f'  # ^ The name of the language in its own language. Example: "Suomi"\n')
        yaml_file.write(f'  name_en: "{language["name_en"]}"\n')
        yaml_file.write(f'  # ^ The name of the language in English. Example: "Finnish"\n')
        yaml_file.write(f'  iso_code: "{language["iso_code"]}"\n')
        yaml_file.write(f'  # ^ The ISO 639-1 code for the language. Example: "fi"\n')
        yaml_file.write(f'  credits: "{language["language_credits"]}"\n')
        yaml_file.write(f'  # ^ The credits for the language show in the UI.\n')
        yaml_file.write(f'  version: "2.0.0"\n')
        yaml_file.write(f"  # ^ Latest compatible version. Checked by the UI for compatibility.\n\n")
        yaml_file.write(f"Translations:\n")
        for key, value in just_translations.items():
            if not key.startswith("_"):
                yaml_file.write(f'  {key}: "{value}"\n')
                if key in comments and comments[key] is not None:
                    yaml_file.write(f"  # ^ {comments[key].replace('\n', ' ')}\n")
            else:
                yaml_file.write("\n  # MARK: " + key[1:].replace("_", " ").lower().capitalize() + "\n\n")

print("All files have been converted to YAML format with comments.")