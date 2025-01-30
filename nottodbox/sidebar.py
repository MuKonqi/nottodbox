# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024-2025MuKonqi (Muhammed S.)

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
import sqlite3
from gettext import gettext as _
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import Slot, Qt, QSortFilterProxyModel
from PySide6.QtWidgets import *
from widgets.lists import StandardItem
from widgets.others import HSeperator, Label, PushButton


username = getpass.getuser()
userdata = f"/home/{username}/.config/io.github.mukonqi/nottodbox/"


class SidebarDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}sidebar.db")
        self.cur = self.db.cursor()
        
        self.createTable()
        
    def appendPage(self, module: str, page: str) -> bool:
        try:
            self.cur.execute("insert into __main__ (module, page) values (?, ?)", (module, page))
            self.db.commit()

        except sqlite3.IntegrityError:
            pass
        
        return self.checkIfThePageExists(module, page)
        
    def checkIfThePageExists(self, module: str, page: str) -> bool:
        self.cur.execute("select * from __main__ where module = ? and page = ?", (module, page))
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
        
    def checkIfTheTableExists(self) -> bool:
        try:
            self.cur.execute("select * from __main__")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS __main__ (
                             module TEXT NOT NULL,
                             page TEXT NOT NULL
                             );
                             """)
        self.db.commit()
        
        check = self.checkIfTheTableExists()
        
        if not check:
            print("[2] Failed to create main table for sidebar.py")
            exit(2)
            
        return check
    
    def deletePage(self, module: str, page: str) -> bool:
        call = self.checkIfThePageExists(module, page)
        
        if call:
            self.cur.execute("delete from __main__ where module = ? and page = ?", (module, page))
            self.db.commit()
            
            call = self.checkIfThePageExists(module, page)
            
            if call:
                return False
            else:
                return True
        
        else:
            return True
        
    def getAll(self) -> list:
        self.cur.execute("select module, page from __main__")
        return self.cur.fetchall()
        
    def recreateTable(self) -> bool:
        self.cur.execute("DROP TABLE IF EXISTS __main__")
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            return False
        else:
            return self.createTable()


sidebardb = SidebarDB()


class SidebarWidget(QWidget):
    def __init__(self, parent: QMainWindow, notes: QTabWidget, diaries: QTabWidget):
        super().__init__(parent)
        
        self.parent_ = parent
        self.notes = notes
        self.diaries = diaries
        
        self.layout_ = QGridLayout(self)
        
        self.entry = QLineEdit(self)
        self.entry.setClearButtonEnabled(True)
        self.entry.setPlaceholderText(_("Search..."))
        self.entry.textChanged.connect(self.setFilter)
        
        self.open_pages_label = Label(self, _("Open Pages"))
        self.open_pages = SidebarOpenPages(self)
        
        self.history_label = Label(self, _("History"))
        self.history = SidebarHistory(self)
        
        self.delete_button = PushButton(self, _("Delete"))
        self.delete_button.clicked.connect(
            lambda: self.history.deletePage(self.history.getModule(), self.history.getPage()))
        
        self.clear_button = PushButton(self, _("Clear"))
        self.clear_button.clicked.connect(
            self.history.deleteAll)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.entry)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.open_pages_label)
        self.layout_.addWidget(self.open_pages)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.history_label)
        self.layout_.addWidget(self.history)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(self.clear_button)
        
    @Slot(str)
    def setFilter(self, text: str):
        self.open_pages.setFilter(text)
        self.history.setFilter(text)
        
        
class SidebarTreeView(QTreeView):
    def __init__(self, parent: SidebarWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.counts = {}
        self.pages = []
        
        self.model_ = QStandardItemModel(self)
        self.model_.setHorizontalHeaderLabels([_("Type"), _("Page")])
        
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setRecursiveFilteringEnabled(True)
        self.proxy.setSourceModel(self.model_)
        
        self.setModel(self.proxy)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setStatusTip(_("Double-click to going to selected page."))
        
        self.doubleClicked.connect(lambda: self.doubleClickEvent(self.getModule(), self.getPage()))
        
    def appendPage(self, module: str, page: str) -> None:
        self.counts[(module, page)] = self.model_.rowCount()
        self.pages.append((module, page))
        
        self.model_.appendRow([StandardItem(_("note").title() if module == "notes" else _("diary").title(), [module, page]), 
                               StandardItem(page, [module, page])])
    
    def deletePage(self, module: str, page: str) -> None:
        self.model_.removeRow(self.counts[module, page])
        
        for parent_, child_ in self.counts.keys():
            if self.counts[(parent_, child_)] > self.counts[(module, page)]:
                self.counts[(parent_, child_)] -= 1
                
        del self.counts[(module, page)]
        self.pages.remove((module, page))
        
    @Slot(str, str)
    def doubleClickEvent(self, module: str, page: str) -> None:
        if module == "notes":
            name, notebook = str(page).split(" @ ")
            self.parent_.notes.home.shortcutEvent(name, notebook)
            
        elif module == "diaries":
            self.parent_.diaries.home.shortcutEvent(page)
        
    def getModule(self) -> str:
        if self.currentIndex().isValid():
            return self.currentIndex().data(Qt.ItemDataRole.UserRole)
        
        else:
            return ""
                    
    def getPage(self) -> str:
        if self.currentIndex().isValid():
            return self.currentIndex().data(Qt.ItemDataRole.UserRole + 1)
        
        else:
            return ""
            
    def setFilter(self, text: str) -> None:
        self.proxy.beginResetModel()
        self.proxy.setFilterFixedString(text)
        self.proxy.endResetModel()
        
        
class SidebarOpenPages(SidebarTreeView):
    def appendPage(self, module: str, page: str) -> None:
        super().appendPage(module, page)
        
        self.parent_.history.appendPage(module, page)
        
        call = sidebardb.appendPage(module, page)
        
        if not call:
            QMessageBox.critical(self, _("Error"), _("Failed to add {page} page to history.").format(page = page))
            

class SidebarHistory(SidebarTreeView):
    def __init__(self, parent: SidebarWidget):
        super().__init__(parent)
        
        call = sidebardb.getAll()
        
        for module, page in call:
            self.appendPage(module, page)
            
    def appendPage(self, module: str, page: str):
        if (module, page) not in self.pages:
            super().appendPage(module, page)
            
    @Slot()
    def deleteAll(self) -> None:
        self.counts = {}
        
        self.model_.clear()
        self.model_.setHorizontalHeaderLabels([_("Type"), _("Page")])
        
        call = sidebardb.recreateTable()
            
        if not call:
            QMessageBox.critical(self, _("Error"), _("Failed to clear history."))
            
    @Slot(str, str)
    def deletePage(self, module: str, page: str):
        super().deletePage(module, page)
        
        call = sidebardb.deletePage(module, page)
        
        if not call:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {page} page from history.").format(page = page))