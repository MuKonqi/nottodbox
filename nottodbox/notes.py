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
from widgets.dialogs import ColorDialog
from widgets.other import HSeperator, Label, PushButton, VSeperator
from widgets.pages import NormalPage, BackupPage
from gettext import gettext as _
from PySide6.QtGui import QStandardItem, QStandardItemModel, QMouseEvent, QColor
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import *


notes = {}
note_counts = {}
note_items = {}
note_menus = {}
notebook_counts = {}
notebook_items = {}

username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"

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
        
    def getAll(self) -> dict:
        all = {}
        
        self.cur.execute("select name, creation, modification, background, foreground from __main__")
        parents = self.cur.fetchall()
        
        for notebook, creation, modification, background, foreground in parents:
            self.cur.execute(f"select name, creation, modification, background, foreground from '{notebook}'")
            all[(notebook, creation, modification, background, foreground)] = self.cur.fetchall()
            
        return all
    
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
    
    def getNotebook(self, name: str) -> tuple:
        self.cur.execute(f"""select creation, modification, 
                         background, foreground from __main__ where name = ?""", (name,))
        creation, modification, background, foreground = self.cur.fetchone()
        
        self.cur.execute(f"""select name, creation, modification, 
                         background, foreground from '{name}'""")
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
    
    def getNoteForeground(self, notebook: str, name: str) -> str:
        self.cur.execute(f"select foreground from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
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
                fetch_format == setting_format
            
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
                        note_items[(notebook, name)][2].setText(date)

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
                    notebook_items[name][2].setText(date)
                    
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
        
        self.tabCloseRequested.connect(self.closeTab)
        
        global notes_parent
        
        notes_parent = parent
        self.backups = {}
        self.note = ""
        self.notebook = ""
        self.current_widget = None
        
        self.home = QWidget(self)
        self.layout_ = QGridLayout(self.home)
        
        self.selecteds = QWidget(self)
        self.selecteds_layout = QHBoxLayout(self.selecteds)
        
        self.notebook_selected = Label(self.selecteds, _("Notebook: "))
        self.note_selected = Label(self.selecteds, _("Note: "))
        
        self.treeview = NotesTreeView(self)
        
        self.entry = QLineEdit(self.home)
        self.entry.setPlaceholderText(_("Search in the list below"))
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
        
        self.home.setLayout(self.layout_)
        self.layout_.addWidget(self.selecteds, 0, 0, 1, 3)
        self.layout_.addWidget(HSeperator(self), 1, 0, 1, 3)
        self.layout_.addWidget(self.entry, 2, 0, 1, 1)
        self.layout_.addWidget(self.treeview, 3, 0, 1, 1)
        self.layout_.addWidget(VSeperator(self), 2, 1, 2, 1)
        self.layout_.addWidget(self.none_options, 2, 2, 2, 1)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
         
    def closeTab(self, index: int) -> None:
        if index != self.indexOf(self.home):           
            try:
                if not notes[self.tabText(index).replace("&", "")].closable:
                    self.question = QMessageBox.question(self, 
                                                         _("Question"),
                                                         _("{name} note not saved.\nDo you want to directly closing or closing after saving it or cancel?")
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
                notes_parent.dock.widget().removePage(self.tabText(index).replace("&", ""), self)
                
            self.removeTab(index)
            
    def insertInformations(self, notebook: str, name: str) -> None:
        self.notebook = notebook
        self.name = name      
        
        self.none_options.setVisible(False)
        self.notebook_options.setVisible(False)
        self.note_options.setVisible(False)
        
        if self.notebook == "":
            self.none_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.none_options)
            
            self.current_widget = self.none_options
            
        elif self.notebook != "" and self.name == "":
            self.notebook_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.notebook_options)
            
            self.current_widget = self.notebook_options
            
        elif self.notebook != "" and self.name != "":
            self.note_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.note_options)
            
            self.current_widget = self.note_options
            
        self.notebook_selected.setText(_("Notebook: ") + notebook)
        self.note_selected.setText(_("Note: ") + name)
        
    def refreshSettings(self) -> None:
        global setting_autosave, setting_format, setting_background, setting_foreground
        
        setting_autosave, setting_format, setting_background, setting_foreground = settingsdb.getModuleSettings("notes")

        
class NotesNoneOptions(QWidget):
    def __init__(self, parent: NotesTabWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.warning_label = Label(self, _("You can select\na notebook\nor a note\non the left."))
        self.warning_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.create_notebook = PushButton(self, _("Create notebook"))
        self.create_notebook.clicked.connect(self.parent_.notebook_options.createNotebook)
        
        self.delete_all = PushButton(self, _("Delete all"))
        self.delete_all.clicked.connect(self.parent_.notebook_options.deleteAll)
        
        self.setFixedWidth(180)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.warning_label)
        self.layout_.addWidget(self.create_notebook)
        self.layout_.addWidget(self.delete_all)
        
        
class NotesNotebookOptions(QWidget):
    def __init__(self, parent: NotesTabWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)

        self.create_note = PushButton(self, _("Create note"))
        self.create_note.clicked.connect(self.parent_.note_options.createNote)
        
        self.create_notebook = PushButton(self, _("Create notebook"))
        self.create_notebook.clicked.connect(self.createNotebook)
        
        self.set_background = PushButton(self, _("Set background color"))
        self.set_background.clicked.connect(self.setNotebookBackground)
        
        self.set_foreground = PushButton(self, _("Set text color"))
        self.set_foreground.clicked.connect(self.setNotebookForeground)
        
        self.rename_notebook = PushButton(self, _("Rename notebook"))
        self.rename_notebook.clicked.connect(self.renameNotebook)
        
        self.reset_notebook = PushButton(self, _("Reset notebook"))
        self.reset_notebook.clicked.connect(self.resetNotebook)
        
        self.delete_notebook = PushButton(self, _("Delete notebook"))
        self.delete_notebook.clicked.connect(self.deleteNotebook)
        
        self.delete_all = PushButton(self, _("Delete all"))
        self.delete_all.clicked.connect(self.deleteAll)
        
        self.setFixedWidth(180)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.create_note)
        self.layout_.addWidget(self.create_notebook)
        self.layout_.addWidget(self.set_background)
        self.layout_.addWidget(self.set_foreground)
        self.layout_.addWidget(self.rename_notebook)
        self.layout_.addWidget(self.reset_notebook)
        self.layout_.addWidget(self.delete_notebook)
        self.layout_.addWidget(self.delete_all)
        
    def checkIfTheNotebookExists(self, name: str, mode: str = "normal") -> bool:
        call = notesdb.checkIfTheNotebookExists(name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no notebook called {name}.").format(name = name))
        
        return call
                    
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
                    self.parent_.insertInformations(name, "")
                    
                    QMessageBox.information(self, _("Successful"), _("{name} notebook created.").format(name = name))
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} notebook.").format(name = name))
                    
    def deleteAll(self) -> None:
        call = notesdb.deleteAll()
        
        if call:
            self.parent_.treeview.updateAll()
            self.parent_.insertInformations("", "")
            
            QMessageBox.information(self, _("Successful"), _("All notebooks deleted."))

        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all notebooks."))
        
    def deleteNotebook(self) -> None:
        name = self.parent_.notebook
        
        if not self.checkIfTheNotebookExists(name):
            return
        
        call = notesdb.deleteNotebook(name)
        
        if call:
            self.parent_.treeview.deleteNotebook(name)
            self.parent_.insertInformations("", "")
            
            QMessageBox.information(self, _("Successful"), _("{name} notebook deleted.").format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {name} notebook.").format(name = name))
        
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
                    self.parent_.insertInformations(newname, "")
                    
                    QMessageBox.information(self, _("Successful"), _("{name} notebook renamed as {newname}.")
                                            .format(name = name, newname = newname))
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to rename {name} notebook.")
                                        .format(name = name))
                    
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newname} notebook, renaming {name} notebook cancalled.")
                                     .format(newname = newname, name = name))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} notebook.")
                                 .format(name = name))
        
    def resetNotebook(self) -> None:
        name = self.parent_.notebook
        
        if not self.checkIfTheNotebookExists(name):
            return
        
        call = notesdb.resetNotebook(name)
        
        if call:
            self.parent_.treeview.deleteNotebook(name)
            self.parent_.treeview.appendNotebook(name)
            self.parent_.insertInformations(name, "")
            
            QMessageBox.information(self, _("Successful"), _("{name} notebook reset.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset {name} notebook.").format(name = name))
            
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
                
                QMessageBox.information(
                    self, _("Successful"), _("Background color setted to {color} for {name} notebook.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {name} notebook.").format(name = name))
        
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
                
                QMessageBox.information(
                    self, _("Successful"), _("Text color setted to {color} for {name} notebook.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set text color for {name} notebook.").format(name = name))


class NotesNoteOptions(QWidget):
    def __init__(self, parent: NotesTabWidget) -> None:
        super().__init__(parent)

        self.parent_ = parent
        
        self.layout_ = QVBoxLayout(self)
        
        self.create_note = PushButton(self, _("Create note"))
        self.create_note.clicked.connect(self.createNote)
        
        self.open_note = PushButton(self, _("Open note"))
        self.open_note.clicked.connect(self.openNote)
        
        self.set_background = PushButton(self, _("Set background color"))
        self.set_background.clicked.connect(self.setNoteBackground)
        
        self.set_foreground = PushButton(self, _("Set text color"))
        self.set_foreground.clicked.connect(self.setNoteForeground)
        
        self.rename = PushButton(self, _("Rename note"))
        self.rename.clicked.connect(self.renameNote)

        self.show_backup = PushButton(self, _("Show backup"))
        self.show_backup.clicked.connect(self.showBackup)

        self.restore_content = PushButton(self, _("Restore content"))
        self.restore_content.clicked.connect(self.restoreContent)
        
        self.clear_content = PushButton(self, _("Clear content"))
        self.clear_content.clicked.connect(self.clearContent)
        
        self.delete_note = PushButton(self, _("Delete note"))
        self.delete_note.clicked.connect(self.deleteNote)

        self.setFixedWidth(180)
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.create_note)
        self.layout_.addWidget(self.open_note)
        self.layout_.addWidget(self.set_background)
        self.layout_.addWidget(self.set_foreground)
        self.layout_.addWidget(self.rename)
        self.layout_.addWidget(self.show_backup)
        self.layout_.addWidget(self.restore_content)
        self.layout_.addWidget(self.clear_content)
        self.layout_.addWidget(self.delete_note)

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
    
    def clearContent(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        call = notesdb.clearContent(notebook, name)
    
        if call:
            QMessageBox.information(self, _("Successful"), _("Content of {name} note cleared.").format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to clear content of {name} note.").format(name = name))
    
    def createNote(self):
        notebook = self.parent_.notebook
        
        if not notesdb.checkIfTheNotebookExists(notebook):
            QMessageBox.critical(self, _("Error"), _("There is no notebook called {name}.").format(name = notebook))
            return
        
        name, topwindow = QInputDialog.getText(
            self, _("Create Note"), _("Please enter a name for creating a note."))
        
        if "@" in name:
            QMessageBox.critical(self, _("Error"), _('The note name can not contain @ character.'))
            return
        
        elif topwindow and name != "":
            call = self.checkIfTheNoteExists(notebook, name, "inverted")
        
            if call:
                QMessageBox.critical(self, _("Error"), _("{name} note already created.").format(name = name))
        
            else:
                call = notesdb.createNote(notebook, name)
                
                if call:
                    self.parent_.treeview.appendNote(notebook, name)
                    self.parent_.insertInformations(notebook, name)
                    
                    QMessageBox.information(self, _("Successful"), _("{name} note created.").format(name = name))
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} note.").format(name = name))
            
    def deleteNote(self) -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        call = notesdb.deleteNote(notebook, name)
            
        if call:
            self.parent_.treeview.deleteNote(notebook, name)
            self.parent_.insertInformations(notebook, "")
            
            QMessageBox.information(self, _("Successful"), _("{name} note deleted.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {name} note.").format(name = name))
        
    def openNote(self, notebook: str = "", name: str = "") -> None:
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        notes_parent.tabwidget.setCurrentIndex(1)
        
        if f"{name} @ {notebook}" in notes:
            self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
            
        else:            
            notes_parent.dock.widget().addPage(f"{name} @ {notebook}", self.parent_)
            notes[f"{name} @ {notebook}"] = NormalPage(self, "notes", notebook, name, setting_autosave, setting_format, notesdb)
            self.parent_.addTab(notes[f"{name} @ {notebook}"], f"{name} @ {notebook}")
            self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
    
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
                    self.parent_.insertInformations(notebook, newname)
                    
                    QMessageBox.information(self, _("Successful"), _("{name} note renamed as {newname}.")
                                            .format(name = name, newname = newname))
    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to rename {name} note.")
                                        .format(name = name))
            
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newname} note, renaming {name} note cancalled.")
                                     .format(newname = newname, name = name))
                
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} note.")
                                 .format(name = name))
            
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
                
                QMessageBox.information(
                    self, _("Successful"), _("Background color setted to {color} for {name} note.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set background color for {name} note.").format(name = name))
        
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
                
                QMessageBox.information(
                    self, _("Successful"), _("Text color setted to {color} for {name} note.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set text color for {name} note.").format(name = name))
            
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


class NotesTreeView(QTreeView):
    def __init__(self, parent: NotesTabWidget, caller: str = "notes") -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.caller = caller

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setRecursiveFilteringEnabled(True)
        
        if self.caller == "notes":
            global notes_model
            
            notes_model = QStandardItemModel(self)
            notes_model.setHorizontalHeaderLabels([_("Name"), _("Creation"), _("Modification")])
            
        self.proxy.setSourceModel(notes_model)
        
        self.setModel(self.proxy)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip(_("Double-click to opening a note."))
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        if self.caller == "notes":
            self.selectionModel().currentRowChanged.connect(
                lambda: self.parent_.insertInformations(self.getParentText(), self.getCurrentText()))
        
        self.doubleClicked.connect(lambda: self.openNote(self.getParentText(), self.getCurrentText()))
        
        self.appendAll()

    def appendAll(self) -> None:
        global notes_menu
        
        call = notesdb.getAll()
        
        if self.caller == "notes":
            if not "notes_menu" in globals():
                notes_menu = notes_parent.menuBar().addMenu(_("Notes"))
            
            notes_menu.clear() 
        
        if call != None and self.caller == "notes":
            model_count = -1
            
            all = [*call]
            
            for (notebook, creation_notebook, modification_notebook, 
                 background_notebook, foreground_notebook) in all:
                model_count += 1
                notebook_count = -1
                
                notebook_counts[notebook] = model_count
                notebook_items[notebook] = [QStandardItem(notebook),
                                            QStandardItem(creation_notebook),
                                            QStandardItem(modification_notebook)]
                
                for item in notebook_items[notebook]:
                    if background_notebook == "global" and setting_background != "default":
                        item.setBackground(QColor(setting_background))
                    elif background_notebook != "global" and background_notebook != "default":
                        item.setBackground(QColor(background_notebook))
                    
                    if foreground_notebook == "global" and setting_foreground != "default":
                        item.setForeground(QColor(setting_foreground))
                    elif foreground_notebook != "global" and foreground_notebook != "default":
                        item.setForeground(QColor(foreground_notebook))
                
                for (name, creation_note, modification_note, 
                     background_note, foreground_note) in call[notebook, creation_notebook, modification_notebook, 
                                                               background_notebook, foreground_notebook]:
                    notebook_count += 1
                    
                    note_counts[(notebook, name)] = notebook_count
                    note_items[(notebook, name)] = [QStandardItem(name), 
                                                    QStandardItem(creation_note), 
                                                    QStandardItem(modification_note)]
                    
                    for item in note_items[(notebook, name)]:
                        if background_note == "global" and setting_background != "default":
                            item.setBackground(QColor(setting_background))
                        elif background_note != "global" and background_note != "default":
                            item.setBackground(QColor(background_note))
                        
                        if foreground_note == "global" and setting_foreground != "default":
                            item.setForeground(QColor(setting_foreground))
                        elif foreground_note != "global" and foreground_note != "default":
                            item.setForeground(QColor(foreground_note))
                
                    notebook_items[notebook][0].appendRow(note_items[(notebook, name)])
                    
                    if self.caller == "notes":
                        note_menus[(notebook, name)] = notes_menu.addAction(
                            f"{name} @ {notebook}", lambda name = name, notebook = notebook: self.openNote(notebook, name))
                
                notes_model.appendRow(notebook_items[notebook])
            
    def appendNote(self, notebook: str, name: str) -> None:
        creation_note, modification_note, background_note, foreground_note = notesdb.getNote(notebook, name)
        
        note_counts[(notebook, name)] = notebook_items[notebook][0].rowCount()
        note_items[(notebook, name)] = [QStandardItem(name), 
                                        QStandardItem(creation_note), 
                                        QStandardItem(modification_note)]
        
        for item in note_items[(notebook, name)]:
            if background_note == "global" and setting_background != "default":
                item.setBackground(QColor(setting_background))
            elif background_note != "global" and background_note != "default":
                item.setBackground(QColor(background_note))
            
            if foreground_note == "global" and setting_foreground != "default":
                item.setForeground(QColor(setting_foreground))
            elif foreground_note != "global" and foreground_note != "default":
                item.setForeground(QColor(foreground_note))
    
        notebook_items[notebook][0].appendRow(note_items[(notebook, name)])
        
        if self.caller == "notes":
            note_menus[(notebook, name)] = notes_menu.addAction(
                f"{name} @ {notebook}", lambda name = name, notebook = notebook: self.openNote(notebook, name))
            
    def appendNotebook(self, notebook: str) -> None:
        (creation_notebook, modification_notebook, 
         background_notebook, foreground_notebook, notes) = notesdb.getNotebook(notebook)
        
        model_count = notes_model.rowCount()
        notebook_count = -1
        
        notebook_counts[notebook] = model_count
        notebook_items[notebook] = [QStandardItem(notebook),
                                    QStandardItem(creation_notebook),
                                    QStandardItem(modification_notebook)]
        
        for item in notebook_items[notebook]:
            if background_notebook == "global" and setting_background != "default":
                item.setBackground(QColor(setting_background))
            elif background_notebook != "global" and background_notebook != "default":
                item.setBackground(QColor(background_notebook))
            
            if foreground_notebook == "global" and setting_foreground != "default":
                item.setForeground(QColor(setting_foreground))
            elif foreground_notebook != "global" and foreground_notebook != "default":
                item.setForeground(QColor(foreground_notebook))
        
        for name, creation_note, modification_note, background_note, foreground_note in notes:
            notebook_count += 1
            
            note_counts[(notebook, name)] = notebook_count
            note_items[(notebook, name)] = [QStandardItem(name), 
                                            QStandardItem(creation_note), 
                                            QStandardItem(modification_note)]
            
            for item in note_items[(notebook, name)]:
                if background_note == "global" and setting_background != "default":
                    item.setBackground(QColor(setting_background))
                elif background_note != "global" and background_note != "default":
                    item.setBackground(QColor(background_note))
                
                if foreground_note == "global" and setting_foreground != "default":
                    item.setForeground(QColor(setting_foreground))
                elif foreground_note != "global" and foreground_note != "default":
                    item.setForeground(QColor(foreground_note))
        
            notebook_items[notebook][0].appendRow(note_items[(notebook, name)])
            
            if self.caller == "notes":
                note_menus[(notebook, name)] = notes_menu.addAction(
                    f"{name} @ {notebook}", lambda name = name, notebook = notebook: self.openNote(notebook, name))
        
        notes_model.appendRow(notebook_items[notebook])
        
    def deleteNote(self, notebook: str, name: str) -> None:
        notebook_items[notebook][0].removeRow(note_counts[(notebook, name)])
        
        del note_items[(notebook, name)]
        del note_counts[(notebook, name)]
        
        if self.caller == "notes":
            notes_menu.removeAction(note_menus[(notebook, name)])
            
            del note_menus[(notebook, name)]
        
    def deleteNotebook(self, notebook: str) -> None:
        notes_model.removeRow(notebook_counts[notebook])
        
        del notebook_counts[notebook]
        del notebook_items[notebook]
        
        for key in note_items.copy().keys():
            if key[0] == notebook:
                del note_items[key]
                
        for key in note_counts.copy().keys():
            if key[0] == notebook:
                del note_counts[key]
                
        if self.caller == "notes":
            for key in note_menus.copy().keys():
                if key[0] == notebook:
                    notes_menu.removeAction(note_menus[key])
                    
                    del note_menus[key]
                    
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
                return self.proxy.itemData(self.currentIndex())[0]
            
            else:
                return ""
            
        except KeyError:
            return ""
                
    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        index = self.indexAt(e.pos())
        
        if index.column() == 0:
            super().mousePressEvent(e)
            
        else:
            QMessageBox.warning(self, _("Warning"), _("Please select a note or a notebook only by clicking on the first column."))
    
    def openNote(self, notebook: str = "", name: str = "") -> None:
        if notebook != "":
            if name == "":
                try:
                    name = next(name_range for notebook_range, name_range in note_items.keys() 
                                if str(notebook_range).startswith(notebook))

                except:
                    call = notesdb.createNote(notebook, _("Unnamed"))
                    
                    if call:
                        name = _("Unnamed")
                        
                        self.parent_.treeview.appendNote(notebook, name)
                        self.parent_.insertInformations(notebook, name)
                    
                    else:
                        QMessageBox.critical(self, _("Error"), _("Failed to create {name} note.").format(name = _("Unnamed")))
                        return
                
            if not self.parent_.note_options.checkIfTheNoteExists(notebook, name):
                return
                
            notes_parent.tabwidget.setCurrentIndex(1)
            
            if f"{name} @ {notebook}" in notes:
                self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
                
            else:            
                notes_parent.dock.widget().addPage(f"{name} @ {notebook}", self.parent_)
                notes[f"{name} @ {notebook}"] = NormalPage(self, "notes", notebook, name, setting_autosave, setting_format, notesdb)
                self.parent_.addTab(notes[f"{name} @ {notebook}"], f"{name} @ {notebook}")
                self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
                
        else:
            QMessageBox.critical(self, _("Error"), _("Please select a note or a notebook."))
                
    def setFilter(self, text: str) -> None:
        self.proxy.beginResetModel()
        self.proxy.setFilterFixedString(text)
        self.proxy.endResetModel()
        
    def updateAll(self) -> None:
        notes_model.clear()
        notes_model.setHorizontalHeaderLabels([_("Name"), _("Creation"), _("Modification")])
        
        notes_menu.clear()
        
        self.appendAll()
        
    def updateNote(self, notebook: str, name: str, newname: str) -> None:
        note_counts[(notebook, newname)] = note_counts.pop((notebook, name))
        note_items[(notebook, newname)] = note_items.pop((notebook, name))
        note_menus[(notebook, newname)] = note_menus.pop((notebook, name))
        
        note_items[(notebook, newname)][0].setText(newname)
        
    def updateNoteBackground(self, notebook: str, name: str, color: str) -> None:
        for item in note_items[(notebook, name)]:
            if color == "global" and setting_background != "default":
                item.setBackground(QColor(setting_background))    
            elif color != "global" and color != "default":
                item.setBackground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.BackgroundRole)
                
    def updateNotebook(self, name: str, newname: str) -> None:
        notebook_counts[newname] = notebook_counts.pop(name)
        notebook_items[newname] = notebook_items.pop(name)
        
        notebook_items[newname][0].setText(newname)
        
    def updateNotebookBackground(self, name: str, color: str) -> None:
        for item in notebook_items[name]:
            if color == "global" and setting_background != "default":
                item.setBackground(QColor(setting_background))    
            elif color != "global" and color != "default":
                item.setBackground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.BackgroundRole)
                
    def updateNotebookForeground(self, name: str, color: str) -> None:
        for item in notebook_items[name]:
            if color == "global" and setting_foreground != "default":
                item.setForeground(QColor(setting_foreground))
            elif color != "global" and color != "default":
                item.setForeground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.ForegroundRole)
                
    def updateNoteForeground(self, notebook: str, name: str, color: str) -> None:
        for item in note_items[(notebook, name)]:
            if color == "global" and setting_foreground != "default":
                item.setForeground(QColor(setting_foreground))
            elif color != "global" and color != "default":
                item.setForeground(QColor(color))
            else:
                item.setData(None, Qt.ItemDataRole.ForegroundRole)