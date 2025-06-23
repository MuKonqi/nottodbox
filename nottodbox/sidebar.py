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
from consts import DARK_COLOR_SCHEME, ICON_DIR


class Sidebar(QWidget):
    def __init__(self, parent: QMainWindow, dock: QDockWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.old_index = 0
        
        self.layout_ = QVBoxLayout(self)
        
        self.buttons = [
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 0), self.tr("Home"), True, self.makeIcon("home"), 40),
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 1), self.tr("Settings"), True, self.makeIcon("settings"), 40),
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 2), self.tr("About"), True, self.makeIcon("about"), 40)
        ]
        
        self.favorites = Favorites(self)
        
        self.row_spinbox = QSpinBox(self)
        self.row_spinbox.setMinimum(1)
        # self.row_spinbox.valueChanged.connect()
        
        self.layout_label = Label(self, "x")
        self.layout_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.column_spinbox = QSpinBox(self)
        self.column_spinbox.setMinimum(1)
        # self.column_spinbox.valueChanged.connect()

        for button in self.buttons:
            self.layout_.addWidget(button)
            
        self.layout_.addWidget(ToolButton(self, lambda: self.parent_.centralWidget().home.selector.setVisible(False if self.parent_.centralWidget().home.selector.isVisible() else True), self.tr("Focus"), True, self.makeIcon("focus"), 40))
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.favorites)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.row_spinbox)
        self.layout_.addWidget(self.layout_label)
        self.layout_.addWidget(self.column_spinbox)
        self.layout_.setContentsMargins(5, 5, 5, 5)
        
        self.setFixedWidth(dock.width())
        self.buttons[0].setChecked(True)
       
    @Slot(bool, int) 
    def setCurrentIndex(self, checked: bool, index: int) -> None:
        self.buttons[self.old_index].setChecked(False if checked else True)
        
        self.old_index = index
        
        self.parent_.centralWidget().setCurrentIndex(checked, index)
    
    def makeIcon(self, name: str) -> QIcon:
        return QIcon(QPixmap(os.path.join(ICON_DIR, "actions", f"io.github.mukonqi.nottodbox_{name}_{"dark" if DARK_COLOR_SCHEME else "light"}.svg")))
    
    
class Favorites(QWidget):
    def __init__(self, parent: Sidebar) -> None:
        super().__init__(parent)
        
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)