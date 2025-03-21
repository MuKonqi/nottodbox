import os
import subprocess

with open("po/LINGUAS") as f:
    linguas = f.readlines()
    
for lang in linguas:
    if not os.path.isdir(f"AppDir/usr/local/lib/python3.13/dist-packages/nottodbox/locale/{lang}/LC_MESSAGES"):
        os.makedirs(f"AppDir/usr/local/lib/python3.13/dist-packages/nottodbox/locale/{lang}/LC_MESSAGES")
    
    subprocess.run(["msgfmt", "-o", f"AppDir/usr/local/lib/python3.13/dist-packages/nottodbox/locale/{lang}/LC_MESSAGES/nottodbox.mo", f"po/{lang}.po"])
    subprocess.run(["msgfmt", "--desktop", "-l", lang, "-o", "AppDir/io.github.mukonqi.nottodbox.desktop", "--template", "share/applications/io.github.mukonqi.nottodbox.desktop.in", f"po/{lang}.po"])