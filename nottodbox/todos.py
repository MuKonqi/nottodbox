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
        
    def addTodolist(self, name: str, created: str) -> bool:
        """
        Add a todolist.

        Args:
            name (str): Todolist name
            created (str): Creation date
            
        Returns:
            bool: True if successful, False if not
        """
        
        sql = f"insert into todolists (name, created, edited) values ('{name}', '{created}', '')"
        
        self.cur.execute(sql)
        self.db.commit()
        
        return self.checkIfTheTablesExists([name])
        
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
            name (str): Todolist name

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
                    name TEXT NOT NULL PRIMARY KEY 
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
        
    def recreateTable(self, table: str) -> bool:
        """
        Recreate a tables.

        Args:
            table (str): Table name

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{table}'")
        self.db.commit()
        
        call = self.checkIfTheTablesExists([table])
        
        if call:
            return False
        else:
            return self.createTables([table])
        
    def setMarkAsCompleted(self, todolist: str, todo: str) -> bool:
        """
        Set mark as completed a todo.

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
        
    def setMarkAsUncompleted(self, todolist: str, todo: str) -> bool:
        """
        Set mark as uncompleted a todo.

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

create_tables = todosdb.createTables(["todolist", "main"])
if create_tables:
    table = True
else:
    table = False


class TodosTabWidget(QTabWidget):
    pass


class TodosListView(QListView):
    pass


class TodoslistWidget(QWidget):
    pass


class TodolistListView(QListView):
    pass