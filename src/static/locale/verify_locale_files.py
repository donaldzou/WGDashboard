import json
import os
import sys

def load_json_file(filename):
    """Safely loads JSON data from a file."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to load {filename}: {e}")
        sys.exit(1)

def save_json_file(filename, data):
    """Saves JSON data to a file."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"[ERROR] Failed to save {filename}: {e}")
        sys.exit(1)

def print_header():
    """Clears the screen and prints a header."""
    os.system("clear" if os.name == "posix" else "cls")
    print("=" * 80)
    print(f" +              WGDashboard - Locale file checker [by @donaldzou]             + ")
    print("=" * 80)

def display_languages(active_languages):
    """Displays available active languages in an aligned format."""
    print("\nActive languages\n")

    max_lang_length = max(len(lang["lang_name"]) for lang in active_languages)

    print(f"{'Language'.ljust(max_lang_length)}   ID")
    print("-" * (max_lang_length + 6))
    lang_dict = {}
    
    for lang in active_languages:
        lang_name = lang["lang_name"].ljust(max_lang_length)
        lang_id = lang["lang_id"]
        print(f"{lang_name}   {lang_id}")
        lang_dict[lang_id] = lang["lang_name"]
    
    print()
    return lang_dict

def get_valid_language_id(lang_dict):
    """Asks the user for a valid language ID with an option to exit."""
    while True:
        lang_id = input("Enter the language ID to verify (or type 'exit' to cancel): ").strip().lower()

        if lang_id == "" or lang_id == "exit":
            print("\nExiting... Goodbye!")
            sys.exit(0)

        if lang_id not in lang_dict:
            print(f"[ERROR] '{lang_id}' is not a valid language ID. Please try again.")
        elif lang_id == "en":
            print(f"[WARNING] '{lang_id}' is not an editable language.")
        else:
            return lang_id

def verify_locale_file(lang_id, language_template):
    """Checks the selected language file for missing or deprecated translations."""
    lang_file_path = f"{lang_id}.json"

    if not os.path.exists(lang_file_path):
        print(f"[ERROR] Language file {lang_file_path} not found.")
        sys.exit(1)

    # Load existing language file
    lang_file = load_json_file(lang_file_path)

    # Identify missing and deprecated translations
    missing_translation = [key for key in language_template if key not in lang_file or not lang_file[key].strip()]
    deprecated_translation = [key for key in lang_file if key not in language_template]

    # Update language file by adding missing keys and removing deprecated ones
    for key in missing_translation:
        lang_file[key] = ""

    for key in deprecated_translation:
        lang_file.pop(key, None)

    # Save updated file
    save_json_file(lang_file_path, lang_file)

    # Summary report
    print(f"\n[Verification Results]")
    print(f"\t[Missing Translations]: {len(missing_translation)}")
    print(f"\t[Deprecated Translations]: {len(deprecated_translation)}")
    print(f"\t[NOTE] Missing translations were added as empty strings, deprecated ones removed.\n")

def main():
    """Main function."""
    print_header()

    # Load required JSON files
    active_languages = load_json_file("active_languages.json")
    language_template = load_json_file("language_template.json")

    # Display available languages and get user selection
    lang_dict = display_languages(active_languages)
    lang_id = get_valid_language_id(lang_dict)

    # Perform translation verification
    verify_locale_file(lang_id, language_template)

if __name__ == "__main__":
    main()
