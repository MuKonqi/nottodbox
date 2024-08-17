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
import sqlite3
import datetime
from gettext import gettext as _
from PyQt6.QtCore import Qt, QStringListModel, QSortFilterProxyModel
from PyQt6.QtWidgets import *


todolists = {}


username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


class TodosDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}todos.db")
        self.cur = self.db.cursor()
        
    def addTodo(self, todolist: str, todo: str) -> bool:
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(
            f"update todolists set edited = '{date_time}' where name = '{todolist}'")
        self.db.commit()
        
        sql = f"""insert into '{todolist}' (todo, status, started) 
        values ('{todo}', 'uncompleted', '{date_time}')"""
        
        self.cur.execute(sql)
        self.db.commit()
        
        self.cur.execute(f"select * from '{todolist}' where todo = '{todo}'")
        control = self.cur.fetchone()
        
        if control[0] == todo and control[1] == "uncompleted" and control[2] == date_time:
            return True
        else:
            return False
        
    def checkIfTheTablesExist(self, tables: list) -> bool:
        try:
            for table in tables:
                self.cur.execute(f"select * from {table}")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def checkIfTheTodoExists(self, todolist: str, todo: str) -> bool:
        self.cur.execute(f"select * from '{todolist}' where todo = '{todo}'")
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
    
    def checkIfTheTodolistExists(self, name: str) -> bool:
        self.cur.execute(f"select * from todolists where name = '{name}'")
        
        try:
            self.cur.fetchone()[0]
            return self.checkIfTheTablesExist([name])
        
        except TypeError:
            return False
        
    def createTables(self, tables: list) -> bool:
        for table in tables:
            if table == "todolists":
                sql = """
                CREATE TABLE IF NOT EXISTS todolists (
                    name TEXT NOT NULL PRIMARY KEY,
                    created TEXT NOT NULL,
                    edited TEXT
                );"""
            
            else:
                sql = f"""
                CREATE TABLE IF NOT EXISTS '{table}' (
                    todo TEXT NOT NULL PRIMARY KEY,
                    status TEXT NOT NULL,
                    started TEXT NOT NULL,
                    completed TEXT
                );"""
        
            self.cur.execute(sql)
            self.db.commit()
        
        return self.checkIfTheTablesExist(tables)
    
    def createTodolist(self, name: str) -> bool:
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        sql = f"insert into todolists (name, created, edited) values ('{name}', '{date_time}', '')"
        
        self.cur.execute(sql)
        self.db.commit()
        
        return self.createTables([name])
    
    def deleteTodo(self, todolist: str, todo: str) -> bool:
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(
            f"update todolists set edited = '{date_time}' where name = '{todolist}'")
        self.db.commit()
        
        self.cur.execute(f"delete from '{todolist}' where todo = '{todo}'")
        self.db.commit()
        
        call = self.checkIfTheTodoExists(todolist, todo)
        
        if call:
            return False
        else:
            return True
        
    def deleteTodolist(self, name: str) -> bool:
        self.cur.execute(f"delete from todolists where name = '{name}'")
        self.db.commit()
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        call = self.checkIfTheTodolistExists(name)
        
        if call:
            return False
        else:
            return True
        
        
    def editTodo(self, todolist: str, todo: str, newtodo: str) -> bool:
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(
            f"update todolists set edited = '{date_time}' where name = '{todolist}'")
        self.db.commit()
        
        self.cur.execute(f"update '{todolist}' set todo = '{newtodo}' where todo = '{todo}'")
        self.db.commit()
        
        return self.checkIfTheTodoExists(todolist, newtodo)
    
    def getTodos(self, todolist: str) -> list:
        self.cur.execute(f"select todo, status from '{todolist}'")
        return self.cur.fetchall()
    
    def getTodolists(self) -> list:
        self.cur.execute(f"select name from todolists")
        return self.cur.fetchall()
    
    def getTodoInformations(self, todolist: str, todo: str) -> tuple:
        self.cur.execute(f"select status, started, completed from '{todolist}' where todo = '{todo}'")
        return self.cur.fetchone()
    
    def getTodolistInformations(self, name: str) -> tuple:
        self.cur.execute(f"select created, edited from todolists where name = '{name}'")
        return self.cur.fetchone()
        
    def recreateTables(self, tables: list) -> bool:
        for table in tables:
            self.cur.execute(f"DROP TABLE IF EXISTS '{table}'")
            self.db.commit()
        
        call = self.checkIfTheTablesExist(tables)
        
        if call:
            return False
        else:
            return self.createTables(tables)
        
    def renameTodolist(self, name: str, newname: str) -> bool:
        self.cur.execute(f"update todolists set name = '{newname}' where name = '{name}'")
        self.db.commit()
        
        self.cur.execute(f"ALTER TABLE '{name}' RENAME TO '{newname}'")
        self.db.commit()
        
        return self.checkIfTheTodolistExists(newname)
        
    def makeCompleted(self, todolist: str, todo: str) -> bool:
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(
            f"update todolists set edited = '{date_time}' where name = '{todolist}'")
        self.db.commit()
        
        self.cur.execute(f"update '{todolist}' set status = 'completed' where todo = '{todo}'")
        self.db.commit()
        
        self.cur.execute(f"select status from '{todolist}' where todo = '{todo}'")
        control = self.cur.fetchone()
        
        if control[0] == "completed":
            return True
        else:
            return False
        
    def makeUncompleted(self, todolist: str, todo: str) -> bool:
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(
            f"update todolists set edited = '{date_time}' where name = '{todolist}'")
        self.db.commit()
        
        self.cur.execute(f"update '{todolist}' set status = 'uncompleted' where todo = '{todo}'")
        self.db.commit()
        
        self.cur.execute(f"select status from '{todolist}' where todo = '{todo}'")
        control = self.cur.fetchone()
        
        if control[0] == "uncompleted":
            return True
        else:
            return False


todosdb = TodosDB()

create_tables = todosdb.createTables(["todolists", "main"])
if not create_tables:
    print("[2] Failed to create tables")
    sys.exit(2)


class TodosTabWidget(QTabWidget): 
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        global todos_parent
        
        todos_parent = parent
        
        self.home = QWidget(self)
        self.home.setLayout(QHBoxLayout(self))
        
        self.maintodos = TodolistWidget(self, "main")
        
        self.side = QWidget(self.home)
        self.side.setFixedWidth(300)
        self.side.setLayout(QGridLayout(self.side))
        
        self.created = QLabel(self.side, alignment=Qt.AlignmentFlag.AlignCenter,
                              text=_("Created: "))
        
        self.edited = QLabel(self.side, alignment=Qt.AlignmentFlag.AlignCenter,
                             text=_("Edited: "))
        
        self.listview = TodosListView(self)
        
        self.entry = QLineEdit(self.side)
        self.entry.setPlaceholderText(_("Enter a todo list name"))
        self.entry.setStatusTip(_("You can search in list while entering anythings in entry."))
        self.entry.setClearButtonEnabled(True)
        self.entry.textChanged.connect(self.listview.setFilter)
        
        self.open_create_button = QPushButton(self.side, text=_("Open/create todo list"))
        self.open_create_button.clicked.connect(lambda: self.openCreate(self.entry.text()))
        
        self.rename_button = QPushButton(self.side, text=_("Rename todo list"))
        self.rename_button.clicked.connect(lambda: self.renameTodolist(self.entry.text()))
        
        self.delete_todolist_button = QPushButton(self.side, text=_("Delete todo list"))
        self.delete_todolist_button.clicked.connect(lambda: self.deleteTodolist(self.entry.text()))
        
        self.delete_all_button = QPushButton(self.side, text=_("Delete all todo lists"))
        self.delete_all_button.clicked.connect(self.deleteAll)
        
        self.side.layout().addWidget(self.created, 0, 0, 1, 2)
        self.side.layout().addWidget(self.edited, 1, 0, 1, 2)
        self.side.layout().addWidget(self.listview, 2, 0, 1, 2)
        self.side.layout().addWidget(self.entry, 3, 0, 1, 2)
        self.side.layout().addWidget(self.open_create_button, 4, 0, 1, 1)
        self.side.layout().addWidget(self.rename_button, 4, 1, 1, 1)
        self.side.layout().addWidget(self.delete_todolist_button, 5, 0, 1, 1)
        self.side.layout().addWidget(self.delete_all_button, 5, 1, 1, 1)
        self.home.layout().addWidget(self.maintodos)
        self.home.layout().addWidget(self.side)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        
    def checkIfTheTodolistExists(self, name: str, mode: str = "normal") -> None:
        call = todosdb.checkIfTheTodolistExists(name)
        
        if call == False and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no todo list called {name}.").format(name = name))
        
        return call
         
    def closeTab(self, index: int) -> None:
        if index != self.indexOf(self.home):           
            del todolists[self.tabText(index).replace("&", "")]
            
            todos_parent.dock.widget().removePage(self.tabText(index).replace("&", ""), self)
            self.removeTab(index)
            
    def deleteAll(self) -> None:
        call = todosdb.recreateTables(["todolists"])
    
        if call:
            self.listview.insertNames()
            self.insertInformations("")
            
            QMessageBox.information(self, _("Successful"), _("All todo lists deleted."))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all todo lists."))
                       
    def deleteTodolist(self, name: str) -> None:
        if name == "" or name == None or name == "main" or name == "todolists":
            QMessageBox.critical(self, _("Error"), _('Todo list name can not be blank, "main" or "todolists".'))
            return
        
        if self.checkIfTheTodolistExists(name) == False:
            return
        
        call = todosdb.deleteTodolist(name)
            
        if call:
            self.listview.insertNames()
            self.insertInformations("")
            
            QMessageBox.information(self, _("Successful"), _("{name} todo list deleted.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {name} todo list.").format(name = name))

    def insertInformations(self, name: str) -> None:
        if name != "":
            call = todosdb.getTodolistInformations(name)
        else:
            call = None
            
        self.entry.setText(name)
        
        try:
            self.created.setText(_("Created: ") + call[0])
        except TypeError:
            self.created.setText(_("Created: "))
            
        try:
            self.edited.setText(_("Edited: ") + call[1])
        except TypeError:
            self.edited.setText(_("Edited: "))
        
    def openCreate(self, name: str) -> None:
        if name == "" or name == None or name == "todolists":
            QMessageBox.critical(self, _("Error"), _('Todo list name can not be blank or "todolists".'))
            return
        
        todos_parent.tabwidget.setCurrentIndex(2)
        
        if name == "main":
            self.setCurrentWidget(self.home)
            return
        
        if name in todolists:
            self.setCurrentWidget(todolists[name])
            
        else:
            todos_parent.dock.widget().addPage(name, self)
            todolists[name] = TodolistWidget(self, name)
            self.addTab(todolists[name], name)
            self.setCurrentWidget(todolists[name])
    
    def renameTodolist(self, name: str) -> None:
        if name == "" or name == None or name == "main" or name == "todolists":
            QMessageBox.critical(self, _("Error"), _('Todo list name can not be blank, "main" or "todolists".'))
            return
        
        if self.checkIfTheTodolistExists(name) == False:
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} Todo List").format(name = name), 
                                                  _("Please enter a new name for {name} below.").format(name = name))
        
        if newname != "" and newname != None and topwindow:
            call = todosdb.renameTodolist(name, newname)
            
            self.listview.insertNames()
            
            if call:
                self.insertInformations(newname)
                
                QMessageBox.information(self, _("Successful"), _("{name} todo list renamed as {newname}.")
                                        .format(name = name, newname = newname))
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to rename {name} todo list.")
                                     .format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} todo list.")
                                 .format(name = name))


class TodosListView(QListView):
    def __init__(self, parent: TodosTabWidget, caller: str = "todos") -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.caller = caller

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        if self.caller == "todos":  
            global todos_model
            
            todos_model = QStringListModel(self)
            
        self.proxy.setSourceModel(todos_model)
        
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip("Double-click to opening a todo list.")
        self.setModel(self.proxy)

        if self.caller == "todos":
            self.selectionModel().selectionChanged.connect(
                lambda: self.parent_.insertInformations(self.getItemText()))
        
        self.doubleClicked.connect(lambda: self.parent_.openCreate(self.getItemText()))
        
        self.insertNames()
        
    def getItemText(self) -> str:
        try:
            return self.proxy.itemData(self.currentIndex())[0]
        except KeyError:
            return ""
        
    def insertNames(self) -> None:
        global menu_todos
        
        call = todosdb.getTodolists()
        names = []
        
        if self.caller == "todos":
            if not "menu_todos" in globals():
                menu_todos = todos_parent.menuBar().addMenu(_("Todos"))
            
            menu_todos.clear()
            
            menu_todos.addAction(_("Main List"), lambda: self.parent_.openCreate("main"))
            
            for name in call:
                names.append(name[0])
                menu_todos.addAction(name[0], lambda name = name: self.parent_.openCreate(name[0]))

        elif self.caller == "home":
            for name in call:
                names.append(name[0])
                
        todos_model.setStringList(names)
        
    def setFilter(self, text: str) -> None:
        self.proxy.beginResetModel()
        self.proxy.endResetModel()
        self.proxy.setFilterFixedString(text)
    
        self.parent_.created.setText(_("Created: "))
        self.parent_.edited.setText(_("Edited: "))


class TodolistWidget(QWidget):
    def __init__(self, parent: TodosTabWidget, name: str) -> None:
        self.parent_ = parent
        self.name = name
        
        call = todosdb.checkIfTheTodolistExists(name)
        
        if name != "main" and not call:
            call = todosdb.createTodolist(name)
            
            self.parent_.listview.insertNames()
            
            if not call:
                global todolists

                del todolists[name]
                
                QMessageBox.critical(parent, _("Error"), _("Failed to create todo list {name}.").format(name = name))

                return       
        
        super().__init__(parent)
        
        self.setLayout(QGridLayout(self))
        
        self.started = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
                              text=_('Started:'))
        self.completed = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
                                text=_("Completed:"))
        
        self.listview = TodolistListView(self, self.name)
        
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText(_("Enter a todo"))
        self.entry.setStatusTip(_("You can search in list while entering anythings in entry."))
        self.entry.setClearButtonEnabled(True)
        self.entry.textChanged.connect(self.listview.setFilter)
        
        self.comp_button = QPushButton(self, text=_("Make completed todo"))
        self.comp_button.clicked.connect(lambda: self.makeCompleted(self.entry.text()))
        
        self.uncomp_button = QPushButton(self, text=_("Make uncompleted todo"))
        self.uncomp_button.clicked.connect(lambda: self.makeUncompleted(self.entry.text()))
        
        self.add_button = QPushButton(self, text=_("Add todo"))
        self.add_button.clicked.connect(lambda: self.addTodo(self.entry.text()))
        
        self.edit_button = QPushButton(self, text=_("Edit todo"))
        self.edit_button.clicked.connect(lambda: self.editTodo(self.entry.text()))
        
        self.delete_todo_button = QPushButton(self, text=_("Delete todo"))
        self.delete_todo_button.clicked.connect(lambda: self.deleteTodo(self.entry.text()))
        
        self.delete_all_button = QPushButton(self, text=_("Delete all todos"))
        self.delete_all_button.clicked.connect(self.deleteAll)
        
        self.layout().addWidget(self.started, 0, 0, 1, 2)
        self.layout().addWidget(self.completed, 1, 0, 1, 2)
        self.layout().addWidget(self.listview, 2, 0, 1, 2)
        self.layout().addWidget(self.entry, 3, 0, 1, 2)
        self.layout().addWidget(self.comp_button, 4, 0, 1, 1)
        self.layout().addWidget(self.uncomp_button, 4, 1, 1, 1)
        self.layout().addWidget(self.add_button, 5, 0, 1, 1)
        self.layout().addWidget(self.edit_button, 5, 1, 1, 1)
        self.layout().addWidget(self.delete_todo_button, 6, 0, 1, 1)
        self.layout().addWidget(self.delete_all_button, 6, 1, 1, 1)
        
    def addTodo(self, todo: str) -> None:
        if todo == "" or todo == None:
            todo, topwindow = QInputDialog.getText(self, 
                                                    _("Add A Todo"),
                                                    _("Please enter a todo below."))
            
            if todo == "" or todo == None or not topwindow:
                QMessageBox.critical(self, _("Error"), _("Failed to add {todo} todo.").format(todo = todo))
                return
        
        call = todosdb.addTodo(self.name, todo)
        
        if call:
            self.listview.insertTodos()
            self.insertInformations(todo)            

            QMessageBox.information(self, _("Successful"), _("{todo} added.").format(todo = todo))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to add {todo} todo.").format(todo = todo))
        
    def checkIfTheTodoExists(self, todo: str, mode: str = "normal") -> None:
        if todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _('Todo name can not be blank.'))
            return
        
        call = todosdb.checkIfTheTodoExists(self.name, todo)
        
        if call == False and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no todo called {todo}.").format(todo = todo))
        
        return call
    
    def insertInformations(self, todo: str) -> None:
        if todo != "":
            call = todosdb.getTodoInformations(self.name, todo)
        else:
            call = None
        
        self.entry.setText(todo)
        
        try:
            self.started.setText(_("Started: ") + call[1])
        except TypeError:
            self.started.setText(_("Started: "))

        try:
            self.completed.setText(_("Completed: ") + call[2])
        except TypeError:
            self.completed.setText(_("Completed: "))
            
    def deleteAll(self) -> None:
        call = todosdb.recreateTables([self.name])

        if call:
            self.listview.insertTodos()
            self.insertInformations("")
            
            QMessageBox.information(self, _("Successful"), _("All todos deleted."))
            
        else:
            QMessageBox.critical(self,_("Error"), _("Failed to delete all todos."))
        
    def deleteTodo(self, todo: str) -> None:
        if todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _('Todo can not be blank.'))
            return
        
        if self.checkIfTheTodoExists(todo) == False:
            return
        
        call = todosdb.deleteTodo(self.name, todo)
        
        if call:
            self.listview.insertTodos()
            self.insertInformations("")
            
            QMessageBox.information(self, _("Successful"), _("Todo {todo} deleted.").format(todo = todo))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {todo}.").format(todo = todo))
        
    def editTodo(self, todo: str) -> None:
        if todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _('Todo can not be blank.'))
            return
        
        if self.checkIfTheTodoExists(todo) == False:
            return
        
        newtodo, topwindow = QInputDialog.getText(self, 
                                                  _("Edit {todo} Todo").format(todo = todo), 
                                                  _("Please enter a text for {todo} below.").format(todo = todo))
        
        if newtodo != "" and newtodo != None and topwindow:
            call = todosdb.editTodo(self.name, todo, newtodo)
            
            self.listview.insertTodos()
            
            if call:
                self.insertInformations(newtodo)
                
                QMessageBox.information(self, _("Successful"), _("{todo} todo edited as {newtodo}.")
                                        .format(todo = todo, newtodo = newtodo))
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to edit {name} todo.")
                                     .format(todo = todo))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to edit {name} todo.")
                                 .format(todo = todo))
        
    def makeCompleted(self, todo: str) -> None:
        if todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _('Todo can not be blank.'))
            return
        
        if self.checkIfTheTodoExists(todo) == False:
            return
        
        call = todosdb.makeCompleted(self.name, todo)
        
        if call:
            self.insertInformations(todo)
            
            QMessageBox.information(self, _("Successful"), _("{todo} maded completed.").format(todo = todo))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to make {todo} completed.").format(todo = todo))
        
    def makeUncompleted(self, todo: str) -> None:
        if todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _('Todo can not be blank.'))
            return
        
        if self.checkIfTheTodoExists(todo) == False:
            return
        
        call = todosdb.makeUncompleted(self.name, todo)
        
        if call:
            self.insertInformations(todo)
            
            QMessageBox.information(self, _("Successful"), _("{todo} maded uncompleted.").format(todo = todo))

        else:
            QMessageBox.critical(self, _("Error"), _("Failed to make {todo} uncompleted.").format(todo = todo))


class TodolistListView(QListView):
    def __init__(self, parent: TodolistWidget, name: str, caller: str = "todos") -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.name = name
        self.caller = caller
        self.proxy = QSortFilterProxyModel(self)
        
        if caller == "todos":
            self.model_ = QStringListModel(self)
            self.proxy.setSourceModel(self.model_)
            
        elif caller == "home":
            global todolist_model_for_home
            
            todolist_model_for_home = QStringListModel(self)
            self.proxy.setSourceModel(todolist_model_for_home)
            
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip(_("Double-click to marking a todo as completed/uncompleted."))
        self.setModel(self.proxy)
        
        if caller == "todos":
            self.selectionModel().selectionChanged.connect(
                lambda: self.parent_.insertInformations(self.getItemText()))
        
        self.doubleClicked.connect(lambda: self.setTodoStatus(self.getItemText()))
        
        self.insertTodos()
        
    def getItemText(self) -> str:
        try:
            return self.proxy.itemData(self.currentIndex())[0]
        except KeyError:
            return ""
    
    def insertTodos(self) -> None:
        call = todosdb.getTodos(self.name)
        todos = []
        
        for todo, status in call:
            if status == "completed":
                prefix = "[+]"
            elif status == "uncompleted":
                prefix = " [-]"
            
            todos.append(f"{prefix} {todo}")
    
        try:
            self.model_.setStringList(todos)
        except AttributeError:
            pass
    
        if self.name == "main":
            try:
                todolist_model_for_home.setStringList(todos)
            except NameError:
                pass

    def setFilter(self, text: str) -> None:
        self.proxy.beginResetModel()
        self.proxy.endResetModel()
        self.proxy.setFilterFixedString(text)
    
        self.parent_.started.setText(_("Started: "))
        self.parent_.completed.setText(_("Completed: "))
        
    def setTodoStatus(self, todo: str) -> None:
        call = todosdb.getTodoInformations(self.name, todo)
        
        if call[0] == "completed":
            self.parent_.makeUncompleted(todo)

        elif call[0] == "uncompleted":
            self.parent_.makeCompleted(todo)