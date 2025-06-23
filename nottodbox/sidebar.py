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
    

import os
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import *
from widgets.controls import HSeperator, Label, ToolButton
from consts import DARK_COLOR_SCHEME, ICON_DIR, ICON_FILE


class Sidebar(QWidget):
    def __init__(self, parent: QMainWindow, dock: QDockWidget) -> None:
        super().__init__(parent)
        
        self.setFixedWidth(dock.width())
        
        self.layout_ = QVBoxLayout(self)
        
        self.home_button = ToolButton(self, self.showHome, self.tr("Home"), True, self.makeIcon("home"), 40)
        
        self.focus_button = ToolButton(self, self.setFocus, self.tr("Focus"), True, self.makeIcon("focus"), 40)
        
        self.settings_button = ToolButton(self, self.showSettings, self.tr("Settings"), True, self.makeIcon("settings"), 40)
        
        self.about_button = ToolButton(self, self.showSettings, self.tr("Settings"), True, QIcon(ICON_FILE), 40)
        
        self.favorites = Favorites(self)
        
        self.row_spinbox = QSpinBox(self)
        # self.row_spinbox.valueChanged.connect()
        
        self.layout_label = Label(self, "x")
        self.layout_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.column_spinbox = QSpinBox(self)
        # self.column_spinbox.valueChanged.connect()

        self.layout_.addWidget(self.home_button)
        self.layout_.addWidget(self.focus_button)
        self.layout_.addWidget(self.settings_button)
        self.layout_.addWidget(self.about_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.favorites)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.row_spinbox)
        self.layout_.addWidget(self.layout_label)
        self.layout_.addWidget(self.column_spinbox)
        self.layout_.setContentsMargins(5, 5, 5, 5)
        
    @Slot()
    def setFocus(self) -> None:
        pass
        
    @Slot()
    def showHome(self) -> None:
        pass
    
    @Slot()
    def showSettings(self) -> None:
        pass
    
    def makeIcon(self, name: str) -> QIcon:
        return QIcon(QPixmap(os.path.join(ICON_DIR, "actions", f"io.github.mukonqi.nottodbox_{name}_{"dark" if DARK_COLOR_SCHEME else "light"}.svg")))
    
    
class Favorites(QWidget):
    def __init__(self, parent: Sidebar) -> None:
        super().__init__(parent)
        
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)