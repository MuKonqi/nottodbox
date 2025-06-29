# SPDX-License-Identifier: GPL-3.0-or-later

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
from PySide6.QtCore import QStandardPaths


APP_ID = "io.github.mukonqi.nottodbox"

APP_MODE = "@MODE@"

APP_VERSION = "v0.0.90"


if APP_MODE == "meson":
    DATA_DIR = "@DATA_DIR@"
    
    
    LOCALE_DIR = "@LOCALE_DIR@"

else:
    if APP_MODE == "appimage":
        DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))), "share")
    
    else:
        DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "share")
    
    
    LOCALE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")


ICON_DIR = os.path.join(DATA_DIR, "icons", "hicolor", "scalable")

ICON_FILE = os.path.join(ICON_DIR, "apps", f"{APP_ID}.svg")


SETTINGS_DEFAULTS = [None, "disabled", "enabled", "markdown", None, "documents", "no", None, None, None, None, None, None, None, None, None]

SETTINGS_OPTIONS = ["default", "global"]

SETTINGS_KEYS = ["completed", "locked", "autosave", "format", "sync", "folder", "pinned", "bg_normal", "bg_hover", "bg_clicked", "fg_normal", "fg_hover", "fg_clicked", "bd_normal", "bd_hover", "bd_clicked"]

SETTINGS_VALUES = [["completed", "uncompleted", None], ["enabled", "disabled"], ["enabled", "disabled"], ["markdown", "html", "plain-text"], ["pdf", "odt", "markdown", "html", "plain-text"], ["documents", "desktop"], ["yes", "no"]]


USER_NAME = getpass.getuser()

USER_DIRS = {"desktop": QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0], "documents": QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DocumentsLocation)[0]}

with open("/etc/passwd") as f:
    passwd = f.readlines()
    
    for row in passwd:
        if row.startswith(USER_NAME):
            USER_NAME_PRETTY = row.split(":")[4]
            
            break

USER_DATABASES_DIR = os.path.join(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.GenericDataLocation)[0], "nottodbox", "databases")
os.makedirs(USER_DATABASES_DIR, exist_ok=True)