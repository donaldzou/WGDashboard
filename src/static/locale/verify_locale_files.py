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

for k in range(len(active_languages)):
    print(f"[Language] {active_languages[k]['lang_name']}")
    if active_languages[k]['lang_id'] != "en":
        with open(f"{active_languages[k]['lang_id']}.json", "r") as f:
            lang_file = json.loads(f.read())
            missing_translation = []
            deprecated_translation = []
    
            for a in language_template.keys():
                if a not in lang_file.keys():
                    missing_translation.append(a)
    
            for b in lang_file.keys():
                if b not in language_template.keys():
                    deprecated_translation.append(b)
    
    
            print("\t[Missing Translations]")
            if len(missing_translation) > 0:
                for a in range(len(missing_translation)):
                    print(f'\t\t"{missing_translation[a]}": ""{(',' if a < len(missing_translation) - 1 else '')}')
            else:
                print("\t\tNo missing translations")
    
    
            print("\n\t[Deprecated Translations]")
            if len(deprecated_translation) > 0:
                for a in range(len(deprecated_translation)):
                    print(f'\t\t"{deprecated_translation[a]}": "{lang_file[deprecated_translation[a]]}"')
    
            else:
                print("\t\tNo deprecated translations")   
            print()