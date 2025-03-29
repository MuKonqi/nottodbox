import xml.etree.ElementTree as ET
import sys
import os

sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "nottodbox"))

from consts import APP_VERSION # type: ignore

with open("share/metainfo/io.github.mukonqi.nottodbox.appdata.xml.in") as f:
    xml = ET.fromstring(f.read())
    
releases = xml.find("releases").findall("release")

changelog = "## What's Changed"

number = -1

for release in releases:
    number += 1
    
    if release.attrib["version"] == APP_VERSION:
        for line in release.find("description").find("ul").iter("li"):
            changelog += f'\n- {line.text}'
            
        break
    
changelog += f'\n\n**Full Changelog**: [{releases[number + 1].attrib["version"]}...{APP_VERSION}](https://github.com/MuKonqi/nottodbox/compare/{releases[number + 1].attrib["version"]}...{APP_VERSION})'

with open("CHANGELOG.md", "w") as f:
    f.write(changelog)