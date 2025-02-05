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


import getpass
import os
import json
from gettext import gettext as _
from PySide6.QtCore import Slot, Qt, QSettings
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import *
from widgets.dialogs import ColorDialog
from widgets.others import HSeperator, Label, PushButton, VSeperator


USER_NAME = getpass.getuser()

SYSTEM_COLOR_SCHEMES_DIR = "@COLOR-SCHEMES@"
USER_COLOR_SCHEMES_DIR = f"/home/{USER_NAME}/.local/share/io.github.mukonqi/nottodbox/color-schemes"
if not os.path.isdir(USER_COLOR_SCHEMES_DIR):
    os.makedirs(USER_COLOR_SCHEMES_DIR)


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
    

class SettingsWindow(QDialog):
    def __init__(self, parent: QMainWindow, notes, todos, diaries) -> None:        
        super().__init__(parent)
        
        self.parent_ = parent
        self.layout_ = QGridLayout(self)
        
        self.parent_.menuBar().addAction(_("Settings"), lambda: self.exec())
        
        self.list = QListWidget(self)
        self.list.setFixedWidth(100)
        
        self.list_appearance = QListWidgetItem(_("Appearance"), self.list)
        self.list_appearance.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_notes = QListWidgetItem(_("Notes"), self.list)
        self.list_notes.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_todos = QListWidgetItem(_("To-dos"), self.list)
        self.list_todos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_diaries = QListWidgetItem(_("Diaries"), self.list)
        self.list_diaries.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea {border: 0px;}")
        scroll_area.setWidget(AppearanceSettings(self))
        scroll_area.apply = scroll_area.widget().apply
        scroll_area.load = scroll_area.widget().load
        scroll_area.reset = scroll_area.widget().reset
        
        self.stacked = QStackedWidget(self)
        
        self.pages = [
            scroll_area,
            ModuleSettings(self, "notes", notes),
            ModuleSettings(self, "todos",  todos),
            ModuleSettings(self, "diaries", diaries)
        ]
        
        self.buttons = QDialogButtonBox(self)
        
        self.reset_button = PushButton(self.buttons, _("Reset"))
        self.reset_button.clicked.connect(self.reset)
        
        self.apply_button = PushButton(self.buttons, _("Apply"))
        self.apply_button.clicked.connect(self.apply)
        
        self.cancel_button = PushButton(self.buttons, _("Cancel"))
        self.cancel_button.clicked.connect(self.cancel)
        
        self.list.addItem(self.list_appearance)
        self.list.addItem(self.list_notes)
        self.list.addItem(self.list_todos)
        self.list.addItem(self.list_diaries)
        
        for page in self.pages:
            self.stacked.addWidget(page)
        
        self.buttons.addButton(self.reset_button, QDialogButtonBox.ButtonRole.ResetRole)
        self.buttons.addButton(self.apply_button, QDialogButtonBox.ButtonRole.ApplyRole)
        self.buttons.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.list, 0, 0, 3, 1)
        self.layout_.addWidget(VSeperator(self), 0, 1, 3, 1)
        self.layout_.addWidget(self.stacked, 0, 2, 1, 1)
        self.layout_.addWidget(HSeperator(self), 1, 2, 1, 1)
        self.layout_.addWidget(self.buttons, 2, 2, 1, 1)
        
        self.list.setCurrentRow(0)
        self.list.currentRowChanged.connect(lambda: self.stacked.setCurrentIndex(self.list.currentRow()))
        
        self.setWindowTitle(_("Settings") + " — Nottodbox")
        self.setMinimumSize(750, 525)
        
    @Slot()
    def apply(self) -> None:
        successful = True
                
        for page in self.pages:            
            if not page.apply():
                successful = False
        
        if successful:
            QMessageBox.information(self, _("Successful"), _("All new settings applied."))
            
            self.done(1)
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to apply all new settings."))
            
            self.done(0)
    
    @Slot()
    def cancel(self) -> None:
        for page in self.pages:
            page.load()
    
    @Slot()
    def reset(self) -> None:
        successful = True
        
        for page in self.pages:                
            if not page.reset():
                successful = False
        
        if successful:
            QMessageBox.information(self, _("Successful"), _("All setting reset."))
            
            self.done(1)
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset all settings."))
            
            self.done(0)
            

class AppearanceSettings(QWidget):
    def __init__(self, parent: SettingsWindow) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.default_style = self.parent_.parent_.application.default_style.title()
        
        self.form = QFormLayout(self)
        
        self.styles_list = QStyleFactory.keys()
        self.styles_list.insert(0, _("System default ({})").format(self.default_style))
        
        self.styles_combobox = QComboBox(self)
        self.styles_combobox.setEditable(False)
        self.styles_combobox.addItems(self.styles_list)
        
        self.color_schemes_combobox = QComboBox(self)
        self.color_schemes_combobox.setEditable(False)
        
        self.custom_color_schemes = CustomColorSchemes(self)
        
        self.load()
        
        self.setLayout(self.form)
        self.form.addRow(_("Style:*"), self.styles_combobox)
        self.form.addRow(_("Color scheme:"), self.color_schemes_combobox)
        self.form.addRow(_("Custom color scheme:"), self.custom_color_schemes.name)
        self.form.addWidget(self.custom_color_schemes)
        self.form.addRow(HSeperator(self))
        self.form.addRow(Label(self, _("If PySide6 is installed with Pip, some system themes may not detected by Qt."), False))
        self.form.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        
        self.styles_combobox.currentTextChanged.connect(self.styleChanged)
        self.color_schemes_combobox.currentTextChanged.connect(self.colorSchemeChanged)
        
    def apply(self) -> bool:
        successful = True
        
        if self.use_default_style:
            settings.setValue("appearance/style", "")
            QApplication.setStyle(self.default_style)
            
            if settings.value("appearance/style") != "":
                successful = False
            
        else:
            settings.setValue("appearance/style", self.current_style)
            QApplication.setStyle(self.current_style)
            
            if settings.value("appearance/style") != self.current_style:
                successful = False
                
        if not self.custom_color_schemes.apply():
            successful = False
        
        if self.use_default_color_scheme:
            settings.setValue("appearance/color-scheme", "")
            
            if settings.value("appearance/color-scheme") != "":
                successful = False
            
        else:
            settings.setValue("appearance/color-scheme", self.current_color_scheme)
            
            if settings.value("appearance/color-scheme") != self.current_color_scheme:
                successful = False
                
        self.loadPalette()
                
        return successful
    
    @Slot(str)
    def colorSchemeChanged(self, value: str) -> None:
        if value == _("From selected style ({})").format(self.current_style):
            self.current_color_scheme = ""
            self.use_default_color_scheme = True
            self.custom_color_schemes.setEnabled(False)
        
        elif value == _("Custom"):
            self.custom_color_schemes.setEnabled(True)
            
        else:
            self.current_color_scheme = value
            self.use_default_color_scheme = False
            self.custom_color_schemes.setEnabled(False)
        
    def load(self) -> None:
        self.current_style = settings.value("appearance/style")
        
        if self.current_style is None:
            settings.setValue("appearance/style", "")
            self.current_style = self.default_style
            self.use_default_style = True
        
        elif self.current_style == "":
            self.current_style = self.default_style
            self.use_default_style = True
            
        else:
            QApplication.setStyle(self.current_style)
            
            self.use_default_style = False
        
        self.color_schemes = {}
        
        for entry in os.scandir(SYSTEM_COLOR_SCHEMES_DIR):
            if entry.is_file() and entry.name.endswith(".json"):
                with open(entry.path) as file:
                    data = json.load(file)
                    
                    self.color_schemes[data["name"]] = data["colors"]
        
        for entry in os.scandir(USER_COLOR_SCHEMES_DIR):
            if entry.is_file() and entry.name.endswith(".json"):
                with open(entry.path) as file:
                    data = json.load(file)
                    
                    if data["name"] in self.color_schemes.copy().keys():
                        self.color_schemes[data["name"] + _("(System)")] = data.pop("name")
                        self.color_schemes[data["name"] + _("(User)")] = data["colors"]
                        
                    else:
                        self.color_schemes[data["name"]] = data["colors"]
        
        self.color_schemes_list = list(self.color_schemes.keys())
        self.color_schemes_list.insert(0, _("From selected style ({})"))
        self.color_schemes_list.append(_("Custom"))
        
        self.color_schemes_combobox.addItems(self.color_schemes_list)
        
        self.current_color_scheme = settings.value("appearance/color-scheme")
        
        if self.current_color_scheme in self.color_schemes.keys():
            self.use_default_color_scheme = False
            
            self.color_schemes_combobox.setCurrentText(self.current_color_scheme)
        
        else:
            if self.current_color_scheme is None:
                settings.setValue("appearance/color-scheme", "")

            self.current_color_scheme = ""

            self.use_default_color_scheme = True
            
            self.color_schemes_combobox.setCurrentIndex(0)
        
        self.loadOnlySomeTexts()
        self.loadPalette()
        
    def loadOnlySomeTexts(self) -> None:
        self.color_schemes_list[0] = _("From selected style ({})").format(self.current_style)
        self.color_schemes_combobox.setItemText(0, self.color_schemes_list[0])
        
    def loadPalette(self) -> None:
        if not self.use_default_color_scheme:
            palette = QPalette()
            
            for key in self.color_schemes[self.current_color_scheme].keys():
                    palette.setColor(QPalette.ColorRole[key], self.color_schemes[self.current_color_scheme][key])
            
            QApplication.setPalette(palette)
        
    def reset(self) -> bool:
        settings.remove("appearance/style")
        settings.remove("appearance/color-scheme")
        
        if settings.value("appearance/style") is None and settings.value("appearance/color-scheme") is None:
            self.load()
            
            return self.apply()
        
        else:
            return False
        
    @Slot(str)
    def styleChanged(self, value: str) -> None:
        if value == _("System default ({})").format(self.default_style):
            self.current_style = self.default_style
            self.use_default_style = True
        
        else:
            self.current_style = value
            self.use_default_style = False
            
        self.loadOnlySomeTexts()
    
    
class CustomColorSchemes(QWidget):
    def __init__(self, parent: AppearanceSettings) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.name = QLineEdit(self.parent_)
        self.name.setClearButtonEnabled(True)
        self.name.setPlaceholderText(f"Color scheme by {USER_NAME}")
        
        self.form = QFormLayout(self)
               
        self.labels = {"Window": _("Window"),
                       "WindowText": _("Window text"),
                       "Base": _("Base"),
                       "Shadow": _("Shadow"),
                       "Accent": _("Accent"),
                       "Text": _("Text"),
                       "BrightText": _("Bright text"),
                       "PlaceholderText": _("Placeholder text"),
                       "Button": _("Button"),
                       "ButtonText": _("Button text"),
                       "ToolTipBase": _("Tooltip base"),
                       "ToolTipText": _("Tooltip text"),
                       "Highlight": _("Highlight"),
                       "HighlightedText": _("Highlighted text")}
        
        self.buttons = {}
        
        self.values = {}
        
        for color_role in self.labels.keys():
            self.values[color_role] = ""
            
            self.buttons[color_role] = PushButton(self, _("Select color (selected: {})").format(_("none")))
            self.buttons[color_role].clicked.connect(lambda state, color_role = color_role: self.setColorRoleValue(False, color_role))
            
            self.form.addRow(f"{self.labels[color_role]}:", self.buttons[color_role])
        
        self.setLayout(self.form)
        self.setEnabled(False)
        
    def apply(self) -> bool:
        if self.parent_.color_schemes_combobox.currentText() == _("Custom"):
            name = self.name.text()
            
            if name == "":
                name = self.name.placeholderText()
            
            data = {"name": name}
            
            color_scheme = {}
            
            for color_role in self.labels.keys():
                if self.values[color_role] != "":
                    color_scheme[color_role] = self.values[color_role]
                
            data["colors"] = color_scheme
            
            with open(f"{USER_COLOR_SCHEMES_DIR}/{name}.json", "w") as file:
                json.dump(data, file)
                
            with open(f"{USER_COLOR_SCHEMES_DIR}/{name}.json") as file:
                check_data = json.load(file)
                
            if data == check_data:
                self.parent_.color_schemes[name] = color_scheme
                self.parent_.color_schemes_list.insert(len(self.parent_.color_schemes_list) - 2, name)
                self.parent_.color_schemes_combobox.addItems(self.parent_.color_schemes_list)
                self.parent_.color_schemes_combobox.setCurrentText(name)
                
                return True
            
            else:
                return False
        
        else:
            return True
    
    @Slot(bool)
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.name.setEnabled(enabled)
            
    @Slot(bool, str)
    def setColorRoleValue(self, state: bool, color_role: str) -> None:
        ok, status, qcolor = ColorDialog(self, False, False, 
                                         QColor(self.values[color_role] if color_role in self.values else "#000000"), 
                                         _("Select {} Color").format(self.labels[color_role].title())).getColor()
        
        if ok:
            if status == "new":
                self.values[color_role] = qcolor.name()
                
                self.buttons[color_role].setText(_("Select color (selected: {})").format(_(self.values[color_role])))
                self.buttons[color_role].setStyleSheet(f"background-color: {self.values[color_role]};")

        
class ModuleSettings(QWidget):
    def __init__(self, parent: SettingsWindow, module: str, target) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.target = target
        
        self.format_changed = False
        self.do_not_check = True
        
        self.form = QFormLayout(self)
            
        if self.module == "notes" or self.module == "diaries":    
            self.autosave_checkbox = QCheckBox(self)
            self.autosave_checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            try:
                self.autosave_checkbox.checkStateChanged.connect(self.setAutosave)
            except:
                self.autosave_checkbox.stateChanged.connect(self.setAutosave)
            
            self.format_combobox = QComboBox(self)
            self.format_combobox.addItems([_("Plain-text"), "Markdown", "HTML"])
            self.format_combobox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.format_combobox.setEditable(False)
            self.format_combobox.currentIndexChanged.connect(self.setFormat)
                
            self.form.addRow(_("Auto-save:"), self.autosave_checkbox)
            self.form.addRow(_("Format:"), self.format_combobox)
        
        if self.module == "notes" or self.module == "todos":
            self.background_button = PushButton(self)
            self.background_button.clicked.connect(self.setBackground)
            
            self.foreground_button = PushButton(self)
            self.foreground_button.clicked.connect(self.setForeground)
            
            self.form.addRow("{}:".format(_("Background color")), self.background_button)
            self.form.addRow("{}:".format(_("Text color")), self.foreground_button)
            
        if self.module == "diaries":
            self.highlight_button = PushButton(self)
            self.highlight_button.clicked.connect(self.setHighlight)
            
            self.form.addRow("{}:".format(_("Highlight color")), self.highlight_button)
            
        self.setLayout(self.form)
        
        self.load()
        
    def apply(self) -> bool:
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
                
            return True
        
        else:
            return False
        
    def load(self) -> None:
        self.autosave, self.background, self.foreground, self.format, self.highlight = settings.get(self.module)
        
        if self.module == "notes" or self.module == "diaries":    
            if self.autosave == "enabled":
                self.autosave_checkbox.setText(_("Enabled"))
                self.autosave_checkbox.setChecked(True)
            elif self.autosave == "disabled":
                self.autosave_checkbox.setText(_("Disabled"))
                self.autosave_checkbox.setChecked(False)
        
            self.loadOnlyFormat()
        
        if self.module == "notes" or self.module == "todos":
            self.background_button.setText(_("Select color (selected: {})")
                                           .format(_("default") if self.background == "default" else self.background))
            
            self.foreground_button.setText(_("Select color (selected: {})")
                                           .format(_("default") if self.foreground == "default" else self.foreground))

        if self.module == "diaries":
            self.highlight_button.setText(_("Select color (selected: {})")
                                          .format(_("default") if self.highlight == "default" else self.highlight))
            
    def loadOnlyFormat(self) -> None:
        if self.module == "notes" or self.module == "diaries":  
            if self.format == "plain-text":
                self.format_combobox.setCurrentIndex(0)
                
            elif self.format == "markdown":
                self.format_combobox.setCurrentIndex(1)
                
            elif self.format == "html":
                self.format_combobox.setCurrentIndex(2)
        
    def reset(self) -> bool:
        if settings.reset(self.module):
            self.load()
                
            self.target.refreshSettings()
                
            return True
        
        else:
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
        ok, status, qcolor = ColorDialog(self, False, True,
            QColor(self.background if self.background != "default" else "#FFFFFFF"), 
            _("Select {} Color").format(_("Background"))).getColor()
        
        if ok:
            self.background = qcolor.name() if status == "new" else "default"
            
            self.background_button.setText(_("Select color (selected: {})")
                                           .format(_("default") if self.background == "default" else self.background))
          
    @Slot()  
    def setForeground(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, True,
            QColor(self.foreground if self.foreground != "default" else "#FFFFFF"), 
            _("Select {} Color").format(_("Text"))).getColor()
        
        if ok:
            self.foreground = qcolor.name() if status == "new" else "default"
            
            self.foreground_button.setText(_("Select color (selected: {})")
                                           .format(_("default") if self.foreground == "default" else self.foreground))
                
    @Slot(int)
    def setFormat(self, index: int) -> None:
        if self.do_not_check:
            self.do_not_check = False
        
        else:
            question = QMessageBox.question(
                self, _("Question"), _("If you have documents with the format setting set to global," +
                                       " this change may corrupt them.\nDo you really want to apply the new format setting?"))
            
            if question != QMessageBox.StandardButton.Yes:
                self.do_not_check = True
                
                self.loadOnlyFormat()
                
                self.do_not_check = False
                
                return
        
        if index == 0:
            self.format = "plain-text"
        elif index == 1:
            self.format = "markdown"
        elif index == 2:
            self.format = "html"
            
    @Slot()
    def setHighlight(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, True,
            QColor(self.highlight if self.highlight != "default" else "#376296"), 
            _("Select {} Color").format(_("Highlight"))).getColor()
        
        if ok:
            self.highlight = qcolor.name() if status == "new" else "#376296"
                    
            self.highlight_button.setText(_("Select color (selected: {})")
                                           .format(_("default") if self.highlight == "default" else self.highlight))