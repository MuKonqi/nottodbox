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
from PySide6.QtCore import QEvent, QModelIndex, QPoint, QSortFilterProxyModel, Qt, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import *
from .widgets.controls import Action, CalendarWidget, Label, LineEdit, HSeperator, PushButton
from .widgets.dialogs import ChangeAppearance, ChangeSettings, GetName, GetNameAndDescription, GetDescription
from .widgets.documents import BackupView, NormalView
from .widgets.lists import ButtonDelegateBase, TreeViewBase
from .consts import APP_DEFAULTS, APP_OPTIONS, APP_SETTINGS
from .databases import MainDB


maindb = MainDB()
        
        
class Selector(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
                
        self.options = Options(self)
        
        self.layout_ = QVBoxLayout(self)
        
        self.buttons = QWidget(self)
        
        self.tree_view = TreeView(self)
        
        self.search_entry = LineEdit(self, self.tr("Search"))
        self.search_entry.textChanged.connect(self.tree_view.setFilter)
        
        self.filter_combobox = QComboBox(self)
        self.filter_combobox.addItems([self.tr("By name"), self.tr("By creation date"), self.tr("By modification date"), self.tr("By content / description")])
        self.filter_combobox.currentIndexChanged.connect(self.tree_view.filterChanged)
        
        self.calendar_widget = CalendarWidget(self)
        self.calendar_widget.selectionChanged.connect(self.selectedDateChanged)
        
        self.calendar_checkbox = QCheckBox(self)
        self.calendar_checkbox.setText(self.tr("Calendar"))
        self.calendar_checkbox.setChecked(True)
        try:
            self.calendar_checkbox.checkStateChanged.connect(self.enableCalendar)
        except:
            self.calendar_checkbox.stateChanged.connect(self.enableCalendar)
            
        self.create_first_notebook = CreateFirstNotebook(self)
        
        self.buttons_layout = QHBoxLayout(self.buttons)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QWidget(self)
        self.container_layout = QGridLayout(self.container)
            
        self.pages = QStackedWidget(self)
        self.pages.addWidget(self.create_first_notebook)
        self.pages.addWidget(self.container)
        
        for button in self.tree_view.buttons:
            self.buttons_layout.addWidget(button)
            
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setColumnStretch(1, 2)
        self.container_layout.addWidget(self.calendar_checkbox, 0, 0, 1, 1)
        self.container_layout.addWidget(self.filter_combobox, 0, 1, 1, 1)
        self.container_layout.addWidget(self.search_entry, 1, 0, 1, 2)
        self.container_layout.addWidget(self.tree_view, 2, 0, 1, 2)
        
        self.layout_.addWidget(self.buttons)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.calendar_widget)
        self.layout_.addWidget(self.pages)
        
        self.tree_view.appendAll()
        
        self.setFixedWidth(345)
                
    @Slot(int or Qt.CheckState)
    def enableCalendar(self, signal: int | Qt.CheckState):
        self.calendar_widget.setVisible(False if signal == Qt.CheckState.Unchecked or signal == 0 else True)
        
    def setPage(self) -> None:
        if self.tree_view.model_.rowCount() == 0:
            self.pages.setCurrentIndex(0)
            
        else:
            self.pages.setCurrentIndex(1)
            
    @Slot()
    def selectedDateChanged(self) -> None:
        if self.pages.currentIndex() == 0:
            self.create_first_notebook.name.setText(self.calendar_widget.selectedDate().toString("dd/MM/yyyy"))
            
        elif self.pages.currentIndex() == 1:
            self.search_entry.setText(self.calendar_widget.selectedDate().toString("dd/MM/yyyy"))
            
    def setVisible(self, visible: bool):
        self.parent_.seperator.setVisible(visible)
        return super().setVisible(visible)


class CreateFirstNotebook(QWidget):
    def __init__(self, parent: Selector):
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.label = Label(self, self.tr("Create your first notebook"))
        font = self.label.font()
        font.setBold(True)
        font.setPointSize(16)
        self.label.setFont(font)
        
        self.name = QLineEdit(self)
        self.name.setPlaceholderText(self.tr("Name (required)"))
        
        self.description = QLineEdit(self)
        self.description.setPlaceholderText(self.tr("Description (not required)"))
        
        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(lambda: self.createNotebook(self.name.text(), self.description.text()))
        
        self.layout_.addWidget(self.label)
        self.layout_.addWidget(self.name)
        self.layout_.addWidget(self.description)
        self.layout_.addWidget(self.buttons)
        
    @Slot(str, str)
    def createNotebook(self, name: str, description: str) -> None:
        if name == "":
            QMessageBox.critical(self.parent_, self.tr("Error"), self.tr("A name is required."))
            return
        
        if self.parent_.options.createNotebook(name, description):
            self.name.clear()
            self.parent_.setPage()
            
            
class Options:
    pages = {}
    
    def __init__(self, parent: Selector) -> None:
        self.parent_ = parent
        
    @Slot(QModelIndex)
    def addLock(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if maindb.set("yes", "locked", name, table):
            index.model().setData(index, ["self", "yes"], Qt.ItemDataRole.UserRole + 21)
            
            QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.parent_.tr("Lock added."))

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to add lock."))
        
    @Slot(QModelIndex)
    def changeAppearance(self, index: QModelIndex) -> None:
        name, table = self.get(index)
        
        ok, values = ChangeAppearance(self.parent_, maindb, index).get()
    
    @Slot(QModelIndex)
    def changeSettings(self, index: QModelIndex) -> None:
        name, table = self.get(index)
        
        ok, values = ChangeSettings(self.parent_, maindb, index).get()
    
    @Slot(QModelIndex)
    def clearContent(self, index: QModelIndex) -> None:
        document = index.data(Qt.ItemDataRole.UserRole + 101)
        notebook = index.data(Qt.ItemDataRole.UserRole + 100)
        
        if maindb.clearContent(document, notebook):
            index.model().setData(index, "", Qt.ItemDataRole.UserRole + 104)
            index.model().setData(index, maindb.getBackup(document, notebook), Qt.ItemDataRole.UserRole + 105)
            
            QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.parent_.tr("Content cleared."))
            
        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to clear content."))
            
    @Slot(QModelIndex)
    def close(self, index: QModelIndex) -> None:
        index.model().setData(index, False, Qt.ItemDataRole.UserRole + 1)
        
        try:
            self.parent_.parent_.area.pages.layout_.replaceWidget(index.data(Qt.ItemDataRole.UserRole + 5), index.data(Qt.ItemDataRole.UserRole + 4))
            
            if index.data(Qt.ItemDataRole.UserRole + 5).mode == "normal":
                index.data(Qt.ItemDataRole.UserRole + 5).changeAutosaveConnections("disconnect")
            
            index.data(Qt.ItemDataRole.UserRole + 5).deleteLater()
            index.model().setData(index, None, Qt.ItemDataRole.UserRole + 5)
            
            del self.pages[index.data(Qt.ItemDataRole.UserRole + 4)]
            index.model().setData(index, None, Qt.ItemDataRole.UserRole + 4)
        
        except RuntimeError:
            pass
        
    @Slot(QModelIndex)
    def createDocument(self, index: QModelIndex) -> None:
        dialog = GetName(self.parent_, self.parent_.tr("Create Document"), True, "document")
        dialog.set()
        ok, default, document = dialog.get()
        
        options = APP_OPTIONS.copy()
        options.append("notebook")
        
        default = options[default]

        if ok:
            try:
                diary = bool(datetime.datetime.strptime(document, "%d/%m/%Y"))
                
            except ValueError:
                diary = False
            
            if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                notebook = index.data(Qt.ItemDataRole.UserRole + 101)
                
            elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                notebook = index.data(Qt.ItemDataRole.UserRole + 100)
            
            if document == "":
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                return
            
            if maindb.createDocument(default, "yes" if diary else None, document, notebook):
                self.parent_.tree_view.appendDocument(maindb.getDocument(document, notebook), maindb.items[(notebook, "__main__")], notebook)
                
            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to create document."))
    
    @Slot(str or None, str or None)
    def createNotebook(self, name: str | None = None, description: str | None = None) -> bool | None:
        ok = True
        
        if name is None:
            dialog = GetNameAndDescription(self.parent_, self.parent_.tr("Create Notebook"), True, "notebook")
            dialog.set()
            ok, default, name, description = dialog.get()
            
            default = APP_OPTIONS[default]
            
        else:
            default = "default"
            
        if ok:
            try:
                diary = bool(datetime.datetime.strptime(name, "%d/%m/%Y"))
                
            except ValueError:
                diary = False
            
            if name == "":
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                return
            
            successful = maindb.createNotebook(default, "yes" if diary else None, description, name)
            
            if successful:
                self.parent_.tree_view.appendNotebook(maindb.getNotebook(name))
                
            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to create notebook."))
                
            self.parent_.setPage()
            
            return successful
    
    @Slot(QModelIndex)
    def delete(self, index: QModelIndex) -> None:
        name, table = self.get(index)
        
        if maindb.delete(name, table):
            if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                self.parent_.tree_view.model_.removeRow(index.row())
                
                for name_, table_ in maindb.items.copy().keys():
                    if table_ == name:
                        del maindb.items[(name_, table_)]
            
            elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                maindb.items[(table, "__main__")].removeRow(index.row()) 
                
            del maindb.items[(name, table)]
            
        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to delete."))
                
        self.parent_.setPage()
    
    @Slot(QModelIndex)
    def editDescription(self, index: QModelIndex) -> None:
        name = index.data(Qt.ItemDataRole.UserRole + 101)
        
        dialog = GetDescription(self.parent_, self.parent_.tr("Edit Description"))
        dialog.set()
        ok, description = dialog.get()
        
        if ok:
            if maindb.set(description, "content", name):
                index.model().setData(index, description, Qt.ItemDataRole.UserRole + 104)
                
            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to edit description."))
            
    def get(self, index: QModelIndex) -> tuple[str, str]:
        if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
            return index.data(Qt.ItemDataRole.UserRole + 101), "__main__"
            
        elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
            return index.data(Qt.ItemDataRole.UserRole + 101), index.data(Qt.ItemDataRole.UserRole + 100)
    
    @Slot(QModelIndex)
    def markAsCompleted(self, index: QModelIndex) -> None:
        name, table = self.get(index)
        
        if maindb.set("completed", "completed", name, table):
            index.model().setData(index, ["self", "completed"], Qt.ItemDataRole.UserRole + 20)
            
        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to mark as completed."))
    
    @Slot(QModelIndex)
    def markAsUncompleted(self, index: QModelIndex) -> None:
        name, table = self.get(index)
        
        if maindb.set("uncompleted", "completed", name, table):
            index.model().setData(index, ["self", "uncompleted"], Qt.ItemDataRole.UserRole + 20)
            
        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to mark as uncompleted."))
    
    @Slot(QModelIndex, str)
    def open(self, index: QModelIndex, mode: str, make: bool = False) -> None:
        try:
            self.close(self.pages[self.parent_.parent_.area.pages.focused_on])
        
        except KeyError:
            pass
        
        if make:
            index.model().setData(index, True, Qt.ItemDataRole.UserRole + 1)
        
        self.pages[self.parent_.parent_.area.pages.focused_on] = index
        
        index.model().setData(index, self.parent_.parent_.area.pages.focused_on, Qt.ItemDataRole.UserRole + 4)
        index.model().setData(index, NormalView(self.parent_.parent_.area.pages, maindb, index) if mode == "normal" else BackupView(self.parent_.parent_.area.pages, maindb, index), Qt.ItemDataRole.UserRole + 5)
        
        self.parent_.parent_.area.pages.layout_.replaceWidget(self.parent_.parent_.area.pages.focused_on, index.data(Qt.ItemDataRole.UserRole + 5))
    
    @Slot(QModelIndex)
    def removeLock(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if maindb.set(None, "locked", name, table):
            index.model().setData(index, ["self", None], Qt.ItemDataRole.UserRole + 21)
            
            QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.parent_.tr("Lock removed."))

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to remove lock."))
    
    @Slot(QModelIndex)
    def rename(self, index: QModelIndex) -> None:
        name, table = self.get(index)
        
        dialog = GetName(self.parent_, self.parent_.tr("Rename"))
        dialog.set()
        ok, new_name = dialog.get()
        
        if ok:
            try:
                diary = bool(datetime.datetime.strptime(new_name, "%d/%m/%Y"))
                
            except ValueError:
                diary = False
            
            if new_name == "":
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                return
            
            if maindb.rename("yes" if diary else None, new_name, name, table):
                if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                    for name_, table_ in maindb.items.copy().keys():
                        if table_ == name:
                            maindb.items[(name_, table_)].setData(new_name, Qt.ItemDataRole.UserRole + 100)
                            maindb.items[(name_, new_name)] = maindb.items.pop((name_, table_))
                            
                maindb.items[(new_name, table)] = maindb.items.pop((name, table))
                
                index.model().setData(index, "yes" if diary else None, Qt.ItemDataRole.UserRole + 21)
                index.model().setData(index, new_name, Qt.ItemDataRole.UserRole + 101)
                
            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to rename."))
    
    @Slot(QModelIndex)
    def reset(self, index: QModelIndex) -> None:
        name, table = self.get(index)
        
        if maindb.reset(name):
            maindb.items[(name, table)].removeRows(0, maindb.items[(name, table)].rowCount())
            
            for name_, table_ in maindb.items.copy().keys():
                if table_ == name:
                    del maindb.items[(name_, table_)]
            
        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to reset."))
    
    @Slot(QModelIndex)
    def restoreContent(self, index: QModelIndex) -> None:
        document, notebook = self.get(index)
        
        if maindb.restoreContent(document, notebook):
            index.model().setData(index, maindb.getContent(document, notebook), Qt.ItemDataRole.UserRole + 104)
            index.model().setData(index, maindb.getBackup(document, notebook), Qt.ItemDataRole.UserRole + 105)
            
            QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.parent_.tr("Content restored."))
            
        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to restore content."))
    
    @Slot(QModelIndex)
    def unmark(self, index: QModelIndex) -> None:
        name, table = self.get(index)
        
        if maindb.set(None, "completed", name, table):
            index.model().setData(index, ["self", None], Qt.ItemDataRole.UserRole + 20)
            
        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to unmark."))
    
    
class TreeView(TreeViewBase):
    def __init__(self, parent: Selector):
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.buttons = [
            PushButton(parent.buttons, lambda: self.setType(0), self.tr("Notes"), True, True),
            PushButton(parent.buttons, lambda: self.setType(1), self.tr("To-dos"), True, True),
            PushButton(parent.buttons, lambda: self.setType(2), self.tr("Diaries"), True, True)
            ]
        
        self.types = ["note", "todo", "diary"]
        
        self.model_ = QStandardItemModel(self)
            
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
        self.normal_filterer.setFilterRole(Qt.ItemDataRole.UserRole + 101)
        
        self.delegate = ButtonDelegate(self)
        
        self.setItemDelegate(self.delegate)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setModel(self.normal_filterer)
        self.selectionModel().currentRowChanged.connect(self.rowChanged)
        
        self.delegate.menu_requested.connect(self.openMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        
    def appendAll(self) -> None:            
        items = maindb.getAll()
        
        if items != []:
            self.parent_.pages.setCurrentIndex(1)
        
        for data in items:
            self.appendNotebook(data)
            
    def appendDocument(self, data: list, item: QStandardItem, notebook: str) -> None:
        document = QStandardItem()
        maindb.items[(data[len(data) - 5], notebook)] = document
        
        document.setData(False, Qt.ItemDataRole.UserRole + 1)
        document.setData("document", Qt.ItemDataRole.UserRole + 2)
        document.setData(self.getType(data[1], data[2]), Qt.ItemDataRole.UserRole + 3)
        
        document.setData(notebook, Qt.ItemDataRole.UserRole + 100) 
        for i in range(5):
            document.setData(data[len(data) - 1 - i], Qt.ItemDataRole.UserRole + 105 - i)
            
        for i in range(15):
            document.setData(self.handleSetting(document, i, data[1 + i]), Qt.ItemDataRole.UserRole + 20 + i)
            
        item.appendRow(document)
            
    def appendNotebook(self, data: list) -> None:
        notebook = QStandardItem()
        maindb.items[(data[len(data) - 4], "__main__")] = notebook
        
        notebook.setData(False, Qt.ItemDataRole.UserRole + 1)
        notebook.setData("notebook", Qt.ItemDataRole.UserRole + 2)
        
        for i in range(4):
            notebook.setData(data[len(data) - 1 - i], Qt.ItemDataRole.UserRole + 104 - i)
            
        for i in range(15):
            notebook.setData(self.handleSetting(notebook, i, data[2 + i]), Qt.ItemDataRole.UserRole + 20 + i)
            
        for data_ in data[0]:
            self.appendDocument(data_, notebook, data[len(data) - 4])
        
        self.model_.appendRow(notebook)
        
    def handleSettingViaGlobal(self, setting: str) -> str | None:
        if setting == "default":
            return APP_DEFAULTS[setting]
                
        else:
            return APP_DEFAULTS[setting] # tmp
        
    def handleSettingViaNotebook(self, item: QStandardItem, number: int) -> str | None:
        if maindb.items[(item.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + number)[1] == "default":
            return APP_DEFAULTS[APP_SETTINGS[number]]
            
        elif maindb.items[(item.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + number)[1] == "global":
            return self.handleSettingViaGlobal(number)
                
        else:
            return maindb.items[(item.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + number)[1]
        
    def handleSetting(self, item: QStandardItem, number: int, value: str | None) -> tuple[str, str | None]:
        if value == "default":
            return "default", APP_DEFAULTS[number]
            
        elif value == "global":
            return "global", self.handleSettingViaGlobal(number)
            
        elif value == "notebook":
            return "notebook", self.handleSettingViaNotebook(item, number)
        
        else:
            return "self", value
        
    @Slot(int)
    def filterChanged(self, index: int) -> None:
        self.normal_filterer.setFilterRole(Qt.ItemDataRole.UserRole + 101 + index)
        
    def getType(self, completed: str | None, locked: str | None) -> str:
        if completed is None and locked is None:
            return "note"
        
        elif completed is not None and locked is not None:
            return "todo diary"
        
        elif completed is not None:
            return "todo"
        
        elif locked is not None:
            return "diary"
        
    @Slot(QPoint or QModelIndex)
    def openMenu(self, context_data: QPoint | QModelIndex):
        index = None
        position = None
        
        if isinstance(context_data, QModelIndex):
            index = context_data

            visual_rect = self.visualRect(index)
            global_pos = self.viewport().mapToGlobal(visual_rect.bottomRight())
            
            global_pos.setX(global_pos.x() - 26)
            global_pos.setY(global_pos.y() - 43)

        elif isinstance(context_data, QPoint):
            position = context_data
            index = self.indexAt(position)
            global_pos = self.viewport().mapToGlobal(position)
        
        if not index or not index.isValid():
            return
            
        menu = QMenu()
        menu.addAction(Action(self, lambda: self.parent_.options.createDocument(index), self.tr("Create Document")))
        menu.addAction(Action(self, lambda: self.parent_.options.createNotebook(), self.tr("Create Notebook")))
        
        menu.addSeparator()
        if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
            menu.addAction(Action(self, lambda: self.parent_.options.editDescription(index), self.tr("Edit Description")))
        
        elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
            menu.addAction(Action(self, lambda: self.parent_.options.open(index, "normal", True), self.tr("Open")))
            menu.addAction(Action(self, lambda: self.parent_.options.open(index, "backup", True), self.tr("Show Backup")))
            menu.addAction(Action(self, lambda: self.parent_.options.restoreContent(index), self.tr("Restore Content")))
            menu.addAction(Action(self, lambda: self.parent_.options.clearContent(index), self.tr("Clear Content")))
            
        menu.addSeparator()
        if index.data(Qt.ItemDataRole.UserRole + 20)[1] == "completed":
            menu.addAction(Action(self, lambda: self.parent_.options.markAsUncompleted(index), self.tr("Mark as Uncompleted")))
            menu.addAction(Action(self, lambda: self.parent_.options.unmark(index), self.tr("Unmark")))
        
        elif index.data(Qt.ItemDataRole.UserRole + 20)[1] == "uncompleted":
            menu.addAction(Action(self, lambda: self.parent_.options.markAsCompleted(index), self.tr("Mark as Completed")))
            menu.addAction(Action(self, lambda: self.parent_.options.unmark(index), self.tr("Unmark")))
        
        else:
            menu.addAction(Action(self, lambda: self.parent_.options.markAsCompleted(index), self.tr("Mark as Completed")))
            menu.addAction(Action(self, lambda: self.parent_.options.markAsUncompleted(index), self.tr("Mark as Uncompleted")))
            
        menu.addSeparator()
        if index.data(Qt.ItemDataRole.UserRole + 21)[1] == "yes":
            menu.addAction(Action(self, lambda: self.parent_.options.removeLock(index), self.tr("Remove Lock")))
        else:
            menu.addAction(Action(self, lambda: self.parent_.options.addLock(index), self.tr("Add Lock")))
        
        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.parent_.options.rename(index), self.tr("Rename")))
        menu.addAction(Action(self, lambda: self.parent_.options.delete(index), self.tr("Delete")))
        
        if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
            menu.addAction(Action(self, lambda: self.parent_.options.reset(index), self.tr("Reset")))
            
        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.parent_.options.changeAppearance(index), self.tr("Change Appearance")))
        menu.addAction(Action(self, lambda: self.parent_.options.changeSettings(index), self.tr("Change Settings")))
        
        if index.data(Qt.ItemDataRole.UserRole + 2) == "document" and index.data(Qt.ItemDataRole.UserRole + 4) is not None:
            menu.addSeparator()
            menu.addAction(Action(self, lambda: self.parent_.options.close(index), self.tr("Close")))
                
        menu.exec(global_pos)

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
        
    @Slot(QModelIndex, QModelIndex)
    def rowChanged(self, new: QModelIndex, old: QModelIndex) -> None:
        super().rowChanged(new, old)
        
        if old.isValid() and old.data(Qt.ItemDataRole.UserRole + 2) == "document":
            self.parent_.options.close(old)
        
        
class ButtonDelegate(ButtonDelegateBase):
    def __init__(self, parent: TreeView) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
    
    def editorEvent(self, event: QEvent, model: QStandardItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        button_rect = self.getButtonRect(option)
        
        if index.data(Qt.ItemDataRole.UserRole + 2) == "document" and event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton and not button_rect.contains(event.position().toPoint()):
            self.parent_.parent_.options.open(index, "normal")

        return super().editorEvent(event, model, option, index)