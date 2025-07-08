import os
import sys

with open(os.path.join("nottodbox", "scripts", "version.py")) as f_read:
    lines = f_read.readlines()

new_lines = []
fount_app_build = False
for line in lines:
    if line.startswith("APP_BUILD"):
        new_line = f'APP_BUILD = "{"Flatpak" if "--flatpak" in sys.argv else "AppImage" if os.environ.get("RUNNER_OS") == "Linux" else "PyInstaller"}"\n'
        new_lines.append(new_line)
        fount_app_build = True
    else:
        new_lines.append(line)

if not fount_app_build:
    new_lines.append(f'APP_BUILD = "{"Flatpak" if "--flatpak" in sys.argv else "AppImage" if os.environ.get("RUNNER_OS") == "Linux" else "PyInstaller"}"\n')

with open(os.path.join("nottodbox", "scripts", "version.py"), "w") as f_write:
    f_write.writelines(new_lines)
