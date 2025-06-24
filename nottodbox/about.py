# SPDX-License-Identifier: GPL-3.0-or-later

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


import os
from PySide6.QtCore import Qt, qVersion
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import *
from consts import APP_VERSION
from widgets.controls import HSeperator, Label, PushButton


class About(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.icon_and_nottodbox = QWidget(self)
        
        self.icon = Label(self.icon_and_nottodbox)
        self.icon.setPixmap(self.windowIcon().pixmap(96, 96))
        
        self.nottodbox = Label(self.icon_and_nottodbox, self.tr("Nottodbox"))
        font = self.nottodbox.font()
        font.setBold(True)
        font.setPointSize(32)
        self.nottodbox.setFont(font)
        
        self.version_label = Label(self, self.tr("Version") + f': <a href="https://github.com/mukonqi/nottodbox/releases/tag/{APP_VERSION}">{APP_VERSION}</a>')
        self.version_label.setOpenExternalLinks(True)
        
        self.source_label = Label(self, self.tr("Source codes") + ': <a href="https://github.com/mukonqi/nottodbox">GitHub</a>')
        self.source_label.setOpenExternalLinks(True)

        self.developer_label = Label(self, self.tr("Developer") + ': <a href="https://mukonqi.github.io">MuKonqi (Muhammed S.)</a>')
        self.developer_label.setOpenExternalLinks(True)
        
        with open("@APP_DIR@/LICENSE.txt" if os.path.isfile("@APP_DIR@/LICENSE.txt") else 
                    f"{os.path.dirname(__file__)}/LICENSE.txt" if os.path.isfile(f"{os.path.dirname(__file__)}/LICENSE.txt") else
                    f"{os.path.dirname(os.path.dirname(__file__))}/LICENSE.txt") as license_file:
            license_text = license_file.read()
            
        self.license_textedit = QTextEdit(self)
        self.license_textedit.setFixedWidth(79 * 8 * QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).pointSize() / 10 + 
                                            QApplication.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarSliderMin) + 10)
        self.license_textedit.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.license_textedit.setText(license_text)
        self.license_textedit.setReadOnly(True)
        
        self.icon_and_nottodbox_layout = QHBoxLayout(self.icon_and_nottodbox)
        self.icon_and_nottodbox_layout.setSpacing(6)
        self.icon_and_nottodbox_layout.addStretch()
        self.icon_and_nottodbox_layout.addWidget(self.icon)
        self.icon_and_nottodbox_layout.addWidget(self.nottodbox)
        self.icon_and_nottodbox_layout.addStretch()
        
        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(self.icon_and_nottodbox)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.version_label)
        self.layout_.addWidget(self.source_label)
        self.layout_.addWidget(PushButton(self, QApplication.aboutQt, self.tr("Qt version:") + f" v{qVersion()}", False, True))
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.developer_label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(Label(self, self.tr("Copyright (C)") + f': 2024-2025 MuKonqi (Muhammed S.)'))
        self.layout_.addWidget(Label(self, self.tr("License: GNU General Public License, Version 3 or later")))
        self.layout_.addWidget(self.license_textedit, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout_.setStretchFactor(self.icon_and_nottodbox, 2)