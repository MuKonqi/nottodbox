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
from PyQt6.QtCore import Qt, QStringListModel, QSortFilterProxyModel
from PyQt6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)
    

class SidebarDB:
    """The sidebar database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}sidebar.db")
        self.cur = self.db.cursor()
        
    def addPage(self, page: str, module: str) -> bool:
        """
        Add a opened page.
        
        Args:
            page (str): Page name
            module (str): Module

        Returns:
            bool: True if successful, False if not
        """
        
        try:
            self.cur.execute(f"insert into pages (page, module) values ('{page}', '{module}')")
            self.db.commit()

        except sqlite3.IntegrityError:
            pass
        
        self.cur.execute(f"select page, module from pages where page = '{page}'")
        control = self.cur.fetchone()

        if control[0] == page and control[1] == module:            
            return True
        else:
            return False
        
    def checkIfThePageExists(self, name: str) -> bool:
        """
        Check if the page exists.

        Args:
            name (str): Page name

        Returns:
            bool: True if the page exists, if not False
        """
        
        self.cur.execute(f"select * from pages where page = '{name}'")
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
        
    def checkIfTheTableExists(self) -> bool:
        """
        Check if the table exists.

        Returns:
            bool: True if the table exists, if not False
        """
        
        try:
            self.cur.execute("select * from pages")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
        """
        If the notes table not exists, create it.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        sql = """
        CREATE TABLE IF NOT EXISTS pages (
            page TEXT NOT NULL PRIMARY KEY,
            module TEXT NOT NULL
        );"""
        
        self.cur.execute(sql)
        self.db.commit()
        
        return self.checkIfTheTableExists()
    
    def deletePage(self, page: str) -> bool:
        """Delete a page.

        Args:
            name (str): Page name

        Returns:
            bool: True if successful, False if not
        """
        
        call = self.checkIfThePageExists(page)
        
        if call:
            self.cur.execute(f"delete from pages where page = '{page}'")
            self.db.commit()
            
            call = self.checkIfThePageExists(page)
            
            if call:
                return False
            else:
                return True
        
        else:
            return True
        
    def getNames(self) -> list:
        """Get all pages' names.

        Returns:
            list: List of all pages' names.
        """
        
        self.cur.execute("select * from pages")
        return self.cur.fetchall()
        
    def recreateTable(self) -> bool:
        """Recreates the pages table.

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"DROP TABLE IF EXISTS pages")
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            return False
        else:
            return self.createTable()


sidebardb = SidebarDB()

create_table = sidebardb.createTable()
if create_table:
    table = True
else:
    table = False


class SidebarWidget(QWidget):
    """List for open pages."""
    
    def __init__(self, parent: QMainWindow, notes: QTabWidget, todos: QTabWidget, diaries: QTabWidget):
        """
        Display a list for open pages.

        Args:
            parent (QMainWindow): Parent of this widget (main window)
            notes (QTabWidget): Notes widget of parent
            todos (QTabWidget): Todos widget of parent
            diaries (QTabWidget): Diaries widget of parent
        """
        
        super().__init__(parent)
        
        self.setLayout(QGridLayout(self))
        
        self.parent_ = parent
        self.notes = notes
        self.todos = todos
        self.diaries = diaries
        
        self.entry = QLineEdit(self)
        self.entry.setClearButtonEnabled(True)
        self.entry.setPlaceholderText(_("Search in lists"))
        self.entry.textChanged.connect(self.setFilter)
        
        self.model1 = QStringListModel(self)

        self.proxy1 = QSortFilterProxyModel(self)
        self.proxy1.setSourceModel(self.model1)
        
        self.label1 = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                             text=_("Currently Open Pages"))
        
        self.listview1 = QListView(self)
        self.listview1.setStatusTip(_("Double-click to going to selected page."))
        self.listview1.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listview1.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listview1.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.listview1.setModel(self.proxy1)
        self.listview1.doubleClicked.connect(
            lambda: self.goToPage(self.proxy1.itemData(self.listview1.currentIndex())[0]))
        
        self.model2 = QStringListModel(self)

        self.proxy2 = QSortFilterProxyModel(self)
        self.proxy2.setSourceModel(self.model2)
        
        self.label2 = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                             text=_("Last Opened Pages"))
        
        self.listview2 = QListView(self)
        self.listview2.setStatusTip(_("Double-click to going to selected page."))
        self.listview2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listview2.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listview2.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.listview2.setModel(self.proxy2)
        self.listview2.doubleClicked.connect(
            lambda: self.goToPage(self.proxy2.itemData(self.listview2.currentIndex())[0]))
        
        self.label_2nd = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                                text=_('Only for 2nd list:'))
        
        self.button_delete = QPushButton(self, text=_("Delete"))
        self.button_delete.clicked.connect(lambda: 
            self.deletePage(self.proxy2.itemData(self.listview2.currentIndex())[0]))
        
        self.button_clear = QPushButton(self, text=_("Clear"))
        self.button_clear.clicked.connect(self.clearList)
        
        self.layout().addWidget(self.entry, 0, 0, 1, 2)
        self.layout().addWidget(self.label1, 1, 0, 1, 2)
        self.layout().addWidget(self.listview1, 2, 0, 1, 2)
        self.layout().addWidget(self.label2, 3, 0, 1, 2)
        self.layout().addWidget(self.listview2, 4, 0, 1, 2)
        self.layout().addWidget(self.label_2nd, 5, 0, 1, 2)
        self.layout().addWidget(self.button_delete, 6, 0, 1, 1)
        self.layout().addWidget(self.button_clear, 6, 1, 1, 1)
        
        self.insertPages()
        
    def addPage(self, text: str, target: QTabWidget) -> None:
        """
        Add the open page to list.

        Args:
            text (str): Name of page
            target (QTabWidget): Parent widget of page
        """
        
        stringlist = self.model1.stringList()

        if target == self.notes:
            module = "notes"
            
            stringlist.append(_("Note: {name}").format(name = text))
            
        elif target == self.todos:
            module = "todos"
            
            stringlist.append(_("Todo list: {todolist}").format(todolist = text))
            
        elif target == self.diaries:
            module = "diaries"
            
            stringlist.append(_("Diary: {date}").format(date = text))
            
        if not text.endswith(_(" (Backup)")):
            call = sidebardb.addPage(text, module)

            if not call:
                QMessageBox.critical(self, _("Error"), _("Failed to add {page} to 2nd list.").format(page = text))
        
        self.model1.setStringList(stringlist)
        
        self.insertPages()
        
    def clearList(self) -> None:
        """Clear 2nd list, last opened pages."""
        
        call = sidebardb.recreateTable()
        
        self.insertPages()
        
        if call:
            QMessageBox.information(self, _("Successful"), _("2nd list cleaned."))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to clear 2nd list."))
            
    def deletePage(self, key: str) -> None:
        """Delete a page.

        Args:
            key (str): Name of page
        """
        
        if key.startswith(_("Note: ")):
            length = len(_("Note: "))
                
        elif key.startswith(_("Todo list: ")):
            length = len(_("Todo list: "))

        elif key.startswith(_("Diary: ")):
            length = len(_("Diary: "))
        
        call = sidebardb.deletePage(key[length:])
        
        self.insertPages()
        
        if call:
            QMessageBox.information(self, _("Successful"), _("{page} deleted from 2nd list.").format(page = key[length:]))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {page} from 2nd list.").format(page = key[length:]))

    def goToPage(self, key: str) -> None:
        """
        Go directly to the selected page.

        Args:
            key (str): Type and name of selected page
        """
        
        if key.startswith(_("Note: ")):
            length = len(_("Note: "))
            
            if key.endswith(_(" (Backup)")):
                self.notes.showBackup(key[length:].replace(_(" (Backup)"), ""))

            else:
                self.notes.openCreate(key[length:])
                
        elif key.startswith(_("Todo list: ")):
            length = len(_("Todo list: "))
            
            self.todos.open(key[length:])

        elif key.startswith(_("Diary: ")):
            length = len(_("Diary: "))
            
            if key.endswith(_(" (Backup)")):
                self.diaries.showBackup(key[length:].replace(_(" (Backup)"), ""))

            else:
                self.diaries.openCreate(key[length:])
        
    def insertPages(self) -> None:
        """Insert pages' names."""
        
        call = sidebardb.getNames()
        pages = []

        for page, module in call:
            if module == "notes":
                pages.append(_("Note: {page}").format(page = page))
            if module == "todos":
                pages.append(_("Todo list: {page}").format(page = page))
            if module == "diaries":
                pages.append(_("Diary: {page}").format(page = page))
            
        self.model2.setStringList(pages)
        
    def removePage(self, text: str, target: QTabWidget) -> None:
        """
        Remove the open (after calling this should be closed) page from list.

        Args:
            text (str): Name of page
            target (QTabWidget): Parent widget of page
        """
        
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
        """
        Set filter for all listviews.

        Args:
            text (str): The text
        """
        
        self.proxy1.beginResetModel()
        self.proxy2.beginResetModel()
        self.proxy1.setFilterFixedString(text)
        self.proxy2.setFilterFixedString(text)
        self.proxy1.endResetModel()  
        self.proxy2.endResetModel()