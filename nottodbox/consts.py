# SPDX-License-Identifier: GPL-3.0-or-later

# Nottodbox (io.github.mukonqi.nottodbox)

# Copyright (C) 2025 MuKonqi (Muhammed S.)

# Nottodbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Nottodbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Nottodbox.  If not, see <https://www.gnu.org/licenses/>.


import getpass
import os


APP_ID = "io.github.mukonqi.nottodbox"

APP_MODE = "@MODE@"

APP_VERSION = "v0.0.9-3"


if APP_MODE == "meson":
    DATA_DIR = "@DATA_DIR@"
    
    
    LOCALE_DIR = "@LOCALE_DIR@"

else:
    if APP_MODE == "appimage":
        DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "share")
    
    else:
        DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "share")
    
    
    LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")

    
if APP_MODE == "appimage":
    DESKTOP_FILE = os.path.join(os.path.dirname(os.path.dirname(DATA_DIR)), f"{APP_ID}.desktop")
    
else:
    DESKTOP_FILE = os.path.join(DATA_DIR, "applications", f"{APP_ID}.desktop")
    
DESKTOP_FILE_FOUND = os.path.isfile(DESKTOP_FILE)

if not DESKTOP_FILE_FOUND and APP_MODE == "@MODE@":
    DESKTOP_FILE += ".in.in"
    
    DESKTOP_FILE_FOUND = os.path.isfile(DESKTOP_FILE)


ICON_FILE = os.path.join(DATA_DIR, "icons", "hicolor", "scalable", "apps", f"{APP_ID}.svg")


USER_NAME = getpass.getuser()


USER_DESKTOP_FILE = f"/home/{USER_NAME}/.local/share/applications/{APP_ID}.desktop"

USER_DESKTOP_FILE_FOUND = os.path.isfile(USER_DESKTOP_FILE)


with open("/etc/passwd") as f:
    passwd = f.readlines()
    
    for row in passwd:
        if row.startswith(USER_NAME):
            USER_NAME_PRETTY = row.split(":")[4]
            
            break


USER_DATABASES_DIR = f"/home/{USER_NAME}/.local/share/nottodbox/databases"
os.makedirs(USER_DATABASES_DIR, exist_ok=True)


SYSTEM_DESKTOP_FILE_FOUND = os.path.isfile(f"/usr/share/applications/{APP_ID}.desktop") or os.path.isfile(f"/usr/local/share/applications/{APP_ID}.desktop")