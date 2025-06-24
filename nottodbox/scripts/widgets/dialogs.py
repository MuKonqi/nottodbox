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


from PySide6.QtCore import QModelIndex, QDate, Qt, Slot
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import *
from .controls import CalendarWidget, Label, LineEdit, PushButton
from ..consts import APP_DEFAULTS, APP_OPTIONS
from ..databases import MainDB


class GetColor(QColorDialog):
    def __init__(self, parent: QWidget, show_default: bool, show_global: bool, show_notebook: bool, color: QColor | Qt.GlobalColor, title: str) -> None:
        super().__init__(color, parent)
        
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        
        self.buttonbox = self.findChild(QDialogButtonBox)
        
        if show_default:
            self.set_to_default = PushButton(self.buttonbox, lambda: self.done(2), self.tr("Set to default"))
        
            self.buttonbox.addButton(self.set_to_default, QDialogButtonBox.ButtonRole.ResetRole)
        
        if show_global:
            self.set_to_global = PushButton(self.buttonbox, lambda: self.done(3), self.tr("Set to global"))
            
            self.buttonbox.addButton(self.set_to_global, QDialogButtonBox.ButtonRole.ResetRole)
            
        if show_notebook:
            self.set_to_notebook = PushButton(self.buttonbox, lambda: self.done(4), self.tr("Set to notebook"))
            
            self.buttonbox.addButton(self.set_to_notebook, QDialogButtonBox.ButtonRole.ResetRole)
        
        self.setWindowTitle(title)
        self.exec()

    def getColor(self) -> tuple[bool, str | None, QColor | None]:
        if self.result() == 1:
            return True, "new", self.selectedColor()
        
        elif self.result() == 2:
            return True, "default", None
        
        elif self.result() == 3:
            return True, "global", None
        
        elif self.result() == 4:
            return True, "notebook", None
        
        else:
            return False, None, None
        
    
class ColorSelector(QWidget):
    def __init__(self, parent: QWidget, show_default: bool, show_global: bool, show_notebook: bool, color: QColor | Qt.GlobalColor, title: str) -> None:
        super().__init__(parent)
        
        self.selected = None
        
        self.show_default = show_default
        self.show_global = show_global
        self.show_notebook = show_notebook
        self.color = color
        self.title = title
        
        self.selector = PushButton(self, self.selectColor, self.tr("Select color ({})").format(self.tr("none")))
        
        self.label = Label(self)
        
        self.viewer = QPixmap(self.selector.height(), self.selector.height())

        self.layout_ = QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.addWidget(self.selector)
        self.layout_.addWidget(self.label)
        
    @Slot()
    def selectColor(self) -> None:
        ok, status, qcolor = GetColor(self, self.show_default, self.show_global, self.show_notebook, self.color, self.title).getColor()
        
        if ok:
            if status == "new":
                self.selected = qcolor.name()
                
            else:
                self.selected = status
                
            self.previewColor(self.selected)
        
    def previewColor(self, color: str) -> None:
        self.selector.setText(self.tr("Select color ({})").format(color if color != "" else self.tr("none")))
        self.viewer.fill(color if color != "" and QColor(color).isValid() else Qt.GlobalColor.transparent)
        self.label.setPixmap(self.viewer)
        

class Dialog(QDialog):
    def __init__(self, parent: QWidget, window_title: str) -> None:
        super().__init__(parent)
        
        self.scroll_area = QScrollArea(self, widgetResizable=True)
        
        self.input = QWidget(self.scroll_area)
        
        self.scroll_area.setWidget(self.input)
        
        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.rejected.connect(lambda: self.done(0))
        self.buttons.accepted.connect(lambda: self.done(1))
        
        self.base_layout = QVBoxLayout(self)
        self.base_layout.addWidget(self.scroll_area)
        self.base_layout.addWidget(self.buttons)
        
        self.setWindowTitle(window_title)
        self.resize(500, 350)


class GetName(Dialog):
    def __init__(self, parent: QWidget, window_title: str):
        super().__init__(parent, window_title)

        self.name = QLineEdit(self.input)
        self.name.setPlaceholderText(self.tr("Name (required)"))
        
        self.calendar = CalendarWidget(self)
        self.calendar.selectionChanged.connect(lambda: self.name.setText(self.calendar.selectedDate().toString("dd/MM/yyyy")))
        
    def get(self) -> tuple[bool, str]:
        return self.result() == 1, self.name.text()
    
    def set(self) -> int:
        self.layout_ = QVBoxLayout(self.input)
        self.layout_.addWidget(self.calendar)
        self.layout_.addWidget(self.name)
        
        return self.exec()
    
    
class GetDescription(Dialog):
    def __init__(self, parent: QWidget, window_title: str):
        super().__init__(parent, window_title)

        self.description = QLineEdit(self.input)
        self.description.setPlaceholderText(self.tr("Description (leave blank to remove)"))
        
    def get(self) -> tuple[bool, str]:
        return self.result() == 1, self.description.text()
    
    def set(self) -> int:
        self.layout_ = QVBoxLayout(self.input)
        self.layout_.addWidget(self.description)
        
        return self.exec()
    
    
class GetNameAndDescription(GetName, GetDescription):        
    def get(self) -> tuple[bool, str, str]:
        return self.result() == 1, self.name.text(), self.description.text()
    
    def set(self) -> int:
        self.layout_ = QVBoxLayout(self.input)
        self.layout_.addWidget(self.calendar)
        self.layout_.addWidget(self.name)
        self.layout_.addWidget(self.description)
        
        return self.exec()

        
class GetDate(Dialog):
    def __init__(self, parent: QWidget, title: str, label: str, name: str) -> None:
        super().__init__(parent, title)
        
        self.calendar = QCalendarWidget(self.input)
        self.calendar.setMaximumDate(QDate.currentDate())
        self.calendar.setSelectedDate(QDate.fromString(name, "dd/MM/yyyy"))
        
        self.layout_ = QVBoxLayout(self.input)
        self.layout_.addWidget(Label(self.input, label))
        self.layout_.addWidget(self.calendar)
        
        self.exec()

    def getResult(self) -> tuple[str, bool]:
        if self.result() == 1:
            return QDate.toString(self.calendar.selectedDate(), "dd/MM/yyyy"), True
        
        else:
            return "", False


class GetTwoNumber(Dialog):
    def __init__(self, parent: QWidget, window_title: str, mode: str, 
                 top_text: str, bottom_text: str, top_extra: int | str, bottom_extra: int | str) -> None:
        super().__init__(parent, window_title)
        
        self.mode = mode
        
        if self.mode == "text":
            self.top_widget = LineEdit(self.input, top_extra)
            
            self.bottom_widget = LineEdit(self.input, bottom_extra)
        
        elif self.mode == "number":
            self.top_widget = QSpinBox(self.input)
            self.top_widget.setMinimum(top_extra)
            self.top_widget.setValue(top_extra)
            self.top_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
            self.bottom_widget = QSpinBox(self.input)
            self.bottom_widget.setMinimum(bottom_extra)
            self.bottom_widget.setValue(bottom_extra)
            self.bottom_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
        self.layout_ = QFormLayout(self.input)
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
        
        
class Settings(Dialog):
    def __init__(self, parent: QWidget, db: MainDB, index: QModelIndex, window_title: str) -> None:
        super().__init__(parent, window_title)
        
        self.parent_ = parent
        
        self.db = db
        
        self.index = index
        
        self.layout_ = QFormLayout(self.input)
        self.layout_.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        
class ChangeAppearance(Settings):
    def __init__(self, parent: QWidget, db: MainDB, index: QModelIndex) -> None:
        super().__init__(parent, db, index, self.tr("Change Appearance"))
        
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
        
        self.buttons = []
        
        for i in range(9):
            self.buttons.append(ColorSelector(self.input, True, True, index.data(Qt.ItemDataRole.UserRole + 2) == "document", QColor("#376296"), self.tr("Select Color")))
            self.layout_.addRow(f"{self.localizeds[i]}:", self.buttons[-1])
            
        self.exec()
                
    def get(self):
        return self.result()
        
        
class ChangeSettings(Settings):
    def __init__(self, parent: QWidget, db: MainDB, index: QModelIndex) -> None:
        super().__init__(parent, db, index, self.tr("Change Settings"))
        
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
            [self.tr("Completed"), self.tr("Uncompleted")],
            [self.tr("Yes"), self.tr("None")],
            [self.tr("Enabled"), self.tr("Disabled")],
            ["Markdown", "HTML", self.tr("Plain-text")]
        ]
        
        self.values = [
            ["completed", "uncompleted"],
            ["yes", None],
            ["enabled", "disabled"],
            ["markdown", "html", "plain-text"]
        ]
        
        for i in range(4):
            combobox = QComboBox(self.input)
            combobox.addItems([
                self.tr("Follow default ({})").format(APP_DEFAULTS[0]),
                self.tr("Follow global ({})").format(APP_DEFAULTS[0]) # tmp
            ])
            
            if index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                combobox.insertItem(2, self.tr("Follow notebook ({})").
                                      format(self.db.items[(index.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + i)[1]))
                
            combobox.addItems(self.options[i])
            
            self.layout_.addRow(Label(self.input, f"{self.localizeds[i]}:", Qt.AlignmentFlag.AlignRight), combobox)
    
            try:
                combobox.setCurrentIndex(self.settings.index(index.data(Qt.ItemDataRole.UserRole + 20 + i)[0]))
            
            except ValueError:
                combobox.setCurrentIndex(len(self.settings) + self.values[i].index(index.data(Qt.ItemDataRole.UserRole + 20 + i)[1]))
                
        self.layout_.addRow(Label(self.input, self.tr("*Setting this to 'Completed' or 'Uncompleted' converts to a to-do."), Qt.AlignmentFlag.AlignLeft))
        self.layout_.addRow(Label(self.input, self.tr("**Setting this to 'Yes' converts to a diary."), Qt.AlignmentFlag.AlignLeft))
                
        self.exec()
                
    def get(self):
        return self.result()