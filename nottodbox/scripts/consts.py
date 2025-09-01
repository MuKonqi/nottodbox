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

from PySide6.QtCore import QStandardPaths, Qt

ITEM_DATAS = {
    "clicked": Qt.ItemDataRole.UserRole + 1,
    "type": Qt.ItemDataRole.UserRole + 2,
    "type_2": Qt.ItemDataRole.UserRole + 3,
    "setCurrentIndex": Qt.ItemDataRole.UserRole + 10,
    "open": Qt.ItemDataRole.UserRole + 11,
    "completed": Qt.ItemDataRole.UserRole + 20,
    "locked": Qt.ItemDataRole.UserRole + 21,
    "autosave": Qt.ItemDataRole.UserRole + 22,
    "format": Qt.ItemDataRole.UserRole + 23,
    "sync": Qt.ItemDataRole.UserRole + 24,
    "folder": Qt.ItemDataRole.UserRole + 25,
    "pinned": Qt.ItemDataRole.UserRole + 26,
    "bg_normal": Qt.ItemDataRole.UserRole + 27,
    "bg_hover": Qt.ItemDataRole.UserRole + 28,
    "bg_clicked": Qt.ItemDataRole.UserRole + 29,
    "fg_normal": Qt.ItemDataRole.UserRole + 30,
    "fg_hover": Qt.ItemDataRole.UserRole + 31,
    "fg_clicked": Qt.ItemDataRole.UserRole + 32,
    "bd_normal": Qt.ItemDataRole.UserRole + 33,
    "bd_hover": Qt.ItemDataRole.UserRole + 34,
    "bd_clicked": Qt.ItemDataRole.UserRole + 35,
    "notebook": Qt.ItemDataRole.UserRole + 100,
    "name": Qt.ItemDataRole.UserRole + 101,
    "creation": Qt.ItemDataRole.UserRole + 102,
    "modification": Qt.ItemDataRole.UserRole + 103,
    "content": Qt.ItemDataRole.UserRole + 104,
    "backup": Qt.ItemDataRole.UserRole + 105,
}

SETTINGS_DEFAULTS = [
    None,
    "disabled",
    "enabled",
    "markdown",
    None,
    "documents",
    "no",
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
]

SETTINGS_OPTIONS = ["default", "global"]

SETTINGS_KEYS = [
    "completed",
    "locked",
    "autosave",
    "format",
    "sync",
    "folder",
    "pinned",
    "bg_normal",
    "bg_hover",
    "bg_clicked",
    "fg_normal",
    "fg_hover",
    "fg_clicked",
    "bd_normal",
    "bd_hover",
    "bd_clicked",
]

SETTINGS_VALUES = [
    ["completed", "uncompleted", None],
    ["enabled", "disabled"],
    ["enabled", "disabled"],
    ["markdown", "html", "plain-text"],
    [f"format_{mode}" for mode in ["all", "export", "import"]]
    + ["pdf_export", "odt_export"]
    + [f"{base}_{mode}" for base in ["markdown", "html", "plain-text"] for mode in ["all", "export", "import"]],
    ["documents", "desktop"],
    ["yes", "no"],
]

USER_NAME = getpass.getuser()

USER_DIRS = {
    "desktop": QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0],
    "documents": QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DocumentsLocation)[0],
}

USER_NOTTODBOX_DIR = os.path.join(
    QStandardPaths.standardLocations(QStandardPaths.StandardLocation.GenericDataLocation)[0], "nottodbox"
)

USER_DATABASES_DIR = os.path.join(USER_NOTTODBOX_DIR, "databases")
os.makedirs(USER_DATABASES_DIR, exist_ok=True)

USER_LOGS_DIR = os.path.join(USER_NOTTODBOX_DIR, "logs")
os.makedirs(USER_LOGS_DIR, exist_ok=True)
