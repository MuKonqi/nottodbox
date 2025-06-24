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


from PySide6.QtCore import Slot
from PySide6.QtWidgets import *
from widgets.controls import HSeperator, PushButton, VSeperator 
        

class Area(QStackedWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.home = Home(self)
        self.pages = Pages(self)
        
        self.addWidget(self.home)
        self.addWidget(self.pages)
        
        self.setCurrentIndex(1)
        
        self.setContentsMargins(0, 0, 0, 0)
        
        
class Home(QWidget):
    def __init__(self, parent: Area) -> None:
        super().__init__(parent)
        
        self.layout_ = QGridLayout(self)
        
        
class Pages(QWidget):
    selectors = []
    
    def __init__(self, parent: Area)-> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QGridLayout(self)
        
        self.setArea(1, 1)
        
    @Slot(int, int)
    def setArea(self, row: int, column: int) -> None:
        for index in range(self.layout_.count()):
            self.layout_.itemAt(index).widget().deleteLater()
            
        for page in self.parent_.parent_.selector.options.pages.copy().values():
            self.parent_.parent_.selector.options.close(page)
            
        self.parent_.parent_.selector.options.pages = {}
            
        self.selectors = []
        
        for row_ in range(row):
            for column_ in range(column):
                self.selectors.append(Selector(self, row_, column_))
                self.layout_.addWidget(self.selectors[-1], row_, column_)
                
        self.focused_on = self.selectors[0]
        
        self.setAsFocused(self.selectors[0])
                
    @Slot()
    def setAsFocused(self, selector: QWidget) -> None:
        self.focused_on.button.setText(self.focused_on.tr("Click this button\nto select a document for here"))
        
        selector.button.setText(selector.tr("Select a document for here"))
        self.focused_on = selector


class Selector(QWidget):
    def __init__(self, parent: Pages, row: int, column: int):
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QGridLayout(self)
        
        if row != 0:
            self.layout_.addWidget(HSeperator(self), 0, 1)
            
        if column != 0:
            self.layout_.addWidget(VSeperator(self), 1, 0)
            
        self.button = PushButton(self, lambda: self.parent_.setAsFocused(self), self.tr("Click this button\nto select a document for here"), False, True, None)
        font = self.button.font()
        font.setBold(True)
        font.setPointSize(24)
        self.button.setFont(font)
    
        self.layout_.addWidget(self.button, 1, 1)