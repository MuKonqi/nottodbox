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

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import *


class Action(QAction):
    def __init__(self, parent: QWidget, text: str):
        super().__init__(text, parent)


class HSeperator(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.HLine)
        
        
class Label(QLabel):
    def __init__(self, parent: QWidget, text: str):
        super().__init__(text, parent)
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

class PushButton(QPushButton):
    def __init__(self, parent: QWidget, text: str):
        super().__init__(text, parent)


class VSeperator(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.VLine)