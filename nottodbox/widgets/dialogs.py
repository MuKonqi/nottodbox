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


import getpass
from gettext import gettext as _
from .other import PushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"


class ColorDialog(QColorDialog):
    def __init__(self, parent: QWidget, show_global: bool, color: QColor | Qt.GlobalColor | int, title: str) -> None:
        super().__init__(color, parent)
        
        self.buttonbox = self.findChild(QDialogButtonBox)
        
        if show_global:
            self.set_to_global = PushButton(self.buttonbox, _("Set to global"))
            self.set_to_global.clicked.connect(lambda: self.done(2))
            
            self.buttonbox.addButton(self.set_to_global, QDialogButtonBox.ButtonRole.ResetRole)
        
        self.set_to_default = PushButton(self.buttonbox, _("Set to default"))
        self.set_to_default.clicked.connect(lambda: self.done(3))
        
        self.buttonbox.addButton(self.set_to_default, QDialogButtonBox.ButtonRole.ResetRole)
        
        self.setWindowTitle(title)
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog)
        self.exec()

    def getColor(self) -> tuple:
        if self.result() == 1:
            return True, "new", self.selectedColor()
        
        elif self.result() == 2:
            return True, "global", None
        
        elif self.result() == 3:
            return True, "default", None
        
        else:
            return False, None, None


class GetTwoDialog(QDialog):
    def __init__(self, parent: QWidget, mode: str, window_title: str, 
                 top_text: str, bottom_text: str, top_extra: int | str, bottom_extra: int | str) -> None:
        super().__init__(parent)
        
        self.mode = mode
        
        self.layout_ = QVBoxLayout(self)
        
        self.inputs = QWidget(self)
        self.form = QFormLayout(self)
        self.inputs.setLayout(self.form)
        
        if self.mode == "text":
            self.top_widget = QLineEdit(self.inputs)
            self.top_widget.setPlaceholderText(top_extra)
            
            self.bottom_widget = QLineEdit(self.inputs)
            self.bottom_widget.setPlaceholderText(bottom_extra)
        
        elif self.mode == "number":
            self.top_widget = QSpinBox(self.inputs)
            self.top_widget.setMinimum(top_extra)
            self.top_widget.setValue(top_extra)
            self.top_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
            self.bottom_widget = QSpinBox(self.inputs)
            self.bottom_widget.setMinimum(bottom_extra)
            self.bottom_widget.setValue(bottom_extra)
            self.bottom_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
        self.form.addRow(top_text, self.top_widget)
        self.form.addRow(bottom_text, self.bottom_widget)
        
        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.rejected.connect(lambda: self.done(0))
        self.buttons.accepted.connect(lambda: self.done(1))
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.inputs)
        self.layout_.addWidget(self.buttons)
        
        self.setWindowTitle(window_title)
        self.exec()
        
    def getItems(self) -> tuple:
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