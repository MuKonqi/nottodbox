import os
import subprocess

with open("po/LINGUAS") as f:
    linguas = f.readlines()
    
for lang in linguas:
    lang = lang.removesuffix("\n")
    
    os.makedirs(f"AppDir/usr/lib/python3.13/site-packages/nottodbox/locale/{lang}/LC_MESSAGES", exist_ok=True)
    subprocess.run(["msgfmt", "-o", f"AppDir/usr/lib/python3.13/site-packages/nottodbox/locale/{lang}/LC_MESSAGES/nottodbox.mo", "-D", "po", f"{lang}.po"])
    
subprocess.run(["msgfmt", "--desktop", "-o", "AppDir/io.github.mukonqi.nottodbox.desktop", "--template", "share/applications/io.github.mukonqi.nottodbox.desktop.in", "-d", "po"])
os.chmod("AppDir/io.github.mukonqi.nottodbox.desktop", 0o777)

os.makedirs("AppDir/usr/share/metainfo", exist_ok=True)
subprocess.run(["msgfmt", "--xml", "-o", "AppDir/usr/share/metainfo/io.github.mukonqi.nottodbox.appdata.xml", "--template", "share/metainfo/io.github.mukonqi.nottodbox.appdata.xml.in", "-d", "po"])