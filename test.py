import os
import subprocess
try: status = subprocess.check_output("wg show wg0", shell=True)
except Exception: print("false")
else:print(status.decode("UTF-8"))