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
from PySide6.QtCore import Slot, Qt, QSortFilterProxyModel, QItemSelectionModel, QSettings
from PySide6.QtGui import QStandardItemModel, QStandardItem, QMouseEvent, QColor
from PySide6.QtWidgets import *
from databases.lists import DBForLists


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
    def __init__(self, parent: QWidget, module: str, db: DBForLists, own: bool = True, model: QStandardItemModel = None) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.db = db
        self.own = own
        
        if model is None:
            self.model_ = QStandardItemModel(self)
            self.setHorizontalLabels()
            
        else:
            self.model_ = model

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setRecursiveFilteringEnabled(True)
        
        if self.module == "notes":
            self.setStatusTip(_("Double-click to opening a note."))
            
        elif self.module == "todos":
            self.setStatusTip(_("Double-click to changing status of a to-do."))
        
        self.setModel(self.proxy)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True if QSettings("io.github.mukonqi", "nottodbox").
                                     value("appearance/alternate-row-colors") == "enabled" else False)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        if self.own:
            self.selectionModel().currentRowChanged.connect(
                lambda: self.parent_.setOptionWidget(self.getChildText(), self.getParentText()))

        self.proxy.setSourceModel(self.model_)
        
        self.doubleClicked.connect(lambda: self.parent_.shortcutEvent(self.getChildText(), self.getParentText()))
        
        self.appendAll()

    def appendAll(self) -> None:
        all = self.db.getAll()
        
        if self.own:
            model_count = -1
            
            for parent in all.keys():
                model_count += 1
                
                self.appendParent(parent)
            
    def appendChild(self, name: str, table: str) -> None:        
        self.parent_.child_counts[(name, table)] = self.parent_.table_items[table][0].rowCount()
        
        if self.module == "notes":
            creation, modification, background, foreground = self.db.getChild(name, table)
            
            self.parent_.child_items[(name, table)] = [StandardItem(name, name), 
                                               StandardItem(creation, name), 
                                               StandardItem(modification, name)]
            
        elif self.module == "todos":
            status, creation, completion, background, foreground = self.db.getChild(name, table)
            
            if status == "completed":
                name_column = StandardItem(f"[+] {name}", name)
            elif status == "uncompleted":
                name_column = StandardItem(f"[-] {name}", name)
            
            if completion == "" or completion == None:
                completion_column = StandardItem(_("Not completed yet"), name)
            else:
                completion_column = StandardItem(completion, name)
                
            self.parent_.child_items[(name, table)] = [name_column, 
                                                StandardItem(creation, name), 
                                                completion_column]
        
        for item in self.parent_.child_items[(name, table)]:
            if background == "global" and self.parent_.background != "default":
                item.setBackground(QColor(self.parent_.background))
            elif background != "global" and background != "default":
                item.setBackground(QColor(background))
            
            if foreground == "global" and self.parent_.foreground != "default":
                item.setForeground(QColor(self.parent_.foreground))
            elif foreground != "global" and foreground != "default":
                item.setForeground(QColor(foreground))
    
        self.parent_.table_items[table][0].appendRow(self.parent_.child_items[(name, table)])
            
    def appendParent(self, name: str) -> None:
        creation, modification, background, foreground, documents = self.db.getParent(name) if self.module == "notes" else self.db.getParent(name)
        
        model_count = self.model_.rowCount()
        
        self.parent_.table_counts[name] = model_count
        self.parent_.table_items[name] = [StandardItem(name, name),
                                   StandardItem(creation, name),
                                   StandardItem(modification, name)]
        
        for item in self.parent_.table_items[name]:
            if background == "global" and self.parent_.background != "default":
                item.setBackground(QColor(self.parent_.background))
            elif background != "global" and background != "default":
                item.setBackground(QColor(background))
            
            if foreground == "global" and self.parent_.foreground != "default":
                item.setForeground(QColor(self.parent_.foreground))
            elif foreground != "global" and foreground != "default":
                item.setForeground(QColor(foreground))
        
        for child in documents:
            self.appendChild(child[0], name)
            
        self.model_.appendRow(self.parent_.table_items[name])
            
    def deleteAll(self) -> None:
        self.parent_.table_counts.clear()
        self.parent_.table_counts.clear()
        self.parent_.child_counts.clear()
        self.model_.clear()
        self.setHorizontalLabels()
        
    def deleteChild(self, name: str, table: str) -> None:
        self.parent_.table_items[table][0].removeRow(self.parent_.child_counts[(name, table)])
        
        for key in self.parent_.child_counts.keys():
            if self.parent_.child_counts[key] > self.parent_.child_counts[(name, table)]:
                self.parent_.child_counts[key] -= 1
        
        del self.parent_.child_items[(name, table)]
        del self.parent_.child_counts[(name, table)]
        
    def deleteParent(self, name: str) -> None:       
        self.model_.removeRow(self.parent_.table_counts[name])
         
        for key in self.parent_.child_items.copy().keys():
            if key[0] == name:
                del self.parent_.child_items[key]
                
        for key in self.parent_.child_counts.copy().keys():
            if key[0] == name:
                del self.parent_.child_counts[key]
                
        for key in self.parent_.table_counts.keys():
            if self.parent_.table_counts[key] > self.parent_.table_counts[name]:
                self.parent_.table_counts[key] -= 1
                
        del self.parent_.table_counts[name]
        del self.parent_.table_items[name]
    
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
        
    def setHorizontalLabels(self) -> None:
        if self.module == "notes":
            self.model_.setHorizontalHeaderLabels(
                [_("Name"), _("Creation"), _("Modification")])
            
        elif self.module == "todos":
            self.model_.setHorizontalHeaderLabels(
                [_("Name"), _("Creation"), "{} / {}".format(_("Modification"), _("Completion"))])
        
    def setIndex(self, child: str, table: str) -> None:        
        if table == "":
            self.selectionModel().clear()
            
        else:
            if table != "" and child == "":
                item = self.parent_.table_items[table][0]
                
            elif table != "" and child != "":
                item = self.parent_.child_items[(child, table)][0]
            
            self.selectionModel().setCurrentIndex(
                self.model().mapFromSource(item.index()),
                QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
        
    def updateBackground(self, value: str, name: str, table: str = "__main__") -> None:
        def startUpgrading(item: StandardItem):
            if value == "global" and self.parent_.background != "default":
                item.setBackground(QColor(self.parent_.background))   
                 
            elif value != "global" and value != "default":
                item.setBackground(QColor(value))
                
            else:
                item.setData(None, Qt.ItemDataRole.BackgroundRole)
        
        if table == "__main__":
            for item in self.parent_.table_items[name]:
                startUpgrading(item)
            
        else:    
            for item in self.parent_.child_items[(name, table)]:
                startUpgrading(item)
                
    def updateForeground(self, value: str, name: str, table: str = "__main__") -> None:
        def startUpgrading(item: StandardItem):
            if value == "global" and self.parent_.foreground != "default":
                item.setForeground(QColor(self.parent_.foreground))
            elif value != "global" and value != "default":
                item.setForeground(QColor(value))
            else:
                item.setData(None, Qt.ItemDataRole.ForegroundRole)
                
        if table == "__main__":
            for item in self.parent_.table_items[name]:
                startUpgrading(item)
            
        else:    
            for item in self.parent_.child_items[(name, table)]:
                startUpgrading(item)
                
    def updateItem(self, newname: str, name: str, table: str = "__main__"):
        if table == "__main__":
            self.parent_.table_counts[newname] = self.parent_.table_counts.pop(name)
            self.parent_.table_items[newname] = self.parent_.table_items.pop(name)
            
            self.parent_.table_items[newname][0].setText(newname)
            
            for item in self.parent_.table_items[newname]:
                item.setData(newname, Qt.ItemDataRole.UserRole)
                
            for key in self.parent_.child_counts.copy().keys():
                if key[0] == name:
                    self.parent_.child_counts[(newname, key[1])] = self.parent_.child_counts.pop((name, key[1]))
                    
            for key in self.parent_.child_items.copy().keys():
                if key[0] == name:
                    self.parent_.child_items[(newname, key[1])] = self.parent_.child_items.pop((name, key[1]))
                
            if self.own:
                self.parent_.setOptionWidget("", newname)
                
        else:
            self.parent_.child_counts[(newname, table)] = self.parent_.child_counts.pop((name, table))
            self.parent_.child_items[(newname, table)] = self.parent_.child_items.pop((name, table))
            
            if self.module == "notes":
                self.parent_.child_items[(newname, table)][0].setText(newname)
                
            elif self.module == "todos":
                status = self.db.getStatus(newname, table)
                
                if status == "completed":
                    self.parent_.child_items[(newname, table)][0].setText(f"[+] {newname}")
                elif status == "uncompleted":
                    self.parent_.child_items[(newname, table)][0].setText(f"[-] {newname}")
            
            for item in self.parent_.child_items[(newname, table)]:
                item.setData(newname, Qt.ItemDataRole.UserRole)
                
            if self.own:
                self.parent_.setOptionWidget(newname, table)