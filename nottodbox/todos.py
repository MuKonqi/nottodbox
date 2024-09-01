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
from widgets.dialogs import ColorDialog
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QMouseEvent, QColor
from PyQt6.QtWidgets import *


todolists = {}


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"


class TodosDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}todos.db")
        self.cur = self.db.cursor()
        
    def checkIfTheTableExist(self, table: str) -> bool:
        try:
            self.cur.execute(f"select * from {table}")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def checkIfTheTodoExists(self, todolist: str, todo: str) -> bool:
        self.cur.execute(f"select * from '{todolist}' where todo = ?", (todo,))
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
    
    def checkIfTheTodolistExists(self, name: str) -> bool:
        self.cur.execute(f"select * from __main__ where name = ?", (name,))
        
        try:
            self.cur.fetchone()[0]
            return self.checkIfTheTableExist(name)
        
        except TypeError:
            return False
        
    def createTable(self, table: str) -> bool:
        if table == "__main__":
            sql = """
            CREATE TABLE IF NOT EXISTS __main__ (
                name TEXT NOT NULL PRIMARY KEY,
                creation TEXT NOT NULL,
                modification TEXT NOT NULL
            );"""
        
        else:
            sql = f"""
            CREATE TABLE IF NOT EXISTS '{table}' (
                todo TEXT NOT NULL PRIMARY KEY,
                status TEXT NOT NULL,
                creation TEXT NOT NULL,
                completion TEXT
            );"""
    
        self.cur.execute(sql)
        self.db.commit()
        
        return self.checkIfTheTableExist(table)
    
    def createTodo(self, todolist: str, todo: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute("update __main__ set modification = ? where name = ?", (date, todolist))
        self.db.commit()
        
        self.cur.execute(
            f"insert into '{todolist}' (todo, status, creation) values (?, ?, ?)",
            (todo, "uncompleted", date))
        self.db.commit()
        
        self.cur.execute(f"select * from '{todolist}' where todo = ?", (todo,))
        control = self.cur.fetchone()
        
        if control[0] == todo and control[1] == "uncompleted" and control[2] == date:
            return True
        else:
            return False
    
    def createTodolist(self, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute("insert into __main__ (name, creation, modification) values (?, ?, ?)", (name, date, ""))
        self.db.commit()
        
        return self.createTable(name)
    
    def deleteTodo(self, todolist: str, todo: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"delete from '{todolist}' where todo = ?", (todo,))
        self.db.commit()
        
        if not self.updateTodolistModificationDate(todolist, date):
            return False
        
        call = self.checkIfTheTodoExists(todolist, todo)
        
        if call:
            return False
        else:
            return True
        
    def deleteTodolist(self, name: str) -> bool:
        self.cur.execute(f"delete from __main__ where name = ?", (name,))
        self.db.commit()
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        call = self.checkIfTheTodolistExists(name)
        
        if call:
            return False
        else:
            return True
        
    def editTodo(self, todolist: str, todo: str, newtodo: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"update '{todolist}' set todo = ? where todo = ?", (newtodo, todo))
        self.db.commit()
        
        if not self.updateTodolistModificationDate(todolist, date):
            return False
        
        return self.checkIfTheTodoExists(todolist, newtodo)
    
    def getBackground(self, name: str) -> str | None:
        self.cur.execute(f"select background from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
        
    def getForeground(self, name: str) -> str | None:
        self.cur.execute(f"select foreground from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
    
    def getTodos(self, todolist: str) -> list:
        self.cur.execute(f"select todo, status from '{todolist}'")
        return self.cur.fetchall()
    
    def getTodolists(self) -> list:
        self.cur.execute(f"select name from __main__")
        return self.cur.fetchall()
    
    def getTodoInformations(self, todolist: str, todo: str) -> tuple:
        self.cur.execute(f"select status, creation, completion from '{todolist}' where todo = ?", (todo,))
        return self.cur.fetchone()
    
    def getTodolistInformations(self, name: str) -> tuple:
        self.cur.execute(f"select creation, modification from __main__ where name = ?", (name,))
        return self.cur.fetchone()
    
    def makeCompleted(self, todolist: str, todo: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"update '{todolist}' set status = ? where todo = ?", ("completed", todo))
        self.db.commit()
        
        if not self.updateTodolistModificationDate(todolist, date):
            return False
        
        self.cur.execute(f"select status from '{todolist}' where todo = ?", (todo,))
        control = self.cur.fetchone()
        
        if control[0] == "completed":
            return True
        else:
            return False
        
    def makeUncompleted(self, todolist: str, todo: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"update '{todolist}' set status = ? where todo = ?", ("uncompleted", todo))
        self.db.commit()
        
        if not self.updateTodolistModificationDate(todolist, date):
            return False
        
        self.cur.execute(f"select status from '{todolist}' where todo = ?", (todo,))
        control = self.cur.fetchone()
        
        if control[0] == "uncompleted":
            return True
        else:
            return False
        
    def resetNotebook(self, name: str) -> bool:
        self.cur.execute("delete from __main__ where name = ?", (name,))
        self.db.commit()
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        if not self.checkIfTheNotebookExists(name):
            return self.createNotebook(name)
        else:
            return False
        
    def renameTodolist(self, name: str, newname: str) -> bool:
        self.cur.execute(f"update __main__ set name = ? where name = ?", (newname, name))
        self.db.commit()
        
        self.cur.execute(f"ALTER TABLE '{name}' RENAME TO '{newname}'")
        self.db.commit()
        
        return self.checkIfTheTodolistExists(newname)
    
    def setBackground(self, name: str, color: str | None) -> bool:
        self.cur.execute("update __main__ set background = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getBackground(name)
        
        if call == color:
            return True
        else:
            return False
        
    def setForeground(self, name: str, color: str | None) -> bool:
        self.cur.execute("update __main__ set foreground = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getForeground(name)
        
        if call == color:
            return True
        else:
            return False
    
    def updateTodolistModificationDate(self, name: str, date: str) -> bool:
        if self.checkIfTheTableExists("__main__"):
            self.cur.execute("update __main__ set modification = ? where name = ?", (date, name))
            self.db.commit()
            
            self.cur.execute("select modification from __main__ where name = ?", (name,))
            
            try:
                fetch = self.cur.fetchone()[0]
                
                if fetch == date:
                    todolist_items[name][2].setText(date)
                    
                    return True
                
                else:
                    return False
        
            except TypeError or KeyError:
                return False
            
        else:
            return False


todosdb = TodosDB()
create_table = todosdb.createTable("__main__")
if not create_table:
    print("[2] Failed to create table")
    sys.exit(2)


class TodosTabWidget(QTabWidget): 
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        return
        
        global todos_parent
        
        todos_parent = parent
        self.todo = ""
        self.todolist = ""
        self.current_widget = None
        
        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self))
        
        self.treeview = TodosTreeView(self)
        
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText(_("Search in the list below"))
        self.entry.setClearButtonEnabled(True)
        self.entry.textChanged.connect(self.treeview.setFilter)

        self.todo_selected = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, text=_("Todo: "))
        self.todolist_selected = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, text=_("Todolist: "))
        
        self.todo_options = TodosTodoOptions(self)
        self.todo_options.setVisible(False)
        
        self.todolist_options = TodosTodolistOptions(self)
        self.todolist_selected.setVisible(False)

        self.none_options = TodosNoneOptions(self)
        
        self.current_widget = self.none_options
        
        self.home.layout().addWidget(self.entry, 0, 0, 1, 2)
        self.home.layout().addWidget(self.todo_selected, 1, 0, 1, 1)
        self.home.layout().addWidget(self.todolist_selected, 1, 1, 1, 1)
        self.home.layout().addWidget(self.none_options, 1, 2, 2, 1)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
         
    def closeTab(self, index: int) -> None:
        if index != self.indexOf(self.home):           
            del todolists[self.tabText(index).replace("&", "")]
            
            todos_parent.dock.widget().removePage(self.tabText(index).replace("&", ""), self)
            self.removeTab(index)
            
    def insertInformations(self, todolist: str, todo: str) -> None:
        self.todolist = todolist
        self.todo = todo      
        
        self.none_options.setVisible(False)
        self.todolist_options.setVisible(False)
        self.todo_options.setVisible(False)
        
        if self.todolist == "":
            self.none_options.setVisible(True)
            self.home.layout().replaceWidget(self.current_widget, self.none_options)
            
            self.current_widget = self.none_options
            
        elif self.todolist != "" and self.todo == "":
            self.todolist_options.setVisible(True)
            self.home.layout().replaceWidget(self.current_widget, self.todolist_options)
            
            self.current_widget = self.todolist_options
            
        elif self.todolist != "" and self.todo != "":
            self.todo_options.setVisible(True)
            self.home.layout().replaceWidget(self.current_widget, self.todo_options)
            
            self.current_widget = self.todo_options
            
        self.todolist_selected.setText(_("Todolist: ") + todolist)
        self.todo_selected.setText(_("Todo: ") + todo)
            
            
class TodosNoneOptions(QWidget):
    def __init__(self, parent: TodosTabWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.warning_label = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                                    text=_("You can select\na todo list or a todo\non the left."))
        self.warning_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.create_todolist = QPushButton(self, text=_("Create todo list"))
        self.create_todolist.clicked.connect(self.parent_.todolist_options.createTodolist)
        
        self.delete_all = QPushButton(self, text=_("Delete all"))
        self.delete_all.clicked.connect(self.parent_.todolist_options.deleteAll)
        
        self.setLayout(QVBoxLayout(self))
        self.setFixedWidth(160)
        
        self.layout().addWidget(self.warning_label)
        self.layout().addWidget(self.create_todolist)
        self.layout().addWidget(self.delete_all)
        
        
class TodosTodolistOptions(QWidget):
    def __init__(self, parent: TodosTabWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.create_todo = QPushButton(self, text=_("Create todo"))
        self.create_todo.clicked.connect(self.parent_.todo_options.createTodo)
        
        self.create_todolist = QPushButton(self, text=_("Create todo list"))
        self.create_todolist.clicked.connect(self.createTodolist)
        
        self.open_todolist = QPushButton(self, text=_("Open todo list"))
        self.open_todolist.clicked.connect(self.openTodolist)
        
        self.rename_todolist = QPushButton(self, text=_("Rename todo list"))
        self.rename_todolist.clicked.connect(self.renameTodolist)
        
        self.reset_todolist = QPushButton(self, text=_("Reset todo list"))
        self.reset_todolist.clicked.connect(self.resetTodolist)
        
        self.delete_todolist = QPushButton(self, text=_("Delete todo list"))
        self.delete_todolist.clicked.connect(self.deleteTodolist)
        
        self.set_background = QPushButton(self, text=_("Set background"))
        self.set_background.clicked.connect(self.setBackground)
        
        self.set_foreground = QPushButton(self, text=_("Set foreground"))
        self.set_foreground.clicked.connect(self.setForeground)
        
        self.delete_all = QPushButton(self, text=_("Delete all"))
        self.delete_all.clicked.connect(self.deleteAll)
        
        self.setLayout(QVBoxLayout(self))
        self.setFixedWidth(160)
        
        self.layout().addWidget(self.create_todo)
        self.layout().addWidget(self.create_todolist)
        self.layout().addWidget(self.open_todolist)
        self.layout().addWidget(self.rename_todolist)
        self.layout().addWidget(self.reset_todolist)
        self.layout().addWidget(self.delete_todolist)
        self.layout().addWidget(self.set_background)
        self.layout().addWidget(self.set_foreground)
        self.layout().addWidget(self.delete_all)
        
    def checkIfTheTodolistExists(self, name: str, mode: str = "normal") -> None:
        call = todosdb.checkIfTheTodolistExists(name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no todo list called {name}.").format(name = name))
        
        return call
    
    def createTodolist(self) -> None:
        name, topwindow = QInputDialog.getText(self, _("Type a Name"), _("Type a name for creating a todo list."))
        
        if "@" in name or "'" in name:
            QMessageBox.critical(self, _("Error"), _("The todo list name can not contain that character: '"))
            
            return
        
        elif name != "" and name != None and topwindow:
            call = self.checkIfTheTodolistExists(name, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{name} todo list already created.").format(name = name))
        
            else:
                call = todosdb.createTodolist(name)
                
                if call:
                    self.parent_.treeview.appendTodolist(name)
                    self.parent_.insertInformations(name, "")
                    
                    QMessageBox.information(self, _("Successful"), _("{name} todo list created.").format(name = name))
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} todo list.").format(name = name))
            
    def deleteAll(self) -> None:
        call = todosdb.recreateTable("__main__")
    
        if call:
            self.parent_.treeview.updateAll()
            self.parent_.insertInformations("", "")
            
            QMessageBox.information(self, _("Successful"), _("All todo lists deleted."))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all todo lists."))
                       
    def deleteTodolist(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        call = todosdb.deleteTodolist(name)
            
        if call:
            self.parent_.treeview.deleteTodolist(name)
            self.parent_.insertInformations("", "")
            
            QMessageBox.information(self, _("Successful"), _("{name} todo list deleted.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {name} todo list.").format(name = name))
        
    def openTodolist(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        # todos_parent.tabwidget.setCurrentIndex(2)
        
        # if name == "main":
        #     self.setCurrentWidget(self.home)
        #     return
        
        # if name in todolists:
        #     self.setCurrentWidget(todolists[name])
            
        # else:
        #     todos_parent.dock.widget().addPage(name, self)
        #     todolists[name] = TodolistWidget(self, name)
        #     self.addTab(todolists[name], name)
        #     self.setCurrentWidget(todolists[name])
    
    def renameTodolist(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} Todo List").format(name = name), 
                                                  _("Please enter a new name for {name} below.").format(name = name))
        
        if newname != "" and newname != None and topwindow:
            call = todosdb.renameTodolist(name, newname)
            
            if call:
                self.insertInformations(newname, "")
                self.parent_.treeview.updateTodolist(name, newname)
                
                QMessageBox.information(self, _("Successful"), _("{name} todo list renamed as {newname}.")
                                        .format(name = name, newname = newname))
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to rename {name} todo list.")
                                     .format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} todo list.")
                                 .format(name = name))
            
    def resetTodolist(self) -> None:
        name = self.parent_.todo
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        call = todosdb.resetTodolist(name)
        
        if call:
            self.parent_.treeview.deleteTodolist(name)
            self.parent_.treeview.appendTodolist(name)
            self.parent_.insertInformations(name, "")
            
            QMessageBox.information(self, _("Successful"), _("{name} todo list reset.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset {name} todo list.").format(name = name))
            
    def setBackground(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        background = todosdb.getBackground(name)
        
        status, qcolor = ColorDialog(QColor(background), self, _("Select color").format(name = name)).getColor()
        
        if status == "ok":
            if qcolor.isValid():
                color = qcolor.name()
            else:
                color = ""
            
            call = todosdb.setBackground(name, color)

            if call:
                self.parent_.treeview.updateBackground(name, color)
                
                if qcolor.isValid():
                    QMessageBox.information(self, _("Successful"), _("Background color setted to {color} for {name} todo list.").format(color = color, name = name))
                else:
                    QMessageBox.information(self, _("Successful"), _("Background color setted to default for {name} todo list.").format(name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {name} todo list.").format(name = name))
        
    def setForeground(self) -> None:
        name = self.parent_.todolist

        if not self.checkIfTheTodolistExists(name):
            return
        
        foreground = todosdb.getForeground(name)
        
        status, qcolor = ColorDialog(QColor(foreground), self, _("Select color").format(name = name)).getColor()
        
        if status == "ok":
            if qcolor.isValid():
                color = qcolor.name()
            else:
                color = ""
            
            call = todosdb.setForeground(name, color)
                
            if call:
                self.parent_.treeview.updateForeground(name, color)
                
                if qcolor.isValid():
                    QMessageBox.information(self, _("Successful"), _("Foreground color setted to {color} for {name} todo list.").format(color = color, name = name))
                else:
                    QMessageBox.information(self, _("Successful"), _("Foreground color setted to default for {name} todo list.").format(name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set foreground color for {name} todo list.").format(name = name))

        
class TodosTodoOptions(QWidget):
    def __init__(self, parent: TodosTabWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.create_todo = QPushButton(self, text=_("Create todo"))
        self.create_todo.clicked.connect(self.createTodo)
        
        self.make_completed = QPushButton(self, text=_("Make completed"))
        self.make_completed.clicked.connect(self.makeCompleted)
        
        self.make_uncompleted = QPushButton(self, text=_("Make uncompleted"))
        self.make_uncompleted.clicked.connect(self.makeUncompleted)
        
        self.edit_todo = QPushButton(self, text=_("Edit todo"))
        self.edit_todo.clicked.connect(self.editTodo)
        
        self.delete_todo = QPushButton(self, text=_("Delete todo"))
        self.delete_todo.clicked.connect(self.deleteTodo)
        
        self.setLayout(QVBoxLayout(self))
        self.setFixedWidth(160)
        
        self.layout().addWidget(self.create_todo)
        self.layout().addWidget(self.make_completed)
        self.layout().addWidget(self.make_uncompleted)
        self.layout().addWidget(self.edit_todo)
        self.layout().addWidget(self.delete_todo)
        
    def checkIfTheTodoExist(self, todolist: str, todo: str, mode: str) -> bool:
        call = todosdb.checkIfTheTodoExists(todolist, todo)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no todo called {todo}.").format(todo = todo))
        
        return call
    
    def createTodo(self) -> None:
        todolist = self.parent_.todolist
        
        if not todosdb.checkIfTheTodolistExists(todolist):
            QMessageBox.critical(self, _("Error"), _("There is no todo list called {name}.").format(name = todolist))
            return
        
        todo, topwindow = QInputDialog.getText(self, _("Type a Name"), _("Type a name for creating a todo."))
        
        if "@" in todo:
            QMessageBox.critical(self, _("Error"), _('The todo can not contain @ character.'))
            return
        
        elif todo != "" and todo != None and topwindow:
            call = self.checkIfTheTodoExist(todolist, todo, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{todo} todo already created.").format(todo = todo))
        
            else:
                call = todosdb.createTodo(todolist, todo)
                
                if call:
                    self.parent_.treeview.appendTodo(todolist, todo)
                    self.parent_.insertInformations(todolist, todo)
                    
                    QMessageBox.information(self, _("Successful"), _("{name} todo created.").format(todo = todo))
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} todo.").format(todo = todo))
                    
    def deleteTodo(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo
        
        if todolist == "" or todolist == None or todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _("Please select a todo."))
            return
        
        if not self.checkIfTheTodoExist(todolist, todo):
            return
        
        call = todosdb.deleteTodo(todolist, todo)
            
        if call:
            self.parent_.treeview.deleteTodo(todolist, todo)
            self.parent_.insertInformations(todolist, "")
            
            QMessageBox.information(self, _("Successful"), _("{todo} todo deleted.").format(todo = todo))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {todo} todo.").format(todo = todo))
                    
    def editTodo(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo
        
        if todolist == "" or todo == None or todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _("Please select a todo."))
            return
        
        if not self.checkIfTheTodoExist(todolist, todo):
            return
        
        newtodo, topwindow = QInputDialog.getText(self, 
                                                  _("Edit {todo} todo").format(todo = todo), 
                                                  _("Please enter anything for edtiging {todo} todo below.").format(todo = todo))
        
        if newtodo != "" and newtodo != None and topwindow:
            if not self.checkIfTheTodoExist(todolist, newtodo, "no-popup"):
                call = todosdb.editTodo(todolist, todo, newtodo)

                if call:
                    self.parent_.treeview.updateTodo(todolist, todo, newtodo)
                    self.parent_.insertInformations(todo, newtodo)
                    
                    QMessageBox.information(self, _("Successful"), _("{todo} todo edited as {newtodo}.")
                                            .format(todo = todo, newname = newtodo))
    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to edit {todo} todo.")
                                        .format(todo = todo))
            
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newtodo} todo, editing {todo} todo cancalled.")
                                     .format(newtodo = newtodo, todo = todo))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to edit {todo} todo.")
                                 .format(todo = todo))
            
    def makeCompleted(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo
        
        if todolist == "" or todo == None or todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _("Please select a todo."))
            return
        
        if not self.checkIfTheTodoExist(todolist, todo):
            return
        
        call = todosdb.makeCompleted(todolist, todo)
        
        if call:
            self.parent_.treeview.updateTodo(todolist, todo)
            self.parent_.insertInformations(todolist, todo)
            
            QMessageBox.information(self, _("Successful"), _("{todo} maded completion.").format(todo = todo))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to make {todo} completion.").format(todo = todo))
        
    def makeUncompleted(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo
        
        if todolist == "" or todo == None or todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _("Please select a todo."))
            return
        
        if not self.checkIfTheTodoExist(todolist, todo):
            return
        
        call = todosdb.makeUncompleted(todolist, todo)
        
        if call:
            self.parent_.treeview.updateTodo(todolist, todo)
            self.parent_.insertInformations(todolist, todo)
            
            QMessageBox.information(self, _("Successful"), _("{todo} maded uncompleted.").format(todo = todo))

        else:
            QMessageBox.critical(self, _("Error"), _("Failed to make {todo} uncompleted.").format(todo = todo))