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
from widgets.pages import NormalPage, BackupPage
from widgets.lists import TreeView
from PySide6.QtGui import QStandardItemModel, QColor
from PySide6.QtCore import Slot
from PySide6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"

notebook_counts = {}
notebook_items = {}
note_counts = {}
note_items = {}
note_menus = {}
notes = {}

setting_autosave, setting_format, setting_background, setting_foreground = settingsdb.getModuleSettings("notes")


class NotesDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}notes.db")
        self.cur = self.db.cursor()
    
    def checkIfTheNoteExists(self, notebook: str, name: str) -> bool:
        if self.checkIfTheNotebookExists(notebook):
            self.cur.execute(f"select * from '{notebook}' where name = ?", (name,))
            
            try:
                self.cur.fetchone()[0]
                return True
            
            except TypeError:
                return False
            
        else:
            return False
        
    def checkIfTheNoteBackupExists(self, notebook: str, name: str) -> bool:
        if self.checkIfTheNoteExists(notebook):
            self.cur.execute(f"select backup from '{notebook}' where name = ?", (name,))
            fetch = self.cur.fetchone()[0]
            
            if fetch == None or fetch == "":
                return False
            else:
                return True
            
        else:
            return False
        
    def checkIfTheNotebookExists(self, name: str) -> bool:
        self.cur.execute(f"select * from __main__ where name = ?", (name,))
        
        try:
            self.cur.fetchone()[0]
            return self.checkIfTheTableExists(name)
            
        except TypeError:
            return False
        
    def checkIfTheTableExists(self, name: str) -> bool:
        try:
            self.cur.execute(f"select * from '{name}'")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def clearContent(self, notebook: str, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        fetch_before = self.getContent(notebook, name)
            
        self.cur.execute(
            f"update '{notebook}' set content = '', backup = ? where name = ?", (fetch_before, name))
        self.db.commit()
        
        if not self.updateNoteModificationDate(notebook, name, date):
            return False
        
        fetch_after = self.getContent(notebook, name)
        
        if fetch_after == "" or fetch_after == None:
            return True
        else:
            return False
        
    def createNote(self, notebook: str, name: str) -> bool:
        if not self.checkIfTheNoteExists(notebook, name):
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
            self.cur.execute(f"""insert into '{notebook}' 
                             (name, content, backup, creation, modification, background, foreground, autosave, format) 
                             values (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                             (name, "", "", date, date, "global", "global", "global", "global"))
            self.db.commit()
        
            if not self.updateNotebookModificationDate(notebook, date):
                return False
        
            return self.checkIfTheNoteExists(notebook, name)

        else:
            return True

    def createNotebook(self, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute("""
        insert into __main__ (name, creation, modification, background, foreground)
        values (?, ?, ?, ?, ?)""", (name, date, date, "global", "global"))
        self.db.commit()
        
        self.cur.execute(f"""
        CREATE TABLE IF NOT EXISTS '{name}' (
            name TEXT NOT NULL PRIMARY KEY,
            content TEXT,
            backup TEXT, 
            creation TEXT NOT NULL,
            modification TEXT NOT NULL,
            background TEXT NOT NULL,
            foreground TEXT NOT NULL,
            autosave TEXT NOT NULL,
            format TEXT NOT NULL
        );""")
        self.db.commit()
        
        return self.checkIfTheNotebookExists(name)
    
    def createMainTable(self) -> bool:
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS __main__ (
            name TEXT NOT NULL PRIMARY KEY,
            creation TEXT NOT NULL,
            modification TEXT NOT NULL,
            background TEXT NOT NULL,
            foreground TEXT NOT NULL
        )
        """)
        self.db.commit()
        
        return self.checkIfTheTableExists("__main__")
    
    def deleteAll(self) -> bool:
        successful = True
        calls = {}
        
        self.cur.execute("select name from __main__")
        parents = self.cur.fetchall()
        
        for notebook in parents:
            notebook = notebook[0]
            
            calls[notebook] = self.deleteNotebook(notebook)
            
            if not calls[notebook]:
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
    
    def deleteNote(self, notebook: str, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"delete from '{notebook}' where name = ?", (name,))
        self.db.commit()
        
        if not self.updateNotebookModificationDate(notebook, date):
            return False
        
        if self.checkIfTheNoteExists(notebook, name):
            return False
        else:
            return True
        
    def deleteNotebook(self, name: str):
        self.cur.execute("delete from __main__ where name = ?", (name,))
        self.db.commit()
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        if self.checkIfTheNotebookExists(name):
            return False
        else:
            return True
    
    def getAutosave(self, notebook: str, name: str) -> str:
        self.cur.execute(f"select autosave from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getBackup(self, notebook: str, name: str) -> str:
        self.cur.execute(f"select backup from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
    
    def getContent(self, notebook: str, name: str) -> str:
        self.cur.execute(f"select content from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
        
    def getFormat(self, notebook: str, name: str) -> str:
        self.cur.execute(f"select format from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getNote(self, notebook: str, name: str) -> list:
        self.cur.execute(f"""select creation, modification, 
                         background, foreground from '{notebook}' where name = ?""", (name,))
        return self.cur.fetchone()
    
    def getNoteBackground(self, notebook: str, name: str) -> str:
        self.cur.execute(f"select background from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getNoteForeground(self, notebook: str, name: str) -> str:
        self.cur.execute(f"select foreground from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getNotebook(self, name: str) -> tuple:
        self.cur.execute(f"""select creation, modification, 
                         background, foreground from __main__ where name = ?""", (name,))
        creation, modification, background, foreground = self.cur.fetchone()
        
        self.cur.execute(f"select name from '{name}'")
        return creation, modification, background, foreground, self.cur.fetchall()
    
    def getNotebookBackground(self, name: str) -> str:
        self.cur.execute(f"select background from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getNotebookForeground(self, name: str) -> str:
        self.cur.execute(f"select foreground from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getNotebookNames(self) -> list:
        self.cur.execute("select name from __main__")
        return self.cur.fetchall()
    
    def renameNote(self, notebook: str, name: str, newname: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"update '{notebook}' set name = ? where name = ?", (newname, name))
        self.db.commit()
        
        if not self.updateNotebookModificationDate(notebook, date):
            return False
        
        return self.checkIfTheNoteExists(notebook, newname)
    
    def renameNotebook(self, name: str, newname: str) -> bool:
        self.cur.execute("update __main__ set name = ? where name = ?", (newname, name))
        self.db.commit()
        
        self.cur.execute(f"ALTER TABLE '{name}' RENAME TO '{newname}'")
        self.db.commit()
        
        return self.checkIfTheNotebookExists(newname)
        
    def resetNotebook(self, name: str) -> bool:
        self.cur.execute("delete from __main__ where name = ?", (name,))
        self.db.commit()
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        if not self.checkIfTheNotebookExists(name):
            return self.createNotebook(name)
        else:
            return False
    
    def restoreContent(self, notebook: str, name: str) -> bool:
        if not self.checkIfTheNoteBackupExists(notebook, name):
            return False
        
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"select content, backup from '{notebook}' where name = ?", (name,))
        fetch_before = self.cur.fetchone()
        
        self.cur.execute(f"update '{notebook}' set content = ?, backup = ? where name = ?", 
                         (fetch_before[1], fetch_before[0], name))
        self.db.commit()
        
        if not self.updateNoteModificationDate(notebook, name, date):
            return False
        
        self.cur.execute(f"select content, backup from '{notebook}' where name = ?", (name,))
        fetch_after = self.cur.fetchone()
        
        if fetch_before[1] == fetch_after[0] and fetch_before[0] == fetch_after[1]:
            return True
        else:
            return False
        
    def saveAll(self) -> bool:
        successful = True
        calls = {}
        
        for item in notes:
            try:
                name, notebook = str(item).split(" @ ")
            
            except ValueError:
                return False
            
            fetch_format = self.getFormat(notebook, name)
            
            if fetch_format == "global":
                fetch_format = setting_format
            
            if fetch_format == "plain-text":
                text = notes[item].input.toPlainText()
                
            elif fetch_format == "markdown":
                text = notes[item].input.toMarkdown()
                
            elif fetch_format == "html":
                text = notes[item].input.toHtml()
            
            calls[item] = self.saveDocument(notebook,
                                            name,
                                            text, 
                                            notes[item].content, 
                                            False)
            
            if not calls[item]:
                successful = False
                
        return successful

    def saveDocument(self, notebook: str, name: str, content: str, backup: str, autosave: bool) -> bool:        
        if self.checkIfTheNoteExists(notebook, name):
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            if autosave:
                self.cur.execute(f"update '{notebook}' set content = ? where name = ?", 
                                 (content, name))
                        
            else:     
                self.cur.execute(f"update '{notebook}' set content = ?, backup = ? where name = ?", 
                                 (content, backup, name))
            
            self.db.commit()
            
            if not self.updateNoteModificationDate(notebook, name, date):
                return False
        
            self.cur.execute(f"select content from '{notebook}' where name = ?", (name,))
            control = self.cur.fetchone()[0]

            if control == content:            
                return True
            else:
                return False

        else:
            return False
        
    def setAutosave(self, notebook: str, name: str, setting: str) -> bool:
        if not self.checkIfTheNoteExists(notebook, name):
            return False
        
        self.cur.execute(f"update '{notebook}' set autosave = ? where name = ?", (setting, name))
        self.db.commit()
        
        call = self.getAutosave(notebook, name)
        
        if call == setting:
            return True
        else:
            return False
        
    def setFormat(self, notebook: str, name: str, setting: str) -> bool:
        if not self.checkIfTheNoteExists(notebook, name):
            return False
        
        self.cur.execute(f"update '{notebook}' set format = ? where name = ?", (setting, name))
        self.db.commit()
        
        call = self.getFormat(notebook, name)
        
        if call == setting:
            return True
        else:
            return False
        
    def setNoteBackground(self, notebook: str, name: str, color: str) -> bool:
        self.cur.execute(f"update '{notebook}' set background = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getNoteBackground(notebook, name)
        
        if call == color:
            return True
        else:
            return False

    def setNotebookBackground(self, name: str, color: str) -> bool:
        self.cur.execute("update __main__ set background = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getNotebookBackground(name)
        
        if call == color:
            return True
        else:
            return False
        
    def setNotebookForeground(self, name: str, color: str) -> bool:
        self.cur.execute("update __main__ set foreground = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getNotebookForeground(name)
        
        if call == color:
            return True
        else:
            return False
        
    def setNoteForeground(self, notebook: str, name: str, color: str) -> bool:
        self.cur.execute(f"update '{notebook}' set foreground = ? where name = ?", (color, name))
        self.db.commit()
        
        call = self.getNoteForeground(notebook, name)
        
        if call == color:
            return True
        else:
            return False
        
    def updateNoteModificationDate(self, notebook: str, name: str, date: str) -> bool:
        if self.checkIfTheNoteExists(notebook, name):
            if self.updateNotebookModificationDate(notebook, date):
                self.cur.execute(f"update '{notebook}' set modification = ? where name = ?", (date, name))
                self.db.commit()
                
                self.cur.execute(f"select modification from '{notebook}' where name = ?", (name,))
                
                try:
                    fetch = self.cur.fetchone()[0]
                    
                    if fetch == date:
                        note_items[(notebook, name)][2].setText(date, name)

                        return True
    
                    else:
                        return False
            
                except TypeError or KeyError:
                    return False
                
            else:
                return False
        
        else:
            return False
        
    def updateNotebookModificationDate(self, name: str, date: str) -> bool:
        if self.checkIfTheTableExists("__main__"):
            self.cur.execute("update __main__ set modification = ? where name = ?", (date, name))
            self.db.commit()
            
            self.cur.execute("select modification from __main__ where name = ?", (name,))
            
            try:
                fetch = self.cur.fetchone()[0]
                
                if fetch == date:
                    notebook_items[name][2].setText(date, name)
                    
                    return True
                
                else:
                    return False
        
            except TypeError or KeyError:
                return False
            
        else:
            return False


notesdb = NotesDB()
if not notesdb.createMainTable():
    print("[2] Failed to create table")
    sys.exit(2)


class NotesTabWidget(QTabWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        
        global notes_parent
        
        notes_parent = parent
        self.notebook = ""
        self.note = ""
        self.current_widget = None
        self.backups = {}
        
        self.home = QWidget(self)
        self.home_layout = QGridLayout(self.home)
        
        self.selecteds = QWidget(self)
        self.selecteds_layout = QHBoxLayout(self.selecteds)
        
        self.notebook_selected = Label(self.selecteds, _("Notebook: "))
        self.note_selected = Label(self.selecteds, _("Note: "))
        
        self.treeview = NotesTreeView(self)
        
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText(_("Search..."))
        self.entry.setClearButtonEnabled(True)
        self.entry.textEdited.connect(self.treeview.setFilter)
        
        self.note_options = NotesNoteOptions(self)
        self.note_options.setVisible(False)
        
        self.notebook_options = NotesNotebookOptions(self)
        self.notebook_options.setVisible(False)

        self.none_options = NotesNoneOptions(self)
        
        self.current_widget = self.none_options
        
        self.selecteds.setLayout(self.selecteds_layout)
        self.selecteds_layout.addWidget(self.notebook_selected)
        self.selecteds_layout.addWidget(self.note_selected)
        
        self.home.setLayout(self.home_layout)
        self.home_layout.addWidget(self.selecteds, 0, 0, 1, 3)
        self.home_layout.addWidget(HSeperator(self), 1, 0, 1, 3)
        self.home_layout.addWidget(self.entry, 2, 0, 1, 1)
        self.home_layout.addWidget(HSeperator(self), 3, 0, 1, 1)
        self.home_layout.addWidget(self.treeview, 4, 0, 1, 1)
        self.home_layout.addWidget(VSeperator(self), 2, 1, 3, 1)
        self.home_layout.addWidget(self.none_options, 2, 2, 3, 1)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
         
    @Slot(int)
    def closeTab(self, index: int) -> None:
        if index != self.indexOf(self.home):           
            try:
                if not notes[self.tabText(index).replace("&", "")].closable:
                    self.question = QMessageBox.question(self, 
                                                         _("Question"),
                                                         _("{name} note not saved.\nWhat would you like to do?")
                                                         .format(name = self.tabText(index).replace("&", "")),
                                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                                                         QMessageBox.StandardButton.Save)
                    
                    if self.question == QMessageBox.StandardButton.Save:
                        call = notes[self.tabText(index).replace("&", "")].saveDocument()
                        
                        if call:
                            self.closable = True
                    
                    elif self.question != QMessageBox.StandardButton.Yes:
                        return
                
                del notes[self.tabText(index).replace("&", "")]
                
            except KeyError:
                pass
            
            if not str(self.tabText(index).replace("&", "")).endswith(f' {_("(Backup)")}'):
                notes_parent.dock.widget().open_pages.deletePage("notes", self.tabText(index).replace("&", ""))
                
            self.removeTab(index)
            
    @Slot()
    def deleteAll(self) -> None:
        question = QMessageBox.question(self, _("Question"), _("Do you really want to delete all notes?"))
        
        if question == QMessageBox.StandardButton.Yes:
            call = notesdb.deleteAll()
            
            if call:
                self.treeview.deleteAll()
                self.treeview.setIndex("", "")
                self.insertInformations("", "")

            else:
                QMessageBox.critical(self, _("Error"), _("Failed to delete all notebooks."))
            
    @Slot(str, str)
    def insertInformations(self, notebook: str, name: str) -> None:
        self.notebook = notebook
        self.name = name      
        
        self.none_options.setVisible(False)
        self.notebook_options.setVisible(False)
        self.note_options.setVisible(False)
        
        if self.notebook == "":
            self.none_options.setVisible(True)
            self.home_layout.replaceWidget(self.current_widget, self.none_options)
            
            self.current_widget = self.none_options
            
        elif self.notebook != "" and self.name == "":
            self.notebook_options.setVisible(True)
            self.home_layout.replaceWidget(self.current_widget, self.notebook_options)
            
            self.current_widget = self.notebook_options
            
        elif self.notebook != "" and self.name != "":
            self.note_options.setVisible(True)
            self.home_layout.replaceWidget(self.current_widget, self.note_options)
            
            self.current_widget = self.note_options
            
        self.notebook_selected.setText(_("Notebook: ") + notebook)
        self.note_selected.setText(_("Note: ") + name)
        
    def refreshSettings(self) -> None:
        global setting_autosave, setting_format, setting_background, setting_foreground
        
        setting_autosave, setting_format, setting_background, setting_foreground = settingsdb.getModuleSettings("notes")
        
        self.treeview.setting_background = setting_background
        self.treeview.setting_foreground = setting_foreground

        
class NotesNoneOptions(QWidget):
    def __init__(self, parent: NotesTabWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.warning_label = Label(self, _("You can select\na notebook\nor a note\non the left."))
        self.warning_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.create_notebook_button = PushButton(self, _("Create notebook"))
        self.create_notebook_button.clicked.connect(self.parent_.notebook_options.createNotebook)
        
        self.delete_all_button = PushButton(self, _("Delete all"))
        self.delete_all_button.clicked.connect(self.parent_.deleteAll)
        
        self.setFixedWidth(200)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.warning_label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.create_notebook_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        
        
class NotesNotebookOptions(QWidget):
    def __init__(self, parent: NotesTabWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)

        self.create_note_button = PushButton(self, _("Create note"))
        self.create_note_button.clicked.connect(self.parent_.note_options.createNote)
        
        self.create_notebook_button = PushButton(self, _("Create notebook"))
        self.create_notebook_button.clicked.connect(self.createNotebook)
        
        self.set_background_button = PushButton(self, _("Set background color"))
        self.set_background_button.clicked.connect(self.setNotebookBackground)
        
        self.set_foreground_button = PushButton(self, _("Set text color"))
        self.set_foreground_button.clicked.connect(self.setNotebookForeground)
        
        self.rename_button = PushButton(self, _("Rename"))
        self.rename_button.clicked.connect(self.renameNotebook)
        
        self.reset_button = PushButton(self, _("Reset"))
        self.reset_button.clicked.connect(self.resetNotebook)
        
        self.delete_button = PushButton(self, _("Delete"))
        self.delete_button.clicked.connect(self.deleteNotebook)
        
        self.delete_all_button = PushButton(self, _("Delete all"))
        self.delete_all_button.clicked.connect(self.parent_.deleteAll)
        
        self.setFixedWidth(200)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.create_note_button)
        self.layout_.addWidget(self.create_notebook_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.set_background_button)
        self.layout_.addWidget(self.set_foreground_button)
        self.layout_.addWidget(self.rename_button)
        self.layout_.addWidget(self.reset_button)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        
    def checkIfTheNotebookExists(self, name: str, mode: str = "normal") -> bool:
        call = notesdb.checkIfTheNotebookExists(name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no notebook called {name}.").format(name = name))
        
        return call
    
    @Slot()
    def createNotebook(self) -> None:
        name, topwindow = QInputDialog.getText(
            self, _("Create Notebook"), _("Please enter a name for creating a notebook."))
        
        if "'" in name or "@" in name:
            QMessageBox.critical(self, _("Error"), _("The notebook name can not contain these characters: ' and @"))
            return
        
        elif "__main__" == name:
            QMessageBox.critical(self, _("Error"), _("The notebook name can not be to __main__."))
            return
        
        elif topwindow and name != "":
            call = self.checkIfTheNotebookExists(name, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{name} notebook already created.").format(name = name))
        
            else:
                call = notesdb.createNotebook(name)
                
                if call:
                    self.parent_.treeview.appendNotebook(name)
                    self.parent_.treeview.setIndex(name, "")
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} notebook.").format(name = name))
        
    @Slot()
    def deleteNotebook(self) -> None:
        name = self.parent_.notebook
        
        if not self.checkIfTheNotebookExists(name):
            return
        
        question = QMessageBox.question(self, _("Question"), _("Do you really want to delete the {name} notebook?").format(name = name))
        
        if question == QMessageBox.StandardButton.Yes:
            call = notesdb.deleteNotebook(name)
            
            if call:
                self.parent_.treeview.deleteNotebook(name)
                self.parent_.treeview.setIndex("", "")

            else:
                QMessageBox.critical(self, _("Error"), _("Failed to delete {name} notebook.").format(name = name))
        
    @Slot()
    def renameNotebook(self) -> None:
        name = self.parent_.notebook
        
        if not self.checkIfTheNotebookExists(name):
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} Notebook").format(name = name.title()), 
                                                  _("Please enter a new name for {name} notebook.").format(name = name))
        
        if "'" in newname or "@" in newname:
            QMessageBox.critical(self, _("Error"), _("The notebook name can not contain these characters: ' and @"))
            return
        
        elif "__main__" == newname:
            QMessageBox.critical(self, _("Error"), _("The notebook name can not be to __main__."))
            return
        
        elif topwindow and newname != "":
            if not self.checkIfTheNotebookExists(newname, "no-popup"):
                call = notesdb.renameNotebook(name, newname)
                
                if call:
                    self.parent_.treeview.updateNotebook(name, newname)
                    self.parent_.treeview.setIndex(newname, "")
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to rename {name} notebook.")
                                        .format(name = name))
                    
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newname} notebook, renaming {name} notebook cancalled.")
                                     .format(newname = newname, name = name))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} notebook.")
                                 .format(name = name))
        
    @Slot()
    def resetNotebook(self) -> None:
        name = self.parent_.notebook
        
        if not self.checkIfTheNotebookExists(name):
            return
        
        call = notesdb.resetNotebook(name)
        
        if call:
            self.parent_.treeview.deleteNotebook(name)
            self.parent_.treeview.appendNotebook(name)
            self.parent_.treeview.setIndex(name, "")
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset {name} notebook.").format(name = name))
         
    @Slot()
    def setNotebookBackground(self) -> None:
        name = self.parent_.notebook
        
        if not self.checkIfTheNotebookExists(name):
            return
        
        background = notesdb.getNotebookBackground(name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(background if background != "global" and background != "default"
                   else (setting_background if background == "global" and setting_background != "default" 
                         else "#FFFFFF")),
            _("Select Background Color for {name} Notebook").format(name = name.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = notesdb.setNotebookBackground(name, color)
                    
            if call:
                self.parent_.treeview.updateNotebookBackground(name, color)
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {name} notebook.").format(name = name))
        
    @Slot()
    def setNotebookForeground(self) -> None:
        name = self.parent_.notebook

        if not self.checkIfTheNotebookExists(name):
            return
        
        foreground = notesdb.getNotebookForeground(name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(foreground if foreground != "global" and foreground != "default"
                   else (setting_foreground if foreground == "global" and setting_foreground != "default" 
                         else "#FFFFFF")),
            _("Select Text Color for {name} Notebook").format(name = name.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = notesdb.setNotebookForeground(name, color)
                    
            if call:
                self.parent_.treeview.updateNotebookForeground(name, color)
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set text color for {name} notebook.").format(name = name))


class NotesNoteOptions(QWidget):
    def __init__(self, parent: NotesTabWidget) -> None:
        super().__init__(parent)

        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.create_note_button = PushButton(self, _("Create note"))
        self.create_note_button.clicked.connect(self.createNote)
        
        self.open_button = PushButton(self, _("Open"))
        self.open_button.clicked.connect(self.openNote)
        
        self.set_background_button = PushButton(self, _("Set background color"))
        self.set_background_button.clicked.connect(self.setNoteBackground)
        
        self.set_foreground_button = PushButton(self, _("Set text color"))
        self.set_foreground_button.clicked.connect(self.setNoteForeground)
        
        self.rename_button = PushButton(self, _("Rename"))
        self.rename_button.clicked.connect(self.renameNote)

        self.show_backup_button = PushButton(self, _("Show backup"))
        self.show_backup_button.clicked.connect(self.showBackup)

        self.restore_content_button = PushButton(self, _("Restore content"))
        self.restore_content_button.clicked.connect(self.restoreContent)
        
        self.clear_content_button = PushButton(self, _("Clear content"))
        self.clear_content_button.clicked.connect(self.clearContent)
        
        self.delete_button = PushButton(self, _("Delete"))
        self.delete_button.clicked.connect(self.deleteNote)
        
        self.delete_all_button = PushButton(self, _("Delete all"))
        self.delete_all_button.clicked.connect(self.parent_.deleteAll)

        self.setFixedWidth(200)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.create_note_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.open_button)
        self.layout_.addWidget(self.set_background_button)
        self.layout_.addWidget(self.set_foreground_button)
        self.layout_.addWidget(self.rename_button)
        self.layout_.addWidget(self.show_backup_button)
        self.layout_.addWidget(self.restore_content_button)
        self.layout_.addWidget(self.clear_content_button)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)

    def checkIfTheNoteExists(self, notebook: str, name: str, mode: str = "normal") -> bool:
        call = notesdb.checkIfTheNoteExists(notebook, name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no note called {name}.").format(name = name))
        
        return call
    
    def checkIfTheNoteBackupExists(self, notebook: str, name: str) -> bool:  
        call = notesdb.checkIfTheNoteBackupExists(notebook, name)
        
        if not call:
            QMessageBox.critical(self, _("Error"), _("There is no backup for {name} note.").format(name = name))
        
        return call
    
    @Slot()
    def clearContent(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        question = QMessageBox.question(self, _("Question"), _("Do you really want to clear the content of the {name} note?").format(name = name))
        
        if question == QMessageBox.StandardButton.Yes:
            call = notesdb.clearContent(notebook, name)
        
            if call:
                QMessageBox.information(self, _("Successful"), _("Content of {name} note cleared.").format(name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to clear content of {name} note.").format(name = name))
    
    @Slot()
    def createNote(self):
        notebook = self.parent_.notebook
        
        if not notesdb.checkIfTheNotebookExists(notebook):
            QMessageBox.critical(self, _("Error"), _("There is no notebook called {name}.").format(name = notebook))
            return
        
        name, topwindow = QInputDialog.getText(
            self, _("Create Note"), _("Please enter a name for creating a note."))
        
        if "@" in name:
            QMessageBox.critical(self, _("Error"), _("The note name can not contain @ character."))
            return
        
        elif topwindow and name != "":
            call = self.checkIfTheNoteExists(notebook, name, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{name} note already created.").format(name = name))
        
            else:
                call = notesdb.createNote(notebook, name)
                
                if call:
                    self.parent_.treeview.appendNote(notebook, name)
                    self.parent_.treeview.setIndex(notebook, name)
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} note.").format(name = name))
            
    @Slot()
    def deleteNote(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        question = QMessageBox.question(self, _("Question"), _("Do you really want to delete the {name} note?").format(name = name))
        
        if question == QMessageBox.StandardButton.Yes:
            call = notesdb.deleteNote(notebook, name)
                
            if call:
                self.parent_.treeview.deleteNote(notebook, name)
                self.parent_.treeview.setIndex(notebook, "")
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to delete {name} note.").format(name = name))
        
    @Slot()
    def openNote(self, notebook: str = "", name: str = "") -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        notes_parent.tabwidget.setCurrentIndex(1)
        
        if f"{name} @ {notebook}" in notes:
            self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
            
        else:            
            notes_parent.dock.widget().open_pages.appendPage("notes", f"{name} @ {notebook}")
            notes[f"{name} @ {notebook}"] = NormalPage(self, "notes", notebook, name, setting_autosave, setting_format, notesdb)
            self.parent_.addTab(notes[f"{name} @ {notebook}"], f"{name} @ {notebook}")
            self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
    
    @Slot()
    def renameNote(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} Note").format(name = name.title()), 
                                                  _("Please enter a new name for {name} note.").format(name = name))
        
        if "'" in newname or "@" in newname:
            QMessageBox.critical(self, _("Error"), _("The notebook name can not contain these characters: ' and @"))
            return
        
        elif topwindow and newname != "":
            if not self.checkIfTheNoteExists(notebook, newname, "no-popup"):
                call = notesdb.renameNote(notebook, name, newname)
                
                if call:
                    self.parent_.treeview.updateNote(notebook, name, newname)
                    self.parent_.treeview.setIndex(notebook, newname)
    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to rename {name} note.")
                                        .format(name = name))
            
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newname} note, renaming {name} note cancalled.")
                                     .format(newname = newname, name = name))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} note.")
                                 .format(name = name))
            
    @Slot()
    def restoreContent(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        if not self.checkIfTheNoteBackupExists(notebook, name):
            return
        
        call = notesdb.restoreContent(notebook, name)
        
        if call:
            QMessageBox.information(self, _("Successful"), _("Backup of {name} note restored.").format(name = name))
            
        elif not call:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup of {name} note.").format(name = name))
            
    @Slot()
    def setNoteBackground(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        background = notesdb.getNoteBackground(notebook, name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(background if background != "global" and background != "default"
                   else (setting_background if background == "global" and setting_background != "default" 
                         else "#FFFFFF")),
            _("Select Background Color for {name} Note").format(name = name.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = notesdb.setNoteBackground(notebook, name, color)
                    
            if call:
                self.parent_.treeview.updateNoteBackground(notebook, name, color)
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {name} note.").format(name = name))
        
    @Slot()
    def setNoteForeground(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name

        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        foreground = notesdb.getNoteForeground(notebook, name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(foreground if foreground != "global" and foreground != "default"
                   else (setting_foreground if foreground == "global" and setting_foreground != "default" 
                         else "#FFFFFF")),
            _("Select Text Color for {name} Note").format(name = name.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = notesdb.setNoteForeground(notebook, name, color)
                    
            if call:
                self.parent_.treeview.updateNoteForeground(notebook, name, color)
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set text color for {name} note.").format(name = name))
            
    @Slot()
    def showBackup(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        if not self.checkIfTheNoteBackupExists(notebook, name):
            return
        
        notes_parent.tabwidget.setCurrentIndex(1)

        self.parent_.backups[f'{name} @ {notebook}'] = BackupPage(self, "notes", notebook, name, setting_format, notesdb)
        self.parent_.addTab(self.parent_.backups[f'{name} @ {notebook}'], f'{name} @ {notebook} {_("(Backup)")}')
        self.parent_.setCurrentWidget(self.parent_.backups[f'{name} @ {notebook}'])


class NotesTreeView(TreeView):
    def __init__(self, parent: NotesTabWidget, caller: str = "own") -> None:
        super().__init__(parent, "notes", caller)
        
        self.db = notesdb
        self.parent_counts = notebook_counts
        self.parent_items = notebook_items
        self.child_counts = note_counts
        self.child_items = note_items
        self.child_menus = note_menus
        self.setting_background = setting_background
        self.setting_foreground = setting_foreground
        
        if self.caller == "own":
            self.menu = notes_parent.menuBar().addMenu(_("Notes"))
            
            global notes_model
            
            notes_model = QStandardItemModel(self)
            notes_model.setHorizontalHeaderLabels([_("Name"), _("Creation"), _("Modification")])
            
            self.appendAll()
            
        self.proxy.setSourceModel(notes_model)
        
        self.setStatusTip(_("Double-click to opening a note."))

    def appendAll(self) -> None:
        super().appendAll()
        
        for row in notebook_items.values():
            notes_model.appendRow(row)
            
        if self.caller == "own":
            for notebook, name in note_items.keys():
                note_menus[(notebook, name)] = self.menu.addAction(
                    f"{name} @ {notebook}", lambda name = name, notebook = notebook: self.doubleClickEvent(notebook, name))
            
    def appendNote(self, notebook: str, name: str) -> None:     
        super().appendChild(notebook, name)
        
        if self.caller == "own":
            note_menus[(notebook, name)] = self.menu.addAction(
                f"{name} @ {notebook}", lambda name = name, notebook = notebook: self.doubleClickEvent(notebook, name))
            
    def appendNotebook(self, name: str) -> None:
        super().appendParent(name, notes_model.rowCount())
        
        notes_model.appendRow(notebook_items[name])
        
    def deleteAll(self) -> None:        
        super().deleteAll()
        
        self.child_menus.clear()
        self.menu.clear()
        
        notes_model.clear()
        notes_model.setHorizontalHeaderLabels([_("Name"), _("Creation"), _("Modification")])
        
    def deleteNote(self, notebook: str, name: str) -> None:
        super().deleteChild(notebook, name)
        
        if self.caller == "own":
            self.menu.removeAction(note_menus[(notebook, name)])
            
            del note_menus[(notebook, name)]
        
    def deleteNotebook(self, name: str) -> None:
        super().deleteParent(name)
        
        notes_model.removeRow(notebook_counts[name])
        
        for parent_ in notebook_counts.keys():
            if notebook_counts[parent_] > notebook_counts[name]:
                notebook_counts[parent_] -= 1
         
        del notebook_counts[name]
        del notebook_items[name]
        
        if self.caller == "own":
            for key in note_menus.copy().keys():
                if key[0] == name:
                    self.menu.removeAction(note_menus[key])
                    
                    del note_menus[key]
    
    def doubleClickEvent(self, notebook: str = "", name: str = "") -> None:
        if notebook != "":
            if name == "":
                try:
                    name = next(name_range for notebook_range, name_range in note_items.keys() 
                                if str(notebook_range).startswith(notebook))

                except:
                    call = notesdb.createNote(notebook, _("Unnamed"))
                    
                    if call:
                        name = _("Unnamed")
                        
                        self.appendNote(notebook, name)
                        self.setIndex(notebook, name)
                    
                    else:
                        QMessageBox.critical(self, _("Error"), _("Failed to create {name} note.").format(name = _("Unnamed")))
                        return
                
            if not self.parent_.note_options.checkIfTheNoteExists(notebook, name):
                return
                
            notes_parent.tabwidget.setCurrentIndex(1)
            
            if f"{name} @ {notebook}" in notes:
                self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
                
            else:            
                notes_parent.dock.widget().open_pages.appendPage("notes", f"{name} @ {notebook}")
                notes[f"{name} @ {notebook}"] = NormalPage(self, "notes", notebook, name, setting_autosave, setting_format, notesdb)
                self.parent_.addTab(notes[f"{name} @ {notebook}"], f"{name} @ {notebook}")
                self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
                
        else:
            QMessageBox.critical(self, _("Error"), _("Please select a note or a notebook."))
        
    def updateNote(self, notebook: str, name: str, newname: str) -> None:
        super().updateChild(notebook, name, newname)
        
        if self.caller == "own":
            note_menus[(notebook, newname)] = note_menus.pop((notebook, name))
        
    def updateNoteBackground(self, notebook: str, name: str, color: str) -> None:
        super().updateChildBackground(notebook, name, color)
        
    def updateNoteForeground(self, notebook: str, name: str, color: str) -> None:
        super().updateParentBackground(notebook, name, color)
                
    def updateNotebook(self, name: str, newname: str) -> None:
        super().updateParent(name, newname)
        
    def updateNotebookBackground(self, name: str, color: str) -> None:
        super().updateParentBackground(name, color)
                
    def updateNotebookForeground(self, name: str, color: str) -> None:
        super().updateParentForeground(name, color)