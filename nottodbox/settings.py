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


import os
import configparser
import json
from gettext import gettext as _
from PySide6.QtCore import Slot, Qt, QSettings, QStandardPaths
from PySide6.QtGui import QColor, QPalette, QPixmap, QFontDatabase, QIcon
from PySide6.QtWidgets import *
from widgets.dialogs import ColorDialog
from widgets.others import Combobox, HSeperator, Label, PushButton, VSeperator
from consts import APP_MODE, APP_VERSION, DESKTOP_FILE_FOUND, DESKTOP_FILE, ICON_FILE, USER_NAME, USER_DESKTOP_FILE, USER_DESKTOP_FILE_FOUND, SYSTEM_DESKTOP_FILE_FOUND


COLOR_SCHEMES_DIRS = []

KDE_COLOR_SCHEMES_DIRS = QStandardPaths.locateAll(
    QStandardPaths.StandardLocation.GenericDataLocation, 
    "color-schemes", 
    QStandardPaths.LocateOption.LocateDirectory)
KDE_COLOR_SCHEMES_DIRS.reverse()

KDE_COLOR_SCHEMES_FOUND = True
KDE_SYSTEM_COLOR_SCHEMES_FOUND = True
KDE_USER_COLOR_SCHEMES_FOUND = True

if KDE_COLOR_SCHEMES_DIRS == []:
    KDE_COLOR_SCHEMES_FOUND = False
    
elif len(KDE_COLOR_SCHEMES_DIRS) == 1:
    if KDE_COLOR_SCHEMES_DIRS[0] == "/usr/share/color-schemes":
        KDE_USER_COLOR_SCHEMES_FOUND = False
    
    elif KDE_COLOR_SCHEMES_DIRS[0] == f"/home/{USER_NAME}/.local/share/color-schemes":
        KDE_SYSTEM_COLOR_SCHEMES_FOUND = False

NOTTODBOX_COLOR_SCHEMES_DIRS = ["@COLOR-SCHEMES_DIR@" if os.path.isdir("@COLOR-SCHEMES_DIR@") else f"{os.path.dirname(__file__)}/color-schemes", 
                                f"/home/{USER_NAME}/.local/share/nottodbox/color-schemes"]
os.makedirs(NOTTODBOX_COLOR_SCHEMES_DIRS[1], exist_ok=True)

COLOR_SCHEMES_DIRS.extend(KDE_COLOR_SCHEMES_DIRS)
COLOR_SCHEMES_DIRS.extend(NOTTODBOX_COLOR_SCHEMES_DIRS)


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
            
            for module in ["sidebar", "notes", "todos", "diaries"]:
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
    
    def reset(self, module_: str | None = None, format_change_acceptted: bool = True) -> bool:
        if module_ is None:
            successful = True
            
            for module in ["sidebar", "notes", "todos", "diaries"]:
                if not self.resetBase(module, format_change_acceptted):
                    successful = False
                
            return successful
        
        else:
            return self.resetBase(module_, format_change_acceptted)
        
    def resetBase(self, module: str, format_change_acceptted: bool = True) -> bool:
        if module == "sidebar":
            return self.set(module, "disabled", "", "", "", "", "")
        
        elif module == "notes":
            return self.set(module, "disabled", "enabled", "default", "default", 
                            "markdown" if format_change_acceptted else self.getBase(module)[4], "")
        
        elif module == "todos":
            return self.set(module, "disabled", "", "default", "default", "", "")
        
        elif module == "diaries":
            return self.set(module, "", "enabled", "", "", 
                            "markdown" if format_change_acceptted else self.getBase(module)[4], "#376296")
    
    def set(self, module: str, alternate_row_colors: str, autosave: str, background: str, foreground: str, format: str, highlight: str) -> bool:
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
    def __init__(self, parent: QMainWindow, sidebar, notes, todos, diaries) -> None:        
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.menu = self.parent_.menuBar().addMenu(_("Settings"))
        
        self.last_index = 0
        
        self.selector = QListWidget(self)
        self.selector.setFixedWidth(100)
        
        self.container = QStackedWidget(self)
        
        self.pages = [
            (QListWidgetItem(_("Appearance")), self.makeScrollable(AppearanceSettings(self, 0))),
            (QListWidgetItem(_("Sidebar")), self.makeScrollable(ModuleSettings(self, 1, "sidebar", sidebar))),
            (QListWidgetItem(_("Shortcuts")), self.makeScrollable(ShortcutsSettings(self, 2))),
            (QListWidgetItem(_("Notes")), self.makeScrollable(ModuleSettings(self, 3, "notes", notes))),
            (QListWidgetItem(_("To-dos")), self.makeScrollable(ModuleSettings(self, 4, "todos",  todos))),
            (QListWidgetItem(_("Diaries")), self.makeScrollable(ModuleSettings(self, 5, "diaries", diaries)))
        ]
            
        for text, page in self.pages:
            self.menu.addAction(text.text(), page.openPage)
            
            text.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.selector.addItem(text)
            self.container.addWidget(page)
            
        self.container.addWidget(self.makeScrollable(AboutWidget(self)))
            
        self.selector.setCurrentRow(0)
        self.selector.currentRowChanged.connect(self.setCurrentPage)
        
        self.about_button = PushButton(self, _("About"), QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.about_button.setFlat(True)
        self.about_button.setCheckable(True)
        self.about_button.clicked.connect(self.aboutPage)
        
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
        
        self.layout_ = QGridLayout(self)
        self.layout_.addWidget(self.selector, 0, 0, 1, 1)
        self.layout_.addWidget(HSeperator(self), 1, 0, 1, 1)
        self.layout_.addWidget(self.about_button, 2, 0, 1, 1)
        self.layout_.addWidget(VSeperator(self), 0, 1, 3, 1)
        self.layout_.addWidget(self.container, 0, 2, 1, 1)
        self.layout_.addWidget(HSeperator(self), 1, 2, 1, 1)
        self.layout_.addWidget(self.buttons, 2, 2, 1, 1)
        
    @Slot(bool)
    def aboutPage(self, check: bool) -> None:
        if self.container.currentIndex() != self.container.count() - 1:
            self.last_index = self.container.currentIndex()
        
        self.container.setCurrentIndex(self.container.count() - 1 if check else self.last_index)
        
    @Slot()
    def apply(self) -> None:
        successful = True
        do_not_asked_before = True
        format_change_acceptted = True
        
        for text, page in self.pages:
            if (type(page.widget()).__name__ == "ModuleSettings" and 
                (page.widget().module == "notes" or page.widget().module == "diaries") and
                page.widget().format != page.widget().format_ and
                do_not_asked_before):
                do_not_asked_before = False
                format_change_acceptted = True
                
                question = QMessageBox.question(
                    self, _("Question"), _("If you have documents with the format setting set to global," +
                                        " this change may corrupt them.\nDo you really want to apply the format setting(s)?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    format_change_acceptted = False
                          
            if not page.apply(format_change_acceptted):
                successful = False
        
        if successful:
            if format_change_acceptted:
                QMessageBox.information(self, _("Successful"), _("All settings applied."))
            
            else:
                QMessageBox.information(self, _("Successful"), _("All settings applied EXCEPT format settings."))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to apply all settings."))
    
    @Slot()
    def cancel(self) -> None:
        for text, page in self.pages:
            page.load()
            
    def makeScrollable(self, page: QWidget) -> QScrollArea:
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(page)
        
        scroll_area.openPage = page.openPage
        
        if type(page).__name__ != "AboutWidget":
            scroll_area.apply = page.apply
            scroll_area.load = page.load
            scroll_area.reset = page.reset
        
        return scroll_area
    
    @Slot()
    def reset(self) -> None:
        successful = True
        do_not_asked_before = True
        format_change_acceptted = True
        
        for text, page in self.pages:
            if (type(page.widget()).__name__ == "ModuleSettings" and 
                (page.widget().module == "notes" or page.widget().module == "diaries") and
                settings.getBase(page.widget().module)[4] != "markdown" and
                do_not_asked_before):
                do_not_asked_before = False
                format_change_acceptted = True
                
                question = QMessageBox.question(
                    self, _("Question"), _("If you have documents with the format setting set to global," +
                                        " this change may corrupt them.\nDo you really want to apply the format setting(s)?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    format_change_acceptted = False
                          
            if not page.reset(format_change_acceptted):
                successful = False
        
        if successful:
            if format_change_acceptted:
                QMessageBox.information(self, _("Successful"), _("All setting reset."))
            
            else:
                QMessageBox.information(self, _("Successful"), _("All settings reset EXCEPT format settings."))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to reset all settings."))
            
    @Slot(int)
    def setCurrentPage(self, index: int) -> None:
        self.container.setCurrentIndex(index)
        self.about_button.setChecked(False)
            
            
class BaseSettings(QWidget):
    def __init__(self, parent: SettingsWidget, index: int) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.index = index
        
        self.form = QFormLayout(self)
    
    @Slot()
    def openPage(self) -> None:
        self.parent_.parent_.tabwidget.setCurrentPage(self.parent_)
        self.parent_.selector.setCurrentRow(self.index)
        

class AboutWidget(QWidget):
    def __init__(self, parent: SettingsWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.parent_.menu.addAction(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout), _("About"), self.openPage)
        
        self.icon_and_nottodbox = QWidget()
        
        self.icon = Label(self.icon_and_nottodbox)
        self.icon.setPixmap(self.windowIcon().pixmap(96, 96))
        
        self.nottodbox = Label(self.icon_and_nottodbox, _("Nottodbox"))
        font = self.nottodbox.font()
        font.setBold(True)
        font.setPointSize(32)
        self.nottodbox.setFont(font)
        
        self.version_label = Label(self, _("Version") + f': <a href="https://github.com/mukonqi/nottodbox/releases/tag/{APP_VERSION}">{APP_VERSION}</a>')
        self.version_label.setOpenExternalLinks(True)
        
        self.source_label = Label(self, _("Source codes") + ': <a href="https://github.com/mukonqi/nottodbox">GitHub</a>')
        self.source_label.setOpenExternalLinks(True)
        
        self.developer_label = Label(self, _("Developer") + ': <a href="https://mukonqi.github.io">MuKonqi (Muhammed S.)</a>')
        self.developer_label.setOpenExternalLinks(True)
        
        self.copyright_label = Label(self, _("Copyright (C)") + f': 2024-2025 MuKonqi (Muhammed S.)')
        
        self.license_label = Label(self, _("License: GNU General Public License, Version 3 or later"))
        
        with open("@APP_DIR@/LICENSE.txt" if os.path.isfile("@APP_DIR@/LICENSE.txt") else 
                    f"{os.path.dirname(__file__)}/LICENSE.txt" if os.path.isfile(f"{os.path.dirname(__file__)}/LICENSE.txt") else
                    f"{os.path.dirname(os.path.dirname(__file__))}/LICENSE.txt") as license_file:
            license_text = license_file.read()
            
        self.license_textedit = QTextEdit(self)
        self.license_textedit.setFixedWidth(79 * 8 * QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).pointSize() / 10 + 
                                            QApplication.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarSliderMin) + 10)
        self.license_textedit.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.license_textedit.setText(license_text)
        self.license_textedit.setReadOnly(True)
        
        self.icon_and_nottodbox_layout = QHBoxLayout(self.icon_and_nottodbox)
        self.icon_and_nottodbox_layout.setSpacing(6)
        self.icon_and_nottodbox_layout.addStretch()
        self.icon_and_nottodbox_layout.addWidget(self.icon)
        self.icon_and_nottodbox_layout.addWidget(self.nottodbox)
        self.icon_and_nottodbox_layout.addStretch()
        
        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(self.icon_and_nottodbox)
        self.layout_.addWidget(self.version_label)
        self.layout_.addWidget(self.source_label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.developer_label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.copyright_label)
        self.layout_.addWidget(self.license_label)
        self.layout_.addWidget(self.license_textedit, 0, Qt.AlignmentFlag.AlignCenter)
        
    @Slot()
    def openPage(self) -> None:
        self.parent_.parent_.tabwidget.setCurrentPage(self.parent_)
        self.parent_.about_button.setChecked(True if not self.parent_.about_button.isChecked() else False)
        self.parent_.aboutPage(self.parent_.about_button.isChecked())
        

class AppearanceSettings(BaseSettings):
    def __init__(self, parent: SettingsWidget, index: int) -> None:
        super().__init__(parent, index)
        
        self.default_style = QApplication.style().objectName().title()
        
        self.styles_combobox = QComboBox(self)
        self.styles_combobox.setEditable(False)
        
        self.color_schemes_widget = QWidget(self)
        
        self.color_schemes_buttons = QWidget(self.color_schemes_widget)
        
        self.color_schemes_combobox = Combobox(self.color_schemes_widget)
        self.color_schemes_combobox.setEditable(False)
        
        self.color_schemes_rename = PushButton(self.color_schemes_widget, _("Rename"),
                                               QIcon.fromTheme(QIcon.ThemeIcon.InsertText))
        self.color_schemes_rename.clicked.connect(self.renameColorScheme)

        self.color_schemes_delete = PushButton(self.color_schemes_widget, _("Delete"),
                                               QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.color_schemes_delete.clicked.connect(self.deleteColorScheme,)
        
        self.color_schemes_import = PushButton(self.color_schemes_widget, _("Import"),
                                               QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.color_schemes_import.clicked.connect(self.importColorScheme)
        
        self.load()
        
        self.custom_color_schemes = CustomColorSchemes(self)
        
        self.color_schemes_widget_layout = QHBoxLayout(self.color_schemes_widget)
        self.color_schemes_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.color_schemes_widget_layout.addWidget(self.color_schemes_combobox)
        self.color_schemes_widget_layout.addWidget(self.color_schemes_rename)
        self.color_schemes_widget_layout.addWidget(self.color_schemes_delete)
        self.color_schemes_widget_layout.addWidget(VSeperator(self.color_schemes_widget))
        self.color_schemes_widget_layout.addWidget(self.color_schemes_import)
        
        self.form.addRow(Label(self, _("Style")))
        self.form.addRow("{}*:".format(_("Style")), self.styles_combobox)
        self.form.addRow(Label(self, _("Color scheme").title()))
        self.form.addRow("{}:".format(_("Color scheme")), self.color_schemes_widget)
        self.form.addRow("{} {}:".format(_("Custom"), _("Color scheme").lower()), self.custom_color_schemes.name)
        self.form.addWidget(self.custom_color_schemes)
        self.form.addRow(HSeperator(self))
        self.form.addRow(Label(self, "*{}<ul>- {}<br>- {}</ul>".format(_("Some styles may not be detected in two cases:"),
                                                                 _("If PySide6 is installed with Pip"), 
                                                                 _("If you are using the AppImage version of Nottodbox")), 0x0001))
        self.form.addRow(Label(self, 
                               "<br>{}{}".format(self.superscriptDirNumber(1), _('From the system directory for KDE-format color schemes')), 0x0001))
        self.form.addRow(Label(self, 
                               "<br>{}{}".format(self.superscriptDirNumber(2), _('From the user directory for KDE-format color schemes')), 0x0001))
        self.form.addRow(Label(self, 
                               "<br>{}{}".format(self.superscriptDirNumber(3), _('From the system directory for Nottodbox-format color schemes')), 0x0001))
        self.form.addRow(Label(self, 
                               "<br>{}{}".format(self.superscriptDirNumber(4), _('From the user directory for Nottodbox-format color schemes')), 0x0001))
        
        self.styles_combobox.currentTextChanged.connect(self.styleChanged)
        self.color_schemes_combobox.currentTextChanged.connect(self.colorSchemeChanged)
        
    def apply(self, format_change_acceptted: bool = True) -> bool:
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
            settings.setValue("appearance/color_scheme", "")
            
            if settings.value("appearance/color_scheme") != "":
                successful = False
            
        else:
            settings.setValue("appearance/color_scheme", self.current_color_scheme)
            
            if settings.value("appearance/color_scheme") != self.current_color_scheme:
                successful = False
                
        self.loadPalette()
                
        return successful
    
    @Slot(str)
    def colorSchemeChanged(self, value: str) -> None:
        if value == _("Style default"):
            self.current_color_scheme = ""
            self.use_default_color_scheme = True
            self.custom_color_schemes.setEnabled(False)
        
        elif value == _("Custom"):
            self.custom_color_schemes.setEnabled(True)
            
        else: 
            self.current_color_scheme = value
            self.use_default_color_scheme = False
            self.custom_color_schemes.setEnabled(False)
            
            self.setColorSchemeButtons(value)
            
    def convertToHexColor(self, color_str: str) -> str:
        color_rgb = [int(color) for color in color_str.split(",")]
        
        return QColor(color_rgb[0], color_rgb[1], color_rgb[2]).name()
    
    def convertColorScheme(self, config: configparser.ConfigParser) -> dict:        
        data = {}
        
        data["Window"] = self.convertToHexColor(config["Colors:Window"]["BackgroundNormal"])
        data["WindowText"] = self.convertToHexColor(config["Colors:Window"]["ForegroundNormal"])
        data["Base"] = self.convertToHexColor(config["Colors:View"]["BackgroundNormal"])
        data["AlternateBase"] = self.convertToHexColor(config["Colors:View"]["BackgroundAlternate"])
        data["ToolTipBase"] = self.convertToHexColor(config["Colors:Tooltip"]["BackgroundNormal"])
        data["ToolTipText"] = self.convertToHexColor(config["Colors:Tooltip"]["ForegroundNormal"])
        data["PlaceholderText"] = self.convertToHexColor(config["Colors:View"]["ForegroundInactive"])
        data["Text"] = self.convertToHexColor(config["Colors:View"]["ForegroundNormal"])
        data["Button"] = self.convertToHexColor(config["Colors:Button"]["BackgroundNormal"])
        data["ButtonText"] = self.convertToHexColor(config["Colors:Button"]["ForegroundNormal"])
        data["Highlight"] = self.convertToHexColor(config["Colors:Selection"]["BackgroundNormal"])
        data["Accent"] =self.convertToHexColor( config["Colors:Selection"]["ForegroundNormal"])
        data["HighlightedText"] = self.convertToHexColor(config["Colors:Selection"]["ForegroundNormal"])
        data["Link"] = self.convertToHexColor(config["Colors:View"]["ForegroundLink"])
        data["LinkVisited"] = self.convertToHexColor(config["Colors:View"]["ForegroundVisited"])
        
        return data
            
    @Slot()
    def deleteColorScheme(self) -> None:
        name = self.current_color_scheme
        
        if os.path.isfile(self.color_schemes[name]) and os.path.dirname(self.color_schemes[name]) == NOTTODBOX_COLOR_SCHEMES_DIRS[1]:
            os.remove(self.color_schemes[name])
            
            if settings.value("appearance/color_scheme") == name:
                settings.setValue("appearance/color_scheme", "")
            
            self.color_schemes_list.remove(name)
            del self.color_schemes[name]
            
            if self.applied_color_scheme == name:
                self.color_schemes_combobox.setCurrentIndex(0)
                self.loadPalette()
            
            self.color_schemes_combobox.addItems(self.color_schemes_list)
            self.custom_color_schemes.createList()
            
    def getColorSchemeName(self, path: str, check: bool = False) -> tuple[str, bool]:
        with open(path) as f:
            if path.endswith(".colors"):
                config = configparser.ConfigParser()
                config.read_file(f)
                
                name = config["General"]["Name"]
                
            elif path.endswith(".json"):
                
                name = json.load(f)["name"]
                
        overwrited = False
                
        pretty_name = f"{name}{self.superscriptDirNumber(path if not check else 4)}"
        
        if check and pretty_name in self.color_schemes_list:
            question = QMessageBox.question(self, 
                                            _("Question"),
                                            _("A color scheme with the name '{name}' already exists.\nDo you want to overwrite it?")
                                            .format(name = pretty_name))
            
            if question != QMessageBox.StandardButton.Yes:
                return "", False
            
            else:
                overwrited = True
                
        if not check:
            self.color_schemes[pretty_name] = path
                
        return name, overwrited
    
    def getColorSchemeData(self, path: str) -> dict:
        with open(path) as f:
            if path.endswith(".colors"):
                config = configparser.ConfigParser()
                config.read_file(f)
                
                return self.convertColorScheme(config)
            
            elif path.endswith(".json"):
                return json.load(f)["colors"]
        
    def load(self) -> None:    
        self.styles_list = QStyleFactory.keys()
        self.styles_list.insert(0, "{} ({})".format(_("System default"), self.default_style))
        
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
        
        for dir in COLOR_SCHEMES_DIRS:
            for entry in os.scandir(dir):
                if entry.is_file():
                    self.getColorSchemeName(entry.path)
        
        self.color_schemes_list = list(self.color_schemes.keys())
        self.color_schemes_list.insert(0, _("Style default"))
        self.color_schemes_list.append(_("Custom"))
        
        self.color_schemes_combobox.addItems(self.color_schemes_list)
        
        self.current_color_scheme = settings.value("appearance/color_scheme")
        
        if self.current_color_scheme in self.color_schemes.keys():
            self.use_default_color_scheme = False
            
            self.color_schemes_combobox.setCurrentText(self.current_color_scheme)
        
        else:
            if self.current_color_scheme is None:
                settings.setValue("appearance/color_scheme", "")

            self.current_color_scheme = ""

            self.use_default_color_scheme = True
            
            self.color_schemes_combobox.setCurrentIndex(0)
            
        self.applied_color_scheme = self.current_color_scheme
        
        self.setColorSchemeButtons(self.current_color_scheme)
        
        self.loadOnlySomeTexts()
        self.loadPalette()
        
    def loadOnlySomeTexts(self) -> None:
        self.color_schemes_list[0] = _("Style default")
        self.color_schemes_combobox.setItemText(0, self.color_schemes_list[0])
        
    def loadPalette(self) -> None:
        if self.use_default_color_scheme:
            self.applied_color_scheme = ""
            
            palette = QApplication.style().standardPalette()
            
        else:
            self.applied_color_scheme = self.current_color_scheme
            
            data = self.getColorSchemeData(self.color_schemes[self.current_color_scheme])
                    
            palette = QPalette()
            
            for color_role in data:
                palette.setColor(QPalette.ColorRole[color_role], data[color_role])
            
        QApplication.setPalette(palette)
        
    @Slot()
    def importColorScheme(self) -> None:
        paths = QFileDialog.getOpenFileNames(self,
                                            _("Import a {the_item}").format(the_item = _("Color scheme")).title(),
                                            "",
                                            _("Color schemes (*.colors *.json)"))[0]
        
        for path in paths:
            data = {}
        
            data["name"], overwrited = self.getColorSchemeName(path, True)
            data["colors"] = self.getColorSchemeData(path)
            
            pretty_name = f"{data['name']}{self.superscriptDirNumber(4)}"
                
            if data["name"] != "" and data["colors"] != {}:
                with open(os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{data['name']}.json"), "w") as f:
                    json.dump(data, f)
                    
                self.color_schemes[pretty_name] = os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{data['name']}.json")
                
                if not overwrited:
                    self.color_schemes_list.insert(len(self.color_schemes_list) - 1, pretty_name)
                
                self.color_schemes_combobox.addItems(self.color_schemes_list)
                
                self.custom_color_schemes.createList()
                
    @Slot()
    def renameColorScheme(self) -> None:
        name = self.current_color_scheme
        path = self.color_schemes[name]
        
        newname, topwindow = QInputDialog.getText(self,
                                                _("Rename {the_item}").format(the_item = _("the {name} color scheme").format(name = name)).title(), 
                                                _("Please enter a new name for {item}.").format(item = _("{name} color scheme").format(name = name)))
        
        if topwindow and newname != "":            
            if (not os.path.exists(os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{newname}.json")) and
                os.path.dirname(path) == NOTTODBOX_COLOR_SCHEMES_DIRS[1] and
                os.path.isfile(path)):
                
                with open(path) as f:
                    data = json.load(f)
                    
                data["name"] = newname
                
                if name in os.path.basename(self.color_schemes[name]):
                    path = os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{newname}.json")
                    
                    os.rename(path, os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{newname}.json"))
                
                with open(path, "w") as f:
                    json.dump(data, f)
                    
                if settings.value("appearance/color_scheme") == name:
                    settings.setValue("appearance/color_scheme", newname)
                
                self.color_schemes[f"{newname}{self.superscriptDirNumber(4)}"] = path
                
                self.color_schemes_list[self.color_schemes_list.index(name)] = f"{newname}{self.superscriptDirNumber(4)}"
                
                self.color_schemes_combobox.addItems(self.color_schemes_list)
                self.color_schemes_combobox.setCurrentText(f"{newname}{self.superscriptDirNumber(4)}")
                
                self.custom_color_schemes.createList()
                
            else:
                QMessageBox.critical(self, _("Error"), _("{item} color scheme can not be renamed.")
                                     .format(item = _("{name} color scheme").format(name = name)))
        
    def reset(self, format_change_acceptted: bool = True) -> bool:
        settings.remove("appearance/style")
        settings.remove("appearance/color_scheme")
        
        if settings.value("appearance/style") is None and settings.value("appearance/color_scheme") is None:
            self.load()
            
            return self.apply()
        
        else:
            return False
        
    def setColorSchemeButtons(self, value: str) -> None:
        if self.current_color_scheme != "" and os.path.dirname(self.color_schemes[value]) == NOTTODBOX_COLOR_SCHEMES_DIRS[1]:
            self.color_schemes_rename.setEnabled(True)
            self.color_schemes_delete.setEnabled(True)
            
        else:
            self.color_schemes_rename.setEnabled(False)
            self.color_schemes_delete.setEnabled(False)
        
    @Slot(str)
    def styleChanged(self, value: str) -> None:
        if value == "{} ({})".format(_("System default"), self.default_style):
            self.current_style = self.default_style
            self.use_default_style = True
        
        else:
            self.current_style = value
            self.use_default_style = False
            
        self.loadOnlySomeTexts()

    def superscriptDirNumber(self, value: str | int) -> str:
        if type(value) == int:
            number = value
            
        else:
            if not KDE_COLOR_SCHEMES_FOUND:
                dir_number = 2
                
            elif not KDE_SYSTEM_COLOR_SCHEMES_FOUND:
                dir_number = 1
                
            else:
                dir_number = 0
            
            for dir in COLOR_SCHEMES_DIRS:
                dir_number += 1
                
                if os.path.dirname(value) == dir or dir_number == 4:
                    number = dir_number
                    
                    break
                
                if dir_number == 1 and not KDE_USER_COLOR_SCHEMES_FOUND:
                    dir_number += 1
            
        if number == 1:
            return "\u00b9"
        
        elif number == 2:
            return "\u00b2"
        
        elif number == 3:
            return "\u00b3"
        
        elif number == 4:
            return "\u2074"
        
        else:
            return number
    
    
class CustomColorSchemes(QWidget):
    def __init__(self, parent: AppearanceSettings) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.name = QLineEdit(self.parent_)
        self.name.setClearButtonEnabled(True)
        self.name.setPlaceholderText(f"Color scheme by {USER_NAME}")
        
        self.combobox = Combobox(self)
        
        self.createList()
        
        self.combobox.currentTextChanged.connect(self.baseColorSchemeChanged)
               
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
        
        self.form = QFormLayout(self)
        self.form.addRow("{}:".format(_("Color scheme to be edited")), self.combobox)
        
        for color_role in self.labels.keys():
            number += 1
                        
            self.values[color_role] = ""
            
            self.buttons[color_role] = ColorSelectionWidget(self, color_role, self.labels, self.values)
            
            if number == 1:
                self.form.addRow(Label(self, _("General")))
                
            elif number == 12:
                self.form.addRow(Label(self, _("3D Bevel and Shadow Effects")))
                
            elif number == 17:
                self.form.addRow(Label(self, _("Selected (Marked) Items")))
                
            elif number == 20:
                self.form.addRow(Label(self, _("Links")))
                
            self.form.addRow(f"{self.labels[color_role]}:", self.buttons[color_role])
        
        self.setEnabled(False)
        
    def apply(self, format_change_acceptted: bool = True) -> bool:
        if self.parent_.color_schemes_combobox.currentText() == _("Custom"):
            overwrited = False
            
            name = self.name.text()
            
            if name == "":
                name = self.name.placeholderText()
            
            pretty_name = f"{name}{self.parent_.superscriptDirNumber(4)}"
            
            if pretty_name in self.parent_.color_schemes_list:
                question = QMessageBox.question(self, 
                                                _("Question"),
                                                _("A color scheme with the name '{name}' already exists.\nDo you want to overwrite it?")
                                                .format(name = pretty_name))
                
                if question == QMessageBox.StandardButton.Yes:
                    overwrited = True
                    
                else:
                    return False
            
            data = {"name": name}
            
            color_scheme = {}
            
            for color_role in self.labels.keys():
                if self.values[color_role] != "":
                    color_scheme[color_role] = self.values[color_role]
                
            data["colors"] = color_scheme
            
            with open(os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{name}.json"), "w") as f:
                json.dump(data, f)
                
            with open(os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{name}.json")) as f:
                check_data = json.load(f)
                
            if data == check_data:
                self.parent_.color_schemes[pretty_name] = os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{name}.json")
                
                if not overwrited:
                    self.parent_.color_schemes_list.insert(len(self.parent_.color_schemes_list) - 1, pretty_name)
                
                self.parent_.color_schemes_combobox.addItems(self.parent_.color_schemes_list)
                self.parent_.color_schemes_combobox.setCurrentText(pretty_name)
                
                self.createList()
                
                return True
            
            else:
                return False
        
        else:
            return True
        
    @Slot(str)
    def baseColorSchemeChanged(self, name: str) -> None:
        if name == _("none").title():
            for color_role in self.labels.keys():
                self.buttons[color_role].setColor("")
        
        elif name in self.color_schemes_list:
            data = self.parent_.getColorSchemeData(self.parent_.color_schemes[name])
            
            for color_role in self.labels.keys():
                self.buttons[color_role].setColor(data[color_role] if color_role in data else "")
                
    def createList(self) -> None:
        self.color_schemes_list = self.parent_.color_schemes_list.copy()
        self.color_schemes_list[0] = _("none").title()
        self.color_schemes_list.pop(-1)
        
        self.combobox.addItems(self.color_schemes_list)
    
    @Slot(bool)
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.name.setEnabled(enabled)
        self.combobox.setEnabled(enabled)
                

class ColorSelectionWidget(QWidget):
    def __init__(self, parent: QWidget, color_role: QPalette.ColorRole, labels: dict, values: dict) -> None:
        super().__init__(parent)
        
        self.color_role = color_role
        self.labels = labels
        self.values = values
        
        self.selector = PushButton(self, _("Select color (selected: {})").format(_("none")))
        self.selector.clicked.connect(self.chooseColor)
        
        self.label = Label(self)
        
        self.viewer = QPixmap(self.selector.height(), self.selector.height())

        self.layout_ = QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.addWidget(self.selector)
        self.layout_.addWidget(self.label)
        
    @Slot()
    def chooseColor(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, True, 
                                         QColor(self.values[self.color_role] if self.color_role in self.values else "#000000"), 
                                         _("Select {} Color").format(self.labels[self.color_role].title())).getColor()
        
        if ok:
            if status == "new":
                self.setColor(qcolor.name())
                
            elif status == "default":
                self.setColor("")
                
    def setColor(self, color: str) -> None:
        self.values[self.color_role] = color
        
        self.selector.setText(_("Select color (selected: {})")
                              .format(self.values[self.color_role] if color != "" else _("none")))
        
        self.viewer.fill(color if color != "" else Qt.GlobalColor.transparent)
        self.label.setPixmap(self.viewer)

        
class ModuleSettings(BaseSettings):
    def __init__(self, parent: SettingsWidget, index: int, module: str, target) -> None:
        super().__init__(parent, index)
        
        self.module = module
        self.target = target
        
        self.format_changed = False
        self.do_not_check = True
        
        if self.module == "sidebar" or self.module == "notes" or self.module == "todos":
            self.alternate_row_colors_checkbox = QCheckBox(self)
            self.alternate_row_colors_checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            try:
                self.alternate_row_colors_checkbox.checkStateChanged.connect(self.alternateRowColorsChanged)
            except:
                self.alternate_row_colors_checkbox.stateChanged.connect(self.alternateRowColorsChanged)
            
            self.form.addRow(Label(self, _("List")))
            self.form.addRow("{}:".format(_("Alternate row colors")), self.alternate_row_colors_checkbox)
            
        if self.module == "notes" or self.module == "todos":
            self.background_button = PushButton(self)
            self.background_button.clicked.connect(self.setBackground)
            
            self.foreground_button = PushButton(self)
            self.foreground_button.clicked.connect(self.setForeground)
            
            self.form.addRow("{}:".format(_("Default background color of items")), self.background_button)
            self.form.addRow("{}:".format(_("Default text color of items")), self.foreground_button)
            
        if self.module == "diaries":
            self.highlight_button = PushButton(self)
            self.highlight_button.clicked.connect(self.setHighlight)
            
            self.form.addRow(Label(self, _("List")))
            self.form.addRow("{}:".format(_("Default creation state color of items")), self.highlight_button)
            
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
                
            self.form.addRow(Label(self, _("Document")))
            self.form.addRow(_("Auto-save:"), self.autosave_checkbox)
            self.form.addRow(_("Format:"), self.format_combobox)
        
        self.load()
        
    @Slot(int or Qt.CheckState)
    def alternateRowColorsChanged(self, signal: Qt.CheckState | int) -> None:
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.alternate_row_colors = "disabled"
            self.alternate_row_colors_checkbox.setText(_("Disabled"))
        
        elif signal == Qt.CheckState.Checked or signal == 2:
            self.alternate_row_colors = "enabled"
            self.alternate_row_colors_checkbox.setText(_("Enabled"))
        
    def apply(self, format_change_acceptted: bool) -> bool:
        if (self.module == "notes" or self.module == "diaries") and not format_change_acceptted:
            if self.format_ == "plain-text":
                self.format_combobox.setCurrentIndex(0)
                
            elif self.format_ == "markdown":
                self.format_combobox.setCurrentIndex(1)
                
            elif self.format_ == "html":
                self.format_combobox.setCurrentIndex(2)
        
        if self.module == "sidebar":
            call = settings.set(self.module, self.alternate_row_colors, "", "", "", "", "")
        
        if self.module == "notes":
            call = settings.set(self.module, self.alternate_row_colors, self.autosave, self.background, self.foreground, self.format, "")
        
        elif self.module == "todos":
            call = settings.set(self.module, self.alternate_row_colors, "", self.background, self.foreground, self.format, "")
        
        elif self.module == "diaries":
            call = settings.set(self.module, "", self.autosave, "", "", self.format, self.highlight)
        
        if call:
            self.format_ = self.format
            
            self.target.refreshSettings()
                
            return True
        
        else:
            return False
        
    def load(self) -> None:
        self.alternate_row_colors, self.autosave, self.background, self.foreground, self.format, self.highlight = settings.get(self.module)
        
        self.format_ = self.format
           
        if self.alternate_row_colors == "enabled": 
            self.alternate_row_colors_checkbox.setChecked(True)
            self.alternate_row_colors_checkbox.setText(_("Enabled"))
            
        elif self.alternate_row_colors == "disabled":
            self.alternate_row_colors_checkbox.setChecked(False)
            self.alternate_row_colors_checkbox.setText(_("Disabled"))
        
        if self.module == "notes" or self.module == "todos":
            self.background_button.setText(_("Select color (selected: {})")
                                           .format(_("default") if self.background == "default" else self.background))
            
            self.foreground_button.setText(_("Select color (selected: {})")
                                           .format(_("default") if self.foreground == "default" else self.foreground))
            
        if self.module == "diaries":
            self.highlight_button.setText(_("Select color (selected: {})")
                                          .format(_("default") if self.highlight == "default" else self.highlight))

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
        
    def reset(self, format_change_acceptted: bool) -> bool:
        if settings.reset(self.module, format_change_acceptted):
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
            
            
class ShortcutsSettings(BaseSettings):
    def __init__(self, parent: SettingsWidget, index: int) -> None:
        super().__init__(parent, index)
        
        self.start_menu_shortcut = QWidget(self)

        self.form.addRow(Label(self, _("Start Menu Shortcut")))
            
        self.auto_shortcut_checkbox = QCheckBox("", self.start_menu_shortcut)
        self.auto_shortcut_checkbox.setEnabled(False)      
        self.auto_shortcut_checkbox.setChecked(False)
        try:
            self.auto_shortcut_checkbox.checkStateChanged.connect(self.autoShortcutChanged)
        except:
            self.auto_shortcut_checkbox.stateChanged.connect(self.autoShortcutChanged)
            
        self.add_shortcut_button = PushButton(self.start_menu_shortcut, _("Add"),
                                              QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.add_shortcut_button.setEnabled(False)
        self.add_shortcut_button.clicked.connect(lambda: self.addDesktopFile(True))
            
        self.delete_shortcut_button = PushButton(self.start_menu_shortcut, _("Delete"),
                                                 QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.delete_shortcut_button.setEnabled(False)
        self.delete_shortcut_button.clicked.connect(self.deleteDesktopFile)
        
        self.start_menu_shortcut_layout = QHBoxLayout(self.start_menu_shortcut)
        self.start_menu_shortcut_layout.setContentsMargins(0, 0, 0, 0)
        self.start_menu_shortcut_layout.addWidget(self.auto_shortcut_checkbox)
        self.start_menu_shortcut_layout.addWidget(VSeperator(self.start_menu_shortcut))
        self.start_menu_shortcut_layout.addWidget(self.add_shortcut_button)
        self.start_menu_shortcut_layout.addWidget(self.delete_shortcut_button)
        
        self.form.addRow("{}:".format(_("Auto add at every startup")), self.start_menu_shortcut)
        
        if DESKTOP_FILE_FOUND and (APP_MODE != "meson" or not SYSTEM_DESKTOP_FILE_FOUND):
            self.auto_shortcut_checkbox.setEnabled(True)
                
            self.add_shortcut_button.setEnabled(True)
        
        if USER_DESKTOP_FILE_FOUND:
            self.delete_shortcut_button.setEnabled(True)
        
        self.load()

    @Slot(int or Qt.CheckState)
    def autoShortcutChanged(self, signal: Qt.CheckState | int) -> None:
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.auto_shortcut = "disabled"
            self.auto_shortcut_checkbox.setText(_("Disabled"))
        
        elif signal == Qt.CheckState.Checked or signal == 2:
            self.auto_shortcut = "enabled"
            self.auto_shortcut_checkbox.setText(_("Enabled"))
        
    @Slot()
    def addDesktopFile(self, manual: bool = False) -> None:
        with open(DESKTOP_FILE) as f:
            data = f.read()
            
        if APP_MODE == "@MODE@":
            data = data.replace("Exec=@BIN_DIR@/nottodbox", f"Exec=python3 {os.path.dirname(__file__)}/__init__.py")
            
            data = data.replace("Icon=io.github.mukonqi.nottodbox", f"Icon={ICON_FILE}")
        
        elif APP_MODE == "appimage":           
            data = data.replace("Exec=@BIN_DIR@/nottodbox", f"Exec={os.environ["APPIMAGE"]}")
        
        os.makedirs(f"/home/{USER_NAME}/.local/share/applications", exist_ok=True)
        
        with open(USER_DESKTOP_FILE, "w") as f:
            f.write(data)
            
        if manual:
            with open(USER_DESKTOP_FILE) as f:
                if data == f.read():
                    QMessageBox.information(self, _("Successful"), _("Start menu shortcut was added to start menu."))
            
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to add start menu shortcut to start menu."))
                    
        global USER_DESKTOP_FILE_FOUND
        USER_DESKTOP_FILE_FOUND = True
        self.delete_shortcut_button.setEnabled(True)
        
    def apply(self, format_change_acceptted: bool = True) -> bool:
        successful = True
        
        if DESKTOP_FILE_FOUND and (APP_MODE != "meson" or not SYSTEM_DESKTOP_FILE_FOUND):
            settings.setValue("shortcut/auto_shortcut", self.auto_shortcut)
                
            if self.auto_shortcut == "enabled":
                self.addDesktopFile()
                
            if self.auto_shortcut != settings.value("shortcut/auto_shortcut"):
                successful = False
                
        return successful
    
    @Slot()
    def deleteDesktopFile(self) -> None:
        os.remove(USER_DESKTOP_FILE)
        
        if not os.path.isfile(USER_DESKTOP_FILE):
            QMessageBox.information(self, _("Successful"), _("Start menu shortcut was deleted from start menu."))
            
            global USER_DESKTOP_FILE_FOUND
            USER_DESKTOP_FILE_FOUND = False
            self.delete_shortcut_button.setEnabled(False)
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete start menu shortcut from start menu."))
    
    def load(self) -> None:
        self.auto_shortcut = settings.value("shortcut/auto_shortcut")
        
        if self.auto_shortcut is None or self.auto_shortcut == "":
            settings.setValue("shortcut/auto_shortcut", "disabled")
            
            self.auto_shortcut = "disabled"
            
        if self.auto_shortcut == "enabled":
            self.auto_shortcut_checkbox.setChecked(True)
            self.auto_shortcut_checkbox.setText(_("Enabled"))
            
            if DESKTOP_FILE_FOUND and (APP_MODE != "meson" or not SYSTEM_DESKTOP_FILE_FOUND):
                self.addDesktopFile()
            
        elif self.auto_shortcut == "disabled":
            self.auto_shortcut_checkbox.setChecked(False)
            self.auto_shortcut_checkbox.setText(_("Disabled"))
                
    def reset(self, format_change_acceptted: bool = True) -> bool:
        settings.remove("shortcut/auto_shortcut")
        
        if settings.value("shortcut/auto_shortcut") is None:
            self.load()
            
            return self.apply()
        
        else:
            return False