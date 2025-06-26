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
from PySide6.QtGui import QIcon, QPalette, QPixmap
from PySide6.QtWidgets import *
from .widgets.controls import HSeperator, Label, ToolButton
from .consts import ICON_DIR


class Sidebar(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.old_index = 0
        
        self.icons = ["home", "settings", "about", "focus"]
        
        self.buttons = [
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 0), self.tr("Home"), True, None, 40),
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 1), self.tr("Settings"), True, None, 40),
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 2), self.tr("About"), True, None, 40),
            ToolButton(self, lambda: self.parent_.home.selector.setVisible(False if self.parent_.home.selector.isVisible() else True), self.tr("Focus"), True, None, 40)
        ]
        
        self.favorites = Favorites(self)
        
        # self.row_spinbox = QSpinBox(self)
        # self.row_spinbox.setMinimum(1)
        # self.row_spinbox.valueChanged.connect(lambda value: self.parent_.home.area.pages.setArea(value, self.column_spinbox.value()))
        
        # self.layout_label = Label(self, "x")
        # self.layout_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        # self.column_spinbox = QSpinBox(self)
        # self.column_spinbox.setMinimum(1)
        # self.column_spinbox.valueChanged.connect(lambda value: self.parent_.home.area.pages.setArea(self.row_spinbox.value(), value))
        
        self.layout_ = QVBoxLayout(self)

        for button in self.buttons:
            self.layout_.addWidget(button)
            
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.favorites)
        # self.layout_.addWidget(HSeperator(self))
        # self.layout_.addWidget(self.row_spinbox)
        # self.layout_.addWidget(self.layout_label)
        # self.layout_.addWidget(self.column_spinbox)
        self.layout_.setContentsMargins(5, 5, 5, 5)
        
        self.setFixedWidth(50)
        self.buttons[0].setChecked(True)
       
    @Slot(bool, int) 
    def setCurrentIndex(self, checked: bool, index: int) -> None:
        if (checked and index != 0) or (not checked and self.old_index != 0):
            self.buttons[-1].setVisible(False)
            
        else:
            self.buttons[-1].setVisible(True)
        
        self.buttons[self.old_index].setChecked(False if checked else True)
        
        self.old_index = index
        
        self.parent_.setCurrentIndex(checked, index)
    
    def makeIcon(self, name: str) -> QIcon:
        return QIcon(QPixmap(os.path.join(ICON_DIR, "actions", f"io.github.mukonqi.nottodbox_{name}_{"dark" if QApplication.palette().color(QPalette.ColorRole.WindowText).lightness() > QApplication.palette().color(QPalette.ColorRole.Window).lightness() else "light"}.svg")))
    
    def refresh(self) -> None:
        for i in range(4):
            self.buttons[i].setIcon(self.makeIcon(self.icons[i]))
    
    
class Favorites(QWidget):
    def __init__(self, parent: Sidebar) -> None:
        super().__init__(parent)
        
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)