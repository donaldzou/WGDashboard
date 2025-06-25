#!/usr/bin/env python3
"""
Заменяет функцию GetRemoteEndpoint на заглушку в src/Utilities.py,
работает с любым содержимым функции.
"""

import os
import re

UTILS_PATH = os.path.join('src', 'Utilities.py')

STUB = '''def GetRemoteEndpoint() -> str:
    """
    STUB: Always returns 127.0.0.1 (localhost).
    """
    return "127.0.0.1"
'''

def patch_utilities():
    if not os.path.isfile(UTILS_PATH):
        print(f"Файл не найден: {UTILS_PATH}")
        exit(1)
    with open(UTILS_PATH, 'r') as f:
        content = f.read()

    # Используем регулярку, которая цепляет любую сигнатуру и тело функции
    pattern = r'def\s+GetRemoteEndpoint\s*\([^\)]*\)\s*(->\s*[^\:]+)?\:\s*([\s\S]+?)(?=^def |\Z)'
    new_content, n = re.subn(
        pattern,
        STUB,
        content,
        flags=re.MULTILINE
    )

    if n == 0:
        print("Не удалось найти функцию GetRemoteEndpoint для замены.")
        exit(2)

    with open(UTILS_PATH, 'w') as f:
        f.write(new_content)
    print(f"Заглушка успешно вставлена в {UTILS_PATH}")

if __name__ == "__main__":
    patch_utilities()
