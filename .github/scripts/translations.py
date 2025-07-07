import subprocess

with open("po/LINGUAS") as f:
    languages = f.read().split(" ")

for language in languages:
    subprocess.run(["pyside6-lrelease", f"locale/{language}.ts", "-qm", f"locale/{language}.qm"])

subprocess.run(["pyside6-rcc", "locale/locale.qrc", "-o", "nottodbox/scripts/resources/locale.py"])
