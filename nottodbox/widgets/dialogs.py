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
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


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
    
    def getSettings(self, module: str) -> tuple:
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
            
    def saveSettings(self, module: str, autosave: str, format: str) -> bool:
        self.cur.execute(f"update __main__ set value = '{autosave}' where setting = '{module}-autosave'")
        self.db.commit()
        
        self.cur.execute(f"update __main__ set value = '{format}' where setting = '{module}-format'")
        self.db.commit()
        
        call_autosave, call_format = self.getSettings(module)
        
        if call_autosave == autosave and call_format == format:
            return True
        
        else:
            return False
        

settingsdb = SettingsDB()
if not settingsdb.createTable():
    print("[2] Failed to create table")
    sys.exit(2)


class ColorDialog(QColorDialog):
    def __init__(self, color: QColor | Qt.GlobalColor | int, parent: QWidget, title: str) -> None:
        super().__init__(color, parent)
        self.setWindowTitle(title)
        
        self.buttonbox = self.findChild(QDialogButtonBox)
        
        self.set_to_default = QPushButton(self.buttonbox, text=_("Set to default"))
        self.set_to_default.clicked.connect(lambda: self.done(2))
        
        self.buttonbox.addButton(self.set_to_default, QDialogButtonBox.ButtonRole.DestructiveRole)
        
        self.exec()

    def getColor(self) -> tuple:
        if self.result() == 0:
            return "cancel", QColor()
        
        elif self.result() == 1:
            return "ok", self.selectedColor()
        
        elif self.result() == 2:
            return "ok", QColor()


class GetTwoDialog(QDialog):
    def __init__(self, parent: QWidget, mode: str, window_title: str, 
                 top_text: str, bottom_text: str, top_extra: int | str, bottom_extra: int | str) -> None:
        super().__init__(parent)
        
        self.mode = mode
        
        self.inputs = QWidget(self)
        self.inputs.setLayout(QFormLayout(self.inputs))
        
        if self.mode == "text":
            self.top_widget = QLineEdit(self.inputs)
            self.top_widget.setPlaceholderText(top_extra)
            
            self.bottom_widget = QLineEdit(self.inputs)
            self.bottom_widget.setPlaceholderText(bottom_extra)
        
        elif self.mode == "number":
            self.top_widget = QSpinBox(self.inputs)
            self.top_widget.setMinimum(top_extra)
            self.top_widget.setValue(top_extra)
            self.top_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
            self.bottom_widget = QSpinBox(self.inputs)
            self.bottom_widget.setMinimum(bottom_extra)
            self.bottom_widget.setValue(bottom_extra)
            self.bottom_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
        self.inputs.layout().addRow(top_text, self.top_widget)
        self.inputs.layout().addRow(bottom_text, self.bottom_widget)
        
        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.rejected.connect(lambda: self.done(0))
        self.buttons.accepted.connect(lambda: self.done(1))
        
        self.setWindowTitle(window_title)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.inputs)
        self.layout().addWidget(self.buttons)
        self.exec()
        
    def getItems(self) -> tuple:
        if self.result() == 1:
            if self.mode == "text":
                top_value = self.top_widget.text()
                bottom_value = self.bottom_widget.text()
                    
            elif self.mode == "number":
                top_value = self.top_widget.value()
                bottom_value = self.top_widget.value()
                
            return "ok", top_value, bottom_value

        else:
            return "cancel", None, None
        
        
class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget, module: str, autosave: str, format: str) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.autosave = autosave
        self.format = format
        
        self.inputs = QWidget(self)
        self.inputs.setLayout(QFormLayout(self))
        
        self.checkbox = QCheckBox(self.inputs, text=_("Auto-save"))
        self.checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        if self.autosave == "enabled":
            self.checkbox.setChecked(True)
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
            
        self.inputs.layout().addRow("Autosave:", self.checkbox)
        self.inputs.layout().addRow("Format:", self.combobox)
            
        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.rejected.connect(lambda: self.done(0))
        self.buttons.accepted.connect(lambda: self.done(1))
            
        self.setWindowTitle(_("Settings for {module}".format(module = str(self.module).title())))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.inputs)
        self.layout().addWidget(self.buttons)
        self.exec()
            
    def setAutoSave(self, signal: Qt.CheckState | int) -> None:
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.autosave = "disabled"
        elif signal == Qt.CheckState.Checked or signal == 2:
            self.autosave = "enabled"
                
    def setFormat(self, index: int) -> None:
        if index == 0:
            self.format = "plain-text"
        elif index == 1:
            self.format = "markdown"
        elif index == 2:
            self.format = "html"
            
    def saveSettings(self) -> tuple:
        if self.result() == 1:
            call = settingsdb.saveSettings(self.module, self.autosave, self.format)
            
            if call:
                QMessageBox.information(self.parent_, _("Successful"), _("New settings are saved."))
                return self.autosave, self.format
            
            else:
                QMessageBox.critical(self.parent_, _("Error"), _("Failed to save settings."))
                return None, None
            
        else:
            return None, None