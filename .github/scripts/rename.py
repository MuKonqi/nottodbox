import os
import shutil

if os.environ.get("RUNNER_OS") == "Linux":
    directory = os.listdir()

    for name in directory:
        if "appimage" in name.lower():
            shutil.move(name, "dist/nottodbox.AppImage")

elif os.environ.get("RUNNER_OS") == "macOS":
    shutil.move("dist/nottodbox", "dist/nottodbox-mac")