# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024-2025 Mukonqi (Muhammed S.)

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


from gettext import gettext as _
from PySide6.QtCore import Slot, Qt, QSettings
from PySide6.QtGui import QColor
from PySide6.QtWidgets import *
from widgets.dialogs import ColorDialog
from widgets.others import HSeperator, PushButton, VSeperator


class Settings(QSettings):
    def __init__(self) -> None:
        super().__init__("io.github.mukonqi", "nottodbox")
        
        values_ = self.get()
        
        for values in values_:
            if values == [] and not self.reset():
                print("[2] Failed to set configuration file")
                exit(2)
    
    def get(self, module_: str | None = None) -> list[str] | list[list[str]]:
        if module_ is None:
            values = []
            
            for module in ["notes", "todos", "diaries"]:
                values.append(self.getBase(module))
                
            return values
        
        else:
            return self.getBase(module_)

    def getBase(self, module: str) -> list[str]:
        self.beginGroup(module)
        
        values = []
        
        for key in self.allKeys():
            values.append(self.value(key))
        
        self.endGroup()
        
        return values
    
    def reset(self, module_: str | None = None) -> bool:
        if module_ is None:
            successful = True
            
            for module in ["notes", "todos", "diaries"]:
                if not self.resetBase(module):
                    successful = False
                
            return successful
        
        else:
            return self.resetBase(module_)
        
    def resetBase(self, module: str) -> bool:
        if module == "notes":
            return self.set(module, "enabled", "default", "default", "markdown", "")
        
        elif module == "todos":
            return self.set(module, "", "default", "default", "", "")
        
        elif module == "diaries":
            return self.set(module, "enabled", "", "", "markdown", "#376296")
    
    def set(self, module: str, autosave: str, background: str, foreground: str, format: str, highlight: str) -> bool:
        values = locals()
        values.pop("self")
        values.pop("module")
        
        self.beginGroup(module)
        
        for key, value in values.items():
            self.setValue(key, value)

        self.endGroup()
        
        return self.getBase(module) == list(values.values())
        
        
settings = Settings()
    

class SettingsWidget(QWidget):
    def __init__(self, parent: QMainWindow, notes, todos, diaries) -> None:        
        super().__init__(parent)
        
        self.parent_ = parent
        self.layout_ = QGridLayout(self)
        
        self.menu = self.parent_.menuBar().addMenu(_("Settings"))
        
        self.list = QListWidget(self)
        self.list.setFixedWidth(100)
        
        self.list_notes = QListWidgetItem(_("Notes"), self.list)
        self.list_notes.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_todos = QListWidgetItem(_("To-dos"), self.list)
        self.list_todos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_diaries = QListWidgetItem(_("Diaries"), self.list)
        self.list_diaries.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.stacked = QStackedWidget(self)
        
        self.pages = [
            SettingsPage(self, "notes", _("Notes"), notes, 0),
            SettingsPage(self, "todos", _("To-dos"), todos, 1),
            SettingsPage(self, "diaries", _("Diaries"), diaries, 2)
        ]
        
        self.buttons = QDialogButtonBox(self)
        
        self.reset = PushButton(self.buttons, _("Reset"))
        self.reset.clicked.connect(self.resetAll)
        
        self.apply = PushButton(self.buttons, _("Apply"))
        self.apply.clicked.connect(self.applyAll)
        
        self.cancel = PushButton(self.buttons, _("Cancel"))
        self.cancel.clicked.connect(self.cancelAll)
        
        self.list.addItem(self.list_notes)
        self.list.addItem(self.list_todos)
        self.list.addItem(self.list_diaries)
        
        for page in self.pages:
            self.stacked.addWidget(page)
        
        self.buttons.addButton(self.reset, QDialogButtonBox.ButtonRole.ResetRole)
        self.buttons.addButton(self.apply, QDialogButtonBox.ButtonRole.ApplyRole)
        self.buttons.addButton(self.cancel, QDialogButtonBox.ButtonRole.RejectRole)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.list, 0, 0, 3, 1)
        self.layout_.addWidget(VSeperator(self), 0, 1, 3, 1)
        self.layout_.addWidget(self.stacked, 0, 2, 1, 1)
        self.layout_.addWidget(HSeperator(self), 1, 2, 1, 1)
        self.layout_.addWidget(self.buttons, 2, 2, 1, 1)
        
        self.list.setCurrentRow(0)
        self.list.currentRowChanged.connect(lambda: self.stacked.setCurrentIndex(self.list.currentRow()))
        
    @Slot()
    def applyAll(self) -> None:
        successful = True
        ask_question = True
        
        for page in self.pages:
            if page.format_changed and ask_question:
                ask_question = False
                
                question = QMessageBox.question(
                    self, _("Question"), _("If you have documents with the format setting set to global," +
                                           " this change may corrupt them.\nDo you really want to apply new settings?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    return
                
            call = page.applySettings(False)
            
            if not call:
                successful = False
        
        if successful:
            QMessageBox.information(self, _("Successful"), _("All new settings applied."))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to apply all new settings."))
    
    @Slot()
    def cancelAll(self) -> None:
        for page in self.pages:
            page.setSettingsFromDB()
    
    @Slot()
    def resetAll(self) -> None:
        successful = True
        ask_question = True
        
        for page in self.pages:
            if page.format_changed and ask_question:
                ask_question = False
                
                question = QMessageBox.question(
                    self, _("Question"), _("If you have documents with the format setting set to global," +
                                           " this change may corrupt them.\nDo you really want to apply new settings?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    return
                
            call = page.resetSettings(False)
            
            if not call:
                successful = False
        
        if successful:
            QMessageBox.information(self, _("Successful"), _("All setting reset."))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset all settings."))
              
        
class SettingsPage(QWidget):
    def __init__(self, parent: SettingsWidget, module: str, pretty: str, target, index: int) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.target = target
        self.index = index
        
        self.parent_.menu.addAction(pretty, self.setIndexes)
        
        self.layout_ = QVBoxLayout(self)
        
        self.format_changed = False
        self.startup = True
        
        self.inputs = QWidget(self)
        self.form = QFormLayout(self.inputs)
        self.inputs.setLayout(self.form)
            
        if self.module == "notes" or self.module == "diaries":    
            self.autosave_checkbox = QCheckBox(self.inputs)
            self.autosave_checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            try:
                self.autosave_checkbox.checkStateChanged.connect(self.setAutosave)
            except:
                self.autosave_checkbox.stateChanged.connect(self.setAutosave)
            
            self.format_combobox = QComboBox(self.inputs)
            self.format_combobox.addItems([_("Plain-text"), "Markdown", "HTML"])
            self.format_combobox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.format_combobox.setEditable(False)
            self.format_combobox.currentIndexChanged.connect(self.setFormat)
                
            self.form.addRow(_("Auto-save:"), self.autosave_checkbox)
            self.form.addRow(_("Format:"), self.format_combobox)
        
        if self.module == "notes" or self.module == "todos":
            self.background_button = PushButton(self, "")
            self.background_button.clicked.connect(self.setBackground)
            
            self.foreground_button = PushButton(self, "")
            self.foreground_button.clicked.connect(self.setForeground)
            
            self.form.addRow("{}:".format(_("Background color")), self.background_button)
            self.form.addRow("{}:".format(_("Text color")), self.foreground_button)
            
        if self.module == "diaries":
            self.highlight_button = PushButton(self, "")
            self.highlight_button.clicked.connect(self.setHighlight)
            
            self.form.addRow("{}:".format(_("Highlight color")), self.highlight_button)
            
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.inputs)
        
        self.setSettingsFromDB()
        
    def askFormatChange(self, definitely: bool = False) -> bool:
        if self.format_changed or definitely:
            question = QMessageBox.question(
                self, _("Question"), _("If you have documents with the format setting set to global," +
                                       " this change may corrupt them.\nDo you really want to apply new settings?"))
            
            if question == QMessageBox.StandardButton.Yes:
                self.format_changed = False
                
                return True
            
            else:
                return False
            
        else:
            return True
        
    def applySettings(self, messages: bool = True) -> bool:
        if messages:
            if not self.askFormatChange():
                return False
        
        if self.module == "notes":
            call = settings.set(self.module, self.autosave, self.background, self.foreground, self.format, "")
        
        elif self.module == "todos":
            call = settings.set(self.module, "", self.background, self.foreground, self.format, "")
        
        elif self.module == "diaries":
            call = settings.set(self.module, self.autosave, "", "", self.format, self.highlight)
        
        if call:
            self.target.refreshSettings()
            
            if self.module == "diaries":
                if self.parent_.parent_.home.diary.call_format == "global":
                    self.parent_.parent_.home.diary.format = self.format
                    self.parent_.parent_.home.diary.formatter.updateStatus(self.format)
                    
                self.parent_.parent_.home.diary.format_combobox.setItemText(0, "{} {}".format(_("Format:"), _("Follow global ({setting})")
                                                                                              .format(setting = self.parent_.parent_.home.diary.prettyFormat(self.format))))
                
                if self.parent_.parent_.home.diary.call_autosave == "global":
                    self.parent_.parent_.home.diary.autosave = self.autosave
                    
                    self.parent_.parent_.home.diary.changeAutosaveConnections()
                    
                self.parent_.parent_.home.diary.autosave_combobox.setItemText(0, "{} {}".format(_("Auto-save:"), _("Follow global ({setting})")
                                                                                                .format(setting = self.parent_.parent_.home.diary.prettyAutosave(self.autosave))))
            
            if messages:
                QMessageBox.information(self.parent_, _("Successful"), _("New settings are applied."))
                
            return True
        
        else:
            if messages:
                QMessageBox.critical(self.parent_, _("Error"), _("Failed to apply new settings."))
                
            return False
        
    def resetSettings(self, messages: bool = True) -> bool:
        if messages:
            if not self.askFormatChange(True):
                return False
        
        if settings.reset(self.module):
            self.setSettingsFromDB()
                
            self.target.refreshSettings()
            
            if messages:
                QMessageBox.information(self.parent_, _("Successful"), _("Settings are reset."))
                
            return True
        
        else:
            if messages:
                QMessageBox.critical(self.parent_, _("Error"), _("Failed to reset settings."))
                
            return False
            
    @Slot(int or Qt.CheckState)
    def setAutosave(self, signal: Qt.CheckState | int) -> None:
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.autosave = "disabled"
            self.autosave_checkbox.setText(_("Disabled"))
        
        elif signal == Qt.CheckState.Checked or signal == 2:
            self.autosave = "enabled"
            self.autosave_checkbox.setText(_("Enabled"))
            
    @Slot()
    def setBackground(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, 
            QColor(self.background if self.background != "default" else "#FFFFFFF"), 
            _("Select Background Color")).getColor()
        
        if ok:
            self.background = qcolor.name() if status == "new" else "default"
            
            self.background_button.setText(_("Select color (it is {color})")
                                           .format(color = _("default") if self.background == "default" else self.background))
          
    @Slot()  
    def setForeground(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, 
            QColor(self.foreground if self.foreground != "default" else "#FFFFFF"), 
            _("Select Text Color")).getColor()
        
        if ok:
            self.foreground = qcolor.name() if status == "new" else "default"
            
            self.foreground_button.setText(_("Select color (it is {color})")
                                           .format(color = _("default") if self.foreground == "default" else self.foreground))
                
    @Slot(int)
    def setFormat(self, index: int) -> None:
        if self.startup:
            self.startup = False
        
        else:
            self.format_changed = True
        
        if index == 0:
            self.format = "plain-text"
        elif index == 1:
            self.format = "markdown"
        elif index == 2:
            self.format = "html"
            
    @Slot()
    def setHighlight(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, 
            QColor(self.highlight if self.highlight != "default" else "#376296"), 
            _("Select Highlight Color")).getColor()
        
        if ok:
            self.highlight = qcolor.name() if status == "new" else "#376296"
                    
            self.highlight_button.setText(_("Select color (it is {color})")
                                           .format(color = _("default") if self.highlight == "default" else self.highlight))
            
    def setIndexes(self) -> None:
        self.parent_.parent_.tabwidget.setCurrentIndex(4)
        self.parent_.list.setCurrentRow(self.index)
        
    def setSettingsFromDB(self) -> None:
        self.autosave, self.background, self.foreground, self.format, self.highlight = settings.get(self.module)
        
        if self.module == "notes" or self.module == "diaries":    
            if self.autosave == "enabled":
                self.autosave_checkbox.setText(_("Enabled"))
                self.autosave_checkbox.setChecked(True)
            elif self.autosave == "disabled":
                self.autosave_checkbox.setText(_("Disabled"))
                self.autosave_checkbox.setChecked(False)
        
            if self.format == "plain-text":
                self.format_combobox.setCurrentIndex(0)
                
            elif self.format == "markdown":
                self.format_combobox.setCurrentIndex(1)
                
            elif self.format == "html":
                self.format_combobox.setCurrentIndex(2)
        
        if self.module == "notes" or self.module == "todos":
            self.background_button.setText(_("Select color (it is {color})")
                                           .format(color = _("default") if self.background == "default" else self.background))
            
            self.foreground_button.setText(_("Select color (it is {color})")
                                           .format(color = _("default") if self.foreground == "default" else self.foreground))

        if self.module == "diaries":
            self.highlight_button.setText(_("Select color (it is {color})")
                                          .format(color = _("default") if self.highlight == "default" else self.highlight))