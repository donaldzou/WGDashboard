import json
active_languages = json.loads(open("active_languages.json", "r").read())
language_template = json.loads(open("language_template.json", "r").read())
if __name__ == "__main__":
    welcome = "WGDashboard Locale File Verification [by @donaldzou]"
    print("="*(len(welcome) + 4))
    print(f"| {welcome} |")
    print("="*(len(welcome) + 4))
    print()
    print("Active Languages\n")
    status = False

    for language in active_languages:
        print(f"{language['lang_name']} | {language['lang_id']}")
    
    lang_ids = list(map(lambda x: x['lang_id'], active_languages))    
    print()
    
    lang_id = ""
    
    while not status:
        lang_id = input("Please enter the language ID to verify: ")
        if lang_id not in lang_ids:
            print(f'{lang_id} is not a valid language ID')
        elif lang_id == 'en':
            print(f'{lang_id} is not a editable language')
        else:
            status = True
        
    
    with open(f"{lang_id}.json", "r") as f:
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
    
    with open(f"{lang_id}.json", "w") as f:
        new_lang_file = dict(lang_file)
        for key in missing_translation:
            new_lang_file[key] = ""
    
        for key in deprecated_translation:
            new_lang_file.pop(key)
    
        f.write(json.dumps(new_lang_file, ensure_ascii=False, indent='\t'))
            
    
    print()
    # Print missing translations
    print(f"\t[Missing Translations] {len(missing_translation)} translation{'s' if len(missing_translation) > 1 else ''}")
    # Print deprecated translations
    print(f"\t[Deprecated Translations] {len(deprecated_translation)} translation{'s' if len(deprecated_translation) > 1 else ''}")
    print(f"\t[Note] All missing translations are added into {lang_id}.json, all deprecated translations are removed from {lang_id}.json")