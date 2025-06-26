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


import datetime
from PySide6.QtCore import QDate, QRect, Qt, Slot
from PySide6.QtGui import QPainter, QAction, QIcon
from PySide6.QtWidgets import *


class Action(QAction):
    def __init__(self, parent: QWidget, clicked: object, text: str = "", icon: QIcon | None = None) -> None:
        super().__init__(text, parent)
        
        self.triggered.connect(clicked)
        
        if icon is not None:
            self.setIcon(icon)
            
            
class CalendarWidget(QCalendarWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.setMaximumDate(QDate.currentDate())
    
    @Slot(QPainter, QRect, QDate or datetime.date)
    def paintCell(self, painter: QPainter | None, rect: QRect, date: QDate | datetime.date) -> None:
        super().paintCell(painter, rect, date)
        
        if date >= self.maximumDate():
            painter.setOpacity(0)
        
        
class ComboBox(QComboBox):
    def addItems(self, texts: list[str] | tuple[str]) -> None:
        self.clear()
        return super().addItems(texts)


class HSeperator(QFrame):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.HLine)
        
        
class Label(QLabel):
    def __init__(self, parent: QWidget, text: str = "", alignment: Qt.AlignmentFlag | int = Qt.AlignmentFlag.AlignCenter) -> None:
        super().__init__(text, parent)
        
        if type(alignment) == int:
            alignment = Qt.AlignmentFlag(alignment)
        
        self.setAlignment(alignment)
        
        
class LineEdit(QLineEdit):
    def __init__(self, parent: QWidget, text: str | None = None, clearer: bool = True) -> None:
        super().__init__(parent)
        
        if text is not None:
            self.setPlaceholderText(text)
            
        self.setClearButtonEnabled(clearer)
        

class VSeperator(QFrame):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.VLine)
  

class PushButton(QPushButton):
    def __init__(self, parent: QWidget, clicked: object, text: str = "", checkable: bool = False, flat: bool = False, icon: QIcon | None = None, size: int | None = None) -> None:
        super().__init__(text, parent)
        
        self.setCheckable(checkable)
        self.setFlat(flat)
        self.setFixedHeight(size if size is not None else 30)
        self.clicked.connect(clicked)
        
        if icon is not None:
            self.setIcon(icon)
            
        if size is not None:
            self.setFixedWidth(size)
            

class ToolButton(QToolButton):
    def __init__(self, parent: QWidget, clicked: object, text: str = "", checkable: bool = False, icon: QIcon | None = None, size: int | None = None) -> None:
        super().__init__(parent)
        
        self.setText(text)
        self.setCheckable(checkable)
        self.setFixedHeight(size if size is not None else 30)
        self.clicked.connect(clicked)
        
        if icon is not None:
            self.setIcon(icon)
            
        if size is not None:
            self.setFixedWidth(size)