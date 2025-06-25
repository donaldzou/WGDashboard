#!/usr/bin/env python3
"""
Автоматически заменяет функцию GetRemoteEndpoint в src/Utilities.py на заглушку.
"""

import os
import re

UTILS_PATH = os.path.join('src', 'Utilities.py')

STUB = '''def GetRemoteEndpoint():
    return "127.0.0.1"
'''

def patch_utilities():
    if not os.path.isfile(UTILS_PATH):
        print(f"Файл не найден: {UTILS_PATH}")
        exit(1)
    with open(UTILS_PATH, 'r') as f:
        content = f.read()

    # Заменяем функцию на заглушку
    new_content, n = re.subn(
        r'def GetRemoteEndpoint\s*\([^)]*\):.*?(?=^def |\Z)',
        STUB,
        content,
        flags=re.DOTALL | re.MULTILINE,
    )

    if n == 0:
        print("Не удалось найти функцию GetRemoteEndpoint для замены.")
        exit(2)

    with open(UTILS_PATH, 'w') as f:
        f.write(new_content)
    print(f"Заглушка успешно вставлена в {UTILS_PATH}")

if __name__ == "__main__":
    patch_utilities()
