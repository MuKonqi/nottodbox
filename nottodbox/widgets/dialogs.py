# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024-2025 Mukonqi (Muhammed S.)

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


from gettext import gettext as _
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import *
from .others import Label, PushButton


class ColorDialog(QColorDialog):
    def __init__(self, parent: QWidget, show_global: bool, show_default: bool, color: QColor | Qt.GlobalColor, title: str) -> None:
        super().__init__(color, parent)
        
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        
        self.buttonbox = self.findChild(QDialogButtonBox)
        
        if show_global:
            self.set_to_global = PushButton(self.buttonbox, _("Set to global"))
            self.set_to_global.clicked.connect(lambda: self.done(2))
            
            self.buttonbox.addButton(self.set_to_global, QDialogButtonBox.ButtonRole.ResetRole)
        
        self.set_to_default = PushButton(self.buttonbox, _("Set to default"))
        self.set_to_default.clicked.connect(lambda: self.done(3))
        
        self.buttonbox.addButton(self.set_to_default, QDialogButtonBox.ButtonRole.ResetRole)
        
        self.setWindowTitle(title)
        self.exec()

    def getColor(self) -> tuple[bool, str | None, QColor | None]:
        if self.result() == 1:
            return True, "new", self.selectedColor()
        
        elif self.result() == 2:
            return True, "global", None
        
        elif self.result() == 3:
            return True, "default", None
        
        else:
            return False, None, None
        

class GetDialogBase(QDialog):
    def __init__(self, parent: QWidget, window_title: str) -> None:
        super().__init__(parent)
        
        self.layout_base = QVBoxLayout(self)
        
        self.input = QWidget(self)
        
        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.rejected.connect(lambda: self.done(0))
        self.buttons.accepted.connect(lambda: self.done(1))
        
        self.setLayout(self.layout_base)
        self.layout_base.addWidget(self.input)
        self.layout_base.addWidget(self.buttons)
        
        self.setWindowTitle(window_title)     

        
class GetDateDialog(GetDialogBase):
    def __init__(self, parent: QWidget, title: str, label: str, name: str) -> None:
        super().__init__(parent, title)
        
        self.layout_ = QVBoxLayout(self.input)
        self.input.setLayout(self.layout_)
        
        self.calendar = QCalendarWidget(self.input)
        self.calendar.setMaximumDate(QDate.currentDate())
        self.calendar.setSelectedDate(QDate.fromString(name, "dd.MM.yyyy"))
        
        self.layout_.addWidget(Label(self.input, label))
        self.layout_.addWidget(self.calendar)
        
        self.exec()

    def getResult(self) -> tuple[str, bool]:
        if self.result() == 1:
            return QDate.toString(self.calendar.selectedDate(), "dd.MM.yyyy"), True
        
        else:
            return "", False


class GetTwoDialog(GetDialogBase):
    def __init__(self, parent: QWidget, window_title: str, mode: str, 
                 top_text: str, bottom_text: str, top_extra: int | str, bottom_extra: int | str) -> None:
        super().__init__(parent, window_title)
        
        self.mode = mode
        
        self.layout_ = QFormLayout(self.input)
        self.input.setLayout(self.layout_)
        
        if self.mode == "text":
            self.top_widget = QLineEdit(self.input)
            self.top_widget.setClearButtonEnabled(True)
            self.top_widget.setPlaceholderText(top_extra)
            
            self.bottom_widget = QLineEdit(self.input)
            self.bottom_widget.setClearButtonEnabled(True)
            self.bottom_widget.setPlaceholderText(bottom_extra)
        
        elif self.mode == "number":
            self.top_widget = QSpinBox(self.input)
            self.top_widget.setMinimum(top_extra)
            self.top_widget.setValue(top_extra)
            self.top_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
            self.bottom_widget = QSpinBox(self.input)
            self.bottom_widget.setMinimum(bottom_extra)
            self.bottom_widget.setValue(bottom_extra)
            self.bottom_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
        self.layout_.addRow(top_text, self.top_widget)
        self.layout_.addRow(bottom_text, self.bottom_widget)
        
        self.exec()
        
    def getResult(self) -> tuple[bool, str | int | None, str | int | None]:
        if self.result() == 1:
            if self.mode == "text":
                top_value = self.top_widget.text()
                bottom_value = self.bottom_widget.text()
                    
            elif self.mode == "number":
                top_value = self.top_widget.value()
                bottom_value = self.top_widget.value()
                
            return "ok", top_value, bottom_value

        else:
            return "cancel", None, None