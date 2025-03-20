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
from gettext import gettext as _
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import *
from widgets.others import HSeperator, Label


class AboutWidget(QWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.layout_ = QGridLayout(self)
        
        self.parent_.menuBar().addAction(_("About"), lambda: self.parent_.tabwidget.tabbar.setCurrentIndex(5))
        
        self.icon_and_nottodbox = QWidget(self)
        self.icon_and_nottodbox_layout = QHBoxLayout(self.icon_and_nottodbox)
        
        self.icon = Label(self.icon_and_nottodbox, "")
        self.icon.setPixmap(QIcon.fromTheme("io.github.mukonqi.nottodbox", self.parent_.application.getIcon()).pixmap(96, 96))
        
        self.nottodbox = Label(self.icon_and_nottodbox, _("Nottodbox"))
        font = self.nottodbox.font()
        font.setBold(True)
        font.setPointSize(32)
        self.nottodbox.setFont(font)
        
        self.version_label = Label(self, _("Version") + ': <a href="https://github.com/mukonqi/nottodbox/releases/tag/v0.0.8">v0.0.8</a>')
        self.version_label.setOpenExternalLinks(True)
        
        self.source_label = Label(self, _("Source codes") + ': <a href="https://github.com/mukonqi/nottodbox">GitHub</a>')
        self.source_label.setOpenExternalLinks(True)
        
        self.developer_label = Label(self, _("Developer") + ': <a href="https://mukonqi.github.io">MuKonqi (Muhammed S.)</a>')
        self.developer_label.setOpenExternalLinks(True)
        
        self.copyright_label = Label(self, _("Copyright (C)") + f': 2024-2025 MuKonqi (Muhammed S.)')
        
        self.license_label = Label(self, _("License: GNU General Public License, Version 3 or later"))
        
        self.icon_and_nottodbox.setLayout(self.icon_and_nottodbox_layout)
        self.icon_and_nottodbox_layout.setSpacing(6)
        self.icon_and_nottodbox_layout.addStretch()
        self.icon_and_nottodbox_layout.addWidget(self.icon)
        self.icon_and_nottodbox_layout.addWidget(self.nottodbox)
        self.icon_and_nottodbox_layout.addStretch()
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.icon_and_nottodbox)
        self.layout_.addWidget(self.version_label)
        self.layout_.addWidget(self.source_label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.developer_label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.copyright_label)
        self.layout_.addWidget(self.license_label)
        
        with open("@APP_DIR@/LICENSE.txt" if os.path.isfile("@APP_DIR@/LICENSE.txt") else 
                    f"{os.path.dirname(__file__)}/LICENSE.txt" if os.path.isfile(f"{os.path.dirname(__file__)}/LICENSE.txt") else
                    f"{os.path.dirname(os.path.dirname(__file__))}/LICENSE.txt") as license_file:
            license_text = license_file.read()
            
        self.license_textedit = QTextEdit(self)
        
        self.license_textedit.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.license_textedit.setText(license_text)
        self.license_textedit.setReadOnly(True)
        self.layout_.addWidget(self.license_textedit)