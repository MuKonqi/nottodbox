import os
import shutil
import subprocess

if os.environ.get("RUNNER_OS") == "Linux":
    directory = os.listdir()

    for name in directory:
        if "appimage" in name.lower():
            shutil.move(name, "dist/nottodbox.AppImage")

elif os.environ.get("RUNNER_OS") == "macOS":
    subprocess.run(["zip", "-r", "dist/nottodbox.app.zip", "dist/nottodbox.app"])
    os.remove("dist/nottodbox.app")
