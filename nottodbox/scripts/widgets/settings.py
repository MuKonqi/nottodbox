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


from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import *
from .controls import Label
from ..consts import APP_DEFAULTS, APP_OPTIONS, APP_VALUES


def changeAppearance(self: QDialog, index: QModelIndex, show_global: bool, color_selector: QWidget) -> None:
    self.localizeds = [
            self.tr("Background color"),
            self.tr("Background color when mouse is over"),
            self.tr("Background color when clicked"),
            self.tr("Foreground color"),
            self.tr("Foreground color when mouse is over"),
            self.tr("Foreground color when clicked"),
            self.tr("Border color"),
            self.tr("Border color when mouse is over"),
            self.tr("Border color when clicked")
            ]
        
    for i in range(9):
        widget = QWidget(self.input)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = Label(widget, f"{self.localizeds[i]}:", Qt.AlignmentFlag.AlignRight)
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
        self.selectors.append(color_selector(widget, True, show_global, index.data(Qt.ItemDataRole.UserRole + 2) == "document", index.data(Qt.ItemDataRole.UserRole + 26 + i)[1] if index.data(Qt.ItemDataRole.UserRole + 26 + i)[0] == "self" else index.data(Qt.ItemDataRole.UserRole + 26 + i)[0], self.tr("Select Color")))
        
        layout.addWidget(label)
        layout.addWidget(self.selectors[-1])
        
        self.layout_.addWidget(widget)
        
        
def changeSettings(self: QDialog, index: QModelIndex, show_global: bool) -> None:
    self.settings = APP_OPTIONS.copy()
    
    if index.data(Qt.ItemDataRole.UserRole + 2) == "document":
        self.settings.append("notebook")
    
    self.localizeds = [
        self.tr("Completion status*"),
        self.tr("Lock status**"),
        self.tr("Auto-save"),
        self.tr("Format")
        ]
    
    self.options = [
        [self.tr("Completed"), self.tr("Uncompleted"), self.tr("None")],
        [self.tr("Yes"), self.tr("None")],
        [self.tr("Enabled"), self.tr("Disabled")],
        ["Markdown", "HTML", self.tr("Plain-text")]
    ]
    
    for i in range(4):
        widget = QWidget(self.input)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.selectors.append(QComboBox(widget))
        
        self.selectors[-1].addItem(self.tr("Follow default ({})").format(APP_DEFAULTS[0]))
        
        if show_global:
            self.selectors[-1].insertItem(1, self.tr("Follow global ({})").format(APP_DEFAULTS[0])) # tmp
        
        if index.data(Qt.ItemDataRole.UserRole + 2) == "document":
            self.selectors[-1].insertItem(2 if show_global else 1, self.tr("Follow notebook ({})").
                                    format(self.db.items[(index.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + i)[1]))
        
        self.selectors[-1].addItems(self.options[i])
        
        label = Label(widget, f"{self.localizeds[i]}:", Qt.AlignmentFlag.AlignRight)
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
        layout.addWidget(label)
        layout.addWidget(self.selectors[-1])
        
        self.layout_.addWidget(widget)

        try:
            self.selectors[-1].setCurrentIndex(self.settings.index(index.data(Qt.ItemDataRole.UserRole + 20 + i)[0]))
        
        except ValueError:
            self.selectors[-1].setCurrentIndex(len(self.settings) + APP_VALUES[i].index(index.data(Qt.ItemDataRole.UserRole + 20 + i)[1]))
            
    self.layout_.addWidget(Label(self.input, self.tr("*Setting this to 'Completed' or 'Uncompleted' converts to a to-do."), Qt.AlignmentFlag.AlignLeft))
    self.layout_.addWidget(Label(self.input, self.tr("**Setting this to 'Yes' converts to a diary."), Qt.AlignmentFlag.AlignLeft))