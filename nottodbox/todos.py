#!/usr/bin/env python3

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


if __name__ == "__main__":
    import sys
    from mainwindow import MainWindow
    from PyQt6.QtWidgets import QApplication
    
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.tabview.setCurrentIndex(2)

    sys.exit(application.exec())


import locale
import gettext
import getpass
import os
import sqlite3
import datetime
from sidebar import Sidebar
from PyQt6.QtCore import Qt, QStringListModel, QSortFilterProxyModel, QRegularExpression
from PyQt6.QtWidgets import *


if locale.getlocale()[0].startswith("tr"):
    language = "tr"
    translations = gettext.translation("nottodbox", "po", languages=["tr"], fallback=True)
else:
    language = "en"
    translations = gettext.translation("nottodbox", "po", languages=["en"], fallback=True)
translations.install()

_ = translations.gettext

align_center = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)

todolist_list = {}
todolist_model1 = {}
todolist_model2 = {}
        

def create_db():    
    with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as db_todos:
        cur_todos = db_todos.cursor()
        
        todos_sql1 = """
        CREATE TABLE IF NOT EXISTS todos (
            name TEXT NOT NULL PRIMARY KEY,
            created TEXT NOT NULL
        );"""
        cur_todos.execute(todos_sql1)
        db_todos.commit()
        
        todos_sql2 = """
        CREATE TABLE IF NOT EXISTS main (
            todo TEXT NOT NULL PRIMARY KEY,
            status TEXT NOT NULL,
            started TEXT NOT NULL,
            completed TEXT
        );"""
        cur_todos.execute(todos_sql2)
        db_todos.commit()

create_db()


class TodolistListView(QListView):
    def __init__(self, parent: QTabWidget, todolist: str, caller: str = "todolist"):
        super().__init__(parent)
        
        global todolist_model1, todolist_model2
        
        self.proxy = QSortFilterProxyModel(self)
        
        if caller == "todolist":  
            todolist_model1[todolist] = QStringListModel(self)
            self.proxy.setSourceModel(todolist_model1[todolist])
            
        elif caller == "home":
            todolist_model2[todolist] = QStringListModel(self)
            self.proxy.setSourceModel(todolist_model2[todolist])
        
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip(_("Double-click to marking a todo as completed/uncompleted."))
        self.setModel(self.proxy)
        
        if caller == "todolist":
            self.selectionModel().selectionChanged.connect(
                lambda: Todolist.insert(parent, self.proxy.itemData(self.currentIndex())))
        
        self.doubleClicked.connect(lambda: self.mark(todolist, self.proxy.itemData(self.currentIndex())))
        
        self.refresh(todolist)
        
    def refresh(self, todolist: str):
        global todolist_list
        
        todolist_list[todolist] = []
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_refresh:
            self.cur_refresh = self.db_refresh.cursor()
            self.cur_refresh.execute(f"select * from {todolist}")
            self.fetch_refresh = self.cur_refresh.fetchall()
        
        for i in range(0, len(self.fetch_refresh)):
            if self.fetch_refresh[i][1] == "completed":
                todolist_list[todolist].append(f"[+] {self.fetch_refresh[i][0]}")
                
            elif self.fetch_refresh[i][1] == "uncompleted":
                todolist_list[todolist].append(f"[-] {self.fetch_refresh[i][0]}")
            
        try:
            todolist_model1[todolist].setStringList(todolist_list[todolist])
        except KeyError:
            pass
    
        
        try:
            todolist_model2[todolist].setStringList(todolist_list[todolist])
        except KeyError:
            pass
        
    def mark(self, todolist: str, todo: str):
        if todo[0].startswith("[-]"):
            todo = todo[0].replace("[-] ", "")
        elif todo[0].startswith("[+]"):
            todo = todo[0].replace("[+] ", "")
                
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_mark:
            self.cur_mark = self.db_mark.cursor()
            self.cur_mark.execute(f"select status from {todolist} where todo = '{todo}'")
            self.fetch_comp2 = self.cur_mark.fetchone()[0]
        
        if self.fetch_comp2 == "completed":
            self.uncomp(todolist, todo)  
        elif self.fetch_comp2 == "uncompleted":
            self.comp(todolist, todo, datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            
    def comp(self, todolist: str, todo: str, completed: str):
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_comp1:
            self.cur_comp1 = self.db_comp1.cursor()
            self.cur_comp1.execute(f"update {todolist} set status = 'completed', completed = '{completed}' where todo = '{todo}'")
            self.db_comp1.commit()
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_comp2:
            self.cur_comp2 = self.db_comp2.cursor()
            self.cur_comp2.execute(f"select status from {todolist} where todo = '{todo}'")
            self.fetch_comp2 = self.cur_comp2.fetchone()[0]
        
        self.refresh(todolist)
        
        if self.fetch_comp2 == "completed":
            QMessageBox.information(self, _("Successful"), _("{todo} in {todolist} marked as completed.").format(todo = todo, todolist = todolist))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to mark {todo} in {todolist} as completed.").format(todo = todo, todolist = todolist))
    
    def uncomp(self, todolist: str, todo: str):
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_uncomp1:
            self.cur_uncomp1 = self.db_uncomp1.cursor()
            self.cur_uncomp1.execute(f"update {todolist} set status = 'uncompleted', completed = NULL where todo = '{todo}'")
            self.db_uncomp1.commit()
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_uncomp2:
            self.cur_uncomp2 = self.db_uncomp2.cursor()
            self.cur_uncomp2.execute(f"select status from {todolist} where todo = '{todo}'")
            self.fetch_uncomp2 = self.cur_uncomp2.fetchone()[0]
            
        self.refresh(todolist)
        
        if self.fetch_uncomp2 == "uncompleted":
            QMessageBox.information(self, _("Successful"), _("{todo} in {todolist} marked as uncompleted.").format(todo = todo, todolist = todolist))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to mark {todo} in {todolist} as uncompleted.").format(todo = todo, todolist = todolist))


class Todolist(QWidget):
    def __init__(self, parent: QTabWidget, todolist: str = "main"):
        super().__init__(parent)
        
        self._todolist = todolist
        
        self.setLayout(QGridLayout(self))
        self.setStatusTip(_("Double-click on list to marking a todo as completed/uncompleted."))
        
        self.started = QLabel(self, alignment=align_center, 
                              text=_('Started:'))
        self.completed = QLabel(self, alignment=align_center, 
                                text=_("Completed:"))
        
        self.listview = TodolistListView(self, self._todolist)
        
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText(_('Type a todo'))
        self.entry.setStatusTip("Typing in entry also searches in list.")
        self.entry.textChanged.connect(
            lambda: self.listview.proxy.setFilterRegularExpression(QRegularExpression
                                                          (self.entry.text(), QRegularExpression.PatternOption.CaseInsensitiveOption)))
        
        self.comp_button = QPushButton(self, text=_("Mark as completed"))
        self.comp_button.clicked.connect(lambda: self.comp(self.entry.text(), 
                                                           datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
        self.uncomp_button = QPushButton(self, text=_("Mark as uncompleted"))
        self.uncomp_button.clicked.connect(lambda: self.uncomp(self.entry.text()))
        
        self.add_button = QPushButton(self, text=_("Add"))
        self.add_button.clicked.connect(lambda: self.add(self.entry.text(),
                                                         datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
        self.edit_button = QPushButton(self, text=_("Edit"))
        self.edit_button.clicked.connect(lambda: self.edit(self.entry.text()))
        
        self.delete_button = QPushButton(self, text=_("Delete"))
        self.delete_button.clicked.connect(lambda: self.delete(self.entry.text()))
        
        self.delete_all_button = QPushButton(self, text=_("Delete All"))
        self.delete_all_button.clicked.connect(self.delete_all)
        
        self.layout().addWidget(self.started, 0, 0, 1, 1)
        self.layout().addWidget(self.completed, 0, 1, 1, 1)
        self.layout().addWidget(self.listview, 1, 0, 1, 2)
        self.layout().addWidget(self.entry, 2, 0, 1, 2)
        self.layout().addWidget(self.comp_button, 3, 0, 1, 1)
        self.layout().addWidget(self.uncomp_button, 3, 1, 1, 1)
        self.layout().addWidget(self.add_button, 4, 0, 1, 1)
        self.layout().addWidget(self.edit_button, 4, 1, 1, 1)
        self.layout().addWidget(self.delete_button, 5, 0, 1, 1)
        self.layout().addWidget(self.delete_all_button, 5, 1, 1, 1)
        
    def insert(self, todo: str):
        if todo != {}:
            if Todos.control(self, self._todolist) == False:
                return
            
            if todo[0].startswith("[-]"):
                todo = todo[0].replace("[-] ", "")
            elif todo[0].startswith("[+]"):
                todo = todo[0].replace("[+] ", "")
            
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_insert:
                self.cur_insert = self.db_insert.cursor()
                self.cur_insert.execute(f"select todo, started, completed from {self._todolist} where todo = '{todo}'")
                self.fetch_insert = self.cur_insert.fetchone()
            
            try:
                self.entry.setText(self.fetch_insert[0])
                self.started.setText(f"{_('Started')}: {self.fetch_insert[1]}")
                self.completed.setText(f"{_('Completed')}: {self.fetch_insert[2]}")
            except TypeError:
                self.started.setText(f"{_('Started')}:")
                self.completed.setText(f"{_('Completed')}:")
        
    def control(self, todo: str, mode: str = "normal"):
        if Todos.control(self, self._todolist) == False:
            return
        
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_control:
                self.cur_control = self.db_control.cursor()
                self.cur_control.execute(f"select * from {self._todolist} where todo = '{todo}'")
                self.fetch_control = self.cur_control.fetchone()[0]
            return True
        except TypeError:
            if mode == "normal":
                QMessageBox.critical(self, _('Error'), _('There is no todo in {todolist} list called {todo}.').format(todolist = self._todolist, todo = todo))
            return False
    
    def comp(self, todo: str, completed: str):
        if todo == "" or todo == None:
            QMessageBox.critical(self, _('Error'), _('Todo can not be blank.'))
            return        
        
        if self.control(todo) == False:
            return
        
        if Todos.control(self, self._todolist) == False:
            return
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_comp1:
            self.cur_comp1 = self.db_comp1.cursor()
            self.cur_comp1.execute(f"update {self._todolist} set status = 'completed', completed = '{completed}' where todo = '{todo}'")
            self.db_comp1.commit()
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_comp2:
            self.cur_comp2 = self.db_comp2.cursor()
            self.cur_comp2.execute(f"select status from {self._todolist} where todo = '{todo}'")
            self.fetch_comp2 = self.cur_comp2.fetchone()[0]
        
        TodolistListView.refresh(self.listview, self._todolist)
        
        if self.fetch_comp2 == "completed":
            QMessageBox.information(self, _("Successful"), _("{todo} in {todolist} marked as completed.").format(todo = todo, todolist = self._todolist))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to mark {todo} in {todolist} as completed.").format(todo = todo, todolist = self._todolist))
    
    def uncomp(self, todo: str):
        if todo == "" or todo == None:
            QMessageBox.critical(self, _('Error'), _('Todo can not be blank.'))
            return        
        
        if self.control(todo) == False:
            return
        
        if Todos.control(self, self._todolist) == False:
            return
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_uncomp1:
            self.cur_uncomp1 = self.db_uncomp1.cursor()
            self.cur_uncomp1.execute(f"update {self._todolist} set status = 'uncompleted', completed = NULL where todo = '{todo}'")
            self.db_uncomp1.commit()
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_uncomp2:
            self.cur_uncomp2 = self.db_uncomp2.cursor()
            self.cur_uncomp2.execute(f"select status from {self._todolist} where todo = '{todo}'")
            self.fetch_uncomp2 = self.cur_uncomp2.fetchone()[0]
            
        TodolistListView.refresh(self.listview, self._todolist)
        
        if self.fetch_uncomp2 == "uncompleted":
            QMessageBox.information(self, _("Successful"), _("{todo} in {todolist} marked as uncompleted.").format(todo = todo, todolist = self._todolist))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to mark {todo} in {todolist} as uncompleted.").format(todo = todo, todolist = self._todolist))
    
    def add(self, todo: str, started: str):
        if todo == "" or todo == None:
            QMessageBox.critical(self, _('Error'), _('Todo can not be blank.'))
            return           
        
        if Todos.control(self, self._todolist) == False:
            return
        
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_add1:
                self.sql_add1 = f"""insert into {self._todolist} (todo, status, started) 
                values ('{todo}', 'uncompleted', '{started}')"""
                self.cur_add1 = self.db_add1.cursor()
                self.cur_add1.execute(self.sql_add1)
                self.db_add1.commit()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, _('Error'), _('{todo} todo already added to {todolist}.').format(todo = todo, todolist = self._todolist))
            return
                
        TodolistListView.refresh(self.listview, self._todolist)
    
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_add2:
            self.cur_add2 = self.db_add2.cursor()
            self.cur_add2.execute(f"select todo, status, started from {self._todolist} where todo = '{todo}'")
            self.fetch_add2 = self.cur_add2.fetchone()

        self.if_add = self.fetch_add2[0] == todo and self.fetch_add2[1] == "uncompleted"
        
        if self.if_add == True and self.fetch_add2[2] == started:
            QMessageBox.information(self, _('Successful'), _('{todo} added to {todolist}.').format(todo = todo, todolist = self._todolist))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to add {todo} to {todolist}.').format(todo = todo, todolist = self._todolist))
    
    def edit(self, todo: str):
        if todo == "" or todo == None:
            QMessageBox.critical(self, _('Error'), _('Todo can not be blank.'))
            return        
        
        if self.control(todo) == False:
            return
        
        if Todos.control(self, self._todolist) == False:
            return
        
        self.newtodo, self.topwindow = QInputDialog.getText(self, 
                                                             _("Edit {todo} todo in {todolist}").format(todo = todo, todolist = self._todolist), 
                                                             _("Please enter a todo for {todo} in {todolist} below.").format(todo = todo, todolist = self._todolist))
        
        if self.newtodo != "" and self.newtodo != None and self.topwindow == True:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_edit1:
                self.sql_edit1 = f"update {self._todolist} set todo = '{self.newtodo}' where todo = '{todo}'"
                self.cur_edit1 = self.db_edit1.cursor()
                self.cur_edit1.execute(self.sql_edit1)
                self.db_edit1.commit()
            
            TodolistListView.refresh(self.listview, self._todolist)
            self.entry.setText(self.newtodo)

            try:
                with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_edit2:
                    self.cur_edit2 = self.db_edit2.cursor()
                    self.cur_edit2.execute(f"select * from {self._todolist} where todo = '{self.newtodo}'")
                    self.fetch_edit2 = self.cur_edit2.fetchone()[0]
                
                self.entry.setText(self.newtodo)
                
                QMessageBox.information(self, _('Successful'),
                                        _('{todo} todo in {todolist} edited as {newtodo}.')
                                        .format(todo = todo, todolist = self._todolist, newtodo = self.newtodo))
                
            except TypeError:
                QMessageBox.critical(self, _('Error'), _('Failed to edit {todo} todo in {todolist}.').format(todo = todo, todolist = self._todolist))
                
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to edit {todo} todo in {todolist}.').format(todo = todo, todolist = self._todolist))
    
    def delete(self, todo: str):
        if todo == "" or todo == None:
            QMessageBox.critical(self, _('Error'), _('Todo can not be blank.'))
            return
        
        if self.control(todo) == False:
            return
        
        if Todos.control(self, self._todolist) == False:
            return
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_remove1:
            self.cur_remove1 = self.db_remove1.cursor()
            self.cur_remove1.execute(f"delete from {self._todolist} where todo = '{todo}'")
            self.db_remove1.commit()
            
        TodolistListView.refresh(self.listview, self._todolist)
        self.entry.setText("")
            
        if self.control(todo, "inverted") == False:
            QMessageBox.information(self, _('Successful'), _('{todo} todo in {todolist} deleted.').format(todo = todo, todolist = self._todolist))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete {todo} todo in {todolist}.').format(todo = todo, todolist = self._todolist))
    
    def delete_all(self):
        if Todos.control(self, self._todolist) == False:
            return
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all1:
            self.cur_delete_all1 = self.db_delete_all1.cursor()
            self.cur_delete_all1.execute(f"select todo from {self._todolist}")
            self.fetch_delete_all1 = self.cur_delete_all1.fetchall()
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all2:
            self.cur_delete_all2 = self.db_delete_all2.cursor()
            
            for todolist in self.fetch_delete_all1:
                self.cur_delete_all2.execute(f"delete from '{self._todolist}' where todo = '{todolist[0]}'")
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all3:
            self.cur_delete_all3 = self.db_delete_all3.cursor()
            self.cur_delete_all3.execute(f"select * from {self._todolist}")
            self.fetch_delete_all3 = self.cur_delete_all3.fetchall()
        
        TodolistListView.refresh(self.listview, self._todolist)
        
        if self.fetch_delete_all3 == []:
            QMessageBox.information(self, _('Successful'), _('All todos in {todolist} deleted.').format(todolist = self._todolist))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete all todos in {todolist}.').format(todolist = self._todolist))


class TodosListView(QListView):
    def __init__(self, parent: QTabWidget, caller: str = "todos"):
        super().__init__(parent)
        
        global todos_model1, todos_model2
        
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip(_("Double-click to opening a todolist."))
        
        self.proxy = QSortFilterProxyModel(self)
        
        if caller == "todos":  
            todos_model1 = QStringListModel(self)
            self.proxy.setSourceModel(todos_model1)
            
        elif caller == "home":
            todos_model2 = QStringListModel(self)
            self.proxy.setSourceModel(todos_model2)
        
        self.setModel(self.proxy)
        
        if caller == "todos":
            self.selectionModel().selectionChanged.connect(
                lambda: Todos.insert(parent, self.proxy.itemData(self.currentIndex())))
        
        self.doubleClicked.connect(lambda: Todos.open(parent, self.proxy.itemData(self.currentIndex())[0]))
        
        self.refresh()
        
    def refresh(self):
        global todos_list
        
        todos_list = []
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_refresh:
            self.cur_refresh = self.db_refresh.cursor()
            self.cur_refresh.execute("select name from todos")
            self.fetch_refresh = self.cur_refresh.fetchall()
        
        for i in range(0, len(self.fetch_refresh)):
            todos_list.append(self.fetch_refresh[i][0])

        try:
            todos_model1.setStringList(todos_list)
        except NameError:
            pass
    
        try:
            todos_model2.setStringList(todos_list)
        except NameError:
            pass


class Todos(QTabWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        
        self.todolists = {}
        
        self.home = QWidget(self)
        self.home.setLayout(QHBoxLayout(self.home))
        
        self.side = QWidget(self.home)
        self.side.setFixedWidth(288)
        self.side.setLayout(QGridLayout(self.side))
        self.side.setStatusTip(_("Double-click on list to opening a todolist."))
        
        self.created = QLabel(self.side, alignment=align_center, 
                              text=_('Created:'))
        
        self.listview = TodosListView(self)
        
        self.entry = QLineEdit(self.side)
        self.entry.setPlaceholderText(_('Type a todolist name'))
        self.entry.setStatusTip("Typing in entry also searches in list.")
        self.entry.textChanged.connect(
            lambda: self.listview.proxy.setFilterRegularExpression(QRegularExpression
                                                          (self.entry.text(), QRegularExpression.PatternOption.CaseInsensitiveOption)))
        
        self.open_button = QPushButton(self.side, text=_("Open"))
        self.open_button.clicked.connect(lambda: self.open(self.entry.text()))
        
        self.add_button = QPushButton(self.side, text=_("Add"))
        self.add_button.clicked.connect(lambda: self.add(self.entry.text(),
                                                         datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
        self.rename_button = QPushButton(self.side, text=_("Rename"))
        self.rename_button.clicked.connect(lambda: self.rename(self.entry.text()))
        
        self.delete_button = QPushButton(self.side, text=_("Delete"))
        self.delete_button.clicked.connect(lambda: self.delete(self.entry.text()))
        
        self.delete_all_button = QPushButton(self.side, text=_("Delete All"))
        self.delete_all_button.clicked.connect(self.delete_all)

        self.home.layout().addWidget(Todolist(self, "main"))
        self.side.layout().addWidget(self.created, 0, 0, 1, 2)
        self.side.layout().addWidget(self.listview, 1, 0, 1, 2)
        self.side.layout().addWidget(self.entry, 2, 0, 1, 2)
        self.side.layout().addWidget(self.open_button, 3, 0, 1, 2)
        self.side.layout().addWidget(self.add_button, 4, 0, 1, 1)
        self.side.layout().addWidget(self.rename_button, 4, 1, 1, 1)
        self.side.layout().addWidget(self.delete_button, 5, 0, 1, 1)
        self.side.layout().addWidget(self.delete_all_button, 5, 1, 1, 1)
        self.home.layout().addWidget(self.side)
        
        self.addTab(self.home, _('Home'))
        self.setTabsClosable(True)
        self.setMovable(True)
        
        self.tabCloseRequested.connect(self.close)
         
    def close(self, index: int):
        if index != self.indexOf(self.home):
            Sidebar.remove(self.tabText(index).replace("&", ""), self)
            try:
                del self.todolists[self.tabText(index).replace("&", "")]
            finally:
                self.removeTab(index)
    
    def insert(self, todolist: str):
        if todolist != {}:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_insert:
                self.cur_insert = self.db_insert.cursor()
                self.cur_insert.execute(f"select name, created from todos where name = '{todolist[0]}'")
                self.fetch_insert = self.cur_insert.fetchone()
            
            try:
                self.entry.setText(self.fetch_insert[0])
                self.created.setText(f"{_('Created')}: {self.fetch_insert[1]}")
            except TypeError:
                self.created.setText(f"{_('Created')}:")
        
    def control(self, todolist: str, mode: str = "normal"):
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_control:
                self.cur_control = self.db_control.cursor()
                self.cur_control.execute(f"select * from '{todolist}'")
            return True
        except sqlite3.OperationalError:
            if mode == "normal":
                QMessageBox.critical(self, _('Error'), _('There is no todo list called {todolist}.').format(todolist = todolist))
            return False
        finally:
            self.cur_control.close()
    
    def open(self, todolist: str):
        if todolist == "main" or todolist == "" or todolist == None:
            QMessageBox.critical(self, _('Error'), _('Todo list name can not be blank or main.'))
            return
        
        if self.control(todolist) == False:
            return
        
        if todolist in self.todolists:
            self.setCurrentWidget(self.todolists[todolist])
            
        else:
            Sidebar.add(todolist, self)
            self.todolists[todolist] = Todolist(self, todolist)
            self.addTab(self.todolists[todolist], todolist)
            self.setCurrentWidget(self.todolists[todolist])
    
    def add(self, todolist: str, created: str):
        if todolist == "main" or todolist == "" or todolist == None:
            QMessageBox.critical(self, _('Error'), _('Todo list name can not be blank or main.'))
            return 
        
        try:
            with sqlite3.connect(f"{userdata}todos.db") as self.db_add1:
                self.sql_add1 = f"""
                CREATE TABLE {todolist} (
                    todo TEXT NOT NULL PRIMARY KEY,
                    status TEXT NOT NULL,
                    started TEXT NOT NULL,
                    completed TEXT
                );"""
                self.cur_add1 = self.db_add1.cursor()
                self.cur_add1.execute(self.sql_add1)
                self.cur_add1.execute(f"insert into todos (name, created) values ('{todolist}', '{created}')")
                self.db_add1.commit()
                
        except sqlite3.OperationalError:
            QMessageBox.critical(self, _('Error'), _('{todolist} list already exist.').format(todolist = todolist))
            return
        
        TodosListView.refresh(self.listview)
        
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5) as self.db_add2:
                self.cur_add2 = self.db_add2.cursor()
                self.cur_add2.execute(f"select * from '{todolist}'")
                self.cur_add2.fetchall()
                self.cur_add2.execute(f"select name, created from todos where name = '{todolist}'")
                self.fetch_add2 = self.cur_add2.fetchone()
            
            if todolist in self.fetch_add2 and created in self.fetch_add2:
                QMessageBox.information(self, _('Successful'), _('{todolist} list added.').format(todolist = todolist))
                
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to add {todolist} list.').format(todolist = todolist))
        
        except sqlite3.OperationalError:
            QMessageBox.critical(self, _('Error'), _('Failed to add {todolist} list.').format(todolist = todolist))

    def rename(self, todolist: str):
        if todolist == "main" or todolist == "" or todolist == None:
            QMessageBox.critical(self, _('Error'), _('Todo list name can not be blank or main.'))
            return
        
        if self.control(todolist) == False:
            return

        self.newname, self.topwindow = QInputDialog.getText(self, 
                                                             _("Rename {todolist} List").format(todolist = todolist), 
                                                             _("Please enter a new name for {todolist} list below.").format(todolist = todolist))
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_rename1:
            self.cur_rename1 = self.db_rename1.cursor()
            self.cur_rename1.execute(f"ALTER TABLE {todolist} RENAME TO {self.newname}")
            self.cur_rename1.execute(f"update todos set name = '{self.newname}' where name = '{todolist}'")
            self.db_rename1.commit()
        
        TodosListView.refresh(self.listview)
        
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5) as self.db_rename2:
                self.cur_rename2 = self.db_rename2.cursor()
                self.cur_rename2.execute(f"select * from '{self.newname}'")
                self.cur_rename2.fetchall()
                self.cur_rename2.execute(f"select name from todos")
                self.fetch_rename2 = self.cur_rename2.fetchone()
                
            self.entry.setText(self.newname)
                
            if self.newname in self.fetch_rename2:
                QMessageBox.information(self, _('Successful'), _('{todolist} list renamed as {newname}.').format(todolist = todolist, newname = self.newname))
        
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to rename {todolist} list.').format(todolist = todolist))
        
        except sqlite3.OperationalError:
            QMessageBox.critical(self, _('Error'), _('Failed to rename {todolist} list.').format(todolist = todolist))
    
    def delete(self, todolist: str):
        if todolist == "main" or todolist == "" or todolist == None:
            QMessageBox.critical(self, _('Error'), _('Todo list name can not be blank or main.'))
            return
        
        if self.control(todolist) == False:
            return
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete1:
            self.cur_delete1 = self.db_delete1.cursor()
            self.cur_delete1.execute(f"DROP TABLE {todolist}")
            self.cur_delete1.execute(f"delete from todos where name = '{todolist}'")
            self.db_delete1.commit()
        
        TodosListView.refresh(self.listview)
        self.entry.setText("")
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5) as self.db_delete2:
            self.cur_delete2 = self.db_delete2.cursor()
            
            try:
                self.cur_delete2.execute(f"select * from '{todolist}'")
                self.cur_delete2.fetchall()
            
            except sqlite3.OperationalError:
                self.cur_delete2.execute(f"select name from todos")
                self.fetch_delete2 = self.cur_delete2.fetchall()
                    
                if todolist not in self.fetch_delete2:
                    create_db()
                    QMessageBox.information(self, _('Successful'), _('{todolist} list deleted.').format(todolist = todolist))
            
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to delete {todolist} list.').format(todolist = todolist))
    
    def delete_all(self):
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all1:
            self.cur_delete_all1 = self.db_delete_all1.cursor()
            self.cur_delete_all1.execute(f"select name from todos")
            self.fetch_delete_all1 = self.cur_delete_all1.fetchall()
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all2:
            self.cur_delete_all2 = self.db_delete_all2.cursor()
            self.cur_delete_all2.execute("DROP TABLE todos")
            
            for todolist in self.fetch_delete_all1:
                self.cur_delete_all2.execute(f"DROP TABLE {todolist[0]}")
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all3:
            self.cur_delete_all3 = self.db_delete_all3.cursor()
            
            try:
                for todolist in self.fetch_delete_all1:
                    self.cur_delete_all3.execute(f"select * from {todolist[0]}")
                self.cur_delete_all3.fetchall()
                
            except sqlite3.OperationalError:
                try:
                    self.cur_delete_all3.execute(f"select name from todos'")
                    self.cur_delete_all3.fetchall()

                except sqlite3.OperationalError:
                    create_db()
                    TodosListView.refresh(self.listview)
                    
                    QMessageBox.information(self, _('Successful'), _('All todolists deleted.'))

            else:
                QMessageBox.critical(self, _('Error'), _('Failed to delete all todolists.')) 
    
    
if __name__ == "__main__":
    from mainwindow import MainWindow
    
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    
    window.tabview.setCurrentIndex(2)

    application.exec()