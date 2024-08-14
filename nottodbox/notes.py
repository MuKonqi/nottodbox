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
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QMouseEvent
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtWidgets import *


notes = {}
note_counts = {}
note_items = {}
note_menus = {}
notebook_counts = {}
notebook_items = {}

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


class SettingsDB:
    """The settings database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}settings.db")
        self.cur = self.db.cursor()
    
    def getSettings(self) -> tuple:
        """
        Get required settings. If not any string, create them with default value.

        Returns:
            str: Settings' values
        """
        
        try:
            self.cur.execute(f"select value from settings where setting = 'notes-autosave'")
            self.setting_autosave = self.cur.fetchone()[0]

        except:
            self.cur.execute(f"insert into settings (setting, value) values ('notes-autosave', 'enabled')")
            self.db.commit()
            self.setting_autosave = "enabled"
        
        try:
            self.cur.execute(f"select value from settings where setting = 'notes-format'")
            self.setting_format = self.cur.fetchone()[0]

        except:
            self.cur.execute(f"insert into settings (setting, value) values ('notes-format', 'markdown')")
            self.db.commit()
            self.setting_format = "markdown"
    
        return self.setting_autosave, self.setting_format
    
    def setAutoSave(self, signal: Qt.CheckState | int) -> bool:
        """
        Set auto-save setting for global.

        Args:
            signal (Qt.CheckState | int): QCheckBox's signal.

        Returns:
            bool: True if successful, False if not
        """
        
        global setting_autosave
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            setting_autosave = "disabled"

        elif signal == Qt.CheckState.Checked or signal == 2:
            setting_autosave = "enabled"
            
        self.cur.execute(f"update settings set value = '{setting_autosave}' where setting = 'notes-autosave'")
        self.db.commit()
        
        call = self.getSettings()
        
        if call[0] == setting_autosave:
            return True
        elif call[0] == setting_autosave:
            return False
                
    def setFormat(self, index: int) -> bool:
        """
        Set format setting for global.

        Args:
            index (int): Selected index in QComboBox.

        Returns:
            bool: True if successful, False if not
        """
        
        global setting_format
        
        if index == 0:
            setting_format = "plain-text"
        
        elif index == 1:
            setting_format = "markdown"
        
        elif index == 2:
            setting_format = "html"

        self.cur.execute(f"update settings set value = '{setting_format}' where setting = 'notes-format'")
        self.db.commit()
        
        call = self.getSettings()
        
        if call[1] == setting_format:
            return True
        elif call[1] == setting_format:
            return False
    

settingsdb = SettingsDB()
setting_autosave, setting_format = settingsdb.getSettings()


class NotesDB:
    """The notes database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}notes.db")
        self.cur = self.db.cursor()
    
    def checkIfTheNoteExists(self, notebook: str, name: str) -> bool:
        """
        Check if the note exists.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            bool: True if the note exists, if not False
        """
        
        call = self.checkIfTheNotebookExists(notebook)
        
        if call:
            self.cur.execute(f"select * from '{notebook}' where name = ?", (name,))
            
            try:
                self.cur.fetchone()[0]
                return True
            
            except TypeError:
                return False
            
        else:
            return False
        
    def checkIfTheNoteBackupExists(self, notebook: str, name: str) -> bool:
        """
        Check if the note's backup exists.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            bool: True if the backup exists, if not False
        """
        
        call = self.checkIfTheNotebookExists(notebook)
        
        if call:
            self.cur.execute(f"select backup from '{notebook}' where name = ?", (name,))
            fetch = self.cur.fetchone()[0]
            
            if fetch == None or fetch == "":
                return False
            else:
                return True
            
        else:
            return False
        
    def checkIfTheNotebookExists(self, name: str) -> bool:
        """
        Check if the table exists.

        Args:
            name (str): Table name

        Returns:
            bool: True if the table exists, if not False
        """
        
        try:
            self.cur.execute(f"select * from '{name}'")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createNote(self, notebook: str, name: str) -> bool:
        """
        Create a note if not exist.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            bool: True if successful, False if not
        """
        
        if not self.checkIfTheNoteExists(notebook, name):
            date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            sql = f"""
            insert into '{notebook}' (name, content, backup, creation, modification, autosave, format) 
            values (?, ?, ?, ?, ?, ?, ?)
            """
                
            self.cur.execute(sql, (name, "", "", date_time, date_time, "global", "global"))
            self.db.commit()
        
            return self.checkIfTheNoteExists(notebook, name)

        else:
            return True

    def createNotebook(self, name: str) -> bool:
        """
        Create a notebook if not exist.
        
        Args:
            name (str): Notebook name

        Returns:
            bool: True if successful, False if not
        """
        
        sql = f"""
        CREATE TABLE IF NOT EXISTS '{name}' (
            name TEXT NOT NULL PRIMARY KEY,
            content TEXT,
            backup TEXT, 
            creation TEXT NOT NULL,
            modification TEXT,
            autosave INTEGER NOT NULL,
            format TEXT NOT NULL
        );"""
        
        self.cur.execute(sql)
        self.db.commit()
        
        return self.checkIfTheNotebookExists(name)
    
    def deleteAll(self) -> bool:
        """Delete all."""
        
        successful = True
        calls = {}
        
        self.cur.execute("select name from sqlite_master where type = 'table'")
        notebooks = self.cur.fetchall()
        
        for notebook in notebooks:
            notebook = notebook[0]
            
            calls[notebook] = self.deleteNotebook(notebook)
            
            if not calls[notebook]:
                successful = False
        
        return successful
    
    def deleteContent(self, notebook: str, name: str) -> bool:
        """
        Delete content of a note.

        Args:
            notebook (str): Notebook name    
            name (str): Note name

        Returns:
            bool: True if successful, False if not
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        fetch_before = self.getContent(notebook, name)
        
        sql = f"update '{notebook}' set content = '', backup = ?, modification = ? where name = ?"
            
        self.cur.execute(sql, (fetch_before, date_time, name))
        self.db.commit()
        
        fetch_after = self.getContent(notebook, name)
        
        if fetch_after == "" or fetch_after == None:
            return True
        else:
            return False
    
    def deleteNote(self, notebook: str, name: str) -> bool:
        """
        Delete a note.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"delete from '{notebook}' where name = ?", (name,))
        self.db.commit()
        
        call = self.checkIfTheNoteExists(notebook, name)
        
        if call:
            return False
        else:
            return True
        
    def deleteNotebook(self, name: str):
        """
        Delete a notebook.

        Args:
            name (str): Notebook name
        """
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        if self.checkIfTheNotebookExists(name):
            return False
        else:
            return True
        
    def getAll(self) -> dict:
        """
        Get all notebooks' names, notes' informations and names.

        Returns:
            dict: Notebooks', notes' informations and names
        """
        
        all = {}
        
        self.cur.execute("select name from sqlite_master where type = 'table'")
        notebooks = self.cur.fetchall()
        
        for notebook in notebooks:
            notebook = notebook[0]
            
            self.cur.execute(f"select name, creation, modification from '{notebook}'")
            all[notebook] = self.cur.fetchall()
            
        return all
    
    def getAutosave(self, notebook: str, name: str) -> str:
        """
        Get auto-save setting of a note.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            str: Setting
        """
        
        self.cur.execute(f"select autosave from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = setting_autosave
        return fetch
    
    def getBackup(self, notebook: str, name: str) -> str:
        """
        Get backup of a note.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            str: Content
        """
        
        self.cur.execute(f"select backup from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
    
    def getContent(self, notebook: str, name: str) -> str:
        """
        Get content of a note.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            str: Content.
        """
        
        self.cur.execute(f"select content from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
        
    def getFormat(self, notebook: str, name: str) -> str:
        """
        Get format setting of a note.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            str: Setting
        """
        
        self.cur.execute(f"select format from '{notebook}' where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = setting_format
        return fetch
    
    def getNote(self, notebook: str, name: str) -> list:
        """
        Get a note's creation and modification dates.

        Args:
            notebook (str): Notebook name
            name (str): Note name

        Returns:
            list: A note's creation and modefication dates
        """
        
        self.cur.execute(f"select creation, modification from '{notebook}' where name = ?", (name,))
        return self.cur.fetchone()
    
    def getNotebook(self, name: str) -> list:
        """
        Get a notebook's notes' names, creation and modification dates.

        Args:
            name (str): Notebook name

        Returns:
            list: A notebook's notes' names, creation and modification dates
        """
        
        self.cur.execute(f"select name, creation, modification from '{name}'")
        return self.cur.fetchall()
    
    def renameNote(self, notebook: str, name: str, newname: str) -> bool:
        """
        Rename a note.

        Args:
            notebook (str): Notebook name
            name (str): Old name
            newname (str): New name

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"update '{notebook}' set name = ? where name = ?", (newname, name))
        self.db.commit()
        
        return self.checkIfTheNoteExists(notebook, newname)
    
    def renameNotebook(self, name: str, newname: str) -> bool:
        """
        Rename a notebook.
        
        Args:
            name (str): Notebook name
            newname (str): New name
            
        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"ALTER TABLE '{name}' RENAME TO '{newname}'")
        self.db.commit()
        
        return self.checkIfTheNotebookExists(newname)
        
    def resetNotebook(self, name: str) -> bool:
        """
        Reset a notebook.

        Args:
            name (str): Notebook name

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        call = self.checkIfTheNotebookExists(name)
        
        if call:
            return False
        else:
            return self.createNotebook(name)
    
    def restoreContent(self, notebook: str, name: str) -> bool:
        """
        Restore content of note.
        
        Args:
            notebook (str): Notebook name
            name (str): Note name
            
        Returns:
            bool: True if successful, False if not
        """
        
        if not self.checkIfTheNoteBackupExists(notebook, name):
            return False
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"select content, backup from '{notebook}' where name = ?", (name,))
        fetch_before = self.cur.fetchone()
        
        sql = f"update '{notebook}' set content = ?, backup = ?, modification = ? where name = ?"
        
        self.cur.execute(sql, (fetch_before[1], fetch_before[0], date_time, name))
        self.db.commit()
        
        self.cur.execute(f"select content, backup from '{notebook}' where name = ?", (name,))
        fetch_after = self.cur.fetchone()
        
        if fetch_before[1] == fetch_after[0] and fetch_before[0] == fetch_after[1]:
            return True
        else:
            return False
        
    def saveAll(self) -> bool:
        """
        Save all notes.
        If there is such a note, create it.

        Returns:
            bool: True if successful, False if not
        """
        
        successful = True
        calls = {}
        
        for item in notes:
            try:
                name, notebook = str(name).split(" @ ")
            
            except ValueError:
                return False
            
            calls[item] = self.saveNote(notebook,
                                        name,
                                        notes[item].input.toPlainText(), 
                                        notes[item].content, 
                                        False)
            
            if not calls[item]:
                successful = False
                
        return successful

    def saveNote(self, notebook: str, name: str, content: str, backup: str, autosave: bool) -> bool:        
        """
        Save a note.
        
        Args:
            notebook (str): Notebook name
            name (str): Note name
            content (str): Content of note
            backup (str): Backup of diary
            autosave (bool): True if the caller is "auto-save", false if it is not
            
        Returns:
            bool: True if successful, False if not
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        check = self.checkIfTheNoteExists(notebook, name)
        
        if check:
            if autosave:
                sql = f"update '{notebook}' set content = ?, modification = ? where name = ?"
                
                self.cur.execute(sql, (content, date_time, name))
                        
            else:
                sql = f"update '{notebook}' set content = ?, backup = ?, modification = ? where name = ?"
                
                self.cur.execute(sql, (content, backup, date_time, name))
            
            self.db.commit()
        
            self.cur.execute(f"select content, modification from '{notebook}' where name = ?", (name,))
            control = self.cur.fetchone()

            if control[0] == content and control[1] == date_time:            
                return True
            else:
                return False

        else:
            return False
        
    def setAutosave(self, notebook: str, name: str, setting: str) -> bool:
        """
        Set auto-save setting for a note.

        Args:
            notebook (str): Notebook name
            name (str): Note name
            setting (str): New setting

        Returns:
            bool: True if successful, False if not
        """
        
        if not self.checkIfTheNotebookExists(notebook):
            return False
        
        self.cur.execute(f"update '{notebook}' set autosave = ? where name = ?", (setting, name))
        self.db.commit()
        
        call = self.getAutosave(notebook, name)
        
        if call == setting:
            return True
        else:
            return False
        
    def setFormat(self, notebook: str, name: str, setting: str) -> bool:
        """
        Set format setting for a note.

        Args:
            notebook (str): Notebook name
            name (str): Note name
            setting (str): New setting

        Returns:
            bool: True if successful, False if not
        """
        
        if not self.checkIfTheNotebookExists(notebook):
            return False
        
        self.cur.execute(f"update '{notebook}' set format = ? where name = ?", (setting, name))
        self.db.commit()
        
        call = self.getFormat(notebook, name)
        
        if call == setting:
            return True
        else:
            return False


notesdb = NotesDB()


class NotesTabWidget(QTabWidget):
    """The "Notes" tab widget class."""
    
    def __init__(self, parent: QMainWindow) -> None:
        """Init and then set.

        Args:
            parent (QMainWindow): Main window
        """
        
        super().__init__(parent)
        
        global notes_parent
        
        notes_parent = parent
        self.backups = {}
        self.note = ""
        self.notebook = ""
        self.current_widget = None
        
        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self.home))
        
        self.treeview = NotesTreeView(self)
        
        self.entry = QLineEdit(self.home)
        self.entry.setPlaceholderText("Search in the list below")
        self.entry.setClearButtonEnabled(True)
        self.entry.textEdited.connect(self.treeview.setFilter)
        
        self.notebook_selected = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, text=_("Notebook: "))
        self.note_selected = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, text=_("Note: "))
        
        self.note_options = NotesNoteOptions(self)
        self.note_options.setVisible(False)
        
        self.notebook_options = NotesNotebookOptions(self)
        self.notebook_options.setVisible(False)

        self.none_options = NotesNoneOptions(self)
        
        self.current_widget = self.none_options
        
        self.home.layout().addWidget(self.entry, 0, 0, 1, 3)
        self.home.layout().addWidget(self.note_selected, 1, 0, 1, 1)
        self.home.layout().addWidget(self.notebook_selected, 1, 1, 1, 1)
        self.home.layout().addWidget(self.treeview, 2, 0, 1, 2)
        self.home.layout().addWidget(self.none_options, 1, 2, 2, 1)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
         
    def closeTab(self, index: int) -> None:
        """
        Close a tab.

        Args:
            index (int): Index of tab
        """
        
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
                        call = notes[self.tabText(index).replace("&", "")].saveNote()
                        
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
        """
        Insert informations.

        Args:
            notebook (str): Notebook name
            name (str): Note name
        """

        self.notebook = notebook
        self.name = name      
        
        self.none_options.setVisible(False)
        self.notebook_options.setVisible(False)
        self.note_options.setVisible(False)
        
        if self.notebook == "":
            self.none_options.setVisible(True)
            self.home.layout().replaceWidget(self.current_widget, self.none_options)
            
            self.current_widget = self.none_options
            
        elif self.notebook != "" and self.name == "":
            self.notebook_options.setVisible(True)
            self.home.layout().replaceWidget(self.current_widget, self.notebook_options)
            
            self.current_widget = self.notebook_options
            
        elif self.notebook != "" and self.name != "":
            self.note_options.setVisible(True)
            self.home.layout().replaceWidget(self.current_widget, self.note_options)
            
            self.current_widget = self.note_options
            
        self.notebook_selected.setText(_("Notebook: ") + notebook)
        self.note_selected.setText(_("Note: ") + name)

        
class NotesNoneOptions(QWidget):
    """Options when selected nothing."""
    
    def __init__(self, parent: NotesTabWidget) -> None:
        """
        Init and then set widget.
        
        Args:
            parent (NotesTabWidget): "Notes" tab in main window
        """
        
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.warning_label = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                                    text=_("You can select\na notebook or a note\non the left."))
        self.warning_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)
        
        self.create_notebook = QPushButton(self, text=_("Create notebook"))
        self.create_notebook.clicked.connect(self.parent_.notebook_options.createNotebook)
        
        self.delete_all = QPushButton(self, text=_("Delete all"))
        self.delete_all.clicked.connect(self.parent_.notebook_options.deleteAll)
        
        self.setLayout(QVBoxLayout(self))
        self.setFixedWidth(150)
        
        self.layout().addWidget(self.warning_label)
        self.layout().addWidget(self.create_notebook)
        self.layout().addWidget(self.delete_all)


class NotesNoteOptions(QWidget):
    """Options when selected note."""
    
    def __init__(self, parent: NotesTabWidget) -> None:
        """
        Init and then set widget.

        Args:
            parent (NotesTabWidget): "Notes" tab in main window
        """
        
        super().__init__(parent)

        self.parent_ = parent
        
        self.create_note = QPushButton(self, text=_("Create note"))
        self.create_note.clicked.connect(self.createNote)
        
        self.open_note = QPushButton(self, text=_("Open note"))
        self.open_note.clicked.connect(self.openNote)
        
        self.rename_note = QPushButton(self, text=_("Rename note"))
        self.rename_note.clicked.connect(self.renameNote)

        self.show_backup = QPushButton(self, text=_("Show backup"))
        self.show_backup.clicked.connect(self.showBackup)

        self.restore_content = QPushButton(self, text=_("Restore content"))
        self.restore_content.clicked.connect(self.restoreContent)
        
        self.delete_content = QPushButton(self, text=_("Delete content"))
        self.delete_content.clicked.connect(self.deleteContent)
        
        self.delete_note = QPushButton(self, text=_("Delete note"))
        self.delete_note.clicked.connect(self.deleteNote)

        self.setLayout(QVBoxLayout(self))
        self.setFixedWidth(150)
        
        self.layout().addWidget(self.create_note)
        self.layout().addWidget(self.open_note)
        self.layout().addWidget(self.rename_note)
        self.layout().addWidget(self.show_backup)
        self.layout().addWidget(self.restore_content)
        self.layout().addWidget(self.delete_content)
        self.layout().addWidget(self.delete_note)

    def checkIfTheNoteExists(self, notebook: str, name: str, mode: str = "normal") -> bool:
        """
        Check if the note exists.

        Args:
            notebook (str): Notebook name
            name (str): Note name
            mode (str, optional): Inverted mode for deleting etc. Defaults to "normal".
            
        Returns:
            bool: True if successful, False if not
        """
        
        call = notesdb.checkIfTheNoteExists(notebook, name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no note called {name}.").format(name = name))
        
        return call
    
    def checkIfTheNoteBackupExists(self, notebook: str, name: str) -> bool:
        """
        Check if the note backup exists.

        Args:
            notebook (str): Notebook name
            name (str): Note name
        """
        
        call = notesdb.checkIfTheNoteBackupExists(notebook, name)
        
        if not call:
            QMessageBox.critical(self, _("Error"), _("There is no backup for note {name}.").format(name = name))
        
        return call
    
    def createNote(self):
        """Create a note."""
        
        notebook = self.parent_.notebook
        
        if not notesdb.checkIfTheNotebookExists(notebook):
            QMessageBox.critical(self, _("Error"), _("There is no notebook called {name}.").format(name = notebook))
            
            return
        
        name, topwindow = QInputDialog.getText(self, _("Type a Name"), _("Type a name for creating a note."))
        
        if "@" in name:
            QMessageBox.critical(self, _("Error"), _('The note name cannot contain @ character.'))
            
            return
        
        elif name != "" and name != None and topwindow:
            call = self.parent_.note_options.checkIfTheNoteExists(notebook, name, "inverted")
        
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
        
    def deleteContent(self) -> None:
        """Delete content of a note."""
        
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if notebook == "" or notebook == None or name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Please select a note."))
            return
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        call = notesdb.deleteContent(notebook, name)
    
        if call:
            QMessageBox.information(self, _("Successful"), _("Content of {name} note deleted.").format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete content of {name} note.").format(name = name))
            
    def deleteNote(self) -> None:
        """Delete a note."""
        
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if notebook == "" or notebook == None or name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Please select a note."))
            return
        
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
        """Open a note."""

        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if notebook == "" or notebook == None or name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Please select a note."))
            return

        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        notes_parent.tabwidget.setCurrentIndex(1)
        
        if f"{name} @ {notebook}" in notes:
            self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
            
        else:            
            notes_parent.dock.widget().addPage(f"{name} @ {notebook}", self.parent_)
            notes[f"{name} @ {notebook}"] = NotesNote(self, notebook, name)
            self.parent_.addTab(notes[f"{name} @ {notebook}"], f"{name} @ {notebook}")
            self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
    
    def renameNote(self) -> None:
        """Rename a note."""
        
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if notebook == "" or notebook == None or name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Please select a note."))
            return
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} Note").format(name = name), 
                                                  _("Please enter a new name for {name} below.").format(name = name))
        
        if newname != "" and newname != None and topwindow:
            call = notesdb.renameNote(notebook, name, newname)

            self.parent_.treeview.updateNote(notebook, name, newname)
            
            if call:
                self.parent_.insertInformations(notebook, newname)
                
                QMessageBox.information(self, _("Successful"), _("{name} note renamed as {newname}.")
                                        .format(name = name, newname = newname))
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to rename {name} note.")
                                     .format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} note.")
                                 .format(name = name))
            
    def restoreContent(self) -> None:
        """Restore content of a note."""
        
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if notebook == "" or notebook == None or name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Please select a note."))
            return
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        if not self.checkIfTheNoteBackupExists(notebook, name):
            return
        
        call = notesdb.restoreContent(notebook, name)
        
        if call:
            QMessageBox.information(self, _("Successful"), _("Backup of {name} note restored.").format(name = name))
            
        elif not call:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup of {name} note.").format(name = name))
            
    def showBackup(self) -> None:
        """Show backup of a note."""
        
        notebook = self.parent_.notebook
        name = self.parent_.name
        
        if notebook == "" or notebook == None or name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Please select a note."))
            return
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        if not self.checkIfTheNoteBackupExists(notebook, name):
            return
        
        notes_parent.tabwidget.setCurrentIndex(1)

        self.parent_.backups[f'{name} @ {notebook}'] = NotesBackup(self, notebook, name)
        self.parent_.addTab(self.parent_.backups[f'{name} @ {notebook}'], f'{name} @ {notebook} {_("(Backup)")}')
        self.parent_.setCurrentWidget(self.parent_.backups[f'{name} @ {notebook}'])
            
            
class NotesNotebookOptions(QWidget):
    """Options when selected notebook."""
    
    def __init__(self, parent: NotesTabWidget) -> None:
        """
        Init and then set widget.

        Args:
            parent (NotesTabWidget): "Notes" tab in main window
        """
        
        super().__init__(parent)
        
        self.parent_ = parent

        self.create_note = QPushButton(self, text=_("Create note"))
        self.create_note.clicked.connect(self.parent_.note_options.createNote)
        
        self.create_notebook = QPushButton(self, text=_("Create notebook"))
        self.create_notebook.clicked.connect(self.createNotebook)
        
        self.rename_notebook = QPushButton(self, text=_("Rename notebook"))
        self.rename_notebook.clicked.connect(self.renameNotebook)
        
        self.reset_notebook = QPushButton(self, text=_("Reset notebook"))
        self.reset_notebook.clicked.connect(self.resetNotebook)
        
        self.delete_notebook = QPushButton(self, text=_("Delete notebook"))
        self.delete_notebook.clicked.connect(self.deleteNotebook)
        
        self.delete_all = QPushButton(self, text=_("Delete all"))
        self.delete_all.clicked.connect(self.deleteAll)
        
        self.setLayout(QVBoxLayout(self))
        self.setFixedWidth(150)
        
        self.layout().addWidget(self.create_note)
        self.layout().addWidget(self.create_notebook)
        self.layout().addWidget(self.rename_notebook)
        self.layout().addWidget(self.reset_notebook)
        self.layout().addWidget(self.delete_notebook)
        self.layout().addWidget(self.delete_all)
        
    def checkIfTheNotebookExists(self, name: str, mode: str = "normal") -> bool:
        """
        Check if the notebook exists.

        Args:
            name (str): Notebook name
            mode (str, optional): Inverted mode for deleting etc. Defaults to "normal".
            
        Returns:
            bool: True if successful, False if not
        """
        
        call = notesdb.checkIfTheNotebookExists(name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no notebook called {name}.").format(name = name))
        
        return call
                    
    def createNotebook(self) -> None:
        """Create a notebook."""
        
        name, topwindow = QInputDialog.getText(self, _("Type a Name"), _("Type a name for creating a notebook."))
        
        if "@" in name or "'" in name:
            QMessageBox.critical(self, _("Error"), _("The notebook name cannot contain these characters: @ and '"))
            
            return
        
        elif name != "" and name != None and topwindow:
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
                    QMessageBox.critical(self, _("Error"), _("Failed to create notebook {name}.").format(name = name))
                    
    def deleteAll(self) -> None:
        """Delete all."""
        
        call = notesdb.deleteAll()
        
        if call:
            self.parent_.treeview.updateAll()
            self.parent_.insertInformations("", "")
            
            QMessageBox.information(self, _("Successful"), _("All notebooks deleted."))

        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all notebooks."))
        
    def deleteNotebook(self) -> None:
        """Delete a notebook."""
        
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
        """Rename a notebook."""
        
        name = self.parent_.notebook
        
        if not self.checkIfTheNotebookExists(name):
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} Notebook").format(name = name), 
                                                  _("Please enter a new name for {name} below.").format(name = name))
        
        if newname != "" and newname != None and topwindow:
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
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} notebook.")
                                 .format(name = name))
        
    def resetNotebook(self) -> None:
        """Reset a notebook."""
        
        name = self.parent_.notebook
        
        if not self.checkIfTheNotebookExists(name):
            return
        
        call = notesdb.resetNotebook(name)
        
        if call:
            self.parent_.treeview.updateNotebook(name, name)
            self.parent_.insertInformations(name, "")
            
            QMessageBox.information(self, _("Successful"), _("{name} notebook reset.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset {name} notebook.").format(name = name))


class NotesNote(QWidget):
    """A page for notes."""
    
    def __init__(self, parent: NotesTabWidget, notebook: str, name: str) -> None:
        """Init and then set page.
        
        Args:
            parent (NotesTabWidget): "Notes" tab in main window
            notebook (str): Notebook name
            name (str): Note name
        """
        
        super().__init__(parent)
        
        self.parent_ = parent
        self.notebook = notebook
        self.name = name
        self.closable = True
        
        self.content = notesdb.getContent(notebook, name)
        
        self.call_autosave = notesdb.getAutosave(notebook, name)
        if self.call_autosave == "global":
            self.setting_autosave = setting_autosave
        else:
            self.setting_autosave = self.call_autosave
        
        self.call_format = notesdb.getFormat(notebook, name)
        if self.call_format == "global":
            self.setting_format = setting_format
        else:
            self.setting_format = self.call_format
              
        self.autosave = QComboBox(self)
        self.autosave.addItems([
            _("Auto-save for this note: Follow global ({setting})").format(setting = setting_autosave),
            _("Auto-save for this note: Enabled"), 
            _("Auto-save for this note: Disabled")])
        
        if self.call_autosave == "global":
            self.autosave.setCurrentIndex(0)
        elif self.call_autosave == "enabled":
            self.autosave.setCurrentIndex(1)
        elif self.call_autosave == "disabled":
            self.autosave.setCurrentIndex(2)
        
        self.autosave.setEditable(False)
        self.autosave.currentIndexChanged.connect(self.setAutoSave)
        
        self.format = QComboBox(self)
        self.format.addItems([
            _("Format for this note: Follow global ({setting})").format(setting = setting_format),
            _("Format for this note: Plain-text"), 
            _("Format for this note: Markdown"), 
            _("Format for this note: HTML")])
        
        if self.call_format == "global":
            self.format.setCurrentIndex(0)
        elif self.call_format == "plain-text":
            self.format.setCurrentIndex(1)
        elif self.call_format == "markdown":
            self.format.setCurrentIndex(2)
        elif self.call_format == "html":
            self.format.setCurrentIndex(3)
        
        self.format.setEditable(False)
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.input = QTextEdit(self)
        self.input.setPlainText(self.content)
        self.input.textChanged.connect(
            lambda: self.updateOutput(self.input.toPlainText()))
        self.input.textChanged.connect(lambda: self.saveNote(True))
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        
        self.button = QPushButton(self, text=_("Save"))
        self.button.clicked.connect(self.saveNote)
        
        self.setLayout(QGridLayout(self))
        self.setStatusTip(_("Auto-saves do not change backups."))
        
        self.layout().addWidget(self.autosave, 0, 0, 1, 1)
        self.layout().addWidget(self.input, 1, 0, 1, 1)
        self.layout().addWidget(self.format, 0, 1, 1, 1)
        self.layout().addWidget(self.output, 1, 1, 1, 1)
        self.layout().addWidget(self.button, 2, 0, 1, 2)
        
        self.updateOutput(self.content)
        
    def saveNote(self, autosave: bool = False) -> bool:
        """
        Save a note.

        Args:
            autosave (bool, optional): Autosave value. Defaults to False.
            
        Returns:
            bool: True if successful, False if not
        """
        
        self.closable = False
        
        if not autosave or (autosave and self.setting_autosave == "enabled"):
            call = notesdb.saveNote(self.notebook,
                                    self.name,
                                    self.input.toPlainText(),
                                    self.content,
                                    autosave)

            if call:
                self.closable = True
                
                if not autosave:
                    QMessageBox.information(self, _("Successful"), _("Note {name} saved.").format(name = self.name))
                    
                return True
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to save {name} note.").format(name = self.name))
                
                return False
                
    def setAutoSave(self, index: int) -> None:
        """
        Set auto-save setting for this note.

        Args:
            index (int): Selected index
        """
        
        if index == 0:
            setting = "global"
        
        elif index == 1:
            setting = "enabled"
        
        elif index == 2:
            setting = "disabled"
        
        call = notesdb.setAutosave(self.notebook, self.name, setting)
        
        if call:
            self.setting_autosave = setting
            
            self.updateOutput(self.input.toPlainText())
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new autosave setting."))

    def setFormat(self, index: int) -> None:
        """
        Set format setting for this note.

        Args:
            index (int): Selected index
        """
        
        if index == 0:
            setting = "global"
        
        elif index == 1:
            setting = "plain-text"
        
        elif index == 2:
            setting = "markdown"
        
        elif index == 3:
            setting = "html"
        
        call = notesdb.setFormat(self.notebook, self.name, setting)
        
        if call:
            self.setting_format = setting
            
            self.updateOutput(self.input.toPlainText())
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new format setting."))
            
    def updateOutput(self, text: str) -> None:
        """
        Update output when input's text changed or format changed.

        Args:
            text (str): Content
        """
        
        if self.setting_format == "plain-text":
            self.output.setPlainText(text)
        
        elif self.setting_format == "markdown":
            self.output.setMarkdown(text)
        
        elif self.setting_format == "html":
            self.output.setHtml(text)
            

class NotesBackup(QWidget):
    """A page for notes' backups."""
    
    def __init__(self, parent: NotesTabWidget, notebook: str, name: str) -> None:
        """Init and then set page.
        
        Args:
            parent (NotesTabWidget): "Notes" tab in main window
            notebook (str): Notebook name
            name (str): Note name
        """        
        
        super().__init__(parent)
        
        self.parent_ = parent
        self.notebook = notebook
        self.name = name
        
        self.backup = notesdb.getBackup(notebook, name)
        
        self.setting_format = setting_format
        
        self.call_format = notesdb.getFormat(notebook, name)
        if self.call_format == "global":
            self.setting_format = setting_format
        else:
            self.setting_format = self.call_format
        
        self.format = QComboBox(self)
        self.format.addItems([
            _("Format for this note: Follow global ({setting})").format(setting = setting_format),
            _("Format for this note: Plain-text"), 
            _("Format for this note: Markdown"), 
            _("Format for this note: HTML")])
        
        if self.call_format == "global":
            self.format.setCurrentIndex(0)
        elif self.call_format == "plain-text":
            self.format.setCurrentIndex(1)
        elif self.call_format == "markdown":
            self.format.setCurrentIndex(2)
        elif self.call_format == "html":
            self.format.setCurrentIndex(3)
        
        self.format.setEditable(False)
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        
        self.button = QPushButton(self, text=_("Restore content"))
        self.button.clicked.connect(self.restoreContent)
        
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.format)
        self.layout().addWidget(self.output)
        self.layout().addWidget(self.button)
        
        self.updateOutput(self.backup)

    def setFormat(self, index: int) -> None:
        """
        Set format setting for this note.

        Args:
            index (int): Selected index
        """
        
        if index == 0:
            setting = "global"
        
        elif index == 1:
            setting = "plain-text"
        
        elif index == 2:
            setting = "markdown"
        
        elif index == 3:
            setting = "html"
        
        call = notesdb.setFormat(self.notebook, self.name, setting)
        
        if call:
            self.setting_format = setting
            
            self.updateOutput(self.backup)
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new format setting."))
            
    def updateOutput(self, text: str) -> None:
        """
        Update output when format changed.

        Args:
            text (str): Content
        """
        
        if self.setting_format == "plain-text":
            self.output.setPlainText(text)
        
        elif self.setting_format == "markdown":
            self.output.setMarkdown(text)
        
        elif self.setting_format == "html":
            self.output.setHtml(text)
            
    def restoreContent(self):
        """Restore content of a note."""
        
        notebook = self.notebook
        name = self.name
        
        if notebook == "" or notebook == None or name == "" or name == None:
            find_status, notebook, name = self.tryFindTheNoteInModel(notebook, name)
            
            if not find_status:
                return False
        
        if not self.checkIfTheNoteExists(notebook, name):
            return
        
        call = notesdb.restoreContent(notebook, name)
        
        if call:
            QMessageBox.information(self, _("Successful"), _("Backup of {name} note restored.").format(name = name))
            
        elif not call:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup of {name} note.").format(name = name))


class NotesTreeView(QTreeView):
    """A list for showing notes' names."""
    
    def __init__(self, parent: NotesTabWidget, caller: str = "notes") -> None:
        """Init and then set properties.

        Args:
            parent (NotesTabWidget): "Notes" tab in main window
            caller (str, optional): For some special properties. Defaults to "notes".
        """
        
        super().__init__(parent)
        
        self.parent_ = parent
        self.caller = caller

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setRecursiveFilteringEnabled(True)
        
        if self.caller == "notes":
            global notes_model
            
            notes_model = QStandardItemModel(self)
            notes_model.setHorizontalHeaderLabels(["Name", "Creation date", "Modification date"])
            
        self.proxy.setSourceModel(notes_model)
        
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip(_("Double-click to opening a note."))
        self.setModel(self.proxy)

        if self.caller == "notes":
            self.selectionModel().currentRowChanged.connect(
                lambda: self.parent_.insertInformations(self.getParentText(), self.getCurrentText()))
        
        self.doubleClicked.connect(lambda: self.openNote(self.getParentText(), self.getCurrentText()))
        
        self.appendAll()

    def appendAll(self) -> None:
        """Append all."""
        
        global menu_notes
        
        call = notesdb.getAll()
        
        if self.caller == "notes":
            if not "menu_notes" in globals():
                menu_notes = notes_parent.menuBar().addMenu(_("Notes"))
            
            menu_notes.clear() 
        
        if call != None and self.caller == "notes":
            model_count = -1
            
            notebooks = [*call]
            
            for notebook in notebooks:
                model_count += 1
                notebook_count = -1
                
                notebook_counts[notebook] = model_count
                notebook_items[model_count] = QStandardItem(notebook)
                
                for name, creation, modification in call[notebook]:
                    notebook_count += 1
                    
                    name_column = QStandardItem(name)
                    creation_column = QStandardItem(creation)
                    modification_column = QStandardItem(modification)
                    
                    note_counts[(notebook, name)] = notebook_count
                    note_items[(notebook, notebook_count)] = [name_column, creation_column, modification_column]
                
                    notebook_items[model_count].appendRow(note_items[(notebook, notebook_count)])
                    
                    if self.caller == "notes":
                        note_menus[(notebook, name)] = menu_notes.addAction(
                            f"{name} @ {notebook}", lambda name = name, notebook = notebook: self.openNote(notebook, name))
                
                notes_model.appendRow(notebook_items[model_count])

                self.setFirstColumnSpanned(0, self.rootIndex(), True)
                
            self.expandAll()
            
    def appendNote(self, notebook: str, name: str) -> None:
        """
        Append a note.

        Args:
            notebook (str): Notebook name
            name (str): Name
        """
    
        creation, modification = notesdb.getNote(notebook, name)
        
        name_column = QStandardItem(name)
        creation_column = QStandardItem(creation)
        modification_column = QStandardItem(modification)
        
        notebook_count = notebook_items[notebook_counts[notebook]].rowCount()
        
        note_counts[(notebook, name)] = notebook_count
        note_items[(notebook, notebook_count)] = [name_column, creation_column, modification_column]
        
        if self.caller == "notes":
            note_menus[(notebook, name)] = menu_notes.addAction(
                f"{name} @ {notebook}", lambda name = name, notebook = notebook: self.openNote(notebook, name))
        
        notebook_items[notebook_counts[notebook]].appendRow(note_items[(notebook, notebook_count)])
            
    def appendNotebook(self, notebook: str) -> None:
        """
        Append a notebook.

        Args:
            notebook (str): Notebook name
        """
        
        call = notesdb.getNotebook(notebook)
        
        model_count = notes_model.rowCount()
        notebook_count = -1
        
        notebook_counts[notebook] = model_count
        notebook_items[model_count] = QStandardItem(notebook)
        
        for name, creation, modification in call:
            notebook_count += 1
            
            name_column = QStandardItem(name)
            creation_column = QStandardItem(creation)
            modification_column = QStandardItem(modification)
            
            note_counts[(notebook, name)] = notebook_count
            note_items[(notebook, notebook_count)] = [name_column, creation_column, modification_column]
        
            notebook_items[model_count].appendRow(note_items[(notebook, notebook_count)])
            
            if self.caller == "notes":
                note_menus[(notebook, name)] = menu_notes.addAction(
                    f"{name} @ {notebook}", lambda name = name, notebook = notebook: self.openNote(notebook, name))
        
        notes_model.appendRow(notebook_items[model_count])
        
    def deleteNote(self, notebook: str, name: str) -> None:
        """
        Delete a note.

        Args:
            notebook (str): Notebook name
            name (str): Note name
        """
        
        notebook_items[notebook_counts[notebook]].removeRow(note_counts[(notebook, name)])
        
        del note_items[(notebook, note_counts[(notebook, name)])]
        del note_counts[(notebook, name)]
        
        if self.caller == "notes":
            menu_notes.removeAction(note_menus[(notebook, name)])
            
            del note_menus[(notebook, name)]
        
    def deleteNotebook(self, notebook: str) -> None:
        """
        Delete a notebook.

        Args:
            notebook (str): Notebook name
        """
        
        notebook_count = notebook_counts[notebook]
        
        notes_model.removeRow(notebook_counts[notebook])
        
        del notebook_items[notebook_count]
        del notebook_counts[notebook]
        
        for key in note_items.copy().keys():
            if key[0] == notebook:
                del note_items[key]
                
        for key in note_counts.copy().keys():
            if key[0] == notebook:
                del note_counts[key]
                
        if self.caller == "notes":
            for key in note_menus.copy().keys():
                if key[0] == notebook:
                    menu_notes.removeAction(note_menus[key])
                    
                    del note_menus[key]
                    
    def getParentText(self) -> str:
        """
        Get and then return parent item text.

        Returns:
            str: The text
        """
        
        try:
            if self.currentIndex().parent().isValid():
                return self.proxy.itemData(self.currentIndex().parent())[0]
            
            else:
                return self.proxy.itemData(self.currentIndex())[0]
            
        except KeyError:
            return ""
        
    def getCurrentText(self) -> str:
        """
        Get and then return current item's text.

        Returns:
            str: The text
        """
        
        try:
            if self.currentIndex().parent().isValid():
                return self.proxy.itemData(self.currentIndex())[0]
            
            else:
                return ""
            
        except KeyError:
            return ""
                
    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        """
        Override of QTreeView's mousePressEvent function.

        Args:
            e (QMouseEvent | None): Mouse event
        """
        
        index = self.indexAt(e.pos())
        
        if index.column() == 0:
            super().mousePressEvent(e)
            
        else:
            QMessageBox.warning(self, _("Warning"), _("Please select a note only by clicking on the first column."))
    
    def openNote(self, notebook: str = "", name: str = "") -> None:
        """
        Open a note.

        Args:
            notebook (str, optional): Notebook name. Defaults to "".
            name (str, optional): Note name. Defaults to "".
        """
        
        if notebook == "" or notebook == None or name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Please select a note."))
            return

        if not self.parent_.note_options.checkIfTheNoteExists(notebook, name):
            return
        
        notes_parent.tabwidget.setCurrentIndex(1)
        
        if f"{name} @ {notebook}" in notes:
            self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
            
        else:            
            notes_parent.dock.widget().addPage(f"{name} @ {notebook}", self.parent_)
            notes[f"{name} @ {notebook}"] = NotesNote(self, notebook, name)
            self.parent_.addTab(notes[f"{name} @ {notebook}"], f"{name} @ {notebook}")
            self.parent_.setCurrentWidget(notes[f"{name} @ {notebook}"])
                
    def setFilter(self, text: str) -> None:
        """Set filtering proxy.

        Args:
            text (str): Filtering text
        """
        
        self.proxy.beginResetModel()
        self.proxy.setFilterFixedString(text)
        self.proxy.endResetModel()
        
    def updateAll(self) -> None:
        """Delete all and then append all."""
        
        notes_model.clear()
        self.appendAll()
        
    def updateNote(self, notebook: str, name: str, newname: str) -> None:
        """
        Delete and then append a note.

        Args:
            notebook (str): Notebook name
            name (str): Old note name
            newname (str): New note name
        """
        
        self.deleteNote(notebook, name)
        self.appendNote(notebook, newname)
        
    def updateNotebook(self, name: str, newname: str) -> None:
        """
        Delete and then append a notebook.

        Args:
            name (str): Old notebook name
            newname (str): New notebook name
        """
        
        self.deleteNotebook(name)
        self.appendNotebook(newname)