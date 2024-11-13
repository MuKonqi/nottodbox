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


from gettext import gettext as _
from PySide6.QtCore import Slot, Qt, QSortFilterProxyModel, QItemSelectionModel
from PySide6.QtGui import QStandardItemModel, QStandardItem, QMouseEvent, QColor
from PySide6.QtWidgets import *


class StandardItem(QStandardItem):
    def __init__(self, text: str, datas: str | list) -> None:
        super().__init__(text)
        
        if type(datas) == str:
            self.setData(datas, Qt.ItemDataRole.UserRole)
        
        elif type(datas) == list:
            count = -1
            
            for data in datas:
                count += 1
                
                self.setData(data, Qt.ItemDataRole.UserRole + count)
        
    def setText(self, text: str, datas: str | list | None = None):
        super().setText(text)
        
        if type(datas) == str:
            self.setData(datas, Qt.ItemDataRole.UserRole)
            
        elif type(datas) == list:
            count = -1
            
            for data in datas:
                count += 1
                
                self.setData(data, Qt.ItemDataRole.UserRole + count)
        
        elif datas == None:
            if text.startswith("[+] "):
                self.setData(text.removeprefix("[+] "), Qt.ItemDataRole.UserRole)
            elif text.startswith("[-] "):
                self.setData(text.removeprefix("[-] "), Qt.ItemDataRole.UserRole)
            else:
                self.setData(text, Qt.ItemDataRole.UserRole)


class TreeView(QTreeView):
    def __init__(self, parent: QWidget, module: str, caller: str = "own") -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.caller = caller
        
        self.model_ = QStandardItemModel(self)
        self.db = None
        self.parent_counts = {}
        self.parent_items = {}
        self.child_counts = {}
        self.child_items = {}
        self.setting_background = ""
        self.setting_foreground = ""

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setRecursiveFilteringEnabled(True)
        self.proxy.setSourceModel(self.model_)
        
        self.setModel(self.proxy)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        if self.caller == "own":
            self.selectionModel().currentRowChanged.connect(
                lambda: self.parent_.insertInformations(self.getParentText(), self.getChildText()))
        
        self.doubleClicked.connect(lambda: self.doubleClickEvent(self.getParentText(), self.getChildText()))

    def appendAll(self) -> None:
        names = self.db.getNotebookNames() if self.module == "notes" else self.db.getTodolistNames()
        
        if self.caller == "own":
            model_count = -1
            
            for name in names:
                model_count += 1
                
                self.appendParent(name[0])
            
    def appendChild(self, parent: str, name: str) -> None:
        self.child_counts[(parent, name)] = self.parent_items[parent][0].rowCount()
        
        if self.module == "notes":
            creation, modification, background, foreground = self.db.getNote(parent, name)
            
            self.child_items[(parent, name)] = [StandardItem(name, name), 
                                                StandardItem(creation, name), 
                                                StandardItem(modification, name)]
            
        elif self.module == "todos":
            status, creation, completion, background, foreground = self.db.getTodo(parent, name)
            
            if status == "completed":
                name_column = StandardItem(f"[+] {name}", name)
            elif status == "uncompleted":
                name_column = StandardItem(f"[-] {name}", name)
            
            if completion == "" or completion == None:
                completion_column = StandardItem(_("Not completed yet"), name)
            else:
                completion_column = StandardItem(completion, name)
                
            self.child_items[(parent, name)] = [name_column, 
                                                StandardItem(creation, name), 
                                                completion_column]
        
        for item in self.child_items[(parent, name)]:
            if background == "global" and self.setting_background != "default":
                item.setBackground(QColor(self.setting_background))
            elif background != "global" and background != "default":
                item.setBackground(QColor(background))
            
            if foreground == "global" and self.setting_foreground != "default":
                item.setForeground(QColor(self.setting_foreground))
            elif foreground != "global" and foreground != "default":
                item.setForeground(QColor(foreground))
    
        self.parent_items[parent][0].appendRow(self.child_items[(parent, name)])
            
    def appendParent(self, parent: str) -> None:
        creation, modification, background, foreground, names = self.db.getNotebook(parent) if self.module == "notes" else self.db.getTodolist(parent)
        
        model_count = self.model_.rowCount()
        
        self.parent_counts[parent] = model_count
        self.parent_items[parent] = [StandardItem(parent, parent),
                                     StandardItem(creation, parent),
                                     StandardItem(modification, parent)]
        
        for item in self.parent_items[parent]:
            if background == "global" and self.setting_background != "default":
                item.setBackground(QColor(self.setting_background))
            elif background != "global" and background != "default":
                item.setBackground(QColor(background))
            
            if foreground == "global" and self.setting_foreground != "default":
                item.setForeground(QColor(self.setting_foreground))
            elif foreground != "global" and foreground != "default":
                item.setForeground(QColor(foreground))
        
        for name in names:
            self.appendChild(parent, name[0])
            
        self.model_.appendRow(self.parent_items[parent])
            
    def deleteAll(self) -> None:
        self.parent_counts.clear()
        self.parent_counts.clear()
        self.child_counts.clear()
        self.model_.clear()
        
    def deleteChild(self, parent: str, name: str) -> None:
        self.parent_items[parent][0].removeRow(self.child_counts[(parent, name)])
        
        for key in self.child_counts.keys():
            if self.child_counts[key] > self.child_counts[(parent, name)]:
                self.child_counts[key] -= 1
        
        del self.child_items[(parent, name)]
        del self.child_counts[(parent, name)]
        
    def deleteParent(self, parent: str) -> None:       
        self.model_.removeRow(self.parent_counts[parent])
         
        for key in self.child_items.copy().keys():
            if key[0] == parent:
                del self.child_items[key]
                
        for key in self.child_counts.copy().keys():
            if key[0] == parent:
                del self.child_counts[key]
                
        for key in self.parent_counts.keys():
            if self.parent_counts[key] > self.parent_counts[parent]:
                self.parent_counts[key] -= 1
                
        del self.parent_counts[parent]
        del self.parent_items[parent]
                    
    @Slot(str, str)
    def doubleClickEvent(self, parent: str, child: str) -> None:
        pass
    
    def getChildText(self) -> str:
        if self.currentIndex().isValid() and self.currentIndex().parent().isValid():
            return self.currentIndex().data(Qt.ItemDataRole.UserRole)
        
        else:
            return ""
                    
    def getParentText(self) -> str:
        if self.currentIndex().parent().isValid():
            return self.currentIndex().parent().data(Qt.ItemDataRole.UserRole)
        
        elif self.currentIndex().isValid():
            return self.currentIndex().data(Qt.ItemDataRole.UserRole)
        
        else:
            return ""
                
    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        index = self.indexAt(e.pos())
        
        if index.isValid():
            super().mousePressEvent(e)
            
    @Slot(str)
    def setFilter(self, text: str) -> None:
        self.proxy.beginResetModel()
        self.proxy.setFilterFixedString(text)
        self.proxy.endResetModel()
        
    def setIndex(self, parent: str, child: str) -> None:        
        if parent == "":
            self.selectionModel().clear()
            
        else:
            if parent != "" and child == "":
                item = self.parent_items[parent][0]
                
            elif parent != "" and child != "":
                item = self.child_items[(parent, child)][0]
            
            self.selectionModel().setCurrentIndex(
                self.model().mapFromSource(item.index()),
                QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
            
    def updateChild(self, parent: str, name: str, newname: str) -> None:
        self.child_counts[(parent, newname)] = self.child_counts.pop((parent, name))
        self.child_items[(parent, newname)] = self.child_items.pop((parent, name))
        
        self.child_items[(parent, newname)][0].setText(newname)
        
        for item in self.child_items[(parent, newname)]:
            item.setData(newname, Qt.ItemDataRole.UserRole)
            
        if self.caller == "own":
            self.parent_.insertInformations(parent, newname)
        
    def updateChildBackground(self, parent: str, name: str, color: str) -> None:
        for item in self.child_items[(parent, name)]:
            if color == "global" and self.setting_background != "default":
                item.setBackground(QColor(self.setting_background))    
            elif color != "global" and color != "default":
                item.setBackground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.BackgroundRole)
                
    def updateChildForeground(self, parent: str, name: str, color: str) -> None:
        for item in self.child_items[(parent, name)]:
            if color == "global" and self.setting_foreground != "default":
                item.setForeground(QColor(self.setting_foreground))
            elif color != "global" and color != "default":
                item.setForeground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.ForegroundRole)
                
    def updateParent(self, name: str, newname: str) -> None:
        self.parent_counts[newname] = self.parent_counts.pop(name)
        self.parent_items[newname] = self.parent_items.pop(name)
        
        self.parent_items[newname][0].setText(newname)
        
        for item in self.parent_items[newname]:
            item.setData(newname, Qt.ItemDataRole.UserRole)
            
        for key in self.child_counts.copy().keys():
            if key[0] == name:
                self.child_counts[(newname, key[1])] = self.child_counts.pop((name, key[1]))
                
        for key in self.child_items.copy().keys():
            if key[0] == name:
                self.child_items[(newname, key[1])] = self.child_items.pop((name, key[1]))
            
        if self.caller == "own":
            self.parent_.insertInformations(newname, "")
        
    def updateParentBackground(self, name: str, color: str) -> None:
        for item in self.parent_items[name]:
            if color == "global" and self.setting_background != "default":
                item.setBackground(QColor(self.setting_background))    
            elif color != "global" and color != "default":
                item.setBackground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.BackgroundRole)
                
    def updateParentForeground(self, name: str, color: str) -> None:
        for item in self.parent_items[name]:
            if color == "global" and self.setting_foreground != "default":
                item.setForeground(QColor(self.setting_foreground))
            elif color != "global" and color != "default":
                item.setForeground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.ForegroundRole)