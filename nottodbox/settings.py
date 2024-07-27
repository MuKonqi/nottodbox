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
from gettext import gettext as _
from notes import NotesTabWidget
from diaries import DiariesTabWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


settings = {
    "mainwindow-unsaved": "true",
    "mainwindow-documentmode": "false",

    "notes-autohide": "true",
    "notes-documentmode": "true",
    "notes-autosave": "true",
    "notes-format": "markdown",
    "notes-unsaved": "true",

    "todos-autohide": "true",
    "todos-documentmode": "true",

    "diaries-autohide": "true",
    "diaries-documentmode": "true",
    "diaries-autosave": "true",
    "diaries-format": "markdown",
    "diaries-space": "2",
    "diaries-unsaved": "true",
    "diaries-olddiary": "true",
    "diaries-sections": "all"
}

defaults = settings.copy()


class SettingsDB:
    """The settings database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}settings.db")
        self.cur = self.db.cursor()
        
    def checkIfTheTableExists(self) -> bool:
        """
        Check if the table exists.

        Returns:
            bool: True if the table exists, if not False
        """
        
        try:
            self.cur.execute("select * from settings")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
        """
        If the settings table not exists, create it.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        sql = """
        CREATE TABLE IF NOT EXISTS settings (
            setting TEXT NOT NULL PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
        
        self.cur.execute(sql)
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            self.getAllSettings()
        
        return call
    
    def getAllSettings(self) -> None:
        """Get all settings' values."""

        for setting, value in settings.items():
                self.getSetting(setting.replace("-", " ").split()[0], 
                                setting.replace("-", " ").split()[1])
    
    def getSetting(self, module: str, setting: str) -> str:
        """
        Get the setting's value. If not any value, create them with default value.

        Args:
            module (str): The module
            setting (str): The setting

        Returns:
            str: Setting's value
        """
        
        global settings
        
        settings[f"{module}-{setting}"]
               
        try:
            self.cur.execute(f"select value from settings where setting = '{module}-{setting}'")
            return self.cur.fetchone()[0]

        except:
            self.cur.execute(
                f"insert into settings (setting, value) values ('{module}-{setting}', '{defaults[f'{module}-{setting}']}')")
            self.db.commit()
            return defaults[f'{module}-{setting}']
        
    def updateSetting(self, module: str, setting: str, value: str) -> bool:
        """
        Update the setting.

        Args:
            module (str): The module
            setting (str): The setting
            value (str): New value

        Returns:
            bool: True if successful, False if not
        """
            
        self.cur.execute(f"update settings set value = '{value}' where setting = '{module}-{setting}'")
        self.db.commit()
        
        call = self.getSetting(module, setting)
        
        if call[0] == value:
            global settings
            settings[f"module-setting"] = value

            return True

        elif call[0] == value:
            return False

settingsdb = SettingsDB()

create_table = settingsdb.createTable()
if create_table:
    table = True
else:
    table = False


class SettingsScrollArea(QScrollArea):
    """Scrollable area for Settings module."""
    
    def __init__(self, parent: QMainWindow, notes: NotesTabWidget, diaries: DiariesTabWidget) -> None:
        """
        Init and set scrollable area.

        Args:
            parent (QMainWindow): Main window
            notes (NotesTabWidget): Notes tab widget
            diaries (DiariesTabWidget): Diaries tab widget
        """
        
        super().__init__(parent)
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(SettingsWidget(self, notes, diaries))


class SettingsWidget(QWidget):
    """Main widget class for Settings module."""
    
    def __init__(self, parent: QMainWindow, notes: NotesTabWidget, diaries: DiariesTabWidget) -> None:        
        """
        Display a widget for list of setting modules.

        Args:
            parent (QMainWindow): Main window
            notes (NotesTabWidget): Notes tab widget
            diaries (DiariesTabWidget): Diaries tab widget
        """
        
        super().__init__(parent)
        
        self.setLayout(QHBoxLayout(self))
        
        self.stacked = QStackedWidget(self)
        self.stacked.addWidget(SettingsInterface(self, notes, diaries))
        self.stacked.addWidget(SettingsDocument(self, notes, diaries))
        self.stacked.addWidget(SettingsQuestions(self, notes, diaries))
        
        self.list = QListWidget(self)
        self.list.setCurrentRow(0)
        self.list.setFixedWidth(150)
        self.list.currentRowChanged.connect(lambda: self.stacked.setCurrentIndex(self.list.currentRow()))
        
        self.list_interface = QListWidgetItem(_("Interface"), self.list)
        self.list_interface.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_document = QListWidgetItem(_("Document"), self.list)
        self.list_document.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_questions = QListWidgetItem(_("Questions"), self.list)
        self.list_questions.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list.addItem(self.list_interface)
        self.list.addItem(self.list_document)
        self.list.addItem(self.list_questions)
        
        self.layout().addWidget(self.list)
        self.layout().addWidget(self.stacked)
        
    def showPage(self, index: int) -> None:
        """Show the selected page.

        Args:
            index (int): Selected index
        """
        
        self.stacked.setCurrentIndex(index)
        

class SettingsInterface(QWidget):
    """Widget for interface settings."""
    
    def __init__(self, parent: QWidget, notes: NotesTabWidget, diaries: DiariesTabWidget):
        """
        Display a widget for setting interface settings.

        Args:
            parent (SettingsWidget): Main settings widget
            notes (NotesTabWidget): Notes tab widget
            diaries (DiariesTabWidget): Diaries tab widget
        """
        
        super().__init__(parent)
        

class SettingsDocument(QWidget):
    """Widget for document settings."""
    
    def __init__(self, parent: QWidget, notes: NotesTabWidget, diaries: DiariesTabWidget):
        """
        Display a widget for setting document settings.

        Args:
            parent (SettingsWidget): Main settings widget
            notes (NotesTabWidget): Notes tab widget
            diaries (DiariesTabWidget): Diaries tab widget
        """
        
        super().__init__(parent)


class SettingsQuestions(QWidget):
    """Widget for question settings."""
    
    def __init__(self, parent: QWidget, notes: NotesTabWidget, diaries: DiariesTabWidget):
        """
        Display a widget for setting diaries' settings.

        Args:
            parent (SettingsWidget): Main settings widget
            notes (NotesTabWidget): Notes tab widget
            diaries (DiariesTabWidget): Diaries tab widget
        """
        
        super().__init__(parent)