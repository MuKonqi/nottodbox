# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024 MuKonqi (Muhammed S.)

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
sys.dont_write_bytecode = True


import webbrowser as wb
from gettext import gettext as _
from PySide6.QtGui import QFontDatabase
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *


class AboutWidget(QWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.parent_.menuBar().addAction(_("About"), lambda: self.parent_.tabwidget.setCurrentIndex(5))
        
        self.version_label = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                              text=_("Version: {version}").format(version = "@VERSION@"))
        
        self.commit_label = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                             text=_("Commit: {commit}").format(commit = "@COMMIT@"))
        self.commit_label.setStyleSheet("margin-top: 10px")
        
        self.developer_label = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                                text=_("Developer: MuKonqi (Muhammed S.)"))
        self.developer_label.setStyleSheet("margin-top: 10px")
        
        self.copyright_label = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                                text=_("Copyright (C): 2024 MuKonqi (Muhammed S.)"))
        self.copyright_label.setStyleSheet("margin-top: 10px")
        
        self.license_label = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                              text=_("License: GNU General Public License, Version 3 or later"))
        self.license_label.setStyleSheet("margin-top: 10px")
        
        with open("@APPDIR@/LICENSE.txt") as license_file:
            license_text = license_file.read()
        
        self.license_textedit = QTextEdit(self)
        self.license_textedit.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.license_textedit.setText(license_text)
        self.license_textedit.setReadOnly(True)
        self.license_textedit.setStyleSheet("margin-bottom: 10px")
        
        self.developer_button = QPushButton(self, text=_("Open Developer's Page"))
        self.developer_button.clicked.connect(lambda: wb.open("https://mukonqi.github.io"))
        
        self.source_button = QPushButton(self, text=_("Open GitHub Page"))
        self.source_button.clicked.connect(lambda: wb.open("https://github.com/mukonqi/nottodbox", 2))
        
        self.website_button = QPushButton(self, text=_("Open Web Page"))
        
        self.flathub_button = QPushButton(self, text=_("Open Flathub Page"))
        
        self.setLayout(QGridLayout(self))
        self.layout().addWidget(self.version_label, 0, 0, 1, 4)
        self.layout().addWidget(self.commit_label, 1, 0, 1, 4)
        self.layout().addWidget(self.developer_label, 2, 0, 1, 4)
        self.layout().addWidget(self.copyright_label, 3, 0, 1, 4)
        self.layout().addWidget(self.license_label, 4, 0, 1, 4)
        self.layout().addWidget(self.license_textedit, 5, 0, 1, 4)
        self.layout().addWidget(self.developer_button, 6, 0, 1, 1)
        self.layout().addWidget(self.source_button, 6, 1, 1, 1)
        self.layout().addWidget(self.website_button, 6, 2, 1, 1)
        self.layout().addWidget(self.flathub_button, 6, 3, 1, 1)