import re
import os

file_path = os.path.join('src', 'Utilities.py')

if not os.path.exists(file_path):
    print(f'[ERROR] {file_path} not found!')
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    src = f.read()

pattern = (
    r'def\s+GetRemoteEndpoint\s*\([^)]*\):[\s\S]+?^(?=def |\Z)'
)
replacement = '''def GetRemoteEndpoint():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("1.1.1.1", 80))
        endpoint = s.getsockname()[0]
        s.close()
        return endpoint
    except Exception as e:
        print(f"[WARNING] Network unreachable in GetRemoteEndpoint: {e}")
        return "127.0.0.1"\n
'''

new_src, count = re.subn(pattern, replacement, src, flags=re.MULTILINE)
if count == 0:
    print('[WARN] GetRemoteEndpoint not patched! Функция не найдена или уже заменена.')
else:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_src)
    print('[INFO] Patched GetRemoteEndpoint in src/Utilities.py')
