import os
import subprocess
import shutil

with open("po/LINGUAS") as f:
    linguas = f.readlines()
    
for lang in linguas:
    if not os.path.isdir(f"AppDir/usr/local/lib/python3.12/dist-packages/nottodbox/locale/{lang}/LC_MESSAGES"):
        os.makedirs(f"AppDir/usr/local/lib/python3.12/dist-packages/nottodbox/locale/{lang}/LC_MESSAGES")
    
    subprocess.run(["msgfmt", f"po/{lang}.po"])
    shutil.move("messages.mo", f"AppDir/usr/local/lib/python3.12/dist-packages/nottodbox/locale/{lang}/LC_MESSAGES/nottodbox.mo")
    
    subprocess.run(["msgfmt", "--desktop", "--template", "share/applications/io.github.mukonqi.nottodbox.desktop.in", "-l", lang, "-o", "AppDir/usr/local/share/applications/io.github.mukonqi.nottodbox.desktop", f"po/{lang}.po"])
    subprocess.run(["msgfmt", "--xml", "--template", "share/metainfo/io.github.mukonqi.nottodbox.metainfo.xml.in", "-l", lang, "-o", "AppDir/usr/local/share/metainfo/io.github.mukonqi.nottodbox.metainfo.xml", f"po/{lang}.po"])