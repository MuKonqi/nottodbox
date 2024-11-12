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
import getpass
import sqlite3
import datetime
from gettext import gettext as _
from settings import settingsdb
from widgets.dialogs import ColorDialog
from widgets.other import HSeperator, Label, PushButton, VSeperator
from widgets.lists import TreeView
from PySide6.QtCore import Slot
from PySide6.QtGui import QStandardItemModel, QColor
from PySide6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"

todolist_counts = {}
todolist_items = {}
todo_counts = {}
todo_items = {}

setting_background, setting_foreground = settingsdb.getModuleSettings("todos")


class TodosDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}todos.db")
        self.cur = self.db.cursor()

    def changeStatus(self, todolist: str, name: str) -> tuple:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        status = self.getStatus(todolist, name)
        
        if status == "completed":
            newstatus = "uncompleted"
            
            todo_items[(todolist, name)][2].setText(_("Not completed yet"), name) 
        
        elif status == "uncompleted": 
            newstatus = "completed"
            
            todo_items[(todolist, name)][2].setText(date, name) 
            
        self.cur.execute(f"update '{todolist}' set status = ?, completion = ? where name = ?", (newstatus, date, name))
        self.db.commit()
        
        if not self.updateTodolistModificationDate(todolist, date):
            return False
        
        self.cur.execute(f"select status from '{todolist}' where name = ?", (name,))
        control = self.cur.fetchone()[0]
        
        if control == newstatus:
            return True
        
        else:
            return False 
       
    def checkIfTheTableExists(self, table: str) -> bool:
        try:
            self.cur.execute(f"select * from '{table}'")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def checkIfTheTodoExists(self, todolist: str, name: str) -> bool:
        if self.checkIfTheTodolistExists(todolist):
            self.cur.execute(f"select * from '{todolist}' where name = ?", (name,))
            
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
    
    def createTodo(self, todolist: str, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute("update __main__ set modification = ? where name = ?", (date, todolist))
        self.db.commit()
        
        self.cur.execute(f"""insert into '{todolist}' 
                         (name, status, creation, background, foreground) values (?, ?, ?, ?, ?)""",
                         (name, "uncompleted", date, "global", "global"))
        self.db.commit()
        
        self.cur.execute(f"select * from '{todolist}' where name = ?", (name,))
        control = self.cur.fetchone()
        
        if control[0] == name and control[1] == "uncompleted" and control[2] == date:
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
                name TEXT NOT NULL PRIMARY KEY,
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
    
    def deleteTodo(self, todolist: str, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"delete from '{todolist}' where name = ?", (name,))
        self.db.commit()
        
        if not self.updateTodolistModificationDate(todolist, date):
            return False
        
        call = self.checkIfTheTodoExists(todolist, name)
        
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
        
    def editTodo(self, todolist: str, name: str, newname: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"update '{todolist}' set name = ? where name = ?", (newname, name))
        self.db.commit()
        
        if not self.updateTodolistModificationDate(todolist, date):
            return False
        
        return self.checkIfTheTodoExists(todolist, newname)
        
    def getStatus(self, todolist: str, name: str) -> str:
        self.cur.execute(f"select status from '{todolist}' where name = ?", (name,))
        return self.cur.fetchone()[0]
    
    def getTodo(self, todolist: str, name: str) -> list:
        self.cur.execute(f"""select status, creation, completion,
                         background, foreground from '{todolist}' where name = ?""", (name,))
        return self.cur.fetchone()
    
    def getTodoBackground(self, todolist: str, name: str) -> str:
        self.cur.execute(f"select background from '{todolist}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
        
    def getTodoForeground(self, todolist: str, name: str) -> str:
        self.cur.execute(f"select foreground from '{todolist}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getTodolist(self, name: str) -> tuple:
        self.cur.execute(f"""select creation, modification, 
                         background, foreground from __main__ where name = ?""", (name,))
        creation, modification, background, foreground = self.cur.fetchone()
        
        self.cur.execute(f"select name from '{name}'")
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
    
    def getTodolistNames(self) -> list:
        self.cur.execute("select name from __main__")
        return self.cur.fetchall()
        
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
    
    def setTodoBackground(self, todolist: str, name: str, color: str) -> bool:
        self.cur.execute(f"update '{todolist}' set background = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getTodoBackground(todolist, name)
        
        if call == color:
            return True
        else:
            return False
        
    def setTodoForeground(self, todolist: str, name: str, color: str) -> bool:
        self.cur.execute(f"update '{todolist}' set foreground = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getTodoForeground(todolist, name)
        
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
        self.todolist = ""
        self.name = ""
        self.current_widget = None
        
        self.home_layout = QGridLayout(self)
        
        self.selecteds = QWidget(self)
        self.selecteds_layout = QHBoxLayout(self.selecteds)
        
        self.todolist_selected = Label(self, "{}: ".format(_("to-do list").title()))
        self.todo_selected = Label(self, "{}: ".format(_("to-do").title()))
        
        self.treeview = TodosTreeView(self)
        
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText(_("Search..."))
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
        
        self.setLayout(self.home_layout)
        self.home_layout.addWidget(self.selecteds, 0, 0, 1, 3)
        self.home_layout.addWidget(HSeperator(self), 1, 0, 1, 3)
        self.home_layout.addWidget(self.entry, 2, 0, 1, 1)
        self.home_layout.addWidget(HSeperator(self), 3, 0, 1, 1)
        self.home_layout.addWidget(self.treeview, 4, 0, 1, 1)
        self.home_layout.addWidget(VSeperator(self), 2, 1, 3, 1)
        self.home_layout.addWidget(self.none_options, 2, 2, 3, 1)
        
    @Slot()
    def deleteAll(self) -> None:
        question = QMessageBox.question(self, _("Question"), _("Do you really want to delete all to-dos?"))
        
        if question == QMessageBox.StandardButton.Yes:
            call = todosdb.deleteAll()
        
            if call:
                self.treeview.deleteAll()
                self.treeview.setIndex("", "")
                self.insertInformations("", "")
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to delete all to-do lists."))
            
    @Slot(str, str)
    def insertInformations(self, todolist: str, name: str) -> None:
        self.todolist = todolist
        self.name = name      
        
        self.none_options.setVisible(False)
        self.todolist_options.setVisible(False)
        self.todo_options.setVisible(False)
        
        if self.todolist == "":
            self.none_options.setVisible(True)
            self.home_layout.replaceWidget(self.current_widget, self.none_options)
            
            self.current_widget = self.none_options
            
        elif self.todolist != "" and self.name == "":
            self.todolist_options.setVisible(True)
            self.home_layout.replaceWidget(self.current_widget, self.todolist_options)
            
            self.current_widget = self.todolist_options
            
        elif self.todolist != "" and self.name != "":
            self.todo_options.setVisible(True)
            self.home_layout.replaceWidget(self.current_widget, self.todo_options)
            
            self.current_widget = self.todo_options
            
        self.todolist_selected.setText("{}: ".format(_("to-do list").title()) + todolist)
        self.todo_selected.setText("{}: ".format(_("to-do").title()) + name)
        
    def refreshSettings(self) -> None:
        global setting_background, setting_foreground
        
        setting_background, setting_foreground = settingsdb.getModuleSettings("todos")
        
        self.treeview.setting_background = setting_background
        self.treeview.setting_foreground = setting_foreground
            
            
class TodosNoneOptions(QWidget):
    def __init__(self, parent: TodosWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.warning_label = Label(self, _("You can select\na to-do list\nor a to-do\non the left."))
        self.warning_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.create_todolist_button = PushButton(self, _("Create {}").format(_("to-do list").title()))
        self.create_todolist_button.clicked.connect(self.parent_.todolist_options.createTodolist)
        
        self.delete_all_button = PushButton(self, _("Delete All"))
        self.delete_all_button.clicked.connect(self.parent_.deleteAll)
        
        self.setFixedWidth(200)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.warning_label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.create_todolist_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        
        
class TodosTodolistOptions(QWidget):
    def __init__(self, parent: TodosWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.create_todo_button = PushButton(self, _("Create {}").format(_("to-do").title()))
        self.create_todo_button.clicked.connect(self.parent_.todo_options.createTodo)
        
        self.create_todolist_button = PushButton(self, _("Create {}").format(_("to-do list").title()))
        self.create_todolist_button.clicked.connect(self.createTodolist)
        
        self.set_background_button = PushButton(self, _("Set Background Color"))
        self.set_background_button.clicked.connect(self.setTodolistBackground)
        
        self.set_foreground_button = PushButton(self, _("Set Text Color"))
        self.set_foreground_button.clicked.connect(self.setTodolistForeground)
        
        self.rename_button = PushButton(self, _("Rename"))
        self.rename_button.clicked.connect(self.renameTodolist)
        
        self.reset_button = PushButton(self, _("Reset"))
        self.reset_button.clicked.connect(self.resetTodolist)
        
        self.delete_button = PushButton(self, _("Delete"))
        self.delete_button.clicked.connect(self.deleteTodolist)
        
        self.delete_all_button = PushButton(self, _("Delete All"))
        self.delete_all_button.clicked.connect(self.parent_.deleteAll)
        
        self.setFixedWidth(200)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.create_todo_button)
        self.layout_.addWidget(self.create_todolist_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.set_background_button)
        self.layout_.addWidget(self.set_foreground_button)
        self.layout_.addWidget(self.rename_button)
        self.layout_.addWidget(self.reset_button)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        
    def checkIfTheTodolistExists(self, name: str, mode: str = "normal") -> None:
        call = todosdb.checkIfTheTodolistExists(name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no {item}.")
                                 .format(item = _("{name} to-do list").format(name = name)))
        
        return call
    
    def checkTheName(self, name: str) -> bool:
        if "'" in name or "@" in name:
            QMessageBox.critical(self, _("Error"), _("The {} name can not contain these characters: ' and @")
                                 .format(_("to-do list")))
            return False
        
        elif "__main__" == name:
            QMessageBox.critical(self, _("Error"), _("The {} name can not be to __main__.")
                                 .format(_("to-do list")))
            return False
        
        else:
            return True
    
    @Slot()
    def createTodolist(self) -> None:
        name, topwindow = QInputDialog.getText(self, 
                                               _("Create {}").format(_("to-do list").title()), 
                                               _("Please enter a name for creating a {}.").format(_("to-do list")))
        
        if not self.checkTheName(name):
            return
        
        elif topwindow and name != "":
            call = self.checkIfTheTodolistExists(name, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{item} already created.")
                                     .format(item = _("{name} to-do list").format(name = name)))
        
            else:
                call = todosdb.createTodolist(name)
                
                if call:
                    self.parent_.treeview.appendTodolist(name)
                    self.parent_.treeview.setIndex(name, "")
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {item}.")
                                         .format(item = _("{name} to-do list").format(name = name)))
          
    @Slot()             
    def deleteTodolist(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        question = QMessageBox.question(self, _("Question"), _("Do you really want to delete the {item}?")
                                        .format(item = _("{name} to-do list").format(name = name)))
        
        if question == QMessageBox.StandardButton.Yes:
            call = todosdb.deleteTodolist(name)
                
            if call:
                self.parent_.treeview.deleteTodolist(name)
                self.parent_.treeview.setIndex("", "")
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to delete {item}.")
                                     .format(item = _("{name} to-do list").format(name = name)))
    
    @Slot()
    def renameTodolist(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {item}")
                                                  .format(item = _("{name} to-do list").format(name = name).title()), 
                                                  _("Please enter a new name for {item}.")
                                                  .format(item = _("{name} to-do list").format(name = name)))
        
        if not self.checkTheName(name):
            return
        
        elif topwindow and newname != "":
            if not self.checkIfTheTodolistExists(newname, "no-popup"):
                call = todosdb.renameTodolist(name, newname)
                
                if call:
                    self.parent_.treeview.updateTodolist(name, newname)
                    self.parent_.treeview.setIndex(newname, "")
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to rename {item}.")
                                        .format(item = _("{name} to-do list").format(name = name)))
                    
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newitem}, renaming {the_item} cancalled.")
                                     .format(newitem = _("{name} to-do list").format(name = name), 
                                             the_item = _("the {name} to-do list").format(name = name)))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {item}.")
                                 .format(item = _("{name} to-do list").format(name = name)))
    
    @Slot()        
    def resetTodolist(self) -> None:
        name = self.parent_.name
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        call = todosdb.resetTodolist(name)
        
        if call:
            self.parent_.treeview.deleteTodolist(name)
            self.parent_.treeview.appendTodolist(name)
            self.parent_.treeview.setIndex(name, "")
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset {item}.")
                                 .format(item = _("{name} to-do list").format(name = name)))
       
    @Slot()     
    def setTodolistBackground(self) -> None:
        name = self.parent_.todolist
        
        if not self.checkIfTheTodolistExists(name):
            return
        
        background = todosdb.getTodolistBackground(name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(background if background != "global" and background != "default"
                   else (setting_background if background == "global" and setting_background != "default" 
                         else "#FFFFFF")),
            _("Select Background Color for {item}")
            .format(item = _("{name} to-do list").format(name = name)).title()).getColor()
        
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
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {item}.")
                                     .format(item = _("{name} to-do list").format(name = name)))
        
    @Slot()
    def setTodolistForeground(self) -> None:
        name = self.parent_.todolist

        if not self.checkIfTheTodolistExists(name):
            return
        
        foreground = todosdb.getTodolistForeground(name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(foreground if foreground != "global" and foreground != "default"
                   else (setting_foreground if foreground == "global" and setting_foreground != "default" 
                         else "#FFFFFF")),
            _("Select Text Color for {item}")
            .format(item = _("{name} to-do list").format(name = name)).title()).getColor()
        
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
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set text color for {item}.")
                                     .format(item = _("{name} to-do list").format(name = name)))

        
class TodosTodoOptions(QWidget):
    def __init__(self, parent: TodosWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.create_todo_button = PushButton(self, _("Create {}").format(_("to-do")))
        self.create_todo_button.clicked.connect(self.createTodo)
        
        self.set_background_button = PushButton(self, _("Set Background Color"))
        self.set_background_button.clicked.connect(self.setTodoBackground)
        
        self.set_foreground_button = PushButton(self, _("Set Text Color"))
        self.set_foreground_button.clicked.connect(self.setTodoForeground)
        
        self.change_status_button = PushButton(self, _("Change Status"))
        self.change_status_button.clicked.connect(self.changeStatus)
        
        self.edit_button = PushButton(self, _("Edit"))
        self.edit_button.clicked.connect(self.editTodo)
        
        self.delete_button = PushButton(self, _("Delete"))
        self.delete_button.clicked.connect(self.deleteTodo)
        
        self.delete_all_button = PushButton(self, _("Delete All"))
        self.delete_all_button.clicked.connect(self.parent_.deleteAll)
        
        self.setFixedWidth(200)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.create_todo_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.set_background_button)
        self.layout_.addWidget(self.set_foreground_button)
        self.layout_.addWidget(self.change_status_button)
        self.layout_.addWidget(self.edit_button)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        
    def checkIfTheTodoExists(self, todolist: str, name: str, mode: str = "normal") -> bool:
        call = todosdb.checkIfTheTodoExists(todolist, name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no {item}.")
                                 .format(item = _("{name} to-do").format(name = name)))
        
        return call
    
    @Slot()
    def changeStatus(self) -> None:
        todolist = self.parent_.todolist
        name = self.parent_.name
        
        if not self.checkIfTheTodoExists(todolist, name):
            return
        
        call = todosdb.changeStatus(todolist, name)
        
        if call:
            self.parent_.treeview.updateTodo(todolist, name, name)
    
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to change status {of_item}.")
                                 .format(of_item = _("of {name} to-do").format(name = name)))
    
    @Slot()
    def createTodo(self) -> None:
        todolist = self.parent_.todolist
        
        if not todosdb.checkIfTheTodolistExists(todolist):
            QMessageBox.critical(self, _("Error"), _("There is no {item}.")
                                 .format(of_item = _("of {name} to-do list").format(name = todolist)))
            return
        
        name, topwindow = QInputDialog.getText(self, 
                                               _("Create {}").format(_("to-do").title()), 
                                               _("Please enter a name for creating a {}.").format(_("to-do")))
        
        if topwindow and name != "":
            call = self.checkIfTheTodoExists(todolist, name, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{item} already created.")
                                     .format(item = _("{name} to-do").format(name = name)))
        
            else:
                call = todosdb.createTodo(todolist, name)
                
                if call:
                    self.parent_.treeview.appendTodo(todolist, name)
                    self.parent_.treeview.setIndex(todolist, name)
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {item}.")
                                         .format(item = _("{name} to-do").format(name = name)))
                    
    @Slot()
    def deleteTodo(self) -> None:
        todolist = self.parent_.todolist
        name = self.parent_.name
        
        if not self.checkIfTheTodoExists(todolist, name):
            return
        
        call = todosdb.deleteTodo(todolist, name)
        
        question = QMessageBox.question(self, _("Question"), _("Do you really want to delete the {item}?")
                                        .format(item = _("{name} to-do").format(name = name)))
        
        if question == QMessageBox.StandardButton.Yes:
            if call:
                self.parent_.treeview.deleteTodo(todolist, name)
                self.parent_.treeview.setIndex(todolist, "")
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to delete {item}.")
                                     .format(item = _("{name} to-do").format(name = name)))
                    
    @Slot()
    def editTodo(self) -> None:
        todolist = self.parent_.todolist
        name = self.parent_.name
        
        if not self.checkIfTheTodoExists(todolist, name):
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Edit {item}")
                                                  .format(item = _("{name} to-do").format(name = name)).title(), 
                                                  _("Please enter anything for editing {the_item}.")
                                                  .format(the_item = _("the {name} to-do").format(name = name)))
        
        if topwindow and newname != "":
            if not self.checkIfTheTodoExists(todolist, newname, "no-popup"):
                call = todosdb.editTodo(todolist, name, newname)

                if call:
                    self.parent_.treeview.updateTodo(todolist, name, newname)
                    self.parent_.treeview.setIndex(todolist, newname)
    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to edit {item}.")
                                        .format(item = _("{name} to-do").format(name = name)))
            
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newitem}, renaming {the_item} cancalled.")
                                     .format(newitem = _("{name} to-do").format(name = name), 
                                             the_item = _("the {name} to-do").format(name = name)))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to edit {item}.")
                                 .format(item = _("{name} to-do").format(name = name)))
            
    @Slot()
    def setTodoBackground(self) -> None:
        todolist = self.parent_.todolist
        name = self.parent_.name
        
        if not self.checkIfTheTodoExists(todolist, name):
            return
        
        background = todosdb.getTodoBackground(todolist, name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(background if background != "global" and background != "default"
                   else (setting_background if background == "global" and setting_background != "default" 
                         else "#FFFFFF")),
            _("Select Background Color for {item}")
            .format(item = _("{name} to-do").format(name = name)).title()).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = todosdb.setTodoBackground(todolist, name, color)
                    
            if call:
                self.parent_.treeview.updateTodoBackground(todolist, name, color)
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {item}.")
                                     .format(item = _("{name} to-do").format(name = name)))
        
    @Slot()
    def setTodoForeground(self) -> None:
        todolist = self.parent_.todolist
        name = self.parent_.name

        if not self.checkIfTheTodoExists(todolist, name):
            return
        
        foreground = todosdb.getTodoForeground(todolist, name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(foreground if foreground != "global" and foreground != "default"
                   else (setting_foreground if foreground == "global" and setting_foreground != "default" 
                         else "#FFFFFF")),
            _("Select Text Color for {item}")
            .format(item = _("{name} to-do").format(name = name)).title()).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = todosdb.setTodoForeground(todolist, name, color)
                    
            if call:
                self.parent_.treeview.updateTodoForeground(todolist, name, color)
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set text color for {item}.")
                                     .format(item = _("{name} to-do").format(name = name)))
            
            
class TodosTreeView(TreeView):
    def __init__(self, parent: TodosWidget, caller: str = "own") -> None:
        super().__init__(parent, "todos", caller)
        
        self.db = todosdb
        self.parent_counts = todolist_counts
        self.parent_items = todolist_items
        self.child_counts = todo_counts
        self.child_items = todo_items
        self.setting_background = setting_background
        self.setting_foreground = setting_foreground
        
        if self.caller == "own":
            todos_parent.menuBar().addAction(_("To-dos"), lambda: todos_parent.tabwidget.setCurrentIndex(2))
            
            global todos_model
            
            todos_model = QStandardItemModel(self)
            todos_model.setHorizontalHeaderLabels(["{} / {}".format(_("to-do list"), _("to-do")).title(), 
                                                   _("Creation"), 
                                                   "{} / {}".format(_("Modification"), _("Completion"))])
            
            self.appendAll()
            
        self.proxy.setSourceModel(todos_model)
        
        self.setStatusTip(_("Double-click to changing status of a to-do."))

    def appendAll(self) -> None:
        super().appendAll()
        
        for row in todolist_items.values():
            todos_model.appendRow(row)
            
    def appendTodo(self, todolist: str, name: str) -> None:
        super().appendChild(todolist, name)
            
    def appendTodolist(self, name: str) -> None:
        super().appendParent(name, todos_model.rowCount())
        
        todos_model.appendRow(todolist_items[name])
        
    def deleteAll(self) -> None:
        super().deleteAll()
        
        todos_model.clear()
        todos_model.setHorizontalHeaderLabels(["{} / {}".format(_("to-do list"), _("to-do")).title(), 
                                               _("Creation"), 
                                               "{} / {}".format(_("Modification"), _("Completion"))])
        
    def deleteTodo(self, todolist: str, name: str) -> None:
        super().deleteChild(todolist, name)
        
    def deleteTodolist(self, name: str) -> None:
        super().deleteParent(name)
        
        todos_model.removeRow(todolist_counts[name])
        
        for parent_ in todolist_counts.keys():
            if todolist_counts[parent_] > todolist_counts[name]:
                todolist_counts[parent_] -= 1
        
        del todolist_counts[name]
        del todolist_items[name]
        
    def doubleClickEvent(self, todolist: str, name: str) -> None:
        if name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Please select a {}.").format(_("to-do")))
            return
                
        else:
            if not self.parent_.todo_options.checkIfTheTodoExists(todolist, name):
                return
            
        call = todosdb.changeStatus(todolist, name)
            
        if call:
            self.updateTodo(todolist, name, name)
    
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to change status {of_item}.")
                                 .format(item = _("{name} to-do").format(name = name)))
        
    def updateTodo(self, todolist: str, name: str, newname: str) -> None:
        super().updateChild(todolist, name, newname)
        
        status = self.db.getStatus(todolist, newname)
        
        if status == "completed":
            self.child_items[(todolist, newname)][0].setText(f"[+] {newname}")
        elif status == "uncompleted":
            self.child_items[(todolist, newname)][0].setText(f"[-] {newname}")
        
    def updateTodoBackground(self, todolist: str, name: str, color: str) -> None:
        super().updateChildBackground(todolist, name, color)
        
    def updateTodoForeground(self, todolist: str, name: str, color: str) -> None:
        super().updateParentBackground(todolist, name, color)
                
    def updateTodolist(self, name: str, newname: str) -> None:
        super().updateParent(name, newname)
        
    def updateTodolistBackground(self, name: str, color: str) -> None:
        super().updateParentBackground(name, color)
                
    def updateTodolistForeground(self, name: str, color: str) -> None:
        super().updateParentForeground(name, color)