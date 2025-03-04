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


import typing
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import *


class Action(QAction):
    def __init__(self, parent: QWidget, text: str = ""):
        super().__init__(text, parent)
        

class Combobox(QComboBox):
    def addItems(self, texts: list[str] | tuple[str]):
        self.clear()
        return super().addItems(texts)


class HSeperator(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.HLine)
        
        
class Label(QLabel):
    def __init__(self, parent: QWidget, text: str = "", alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter):
        super().__init__(text, parent)
        
        self.setAlignment(alignment)
        

class PushButton(QPushButton):
    def __init__(self, parent: QWidget, text: str = ""):
        super().__init__(text, parent)
        
        self.setFixedHeight(30)


class VSeperator(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.VLine)