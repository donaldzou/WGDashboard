# Not using it

# import os.path
# import shutil
# import requests
# import subprocess
# 
# class DashboardPluginsManager:
#     def __init__(self):
#         self.baseUrl = "https://api.github.com/repos/WGDashboard/WGDashboard-Plugins/contents/"
#         self.discoveredPlugins = {}
#         
#     def discoverPlugins(self):
#         self.discoveredPlugins.clear()
#         print('[#] Discovering plugins on GitHub')
#         try:
#             pluginsRepo = requests.get(self.baseUrl)
#             repoData = pluginsRepo.json()
#         except Exception as e:
#             print(f"[!] Failed to fetch list of plugins. Reason: {str(e)}")
#             exit(1)
# 
#         for plugin in repoData:
#             if plugin['type'] == 'dir' and not plugin['path'].startswith('.'):
#                 self.discoveredPlugins[plugin['name']] = plugin['url']
#         print(f'[#] Discovered {len(self.discoveredPlugins.keys())} plugin(s)')
#     
#     def downloadPlugin(self, url: str, level = 1):
#         chunkSize = 8192
#         try:
#             data = requests.get(url)
#             files = data.json()
#             for f in files:
#                 if f['type'] == 'dir':
#                     if not os.path.exists(f['path']):
#                         os.mkdir(f['path'])
#                         print(f"[#] {"  " * level}|__ {f['path']}")
#                     self.downloadPlugin(f['url'], level+1)
#                 elif f['type'] == 'file':
#                     
#                     data = requests.get(f['download_url'], stream=True)
#                     totalSize = int(f['size'])
#                     downloadedSize = 0
#                     with open(f['path'], 'wb+') as fb:
#                         for chunk in data.iter_content(chunk_size=chunkSize):
#                             if chunk:
#                                 fb.write(chunk)
#                                 if chunkSize >= totalSize or downloadedSize + chunkSize > totalSize:
#                                     downloadedSize = totalSize
#                                 else:
#                                     downloadedSize += chunkSize
#                                 percentage = round((downloadedSize / totalSize) * 100, 2)
#                                 print(f'\r[#] {"  " * level}|__ {f['name']}: {percentage}%', end='', flush=True)
#                     print()
#                     sha = subprocess.check_output(['git', 'hash-object', f['path']]).decode('utf-8').strip('\n')
#                     if sha != f['sha']:
#                         print(f"[!] File corrupted: {f['path']}")
#                         exit(1)
#         except Exception as e:
#             print(f"[!] Failed to download. Reason: {str(e)}")
#             print(e.__traceback__)
#             exit(1)
#         
#         
#     
# 
#         
#         
#     
#         
#         
# if __name__ == "__main__":
#     title = "WGDashboard Plugin Manager [by @donaldzou]"
#     border = "=" * (len(title) + 4)
# 
#     print(border)
#     print(f"| {title} |")
#     print(border)
#     print()
#     
#     downloader = DashboardPluginsManager()
#     downloader.discoverPlugins()
#     
#     if not downloader.discoveredPlugins:
#         print('[!] No plugin available')
#         exit(1)
#     
#     print()
#     pluginMenuTitle = 'Available Plugin(s)'
#     print(border)
#     print(f"| {pluginMenuTitle: ^{len(title)}} |")
#     print(border)
#     print()
#     for p in downloader.discoveredPlugins.keys():
#         print(f'[>] {p}')
#     print()  
#     print(border)
#     
#     choice = None
#     
#     print("[?] Which plugin you want to install")
#     print("[?] Or type [exit] to terminate")
#     while choice is None:
#         c = input("[?] Plugin name: ")
#         if c == 'exit':
#             exit(1)
#         if c in downloader.discoveredPlugins.keys():
#             choice = c
#         else:
#             print(f"[!] {c} is not a available plugin")
#     
#     if os.path.exists(choice):
#         print(f"[!] {choice} already installed. Install it again will remove previous installation.")
#         c = input("[?] Are you sure to continue [y/Y | n/N]: ")
#         if c.lower() == 'n':
#             print("[!] Exiting now...")
#             exit(0)
#         print("[#] Removing previous installation")
#         shutil.rmtree(choice)
#     os.mkdir(choice)
#     print(f"\n[#] Starting to download {choice}")
#     downloader.downloadPlugin(downloader.discoveredPlugins[choice])
#             