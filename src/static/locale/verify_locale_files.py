import json
import os.path

from typing_extensions import deprecated

active_languages = json.loads(open("active_languages.json", "r").read())
language_template = json.loads(open("language_template.json", "r").read())
welcome = "WGDashboard Locale File Verification [by @donaldzou]"

print("="*(len(welcome) + 4))
print(f"| {welcome} |")
print("="*(len(welcome) + 4))
print()
print("Active Languages")

status = {}

for language in active_languages:
    print(f"[Language] {language['lang_name']}")
    
    if language['lang_id'] != "en":
        with open(f"{language['lang_id']}.json", "r") as f:
            lang_file = json.load(f)
        
        # Identify missing and deprecated translations
        missing_translation = [
            key for key in language_template
            if key not in lang_file or not lang_file[key].strip()
            ]
        
        deprecated_translation = [
            key for key in lang_file
            if key not in language_template
            ]
        
        # Print missing translations
        print("\t[Missing Translations]")
        if missing_translation:
            print(",\n".join(f'\t\t"{key}": ""'
                    for key in missing_translation))
        else:
            print("\t\tNo missing translations")
        
        # Print deprecated translations
        print("\n\t[Deprecated Translations]")
        if deprecated_translation:
            print("\n".join(f'\t\t"{key}": "{lang_file[key]}"'
                    for key in deprecated_translation))
        else:
            print("\t\tNo deprecated translations")
        
        print()
