import os
import subprocess
import sys

if "--appimage" in sys.argv:
    LOCALE_DIR = "AppDir/usr/lib/python3.13/site-packages/nottodbox/locale"
    DESKTOP_FILE = "AppDir/usr/share/applications/io.github.mukonqi.nottodbox.desktop"
    METADATA_FILE = "AppDir/usr/share/metainfo/io.github.mukonqi.nottodbox.appdata.xml"
    
    os.makedirs("AppDir/usr/share/applications", exist_ok=True)
    os.makedirs("AppDir/usr/share/metainfo", exist_ok=True)
    
else:
    LOCALE_DIR = "nottodbox/locale"
    DESKTOP_FILE = "share/applications/io.github.mukonqi.nottodbox.desktop"
    METADATA_FILE = "share/metainfo/io.github.mukonqi.nottodbox.appdata.xml"
    

with open("po/LINGUAS") as f:
    linguas = f.readlines()
    
for lang in linguas:
    lang = lang.removesuffix("\n")
    
    os.makedirs(f"{LOCALE_DIR}/{lang}/LC_MESSAGES", exist_ok=True)
    subprocess.run(["msgfmt", "-o", f"{LOCALE_DIR}/{lang}/LC_MESSAGES/nottodbox.mo", "-D", "po", f"{lang}.po"])


subprocess.run(["msgfmt", "--desktop", "-o", DESKTOP_FILE, "--template", "share/applications/io.github.mukonqi.nottodbox.desktop.in.in", "-d", "po"])
os.chmod(DESKTOP_FILE, 0o777)

subprocess.run(["msgfmt", "--xml", "-o", METADATA_FILE, "--template", "share/metainfo/io.github.mukonqi.nottodbox.appdata.xml.in", "-d", "po"])