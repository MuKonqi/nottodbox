import os
import subprocess
import shutil

with open("po/LINGUAS") as f:
    linguas = f.readlines()
    
for lang in linguas:
    os.makedirs(f"AppDir/usr/local/lib/python3.12/dist-packages/nottodbox/locale/{lang}/LC_MESSAGES")
    subprocess.run(["msgfmt", "-D", "po", f"{lang}.po"])
    shutil.move("messages.mo", f"AppDir/usr/local/lib/python3.12/dist-packages/nottodbox/locale/{lang}/LC_MESSAGESnottodbox.mo")