#!/usr/bin/env python3

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


if __name__ == "__main__":
    import sys
    from mainwindow import MainWindow
    from PyQt6.QtWidgets import QApplication
    
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.tabview.setCurrentIndex(1)

    sys.exit(application.exec())


import locale
import gettext
import getpass
import sqlite3
import datetime
from sidebar import Sidebar
from PyQt6.QtCore import Qt, QStringListModel, QSortFilterProxyModel, QRegularExpression
from PyQt6.QtWidgets import *


if locale.getlocale()[0].startswith("tr"):
    language = "tr"
    translations = gettext.translation("nottodbox", "po", languages=["tr"], fallback=True)
else:
    language = "en"
    translations = gettext.translation("nottodbox", "po", languages=["en"], fallback=True)
translations.install()

_ = translations.gettext

align_center = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


class SettingsDB:
    """The settings database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}settings.db")
        self.cur = self.db.cursor()
    
    def getSettings(self) -> tuple:
        """Get required settings. If not any string, create them with default value."""
        
        try:
            self.cur.execute(f"select value from settings where setting = 'notes-autosave'")
            self.get_autosave = self.cur.fetchone()[0]

        except:
            self.cur.execute(f"insert into settings (setting, value) values ('notes-autosave', 'true')")
            self.db.commit()
            self.get_autosave = "true"
        
        try:
            self.cur.execute(f"select value from settings where setting = 'notes-format'")
            self.get_format = self.cur.fetchone()[0]

        except:
            self.cur.execute(f"insert into settings (setting, value) values ('notes-format', 'markdown')")
            self.db.commit()
            self.get_format = "markdown"
    
        return self.get_autosave, self.get_format
    
    def setAutoSave(self, signal: Qt.CheckState | int) -> bool:
        """
        Set auto-save setting for global.

        Args:
            signal (Qt.CheckState | int): QCheckBox's signal.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        global get_autosave
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            get_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            get_autosave = "true"
            
        self.cur.execute(f"update settings set value = '{get_autosave}' where setting = 'notes-autosave'")
        self.db.commit()
        
        call = self.getSettings()
        
        if call[0] == get_autosave:
            return True
        elif call[0] == get_autosave:
            return False
                
    def setFormat(self, index: int) -> bool:
        """
        Set format setting for global.

        Args:
            index (int): Selected index in QComboBox.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        global get_format
        
        if index == 0:
            get_format = "plain-text"
        
        elif index == 1:
            get_format = "markdown"
        
        elif index == 2:
            get_format = "html"

        self.cur.execute(f"update settings set value = '{get_format}' where setting = 'notes-format'")
        self.db.commit()
        
        call = self.getSettings()
        
        if call[1] == get_format:
            return True
        elif call[1] == get_format:
            return False
    

settingsdb = SettingsDB()
get_autosave, get_format = settingsdb.getSettings()


class NotesDB:
    """The notes database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}notes.db")
        self.cur = self.db.cursor()
        self.widgets = {}
    
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
        """Delete content of a note.

        Args:
            name (str): Note name

        Returns:
            bool: True if successful, False if unsuccessful
        """
        
        fetch_before = self.getContent(name)
            
        self.cur.execute(f"update notes set content = '', backup = '{fetch_before}' where name = '{name}'")
        self.db.commit()
        
        fetch_after = self.getContent(name)
        
        if fetch_after == "" or fetch_after == None:
            return True
        else:
            return False
    
    def deleteOne(self, name) -> bool:
        """Delete a note.

        Args:
            name (str): Note name

        Returns:
            bool: True if successful, False if unsuccessful
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

        try:
            self.cur.execute(f"select * from notes where name = '{newname}'")
            self.cur.fetchone()[0]
            return True
            
        except TypeError:
            return False
        
    def recreateTable(self) -> bool:
        """Recreates the notes table.

        Returns:
            bool: True if successful, False if unsuccessful
        """
        
        self.cur.execute(f"DROP TABLE IF EXISTS notes")
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            return False
        else:
            return self.createTable()
    
    def restoreContent(self, name: str, edited: str) -> tuple:
        """
        Restore content of note.
        
        Args:
            name (str): Note name
            edited (str): Editing date
            
        Returns:
            tuple: Status and True if successful, False if unsuccesful
        """
        
        self.cur.execute(f"select content, backup from notes where name = '{name}'")
        fetch_before = self.cur.fetchone()
        
        if fetch_before[1] == None or fetch_before[1] == "":
            return "no-backup", False
        
        sql = f"""update notes set content = '{fetch_before[1]}', 
        backup = '{fetch_before[0]}', edited = '{edited}' where name = '{name}'"""
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
        
        for name in self.widgets:
            calls[name] = self.saveOne(name, self.widgets[name].toPlainText(), 
                                       datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 
                                       False)
            
            if calls[name] == False:
                successful = False
                
        return successful

    def saveOne(self, name: str, content: str, edited: str, autosave: bool, widget: QTextEdit) -> bool:        
        """Save a note.
        If there is such a note, create it.
        
        Args:
            name (str): Note name
            content (str): Content of note
            edited (str): Creating/editing date
            autosave (bool): True if the caller is "auto-save", false if it is not
            widget (QTextEdit): Input widget
            
        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        self.cur.execute(f"select content from notes where name = '{name}'")
        
        try:
            old_content = self.cur.fetchone()[0]
            
            if autosave:
                sql = f"""update notes set content = '{content}',
                edited = '{edited}' where name = '{name}'"""
                        
            else:
                sql = f"""update notes set content = '{content}', backup = '{old_content}',
                edited = '{edited}' where name = '{name}'"""
            
            self.cur.execute(sql)
            self.db.commit()
            
        except TypeError:
            sql = f"""insert into notes (name, content, backup, created, edited) 
                    values ('{name}', '{content}', '', '{edited}', '{edited}')"""
            self.cur.execute(sql)
            self.db.commit()
                        
        self.cur.execute(f"select content, edited from notes where name = '{name}'")
        control = self.cur.fetchone()

        if control[0] == content and control[1] == edited: 
            self.widgets[name] = widget
                       
            return True

        else:
            return False


notesdb = NotesDB()

create_table = notesdb.createTable()
if create_table:
    table = True
else:
    table = False


class Note(QWidget):
    """A page for notes."""
    
    def __init__(self, parent: QTabWidget, name: str) -> None:
        """Init and then set page.
        
        Args:
            parent (QTabWidget): "Notes" tab widget in main window
            name (str): Note name
        """
        
        super().__init__(parent)
        
        self.parent_ = parent
        self.name = name
        self.content = notesdb.getContent(name)
        self.get_autosave = get_autosave
        self.get_format = get_format
        self.closable = True
        
        self.setLayout(QGridLayout(self))
        self.setStatusTip(_("Auto-saves do not change backups."))
        
        self.autosave = QCheckBox(self, text=_('Enable auto-save for this time'))
        if get_autosave == "true":
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
        if self.get_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif self.get_format == "markdown":
            self.format.setCurrentIndex(1)
        elif self.get_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.updateOutput(self.content)
        
        self.button = QPushButton(self, text=_('Save'))
        self.button.clicked.connect(self.saveNote)
        
        self.layout().addWidget(self.autosave, 0, 0, 1, 1)
        self.layout().addWidget(self.input, 1, 0, 1, 1)
        self.layout().addWidget(self.format, 0, 1, 1, 1)
        self.layout().addWidget(self.output, 1, 1, 1, 1)
        self.layout().addWidget(self.button, 2, 0, 1, 2)
        
    def saveNote(self, autosave: bool = False) -> None:
        """Save a note with NotesDB's saveOne function.

        Args:
            autosave (bool, optional): _description_. Defaults to False.
        """
        
        self.closable = False
        
        if not autosave or (autosave and self.get_autosave == "true"):
            call = notesdb.saveOne(self.name,
                                   self.input.toPlainText(),
                                   datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 
                                   autosave,
                                   self.input)
            
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
            self.get_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            self.get_autosave = "true"

    def setFormat(self, index: int) -> None:
        """Set format setting for only this page.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        if index == 0:
            self.get_format = "plain-text"
        
        elif index == 1:
            self.get_format = "markdown"
        
        elif index == 2:
            self.get_format = "html"
            
        self.updateOutput(self.input.toPlainText())
            
    def updateOutput(self, text: str) -> None:
        """Update output when input's text changed or format changed.

        Args:
            text (str): Content
        """
        
        if self.get_format == "plain-text":
            self.output.setPlainText(text)
        
        elif self.get_format == "markdown":
            self.output.setMarkdown(text)
        
        elif self.get_format == "html":
            self.output.setHtml(text)
            

class Backup(QWidget):
    """A page for notes' backups."""
    
    def __init__(self, parent: QTabWidget, name: str) -> None:
        """Init and then set page.
        
        Args:
            parent (QTabWidget): "Notes" tab widget in main window
            name (str): Note name
        """        
        
        super().__init__(parent)
        
        self.backup = notesdb.getBackup(name)
        
        self.get_format = get_format
        
        self.setLayout(QVBoxLayout(self))
        self.setStatusTip(_("Auto-saves do not change backups."))
            
        self.format = QComboBox(self)
        self.format.addItems([_("Format for this time: Plain text"), 
                               _("Format for this time: Markdown"), 
                               _("Format for this time: HTML")])
        self.format.setEditable(False)
        if self.get_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif self.get_format == "markdown":
            self.format.setCurrentIndex(1)
        elif self.get_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.updateOutput(self.backup)
        
        self.button = QPushButton(self, text=_('Restore content'))
        self.button.clicked.connect(lambda: Notes.restoreContent(parent, name))
        
        self.layout().addWidget(self.format)
        self.layout().addWidget(self.output)
        self.layout().addWidget(self.button)

    def setFormat(self, index: int) -> None:
        """Set format setting for only this page.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        if index == 0:
            self.get_format = "plain-text"
        
        elif index == 1:
            self.get_format = "markdown"
        
        elif index == 2:
            self.get_format = "html"
            
        self.updateOutput(self.backup)
            
    def updateOutput(self, text: str) -> None:
        """Update output when format changed.

        Args:
            text (str): Content
        """
        
        if self.get_format == "plain-text":
            self.output.setPlainText(text)
        
        elif self.get_format == "markdown":
            self.output.setMarkdown(text)
        
        elif self.get_format == "html":
            self.output.setHtml(text)


class NotesListView(QListView):
    """A list for showing notes' names."""
    
    def __init__(self, parent: QTabWidget, caller: str = "notes") -> None:
        """Init and then set properties.

        Args:
            parent (QTabWidget): "Notes" tab widget in main window
            caller (str, optional): For some special properties. Defaults to "notes".
        """
        
        super().__init__(parent)
        
        global notes_model1, notes_model2
        
        self.proxy = QSortFilterProxyModel(self)
        
        if caller == "notes":  
            notes_model1 = QStringListModel(self)
            self.proxy.setSourceModel(notes_model1)
            
        elif caller == "home":
            notes_model2 = QStringListModel(self)
            self.proxy.setSourceModel(notes_model2)
        
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStatusTip("Double-click to opening a note.")
        self.setModel(self.proxy)

        if caller == "notes":
            self.selectionModel().selectionChanged.connect(
                lambda: Notes.insertInformations(parent, self.proxy.itemData(self.currentIndex())[0]))
        
        self.doubleClicked.connect(lambda: Notes.openCreate(parent, self.proxy.itemData(self.currentIndex())[0]))
        
        self.insertNames()
        
    def insertNames(self) -> None:
        """Insert notes' names with NotesDB's getNames function."""
        
        call = notesdb.getNames()
        names = []
        
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


class Notes(QTabWidget):
    """The "Notes" tab widget class."""
    
    def __init__(self, parent: QMainWindow) -> None:
        """Init and then set.

        Args:
            parent (QMainWindow): Main window.
        """
        
        super().__init__(parent)
        
        self.notes =  {}
        self.backups = {}
        
        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self.home))
        
        self.listview = NotesListView(self)
        
        self.entry = QLineEdit(self.home)
        self.entry.setPlaceholderText("Type a note name")
        self.entry.setStatusTip("Typing in entry also searches in list.")
        self.entry.textChanged.connect(
            lambda: self.listview.proxy.setFilterRegularExpression(QRegularExpression
                                                          (self.entry.text(), QRegularExpression.PatternOption.CaseInsensitiveOption)))
        
        self.clear_button = QPushButton(self.home, text=_("Clear"))
        self.clear_button.setFixedWidth(144)
        self.clear_button.clicked.connect(lambda: self.entry.setText(""))
        
        self.created = QLabel(self.home, alignment=align_center, 
                              text=_('Created:'))
        self.edited = QLabel(self.home, alignment=align_center, 
                             text=_('Edited:'))

        self.side = QWidget(self.home)
        self.side.setFixedWidth(144)
        self.side.setLayout(QVBoxLayout(self.side))
        
        self.open_button = QPushButton(self.side, text=_('Open/create note'))
        self.open_button.clicked.connect(lambda: self.openCreate(self.entry.text()))
        
        self.rename_button = QPushButton(self.side, text=_('Rename note'))
        self.rename_button.clicked.connect(lambda: self.renameNote(self.entry.text()))

        self.show_backup_button = QPushButton(self.side, text=_('Show backup'))
        self.show_backup_button.clicked.connect(lambda: self.showBackup(self.entry.text()))

        self.restore_button = QPushButton(self.side, text=_('Restore content'))
        self.restore_button.clicked.connect(lambda: self.restoreContent(self.entry.text()))
        
        self.delete_content_button = QPushButton(self.side, text=_('Delete content'))
        self.delete_content_button.clicked.connect(lambda: self.deleteContent(self.entry.text()))
        
        self.delete_note_button = QPushButton(self.side, text=_('Delete note'))
        self.delete_note_button.clicked.connect(lambda: self.deleteNote(self.entry.text()))
        
        self.delete_all_button = QPushButton(self.side, text=_('Delete all notes'))
        self.delete_all_button.clicked.connect(self.deleteAll)
        
        self.format = QComboBox(self)
        self.format.addItems([_("Format: Plain text"), _("Format: Markdown"), _("Format: HTML")])
        self.format.setEditable(False)
        if get_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif get_format == "markdown":
            self.format.setCurrentIndex(1)
        elif get_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)        
        
        self.autosave = QCheckBox(self, text=_('Enable auto-save'))
        if get_autosave == "true":
            self.autosave.setChecked(True)
        self.autosave.setStatusTip(_("Auto-saves do not change backups."))
        try:
            self.autosave.checkStateChanged.connect(self.setAutoSave)
        except:
            self.autosave.stateChanged.connect(self.setAutoSave)
        
        self.side.layout().addWidget(self.open_button)
        self.side.layout().addWidget(self.rename_button)
        self.side.layout().addWidget(self.show_backup_button)
        self.side.layout().addWidget(self.restore_button)
        self.side.layout().addWidget(self.delete_content_button)
        self.side.layout().addWidget(self.delete_note_button)
        self.side.layout().addWidget(self.delete_all_button)
        self.side.layout().addWidget(self.format)
        self.side.layout().addWidget(self.autosave)
        self.home.layout().addWidget(self.side, 1, 2, 2, 1)
        self.home.layout().addWidget(self.entry, 0, 0, 1, 2)
        self.home.layout().addWidget(self.clear_button, 0, 2, 1, 1)
        self.home.layout().addWidget(self.created, 1, 0, 1, 1)
        self.home.layout().addWidget(self.edited, 1, 1, 1, 1)
        self.home.layout().addWidget(self.listview, 2, 0, 1, 2)
        
        self.addTab(self.home, _('Home'))
        self.setTabsClosable(True)
        self.setMovable(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        
    def checkIfTheNoteExists(self, name: str, mode: str = "normal") -> None:
        """
        Check if the note exists.

        Args:
            name (str): Note name.
            mode (str, optional): Inverted mode for deleting etc. Defaults to "normal".
        """
        
        call = notesdb.checkIfTheNoteExists(name)
        
        if call == False and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no note called {name}.").format(name = name))
        
        return call
         
    def closeTab(self, index: int) -> None:
        """
        Close tab.

        Args:
            index (int): Index of tab
        """
        
        if index != self.indexOf(self.home):           
            try:
                if self.notes[self.tabText(index).replace("&", "")].closable == False:
                    self.question = QMessageBox.question(self, 
                                                        _("Warning"),
                                                        _("{name} note not saved.\nDo you want to closing after saving it or directly closing or cancel?")
                                                        .format(name = self.tabText(index).replace("&", "")),
                                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                                                        QMessageBox.StandardButton.Save)
                    
                    if self.question == QMessageBox.StandardButton.Save:
                        call = notesdb.saveOne(self.tabText(index).replace("&", ""),
                                               self.notes[self.tabText(index).replace("&", "")].input.toPlainText(),
                                               datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 
                                               False,
                                               self.notes[self.tabText(index).replace("&", "")].input)
                        
                        self.listview.insertNames()
                        
                        if call:
                            self.closable = True
                        else:
                            QMessageBox.critical(self, _("Error"), _("Failed to save {name} note.").format(name = self.tabText(index).replace("&", "")))
                    
                    elif self.question != QMessageBox.StandardButton.Yes:
                        return
                
                del self.notes[self.tabText(index).replace("&", "")]
                
            except KeyError:
                pass
            
            Sidebar.remove(self.tabText(index).replace("&", ""), self)
            self.removeTab(index)
        
    def deleteAll(self) -> None:
        """Delete all notes."""
        
        call = notesdb.recreateTable()
        
        self.listview.insertNames()
        self.insertInformations("")
    
        if call:
            QMessageBox.information(self, _('Successful'), _('All notes deleted.'))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete all notes.'))
        
    def deleteContent(self, name: str) -> None:
        """
        Delete content of note with NotesDB's deleteContent function.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return        
        
        if self.checkIfTheNoteExists(name) == False:
            return
        
        call = notesdb.deleteContent(name)
    
        if call:
            QMessageBox.information(self, _('Successful'), _('Content of {name} note deleted.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete content of {name} note.').format(name = name))
                       
    def deleteNote(self, name: str) -> None:
        """
        Delete note of note with NotesDB's deleteOne function.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return
        
        if self.checkIfTheNoteExists(name) == False:
            return
        
        call = notesdb.deleteOne(name)
        
        self.listview.insertNames()
        self.insertInformations("")
            
        if call:
            QMessageBox.information(self, _('Successful'), _('{name} note deleted.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete {name} note.').format(name = name))
        
    def insertInformations(self, name: str) -> None:
        """Insert name and creation, edit dates.

        Args:
            name (str): Note name.
        """
        
        if name != "":
            call = notesdb.getInformations(name)
        else:
            call = None
            
        try:
            self.entry.setText(name)
            self.created.setText(f"{_('Created')}: {call[0]}")
            self.edited.setText(f"{_('Edited')}: {call[1]}")
        except TypeError:
            self.entry.setText("")
            self.created.setText(f"{_('Created')}:")
            self.edited.setText(f"{_('Edited')}:")
        
    def openCreate(self, name: str) -> None:
        """Open or create a note.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return
        
        if name in self.notes:
            self.setCurrentWidget(self.notes[name])
            
        else:
            Sidebar.add(name, self)
            self.notes[name] = Note(self, name)
            self.addTab(self.notes[name], name)
            self.setCurrentWidget(self.notes[name])
    
    def renameNote(self, name: str) -> None:
        """Rename note with NotesDB's rename function.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
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
                self.entry.setText(newname)
                
                QMessageBox.information(self, _('Successful'), _('{name} note renamed as {newname}.').format(name = name, newname = newname))
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to rename {name} note.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to rename {name} note.').format(name = name))
            
    def restoreContent(self, name: str) -> None:
        """Restore content of note with NotesDB's rename function.

        Args:
            name (str): Note name
        """
        
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return
        
        if self.checkIfTheNoteExists(name) == False:
            return
        
        status, call = notesdb.restoreContent(name,
                                              datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        if status == "successful" and call:
            QMessageBox.information(self, _("Successful"), _("Backup of {name} note restored.").format(name = name))
        
        elif status == "no-backup" and not call:
            QMessageBox.critical(self, _("Error"), _("There is no backup for {name} note.").format(name = name))
            
        elif status == "failed" and not call:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup of {name} note.").format(name = name))
            
    def setAutoSave(self, signal: Qt.CheckState | int) -> None:
        """
        Set auto-save setting for global with SettingsDB's setAutoSave function.

        Args:
            signal (Qt.CheckState | int): QCheckBox's signal.
        """
        
        global get_autosave
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            get_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            get_autosave = "true"
            
        call = settingsdb.setAutoSave(signal)
        
        if call == False:
            QMessageBox.critical(self, _("Erorr"), _("Failed to set auto-save setting."))
                
    def setFormat(self, index: int) -> None:
        """
        Set format setting for global with SettingsDB's setFormat function.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        global get_format
        
        if index == 0:
            get_format = "plain-text"
        
        elif index == 1:
            get_format = "markdown"
        
        elif index == 2:
            get_format = "html"
            
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
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return

        if self.checkIfTheNoteExists(name) == False:
            return
        
        Sidebar.add(name + " " + _("(Backup)"), self)
        self.backups[name] = Backup(self, name)
        self.addTab(self.backups[name], (name + " " + _("(Backup)")))
        self.setCurrentWidget(self.backups[name])