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
from widgets.dialogs import ColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *


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
    
    def getModuleSettings(self, module: str) -> tuple:
        if not self.createTable():
            print("[2] Failed to create table")
            sys.exit(2)
            
        if module == "notes" or module == "diaries":
            try:
                self.cur.execute(f"select value from __main__ where setting = '{module}-autosave'")
                autosave = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('{module}-autosave', 'enabled')")
                self.db.commit()
                autosave = "enabled"
            
            try:
                self.cur.execute(f"select value from __main__ where setting = '{module}-format'")
                format = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('{module}-format', 'markdown')")
                self.db.commit()
                format = "markdown"
                
        if module == "notes" or module == "todos":
            try:
                self.cur.execute(f"select value from __main__ where setting = '{module}-background'")
                background = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('{module}-background', 'default')")
                self.db.commit()
                background = "default"
            
            try:
                self.cur.execute(f"select value from __main__ where setting = '{module}-foreground'")
                foreground = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('{module}-foreground', 'default')")
                self.db.commit()
                foreground = "default"
        
        if module == "diaries": 
            try:
                self.cur.execute(f"select value from __main__ where setting = '{module}-highlight'")
                highlight = str(self.cur.fetchone()[0])

            except TypeError:
                self.cur.execute(f"insert into __main__ (setting, value) values ('{module}-highlight', 'default')")
                self.db.commit()
                highlight = "default"
                
        if module == "notes":        
            return autosave, format, background, foreground
        
        elif module == "todos":
            return background, foreground
        
        elif module == "diaries":
            return autosave, format, highlight
    
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
            
    def saveModuleSettings(self, module: str, autosave: str | None, format: str | None, background: str | None, foreground: str | None, highlight: str | None) -> bool:
        if module == "notes" or module == "diaries":
            self.cur.execute(f"update __main__ set value = '{autosave}' where setting = '{module}-autosave'")
            self.db.commit()
            
            self.cur.execute(f"update __main__ set value = '{format}' where setting = '{module}-format'")
            self.db.commit()
            
        if module == "notes" or module == "todos":
            self.cur.execute(f"update __main__ set value = '{background}' where setting = '{module}-background'")
            self.db.commit()
            
            self.cur.execute(f"update __main__ set value = '{foreground}' where setting = '{module}-foreground'")
            self.db.commit()

        if module == "diaries":
            self.cur.execute(f"update __main__ set value = '{highlight}' where setting = '{module}-highlight'")
            self.db.commit()
            
        if module == "notes":
            call_autosave, call_format, call_background, call_foreground = self.getModuleSettings(module)
            
            if call_autosave == autosave and call_format == format and call_background == background and call_foreground == foreground:
                return True
            else:
                return False
            
        elif module == "todos":
            call_background, call_foreground = self.getModuleSettings(module)
            
            if call_background == background and call_foreground == foreground:
                return True
            else:
                return False
            
        elif module == "diaries":
            call_autosave, call_format, call_highlight = self.getModuleSettings(module)
            
            if call_autosave == autosave and call_format == format and call_highlight == highlight:
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
    def __init__(self, parent: QMainWindow, notes, todos, diaries) -> None:        
        super().__init__(parent)
        
        self.parent_ = parent
        self.menu = self.parent_.menuBar().addMenu(_("Settings"))
        
        self.stacked = QStackedWidget(self)
        self.stacked.addWidget(SettingsPage(self, "notes", _("Notes"), notes, 0))
        self.stacked.addWidget(SettingsPage(self, "todos", _("To-dos"), todos, 1))
        self.stacked.addWidget(SettingsPage(self, "diaries", _("Diaries"), diaries, 2))
        
        self.list = QListWidget(self)
        self.list.setCurrentRow(0)
        self.list.setFixedWidth(90)
        self.list.currentRowChanged.connect(lambda: self.stacked.setCurrentIndex(self.list.currentRow()))
        
        self.list_notes = QListWidgetItem(_("Notes"), self.list)
        self.list_notes.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_todos = QListWidgetItem(_("To-dos"), self.list)
        self.list_todos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_diaries = QListWidgetItem(_("Diaries"), self.list)
        self.list_diaries.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list.addItem(self.list_notes)
        self.list.addItem(self.list_diaries)
        
        self.list.setCurrentRow(0)
        
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(self.list)
        self.layout().addWidget(self.stacked)
        
        
class SettingsPage(QWidget):
    def __init__(self, parent: SettingsWidget, module: str, pretty: str, target, index: int) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.target = target
        self.index = index
        
        if self.module == "notes":
            self.autosave, self.format, self.background, self.foreground = settingsdb.getModuleSettings("notes")
            
        elif self.module == "todos":
            self.background, self.foreground = settingsdb.getModuleSettings("todos")
            
        elif self.module == "diaries":
            self.autosave, self.format, self.highlight = settingsdb.getModuleSettings("diaries")
        
        self.parent_.menu.addAction(pretty, self.setIndexes)
        
        self.inputs = QWidget(self)
        self.inputs.setLayout(QFormLayout(self))
            
        if self.module == "notes" or self.module == "diaries":    
            self.autosave_checkbox = QCheckBox(self.inputs)
            self.autosave_checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            if self.autosave == "enabled":
                self.autosave_checkbox.setText(_("Enabled"))
                self.autosave_checkbox.setChecked(True)
            elif self.autosave == "disabled":
                self.autosave_checkbox.setText(_("Disabled"))
                self.autosave_checkbox.setChecked(False)
            try:
                self.autosave_checkbox.checkStateChanged.connect(self.setAutoSave)
            except:
                self.autosave_checkbox.stateChanged.connect(self.setAutoSave)
            
            self.format_combobox = QComboBox(self.inputs)
            self.format_combobox.addItems([_("Plain-text"), _("Markdown"), _("HTML")])
            self.format_combobox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            if self.format == "plain-text":
                self.format_combobox.setCurrentIndex(0)
            elif self.format == "markdown":
                self.format_combobox.setCurrentIndex(1)
            elif self.format == "html":
                self.format_combobox.setCurrentIndex(2)
            self.format_combobox.setEditable(False)
            self.format_combobox.currentIndexChanged.connect(self.setFormat)
                
            self.inputs.layout().addRow(_("Auto-save:"), self.autosave_checkbox)
            self.inputs.layout().addRow(_("Format:"), self.format_combobox)
        
        if self.module == "notes" or self.module == "todos":
            self.background_button = QPushButton(self, 
                                                 text=_("Select color (it is {color})")
                                                 .format(color = _("default") if self.background == "default" else self.background))
            self.background_button.clicked.connect(self.setBackground)
            
            self.foreground_button = QPushButton(self, 
                                                 text=_("Select color (it is {color})")
                                                 .format(color = _("default") if self.foreground == "default" else self.foreground))
            self.foreground_button.clicked.connect(self.setForeground)
            
            self.inputs.layout().addRow(_("Background color:"), self.background_button)
            self.inputs.layout().addRow(_("Text color:"), self.foreground_button)
            
        if self.module == "diaries":
            self.highlight_button = QPushButton(self, 
                                                 text=_("Select color (it is {color})")
                                                 .format(color = _("default") if self.highlight == "default" else self.highlight))
            self.highlight_button.clicked.connect(self.setHighlight)
            
            self.inputs.layout().addRow(_("Highlight color:"), self.highlight_button)
                
        self.buttons = QDialogButtonBox(self)
        
        self.save = QPushButton(self.buttons, text=_("Save"))
        self.save.clicked.connect(self.saveSettings)
        
        self.reset = QPushButton(self.buttons, text=_("Reset"))
        self.reset.clicked.connect(self.resetSettings)
        
        self.buttons.addButton(self.save, QDialogButtonBox.ButtonRole.ApplyRole)
        self.buttons.addButton(self.reset, QDialogButtonBox.ButtonRole.ApplyRole)
        
        self.format_changed = False
            
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.inputs)
        self.layout().addStretch()
        self.layout().addWidget(self.buttons)
        
    def askFormatChange(self) -> bool:
        if self.format_changed:
            accepted = QMessageBox.question(
                self, _("Question"), _("If you have documents with the format setting set to global," +
                                       " this change may corrupt them.\nAre you sure?"))
            
            if accepted == QMessageBox.StandardButton.Yes:
                self.format_changed = False
                
                return True
            
            else:
                return False
            
        else:
            return True
        
    def resetSettings(self) -> None:
        if self.module == "notes":
            format_change_acceptted = self.askFormatChange()
            
            if format_change_acceptted:
                call = settingsdb.saveModuleSettings(
                    self.module, "enabled", "markdown", "default", "default", None)
                
            else:
                return
        
        elif self.module == "todos":
            call = settingsdb.saveModuleSettings(
                self.module, None, None, "default", "default", None)
        
        elif self.module == "diaries":
            format_change_acceptted = self.askFormatChange()
            
            if format_change_acceptted:
                call = settingsdb.saveModuleSettings(
                    self.module, "enabled", "markdown", None, None, "default")
            
            else:
                return
        
        if call:
            if self.module == "notes":
                self.background = "default"
                self.foreground = "default"
                
                self.autosave_checkbox.setChecked(True)
                self.format_combobox.setCurrentIndex(1)
                self.background_button.setText(_("Select color (it is {color})")
                                               .format(color = _("default") if self.background == "default" else self.background))
                self.foreground_button.setText(_("Select color (it is {color})")
                                               .format(color = _("default") if self.foreground == "default" else self.foreground))
                
            elif self.module == "todos":
                self.background = "default"
                self.foreground = "default"
                
                self.background_button.setText(_("Select color (it is {color})")
                                            .format(color = _("default") if self.background == "default" else self.background))
                self.foreground_button.setText(_("Select color (it is {color})")
                                               .format(color = _("default") if self.foreground == "default" else self.foreground))
            
            elif self.module == "diaries":
                self.highlight = "default"
                
                self.autosave_checkbox.setChecked(True)
                self.format_combobox.setCurrentIndex(1)
                self.highlight_button.setText(_("Select color (it is {color})")
                                              .format(color = _("default") if self.highlight == "default" else self.highlight))
                
            self.target.refreshSettings()
            
            QMessageBox.information(self.parent_, _("Successful"), _("Settings are reset."))
        
        else:
            QMessageBox.critical(self.parent_, _("Error"), _("Failed to reset settings."))
            
    def saveSettings(self) -> None:
        if self.module == "notes":
            format_change_acceptted = self.askFormatChange()
                
            if format_change_acceptted:
                call = settingsdb.saveModuleSettings(
                    self.module, self.autosave, self.format, self.background, self.foreground, None)
                
            else:
                return
        
        elif self.module == "todos":
            call = settingsdb.saveModuleSettings(
                self.module, None, None, self.background, self.foreground, None)
        
        elif self.module == "diaries":
            format_change_acceptted = self.askFormatChange()
            
            if format_change_acceptted:
                call = settingsdb.saveModuleSettings(
                    self.module, self.autosave, self.format, None, None, self.highlight)
            
            else:
                return
        
        if call:
            self.target.refreshSettings()
            
            QMessageBox.information(self.parent_, _("Successful"), _("New settings are saved."))
        
        else:
            QMessageBox.critical(self.parent_, _("Error"), _("Failed to save settings."))
            
    def setAutoSave(self, signal: Qt.CheckState | int) -> None:
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.autosave = "disabled"
            self.autosave_checkbox.setText(_("Disabled"))
        
        elif signal == Qt.CheckState.Checked or signal == 2:
            self.autosave = "enabled"
            self.autosave_checkbox.setText(_("Enabled"))
            
    def setBackground(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, 
            QColor(self.background if self.background != "default" else "#FFFFFFF"), 
            _("Select Background Color")).getColor()
        
        if ok:
            self.background = qcolor.name() if status == "new" else "default"
            
            self.background_button.setText(_("Select color (it is {color})")
                                           .format(color = _("default") if self.background == "default" else self.background))
            
    def setForeground(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, 
            QColor(self.foreground if self.foreground != "default" else "#FFFFFF"), 
            _("Select Text Color")).getColor()
        
        if ok:
            self.foreground = qcolor.name() if status == "new" else "default"
            
            self.foreground_button.setText(_("Select color (it is {color})")
                                           .format(color = _("default") if self.foreground == "default" else self.foreground))
                
    def setFormat(self, index: int) -> None:
        self.format_changed = True
        
        if index == 0:
            self.format = "plain-text"
        elif index == 1:
            self.format = "markdown"
        elif index == 2:
            self.format = "html"
            
    def setHighlight(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, 
            QColor(self.highlight if self.highlight != "default" else "#376296"), 
            _("Select Highlight Color")).getColor()
        
        if ok:
            self.highlight = qcolor.name() if status == "new" else "default"
                    
            self.highlight_button.setText(_("Select color (it is {color})")
                                           .format(color = _("default") if self.highlight == "default" else self.highlight))
            
    def setIndexes(self) -> None:
        self.parent_.parent_.tabwidget.setCurrentIndex(4)
        self.parent_.list.setCurrentRow(self.index)