import os
import shutil
import subprocess

if os.environ.get("RUNNER_OS") == "Linux":
    directory = os.listdir()

    for name in directory:
        if "nottodbox" in name.lower() and "appimage" in name.lower():
            shutil.move(name, "dist/nottodbox.AppImage")

elif os.environ.get("RUNNER_OS") == "macOS":
    os.chdir("dist")
    subprocess.run(["zip", "-r", "nottodbox.app.zip", "nottodbox.app"])
    shutil.rmtree("nottodbox.app")
