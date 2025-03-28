import xml.etree.ElementTree as ET
import sys
import os

sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "nottodbox"))

from consts import APP_VERSION # type: ignore

with open("share/metainfo/io.github.mukonqi.nottodbox.appdata.xml.in") as f:
    xml = ET.fromstring(f.read())
    
releases = xml.find("releases").findall("release")

changelog = ""

for release in releases:
    if release.attrib["version"] == APP_VERSION:
        for line in release.find("description").iter("ul"):
            changelog += f"<ul>{line.text}</ul>\n"
            
        break
    
changelog = changelog.removesuffix("\n")

with open("CHANGELOG.html", "w") as f:
    f.write(changelog)