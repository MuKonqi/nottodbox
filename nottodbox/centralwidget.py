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


import datetime
from PySide6.QtCore import QDate, QRect, QSortFilterProxyModel, Qt, Slot
from PySide6.QtGui import QPainter, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import *
from widgets.controls import HSeperator, PushButton, VSeperator
from widgets.lists import TreeViewBase


class CentralWidget(QWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        
        self.layout_ = QHBoxLayout(self)
        
        self.selector = Selector(self)
        
        self.area = Area(self)
        
        self.layout_.addWidget(self.selector)
        self.layout_.addWidget(VSeperator(self))
        self.layout_.addWidget(self.area)
        
        
class Selector(QWidget):
    def __init__(self, parent: CentralWidget) -> None:
        super().__init__(parent)
        
        self.setFixedWidth(345)
        
        self.layout_ = QGridLayout(self)
        
        self.buttons = QWidget(self)
        
        self.buttons_layout = QHBoxLayout(self.buttons)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree_view = TreeView(self)
        
        self.calendar_widget = CalendarWidget(self)
        self.calendar_widget.setMaximumDate(QDate.currentDate())
        
        self.search_entry = QLineEdit(self)
        self.search_entry.setClearButtonEnabled(True)
        self.search_entry.setPlaceholderText(self.tr("Search..."))
        self.search_entry.textChanged.connect(self.tree_view.setFilter)
        
        self.filter_combobox = QComboBox(self)
        self.filter_combobox.addItems([self.tr("By name"), self.tr("By content"), self.tr("By creation date"), self.tr("By modification date")])
        self.filter_combobox.currentIndexChanged.connect(self.tree_view.filterChanged)
        
        self.calender_checkbox = QCheckBox(self)
        self.calender_checkbox.setText(self.tr("Calendar"))
        self.calender_checkbox.setChecked(True)
        try:
            self.calender_checkbox.checkStateChanged.connect(self.enableCalendar)
        except:
            self.calender_checkbox.stateChanged.connect(self.enableCalendar)
        
        for button in self.tree_view.buttons:
            self.buttons_layout.addWidget(button)
        
        self.layout_.setColumnStretch(1, 2)
        self.layout_.addWidget(self.buttons, 0, 0, 1, 2)
        self.layout_.addWidget(HSeperator(self), 1, 0, 1, 2)
        self.layout_.addWidget(self.calendar_widget, 2, 0, 1, 2)
        self.layout_.addWidget(self.calender_checkbox, 3, 0, 1, 1)
        self.layout_.addWidget(self.filter_combobox, 3, 1, 1, 1)
        self.layout_.addWidget(self.search_entry, 4, 0, 1, 2)
        self.layout_.addWidget(self.tree_view, 5, 0, 1, 2)
                
    @Slot(int or Qt.CheckState)
    def enableCalendar(self, signal: int | Qt.CheckState):
        self.calendar_widget.setVisible(False if signal == Qt.CheckState.Unchecked or signal == 0 else True)
  
        
class Area(QWidget):
    def __init__(self, parent: CentralWidget) -> None:
        super().__init__(parent)
        
        self.setContentsMargins(0, 0, 0, 0)
        
        
class TreeView(TreeViewBase):
    def __init__(self, parent: Selector):
        super().__init__(parent)
        
        self.buttons = [
            PushButton(parent.buttons, lambda: self.setType(0), self.tr("Notes"), True, True),
            PushButton(parent.buttons, lambda: self.setType(1), self.tr("To-dos"), True, True),
            PushButton(parent.buttons, lambda: self.setType(2), self.tr("Diaries"), True, True)
            ]
        
        self.types = ["note", "todo", "diary"]
        
        self.model_ = QStandardItemModel(self)
        
        for i in range(2):
            notebook = QStandardItem()
            notebook.setData(False, Qt.ItemDataRole.UserRole + 1)
            notebook.setData("notebook", Qt.ItemDataRole.UserRole + 2)
            notebook.setData(f"{i}. notebook", Qt.ItemDataRole.UserRole + 10)
            notebook.setData(f"Lorem ipsum dolor sit amet, consectetur adipiscing elit. This is a long text.", Qt.ItemDataRole.UserRole + 11)
            notebook.setData("04.12.2008 14:19", Qt.ItemDataRole.UserRole + 12)
            notebook.setData("04.12.2008 14:23", Qt.ItemDataRole.UserRole + 13)
            
            for j in range(3):
                document = QStandardItem()
                document.setData(False, Qt.ItemDataRole.UserRole + 1)
                document.setData("document", Qt.ItemDataRole.UserRole + 2)
                document.setData(self.types[j], Qt.ItemDataRole.UserRole + 3)
                document.setData(self.types[j].title(), Qt.ItemDataRole.UserRole + 10)
                document.setData(f"Lorem ipsum dolor sit amet, consectetur adipiscing elit. This is a long text.", Qt.ItemDataRole.UserRole + 11)
                document.setData("01.01.1970 14:19", Qt.ItemDataRole.UserRole + 12)
                document.setData("01.01.1970 14:23", Qt.ItemDataRole.UserRole + 13)
                notebook.appendRow(document)

            self.model_.appendRow(notebook)
            
        self.model_.setHorizontalHeaderLabels([self.tr("Name")])
        
        self.type_filterer = QSortFilterProxyModel(self)
        self.type_filterer.setSourceModel(self.model_)
        self.type_filterer.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.type_filterer.setRecursiveFilteringEnabled(True)
        self.type_filterer.setFilterRole(Qt.ItemDataRole.UserRole + 3)
        
        self.normal_filterer = QSortFilterProxyModel(self)
        self.normal_filterer.setSourceModel(self.type_filterer)
        self.normal_filterer.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.normal_filterer.setRecursiveFilteringEnabled(True)
        self.normal_filterer.setFilterRole(Qt.ItemDataRole.UserRole + 10)
        
        self.setModel(self.normal_filterer)
        self.selectionModel().currentRowChanged.connect(self.rowChanged)
        
    @Slot(int)
    def filterChanged(self, index: int) -> None:
        self.normal_filterer.setFilterRole(Qt.ItemDataRole.UserRole + 10 + index)
        
    @Slot(str)
    def setFilter(self, text: str) -> None:
        self.normal_filterer.beginResetModel()
        self.normal_filterer.setFilterFixedString(text)
        self.normal_filterer.endResetModel()
        
    @Slot(int)
    def setType(self, index: int) -> None:
        if self.buttons[index].isChecked():
            buttons = self.buttons.copy()
            del buttons[index]
            
            for button in buttons:
                button.setChecked(False)
        
        self.type_filterer.beginResetModel()
        self.type_filterer.setFilterFixedString(self.types[index] if self.buttons[index].isChecked() else "")
        self.type_filterer.endResetModel()
        
        
class CalendarWidget(QCalendarWidget):
    @Slot(QPainter, QRect, QDate or datetime.date)
    def paintCell(self, painter: QPainter | None, rect: QRect, date: QDate | datetime.date) -> None:
        super().paintCell(painter, rect, date)
        
        if date >= self.maximumDate():
            painter.setOpacity(0)