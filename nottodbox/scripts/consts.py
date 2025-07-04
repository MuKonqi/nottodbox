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


SETTINGS_DEFAULTS = [None, "disabled", "enabled", "markdown", None, "documents", "no", None, None, None, None, None, None, None, None, None]

SETTINGS_OPTIONS = ["default", "global"]

SETTINGS_KEYS = ["completed", "locked", "autosave", "format", "sync", "folder", "pinned", "bg_normal", "bg_hover", "bg_clicked", "fg_normal", "fg_hover", "fg_clicked", "bd_normal", "bd_hover", "bd_clicked"]

SETTINGS_VALUES = [["completed", "uncompleted", None], ["enabled", "disabled"], ["enabled", "disabled"], ["markdown", "html", "plain-text"], ["format", "pdf", "odt", "markdown", "html", "plain-text"], ["documents", "desktop"], ["yes", "no"]]


USER_NAME = getpass.getuser()

USER_DIRS = {"desktop": QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0], "documents": QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DocumentsLocation)[0]}

USER_DATABASES_DIR = os.path.join(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.GenericDataLocation)[0], "nottodbox", "databases")
os.makedirs(USER_DATABASES_DIR, exist_ok=True)