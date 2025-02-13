# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024-2025 MuKonqi (Muhammed S.)

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
from widgets.others import Combobox, HSeperator, Label, PushButton, VSeperator


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
    

class SettingsWidget(QWidget):
    def __init__(self, parent: QMainWindow, notes, todos, diaries) -> None:        
        super().__init__(parent)
        
        self.parent_ = parent
        self.layout_ = QGridLayout(self)
        
        self.menu = self.parent_.menuBar().addMenu(_("Settings"))
        
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
        
        appearance_scroll_area = QScrollArea(self)
        appearance_scroll_area.setWidgetResizable(True)
        appearance_scroll_area.setWidget(AppearanceSettings(self, 0))
        appearance_scroll_area.apply = appearance_scroll_area.widget().apply
        appearance_scroll_area.load = appearance_scroll_area.widget().load
        appearance_scroll_area.reset = appearance_scroll_area.widget().reset
        
        self.container = QStackedWidget(self)
        
        self.pages = [
            appearance_scroll_area,
            ModuleSettings(self, 1, "notes", notes),
            ModuleSettings(self, 2, "todos",  todos),
            ModuleSettings(self, 3, "diaries", diaries)
        ]
        
        for page in self.pages:
            self.container.addWidget(page)
            
        self.list.addItem(self.list_appearance)
        self.list.addItem(self.list_notes)
        self.list.addItem(self.list_todos)
        self.list.addItem(self.list_diaries)
        
        self.buttons = QDialogButtonBox(self)
        
        self.reset_button = PushButton(self.buttons, _("Reset"))
        self.reset_button.clicked.connect(self.reset)
        
        self.apply_button = PushButton(self.buttons, _("Apply"))
        self.apply_button.clicked.connect(self.apply)
        
        self.cancel_button = PushButton(self.buttons, _("Cancel"))
        self.cancel_button.clicked.connect(self.cancel)
        
        self.buttons.addButton(self.reset_button, QDialogButtonBox.ButtonRole.ResetRole)
        self.buttons.addButton(self.apply_button, QDialogButtonBox.ButtonRole.ApplyRole)
        self.buttons.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.list, 0, 0, 3, 1)
        self.layout_.addWidget(VSeperator(self), 0, 1, 3, 1)
        self.layout_.addWidget(self.container, 0, 2, 1, 1)
        self.layout_.addWidget(HSeperator(self), 1, 2, 1, 1)
        self.layout_.addWidget(self.buttons, 2, 2, 1, 1)
        
        self.list.setCurrentRow(0)
        self.list.currentRowChanged.connect(lambda: self.container.setCurrentIndex(self.list.currentRow()))
        
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
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to apply all new settings."))
    
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
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset all settings."))
            
            
class BaseSettings(QWidget):
    def __init__(self, parent: SettingsWidget, index: int) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.index = index
        
        self.parent_.menu.addAction(self.parent_.list.item(self.index).text(), self.openPage)
    
    @Slot()
    def openPage(self) -> None:
        self.parent_.parent_.tabwidget.tabbar.setCurrentIndex(4)
        self.parent_.list.setCurrentRow(self.index)
            

class AppearanceSettings(BaseSettings):
    def __init__(self, parent: SettingsWidget, index: int) -> None:
        super().__init__(parent, index)
        
        self.parent_ = parent
        
        self.default_style = QApplication.style().objectName().title()
        
        self.form = QFormLayout(self)
        
        self.alternate_row_colors_checkbox = QCheckBox(self)
        self.alternate_row_colors_checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        try:
            self.alternate_row_colors_checkbox.checkStateChanged.connect(self.alternateRowColorsChanged)
        except:
            self.alternate_row_colors_checkbox.stateChanged.connect(self.alternateRowColorsChanged)
        
        self.styles_combobox = QComboBox(self)
        self.styles_combobox.setEditable(False)
        
        self.color_schemes_widget = QWidget(self)
        self.color_schemes_widget_layout = QHBoxLayout(self.color_schemes_widget)
        self.color_schemes_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        self.color_schemes_buttons = QWidget(self.color_schemes_widget)
        self.color_schemes_buttons_layout = QHBoxLayout(self.color_schemes_buttons)
        self.color_schemes_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.color_schemes_combobox = Combobox(self.color_schemes_widget)
        self.color_schemes_combobox.setEditable(False)
        
        self.color_schemes_rename = PushButton(self.color_schemes_buttons, _("Rename"))
        self.color_schemes_rename.clicked.connect(self.renameColorScheme)

        self.color_schemes_delete = PushButton(self.color_schemes_buttons, _("Delete"))
        self.color_schemes_delete.clicked.connect(self.deleteColorScheme)
        
        self.color_schemes_import = PushButton(self.color_schemes_widget, _("Import"))
        self.color_schemes_import.clicked.connect(self.importColorScheme)
        
        self.custom_color_schemes = CustomColorSchemes(self)
        
        self.load()
        
        self.color_schemes_buttons.setLayout(self.color_schemes_buttons_layout)
        self.color_schemes_buttons_layout.addWidget(self.color_schemes_rename)
        self.color_schemes_buttons_layout.addWidget(self.color_schemes_delete)
        
        self.color_schemes_widget.setLayout(self.color_schemes_widget_layout)
        self.color_schemes_widget_layout.addWidget(self.color_schemes_combobox)
        self.color_schemes_widget_layout.addWidget(self.color_schemes_buttons)
        self.color_schemes_widget_layout.addWidget(VSeperator(self.color_schemes_widget))
        self.color_schemes_widget_layout.addWidget(self.color_schemes_import)
        
        self.setLayout(self.form)
        self.form.addRow("{}{}".format(_("Alternate row colors"), ":"), self.alternate_row_colors_checkbox)
        self.form.addRow("{}{}*".format(_("Style"), ":"), self.styles_combobox)
        self.form.addRow("{}{}".format(_("Color scheme"), ":"), self.color_schemes_widget)
        self.form.addRow("{} {}{}".format(_("Custom"), _("Color scheme").lower(), ":"), self.custom_color_schemes.name)
        self.form.addWidget(self.custom_color_schemes)
        self.form.addRow(HSeperator(self))
        self.form.addRow(Label(self, _("If PySide6 is installed with Pip, some system themes may not detected by Qt.*"), False))
        self.form.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        
        self.styles_combobox.currentTextChanged.connect(self.styleChanged)
        self.color_schemes_combobox.currentTextChanged.connect(self.colorSchemeChanged)
        
    @Slot(int or Qt.CheckState)
    def alternateRowColorsChanged(self, signal: Qt.CheckState | int) -> None:
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.alternate_row_colors = "disabled"
            self.alternate_row_colors_checkbox.setText(_("Disabled"))
        
        elif signal == Qt.CheckState.Checked or signal == 2:
            self.alternate_row_colors = "enabled"
            self.alternate_row_colors_checkbox.setText(_("Enabled"))
        
    def apply(self) -> bool:
        successful = True
        
        settings.setValue("appearance/alternate-row-colors", self.alternate_row_colors)
        
        if settings.value("appearance/alternate-row-colors") != self.alternate_row_colors:
            successful = False
            
        pages = [self.parent_.parent_.dock.widget().open_pages, self.parent_.parent_.dock.widget().history,
                self.parent_.parent_.home.notes, self.parent_.parent_.home.todos, 
                self.parent_.parent_.notes.home.treeview, self.parent_.parent_.todos.treeview]
        
        for page in pages:
            page.setAlternatingRowColors(True if self.alternate_row_colors == "enabled" else False)
        
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
            self.setColorSchemeButtons(value)
                
            self.current_color_scheme = value
            self.use_default_color_scheme = False
            self.custom_color_schemes.setEnabled(False)
    
    def setColorSchemeButtons(self, value: str) -> None:
        if value in self.user_color_schemes:
            self.color_schemes_buttons.setEnabled(True)
            
        else:
            self.color_schemes_buttons.setEnabled(False)
            
    @Slot()
    def deleteColorScheme(self) -> None:
        name = self.current_color_scheme
        
        if (name in self.user_color_schemes and 
            os.path.isfile(self.user_color_schemes[name])):
                os.remove(self.user_color_schemes[name])
                
                if settings.value("appearance/color-scheme") == name:
                    settings.setValue("appearance/color-scheme", "")
                
                self.color_schemes_list.remove(name)
                del self.color_schemes[name]
                del self.user_color_schemes[name]
                
                if self.applied_color_scheme == name:
                    self.color_schemes_combobox.setCurrentIndex(0)
                    self.loadPalette()
                
                self.color_schemes_combobox.addItems(self.color_schemes_list)
        
    def load(self) -> None:
        self.alternate_row_colors = settings.value("appearance/alternate-row-colors")
        
        if self.alternate_row_colors is None or self.alternate_row_colors == "":
            if self.alternate_row_colors is None:
                settings.setValue("appearance/alternate-row-colors", "disabled")
                
            self.alternate_row_colors = "disabled"
           
        if self.alternate_row_colors == "enabled": 
            self.alternate_row_colors_checkbox.setChecked(True)
            self.alternate_row_colors_checkbox.setText(_("Enabled"))
            
        elif self.alternate_row_colors == "disabled":
            self.alternate_row_colors_checkbox.setChecked(False)
            self.alternate_row_colors_checkbox.setText(_("Disabled"))
            
        self.styles_list = QStyleFactory.keys()
        self.styles_list.insert(0, _("System default ({})").format(self.default_style))
        
        self.styles_combobox.addItems(self.styles_list)
        
        self.current_style = settings.value("appearance/style")
        
        if self.current_style is None or self.current_style == "":
            if self.current_style is None:
                settings.setValue("appearance/style", "")
                
            self.current_style = self.default_style
            self.use_default_style = True
            
            self.styles_combobox.setCurrentIndex(0)
            
        else:
            QApplication.setStyle(self.current_style)
            
            self.use_default_style = False
            
            self.styles_combobox.setCurrentText(self.current_style)
        
        self.color_schemes = {}
        
        for entry in os.scandir(SYSTEM_COLOR_SCHEMES_DIR):
            if entry.is_file() and entry.name.endswith(".json"):
                with open(entry.path) as f:
                    data = json.load(f)
                    
                self.color_schemes[data["name"]] = data["colors"]
                
        self.user_color_schemes = {}
        
        for entry in os.scandir(USER_COLOR_SCHEMES_DIR):
            if entry.is_file() and entry.name.endswith(".json"):
                with open(entry.path) as f:
                    data = json.load(f)

                if data["name"] in self.color_schemes.copy().keys():
                    self.color_schemes["{} {}".format(data["name"], _("(System)"))] = self.color_schemes.pop(data["name"])
                    self.color_schemes["{} {}".format(data["name"], _("(User)"))] = data["colors"]
                    
                    self.user_color_schemes["{} {}".format(data["name"], _("(User)"))] = entry.path
                    
                else:
                    self.color_schemes[data["name"]] = data["colors"]
                    
                    self.user_color_schemes[data["name"]] = entry.path
        
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
            
        self.applied_color_scheme = self.current_color_scheme
        
        self.setColorSchemeButtons(self.current_color_scheme)
        
        self.loadOnlySomeTexts()
        self.loadPalette()
        
    def loadOnlySomeTexts(self) -> None:
        self.color_schemes_list[0] = _("From selected style ({})").format(self.current_style)
        self.color_schemes_combobox.setItemText(0, self.color_schemes_list[0])
        
    def loadPalette(self) -> None:
        if self.use_default_color_scheme:
            self.applied_color_scheme = ""
            
            palette = QApplication.style().standardPalette()
            
        else:
            self.applied_color_scheme = self.current_color_scheme
            
            palette = QPalette()
            
            for key in self.color_schemes[self.current_color_scheme].keys():
                palette.setColor(QPalette.ColorRole[key], self.color_schemes[self.current_color_scheme][key])
            
        QApplication.setPalette(palette)
        
    @Slot()
    def importColorScheme(self) -> None:
        paths = QFileDialog.getOpenFileNames(self,
                                            _("Import a {the_item}").format(the_item = _("Color scheme")).title(),
                                            "",
                                            _("Color schemes (*.json)"))[0]
        
        for path in paths:
            if path.endswith(".json"):
                with open(path) as f:
                    data = json.load(f)
                    
                name = data["name"]
                
                if name is not None and name != "" and data["colors"] != {}:
                    with open(os.path.join(USER_COLOR_SCHEMES_DIR, f"{name}.json"), "w") as f:
                        json.dump(data, f)
                        
                    self.color_schemes[name] = data["colors"]
                        
                self.user_color_schemes[name] = os.path.join(USER_COLOR_SCHEMES_DIR, f"{name}.json")
                
                self.color_schemes_list.insert(len(self.color_schemes_list) - 1, name)
                
                self.color_schemes_combobox.addItems(self.color_schemes_list)
                
    @Slot()
    def renameColorScheme(self) -> None:
        name = self.current_color_scheme
        
        newname, topwindow = QInputDialog.getText(self,
                                                _("Rename {the_item}").format(the_item = _("the {name} color scheme").format(name = name)).title(), 
                                                _("Please enter a new name for {the_item}.").format(the_item = _("the {name} color scheme").format(name = name)))
        
        if topwindow and newname != "":
            if not os.path.exists(os.path.join(USER_COLOR_SCHEMES_DIR, f"{newname}.json")):
                os.rename(os.path.join(USER_COLOR_SCHEMES_DIR, f"{name}.json"), os.path.join(USER_COLOR_SCHEMES_DIR, f"{newname}.json"))
                
                with open(os.path.join(USER_COLOR_SCHEMES_DIR, f"{newname}.json")) as f:
                    data = json.load(f)
                    
                data["name"] = newname
                
                with open(os.path.join(USER_COLOR_SCHEMES_DIR, f"{newname}.json"), "w") as f:
                    json.dump(data, f)
                    
                if settings.value("appearance/color-scheme") == name:
                    settings.setValue("appearance/color-scheme", newname)
                
                self.color_schemes[newname] = self.color_schemes.pop(name)
                
                self.user_color_schemes[newname] = self.user_color_schemes.pop(name)
                self.user_color_schemes[newname] = os.path.join(USER_COLOR_SCHEMES_DIR, f"{newname}.json")
                
                self.color_schemes_list[self.color_schemes_list.index(name)] = newname
                
                self.color_schemes_combobox.addItems(self.color_schemes_list)
                self.color_schemes_combobox.setCurrentText(newname)
                
            else:
                QMessageBox.critical(self, _("Error"), _("Already existing {newitem}, renaming {the_item} cancalled.")
                                    .format(newitem = newname, the_item = _("the {name} color scheme").format(name = name)))
        
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
                       "AlternateBase": _("Alternate base"),
                       "ToolTipBase": _("Tooltip base"),
                       "ToolTipText": _("Tooltip text"),
                       "PlaceholderText": _("Placeholder text"),
                       "Text": _("Text"),
                       "Button": _("Button"),
                       "ButtonText": _("Button text"),
                       "BrightText": _("Bright text"),
                       "Light": _("Light"),
                       "Midlight": _("Mid light"),
                       "Dark": _("Dark"),
                       "Mid": _("Mid"),
                       "Shadow": _("Shadow"),
                       "Highlight": _("Highlight"),
                       "Accent": _("Accent"),
                       "HighlightedText": _("Highlighted text"),
                       "Link": _("Link"),
                       "LinkVisited": _("Visited link")}
        
        self.buttons = {}
        
        self.values = {}
        
        number = 0
        
        for color_role in self.labels.keys():
            number += 1
                        
            self.values[color_role] = ""
            
            self.buttons[color_role] = PushButton(self, _("Select color (selected: {})").format(_("none")))
            self.buttons[color_role].clicked.connect(lambda state, color_role = color_role: self.setColorRoleValue(False, color_role))
            
            if number == 1:
                self.form.addRow(Label(self, _("Central")))
                
            elif number == 12:
                self.form.addRow(Label(self, _("3D Bevel and Shadow Effects")))
                
            elif number == 17:
                self.form.addRow(Label(self, _("Selected (Marked) Items")))
                
            elif number == 20:
                self.form.addRow(Label(self, _("Links")))
                
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
            
            with open(os.path.join(USER_COLOR_SCHEMES_DIR, f"{name}.json"), "w") as f:
                json.dump(data, f)
                
            with open(os.path.join(USER_COLOR_SCHEMES_DIR, f"{name}.json")) as f:
                check_data = json.load(f)
                
            if data == check_data:
                self.parent_.color_schemes[name] = color_scheme
                self.parent_.user_color_schemes[name] = os.path.join(USER_COLOR_SCHEMES_DIR, f"{name}.json")
                self.parent_.color_schemes_list.insert(len(self.parent_.color_schemes_list) - 1, name)
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

        
class ModuleSettings(BaseSettings):
    def __init__(self, parent: SettingsWidget, index: int, module: str, target) -> None:
        super().__init__(parent, index)
        
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