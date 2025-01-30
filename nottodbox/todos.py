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
import datetime
from gettext import gettext as _
from PySide6.QtCore import Slot
from PySide6.QtWidgets import *
from databases.lists import DBForLists
from widgets.others import HSeperator, PushButton
from widgets.options import HomePageForLists, OptionsForLists 


username = getpass.getuser()
userdata = f"/home/{username}/.config/io.github.mukonqi/nottodbox/"


class TodosDB(DBForLists):
    file = "todos.db"
    widget = HomePageForLists

    def changeStatus(self, name: str, table: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        status = self.getStatus(name, table)
        
        if status == "completed":
            newstatus = "uncompleted"
            
            self.widget.child_items[(name, table)][2].setText(_("Not completed yet"), name) 
        
        elif status == "uncompleted": 
            newstatus = "completed"
            
            self.widget.child_items[(name, table)][2].setText(date, name) 
            
        self.cur.execute(
            f"update '{table}' set status = ?, completion = ? where name = ?", (newstatus, date, name))
        self.db.commit()
        
        if self.getData("status", name, table) == newstatus:
            return self.updateModification(table, "__main__", date)
        
    def createChild(self, name: str, table: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        return super().createChild(f"""
                                   insert into '{table}' 
                                   (name, status, creation, background, foreground) 
                                   values (?, ?, ?, ?, ?)
                                   """,
                                   (name, "uncompleted", date, "global", "global"),
                                   name,
                                   table,
                                   date)
        
    def createMainTable(self) -> bool:
        return super().createMainTable("""
                                       CREATE TABLE IF NOT EXISTS __main__ (
                                           name TEXT NOT NULL PRIMARY KEY,
                                           creation TEXT NOT NULL,
                                           modification TEXT NOT NULL,
                                           background TEXT NOT NULL,
                                           foreground TEXT NOT NULL);
                                           """)
    
    def createParent(self, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        return super().createParent(["""
                                     insert into __main__ 
                                     (name, creation, modification, background, foreground) 
                                     values (?, ?, ?, ?, ?)
                                     """,
                                     f"""CREATE TABLE IF NOT EXISTS '{name}' (
                                         name TEXT NOT NULL PRIMARY KEY,
                                         status TEXT NOT NULL,
                                         creation TEXT NOT NULL,
                                         completion TEXT,
                                         background TEXT NOT NULL,
                                         foreground TEXT NOT NULL);
                                         """],
                                    (name, date, date, "global", "global"),
                                    name)
        
    def getStatus(self, name: str, table: str) -> str:
        return self.getData("status", name, table)
    
    def getChild(self, name: str, table: str) -> list:
        self.cur.execute(f"""select status, creation, completion, background, foreground 
                         from '{table}' where name = ?""", (name,))
        return self.cur.fetchone()
    
    def getParent(self, name: str) -> tuple[str, list]:
        self.cur.execute(f"""select creation, modification, background, foreground 
                         from __main__ where name = ?""", (name,))
        creation, modification, background, foreground = self.cur.fetchone()
        
        self.cur.execute(f"select name from '{name}'")
        return creation, modification, background, foreground, self.cur.fetchall()
    
    def updateModification(self, name: str, table: str = "__main__", date: str | None = None) -> bool:
        if super().updateModification(name, table, date):
            if table == "__main__":
                date = self.getModification(name, table)
                
                self.widget.table_items[name][2].setText(date, name)
                
            return True
        
        else:
            return False


todosdb = TodosDB()


class TodosHomePage(HomePageForLists):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent, "todos", todosdb)
        
        self.child_options = TodosChildOptions(self)
        self.child_options.setVisible(False)
        
    def refreshSettings(self) -> None:
        self.refreshSettingsForLists()
        
    @Slot(str, str)
    def shortcutEvent(self, name: str, table: str = "__main__") -> None:
        self.child_options.changeStatus(False, name, table)
        
        
class TodosChildOptions(OptionsForLists):
    def __init__(self, parent):
        super().__init__(parent, "todos", todosdb)
        
        self.change_status_button = PushButton(self, _("Change Status"))
        self.change_status_button.clicked.connect(self.changeStatus)
        
        self.layout_.addWidget(self.create_parent_button)
        self.layout_.addWidget(self.create_child_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.change_status_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.rename_button)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.set_background_button)
        self.layout_.addWidget(self.set_foreground_button)
        
    @Slot(bool)
    def changeStatus(self, state: bool, name: str = None, table: str = None) -> None:
        if name is None:
            name = self.parent_.name
        
        if table is None:
            table = self.parent_.table
        
        if self.checkIfItExists(name, table):
            if todosdb.changeStatus(name, table):
                self.parent_.shortcuts[(name, table)].setText(self.parent_.returnPretty(name, table))
                
                self.parent_.treeview.updateItem(name, name, table)
        
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to change status {of_item}.")
                                    .format(of_item = _("of {name} to-do").format(name = name)))