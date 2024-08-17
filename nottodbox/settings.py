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
from gettext import gettext as _
from notes import NotesTabWidget
from todos import TodosTabWidget
from diaries import DiariesTabWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


settings = {
    "mainwindow-unsaved": "enabled",
    "mainwindow-documentmode": "disabled",

    "notes-autohide": "enabled",
    "notes-documentmode": "enabled",
    "notes-autosave": "enabled",
    "notes-format": "markdown",
    "notes-unsaved": "enabled",

    "todos-autohide": "enabled",
    "todos-documentmode": "enabled",

    "diaries-autohide": "enabled",
    "diaries-documentmode": "enabled",
    "diaries-autosave": "enabled",
    "diaries-format": "markdown",
    "diaries-space": "2",
    "diaries-unsaved": "enabled",
    "diaries-olddiary": "enabled",
    "diaries-sections": "all"
}

defaults = settings.copy()


class SettingsDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}settings.db")
        self.cur = self.db.cursor()
        
    def checkIfTheTableExists(self) -> bool:
        try:
            self.cur.execute("select * from settings")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
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
        for setting, value in settings.items():
                self.getSetting(setting.replace("-", " ").split()[0], 
                                setting.replace("-", " ").split()[1])
    
    def getSetting(self, module: str, setting: str) -> str:
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
if not create_table:
    print("[2] Failed to create table")
    sys.exit(2)


class SettingsScrollArea(QScrollArea):
    def __init__(self, parent: QMainWindow, notes: NotesTabWidget, todos: TodosTabWidget, diaries: DiariesTabWidget) -> None:
        super().__init__(parent)
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(SettingsWidget(self, notes, todos, diaries))


class SettingsWidget(QWidget):
    def __init__(self, parent: QMainWindow, notes: NotesTabWidget, todos: TodosTabWidget, diaries: DiariesTabWidget) -> None:        
        super().__init__(parent)
        
        self.setLayout(QHBoxLayout(self))
        
        self.stacked = QStackedWidget(self)
        self.stacked.addWidget(SettingsInterface(self, notes, todos, diaries))
        self.stacked.addWidget(SettingsDocument(self, notes, todos, diaries))
        self.stacked.addWidget(SettingsQuestions(self, notes, todos, diaries))
        
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
        
        self.list.setCurrentRow(0)
        
        self.layout().addWidget(self.list)
        self.layout().addWidget(self.stacked)
        
    def showPage(self, index: int) -> None:
        self.stacked.setCurrentIndex(index)
        

class SettingsInterface(QWidget):
    def __init__(self, parent: QWidget, notes: NotesTabWidget, todos: TodosTabWidget, diaries: DiariesTabWidget):
        super().__init__(parent)
        

class SettingsDocument(QWidget): 
    def __init__(self, parent: QWidget, notes: NotesTabWidget, todos: TodosTabWidget, diaries: DiariesTabWidget):
        super().__init__(parent)


class SettingsQuestions(QWidget):
    def __init__(self, parent: QWidget, notes: NotesTabWidget, todos: TodosTabWidget, diaries: DiariesTabWidget):
        super().__init__(parent)