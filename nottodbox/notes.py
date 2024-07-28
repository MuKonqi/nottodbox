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


notes = {}

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
            self.cur.execute(f"insert into settings (setting, value) values ('notes-autosave', 'true')")
            self.db.commit()
            self.setting_autosave = "true"
        
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
            bool: True if successful, False if unsuccesful
        """
        
        global setting_autosave
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            setting_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            setting_autosave = "true"
            
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
            bool: True if successful, False if unsuccesful
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
    
    def checkIfTheNoteExists(self, name: str) -> bool:
        """
        Check if the note exists.

        Args:
            name (str): Note name

        Returns:
            bool: True if the note exists, if not False
        """
        
        self.cur.execute(f"select * from notes where name = '{name}'")
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
        
    def checkIfTheTableExists(self) -> bool:
        """
        Check if the table exists.

        Returns:
            bool: True if the table exists, if not False
        """
        
        try:
            self.cur.execute("select * from notes")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
        """
        If the notes table not exists, create it.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        sql = """
        CREATE TABLE IF NOT EXISTS notes (
            name TEXT NOT NULL PRIMARY KEY,
            content TEXT,
            backup TEXT, 
            created TEXT NOT NULL,
            edited TEXT
        );"""
        
        self.cur.execute(sql)
        self.db.commit()
        
        return self.checkIfTheTableExists()
    
    def deleteContent(self, name: str) -> bool:
        """
        Delete content of a note.

        Args:
            name (str): Note name

        Returns:
            bool: True if successful, False if not
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        fetch_before = self.getContent(name)
        
        sql = f"""
        update notes set content = '', backup = '{fetch_before}', edited = '{date_time}'
        where name = '{name}'
        """
            
        self.cur.execute(sql)
        self.db.commit()
        
        fetch_after = self.getContent(name)
        
        if fetch_after == "" or fetch_after == None:
            return True
        else:
            return False
    
    def deleteOne(self, name: str) -> bool:
        """
        Delete a note.

        Args:
            name (str): Note name

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"delete from notes where name = '{name}'")
        self.db.commit()
        
        call = self.checkIfTheNoteExists(name)
        
        if call:
            return False
        else:
            return True
    
    def getBackup(self, name: str) -> str:
        """
        Get backup of a note.

        Args:
            name (str): Note name.

        Returns:
            str: Content.
        """
        
        self.cur.execute(f"select backup from notes where name = '{name}'")
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch

    def getContent(self, name: str) -> str:
        """
        Get content of a note.

        Args:
            name (str): Note name.

        Returns:
            str: Content.
        """
        
        self.cur.execute(f"select content from notes where name = '{name}'")
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
        
    def getInformations(self, name: str) -> tuple:
        """
        Get creation and edit dates.

        Args:
            name (str): Note name

        Returns:
            tuple: Returns creation and edit dates
        """
        
        self.cur.execute(f"select created, edited from notes where name = '{name}'")
        return self.cur.fetchone()
        
    def getNames(self) -> list:
        """Get all notes' names.

        Returns:
            list: List of all notes' names.
        """
        
        self.cur.execute("select name from notes")
        return self.cur.fetchall()
    
    def renameNote(self, name: str, newname: str) -> bool:
        """
        Rename a note.

        Args:
            name (str): Old name
            newname (str): New name

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        self.cur.execute(f"update notes set name = '{newname}' where name = '{name}'")
        self.db.commit()
        
        return self.checkIfTheNoteExists(newname)
        
    def recreateTable(self) -> bool:
        """Recreates the notes table.

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"DROP TABLE IF EXISTS notes")
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            return False
        else:
            return self.createTable()
    
    def restoreContent(self, name: str) -> tuple:
        """
        Restore content of note.
        
        Args:
            name (str): Note name
            
        Returns:
            tuple: Status and True if successful, False if unsuccesful
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"select content, backup from notes where name = '{name}'")
        fetch_before = self.cur.fetchone()
        
        if fetch_before[1] == None or fetch_before[1] == "":
            return "no-backup", False
        
        sql = f"""update notes set content = '{fetch_before[1]}', 
        backup = '{fetch_before[0]}', edited = '{date_time}' where name = '{name}'"""
        self.cur.execute(sql)
        self.db.commit()
        
        self.cur.execute(f"select content, backup from notes where name = '{name}'")
        fetch_after = self.cur.fetchone()
        
        if fetch_before[1] == fetch_after[0] and fetch_before[0] == fetch_after[1]:
            return "successful", True
        else:
            return "failed", False
        
    def saveAll(self) -> bool:
        """
        Save all notes.
        If there is such a note, create it.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        successful = True
        calls = {}
        
        for name in notes:
            calls[name] = self.saveOne(name,
                                       notes[name].input.toPlainText(), 
                                       notes[name].content, 
                                       False)
            
            if calls[name] == False:
                successful = False
                
        return successful

    def saveOne(self, name: str, content: str, backup: str, autosave: bool) -> bool:        
        """
        Save a note.
        If there is such a note, create it.
        
        Args:
            name (str): Note name
            content (str): Content of note
            backup (str): Backup of diary
            autosave (bool): True if the caller is "auto-save", false if it is not
            
        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        check = self.checkIfTheNoteExists(name)
        
        if check:
            if autosave:
                sql = f"""update notes set content = '{content}',
                edited = '{date_time}' where name = '{name}'"""
                        
            else:
                sql = f"""update notes set content = '{content}', backup = '{backup}',
                edited = '{date_time}' where name = '{name}'"""
            
            self.cur.execute(sql)
            self.db.commit()
            
        else:
            sql = f"""insert into notes (name, content, backup, created, edited) 
                    values ('{name}', '{content}', '', '{date_time}', '{date_time}')"""
            self.cur.execute(sql)
            self.db.commit()
                        
        self.cur.execute(f"select content, edited from notes where name = '{name}'")
        control = self.cur.fetchone()

        if control[0] == content and control[1] == date_time:            
            return True
        else:
            return False


notesdb = NotesDB()

create_table = notesdb.createTable()
if not create_table:
    print("[2] Failed to create table")
    sys.exit(2)


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
        
        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self.home))
        
        self.listview = NotesListView(self)
        
        self.entry = QLineEdit(self.home)
        self.entry.setPlaceholderText("Enter a note name")
        self.entry.setStatusTip(_("You can search in list while entering anythings in entry."))
        self.entry.setClearButtonEnabled(True)
        self.entry.textChanged.connect(self.listview.setFilter)
        
        self.created = QLabel(self.home, alignment=Qt.AlignmentFlag.AlignCenter, 
                              text=_("Created: "))
        self.edited = QLabel(self.home, alignment=Qt.AlignmentFlag.AlignCenter, 
                             text=_("Edited: "))

        self.side = QWidget(self.home)
        self.side.setFixedWidth(150)
        self.side.setLayout(QVBoxLayout(self.side))
        
        self.open_create_button = QPushButton(self.side, text=_("Open/create note"))
        self.open_create_button.clicked.connect(lambda: self.openCreate(self.entry.text()))
        
        self.rename_button = QPushButton(self.side, text=_("Rename note"))
        self.rename_button.clicked.connect(lambda: self.renameNote(self.entry.text()))

        self.show_backup_button = QPushButton(self.side, text=_("Show backup"))
        self.show_backup_button.clicked.connect(lambda: self.showBackup(self.entry.text()))

        self.restore_button = QPushButton(self.side, text=_("Restore content"))
        self.restore_button.clicked.connect(lambda: self.restoreContent(self.entry.text()))
        
        self.delete_content_button = QPushButton(self.side, text=_("Delete content"))
        self.delete_content_button.clicked.connect(lambda: self.deleteContent(self.entry.text()))
        
        self.delete_note_button = QPushButton(self.side, text=_("Delete note"))
        self.delete_note_button.clicked.connect(lambda: self.deleteNote(self.entry.text()))
        
        self.delete_all_button = QPushButton(self.side, text=_("Delete all notes"))
        self.delete_all_button.clicked.connect(self.deleteAll)
        
        self.format = QComboBox(self)
        self.format.addItems([_("Format: Plain text"), _("Format: Markdown"), _("Format: HTML")])
        self.format.setEditable(False)
        if setting_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif setting_format == "markdown":
            self.format.setCurrentIndex(1)
        elif setting_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)        
        
        self.autosave = QCheckBox(self, text=_("Enable auto-save"))
        if setting_autosave == "true":
            self.autosave.setChecked(True)
        self.autosave.setStatusTip(_("Auto-saves do not change backups."))
        try:
            self.autosave.checkStateChanged.connect(self.setAutoSave)
        except:
            self.autosave.stateChanged.connect(self.setAutoSave)
        
        self.side.layout().addWidget(self.open_create_button)
        self.side.layout().addWidget(self.rename_button)
        self.side.layout().addWidget(self.show_backup_button)
        self.side.layout().addWidget(self.restore_button)
        self.side.layout().addWidget(self.delete_content_button)
        self.side.layout().addWidget(self.delete_note_button)
        self.side.layout().addWidget(self.delete_all_button)
        self.side.layout().addWidget(self.format)
        self.side.layout().addWidget(self.autosave)
        self.home.layout().addWidget(self.side, 1, 2, 2, 1)
        self.home.layout().addWidget(self.entry, 0, 0, 1, 3)
        self.home.layout().addWidget(self.created, 1, 0, 1, 1)
        self.home.layout().addWidget(self.edited, 1, 1, 1, 1)
        self.home.layout().addWidget(self.listview, 2, 0, 1, 2)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        
    def checkIfTheNoteExists(self, name: str, mode: str = "normal") -> None:
        """
        Check if the note exists.

        Args:
            name (str): Note name
            mode (str, optional): Inverted mode for deleting etc. Defaults to "normal".
        """
        
        call = notesdb.checkIfTheNoteExists(name)
        
        if call == False and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no note called {name}.").format(name = name))
        
        return call
         
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
                        call = notesdb.saveOne(self.tabText(index).replace("&", ""),
                                               notes[self.tabText(index).replace("&", "")].input.toPlainText(),
                                               notes[self.tabText(index).replace("&", "")].content, 
                                               False)
                        
                        self.listview.insertNames()
                        
                        if call:
                            self.closable = True
                        else:
                            QMessageBox.critical(self, _("Error"), _("Failed to save {name} note.").format(name = self.tabText(index).replace("&", "")))
                    
                    elif self.question != QMessageBox.StandardButton.Yes:
                        return
                
                del notes[self.tabText(index).replace("&", "")]
                
            except KeyError:
                pass
            
            notes_parent.dock.widget().removePage(self.tabText(index).replace("&", ""), self)
            self.removeTab(index)
        
    def deleteAll(self) -> None:
        """Delete all notes."""
        
        call = notesdb.recreateTable()
    
        if call:
            self.listview.insertNames()
            self.insertInformations("")
            
            QMessageBox.information(self, _("Successful"), _("All notes deleted."))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all notes."))
        
    def deleteContent(self, name: str) -> None:
        """
        Delete content of a note.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Note name can not be blank."))
            return        
        
        if self.checkIfTheNoteExists(name) == False:
            return
        
        call = notesdb.deleteContent(name)
    
        if call:
            QMessageBox.information(self, _("Successful"), _("Content of {name} note deleted.").format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete content of {name} note.").format(name = name))
                       
    def deleteNote(self, name: str) -> None:
        """
        Delete a note.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Note name can not be blank."))
            return
        
        if self.checkIfTheNoteExists(name) == False:
            return
        
        call = notesdb.deleteOne(name)
            
        if call:
            self.listview.insertNames()
            self.insertInformations("")
            
            QMessageBox.information(self, _("Successful"), _("{name} note deleted.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {name} note.").format(name = name))
        
    def insertInformations(self, name: str) -> None:
        """Insert name and creation, edit dates.

        Args:
            name (str): Note name
        """
        
        if name != "":
            call = notesdb.getInformations(name)
        else:
            call = None
        
        self.entry.setText(name)
        
        try:
            self.created.setText(_("Created: ") + call[0])
        except TypeError:
            self.created.setText(_("Created: "))
            
        try:
            self.edited.setText(_("Edited: ") + call[1])
        except TypeError:
            self.edited.setText(_("Edited: "))
        
    def openCreate(self, name: str) -> None:
        """
        Open or create a note.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Note name can not be blank."))
            return
        
        notes_parent.tabwidget.setCurrentIndex(1)
        
        if name in notes:
            self.setCurrentWidget(notes[name])
            
        else:
            notes_parent.dock.widget().addPage(name, self)
            notes[name] = NotesNote(self, name)
            self.addTab(notes[name], name)
            self.setCurrentWidget(notes[name])
    
    def renameNote(self, name: str) -> None:
        """Rename a note.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Note name can not be blank."))
            return        
        
        if self.checkIfTheNoteExists(name) == False:
            return
        
        newname, topwindow = QInputDialog.getText(self, 
                                                  _("Rename {name} Note").format(name = name), 
                                                  _("Please enter a new name for {name} below.").format(name = name))
        
        if newname != "" and newname != None and topwindow:
            call = notesdb.renameNote(name, newname)

            self.listview.insertNames()
            
            if call:
                self.insertInformations(newname)
                
                QMessageBox.information(self, _("Successful"), _("{name} note renamed as {newname}.")
                                        .format(name = name, newname = newname))
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to rename {name} note.")
                                     .format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to rename {name} note.")
                                 .format(name = name))
            
    def restoreContent(self, name: str) -> None:
        """Restore content of a note.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Note name can not be blank."))
            return
        
        if self.checkIfTheNoteExists(name) == False:
            return
        
        status, call = notesdb.restoreContent(name)
        
        if status == "successful" and call:
            QMessageBox.information(self, _("Successful"), _("Backup of {name} note restored.").format(name = name))
        
        elif status == "no-backup" and not call:
            QMessageBox.critical(self, _("Error"), _("There is no backup for {name} note.").format(name = name))
            
        elif status == "failed" and not call:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup of {name} note.").format(name = name))
            
    def setAutoSave(self, signal: Qt.CheckState | int) -> None:
        """
        Set auto-save setting for global.

        Args:
            signal (Qt.CheckState | int): QCheckBox's signal.
        """
        
        global setting_autosave
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            setting_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            setting_autosave = "true"
            
        call = settingsdb.setAutoSave(signal)
        
        if call == False:
            QMessageBox.critical(self, _("Erorr"), _("Failed to set auto-save setting."))
                
    def setFormat(self, index: int) -> None:
        """
        Set format setting for global.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        global setting_format
        
        if index == 0:
            setting_format = "plain-text"
        
        elif index == 1:
            setting_format = "markdown"
        
        elif index == 2:
            setting_format = "html"
            
        call = settingsdb.setFormat(index)
        
        if call == False:
            QMessageBox.critical(self, _("Erorr"), _("Failed to set format setting."))
            
    def showBackup(self, name: str) -> None:
        """
        Show backup of a note.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _("Error"), _("Note name can not be blank."))
            return

        if self.checkIfTheNoteExists(name) == False:
            return
        
        notes_parent.tabwidget.setCurrentIndex(1)
        notes_parent.dock.widget().addPage(name + " " + _("(Backup)"), self)

        self.backups[name] = NotesBackup(self, name)
        self.addTab(self.backups[name], (name + " " + _("(Backup)")))
        self.setCurrentWidget(self.backups[name])
        

class NotesNote(QWidget):
    """A page for notes."""
    
    def __init__(self, parent: NotesTabWidget, name: str) -> None:
        """Init and then set page.
        
        Args:
            parent (NotesTabWidget): "Notes" tab widget in main window
            name (str): Note name
        """
        
        super().__init__(parent)
        
        self.parent_ = parent
        self.name = name
        self.content = notesdb.getContent(name)
        self.setting_autosave = setting_autosave
        self.setting_format = setting_format
        self.closable = True
        
        self.setLayout(QGridLayout(self))
        self.setStatusTip(_("Auto-saves do not change backups."))
        
        self.autosave = QCheckBox(self, text=_("Enable auto-save for this time"))
        if setting_autosave == "true":
            self.autosave.setChecked(True)
        try:
            self.autosave.checkStateChanged.connect(self.setAutoSave)
        except:
            self.autosave.stateChanged.connect(self.setAutoSave)
        
        self.input = QTextEdit(self)
        self.input.setPlainText(self.content)
        self.input.textChanged.connect(
            lambda: self.updateOutput(self.input.toPlainText()))
        self.input.textChanged.connect(lambda: self.saveNote(True))
        
        self.format = QComboBox(self)
        self.format.addItems([_("Format for this time: Plain text"), 
                               _("Format for this time: Markdown"), 
                               _("Format for this time: HTML")])
        self.format.setEditable(False)
        if self.setting_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif self.setting_format == "markdown":
            self.format.setCurrentIndex(1)
        elif self.setting_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.updateOutput(self.content)
        
        self.button = QPushButton(self, text=_("Save"))
        self.button.clicked.connect(self.saveNote)
        
        self.layout().addWidget(self.autosave, 0, 0, 1, 1)
        self.layout().addWidget(self.input, 1, 0, 1, 1)
        self.layout().addWidget(self.format, 0, 1, 1, 1)
        self.layout().addWidget(self.output, 1, 1, 1, 1)
        self.layout().addWidget(self.button, 2, 0, 1, 2)
        
    def saveNote(self, autosave: bool = False) -> None:
        """
        Save a note.

        Args:
            autosave (bool, optional): _description_. Defaults to False.
        """
        
        self.closable = False
        
        if not autosave or (autosave and self.setting_autosave == "true"):
            call = notesdb.saveOne(self.name,
                                   self.input.toPlainText(),
                                   self.content,
                                   autosave)
            
            self.parent_.listview.insertNames()

            if call:
                self.closable = True
                
                if not autosave:
                    QMessageBox.information(self, _("Successful"), _("Note {name} saved.").format(name = self.name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to save {name} note.").format(name = self.name))
                
    def setAutoSave(self, signal: Qt.CheckState | int) -> None:
        """Set auto-save setting for only this page.

        Args:
            signal (Qt.CheckState | int): QCheckBox's signal.
        """
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.setting_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            self.setting_autosave = "true"

    def setFormat(self, index: int) -> None:
        """Set format setting for only this page.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        if index == 0:
            self.setting_format = "plain-text"
        
        elif index == 1:
            self.setting_format = "markdown"
        
        elif index == 2:
            self.setting_format = "html"
            
        self.updateOutput(self.input.toPlainText())
            
    def updateOutput(self, text: str) -> None:
        """Update output when input's text changed or format changed.

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
    
    def __init__(self, parent: NotesTabWidget, name: str) -> None:
        """Init and then set page.
        
        Args:
            parent (NotesTabWidget): "Notes" tab widget in main window
            name (str): Note name
        """        
        
        super().__init__(parent)
        
        self.backup = notesdb.getBackup(name)
        
        self.setting_format = setting_format
        
        self.setLayout(QVBoxLayout(self))
        self.setStatusTip(_("Auto-saves do not change backups."))
            
        self.format = QComboBox(self)
        self.format.addItems([_("Format for this time: Plain text"), 
                               _("Format for this time: Markdown"), 
                               _("Format for this time: HTML")])
        self.format.setEditable(False)
        if self.setting_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif self.setting_format == "markdown":
            self.format.setCurrentIndex(1)
        elif self.setting_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.updateOutput(self.backup)
        
        self.button = QPushButton(self, text=_("Restore content"))
        self.button.clicked.connect(lambda: parent.restoreContent(name))
        
        self.layout().addWidget(self.format)
        self.layout().addWidget(self.output)
        self.layout().addWidget(self.button)

    def setFormat(self, index: int) -> None:
        """Set format setting for only this page.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        if index == 0:
            self.setting_format = "plain-text"
        
        elif index == 1:
            self.setting_format = "markdown"
        
        elif index == 2:
            self.setting_format = "html"
            
        self.updateOutput(self.backup)
            
    def updateOutput(self, text: str) -> None:
        """Update output when format changed.

        Args:
            text (str): Content
        """
        
        if self.setting_format == "plain-text":
            self.output.setPlainText(text)
        
        elif self.setting_format == "markdown":
            self.output.setMarkdown(text)
        
        elif self.setting_format == "html":
            self.output.setHtml(text)


class NotesListView(QListView):
    """A list for showing notes' names."""
    
    def __init__(self, parent: NotesTabWidget, caller: str = "notes") -> None:
        """Init and then set properties.

        Args:
            parent (NotesTabWidget): "Notes" tab widget in main window
            caller (str, optional): For some special properties. Defaults to "notes".
        """
        
        super().__init__(parent)
        
        global notes_model1, notes_model2
        
        self.parent_ = parent
        self.caller = caller

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        if self.caller == "notes":  
            notes_model1 = QStringListModel(self)
            self.proxy.setSourceModel(notes_model1)
            
        elif self.caller == "home":
            notes_model2 = QStringListModel(self)
            self.proxy.setSourceModel(notes_model2)
        
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip(_("Double-click to opening a note."))
        self.setModel(self.proxy)

        if self.caller == "notes":
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
        """Insert notes' names."""
        
        global menu_notes
        
        call = notesdb.getNames()
        names = []
        
        if self.caller == "notes":
            if not "menu_notes" in globals():
                menu_notes = notes_parent.menuBar().addMenu(_("Notes"))
            
            menu_notes.clear()
            
            for name in call:
                names.append(name[0])
                menu_notes.addAction(name[0], lambda name = name: self.parent_.openCreate(name[0]))

        elif self.caller == "home":
            for name in call:
                names.append(name[0])
    
        try:
            notes_model1.setStringList(names)
        except NameError:
            pass
    
        try:
            notes_model2.setStringList(names)
        except NameError:
            pass
        
    def setFilter(self, text: str) -> None:
        """Set filtering proxy.

        Args:
            text (str): Filtering text
        """
        
        self.proxy.beginResetModel()
        self.proxy.endResetModel()
        self.proxy.setFilterFixedString(text)
    
        self.parent_.created.setText(_("Created: "))
        self.parent_.edited.setText(_("Edited: "))