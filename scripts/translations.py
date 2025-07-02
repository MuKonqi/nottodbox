import os
import subprocess
import sys

if "--appimage" in sys.argv:
    DESKTOP_FILE = "AppDir/usr/share/applications/io.github.mukonqi.nottodbox.desktop"
    METADATA_FILE = "AppDir/usr/share/metainfo/io.github.mukonqi.nottodbox.appdata.xml"

    os.makedirs("AppDir/usr/share/applications", exist_ok=True)
    os.makedirs("AppDir/usr/share/metainfo", exist_ok=True)
    
else:
    DESKTOP_FILE = "share/applications/io.github.mukonqi.nottodbox.desktop"
    METADATA_FILE = "share/metainfo/io.github.mukonqi.nottodbox.appdata.xml"


subprocess.run(["msgfmt", "--desktop", "-o", DESKTOP_FILE, "--template", "share/applications/io.github.mukonqi.nottodbox.desktop.in", "-d", "po"])
os.chmod(DESKTOP_FILE, 0o777)

subprocess.run(["msgfmt", "--xml", "-o", METADATA_FILE, "--template", "share/metainfo/io.github.mukonqi.nottodbox.appdata.xml.in", "-d", "po"])