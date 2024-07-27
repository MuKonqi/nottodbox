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

from PyQt6.QtWidgets import QWidget
sys.dont_write_bytecode = True


import getpass
import sqlite3
import datetime
from gettext import gettext as _
from PyQt6.QtCore import Qt, QStringListModel, QSortFilterProxyModel
from PyQt6.QtWidgets import *


todolists_widgets = {}
todolists_listviews = {}


username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


class TodosDB:
    """The totos database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}todos.db")
        self.cur = self.db.cursor()
        
    def addTodo(self, todolist: str, todo: str) -> bool:
        """
        Add a todo.

        Args:
            todolist (str): Todolist name
            todo (str): Todo

        Returns:
            bool: True if successful, False if not
        """
        
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
        
    def checkIfTheTablesExists(self, tables: list) -> bool:
        """
        Check if the tables exists.
        
        Args:
            tables (list): Tables' names

        Returns:
            bool: True if the table exists, if not False
        """
        
        try:
            for table in tables:
                self.cur.execute(f"select * from {table}")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def checkIfTheTodoExist(self, todolist: str, todo: str) -> bool:
        """
        Check if the todo exists.

        Args:
            todolist (str): Todolist name
            todo (str): Todo

        Returns:
            bool: True if the todolist exists, if not False
        """
        
        self.cur.execute(f"select * from '{todolist}' where todo = '{todo}'")
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
    
    def checkIfTheTodolistExist(self, name: str) -> bool:
        """
        Check if the todolist exists.

        Args:
            name (str): Todo list name

        Returns:
            bool: True if the todolist exists, if not False
        """
        
        self.cur.execute(f"select * from todolists where name = '{name}'")
        
        try:
            self.cur.fetchone()[0]
            return self.checkIfTheTablesExists([name])
        
        except TypeError:
            return False
        
    def createTables(self, tables: list) -> bool:
        """
        If the tables not exist, create it.
        
        Args:
            tables (list): Tables' names

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
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
        
        return self.checkIfTheTablesExists(tables)
    
    def createTodolist(self, name: str) -> bool:
        """
        Create a todolist.

        Args:
            name (str): Todolist name
            
        Returns:
            bool: True if successful, False if not
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        sql = f"insert into todolists (name, created, edited) values ('{name}', '{date_time}', '')"
        
        self.cur.execute(sql)
        self.db.commit()
        
        return self.createTables([name])
    
    def deleteTodo(self, todolist: str, todo: str) -> bool:
        """
        Delete a todo.

        Args:
            todolist (str): Todolist name
            todo (str): Todo

        Returns:
            bool: True if successful, False if not
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(
            f"update todolists set edited = '{date_time}' where name = '{todolist}'")
        self.db.commit()
        
        self.cur.execute(f"delete from '{todolist}' where todo = '{todo}'")
        self.db.commit()
        
        call = self.checkIfTheTodoExist(todolist, todo)
        
        if call:
            return False
        else:
            return True
        
    def deleteTodolist(self, name: str) -> bool:
        """
        Delete a todolist.

        Args:
            name (str): Todolist name

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"delete from todolists where name = '{name}'")
        self.db.commit()
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        call = self.checkIfTheTodolistExist(name)
        
        if call:
            return False
        else:
            return True
        
        
    def editTodo(self, todolist: str, todo: str, newtodo: str) -> bool:
        """
        Edit a todo.

        Args:
            todolist (str): Todolist name
            todo (str): Old todo
            newtodo (str): New todo

        Returns:
            bool: True if successful, False if not
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(
            f"update todolists set edited = '{date_time}' where name = '{todolist}'")
        self.db.commit()
        
        self.cur.execute(f"update '{todolist}' set todo = '{newtodo}' where todo = '{todo}'")
        self.db.commit()
        
        return self.checkIfTheTodoExist(todolist, newtodo)
    
    def getTodos(self, todolist: str) -> list:
        """
        Get all todos from a todolist.

        Args:
            todolist (str): Todolist name

        Returns:
            list: List of todos
        """
        
        self.cur.execute(f"select todo from '{todolist}'")
        return self.cur.fetchall()
    
    def getTodolists(self) -> list:
        """
        Get todolists' names.

        Returns:
            list: List of names
        """
        
        self.cur.execute(f"select name from todolists")
        return self.cur.fetchall()
    
    def getTodoInformations(self, todolist: str, name: str) -> tuple:
        """
        Get starting and completing dates.

        Args:
            todolist (str): Todo list name
            todo (str): Todo

        Returns:
            tuple: Returns starting and completing dates
        """
        
        self.cur.execute(f"select started, completed from '{todolist}' where name = '{name}'")
        return self.cur.fetchone()
    
    def getTodolistInformations(self, name: str) -> tuple:
        """
        Get creation and edit dates.

        Args:
            name (str): Todo list name

        Returns:
            tuple: Returns creation and edit dates
        """
        
        self.cur.execute(f"select created, edited from todolists where name = '{name}'")
        return self.cur.fetchone()
        
    def recreateTables(self, tables: list) -> bool:
        """
        Recreate a tables.

        Args:
            tables (list): Tables' names

        Returns:
            bool: True if successful, False if not
        """
        
        for table in tables:
            self.cur.execute(f"DROP TABLE IF EXISTS '{table}'")
            self.db.commit()
        
        call = self.checkIfTheTablesExists(tables)
        
        if call:
            return False
        else:
            return self.createTables(tables)
        
    def renameTodolist(self, name: str, newname: str) -> bool:
        """
        Rename a todo list.

        Args:
            name (str): Old name
            newname (str): New name

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        self.cur.execute(f"update todolists set name = '{newname}' where name = '{name}'")
        self.db.commit()
        
        self.cur.execute(f"ALTER TABLE '{name}' RENAME TO '{newname}'")
        self.db.commit()
        
        return self.checkIfTheTodolistExist(newname)
        
    def makeCompleted(self, todolist: str, todo: str) -> bool:
        """
        Make completed a todo.

        Args:
            todolist (str): Todolist name
            todo (str): Todo

        Returns:
            bool: True if successful, False if not
        """
        
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
        """
        Make uncompleted a todo.

        Args:
            todolist (str): Todolist name
            todo (str): Todo

        Returns:
            bool: True if successful, False if not
        """
        
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
    """The "Todos" tab widget."""
    
    def __init__(self, parent: QWidget) -> None:
        """Init and then set."""
        
        super().__init__(parent)
        
        global todos_parent
        
        todos_parent = parent
        
        self.home = QWidget(self)
        self.home.setLayout(QHBoxLayout(self))
        
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
        self.home.layout().addWidget(TodolistWidget(self, "main"))
        self.home.layout().addWidget(self.side)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        
    def checkIfTheTodolistExist(self, name: str, mode: str = "normal") -> None:
        """
        Check if the todo list exists.

        Args:
            name (str): Todo list name
            mode (str, optional): Inverted mode for deleting etc. Defaults to "normal".
        """
        
        call = todosdb.checkIfTheTodolistExist(name)
        
        if call == False and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no todo list called {name}.").format(name = name))
        
        return call
         
    def closeTab(self, index: int) -> None:
        """
        Close a tab.

        Args:
            index (int): Index of tab
        """
        
        if index != self.indexOf(self.home):           
            del todolists_widgets[self.tabText(index).replace("&", "")]
            
            todos_parent.dock.widget().removePage(self.tabText(index).replace("&", ""), self)
            self.removeTab(index)
            
    def deleteAll(self) -> None:
        """Delete all todo lists."""
        
        call = todosdb.recreateTables(["todolists"])
        
        self.listview.insertNames()
        self.insertInformations("")
    
        if call:
            QMessageBox.information(self, _("Successful"), _("All todo lists deleted."))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all todo lists."))
                       
    def deleteTodolist(self, name: str) -> None:
        """
        Delete a todo list.

        Args:
            name (str): Todo list name
        """
        
        if name == "" or name == None or name == "main" or name == "todolists":
            QMessageBox.critical(self, _("Error"), _('Todo list name can not be blank, "main" or "todolists".'))
            return
        
        if self.checkIfTheTodolistExist(name) == False:
            return
        
        call = todosdb.deleteTodolist(name)
        
        self.listview.insertNames()
        self.insertInformations("")
            
        if call:
            QMessageBox.information(self, _("Successful"), _("{name} todo list deleted.").format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {name} todo list.").format(name = name))

    def insertInformations(self, name: str) -> None:
        """Insert name and creation, edit dates.

        Args:
            name (str): Todo list name
        """
        
        if name != "":
            call = todosdb.getTodolistInformations(name)
        else:
            call = None
            
        try:
            self.entry.setText(name)
            self.created.setText(_("Created: ") + call[0])
            self.edited.setText(_("Edited: ") + call[1])
        except TypeError:
            self.entry.setText("")
            self.created.setText(_("Created: "))
            self.edited.setText(_("Edited: "))
        
    def openCreate(self, name: str) -> None:
        """Open or create a todolist.

        Args:
            name (str): Todo list name
        """
        
        if name == "" or name == None or name == "main" or name == "todolists":
            QMessageBox.critical(self, _("Error"), _('Todo list name can not be blank, "main" or "todolists".'))
            return
        
        todos_parent.tabwidget.setCurrentIndex(2)
        
        if name in todolists_widgets:
            self.setCurrentWidget(todolists_widgets[name])
            
        else:
            todos_parent.dock.widget().addPage(name, self)
            todolists_widgets[name] = TodolistWidget(self, name)
            self.addTab(todolists_widgets[name], name)
            self.setCurrentWidget(todolists_widgets[name])
    
    def renameTodolist(self, name: str) -> None:
        """Rename a todo list.

        Args:
            name (str): Todo list name
        """
        
        if name == "" or name == None or name == "main" or name == "todolists":
            QMessageBox.critical(self, _("Error"), _('Todo list name can not be blank, "main" or "todolists".'))
            return
        
        if self.checkIfTheTodolistExist(name) == False:
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} Todo List").format(name = name), 
                                                  _("Please enter a new name for {name} below.").format(name = name))
        
        if newname != "" and newname != None and topwindow:
            call = todosdb.renameTodolist(name, newname)
            self.listview.insertNames()
            
            if call:
                self.entry.setText(newname)
                
                QMessageBox.information(self, _("Successful"), _("{name} todo list renamed as {newname}.")
                                        .format(name = name, newname = newname))
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to rename {name} todo list.")
                                     .format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} todo list.")
                                 .format(name = name))


class TodosListView(QListView):
    """A list for showing todos' names."""
    
    def __init__(self, parent: TodosTabWidget, caller: str = "todos") -> None:
        """Init and then set properties.

        Args:
            parent (TodosTabWidget): "Todos" tab widget in main window
            caller (str, optional): For some special properties. Defaults to "todos".
        """
        
        super().__init__(parent)
        
        global todos_model1, todos_model2
        
        self.parent_ = parent
        self.caller = caller

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        if self.caller == "todos":  
            todos_model1 = QStringListModel(self)
            self.proxy.setSourceModel(todos_model1)
            
        elif self.caller == "home":
            todos_model2 = QStringListModel(self)
            self.proxy.setSourceModel(todos_model2)
        
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
        """
        Get and then return item text.

        Returns:
            str: Item text
        """
        
        try:
            return self.proxy.itemData(self.currentIndex())[0]
        except KeyError:
            return ""
        
    def insertNames(self) -> None:
        """Insert todo lists' names."""
        
        global menu_todos
        
        call = todosdb.getTodolists()
        names = []
        
        if self.caller == "todos":
            if not "menu_todos" in globals():
                menu_todos = todos_parent.menuBar().addMenu(_("todos"))
            
            menu_todos.clear()
            
            for name in call:
                names.append(name[0])
                menu_todos.addAction(name[0], lambda name = name: self.parent_.openCreate(name[0]))

        elif self.caller == "home":
            for name in call:
                names.append(name[0])
    
        try:
            todos_model1.setStringList(names)
        except NameError:
            pass
    
        try:
            todos_model2.setStringList(names)
        except NameError:
            pass
        
    def setFilter(self, text: str) -> None:
        """Set filtering proxy.

        Args:
            text (str): Filtering text
        """
        
        self.proxy.beginResetModel()
        self.proxy.setFilterFixedString(text)
        self.proxy.endResetModel()
    
        self.parent_.created.setText(_("Created: "))
        self.parent_.edited.setText(_("Edited: "))


class TodolistWidget(QWidget):
    """Page for todo lists."""
    
    def __init__(self, parent: TodosTabWidget, name: str) -> None:
        """Init and then set page.
        
        Args:
            parent (TodosTabWidget): "Todos" tab widget in main window
            name (str): Todo list name
        """
        
        self.parent_ = parent
        self.name = name
        
        call = todosdb.checkIfTheTodolistExist(name)
        
        if name != "main" and not call:
            call = todosdb.createTodolist(name)
            
            self.parent_.listview.insertNames()
            
            if not call:
                global todolists_widgets

                del todolists_widgets[name]
                
                QMessageBox.critical(parent, _("Error"), _("Failed to create todo list {name}.").format(name = name))

                return       
        
        super().__init__(parent)
        
        self.setLayout(QGridLayout(self))
        
        self.started = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
                              text=_('Started:'))
        self.completed = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
                                text=_("Completed:"))
        
        self.listview = TodolistListView()
        
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText(_("Enter a todo"))
        self.entry.setStatusTip(_("You can search in list while entering anythings in entry."))
        self.entry.setClearButtonEnabled(True)
        self.entry.textChanged.connect(self.listview.setFilter)
        
        self.comp_button = QPushButton(self, text=_("Make completed todo"))
        self.comp_button.clicked.connect(lambda: self.makeCompleted(self.entry.text(), 
                                                           datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
        self.uncomp_button = QPushButton(self, text=_("Make uncompleted todo"))
        self.uncomp_button.clicked.connect(lambda: self.makeUncompleted(self.entry.text()))
        
        self.add_button = QPushButton(self, text=_("Add todo"))
        self.add_button.clicked.connect(lambda: self.addTodo(self.entry.text(),
                                                         datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
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
        """
        Add a todo.

        Args:
            todo (str): Todo
        """
        
    def checkIfTheTodoExists(self, todo: str, mode: str = "normal") -> None:
        """
        Check if the todo exists.

        Args:
            todo (str): Todo
            mode (str, optional): Inverted mode for deleting etc. Defaults to "normal".
        """
        
        call = todosdb.checkIfTheTodoExist(self.name, todo)
        
        if call == False and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no todo called {todo}.").format(todo = todo))
        
        return call
    
    def insertInformations(self, todo: str) -> None:
        """Insert todo and creation, edit dates.

        Args:
            todo (str): Todo
        """
        
        if todo != "":
            call = todosdb.getTodoInformations(self.name, todo)
        else:
            call = None
            
        try:
            self.entry.setText(todo)
            self.started.setText(_("Started: ") + call[0])
            self.completed.setText(_("Completed: ") + call[1])
        except TypeError:
            self.entry.setText("")
            self.started.setText(_("Started: "))
            self.completed.setText(_("Completed: "))
            
    def deleteAll(self) -> None:
        """Delete all todos."""
        
    def deleteTodo(self, todo: str) -> None:
        """
        Delete a todo.

        Args:
            todo (str): Todo
        """
        
    def editTodo(self, todo: str) -> None:
        """
        Edit a todo.

        Args:
            todo (str): Todo
        """
        
    def makeCompleted(self, todo: str) -> None:
        """
        Make completed a todo.

        Args:
            todo (str): Todo
        """
        
    def makeUncompleted(self, todo: str) -> None:
        """
        Make uncompleted a todo.

        Args:
            todo (str): Todo
        """


class TodolistListView(QListView):
    

    def setFilter(self, text: str) -> None:
        """Set filtering proxy.

        Args:
            text (str): Filtering text
        """
        
        # self.proxy.beginResetModel()
        # self.proxy.setFilterFixedString(text)
        # self.proxy.endResetModel()
    
        # self.parent_.started.setText(_("Started: "))
        # self.parent_.completed.setText(_("Completed: "))