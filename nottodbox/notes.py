# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024-2025 Mukonqi (Muhammed S.)

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


import datetime
from gettext import gettext as _
from PySide6.QtCore import Slot
from PySide6.QtWidgets import *
from databases.documents import DBForDocuments
from databases.lists import DBForLists
from widgets.others import Action, HSeperator
from widgets.options import TabWidget, HomePageForDocuments, HomePageForLists, OptionsForDocuments, OptionsForLists


class NotesDB(DBForDocuments, DBForLists):
    file = "notes.db"
    widget = HomePageForDocuments | HomePageForLists
        
    def createChild(self, name: str, table: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        return super().createChild(f"""
                                      insert into '{table}' 
                                      (name, content, backup, creation, modification, background, foreground, autosave, format) 
                                      values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                      """,
                                      (name, "", "", date, date, "global", "global", "global", "global"),
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
                                   f"""
                                   CREATE TABLE IF NOT EXISTS '{name}' (
                                       name TEXT NOT NULL PRIMARY KEY,
                                       content TEXT,
                                       backup TEXT, 
                                       creation TEXT NOT NULL,
                                       modification TEXT NOT NULL,
                                       background TEXT NOT NULL,
                                       foreground TEXT NOT NULL,
                                       autosave TEXT NOT NULL,
                                       format TEXT NOT NULL);
                                       """],
                                  (name, date, date, "global", "global"),
                                  name)
    
    def getChild(self, name: str, table: str) -> list:
        self.cur.execute(f"""select creation, modification, 
                         background, foreground from '{table}' where name = ?""", (name,))
        
        return self.cur.fetchone()
    
    def getParent(self, name: str) -> tuple[str, list]:  
        self.cur.execute(
            f"""select creation, modification, background, foreground from __main__ where name = ?""", (name,))
        creation, modification, background, foreground = self.cur.fetchone()
        
        self.cur.execute(
            f"select name from '{name}'")
        
        return creation, modification, background, foreground, self.cur.fetchall()
    
    def restoreContent(self, name: str, table: str) -> bool:
        call, content = super().restoreContent(name, table)
        
        if call:
            return self.setBackup(content, name, table)
        
        else:
            return False
        
    def setBackup(self, content: str, name: str, table: str) -> bool:
        self.cur.execute(f"update '{table}' set backup = ? where name = ?", (content, name))
        self.db.commit()
        
        return self.getBackup(name, table) == content
    
    def updateModification(self, name: str, table: str = "__main__", date: str | None = None) -> bool:
        if super().updateModification(name, table, date):
            date = self.getModification(name, table)
            
            if table == "__main__":
                self.widget.table_items[name][2].setText(date, name)
                
            elif table != "__main__":
                self.widget.child_items[(name, table)][2].setText(date, name)
                
            return True
        
        else:
            return False


notesdb = NotesDB()


class NotesTabWidget(TabWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent, "notes")
        
        self.home = NotesHomePage(self)
        
        self.addTab(self.home, _("Home"))
        

class NotesHomePage(HomePageForDocuments, HomePageForLists):
    def __init__(self, parent: NotesTabWidget):
        super().__init__(parent, "notes", notesdb)
        
        self.child_options = NotesChildOptions(self)
        self.child_options.setVisible(False)
        
    def refreshSettings(self) -> None:
        self.refreshSettingsForDocuments()
        self.refreshSettingsForLists()
        
    @Slot(str, str)
    def shortcutEvent(self, name: str, table: str = "__main__") -> None:
        self.child_options.open(False, name, table)
        

class NotesChildOptions(OptionsForDocuments, OptionsForLists):
    def __init__(self, parent: NotesHomePage):
        super().__init__(parent, "notes", notesdb)
        
        self.layout_.addWidget(self.create_child_button)
        self.layout_.addWidget(self.create_parent_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.open_button)
        self.layout_.addWidget(self.show_backup_button)
        self.layout_.addWidget(self.restore_content_button)
        self.layout_.addWidget(self.clear_content_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.rename_button)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.set_background_button)
        self.layout_.addWidget(self.set_foreground_button)
        
    @Slot(bool, str)
    def open(self, state: bool, name: str = None, table: str = None) -> None:
        if name is None:
            name = self.parent_.name
        
        if table is None:
            table = self.parent_.table
        
        if table != "":
            if name == "":
                try:
                    name = next(name_range for name_range, table_range in self.parent_.child_items.keys() 
                                if str(table_range).startswith(table))

                except:
                    call = notesdb.createChild(_("Unnamed"), table)
                    
                    if call:
                        name = _("Unnamed")
                        
                        self.parent_.shortcuts[(name, table)] = Action(self, f"{name} @ {table}")
                        self.parent_.shortcuts[(name, table)].triggered.connect(
                            lambda state: self.parent_.shortcutEvent(name, table))
                        self.parent_.menu.addAction(self.parent_.shortcuts[(name, table)]) 
                        
                        self.parent_.treeview.appendChild(name, table)
                        self.parent_.treeview.setIndex(name, table)
                    
                    else:
                        QMessageBox.critical(self, _("Error"), _("Failed to create {item}.")
                                             .format(item = _("{name} note").format(name = _("Unnamed"))))
                        return
                
            super().open(False, name, table)
                
        else:
            QMessageBox.critical(self, _("Error"), _("Please select a {} or a {}.")
                                 .format(_("notebook"), _("note")))