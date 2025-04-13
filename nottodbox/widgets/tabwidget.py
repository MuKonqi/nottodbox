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


from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import *
from .others import HSeperator, PushButton, VSeperator


class TabWidget(QStackedWidget):
    def __init__(self, parent: QMainWindow, alignment: Qt.AlignmentFlag) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.alignment = alignment
        
        self.current_index = 0
        
        self.pages = {}
        
        self.tabs = []
        
        self.tabbars = []
        
        self.tabbars_widget = QWidget(self.parent_)
        
        if alignment == Qt.AlignmentFlag.AlignTop:
            self.tabbars_layout = QHBoxLayout(self.tabbars_widget)
       
        elif alignment == Qt.AlignmentFlag.AlignLeft:
            self.tabbars_layout = QVBoxLayout(self.tabbars_widget)
        
    def addPage(self, text: str, page: QWidget, seperator: bool = False, icon: QIcon | None = None) -> None:
        if seperator or self.tabbars == []:
            if seperator:
                self.tabbars[-1].addingFinished()
            
            tabbar = TabButtons(self, self.alignment)
            
            self.tabbars.append(tabbar)
            
            self.tabbars_layout.addWidget(tabbar)
        
        self.tabs.append(self.tabbars[-1].addButton(text))
        
        self.pages[page] = self.tabs[-1]
        
        if icon is not None:
            self.tabs[-1].button.setIcon(icon)
        
        self.addWidget(page)
        
    def finished(self) -> None:
        self.tabbars[-1].addingFinished()
        
        if self.alignment == Qt.AlignmentFlag.AlignTop:
            width = self.parent_.width() / (len(self.tabs) + len(self.tabbars) - 1)
            height = 30
        
        elif self.alignment == Qt.AlignmentFlag.AlignLeft:
            width = 30
            height = self.parent_.height() / (len(self.tabs) + len(self.tabbars) - 1)
        
        number = 0
        
        stretchs = {}
        stretch_counter = 0
        
        last_tabbar = self.tabbars[0]
        
        for tab in self.tabs:
            if last_tabbar == tab.parent_:
                stretch_counter += 1
                stretchs[last_tabbar] = stretch_counter
            
            else:
                stretch_counter = 1
                stretchs[tab.parent_] = 1
                
                number += 2
                
                self.tabbars_layout.insertSpacerItem(number - 1, QSpacerItem(width, height))
                self.tabbars_layout.setStretch(number - 1, 1)
                
            last_tabbar = tab.parent()
        
        for tabbar, stretch in stretchs.items():
            self.tabbars_layout.setStretch(self.tabbars_layout.indexOf(tabbar), stretch)
        
    def setCurrentPage(self, page: int | QWidget) -> None:
        tabs = self.tabs.copy()

        tabs[page if type(page) == int else self.indexOf(page)].setSelected()
            
        tabs.pop(page if type(page) == int else self.indexOf(page))
        
        for tab in tabs:
            tab.setUnselected()
            
        self.setCurrentIndex(page if type(page) == int else self.indexOf(page))


class TabButton(QWidget):
    def __init__(self, parent: QWidget, text: str, alignment: Qt.AlignmentFlag) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.button = PushButton(self, text)
        self.button.setCheckable(True)
        self.button.clicked.connect(self.setSelected)
        self.button.clicked.connect(lambda state: self.parent_.parent_.setCurrentPage(self.parent_.parent_.tabs.index(self)))
        
        self.layout_ = QGridLayout(self)
        
        if alignment == Qt.AlignmentFlag.AlignTop:
            margins = self.layout_.contentsMargins()
            margins.setBottom(0)
            
            self.seperators = [VSeperator(self), VSeperator(self), HSeperator(self)]
            self.seperators[0].setFixedHeight(30)
            self.seperators[1].setFixedHeight(30)
            
            self.layout_.setContentsMargins(margins)
            self.layout_.addWidget(self.seperators[0], 0, 0, 1, 1)
            self.layout_.addWidget(self.button, 0, 1, 1, 1)
            self.layout_.addWidget(self.seperators[1], 0, 2, 1, 1)
            self.layout_.addWidget(self.seperators[2], 1, 1, 1, 1)
            
        elif alignment == Qt.AlignmentFlag.AlignLeft:
            self.seperators = [HSeperator(self), HSeperator(self)]
            
            self.layout_.addWidget(self.seperators[0], 0, 0, 1, 1)
            self.layout_.addWidget(self.button, 1, 0, 1, 1)
            self.layout_.addWidget(self.seperators[1], 2, 0, 1, 1)
        
    @Slot()
    def setSelected(self) -> None:
        self.button.setChecked(True)
        
        for seperator in self.seperators:
            seperator.setVisible(True)
            
    def setUnselected(self) -> None:
        self.button.setChecked(False)
        
        for seperator in self.seperators:
            seperator.setVisible(False)
        
        
class TabButtons(QWidget):
    def __init__(self, parent: TabWidget, alignment: Qt.AlignmentFlag) -> None:
        super().__init__(parent)

        self.parent_ = parent
        self.alignment = alignment
        
        self.tabs = []
        
        self.layout_ = QGridLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(0)
        
    def addButton(self, text: str) -> TabButton:
        self.tabs.append(TabButton(self, text, self.alignment))
        
        if self.alignment == Qt.AlignmentFlag.AlignTop:
            self.layout_.addWidget(self.tabs[-1], 1, len(self.tabs) - 1, 1, 1)
            
        elif self.alignment == Qt.AlignmentFlag.AlignLeft:
            self.layout_.addWidget(self.tabs[-1], len(self.tabs) - 1, 2, 1, 1)
            
            seperator = HSeperator(self)
            seperator.setFixedWidth(4)
            self.layout_.addWidget(seperator, len(self.tabs) - 1, 1, 1, 1)
        
        return self.tabs[-1]
            
    def addingFinished(self) -> None:
        if self.alignment == Qt.AlignmentFlag.AlignTop:
            self.layout_.addWidget(HSeperator(self), 0, 0, 1, len(self.tabs))
            
        elif self.alignment == Qt.AlignmentFlag.AlignLeft:
            self.layout_.addWidget(VSeperator(self), 0, 0, len(self.tabs), 1)