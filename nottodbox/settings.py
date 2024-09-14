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

from PyQt6.QtWidgets import QWidget
sys.dont_write_bytecode = True


import getpass
import sqlite3
from gettext import gettext as _
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"


class SettingsDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}settings.db")
        self.cur = self.db.cursor()
        
    def checkIfTheTableExists(self) -> bool:
        try:
            self.cur.execute(f"select * from __main__")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
        sql = """
        CREATE TABLE IF NOT EXISTS __main__ (
            setting TEXT NOT NULL PRIMARY KEY,
            value TEXT NOT NULL
        );"""
        
        self.cur.execute(sql)
        self.db.commit()
        
        return self.checkIfTheTableExists()
    
    def getAutosaveAndFormat(self, module: str) -> tuple:
        if not self.createTable():
            print("[2] Failed to create table")
            sys.exit(2)
            
        if module == "notes":
            try:
                self.cur.execute(f"select value from __main__ where setting = 'notes-autosave'")
                autosave = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('notes-autosave', 'enabled')")
                self.db.commit()
                autosave = "enabled"
            
            try:
                self.cur.execute(f"select value from __main__ where setting = 'notes-format'")
                format = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('notes-format', 'markdown')")
                self.db.commit()
                format = "markdown"
        
        elif module == "diaries":
            try:
                self.cur.execute(f"select value from __main__ where setting = 'diaries-autosave'")
                autosave = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('diaries-autosave', 'enabled')")
                self.db.commit()
                autosave = "enabled"
            
            try:
                self.cur.execute(f"select value from __main__ where setting = 'diaries-format'")
                format = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('diaries-format', 'markdown')")
                self.db.commit()
                format = "markdown"
                
        return autosave, format
    
    def getDockSettings(self) -> tuple:
        if not self.createTable():
            print("[2] Failed to create table")
            sys.exit(2)
            
        try:
            self.cur.execute(f"select value from __main__ where setting = 'sidebar-status'")
            status = str(self.cur.fetchone()[0])

        except TypeError:
            self.cur.execute(f"insert into __main__ (setting, value) values ('sidebar-status', 'enabled')")
            self.db.commit()
            status = "enabled"
            
        try:
            self.cur.execute(f"select value from __main__ where setting = 'sidebar-area'")
            area = str(self.cur.fetchone()[0])

        except TypeError:
            self.cur.execute(f"insert into __main__ (setting, value) values ('sidebar-area', 'left')")
            self.db.commit()
            area = "left"
            
        try:
            self.cur.execute(f"select value from __main__ where setting = 'sidebar-mode'")
            mode = str(self.cur.fetchone()[0])

        except TypeError:
            self.cur.execute(f"insert into __main__ (setting, value) values ('sidebar-mode', 'fixed')")
            self.db.commit()
            mode = "fixed"
                
        return status, area, mode
            
    def saveAutosaveAndFormat(self, module: str, autosave: str, format: str) -> bool:
        self.cur.execute(f"update __main__ set value = '{autosave}' where setting = '{module}-autosave'")
        self.db.commit()
        
        self.cur.execute(f"update __main__ set value = '{format}' where setting = '{module}-format'")
        self.db.commit()
        
        call_autosave, call_format = self.getAutosaveAndFormat(module)
        
        if call_autosave == autosave and call_format == format:
            return True
        else:
            return False
        
    def saveDockSettings(self, status: str, area: str, mode: str) -> bool:
        self.cur.execute(f"update __main__ set value = '{status}' where setting = 'sidebar-status'")
        self.db.commit()
        
        self.cur.execute(f"update __main__ set value = '{area}' where setting = 'sidebar-area'")
        self.db.commit()
        
        self.cur.execute(f"update __main__ set value = '{mode}' where setting = 'sidebar-mode'")
        self.db.commit()
        
        call_status, call_area, call_mode = self.getDockSettings()
        
        
        if call_status == status and call_area == area and call_mode == mode:
            return True
        else:
            return False
        
        
settingsdb = SettingsDB()
if not settingsdb.createTable():
    print("[2] Failed to create table")
    sys.exit(2)


class SettingsWidget(QWidget):
    def __init__(self, parent: QMainWindow) -> None:        
        super().__init__(parent)
        
        self.parent_ = parent
        self.menu = self.parent_.menuBar().addMenu(_("Settings"))
        
        self.setLayout(QHBoxLayout(self))
        
        self.stacked = QStackedWidget(self)
        self.stacked.addWidget(SettingsAutosaveAndFormatPage(self, "notes", _("Notes"), 0))
        self.stacked.addWidget(SettingsAutosaveAndFormatPage(self, "diaries", _("Diaries"), 1))
        
        self.list = QListWidget(self)
        self.list.setCurrentRow(0)
        self.list.setFixedWidth(90)
        self.list.currentRowChanged.connect(lambda: self.stacked.setCurrentIndex(self.list.currentRow()))
        
        self.list_notes = QListWidgetItem(_("Notes"), self.list)
        self.list_notes.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_diaries = QListWidgetItem(_("Diaries"), self.list)
        self.list_diaries.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list.addItem(self.list_notes)
        self.list.addItem(self.list_diaries)
        
        self.list.setCurrentRow(0)
        
        self.layout().addWidget(self.list)
        self.layout().addWidget(self.stacked)
        
        
class SettingsAutosaveAndFormatPage(QWidget):
    def __init__(self, parent: SettingsWidget, module: str, pretty: str, index: int) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.index = index
        self.autosave, self.format = settingsdb.getAutosaveAndFormat(self.module)
        
        self.parent_.menu.addAction(pretty, self.setIndexes)
        
        self.inputs = QWidget(self)
        self.inputs.setLayout(QFormLayout(self))
        
        self.checkbox = QCheckBox(self.inputs)
        self.checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        if self.autosave == "enabled":
            self.checkbox.setText(_("Enabled"))
            self.checkbox.setChecked(True)
        elif self.autosave == "disabled":
            self.checkbox.setText(_("Disabled"))
            self.checkbox.setChecked(False)
        try:
            self.checkbox.checkStateChanged.connect(self.setAutoSave)
        except:
            self.checkbox.stateChanged.connect(self.setAutoSave)
        
        self.combobox = QComboBox(self.inputs)
        self.combobox.addItems([_("Plain-text"), _("Markdown"), _("HTML")])
        self.combobox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        if self.format == "plain-text":
            self.combobox.setCurrentIndex(0)
        elif self.format == "markdown":
            self.combobox.setCurrentIndex(1)
        elif self.format == "html":
            self.combobox.setCurrentIndex(2)
        self.combobox.setEditable(False)
        self.combobox.currentIndexChanged.connect(self.setFormat)
            
        self.inputs.layout().addRow(_("Auto-save:"), self.checkbox)
        self.inputs.layout().addRow(_("Format:"), self.combobox)
            
        self.buttons = QWidget(self)
        self.buttons.setLayout(QHBoxLayout(self))
        
        self.reset = QPushButton(self.buttons, text=_("Reset"))
        self.reset.clicked.connect(self.resetSettings)
        
        self.save = QPushButton(self.buttons, text=_("Save"))
        self.save.clicked.connect(self.saveAutosaveAndFormat)
        
        self.buttons.layout().addStretch()
        self.buttons.layout().addWidget(self.reset)
        self.buttons.layout().addWidget(self.save)
            
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.inputs)
        self.layout().addStretch()
        self.layout().addWidget(self.buttons)
        
    def resetSettings(self) -> None:
        call = settingsdb.saveAutosaveAndFormat(self.module, "enabled", "markdown")
        
        if call:
            self.checkbox.setChecked(True)
            self.combobox.setCurrentIndex(1)
            
            QMessageBox.information(self.parent_, _("Successful"), _("Settings are reset."))
        
        else:
            QMessageBox.critical(self.parent_, _("Error"), _("Failed to reset settings."))
            
    def saveAutosaveAndFormat(self) -> None:
        call = settingsdb.saveAutosaveAndFormat(self.module, self.autosave, self.format)
        
        if call:
            QMessageBox.information(self.parent_, _("Successful"), _("New settings are saved."))
        
        else:
            QMessageBox.critical(self.parent_, _("Error"), _("Failed to save settings."))
            
    def setAutoSave(self, signal: Qt.CheckState | int) -> None:
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.autosave = "disabled"
            self.checkbox.setText(_("Disabled"))
        
        elif signal == Qt.CheckState.Checked or signal == 2:
            self.autosave = "enabled"
            self.checkbox.setText(_("Enabled"))
                
    def setFormat(self, index: int) -> None:
        if index == 0:
            self.format = "plain-text"
        elif index == 1:
            self.format = "markdown"
        elif index == 2:
            self.format = "html"
            
    def setIndexes(self) -> None:
        self.parent_.parent_.tabwidget.setCurrentIndex(4)
        self.parent_.list.setCurrentRow(self.index)