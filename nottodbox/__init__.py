#!@PYTHON3@

# SPDX-License-Identifier: GPL-3.0-or-later

# Nottodbox (io.github.mukonqi.nottodbox)

# Copyright (C) 2024-2025 MuKonqi (Muhammed S.)

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


import sys
import os
from PySide6.QtGui import QIcon
from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication


sys.path.insert(1, "@APP_DIR@" if os.path.isdir("@APP_DIR@") else os.path.dirname(__file__))

from consts import APP_ID, APP_VERSION, DESKTOP_FILE, ICON_FILE, USER_DESKTOP_FILE, USER_DESKTOP_FILE_FOUND  # type: ignore


from mainwindow import MainWindow

class Application(QApplication):
    def __init__(self, argv: list) -> None:
        super().__init__(argv)

        self.setApplicationVersion(APP_VERSION)
        self.setApplicationName("nottodbox")
        self.setApplicationDisplayName("Nottodbox")
        self.setDesktopFileName(USER_DESKTOP_FILE if USER_DESKTOP_FILE_FOUND else DESKTOP_FILE)
        self.setWindowIcon(QIcon.fromTheme(APP_ID, QIcon(ICON_FILE)))
        
        self.mainwindow = MainWindow()
               
application = Application(sys.argv)

sys.exit(application.exec())