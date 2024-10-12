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


import getpass
import os
import sqlite3
from gettext import gettext as _
from widgets.other import Label, PushButton
from PySide6.QtCore import QStringListModel, QSortFilterProxyModel
from PySide6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)
    

class SidebarDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}sidebar.db")
        self.cur = self.db.cursor()
        
    def addPage(self, page: str, module: str) -> bool:
        try:
            self.cur.execute(f"insert into pages (page) values ('{module}-{page}')")
            self.db.commit()

        except sqlite3.IntegrityError:
            pass
        
        self.cur.execute(f"select page from pages where page = '{module}-{page}'")
        control = self.cur.fetchone()

        try:
            if control[0] == f"{module}-{page}":            
                return True
            else:
                return False

        except TypeError:
            return False
        
    def checkIfThePageExists(self, name: str) -> bool:
        self.cur.execute(f"select * from pages where page = '{name}'")
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
        
    def checkIfTheTableExists(self) -> bool:
        try:
            self.cur.execute("select * from pages")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            page TEXT NOT NULL PRIMARY KEY
        );""")
        self.db.commit()
        
        return self.checkIfTheTableExists()
    
    def deletePage(self, page: str, module: str) -> bool:
        call = self.checkIfThePageExists(f"{module}-{page}")
        
        if call:
            self.cur.execute(f"delete from pages where page = '{module}-{page}'")
            self.db.commit()
            
            call = self.checkIfThePageExists(f"{module}-{page}")
            
            if call:
                return False
            else:
                return True
        
        else:
            return True
        
    def getNames(self) -> list:
        self.cur.execute("select * from pages")
        return self.cur.fetchall()
        
    def recreateTable(self) -> bool:
        self.cur.execute(f"DROP TABLE IF EXISTS pages")
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            return False
        else:
            return self.createTable()


sidebardb = SidebarDB()

create_table = sidebardb.createTable()
if not create_table:
    print("[2] Failed to create table")
    sys.exit(2)


class SidebarWidget(QWidget):
    def __init__(self, parent: QMainWindow, notes: QTabWidget, todos: QTabWidget, diaries: QTabWidget):
        super().__init__(parent)
        
        self.parent_ = parent
        self.notes = notes
        self.todos = todos
        self.diaries = diaries
        
        self.layout_ = QGridLayout(self)
        
        self.entry = QLineEdit(self)
        self.entry.setClearButtonEnabled(True)
        self.entry.setPlaceholderText(_("Search in lists"))
        self.entry.textChanged.connect(self.setFilter)
        
        self.model1 = QStringListModel(self)

        self.proxy1 = QSortFilterProxyModel(self)
        self.proxy1.setSourceModel(self.model1)
        
        self.label1 = Label(self, _("Currently Open Pages"))
        
        self.listview1 = QListView(self)
        self.listview1.setStatusTip(_("Double-click to going to selected page."))
        self.listview1.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listview1.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listview1.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.listview1.setModel(self.proxy1)
        self.listview1.doubleClicked.connect(
            lambda: self.goToPage(self.proxy1.itemData(self.listview1.currentIndex())))
        
        self.model2 = QStringListModel(self)

        self.proxy2 = QSortFilterProxyModel(self)
        self.proxy2.setSourceModel(self.model2)
        
        self.label2 = Label(self, _("Last Opened Pages"))
        
        self.listview2 = QListView(self)
        self.listview2.setStatusTip(_("Double-click to going to selected page."))
        self.listview2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listview2.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listview2.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.listview2.setModel(self.proxy2)
        self.listview2.doubleClicked.connect(
            lambda: self.goToPage(self.proxy2.itemData(self.listview2.currentIndex())))
        
        self.label_2nd = Label(self, _('Only for 2nd list:'))
        
        self.buttons = QWidget(self)
        self.buttons_layout = QHBoxLayout(self.buttons)
        
        self.delete_button = PushButton(self.buttons, _("Delete"))
        self.delete_button.clicked.connect(
            lambda: self.deletePage(self.proxy2.itemData(self.listview2.currentIndex())))
        
        self.clear_button = PushButton(self.buttons, _("Clear"))
        self.clear_button.clicked.connect(self.clearList)
        
        self.buttons.setLayout(self.buttons_layout)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.clear_button)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.entry)
        self.layout_.addWidget(self.label1)
        self.layout_.addWidget(self.listview1)
        self.layout_.addWidget(self.label2)
        self.layout_.addWidget(self.listview2)
        self.layout_.addWidget(self.label_2nd)
        self.layout_.addWidget(self.buttons)
        
        self.insertPages()
        
    def addPage(self, text: str, target: QTabWidget) -> None:
        stringlist = self.model1.stringList()

        if target == self.notes:
            call = sidebardb.addPage(text, "notes")

            stringlist.append(_("Note: {name}").format(name = text))
            
        elif target == self.todos:
            call = sidebardb.addPage(text, "todos")
            
            stringlist.append(_("Todo list: {todolist}").format(todolist = text))
            
        elif target == self.diaries:
            call = sidebardb.addPage(text, "diaries")
            
            stringlist.append(_("Diary: {date}").format(date = text))

        if not call:
            QMessageBox.critical(self, _("Error"), _("Failed to add {page} to 2nd list.").format(page = text))
        
        self.model1.setStringList(stringlist)
        
        self.insertPages()
        
    def clearList(self) -> None:
        call = sidebardb.recreateTable()
        
        self.insertPages()
        
        if call:
            QMessageBox.information(self, _("Successful"), _("2nd list cleaned."))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to clear 2nd list."))
            
    def deletePage(self, key: list) -> None:
        try:
            text = key[0]
            
        except KeyError:
            QMessageBox.critical(self, _("Error"), _("The selection is invalid."))
            
            return
        
        if text.startswith(_("Note: ")):
            length = len(_("Note: "))
            module = "notes"
                
        elif text.startswith(_("Todo list: ")):
            length = len(_("Todo list: "))
            module = "todos"

        elif text.startswith(_("Diary: ")):
            length = len(_("Diary: "))
            module = "diaries"
        
        call = sidebardb.deletePage(text[length:], module)
        
        self.insertPages()
        
        if call:
            QMessageBox.information(self, _("Successful"), _("{page} deleted from 2nd list.").format(page = text[length:]))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {page} from 2nd list.").format(page = text[length:]))

    def goToPage(self, key: list) -> None:
        try:
            text = key[0]
            
        except KeyError:
            QMessageBox.critical(self, _("Error"), _("The selection is invalid."))
            
            return
        
        if text.startswith(_("Note: ")):
            length = len(_("Note: "))
            
            try:
                notebook, name = str(text[length:]).split(" @ ")
                self.notes.treeview.openNote(notebook, name)
            
            except ValueError:
                QMessageBox.critical(self, _("Error"), _("Failed to open note via {text} text.").format(text = text[length:]))
                
        elif text.startswith(_("Todo list: ")):
            length = len(_("Todo list: "))
            
            self.todos.treeview.openTodolistOrSetStatus(text[length:], "")

        elif text.startswith(_("Diary: ")):
            length = len(_("Diary: "))
            
            self.diaries.calendar.openCreate(text[length:])
        
    def insertPages(self) -> None:
        call = sidebardb.getNames()
        pages = []

        for page in call:
            page = page[0]
            
            if str(page).startswith("notes-"):
                pages.append(_("Note: {page}").format(page = page[6:]))
            if str(page).startswith("todos-"):
                pages.append(_("Todo list: {page}").format(page = page[6:]))
            if str(page).startswith("diaries-"):
                pages.append(_("Diary: {page}").format(page = page[8:]))
            
        self.model2.setStringList(pages)
        
    def removePage(self, text: str, target: QTabWidget) -> None:
        stringlist = self.model1.stringList()

        if target == self.notes:
            stringlist.remove(_("Note: {name}").format(name = text))
            
        elif target == self.todos:
            stringlist.remove(_("Todo list: {todolist}").format(todolist = text))
            
        elif target == self.diaries:
            stringlist.remove(_("Diary: {date}").format(date = text))
        
        self.model1.setStringList(stringlist)
        
        self.insertPages()
    
    def setFilter(self, text: str) -> None:
        self.proxy1.beginResetModel()
        self.proxy1.setFilterFixedString(text)
        self.proxy2.beginResetModel()
        self.proxy2.setFilterFixedString(text)
        self.proxy1.endResetModel()  
        self.proxy2.endResetModel()