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
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QLocale, QTranslator
from PySide6.QtWidgets import QApplication
from scripts.consts import APP_ID, APP_VERSION
from scripts.mainwindow import MainWindow
from scripts.resources import icons, locale # noqa: F401

class Application(QApplication):
    def __init__(self, argv: list) -> None:
        super().__init__(argv)

        self.setApplicationVersion(APP_VERSION)
        self.setApplicationName("nottodbox")
        self.setApplicationDisplayName("Nottodbox")
        self.setDesktopFileName(APP_ID)
        self.setWindowIcon(QIcon.fromTheme(APP_ID, QIcon(QPixmap(":/icons/window"))))
        
        translator = QTranslator(self)
        if translator.load(QLocale().system(), "", "", ":/locale"):
            self.installTranslator(translator)
        
        self.mainwindow = MainWindow()
               
application = Application(sys.argv)

sys.exit(application.exec())