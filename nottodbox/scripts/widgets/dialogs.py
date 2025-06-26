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


from PySide6.QtCore import QModelIndex, QDate, QSettings, Qt, Slot
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import *
from .controls import CalendarWidget, Label, LineEdit, PushButton
from ..consts import APP_DEFAULTS, APP_OPTIONS, APP_SETTINGS, APP_VALUES


class GetColor(QColorDialog):
    def __init__(self, parent: QWidget, show_default: bool, show_global: bool, show_notebook: bool, color: QColor | Qt.GlobalColor, title: str) -> None:
        super().__init__(color, parent)
        
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        
        self.buttonbox = self.findChild(QDialogButtonBox)
        
        if show_default:
            self.follow_default = PushButton(self.buttonbox, lambda: self.done(2), self.tr("Follow default"))
        
            self.buttonbox.addButton(self.follow_default, QDialogButtonBox.ButtonRole.ResetRole)
        
        if show_global:
            self.follow_global = PushButton(self.buttonbox, lambda: self.done(3), self.tr("Follow global"))
            
            self.buttonbox.addButton(self.follow_global, QDialogButtonBox.ButtonRole.ResetRole)
            
        if show_notebook:
            self.follow_notebook = PushButton(self.buttonbox, lambda: self.done(4), self.tr("Follow notebook"))
            
            self.buttonbox.addButton(self.follow_notebook, QDialogButtonBox.ButtonRole.ResetRole)
        
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
    def __init__(self, parent: QWidget, show_default: bool, show_global: bool, show_notebook: bool, color: str = "default") -> None:
        super().__init__(parent)
        
        self.selected = color
        
        self.show_default = show_default
        self.show_global = show_global
        self.show_notebook = show_notebook
        self.color = color
        
        self.selector = PushButton(self, self.selectColor, self.tr("Select color ({})").format(self.tr("default") if self.color == "default" else color))
        
        self.label = Label(self)
        
        self.viewer = QPixmap(self.selector.height(), self.selector.height())

        self.layout_ = QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.addWidget(self.selector)
        self.layout_.addWidget(self.label)
        
        self.setColor(self.selected)
        
    @Slot()
    def selectColor(self) -> None:
        ok, status, color = GetColor(self, self.show_default, self.show_global, self.show_notebook, self.color, self.tr("Select a Color")).getColor()
        
        if ok:
            self.setColor(color.name() if status == "new" else status)
        
    def setColor(self, color: str) -> None:
        self.selected = color
        self.selector.setText(self.tr("Select color ({})").format(color if color != "" else self.tr("default")))
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
        self.resize(690, 460)


class GetName(Dialog):
    def __init__(self, parent: QWidget, window_title: str, creation: bool = False, item: str = None) -> None:
        super().__init__(parent, window_title)
        
        self.creation = creation
        
        if creation:
            self.selector = QWidget(self.input)
            
            self.selector_layout = QHBoxLayout(self.selector)
            self.selector_layout.setContentsMargins(0, 0, 0, 0)
            self.selector_layout.addWidget(Label(self.selector, self.tr("Settings will follow:")))
            
            self.combobox = QComboBox(self.selector)
            self.combobox.addItems([self.tr("Defaults"), self.tr("Globals")])
            if item == "document":
                self.combobox.addItem(self.tr("Notebooks'"))
                
            self.selector_layout.addWidget(self.combobox)

        self.calendar = CalendarWidget(self.input)
        self.calendar.selectionChanged.connect(lambda: self.name.setText(self.calendar.selectedDate().toString("dd/MM/yyyy")))
        
        self.name = LineEdit(self.input, self.tr("Name (required)"))
        self.name.setText(self.calendar.selectedDate().toString("dd/MM/yyyy"))
        
    def get(self) -> tuple[bool, str] | tuple[bool, int, str]:
        if self.creation:
            return self.result() == 1, self.combobox.currentIndex(), self.name.text()
        
        else:
            return self.result() == 1, self.name.text()
    
    def set(self) -> int:
        self.layout_ = QVBoxLayout(self.input)
        if self.creation:
            self.layout_.addWidget(self.selector)
        self.layout_.addWidget(self.calendar)
        self.layout_.addWidget(self.name)
        
        return self.exec()
    
    
class GetDescription(Dialog):
    def __init__(self, parent: QWidget, window_title: str):
        super().__init__(parent, window_title)

        self.description = LineEdit(self.input, self.tr("Description (leave blank to remove)"))
        
    def get(self) -> tuple[bool, str]:        
        return self.result() == 1, self.description.text()
    
    def set(self) -> int:
        self.layout_ = QVBoxLayout(self.input)
        self.layout_.addWidget(self.description)
        
        return self.exec()
    
    
class GetNameAndDescription(GetName, GetDescription):        
    def get(self) -> tuple[bool, str, str] | tuple[bool, int, str, str]:
        if self.creation:
            return self.result() == 1, self.combobox.currentIndex(), self.name.text(), self.description.text()
        
        else:
            return self.result() == 1, self.name.text(), self.description.text()
    
    def set(self) -> int:
        self.layout_ = QVBoxLayout(self.input)
        if self.creation:
            self.layout_.addWidget(self.selector)
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
    def __init__(self, parent: QWidget, db, index: QModelIndex, window_title: str) -> None:
        super().__init__(parent, window_title)
        
        self.parent_ = parent
        
        self.db = db
        
        self.index = index
        
        self.selectors = []
        
        self.layout_ = QVBoxLayout(self.input)
        
        
class ChangeAppearance(Settings):
    def __init__(self, parent: QWidget, db, index: QModelIndex) -> None:
        super().__init__(parent, db, index, self.tr("Change Appearance"))
        
        self.localized_labels = [
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
            
            label = Label(widget, f"{self.localized_labels[i]}:", Qt.AlignmentFlag.AlignRight)
            label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
            
            self.selectors.append(ColorSelector(widget, True, True, index.data(Qt.ItemDataRole.UserRole + 2) == "document", index.data(Qt.ItemDataRole.UserRole + 26 + i)[1] if index.data(Qt.ItemDataRole.UserRole + 26 + i)[0] == "self" else index.data(Qt.ItemDataRole.UserRole + 26 + i)[0]))
            
            layout.addWidget(label)
            layout.addWidget(self.selectors[-1])
            
            self.layout_.addWidget(widget)
            
        self.exec()
                
    def get(self) -> tuple[bool, list[str] | None]:
        if self.result() == 1:
            return True, [selector.selected for selector in self.selectors]
            
        else:
            return False, None
        
        
class ChangeSettings(Settings):
    def __init__(self, parent: QWidget, db, index: QModelIndex) -> None:
        super().__init__(parent, db, index, self.tr("Change Settings"))
        
        self.settings = QSettings("io.github.mukonqi", "nottodbox")
        
        self.options = APP_OPTIONS.copy()
        
        if index.data(Qt.ItemDataRole.UserRole + 2) == "document":
            self.options.append("notebook")
        
        self.localized_labels = [
            self.tr("Completion status*"),
            self.tr("Lock status**"),
            self.tr("Auto-save"),
            self.tr("Format")
            ]
        
        self.localized_options = [
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
            
            self.selectors[-1].addItem(self.tr("Follow default ({})").format(APP_DEFAULTS[i]))
            self.selectors[-1].addItem(self.tr("Follow global ({})").format(self.settings.value(f"globals/{APP_SETTINGS[i]}")))
            
            if index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                self.selectors[-1].insertItem(2 if True else 1, self.tr("Follow notebook ({})").
                                        format(self.db.items[(index.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + i)[1]))
            
            self.selectors[-1].addItems(self.localized_options[i])
            
            label = Label(widget, f"{self.localized_labels[i]}:", Qt.AlignmentFlag.AlignRight)
            label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
            
            layout.addWidget(label)
            layout.addWidget(self.selectors[-1])
            
            self.layout_.addWidget(widget)

            try:
                self.selectors[-1].setCurrentIndex(self.options.index(index.data(Qt.ItemDataRole.UserRole + 20 + i)[0]))
            
            except ValueError:
                self.selectors[-1].setCurrentIndex(len(self.options) + APP_VALUES[i].index(index.data(Qt.ItemDataRole.UserRole + 20 + i)[1]))
                
        self.layout_.addWidget(Label(self.input, self.tr("*Setting this to 'Completed' or 'Uncompleted' converts to a to-do."), Qt.AlignmentFlag.AlignLeft))
        self.layout_.addWidget(Label(self.input, self.tr("**Setting this to 'Yes' converts to a diary."), Qt.AlignmentFlag.AlignLeft))
                    
        self.exec()
                
    def get(self) -> tuple[bool, list[int] | None]:
        if self.result() == 1:
            return True, [selector.currentIndex() for selector in self.selectors]
            
        else:
            return False, None