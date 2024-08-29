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


from gettext import gettext as _
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


class ColorDialog(QColorDialog):
    def __init__(self, color: QColor | Qt.GlobalColor | int, parent: QWidget | None, title: str) -> None:
        super().__init__(color, parent)
        self.setWindowTitle(title)
        
        self.buttonbox = self.findChild(QDialogButtonBox)
        
        self.set_to_default = QPushButton(self.buttonbox, text=_("Set to default"))
        self.set_to_default.clicked.connect(lambda: self.done(0))
        
        self.buttonbox.addButton(self.set_to_default, QDialogButtonBox.ButtonRole.DestructiveRole)
        
        self.exec()

    def getColor(self) -> QColor:
        if self.result() == 1:
            return self.selectedColor()
        else:
            return QColor()


class GetTwoDialog(QDialog):
    def __init__(self, parent: QWidget, mode: str, window_title: str, 
                 top_text: str, bottom_text: str, top_extra: int | str, bottom_extra: int | str) -> None:
        super().__init__(parent)
        
        self.mode = mode
        
        self.inputs = QWidget(self)
        self.inputs.setLayout(QFormLayout(self.inputs))
        
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
            
        self.inputs.layout().addRow(top_text, self.top_widget)
        self.inputs.layout().addRow(bottom_text, self.bottom_widget)
        
        self.buttons = QWidget(self)
        self.buttons.setLayout(QHBoxLayout(self))
        
        self.cancel_button = QPushButton(self, text=_("Cancel"))
        self.cancel_button.clicked.connect(lambda: self.done(0))
            
        self.ok_button = QPushButton(self, text=_("OK"))
        self.ok_button.clicked.connect(lambda: self.done(1))
        
        self.buttons.layout().addStretch()
        self.buttons.layout().addWidget(self.cancel_button)
        self.buttons.layout().addWidget(self.ok_button)
        
        self.setWindowTitle(window_title)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.inputs)
        self.layout().addWidget(self.buttons)
        self.exec()
        
    def getItems(self) -> tuple:
        if self.result() == 1:
            if self.mode == "text":
                top_value = self.top_widget.text()
                bottom_value = self.bottom_widget.text()
                    
            elif self.mode == "number":
                top_value = self.top_widget.value()
                bottom_value = self.top_widget.value()
                
            return top_value, bottom_value

        else:
            return None, None