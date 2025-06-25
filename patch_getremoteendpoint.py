# patch_getremoteendpoint.py
# Костыль-заглушка для функции GetRemoteEndpoint — возвращает 127.0.0.1

def GetRemoteEndpoint():
    return "127.0.0.1"
