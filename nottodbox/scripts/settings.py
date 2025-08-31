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


import configparser
import json
import os

from PySide6.QtCore import QEvent, QMargins, QModelIndex, QRect, QSettings, QSize, QStandardPaths, Qt, Slot
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QListView,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QStyledItemDelegate,
    QStyleFactory,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from .consts import ITEM_DATAS, SETTINGS_KEYS, SETTINGS_VALUES, USER_NAME
from .widgets.controls import ComboBox, HSeperator, Label, LineEdit, PushButton, VSeperator
from .widgets.dialogs import ColorSelector

COLOR_SCHEMES_DIRS = []

KDE_COLOR_SCHEMES_DIRS = QStandardPaths.locateAll(
    QStandardPaths.StandardLocation.GenericDataLocation, "color-schemes", QStandardPaths.LocateOption.LocateDirectory
)
KDE_COLOR_SCHEMES_DIRS.reverse()

KDE_COLOR_SCHEMES_FOUND = True
KDE_SYSTEM_COLOR_SCHEMES_FOUND = True
KDE_USER_COLOR_SCHEMES_FOUND = True

if KDE_COLOR_SCHEMES_DIRS == []:
    KDE_COLOR_SCHEMES_FOUND = False

elif len(KDE_COLOR_SCHEMES_DIRS) == 1:
    if KDE_COLOR_SCHEMES_DIRS[0] == "/usr/share/color-schemes":
        KDE_USER_COLOR_SCHEMES_FOUND = False

    elif KDE_COLOR_SCHEMES_DIRS[0] == os.path.join(
        QStandardPaths.standardLocations(QStandardPaths.StandardLocation.GenericDataLocation)[0], "color-schemes"
    ):
        KDE_SYSTEM_COLOR_SCHEMES_FOUND = False


NOTTODBOX_COLOR_SCHEMES_DIRS = [
    os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "color-schemes")),
    os.path.join(
        QStandardPaths.standardLocations(QStandardPaths.StandardLocation.GenericDataLocation)[0],
        "nottodbox",
        "color-schemes",
    ),
]
os.makedirs(NOTTODBOX_COLOR_SCHEMES_DIRS[1], exist_ok=True)

COLOR_SCHEMES_DIRS.extend(KDE_COLOR_SCHEMES_DIRS)
COLOR_SCHEMES_DIRS.extend(NOTTODBOX_COLOR_SCHEMES_DIRS)

NUMBERS = {1: "\u00b9", 2: "\u00b2", 3: "\u00b3", 4: "\u2074"}


class SettingsPage(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.settings = QSettings("io.github.mukonqi", "nottodbox")

        for setting in SETTINGS_KEYS:
            if self.settings.value(f"globals/{setting}") is None:
                self.settings.setValue(f"globals/{setting}", "default")

        self.pages = [
            self.makeScrollable(Appearance(self)),
            self.makeScrollable(DocumentSettings(self)),
            self.makeScrollable(ListSettings(self)),
        ]

        self.widget = QStackedWidget(self)

        for page in self.pages:
            self.widget.addWidget(page)

        self.buttons = QDialogButtonBox(self)

        self.buttons.addButton(
            PushButton(self.buttons, self.reset, self.tr("Reset")), QDialogButtonBox.ButtonRole.ResetRole
        )
        self.buttons.addButton(
            PushButton(self.buttons, self.apply, self.tr("Apply")), QDialogButtonBox.ButtonRole.ApplyRole
        )
        self.buttons.addButton(
            PushButton(self.buttons, self.cancel, self.tr("Cancel")), QDialogButtonBox.ButtonRole.RejectRole
        )

        self.layout_ = QGridLayout(self)
        self.layout_.addWidget(ListView(self), 0, 0, 3, 1)
        self.layout_.addWidget(VSeperator(self), 0, 1, 3, 1)
        self.layout_.addWidget(self.widget, 0, 2, 1, 1)
        self.layout_.addWidget(HSeperator(self), 1, 2, 1, 1)
        self.layout_.addWidget(self.buttons, 2, 2, 1, 1)

    def askFormat(self, page: QWidget, do_not_asked_before: bool, format_change_acceptted: bool) -> tuple[bool, bool]:
        if (
            type(page.widget()).__name__ == "DocumentSettings"
            and do_not_asked_before
            and page.widget().selectors[3].currentIndex()
            != page.widget().values[3].index(self.settings.value(f"globals/{SETTINGS_KEYS[3]}"))
        ):
            do_not_asked_before = False

            question = QMessageBox.question(
                self,
                self.tr("Question"),
                self.tr(
                    "If you have documents with the format setting set to global, this change may corrupt them.\nDo you really want to apply the format setting?"
                ),
            )

            if question != QMessageBox.StandardButton.Yes:
                format_change_acceptted = False

        return do_not_asked_before, format_change_acceptted

    @Slot()
    def apply(self) -> None:
        successful = True
        do_not_asked_before = True
        format_change_acceptted = True

        for page in self.pages:
            do_not_asked_before, format_change_acceptted = self.askFormat(
                page, do_not_asked_before, format_change_acceptted
            )

            if not page.apply(format_change_acceptted):
                successful = False

        if successful:
            if format_change_acceptted:
                QMessageBox.information(self, self.tr("Successful"), self.tr("All settings applied."))

            else:
                QMessageBox.information(
                    self, self.tr("Successful"), self.tr("All settings applied EXCEPT format setting.")
                )

        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to apply settings."))

    @Slot()
    def cancel(self) -> None:
        for page in self.pages:
            page.load()

    def makeScrollable(self, page: QWidget) -> QScrollArea:
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(page)

        scroll_area.apply = page.apply
        scroll_area.load = page.load
        scroll_area.reset = page.reset

        return scroll_area

    @Slot()
    def reset(self) -> None:
        successful = True
        do_not_asked_before = True
        format_change_acceptted = True

        for page in self.pages:
            do_not_asked_before, format_change_acceptted = self.askFormat(
                page, do_not_asked_before, format_change_acceptted
            )

            if not page.reset(format_change_acceptted):
                successful = False

        if successful:
            if format_change_acceptted:
                QMessageBox.information(self, self.tr("Successful"), self.tr("All setting reset."))

            else:
                QMessageBox.information(
                    self, self.tr("Successful"), self.tr("All settings reset EXCEPT format setting.")
                )

        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to reset settings."))


class ListView(QListView):
    def __init__(self, parent: SettingsPage) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.indexes = []

        self.localizeds = [self.tr("Appearance"), self.tr("Documents"), self.tr("Lists")]

        self.model_ = QStandardItemModel(self)

        for i in range(3):
            item = QStandardItem(self.localizeds[i])
            item.setData(i, ITEM_DATAS["type"])

            self.model_.appendRow(item)

            self.indexes.append(item.index())

        self.delegate = ButtonDelegate(self)

        self.setFixedWidth(140)
        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setModel(self.model_)
        self.setItemDelegate(self.delegate)
        self.setCurrentIndex(self.indexes[0])
        self.model_.setData(self.indexes[0], True, ITEM_DATAS["clicked"])


class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent: ListView) -> None:
        super().__init__(parent)

        self.parent_ = parent

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()

        name = index.data(Qt.ItemDataRole.DisplayRole)

        name_font = QFont(option.font)
        name_font.setWeight(QFont.Weight.Bold)

        name_rect = QRect(option.rect)
        name_rect.setTop(name_rect.top() + (option.rect.height() - QFontMetrics(name_font).height()) / 2)
        name_rect.setLeft(
            name_rect.left() + (option.rect.width() - QFontMetrics(name_font).horizontalAdvance(name)) / 2
        )
        name_rect.setRight(name_rect.left() + QFontMetrics(name_font).horizontalAdvance(name))
        name_rect.setBottom(name_rect.top() + QFontMetrics(name_font).height())

        border_rect = QRect(option.rect.marginsRemoved(QMargins(10, 10, 10, 10)))

        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, 1, 1)

        situations = [
            bool(index.data(ITEM_DATAS["clicked"])),
            bool(option.state & QStyle.StateFlag.State_MouseOver),
            True,
        ]

        defaults = [
            [option.palette.base().color(), option.palette.text().color(), option.palette.text().color()],
            [option.palette.button().color(), option.palette.text().color(), option.palette.buttonText().color()],
            [option.palette.link().color(), option.palette.text().color(), option.palette.linkVisited().color()],
        ]

        colors = []

        i = 2

        for status in situations:
            if status:
                for j in range(3):
                    colors.append(defaults[i][j])

                break

            i -= 1

        border_pen = QPen(colors[2], 5)
        painter.setPen(border_pen)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawPath(border_path)
        painter.fillPath(border_path, colors[0])

        painter.restore()

        painter.setPen(colors[1])
        painter.setFont(name_font)

        painter.drawText(name_rect, name)

    def editorEvent(
        self, event: QEvent, model: QStandardItemModel, option: QStyleOptionViewItem, index: QModelIndex
    ) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            indexes = self.parent_.indexes.copy()
            indexes.remove(index)

            for index_ in indexes:
                model.setData(index_, False, ITEM_DATAS["clicked"])

            model.setData(index, True, ITEM_DATAS["clicked"])
            self.parent_.parent_.widget.setCurrentIndex(index.data(ITEM_DATAS["type"]))

        return super().editorEvent(event, model, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QRect:
        return QSize(option.rect.width(), option.rect.width())


class Appearance(QWidget):
    def __init__(self, parent: SettingsPage) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.default_style = QApplication.style().objectName().title()

        self.styles_combobox = ComboBox(self)
        self.styles_combobox.setEditable(False)

        self.color_schemes_widget = QWidget(self)

        self.color_schemes_buttons = QWidget(self.color_schemes_widget)

        self.color_schemes_combobox = ComboBox(self.color_schemes_widget)
        self.color_schemes_combobox.setEditable(False)

        self.color_schemes_rename = PushButton(self.color_schemes_widget, self.renameColorScheme, self.tr("Rename"))

        self.color_schemes_delete = PushButton(self.color_schemes_widget, self.deleteColorScheme, self.tr("Delete"))

        self.color_schemes_import = PushButton(self.color_schemes_widget, self.importColorScheme, self.tr("Import"))

        self.load()

        self.custom_color_schemes = CustomColorSchemes(self)

        self.color_schemes_widget_layout = QHBoxLayout(self.color_schemes_widget)
        self.color_schemes_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.color_schemes_widget_layout.addWidget(self.color_schemes_combobox)
        self.color_schemes_widget_layout.addWidget(self.color_schemes_rename)
        self.color_schemes_widget_layout.addWidget(self.color_schemes_delete)
        self.color_schemes_widget_layout.addWidget(VSeperator(self.color_schemes_widget))
        self.color_schemes_widget_layout.addWidget(self.color_schemes_import)

        self.layout_ = QFormLayout(self)
        self.layout_.addRow(Label(self, self.tr("Style")))
        self.layout_.addRow("{}*:".format(self.tr("Style")), self.styles_combobox)
        self.layout_.addRow(Label(self, self.tr("Color scheme").title()))
        self.layout_.addRow("{}:".format(self.tr("Color scheme")), self.color_schemes_widget)
        self.layout_.addRow(
            "{} {}:".format(self.tr("Custom"), self.tr("Color scheme").lower()), self.custom_color_schemes.name
        )
        self.layout_.addWidget(self.custom_color_schemes)
        self.layout_.addRow(HSeperator(self))
        self.layout_.addRow(Label(self, self.tr("Warning: Some styles may not be detected"), 0x0001))
        self.layout_.addRow(
            Label(
                self,
                "<br>{}{}".format(
                    self.superscriptDirNumber(1), self.tr("From the system directory for KDE-format color schemes")
                ),
                0x0001,
            )
        )
        self.layout_.addRow(
            Label(
                self,
                "<br>{}{}".format(
                    self.superscriptDirNumber(2), self.tr("From the user directory for KDE-format color schemes")
                ),
                0x0001,
            )
        )
        self.layout_.addRow(
            Label(
                self,
                "<br>{}{}".format(
                    self.superscriptDirNumber(3),
                    self.tr("From the system directory for Nottodbox-format color schemes"),
                ),
                0x0001,
            )
        )
        self.layout_.addRow(
            Label(
                self,
                "<br>{}{}".format(
                    self.superscriptDirNumber(4), self.tr("From the user directory for Nottodbox-format color schemes")
                ),
                0x0001,
            )
        )

        self.styles_combobox.currentTextChanged.connect(self.styleChanged)
        self.color_schemes_combobox.currentTextChanged.connect(self.colorSchemeChanged)

    @Slot(bool)
    def apply(self, format_change_acceptted: bool = True) -> bool:
        successful = True

        if self.use_default_style:
            self.parent_.settings.setValue("appearance/style", "")
            QApplication.setStyle(self.default_style)

            if self.parent_.settings.value("appearance/style") != "":
                successful = False

        else:
            self.parent_.settings.setValue("appearance/style", self.current_style)
            QApplication.setStyle(self.current_style)

            if self.parent_.settings.value("appearance/style") != self.current_style:
                successful = False

        if not self.custom_color_schemes.apply():
            successful = False

        if self.use_default_color_scheme:
            self.parent_.settings.setValue("appearance/color_scheme", "")

            if self.parent_.settings.value("appearance/color_scheme") != "":
                successful = False

        else:
            self.parent_.settings.setValue("appearance/color_scheme", self.current_color_scheme)

            if self.parent_.settings.value("appearance/color_scheme") != self.current_color_scheme:
                successful = False

        self.loadPalette()

        return successful

    @Slot(str)
    def colorSchemeChanged(self, value: str) -> None:
        if value == self.tr("Style default"):
            self.current_color_scheme = ""
            self.use_default_color_scheme = True
            self.custom_color_schemes.setEnabled(False)

        elif value == self.tr("Custom"):
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
        data["Accent"] = self.convertToHexColor(config["Colors:Selection"]["ForegroundNormal"])
        data["HighlightedText"] = self.convertToHexColor(config["Colors:Selection"]["ForegroundNormal"])
        data["Link"] = self.convertToHexColor(config["Colors:View"]["ForegroundLink"])
        data["LinkVisited"] = self.convertToHexColor(config["Colors:View"]["ForegroundVisited"])

        return data

    @Slot()
    def deleteColorScheme(self) -> None:
        name = self.current_color_scheme

        if (
            os.path.isfile(self.color_schemes[name])
            and os.path.dirname(self.color_schemes[name]) == NOTTODBOX_COLOR_SCHEMES_DIRS[1]
        ):
            os.remove(self.color_schemes[name])

            if self.parent_.settings.value("appearance/color_scheme") == name:
                self.parent_.settings.setValue("appearance/color_scheme", "")

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
            question = QMessageBox.question(
                self,
                self.tr("Question"),
                self.tr("A color scheme with the name '{name}' already exists.\nDo you want to overwrite it?").format(
                    name=pretty_name
                ),
            )

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

    @Slot()
    def load(self) -> None:
        self.styles_list = QStyleFactory.keys()
        self.styles_list.insert(0, "{} ({})".format(self.tr("System default"), self.default_style))

        self.styles_combobox.addItems(self.styles_list)

        self.current_style = self.parent_.settings.value("appearance/style")

        if self.current_style is None or self.current_style == "":
            if self.current_style is None:
                self.parent_.settings.setValue("appearance/style", "")

            self.current_style = self.default_style
            self.use_default_style = True

            self.styles_combobox.setCurrentIndex(0)

        else:
            QApplication.setStyle(self.current_style)

            self.use_default_style = False

            self.styles_combobox.setCurrentText(self.current_style)

        self.color_schemes = {}

        for dir_ in COLOR_SCHEMES_DIRS:
            for entry in os.scandir(dir_):
                if entry.is_file():
                    self.getColorSchemeName(entry.path)

        self.color_schemes_list = list(self.color_schemes.keys())
        self.color_schemes_list.insert(0, self.tr("Style default"))
        self.color_schemes_list.append(self.tr("Custom"))

        self.color_schemes_combobox.addItems(self.color_schemes_list)

        self.current_color_scheme = self.parent_.settings.value("appearance/color_scheme")

        if self.current_color_scheme in self.color_schemes:
            self.use_default_color_scheme = False

            self.color_schemes_combobox.setCurrentText(self.current_color_scheme)

        else:
            if self.current_color_scheme is None:
                self.parent_.settings.setValue("appearance/color_scheme", "")

            self.current_color_scheme = ""

            self.use_default_color_scheme = True

            self.color_schemes_combobox.setCurrentIndex(0)

        self.applied_color_scheme = self.current_color_scheme

        self.setColorSchemeButtons(self.current_color_scheme)

        self.loadOnlySomeTexts()
        self.loadPalette()

    def loadOnlySomeTexts(self) -> None:
        self.color_schemes_list[0] = self.tr("Style default")
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

        self.parent_.parent_.sidebar.refresh()

    @Slot()
    def importColorScheme(self) -> None:
        paths = QFileDialog.getOpenFileNames(
            self,
            self.tr("Import a {the_item}").format(the_item=self.tr("Color scheme")).title(),
            "",
            self.tr("Color schemes (*.colors *.json)"),
        )[0]

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

        newname, topwindow = QInputDialog.getText(self, self.tr("Rename"), self.tr("Please enter a new name."))

        if topwindow and newname != "":
            if (
                not os.path.exists(os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{newname}.json"))
                and os.path.dirname(path) == NOTTODBOX_COLOR_SCHEMES_DIRS[1]
                and os.path.isfile(path)
            ):
                with open(path) as f:
                    data = json.load(f)

                data["name"] = newname

                if name in os.path.basename(self.color_schemes[name]):
                    path = os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{newname}.json")

                    os.rename(path, os.path.join(NOTTODBOX_COLOR_SCHEMES_DIRS[1], f"{newname}.json"))

                with open(path, "w") as f:
                    json.dump(data, f)

                if self.parent_.settings.value("appearance/color_scheme") == name:
                    self.parent_.settings.setValue("appearance/color_scheme", newname)

                self.color_schemes[f"{newname}{self.superscriptDirNumber(4)}"] = path

                self.color_schemes_list[self.color_schemes_list.index(name)] = (
                    f"{newname}{self.superscriptDirNumber(4)}"
                )

                self.color_schemes_combobox.addItems(self.color_schemes_list)
                self.color_schemes_combobox.setCurrentText(f"{newname}{self.superscriptDirNumber(4)}")

                self.custom_color_schemes.createList()

            else:
                QMessageBox.critical(
                    self,
                    self.tr("Error"),
                    self.tr("{the_item} can not be renamed.").format(
                        the_item=self.tr("'{name}' color scheme").format(name=name)
                    ),
                )

    @Slot(bool)
    def reset(self, format_change_acceptted: bool = True) -> bool:
        self.parent_.settings.remove("appearance/style")
        self.parent_.settings.remove("appearance/color_scheme")

        if (
            self.parent_.settings.value("appearance/style") is None
            and self.parent_.settings.value("appearance/color_scheme") is None
        ):
            self.load()

            return self.apply()

        else:
            return False

    def setColorSchemeButtons(self, value: str) -> None:
        if (
            self.current_color_scheme != ""
            and os.path.dirname(self.color_schemes[value]) == NOTTODBOX_COLOR_SCHEMES_DIRS[1]
        ):
            self.color_schemes_rename.setEnabled(True)
            self.color_schemes_delete.setEnabled(True)

        else:
            self.color_schemes_rename.setEnabled(False)
            self.color_schemes_delete.setEnabled(False)

    @Slot(str)
    def styleChanged(self, value: str) -> None:
        if value == "{} ({})".format(self.tr("System default"), self.default_style):
            self.current_style = self.default_style
            self.use_default_style = True

        else:
            self.current_style = value
            self.use_default_style = False

        self.loadOnlySomeTexts()

    def superscriptDirNumber(self, value: str | int) -> str:
        if isinstance(value, int):
            number = value

        else:
            if not KDE_COLOR_SCHEMES_FOUND:
                dir_number = 2

            elif not KDE_SYSTEM_COLOR_SCHEMES_FOUND:
                dir_number = 1

            else:
                dir_number = 0

            for dir_ in COLOR_SCHEMES_DIRS:
                dir_number += 1

                if os.path.dirname(value) == dir_ or dir_number == 4:
                    number = dir_number

                    break

                if dir_number == 1 and not KDE_USER_COLOR_SCHEMES_FOUND:
                    dir_number += 1

        return NUMBERS.get(number, number)


class CustomColorSchemes(QWidget):
    def __init__(self, parent: Appearance) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.name = LineEdit(self.parent_, f"Color scheme by {USER_NAME}")

        self.combobox = ComboBox(self)

        self.createList()

        self.combobox.currentTextChanged.connect(self.baseColorSchemeChanged)

        self.labels = {
            "Window": self.tr("Window"),
            "WindowText": self.tr("Window text"),
            "Base": self.tr("Base"),
            "AlternateBase": self.tr("Alternate base"),
            "ToolTipBase": self.tr("Tooltip base"),
            "ToolTipText": self.tr("Tooltip text"),
            "PlaceholderText": self.tr("Placeholder text"),
            "Text": self.tr("Text"),
            "Button": self.tr("Button"),
            "ButtonText": self.tr("Button text"),
            "BrightText": self.tr("Bright text"),
            "Light": self.tr("Light"),
            "Midlight": self.tr("Mid light"),
            "Dark": self.tr("Dark"),
            "Mid": self.tr("Mid"),
            "Shadow": self.tr("Shadow"),
            "Highlight": self.tr("Highlight"),
            "Accent": self.tr("Accent"),
            "HighlightedText": self.tr("Highlighted text"),
            "Link": self.tr("Link"),
            "LinkVisited": self.tr("Visited link"),
        }

        self.buttons = {}

        number = 0

        self.form = QFormLayout(self)
        self.form.addRow("{}:".format(self.tr("Color scheme to be edited")), self.combobox)

        for number, color_role in enumerate(self.labels):
            self.buttons[color_role] = ColorSelector(self, True, False, False)

            if number == 1:
                self.form.addRow(Label(self, self.tr("General")))

            elif number == 12:
                self.form.addRow(Label(self, self.tr("3D Bevel and Shadow Effects")))

            elif number == 17:
                self.form.addRow(Label(self, self.tr("Selected (Marked) Items")))

            elif number == 20:
                self.form.addRow(Label(self, self.tr("Links")))

            self.form.addRow(f"{self.labels[color_role]}:", self.buttons[color_role])

        self.setEnabled(False)

    def apply(self, format_change_acceptted: bool = True) -> bool:
        if self.parent_.color_schemes_combobox.currentText() == self.tr("Custom"):
            overwrited = False

            name = self.name.text()

            if name == "":
                name = self.name.placeholderText()

            pretty_name = f"{name}{self.parent_.superscriptDirNumber(4)}"

            if pretty_name in self.parent_.color_schemes_list:
                question = QMessageBox.question(
                    self,
                    self.tr("Question"),
                    self.tr(
                        "A color scheme with the name '{name}' already exists.\nDo you want to overwrite it?"
                    ).format(name=pretty_name),
                )

                if question == QMessageBox.StandardButton.Yes:
                    overwrited = True

                else:
                    return False

            data = {"name": name}

            color_scheme = {}

            for color_role in self.labels:
                if self.buttons[color_role].selected != "default":
                    color_scheme[color_role] = self.buttons[color_role].selected

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
        if name == self.tr("Style default"):
            palette = QApplication.style().standardPalette()

            for color_role in self.labels:
                self.buttons[color_role].setColor(palette.color(QPalette.ColorRole[color_role]).name())

        elif name == self.tr("None"):
            for color_role in self.labels:
                self.buttons[color_role].setColor("")

        elif name in self.color_schemes_list:
            data = self.parent_.getColorSchemeData(self.parent_.color_schemes[name])

            for color_role in self.labels:
                self.buttons[color_role].setColor(data.get(color_role, ""))

    def createList(self) -> None:
        self.color_schemes_list = self.parent_.color_schemes_list.copy()
        self.color_schemes_list.insert(0, self.tr("None"))
        self.color_schemes_list.pop(-1)

        self.combobox.addItems(self.color_schemes_list)

    @Slot(bool)
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.name.setEnabled(enabled)


class GlobalSettings(QWidget):
    def __init__(self, parent: SettingsPage) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.selectors = []

        self.layout_ = QVBoxLayout(self)

    @Slot(bool)
    def apply(self, format_change_acceptted: bool = True) -> bool:
        return self.save("apply", format_change_acceptted)

    @Slot(bool)
    def reset(self, format_change_acceptted: bool = True) -> bool:
        successful = self.save("reset", format_change_acceptted)

        if successful:
            self.load()

        return successful


class DocumentSettings(GlobalSettings):
    def __init__(self, parent: SettingsPage) -> None:
        super().__init__(parent)

        self.localized_defaults = [
            self.tr("None").lower(),
            self.tr("Disabled").lower(),
            self.tr("Enabled").lower(),
            "Markdown",
            self.tr("None").lower(),
            self.tr("Documents").lower(),
            self.tr("No").lower(),
        ]

        self.localized_labels = [
            self.tr("Completion status*"),
            self.tr("Content lock**"),
            self.tr("Auto-save"),
            self.tr("Document format"),
            self.tr("External synchronization"),
            self.tr("Export folder"),
            self.tr("Pinned to sidebar"),
        ]

        self.localized_options = [
            [self.tr("Completed"), self.tr("Uncompleted"), self.tr("None")],
            [self.tr("Enabled"), self.tr("Disabled")],
            [self.tr("Enabled"), self.tr("Disabled")],
            ["Markdown", "HTML", self.tr("Plain-text")],
            [
                "{}, {}".format(setting, self.tr("with export synchronization"))
                for setting in [self.tr("Follow format"), "PDF", "ODT"]
            ]
            + [
                f"Markdown, {mode}"
                for mode in [
                    self.tr("with export and import synchronizations"),
                    self.tr("with export synchronization"),
                    self.tr("with import synchronization"),
                ]
            ]
            + ["HTML, {}".format(self.tr("with export synchronization"))]
            + [
                f"Plain-text, {mode}"
                for mode in [
                    self.tr("with export and import synchronizations"),
                    self.tr("with export synchronization"),
                    self.tr("with import synchronization"),
                ]
            ],
            [self.tr("Documents"), self.tr("Desktop")],
            [self.tr("Yes"), self.tr("No")],
        ]

        self.values = [["default"] + values for values in SETTINGS_VALUES]

        for i in range(7):
            widget = QWidget(self)
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)

            self.selectors.append(QComboBox(widget))

            self.selectors[-1].addItem(self.tr("Follow default ({})").format(self.localized_defaults[i]))

            self.selectors[-1].addItems(self.localized_options[i])

            label = Label(widget, f"{self.localized_labels[i]}:", Qt.AlignmentFlag.AlignRight)
            label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

            layout.addWidget(label)
            layout.addWidget(self.selectors[-1])

            self.layout_.addWidget(widget)

        self.layout_.addWidget(
            Label(
                self,
                self.tr("*Setting this to 'Completed' or 'Uncompleted' converts to a to-do."),
                Qt.AlignmentFlag.AlignLeft,
            )
        )
        self.layout_.addWidget(
            Label(self, self.tr("**Setting this to 'Enabled' converts to a diary."), Qt.AlignmentFlag.AlignLeft)
        )

        self.load()

    @Slot()
    def load(self) -> None:
        for i in range(7):
            self.selectors[i].setCurrentIndex(
                self.values[i].index(self.parent_.settings.value(f"globals/{SETTINGS_KEYS[i]}"))
            )

    def save(self, mode: str, format_change_acceptted: bool = True) -> bool:
        if not format_change_acceptted:
            self.selectors[3].setCurrentIndex(
                self.values[3].index(self.parent_.settings.value(f"globals/{SETTINGS_KEYS[3]}"))
            )

        successful = True

        for i in range(7):
            self.parent_.settings.setValue(
                f"globals/{SETTINGS_KEYS[i]}",
                self.values[i][self.selectors[i].currentIndex()] if mode == "apply" else "default",
            )

            check = self.parent_.settings.value(f"globals/{SETTINGS_KEYS[i]}") == (
                self.values[i][self.selectors[i].currentIndex()] if mode == "apply" else "default"
            )

            successful &= check

            if check:
                for item in self.parent_.parent_.home.selector.maindb.items.values():
                    if "global" in item.data(ITEM_DATAS["completed"] + i)[0]:
                        item.setData(
                            (
                                item.data(ITEM_DATAS["completed"] + i)[0],
                                self.parent_.parent_.home.selector.tree_view.handleSettingViaGlobal(i),
                            ),
                            ITEM_DATAS["completed"] + i,
                        )

                        # FIXME
                        if i == 6:
                            if self.values[i][self.selectors[i].currentIndex()] == "yes":
                                self.parent_.parent_.home.selector.options.pin(item.index(), False, False)

                            elif self.values[i][self.selectors[i].currentIndex()] == "no":
                                self.parent_.parent_.home.selector.options.unpin(item.index(), False, False)

        return successful


class ListSettings(GlobalSettings):
    def __init__(self, parent: SettingsPage) -> None:
        super().__init__(parent)

        self.localizeds = [
            self.tr("Background color"),
            self.tr("Background color when mouse is over"),
            self.tr("Background color when clicked"),
            self.tr("Foreground color"),
            self.tr("Foreground color when mouse is over"),
            self.tr("Foreground color when clicked"),
            self.tr("Border color"),
            self.tr("Border color when mouse is over"),
            self.tr("Border color when clicked"),
        ]

        for i in range(9):
            widget = QWidget(self)
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)

            label = Label(widget, f"{self.localizeds[i]}:", Qt.AlignmentFlag.AlignRight)
            label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

            self.selectors.append(ColorSelector(widget, True, False, False))

            layout.addWidget(label)
            layout.addWidget(self.selectors[-1])

            self.layout_.addWidget(widget)

        self.load()

    @Slot()
    def load(self) -> None:
        for i in range(9):
            self.selectors[i].setColor(self.parent_.settings.value(f"globals/{SETTINGS_KEYS[7 + i]}"))

    def save(self, mode: str, format_change_acepptted: bool = True) -> bool:
        successful = True

        for i in range(9):
            self.parent_.settings.setValue(
                f"globals/{SETTINGS_KEYS[7 + i]}", self.selectors[i].selected if mode == "apply" else "default"
            )

            check = self.parent_.settings.value(f"globals/{SETTINGS_KEYS[7 + i]}") == (
                self.selectors[i].selected if mode == "apply" else "default"
            )

            successful &= check

            if check:
                for item in self.parent_.parent_.home.selector.maindb.items.values():
                    if "global" in item.data(ITEM_DATAS["bg_normal"] + i)[0]:
                        item.setData(
                            (
                                item.data(ITEM_DATAS["bg_normal"] + i)[0],
                                self.parent_.parent_.home.selector.tree_view.handleSettingViaGlobal(7 + i),
                            ),
                            ITEM_DATAS["bg_normal"] + i,
                        )

        return successful
