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
from settings import settingsdb
from gettext import gettext as _
from widgets.dialogs import ColorDialog
from widgets.other import HSeperator, Label, PushButton, VSeperator
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItem, QStandardItemModel, QMouseEvent, QColor
from PySide6.QtWidgets import *


todo_counts = {}
todo_items = {}
todolist_counts = {}
todolist_items = {}
todolist_menus = {}

username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"

setting_background, setting_foreground = settingsdb.getModuleSettings("todos")


class TodosDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}todos.db")
        self.cur = self.db.cursor()
        
    def checkIfTheTableExists(self, table: str) -> bool:
        try:
            self.cur.execute(f"select * from '{table}'")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def checkIfTheTodoExists(self, todolist: str, todo: str) -> bool:
        if self.checkIfTheTodolistExists(todolist):
            self.cur.execute(f"select * from '{todolist}' where todo = ?", (todo,))
            
            try:
                self.cur.fetchone()[0]
                return True
            
            except TypeError:
                return False
            
        else:
            return False
    
    def checkIfTheTodolistExists(self, name: str) -> bool:
        self.cur.execute(f"select * from __main__ where name = ?", (name,))
        
        try:
            self.cur.fetchone()[0]
            return self.checkIfTheTableExists(name)
        
        except TypeError:
            return False
        
    def createMainTable(self) -> bool:
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS __main__ (
            name TEXT NOT NULL PRIMARY KEY,
            creation TEXT NOT NULL,
            modification TEXT NOT NULL,
            background TEXT NOT NULL,
            foreground TEXT NOT NULL
        );""")
        self.db.commit()
        
        return self.checkIfTheTableExists("__main__")
    
    def createTodo(self, todolist: str, todo: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute("update __main__ set modification = ? where name = ?", (date, todolist))
        self.db.commit()
        
        self.cur.execute(f"""insert into '{todolist}' 
                         (todo, status, creation, background, foreground) values (?, ?, ?, ?, ?)""",
                         (todo, "uncompleted", date, "global", "global"))
        self.db.commit()
        
        self.cur.execute(f"select * from '{todolist}' where todo = ?", (todo,))
        control = self.cur.fetchone()
        
        if control[0] == todo and control[1] == "uncompleted" and control[2] == date:
            return True
        else:
            return False
    
    def createTodolist(self, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(
            """insert into __main__ (name, creation, modification, background, foreground) 
            values (?, ?, ?, ?, ?)""", (name, date, date, "global", "global"))
        self.db.commit()
            
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS '{name}' (
                todo TEXT NOT NULL PRIMARY KEY,
                status TEXT NOT NULL,
                creation TEXT NOT NULL,
                completion TEXT,
                background TEXT NOT NULL,
                foreground TEXT NOT NULL
            );""")
        self.db.commit()
        
        return self.checkIfTheTodolistExists(name)
    
    def deleteAll(self) -> bool:
        successful = True
        calls = {}
        
        self.cur.execute("select name from __main__")
        parents = self.cur.fetchall()
        
        for todolist in parents:
            todolist = todolist[0]
            
            calls[todolist] = self.deleteTodolist(todolist)
            
            if not calls[todolist]:
                successful = False
        
        if successful:
            self.cur.execute("DROP TABLE IF EXISTS __main__")
            self.db.commit()
            
            if not self.checkIfTheTableExists("__main__"):
                return self.createMainTable()
            else:
                return False

        else:
            return False
    
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
    
    def getAll(self) -> dict:
        all = {}
        
        self.cur.execute("""select name, creation, modification, 
                         background, foreground from __main__""")
        parents = self.cur.fetchall()
        
        for todolist, creation, modification, background, foreground in parents:
            self.cur.execute(f"""select todo, status, creation, completion, 
                             background, foreground from '{todolist}'""")
            all[(todolist, creation, modification, background, foreground)] = self.cur.fetchall()
            
        return all
        
    def getStatus(self, todolist: str, todo: str) -> str:
        self.cur.execute(f"select status from '{todolist}' where todo = ?", (todo,))
        return self.cur.fetchone()[0]
    
    def getTodo(self, todolist: str, todo: str) -> list:
        self.cur.execute(f"""select status, creation, completion,
                         background, foreground from '{todolist}' where todo = ?""", (todo,))
        return self.cur.fetchone()
    
    def getTodoBackground(self, todolist: str, todo: str) -> str:
        self.cur.execute(f"select background from '{todolist}' where todo = ?", (todo,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
        
    def getTodoForeground(self, todolist: str, todo: str) -> str:
        self.cur.execute(f"select foreground from '{todolist}' where todo = ?", (todo,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getTodolist(self, name: str) -> tuple:
        self.cur.execute(f"""select creation, modification, 
                         background, foreground from __main__ where name = ?""", (name,))
        creation, modification, background, foreground = self.cur.fetchone()
        
        self.cur.execute(f"""select todo, status, creation, completion,
                         background, foreground from '{name}'""")
        return creation, modification, background, foreground, self.cur.fetchall()
    
    def getTodolistBackground(self, name: str) -> str:
        self.cur.execute(f"select background from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
        
    def getTodolistForeground(self, name: str) -> str:
        self.cur.execute(f"select foreground from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
        
    def resetTodolist(self, name: str) -> bool:
        self.cur.execute("delete from __main__ where name = ?", (name,))
        self.db.commit()
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        if not self.checkIfTheTodolistExists(name):
            return self.createTodolist(name)
        else:
            return False
        
    def renameTodolist(self, name: str, newname: str) -> bool:
        self.cur.execute(f"update __main__ set name = ? where name = ?", (newname, name))
        self.db.commit()
        
        self.cur.execute(f"ALTER TABLE '{name}' RENAME TO '{newname}'")
        self.db.commit()
        
        return self.checkIfTheTodolistExists(newname)
    
    def setTodoBackground(self, todolist: str, todo: str, color: str) -> bool:
        self.cur.execute(f"update '{todolist}' set background = ? where todo = ?", (color, todo))
        self.db.commit()
        
        call = self.getTodoBackground(todolist, todo)
        
        if call == color:
            return True
        else:
            return False
        
    def setTodoForeground(self, todolist: str, todo: str, color: str) -> bool:
        self.cur.execute(f"update '{todolist}' set foreground = ? where todo = ?", (color, todo))
        self.db.commit()
        
        call = self.getTodoForeground(todolist, todo)
        
        if call == color:
            return True
        else:
            return False
    
    def setTodolistBackground(self, name: str, color: str) -> bool:
        self.cur.execute("update __main__ set background = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getTodolistBackground(name)
        
        if call == color:
            return True
        else:
            return False
        
    def setTodolistForeground(self, name: str, color: str) -> bool:
        self.cur.execute("update __main__ set foreground = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getTodolistForeground(name)
        
        if call == color:
            return True
        else:
            return False
        
    def changeStatus(self, todolist: str, todo: str) -> tuple:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        status = self.getStatus(todolist, todo)
        
        if status == "completed":
            newstatus = "uncompleted"
        
        elif status == "uncompleted": 
            newstatus = "completed"
            
        self.cur.execute(f"update '{todolist}' set status = ? where todo = ?", (newstatus, todo))
        self.db.commit()
        
        if not self.updateTodolistModificationDate(todolist, date):
            return False
        
        self.cur.execute(f"select status from '{todolist}' where todo = ?", (todo,))
        control = self.cur.fetchone()[0]
        
        if control == newstatus:
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
create_table = todosdb.createMainTable()
if not create_table:
    print("[2] Failed to create table")
    sys.exit(2)


class TodosWidget(QWidget): 
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        
        global todos_parent
        
        todos_parent = parent
        self.todo = ""
        self.todolist = ""
        self.current_widget = None
        
        todos_parent.menuBar().addAction(_("To-dos"), lambda: todos_parent.tabwidget.setCurrentIndex(2))
        
        self.layout_ = QGridLayout(self)
        
        self.selecteds = QWidget(self)
        self.selecteds_layout = QHBoxLayout(self.selecteds)
        
        self.todo_selected = Label(self, _("To-do: "))
        self.todolist_selected = Label(self, _("To-do list: "))
        
        self.treeview = TodosTreeView(self)
        
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText(_("Search in the list below"))
        self.entry.setClearButtonEnabled(True)
        self.entry.textChanged.connect(self.treeview.setFilter)
        
        self.todo_options = TodosTodoOptions(self)
        self.todo_options.setVisible(False)
        
        self.todolist_options = TodosTodolistOptions(self)
        self.todolist_options.setVisible(False)

        self.none_options = TodosNoneOptions(self)
        
        self.current_widget = self.none_options
        
        self.selecteds.setLayout(self.selecteds_layout)
        self.selecteds_layout.addWidget(self.todolist_selected)
        self.selecteds_layout.addWidget(self.todo_selected)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.selecteds, 0, 0, 1, 3)
        self.layout_.addWidget(HSeperator(self), 1, 0, 1, 3)
        self.layout_.addWidget(self.entry, 2, 0, 1, 1)
        self.layout_.addWidget(self.treeview, 3, 0, 1, 1)
        self.layout_.addWidget(VSeperator(self), 2, 1, 2, 1)
        self.layout_.addWidget(self.none_options, 2, 2, 2, 1)
            
    def insertInformations(self, todolist: str, todo: str) -> None:
        self.todolist = todolist
        self.todo = todo      
        
        self.none_options.setVisible(False)
        self.todolist_options.setVisible(False)
        self.todo_options.setVisible(False)
        
        if self.todolist == "":
            self.none_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.none_options)
            
            self.current_widget = self.none_options
            
        elif self.todolist != "" and self.todo == "":
            self.todolist_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.todolist_options)
            
            self.current_widget = self.todolist_options
            
        elif self.todolist != "" and self.todo != "":
            self.todo_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.todo_options)
            
            self.current_widget = self.todo_options
            
        self.todolist_selected.setText(_("To-do list: ") + todolist)
        self.todo_selected.setText(_("To-do: ") + todo)
        
    def refreshSettings(self) -> None:
        global setting_background, setting_foreground
        
        setting_background, setting_foreground = settingsdb.getModuleSettings("todos")
            
            
class TodosNoneOptions(QWidget):
    def __init__(self, parent: TodosWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.warning_label = Label(self, _("You can select\na to-do list\nor a to-do\non the left."))
        self.warning_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.create_todolist = PushButton(self, _("Create to-do list"))
        self.create_todolist.clicked.connect(self.parent_.todolist_options.createTodolist)
        
        self.delete_all = PushButton(self, _("Delete all"))
        self.delete_all.clicked.connect(self.parent_.todolist_options.deleteAll)
        
        self.setFixedWidth(180)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.warning_label)
        self.layout_.addWidget(self.create_todolist)
        self.layout_.addWidget(self.delete_all)
        
        
class TodosTodolistOptions(QWidget):
    def __init__(self, parent: TodosWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.create_todo = PushButton(self, _("Create todo"))
        self.create_todo.clicked.connect(self.parent_.todo_options.createTodo)
        
        self.create_todolist = PushButton(self, _("Create to-do list"))
        self.create_todolist.clicked.connect(self.createTodolist)
        
        self.set_background = PushButton(self, _("Set background color"))
        self.set_background.clicked.connect(self.setTodolistBackground)
        
        self.set_foreground = PushButton(self, _("Set text color"))
        self.set_foreground.clicked.connect(self.setTodolistForeground)
        
        self.rename_todolist = PushButton(self, _("Rename to-do list"))
        self.rename_todolist.clicked.connect(self.renameTodolist)
        
        self.reset_todolist = PushButton(self, _("Reset to-do list"))
        self.reset_todolist.clicked.connect(self.resetTodolist)
        
        self.delete_todolist = PushButton(self, _("Delete to-do list"))
        self.delete_todolist.clicked.connect(self.deleteTodolist)
        
        self.delete_all = PushButton(self, _("Delete all"))
        self.delete_all.clicked.connect(self.deleteAll)
        
        self.setFixedWidth(180)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.create_todo)
        self.layout_.addWidget(self.create_todolist)
        self.layout_.addWidget(self.set_background)
        self.layout_.addWidget(self.set_foreground)
        self.layout_.addWidget(self.rename_todolist)
        self.layout_.addWidget(self.reset_todolist)
        self.layout_.addWidget(self.delete_todolist)
        self.layout_.addWidget(self.delete_all)
        
    def checkIfTheTodolistExists(self, name: str, mode: str = "normal") -> None:
        call = todosdb.checkIfTheTodolistExists(name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no to-do list called {name}.").format(name = name))
        
        return call
    
    def createTodolist(self) -> None:
        name, topwindow = QInputDialog.getText(
            self, _("Create To-do List"), _("Please enter a name for creating a to-do list."))
        
        if "'" in name or "@" in name:
            QMessageBox.critical(self, _("Error"), _("The to-do list name can not contain these characters: ' and @"))
            return
        
        elif "__main__" == name:
            QMessageBox.critical(self, _("Error"), _("The to-do list name can not be to __main__."))
            return
        
        elif topwindow and name != "":
            call = self.checkIfTheTodolistExists(name, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{name} to-do list already created.").format(name = name))
        
            else:
                call = todosdb.createTodolist(name)
                
                if call:
                    self.parent_.treeview.appendTodolist(name)
                    self.parent_.insertInformations(name, "")
                    
                    QMessageBox.information(self, _("Successful"), _("{name} to-do list created.").format(name = name))
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} to-do list.").format(name = name))
            
    def deleteAll(self) -> None:
        call = todosdb.deleteAll()
    
        if call:
            self.parent_.treeview.updateAll()
            self.parent_.insertInformations("", "")
            
            QMessageBox.information(self, _("Successful"), _("All to-do lists deleted."))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all to-do lists."))
                       
    def deleteTodolist(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        call = todosdb.deleteTodolist(name)
            
        if call:
            self.parent_.treeview.deleteTodolist(name)
            self.parent_.insertInformations("", "")
            
            QMessageBox.information(self, _("Successful"), _("{name} to-do list deleted.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {name} to-do list.").format(name = name))
    
    def renameTodolist(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} To-do List").format(name = name.title()), 
                                                  _("Please enter a new name for {name} to-do list.").format(name = name))
        
        if "'" in newname or "@" in newname:
            QMessageBox.critical(self, _("Error"), _("The to-do list name can not contain these characters: ' and @"))
            return
        
        elif "__main__" == newname:
            QMessageBox.critical(self, _("Error"), _("The to-do list name can not be to __main__."))
            return
        
        elif topwindow and newname != "":
            if not self.checkIfTheTodolistExists(newname, "no-popup"):
                call = todosdb.renameTodolist(name, newname)
                
                if call:
                    self.insertInformations(newname, "")
                    self.parent_.treeview.updateTodolist(name, newname)
                    
                    QMessageBox.information(self, _("Successful"), _("{name} to-do list renamed as {newname}.")
                                            .format(name = name, newname = newname))
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to rename {name} to-do list.")
                                        .format(name = name))
                    
            else:
                QMessageBox.critical(self, _("Error"), _("{newname} to-do list already created."))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} to-do list.")
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
            
            QMessageBox.information(self, _("Successful"), _("{name} to-do list reset.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset {name} to-do list.").format(name = name))
            
    def setTodolistBackground(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        background = todosdb.getTodolistBackground(name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(background if background != "global" and background != "default"
                   else (setting_background if background == "global" and setting_background != "default" 
                         else "#FFFFFF")),
            _("Select Background Color for {name} To-do List").format(name = name.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = todosdb.setTodolistBackground(name, color)
                    
            if call:
                self.parent_.treeview.updateTodolistBackground(name, color)
                
                QMessageBox.information(
                    self, _("Successful"), _("Background color setted to {color} for {name} to-do list.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {name} to-do list.").format(name = name))
        
    def setTodolistForeground(self) -> None:
        name = self.parent_.todolist

        if not self.checkIfTheTodolistExists(name):
            return
        
        foreground = todosdb.getTodolistForeground(name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(foreground if foreground != "global" and foreground != "default"
                   else (setting_foreground if foreground == "global" and setting_foreground != "default" 
                         else "#FFFFFF")),
            _("Select Text Color for {name} To-do List").format(name = name.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = todosdb.setTodolistForeground(name, color)
                    
            if call:
                self.parent_.treeview.updateTodolistForeground(name, color)
                
                QMessageBox.information(
                    self, _("Successful"), _("Text color setted to {color} for {name} to-do list.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set text color for {name} to-do list.").format(name = name))

        
class TodosTodoOptions(QWidget):
    def __init__(self, parent: TodosWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.create_todo = PushButton(self, _("Create todo"))
        self.create_todo.clicked.connect(self.createTodo)
        
        self.set_background = PushButton(self, _("Set background color"))
        self.set_background.clicked.connect(self.setTodoBackground)
        
        self.set_foreground = PushButton(self, _("Set text color"))
        self.set_foreground.clicked.connect(self.setTodoForeground)
        
        self.change_status = PushButton(self, _("Change status"))
        self.change_status.clicked.connect(self.changeStatus)
        
        self.edit_todo = PushButton(self, _("Edit todo"))
        self.edit_todo.clicked.connect(self.editTodo)
        
        self.delete_todo = PushButton(self, _("Delete todo"))
        self.delete_todo.clicked.connect(self.deleteTodo)
        
        self.setFixedWidth(180)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.create_todo)
        self.layout_.addWidget(self.set_background)
        self.layout_.addWidget(self.set_foreground)
        self.layout_.addWidget(self.change_status)
        self.layout_.addWidget(self.edit_todo)
        self.layout_.addWidget(self.delete_todo)
        
    def checkIfTheTodoExists(self, todolist: str, todo: str, mode: str = "normal") -> bool:
        call = todosdb.checkIfTheTodoExists(todolist, todo)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no to-do called {todo}.").format(todo = todo))
        
        return call
    
    def changeStatus(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo
        
        if not self.checkIfTheTodoExists(todolist, todo):
            return
        
        call = todosdb.changeStatus(todolist, todo)
        
        if call:
            self.parent_.treeview.updateTodo(todolist, todo, todo)
            
            QMessageBox.information(self, _("Successful"), _("{todo} todo's status changed.").format(todo = todo))
    
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to change {todo}'s status.").format(todo = todo))
    
    def createTodo(self) -> None:
        todolist = self.parent_.todolist
        
        if not todosdb.checkIfTheTodolistExists(todolist):
            QMessageBox.critical(self, _("Error"), _("There is no to-do list called {name}.").format(name = todolist))
            return
        
        todo, topwindow = QInputDialog.getText(
            self, _("Create To-do"), _("Please enter anything for creating a to-do."))
        
        if topwindow and todo != "":
            call = self.checkIfTheTodoExists(todolist, todo, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{todo} to-do already created.").format(todo = todo))
        
            else:
                call = todosdb.createTodo(todolist, todo)
                
                if call:
                    self.parent_.treeview.appendTodo(todolist, todo)
                    self.parent_.insertInformations(todolist, todo)
                    
                    QMessageBox.information(self, _("Successful"), _("{todo} to-do created.").format(todo = todo))
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {todo} to-do.").format(todo = todo))
                    
    def deleteTodo(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo
        
        if not self.checkIfTheTodoExists(todolist, todo):
            return
        
        call = todosdb.deleteTodo(todolist, todo)
            
        if call:
            self.parent_.treeview.deleteTodo(todolist, todo)
            self.parent_.insertInformations(todolist, "")
            
            QMessageBox.information(self, _("Successful"), _("{todo} to-do deleted.").format(todo = todo))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {todo} to-do.").format(todo = todo))
                    
    def editTodo(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo
        
        if not self.checkIfTheTodoExists(todolist, todo):
            return
        
        newtodo, topwindow = QInputDialog.getText(self, 
                                                  _("Edit {todo} To-do").format(todo = todo.title()), 
                                                  _("Please enter anything for editing {todo} to-do.").format(todo = todo))
        
        if topwindow and newtodo != "":
            if not self.checkIfTheTodoExists(todolist, newtodo, "no-popup"):
                call = todosdb.editTodo(todolist, todo, newtodo)

                if call:
                    self.parent_.treeview.updateTodo(todolist, todo, newtodo)
                    self.parent_.insertInformations(todolist, newtodo)
                    
                    QMessageBox.information(self, _("Successful"), _("{todo} to-do edited as {newtodo}.")
                                            .format(todo = todo, newtodo = newtodo))
    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to edit {todo} to-do.")
                                        .format(todo = todo))
            
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newtodo} todo, editing {todo} to-do cancalled.")
                                     .format(newtodo = newtodo, todo = todo))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to edit {todo} to-do.")
                                 .format(todo = todo))
            
    def setTodoBackground(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo
        
        if not self.checkIfTheTodoExists(todolist, todo):
            return
        
        background = todosdb.getTodoBackground(todolist, todo)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(background if background != "global" and background != "default"
                   else (setting_background if background == "global" and setting_background != "default" 
                         else "#FFFFFF")),
            _("Select Background Color for {todo} To-do").format(todo = todo.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = todosdb.setTodoBackground(todolist, todo, color)
                    
            if call:
                self.parent_.treeview.updateTodoBackground(todolist, todo, color)
                
                QMessageBox.information(
                    self, _("Successful"), _("Background color setted to {color} for {todo} to-do.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), todo = todo))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {todo} to-do.").format(todo = todo))
        
    def setTodoForeground(self) -> None:
        todolist = self.parent_.todolist
        todo = self.parent_.todo

        if not self.checkIfTheTodoExists(todolist, todo):
            return
        
        foreground = todosdb.getTodoForeground(todolist, todo)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(foreground if foreground != "global" and foreground != "default"
                   else (setting_foreground if foreground == "global" and setting_foreground != "default" 
                         else "#FFFFFF")),
            _("Select Text Color for {todo} To-do").format(todo = todo.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = todosdb.setTodoForeground(todolist, todo, color)
                    
            if call:
                self.parent_.treeview.updateTodoForeground(todolist, todo, color)
                
                QMessageBox.information(
                    self, _("Successful"), _("Text color setted to {color} for {todo} to-do.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), todo = todo))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set text color for {todo} to-do.").format(todo = todo))
            
            
class TodosTreeView(QTreeView):
    def __init__(self, parent: TodosWidget, caller: str = "todos") -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.caller = caller

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setRecursiveFilteringEnabled(True)
        
        if self.caller == "todos":
            global todos_model
            
            todos_model = QStandardItemModel(self)
            todos_model.setHorizontalHeaderLabels([_("Name"), _("Creation"), _("Modification / Completion")])
            
        self.proxy.setSourceModel(todos_model)
        
        self.setModel(self.proxy)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip(_("Double-click to changing status of a to-do."))
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        if self.caller == "todos":
            self.selectionModel().currentRowChanged.connect(
                lambda: self.parent_.insertInformations(self.getParentText(), self.getCurrentText()))
            
        self.doubleClicked.connect(lambda: self.changeStatus(self.getParentText(), self.getCurrentText()))
        
        self.appendAll()

    def appendAll(self) -> None:
        call = todosdb.getAll()
        
        if call != None and self.caller == "todos":
            model_count = -1
            
            all = [*call]
            
            for todolist, creation_todolist, modification_todolist, background_todolist, foreground_todolist in all:
                model_count += 1
                todolist_count = -1
                
                todolist_counts[todolist] = model_count
                todolist_items[todolist] = [QStandardItem(todolist),
                                            QStandardItem(creation_todolist),
                                            QStandardItem(modification_todolist)]
                
                for item in todolist_items[todolist]:
                    if background_todolist == "global" and setting_background != "default":
                        item.setBackground(QColor(setting_background))
                    elif background_todolist != "global" and background_todolist != "default":
                        item.setBackground(QColor(background_todolist))
                    
                    if foreground_todolist == "global" and setting_foreground != "default":
                        item.setForeground(QColor(setting_foreground))
                    elif foreground_todolist != "global" and foreground_todolist != "default":
                        item.setForeground(QColor(foreground_todolist))
                
                for (todo, status_todo, creation_todo, completion_todo,
                     background_todo, foreground_todo) in call[todolist,creation_todolist, modification_todolist,
                                                               background_todolist, foreground_todolist]:
                    todolist_count += 1
                    
                    todo_counts[(todolist, todo)] = todolist_count
                    
                    if status_todo == "completed":
                        name_column = QStandardItem(f"[+] {todo}")
                    elif status_todo == "uncompleted":
                        name_column = QStandardItem(f"[-] {todo}")
                    
                    if completion_todo != "" and completion_todo != None:
                        completion_column = QStandardItem(_("Not completed"))
                    else:
                        completion_column = QStandardItem(completion_todo)
                        
                    todo_items[(todolist, todo)] = [name_column, 
                                                    QStandardItem(creation_todo), 
                                                    completion_column]

                    for item in todo_items[(todolist, todo)]:
                        if background_todo == "global" and setting_background != "default":
                            item.setBackground(QColor(setting_background))
                        elif background_todo != "global" and background_todo != "default":
                            item.setBackground(QColor(background_todo))
                        
                        if foreground_todo == "global" and setting_foreground != "default":
                            item.setForeground(QColor(setting_foreground))
                        elif foreground_todo != "global" and foreground_todo != "default":
                            item.setForeground(QColor(foreground_todo))
                
                    todolist_items[todolist][0].appendRow(todo_items[(todolist, todo)])
                
                todos_model.appendRow(todolist_items[todolist])
            
    def appendTodo(self, todolist: str, todo: str) -> None:
        (status_todo, creation_todo, completion_todo,
         background_todo, foreground_todo) = todosdb.getTodo(todolist, todo)
        
        todo_counts[(todolist, todo)] = todolist_items[todolist][0].rowCount()
        
        if status_todo == "completed":
            name_column = QStandardItem(f"[+] {todo}")
        elif status_todo == "uncompleted":
            name_column = QStandardItem(f"[-] {todo}")
        
        if completion_todo != "" and completion_todo != None:
            completion_column = QStandardItem(_("Not completed"))
        else:
            completion_column = QStandardItem(completion_todo)
            
        todo_items[(todolist, todo)] = [name_column, 
                                        QStandardItem(creation_todo), 
                                        completion_column]
        
        for item in todo_items[(todolist, todo)]:
            if background_todo == "global" and setting_background != "default":
                item.setBackground(QColor(setting_background))
            elif background_todo != "global" and background_todo != "default":
                item.setBackground(QColor(background_todo))
            
            if foreground_todo == "global" and setting_foreground != "default":
                item.setForeground(QColor(setting_foreground))
            elif foreground_todo != "global" and foreground_todo != "default":
                item.setForeground(QColor(foreground_todo))

        todolist_items[todolist][0].appendRow(todo_items[(todolist, todo)])
            
    def appendTodolist(self, todolist: str) -> None:
        (creation_todolist, modification_todolist, 
         background_todolist, foreground_todolist, todos) = todosdb.getTodolist(todolist)
        
        model_count = todos_model.rowCount()
        todolist_count = -1
        
        todolist_counts[todolist] = model_count
        todolist_items[todolist] = [QStandardItem(todolist),
                                    QStandardItem(creation_todolist),
                                    QStandardItem(modification_todolist)]
        
        for item in todolist_items[todolist]:
            if background_todolist == "global" and setting_background != "default":
                item.setBackground(QColor(setting_background))
            elif background_todolist != "global" and background_todolist != "default":
                item.setBackground(QColor(background_todolist))
            
            if foreground_todolist == "global" and setting_foreground != "default":
                item.setForeground(QColor(setting_foreground))
            elif foreground_todolist != "global" and foreground_todolist != "default":
                item.setForeground(QColor(foreground_todolist))
        
        for (todo, status_todo, creation_todo, completion_todo,
                background_todo, foreground_todo) in todos:
            todolist_count += 1
            
            todo_counts[(todolist, todo)] = todolist_count
            
            if status_todo == "completed":
                name_column = QStandardItem(f"[+] {todo}")
            elif status_todo == "uncompleted":
                name_column = QStandardItem(f"[-] {todo}")
            
            if completion_todo != "" and completion_todo != None:
                completion_column = QStandardItem(_("Not completed"))
            else:
                completion_column = QStandardItem(completion_todo)
                
            todo_items[(todolist, todo)] = [name_column, 
                                            QStandardItem(creation_todo), 
                                            completion_column]

            for item in todo_items[(todolist, todo)]:
                if background_todo == "global" and setting_background != "default":
                    item.setBackground(QColor(setting_background))
                elif background_todo != "global" and background_todo != "default":
                    item.setBackground(QColor(background_todo))
                
                if foreground_todo == "global" and setting_foreground != "default":
                    item.setForeground(QColor(setting_foreground))
                elif foreground_todo != "global" and foreground_todo != "default":
                    item.setForeground(QColor(foreground_todo))
        
            todolist_items[todolist][0].appendRow(todo_items[(todolist, todo)])
        
        todos_model.appendRow(todolist_items[todolist])

    def changeStatus(self, todolist: str, todo: str) -> None:
        if todo == "" or todo == None:
            QMessageBox.critical(self, _("Error"), _("Please select a to-do."))
            return
                
        else:
            if not self.parent_.todo_options.checkIfTheTodoExists(todolist, todo):
                return
            
        call = todosdb.changeStatus(todolist, todo)
            
        if call:
            self.updateTodo(todolist, todo, todo)
            
            QMessageBox.information(self, _("Successful"), _("{todo} todo's status changed.").format(todo = todo))
    
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to change {todo}'s status.").format(todo = todo))
        
    def deleteTodo(self, todolist: str, todo: str) -> None:
        todolist_items[todolist][0].removeRow(todo_counts[(todolist, todo)])
        
        del todo_items[(todolist, todo)]
        del todo_counts[(todolist, todo)]
        
    def deleteTodolist(self, todolist: str) -> None:
        todos_model.removeRow(todolist_counts[todolist])
        
        del todolist_counts[todolist]
        del todolist_items[todolist]
        
        for key in todo_items.copy().keys():
            if key[0] == todolist:
                del todo_items[key]
                
        for key in todo_counts.copy().keys():
            if key[0] == todolist:
                del todo_counts[key]
                
        if self.caller == "todos":
            del todolist_menus[todolist]
                    
    def getParentText(self) -> str:
        try:
            if self.currentIndex().parent().isValid():
                return self.proxy.itemData(self.currentIndex().parent())[0]
            
            else:
                return self.proxy.itemData(self.currentIndex())[0]
            
        except KeyError:
            return ""
        
    def getCurrentText(self) -> str:
        try:
            if self.currentIndex().parent().isValid():
                return self.proxy.itemData(self.currentIndex())[0][4:]
            
            else:
                return ""
            
        except KeyError:
            return ""
                
    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        index = self.indexAt(e.pos())
        
        if index.column() == 0:
            super().mousePressEvent(e)
            
        else:
            QMessageBox.warning(self, _("Warning"), _("Please select a to-do or a to-do list only by clicking on the first column."))
                
    def setFilter(self, text: str) -> None:
        self.proxy.beginResetModel()
        self.proxy.setFilterFixedString(text)
        self.proxy.endResetModel()
        
    def updateAll(self) -> None:
        todos_model.clear()
        todos_model.setHorizontalHeaderLabels([_("Name"), _("Creation"), _("Modification / Completion")])
        
        self.appendAll()
        
    def updateTodo(self, todolist: str, todo: str, newtodo: str) -> None:
        status = todosdb.getStatus(todolist, newtodo)
        
        todo_counts[(todolist, newtodo)] = todo_counts.pop((todolist, todo))
        todo_items[(todolist, newtodo)] = todo_items.pop((todolist, todo))
        
        if status == "completed":
            todo_items[(todolist, newtodo)][0].setText(f"[+] {newtodo}")
        elif status == "uncompleted":
            todo_items[(todolist, newtodo)][0].setText(f"[-] {newtodo}")
            
    def updateTodoBackground(self, todolist: str, todo: str, color: str) -> None:
        for item in todo_items[(todolist, todo)]:
            if color == "global" and setting_background != "default":
                item.setBackground(QColor(setting_background))    
            elif color != "global" and color != "default":
                item.setBackground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.BackgroundRole)
                
    def updateTodoForeground(self, todolist: str, todo: str, color: str) -> None:
        for item in todo_items[(todolist, todo)]:
            if color == "global" and setting_foreground != "default":
                item.setForeground(QColor(setting_foreground))
            elif color != "global" and color != "default":
                item.setForeground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.ForegroundRole)
            
    def updateTodolist(self, name: str, newname: str) -> None:
        todolist_counts[newname] = todolist_counts.pop(name)
        todolist_items[newname] = todolist_items.pop(name)
        todolist_menus[newname] = todolist_menus.pop(name)
        
        todolist_items[newname][0].setText(newname)
        
    def updateTodolistBackground(self, name: str, color: str) -> None:
        for item in todolist_items[name]:
            if color == "global" and setting_background != "default":
                item.setBackground(QColor(setting_background))    
            elif color != "global" and color != "default":
                item.setBackground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.BackgroundRole)
                
    def updateTodolistForeground(self, name: str, color: str) -> None:
        for item in todolist_items[name]:
            if color == "global" and setting_foreground != "default":
                item.setForeground(QColor(setting_foreground))
            elif color != "global" and color != "default":
                item.setForeground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.ForegroundRole)