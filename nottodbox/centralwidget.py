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
from widgets.controls import VSeperator
from about import About
from selector import Selector
from area import Area


class CentralWidget(QStackedWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        
        self.old_index = 0
        
        self.home = Home(self)
        self.settings = QWidget(self)
        self.about = About(self)
        
        self.addWidget(self.home)
        self.addWidget(self.settings)
        self.addWidget(self.about)
        
    @Slot(bool, int)
    def setCurrentIndex(self, checked: bool, index: int):
        super().setCurrentIndex(self.old_index if not checked else index)
        
        self.old_index = self.currentIndex()
        
        
class Home(QWidget):
    def __init__(self, parent: CentralWidget) -> None:
        super().__init__(parent)
        
        self.layout_ = QHBoxLayout(self)
        
        self.selector = Selector(self)
        
        self.seperator = VSeperator(self)
        
        self.area = Area(self)
        
        self.layout_.addWidget(self.selector)
        self.layout_.addWidget(self.seperator)
        self.layout_.addWidget(self.area)