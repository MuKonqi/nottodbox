# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2025 MuKonqi (Muhammed S.)

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


import datetime
import os
import typing

from PySide6.QtCore import (
    QEvent,
    QFileSystemWatcher,
    QMargins,
    QModelIndex,
    QObject,
    QPoint,
    QRect,
    QSettings,
    QSize,
    QSortFilterProxyModel,
    Qt,
    QThread,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPdfWriter,
    QPen,
    QStandardItem,
    QStandardItemModel,
    QTextDocument,
    QTextDocumentWriter,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QMenu,
    QMessageBox,
    QStackedWidget,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from .consts import ITEM_DATAS, SETTINGS_DEFAULTS, SETTINGS_KEYS, SETTINGS_OPTIONS, SETTINGS_VALUES, USER_DIRS
from .database import MainDB
from .widgets.controls import Action, CalendarWidget, HSeperator, Label, LineEdit, PushButton, VSeperator
from .widgets.dialogs import ChangeAppearance, ChangeSettings, Export, GetDescription, GetName, GetNameAndDescription
from .widgets.documents import BackupView, NormalView, setDocument


class HomePage(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.layout_ = QHBoxLayout(self)

        self.selector = Selector(self)

        self.area = Area(self)

        self.layout_.addWidget(self.selector)
        self.layout_.addWidget(self.area)


class Area(QWidget):
    pages = []

    def __init__(self, parent: HomePage) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.layout_ = QGridLayout(self)

        self.setArea(1, 1)

    def closeAll(self) -> None:
        pages = [page for page in self.pages if page.document is not None]

        for page in pages:
            page.removeDocument()

    @Slot(int, int)
    def setArea(self, row: int, column: int) -> None:
        self.closeAll()

        for index in range(self.layout_.count()):
            self.layout_.itemAt(index).widget().deleteLater()

        self.pages = []

        for row_ in range(row):
            for column_ in range(column):
                self.pages.append(Page(self))
                self.layout_.addWidget(self.pages[-1], row_, column_)

        # Set first page as target.
        self.target = self.pages[0]
        self.target.setAsTarget()


class Page(QWidget):
    document = None

    def __init__(self, parent: Area) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.pager = QStackedWidget(self)

        self.container = QWidget(self.pager)

        self.button = PushButton(
            self.container, self.setAsTarget, self.tr("Click this button\nto select a document for here"), False, True
        )
        font = self.button.font()
        font.setBold(True)
        font.setPointSize(16)
        self.button.setFixedHeight(QFontMetrics(font).height() * 3)
        self.button.setFont(font)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.addStretch()
        self.container_layout.addWidget(self.button)
        self.container_layout.addStretch()

        self.pager.addWidget(self.container)

        self.layout_ = QGridLayout(self)
        self.layout_.addWidget(self.pager, 1, 1)
        self.layout_.addWidget(HSeperator(self), 0, 1)
        self.layout_.addWidget(VSeperator(self), 1, 2)
        self.layout_.addWidget(HSeperator(self), 2, 1)
        self.layout_.addWidget(VSeperator(self), 1, 0)

    def addDocument(self, document: NormalView | BackupView) -> None:
        if self.document is not None:
            self.removeDocument()

        self.pager.addWidget(document)
        (self.pager.setCurrentIndex(1),)

        self.document = document

    def removeDocument(self) -> None:
        self.parent_.parent_.selector.options.close(self.document.index)

        self.pager.removeWidget(self.document)
        self.pager.setCurrentIndex(0)

        self.document = None

    def setAsTarget(self) -> None:
        pages = self.parent_.pages.copy()
        pages.remove(self)

        for page in pages:
            page.button.setText(self.tr("Click this button\nto select a document for here"))

        self.button.setText(self.tr("Select a document for here"))

        self.parent_.target = self


class Selector(QWidget):
    def __init__(self, parent: HomePage) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.maindb = MainDB()

        self.settings = QSettings("io.github.mukonqi", "nottodbox")

        self.do_not_write = False

        self.options = Options(self)

        self.layout_ = QVBoxLayout(self)

        self.buttons = QWidget(self)

        self.tree_view = TreeView(self)

        self.search_entry = LineEdit(self, self.tr("Search"))
        self.search_entry.textChanged.connect(self.tree_view.filterNormal)

        self.filter_combobox = QComboBox(self)
        self.filter_combobox.addItems(
            [
                self.tr("By name"),
                self.tr("By creation date"),
                self.tr("By modification date"),
                self.tr("By content / description"),
            ]
        )
        self.filter_combobox.currentIndexChanged.connect(self.tree_view.filterChanged)

        self.calendar_widget = CalendarWidget(self)
        self.calendar_widget.selectionChanged.connect(self.selectedDateChanged)

        self.calendar_checkbox = QCheckBox(self)
        self.calendar_checkbox.setText(self.tr("Calendar"))
        try:
            self.calendar_checkbox.checkStateChanged.connect(self.enableCalendar)
        except AttributeError:
            self.calendar_checkbox.stateChanged.connect(self.enableCalendar)
        self.calendar_checkbox.setCheckState(
            Qt.CheckState.Unchecked if self.settings.value("selector/calendar") == "hidden" else Qt.CheckState.Checked
        )

        self.pages = QStackedWidget(self)

        self.updating = Label(self, self.tr("Database\nis updating"))
        font = self.updating.font()
        font.setBold(True)
        font.setPointSize(24)
        self.updating.setFont(font)

        self.create_first_notebook = CreateFirstNotebook(self)

        self.container = QWidget(self)

        self.pages.addWidget(self.updating)
        self.pages.addWidget(self.create_first_notebook)
        self.pages.addWidget(self.container)

        self.buttons_layout = QHBoxLayout(self.buttons)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)

        for button in self.tree_view.buttons:
            self.buttons_layout.addWidget(button)

        self.container_layout = QGridLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setColumnStretch(1, 2)
        self.container_layout.addWidget(self.calendar_checkbox, 0, 0, 1, 1)
        self.container_layout.addWidget(self.filter_combobox, 0, 1, 1, 1)
        self.container_layout.addWidget(self.search_entry, 1, 0, 1, 2)
        self.container_layout.addWidget(self.tree_view, 2, 0, 1, 2)

        self.layout_.addWidget(self.buttons)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.calendar_widget)
        self.layout_.addWidget(self.pages)

        self.maindb.updateDatabase()
        self.tree_view.appendAll()
        self.parent_.parent_.sidebar.buttons[-1].setChecked(self.settings.value("selector/self") == "hidden")

        self.setFixedWidth(330)
        self.enableCalendar(
            Qt.CheckState.Unchecked if self.settings.value("selector/calendar") == "hidden" else Qt.CheckState.Checked
        )
        self.setPage()
        self.setVisible(self.settings.value("selector/self") != "hidden")

    @Slot(int or Qt.CheckState)
    def enableCalendar(self, signal: int | Qt.CheckState) -> None:
        if not self.do_not_write:
            self.settings.setValue(
                "selector/calendar", "hidden" if signal == Qt.CheckState.Unchecked or signal == 0 else "visible"
            )

        self.calendar_widget.setVisible(not (signal == Qt.CheckState.Unchecked or signal == 0))

    def getPageFromIndex(self, index: QModelIndex) -> None | typing.Any:
        return next(
            (page for page in self.parent_.area.pages if page.document is not None and page.document.index == index),
            None,
        )

    def setPage(self) -> None:
        if self.tree_view.model_.rowCount() == 0:
            self.do_not_write = True
            self.calendar_checkbox.setCheckState(Qt.CheckState.Checked)
            self.do_not_write = False

            self.pages.setCurrentIndex(1)

        else:
            self.do_not_write = True
            self.calendar_checkbox.setCheckState(
                Qt.CheckState.Unchecked
                if self.settings.value("selector/calendar") == "hidden"
                else Qt.CheckState.Checked
            )
            self.do_not_write = False

            self.pages.setCurrentIndex(2)

    @Slot()
    def selectedDateChanged(self) -> None:
        if self.pages.currentIndex() == 0:
            self.create_first_notebook.name.setText(self.calendar_widget.selectedDate().toString("dd.MM.yyyy"))

        elif self.pages.currentIndex() == 1:
            self.search_entry.setText(self.calendar_widget.selectedDate().toString("dd.MM.yyyy"))

    def setVisible(self, visible: bool) -> None:
        self.settings.setValue("selector/self", "hidden" if not visible else "visible")

        return super().setVisible(visible)


class CreateFirstNotebook(QWidget):
    def __init__(self, parent: Selector) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.layout_ = QVBoxLayout(self)

        self.label = Label(self, self.tr("Create your first notebook"))
        font = self.label.font()
        font.setBold(True)
        font.setPointSize(16)
        self.label.setFont(font)

        self.name = LineEdit(self, self.tr("Name (required)"))
        self.name.setText(self.parent_.calendar_widget.selectedDate().toString("dd.MM.yyyy"))

        self.description = LineEdit(self, self.tr("Description (not required)"))

        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(lambda: self.createNotebook(self.name.text(), self.description.text()))

        self.layout_.addWidget(self.label)
        self.layout_.addWidget(self.name)
        self.layout_.addWidget(self.description)
        self.layout_.addWidget(self.buttons)

    @Slot(str, str)
    def createNotebook(self, name: str, description: str) -> None:
        if name == "":
            QMessageBox.critical(self.parent_, self.tr("Error"), self.tr("A name is required."))
            return

        if self.parent_.options.createNotebook(name, description):
            self.name.clear()
            self.parent_.setPage()


class Options:
    pages = {}

    def __init__(self, parent: Selector) -> None:
        self.parent_ = parent

    @Slot(QModelIndex)
    def addLock(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set("enabled", "locked", name, table):
            index.model().setData(index, ["self", "enabled"], ITEM_DATAS["locked"])
            self.parent_.tree_view.setType(index)

            page = self.parent_.getPageFromIndex(index)
            if page is not None:
                page.document.refreshSettings()

            QMessageBox.information(
                self.parent_, self.parent_.tr("Successful"), self.tr("Lock added {to_item}.", index)
            )

        else:
            QMessageBox.critical(
                self.parent_, self.parent_.tr("Error"), self.tr("Failed to add lock {to_item}.", index)
            )

    @Slot(QModelIndex)
    def changeAppearance(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        ok, values = ChangeAppearance(self.parent_, self.parent_.maindb, index).get()

        if ok:
            successful = True

            for i in range(9):
                if self.parent_.maindb.set(values[i], SETTINGS_KEYS[7 + i], name, table):
                    index.model().setData(
                        index,
                        self.parent_.tree_view.handleSetting(
                            self.parent_.maindb.items[(name, table)], 7 + i, values[i]
                        ),
                        ITEM_DATAS["bg_normal"] + i,
                    )

                    if index.data(ITEM_DATAS["type"]) == "notebook":
                        for name_, table_ in self.parent_.maindb.items:
                            if (
                                table_ == name
                                and "notebook"
                                in self.parent_.maindb.items[(name_, table_)].data(ITEM_DATAS["bg_normal"] + i)[0]
                            ):
                                self.parent_.maindb.items[(name_, table_)].setData(
                                    self.parent_.tree_view.handleSetting(
                                        self.parent_.maindb.items[(name_, table_)], 7 + i, "notebook"
                                    ),
                                    ITEM_DATAS["bg_normal"] + i,
                                )

                else:
                    successful = False

            if successful:
                QMessageBox.information(
                    self.parent_, self.parent_.tr("Successful"), self.tr("New appearance applied {to_item}.", index)
                )

            else:
                QMessageBox.critical(
                    self.parent_, self.parent_.tr("Error"), self.tr("Failed to apply new appearance {to_item}.", index)
                )

    @Slot(QModelIndex)
    def changeSettings(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        ok, values = ChangeSettings(self.parent_, self.parent_.maindb, index).get()

        if ok:
            successful = True

            for i in range(7):
                options = SETTINGS_OPTIONS + SETTINGS_VALUES[i]

                if table != "__main__":
                    options.insert(2, "notebook")

                if self.parent_.maindb.set(options[values[i]], SETTINGS_KEYS[i], name, table):
                    index.model().setData(
                        index,
                        self.parent_.tree_view.handleSetting(
                            self.parent_.maindb.items[(name, table)], i, options[values[i]]
                        ),
                        ITEM_DATAS["completed"] + i,
                    )

                    page = self.parent_.getPageFromIndex(index)
                    if page is not None:
                        page.document.refreshSettings()

                    if index.data(ITEM_DATAS["type"]) == "notebook":
                        for name_, table_ in self.parent_.maindb.items:
                            if (
                                table_ == name
                                and "notebook"
                                in self.parent_.maindb.items[(name_, table_)].data(ITEM_DATAS["completed"] + i)[0]
                            ):
                                self.parent_.maindb.items[(name_, table_)].setData(
                                    self.parent_.tree_view.handleSetting(
                                        self.parent_.maindb.items[(name_, table_)], i, "notebook"
                                    ),
                                    ITEM_DATAS["completed"] + i,
                                )

                                for page in [
                                    page
                                    for page in self.parent_.parent_.area.pages
                                    if page.document is not None
                                    and page.document.index == self.parent_.maindb.items[(name_, table_)].index()
                                ]:
                                    page.document.refreshSettings()

                    # FIXME
                    if i == 6:
                        if options[values[i]] == "yes":
                            self.pin(index, False, False)

                        elif options[values[i]] == "no":
                            self.unpin(index, False, False)

                else:
                    successful = False

            if successful:
                QMessageBox.information(
                    self.parent_, self.parent_.tr("Successful"), self.tr("New settings applied {to_item}.", index)
                )

            else:
                QMessageBox.critical(
                    self.parent_, self.parent_.tr("Error"), self.tr("Failed to apply new settings {to_item}.", index)
                )

    @Slot(QModelIndex)
    def clearContent(self, index: QModelIndex) -> None:
        document = index.data(ITEM_DATAS["name"])
        notebook = index.data(ITEM_DATAS["notebook"])

        if self.parent_.maindb.clearContent(document, notebook):
            index.model().setData(index, "", ITEM_DATAS["content"])
            index.model().setData(index, self.parent_.maindb.getBackup(document, notebook), ITEM_DATAS["backup"])

            page = self.parent_.getPageFromIndex(index)
            if page is not None:
                page.document.refreshContent()

            QMessageBox.information(
                self.parent_, self.parent_.tr("Successful"), self.tr("The content {of_item} cleared.", index)
            )

        else:
            QMessageBox.critical(
                self.parent_, self.parent_.tr("Error"), self.tr("Failed to clear the content {of_item}.", index)
            )

    @Slot(QModelIndex)
    def close(self, index: QModelIndex) -> None:
        page = self.parent_.getPageFromIndex(index)
        if page is not None:
            if page.document.mode == "normal" and page.document.last_content != page.document.getText():
                self.question = QMessageBox.question(
                    self.parent_,
                    self.parent_.tr("Question"),
                    self.tr("{the_item} not saved.\nWhat would you like to do?", index),
                    QMessageBox.StandardButton.Save
                    | QMessageBox.StandardButton.Discard
                    | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save,
                )

                if self.question == QMessageBox.StandardButton.Save:
                    if not page.document.saver.saveDocument():
                        return

                elif self.question != QMessageBox.StandardButton.Discard:
                    return

            index.model().setData(index, False, ITEM_DATAS["clicked"])

            if page.document.mode == "normal":
                page.document.changeAutosaveConnections("disconnect")

            if index in self.parent_.parent_.parent_.sidebar.list_view.items:
                self.parent_.parent_.parent_.sidebar.list_view.items[index].setData(False, ITEM_DATAS["clicked"])

    @Slot(QModelIndex)
    def createDocument(self, index: QModelIndex) -> None:
        dialog = GetName(self.parent_, self.parent_.tr("Create Document"), True, "document")
        dialog.set()
        ok, default, document = dialog.get()

        options = SETTINGS_OPTIONS.copy()
        options.append("notebook")

        default = options[default]

        if ok:
            if index.data(ITEM_DATAS["type"]) == "notebook":
                notebook = index.data(ITEM_DATAS["name"])

            elif index.data(ITEM_DATAS["type"]) == "document":
                notebook = index.data(ITEM_DATAS["notebook"])

            if not self.parent_.maindb.checkIfItExists(document, notebook):
                try:
                    diary = bool(datetime.datetime.strptime(document, "%d.%m.%Y"))

                except ValueError:
                    diary = False

                if document == "":
                    QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                    return

                if self.parent_.maindb.createDocument(default, "enabled" if diary else default, document, notebook):
                    self.parent_.tree_view.appendDocument(
                        self.parent_.maindb.getDocument(document, notebook),
                        self.parent_.maindb.items[(notebook, "__main__")],
                        notebook,
                    )

                    if self.parent_.maindb.items[(document, notebook)].data(ITEM_DATAS["pinned"])[1] == "yes":
                        self.pin(self.parent_.maindb.items[(document, notebook)].index(), False, False)

                else:
                    QMessageBox.critical(
                        self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to create document.")
                    )

            else:
                QMessageBox.critical(
                    self.parent_,
                    self.parent_.tr("Error"),
                    self.parent_.tr("{the_item} is already exists.")
                    .format(the_item=self.parent_.tr("the '{name}' document").format(name=document))
                    .capitalize(),
                )

    @Slot(str or None, str or None)
    def createNotebook(self, name: str | None = None, description: str | None = None) -> bool | None:
        ok = True

        if name is None:
            dialog = GetNameAndDescription(self.parent_, self.parent_.tr("Create Notebook"), True, "notebook")
            dialog.set()
            ok, default, name, description = dialog.get()

            default = SETTINGS_OPTIONS[default]

        else:
            default = "default"

        if ok:
            if not self.parent_.maindb.checkIfItExists(name):
                try:
                    diary = bool(datetime.datetime.strptime(name, "%d.%m.%Y"))

                except ValueError:
                    diary = False

                if name == "":
                    QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                    return

                successful = self.parent_.maindb.createNotebook(
                    default, "enabled" if diary else default, description, name
                )

                if successful:
                    self.parent_.tree_view.appendNotebook(self.parent_.maindb.getNotebook(name))

                else:
                    QMessageBox.critical(
                        self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to create notebook.")
                    )

                self.parent_.setPage()

                return successful

            else:
                QMessageBox.critical(
                    self.parent_,
                    self.parent_.tr("Error"),
                    self.parent_.tr("{the_item} is already exists.")
                    .format(the_item=self.parent_.tr("the '{name}' notebook").format(name=name))
                    .capitalize(),
                )
                return False

    @Slot(QModelIndex)
    def delete(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.delete(name, table):
            self.unpin(index, False, False)  # because it is deleted

            # Also delete the notebook's documents.
            if index.data(ITEM_DATAS["type"]) == "notebook":
                for name_, table_ in self.parent_.maindb.items.copy():
                    if table_ == name:
                        for page in [
                            page
                            for page in self.parent_.parent_.area.pages
                            if page.document is not None
                            and page.document.index == self.parent_.maindb.items[(name_, table_)].index()
                        ]:
                            page.removeDocument()

                        self.unpin(
                            self.parent_.maindb.items[(name_, table_)].index(), False, False
                        )  # because it is deleted

                        del self.parent_.maindb.items[(name_, table_)]

                self.parent_.tree_view.model_.removeRow(index.row())

            elif index.data(ITEM_DATAS["type"]) == "document":
                page = self.parent_.getPageFromIndex(index)
                if page is not None:
                    page.removeDocument()

                self.parent_.maindb.items[(table, "__main__")].removeRow(index.row())

            del self.parent_.maindb.items[(name, table)]

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to delete {the_item}.", index))

        self.parent_.setPage()

    @Slot(QModelIndex)
    def editDescription(self, index: QModelIndex) -> None:
        name = index.data(ITEM_DATAS["name"])

        dialog = GetDescription(self.parent_, self.parent_.tr("Edit Description"))
        dialog.set()
        ok, description = dialog.get()

        if ok:
            if self.parent_.maindb.set(description, "content", name):
                index.model().setData(index, description, ITEM_DATAS["content"])

            else:
                QMessageBox.critical(
                    self.parent_, self.parent_.tr("Error"), self.tr("Failed to edit description {of_item}.", index)
                )

    @Slot(QModelIndex)
    def export(self, index: QModelIndex, export_: str | None = None) -> None:
        name, table = self.get(index)

        if export_ is None:
            ok, export = Export(self.parent_).get()

        else:
            ok = True
            export = export_

        if ok:
            if index.data(ITEM_DATAS["type"]) == "notebook":
                for name_, table_ in self.parent_.maindb.items:
                    if table_ == name:
                        self.export(
                            self.parent_.tree_view.mapFromSource(self.parent_.maindb.items[(name_, table_)].index()),
                            export,
                        )

            elif index.data(ITEM_DATAS["type"]) == "document":
                os.makedirs(
                    os.path.join(USER_DIRS[index.data(ITEM_DATAS["folder"])[1]], "Nottodbox", table),
                    exist_ok=True,
                )
                document = QTextDocument()
                setDocument(index.data(ITEM_DATAS["content"]), index.data(ITEM_DATAS["format"])[1], document)

                if export == "pdf":
                    writer = QPdfWriter(
                        os.path.join(USER_DIRS[index.data(ITEM_DATAS["folder"])[1]], "Nottodbox", table, f"{name}.pdf")
                    )
                    writer.setTitle(name)

                    document.print_(writer)

                elif export == "plain-text" or export == "markdown":
                    with open(
                        os.path.join(
                            USER_DIRS[index.data(ITEM_DATAS["folder"])[1]],
                            "Nottodbox",
                            table,
                            f"{name}.{'txt' if export == 'plain-text' else 'md'}",
                        ),
                        "w+",
                    ) as f:
                        f.write(document.toPlainText() if export == "plain-text" else document.toMarkdown())

                else:
                    export = index.data(ITEM_DATAS["format"])[1] if export == "format" else export

                    writer = QTextDocumentWriter(
                        os.path.join(
                            USER_DIRS[index.data(ITEM_DATAS["folder"])[1]],
                            "Nottodbox",
                            table,
                            f"{name}.{export}",
                        ),
                        export.encode("utf-8") if export != "odt" else b"odf",
                    )
                    writer.write(document)

            if export_ is None:
                QMessageBox.information(
                    self.parent_, self.parent_.tr("Successful"), self.tr("{the_item} exported.", index)
                )

    def get(self, index: QModelIndex) -> tuple[str, str]:
        """Get name with table/notebook name."""

        if index.data(ITEM_DATAS["type"]) == "notebook":
            return index.data(ITEM_DATAS["name"]), "__main__"

        elif index.data(ITEM_DATAS["type"]) == "document":
            return index.data(ITEM_DATAS["name"]), index.data(ITEM_DATAS["notebook"])

    @Slot(QModelIndex)
    def markAsCompleted(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set("completed", "completed", name, table):
            index.model().setData(index, ["self", "completed"], ITEM_DATAS["completed"])
            self.parent_.tree_view.setType(index)

        else:
            QMessageBox.critical(
                self.parent_, self.parent_.tr("Error"), self.tr("Failed to mark as completed {the_item}.", index)
            )

    @Slot(QModelIndex)
    def markAsUncompleted(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set("uncompleted", "completed", name, table):
            index.model().setData(index, ["self", "uncompleted"], ITEM_DATAS["completed"])
            self.parent_.tree_view.setType(index)

        else:
            QMessageBox.critical(
                self.parent_, self.parent_.tr("Error"), self.tr("Failed to mark as uncompleted {the_item}.", index)
            )

    @Slot(QModelIndex, str)
    def open(self, index: QModelIndex, mode: str, make: bool = False) -> None:
        if index != next(
            (
                page.document.index
                for page in self.parent_.parent_.area.pages
                if page.document is not None and page.document.index == index
            ),
            None,
        ):
            # Making clicked that QModelIndex, this is optional because sometime's already clicked.
            if make:
                index.model().setData(index, True, ITEM_DATAS["clicked"])

            self.parent_.parent_.area.target.addDocument(
                NormalView(self.parent_.parent_.area, self.parent_.maindb, index)
                if mode == "normal"
                else BackupView(self.parent_.parent_.area, self.parent_.maindb, index)
            )

    @Slot(QModelIndex)
    def pin(self, index: QModelIndex, write: bool = True, update: bool = True) -> None:
        if index not in self.parent_.parent_.parent_.sidebar.list_view.items:
            name, table = self.get(index)

            if write and not self.parent_.maindb.set("yes", "pinned", name, table):
                QMessageBox.critical(
                    self.parent_, self.parent_.tr("Error"), self.tr("Failed to pin {the_item} to sidebar.", index)
                )
                return

            if update:
                index.model().setData(index, ("self", "yes"), ITEM_DATAS["pinned"])

            self.parent_.parent_.parent_.sidebar.list_view.addItem(index)

            # Pin the documents that follow the notebook.
            if index.data(ITEM_DATAS["type"]) == "notebook":
                for name_, table_ in self.parent_.maindb.items.copy():
                    if (
                        table_ == name
                        and "notebook" in self.parent_.maindb.items[(name_, table_)].data(ITEM_DATAS["pinned"])[0]
                    ):
                        self.parent_.parent_.parent_.sidebar.list_view.addItem(
                            self.parent_.maindb.items[(name_, table_)].index()
                        )

    @Slot(QModelIndex)
    def removeLock(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set("disabled", "locked", name, table):
            index.model().setData(index, ["self", "disabled"], ITEM_DATAS["locked"])
            self.parent_.tree_view.setType(index)

            page = self.parent_.getPageFromIndex(index)
            if page is not None:
                page.document.refreshSettings()

            QMessageBox.information(
                self.parent_, self.parent_.tr("Successful"), self.tr("Lock removed {from_item}.", index)
            )

        else:
            QMessageBox.critical(
                self.parent_, self.parent_.tr("Error"), self.tr("Failed to remove lock {from_item}.", index)
            )

    @Slot(QModelIndex)
    def rename(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        dialog = GetName(self.parent_, self.parent_.tr("Rename"))
        dialog.set()
        ok, new_name = dialog.get()

        if ok:
            try:
                diary = bool(datetime.datetime.strptime(new_name, "%d.%m.%Y"))

            except ValueError:
                diary = False

            if new_name == "":
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                return

            if not self.parent_.maindb.checkIfItExists(new_name, table):
                if self.parent_.maindb.rename(
                    "enabled" if diary else self.parent_.maindb.get("locked", name, table), new_name, name, table
                ):
                    if diary == "enabled":
                        index.model().setData(index, ("self", "enabled"), ITEM_DATAS["locked"])

                    index.model().setData(index, new_name, ITEM_DATAS["name"])

                    if index.data(ITEM_DATAS["type"]) == "notebook":
                        for name_, table_ in self.parent_.maindb.items.copy():
                            if table_ == name:
                                self.parent_.maindb.items[(name_, table_)].setData(new_name, ITEM_DATAS["notebook"])

                                # Update the notebook's documents' datas.
                                for page in [
                                    page
                                    for page in self.parent_.parent_.area.pages
                                    if page.document is not None
                                    and page.document.index == self.parent_.maindb.items[(name_, table_)].index()
                                ]:
                                    page.document.refreshNames()

                                    if diary == "enabled":
                                        page.document.refreshSettings()

                                self.parent_.maindb.items[(name_, new_name)] = self.parent_.maindb.items.pop(
                                    (name_, table_)
                                )

                    elif index.data(ITEM_DATAS["type"]) == "document":
                        page = self.parent_.getPageFromIndex(index)
                        if page is not None:
                            page.document.refreshNames()

                        if diary == "enabled":
                            page.document.refreshSettings()

                    self.parent_.maindb.items[(new_name, table)] = self.parent_.maindb.items.pop((name, table))

                else:
                    QMessageBox.critical(
                        self.parent_, self.parent_.tr("Error"), self.tr("Failed to rename {the_item}.", index)
                    )

            else:
                QMessageBox.critical(
                    self.parent_, self.parent_.tr("Error"), self.tr("{the_item} is already exists.", index)
                )

    @Slot(QModelIndex)
    def reset(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.reset(name):
            for name_, table_ in self.parent_.maindb.items.copy():
                if table_ == name:
                    for page in [
                        page
                        for page in self.parent_.parent_.area.pages
                        if page.document is not None
                        and page.document.index == self.parent_.maindb.items[(name_, table_)].index()
                    ]:
                        page.removeDocument()

                    del self.parent_.maindb.items[(name_, table_)]

            self.parent_.maindb.items[(name, table)].removeRows(0, self.parent_.maindb.items[(name, table)].rowCount())

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to reset {the_item}.", index))

    @Slot(QModelIndex)
    def restoreContent(self, index: QModelIndex) -> None:
        document, notebook = self.get(index)

        if self.parent_.maindb.restoreContent(document, notebook):
            index.model().setData(index, self.parent_.maindb.getContent(document, notebook), ITEM_DATAS["content"])
            index.model().setData(index, self.parent_.maindb.getBackup(document, notebook), ITEM_DATAS["backup"])

            page = self.parent_.getPageFromIndex(index)
            if page is not None:
                page.document.refreshContent()

            QMessageBox.information(
                self.parent_, self.parent_.tr("Successful"), self.tr("The content {of_item} restored.", index)
            )

        else:
            QMessageBox.critical(
                self.parent_, self.parent_.tr("Error"), self.tr("Failed to restore content {of_item}.", index)
            )

    def tr(self, text_: str, index: QModelIndex) -> str:
        """Just being lazy, sometimes..."""

        name, table = self.get(index)

        if table == "__main__":
            if "{from_item}" in text_:
                text = text_.format(from_item=self.parent_.tr("from '{name}' notebook").format(name=name))

            elif "{of_item}" in text_:
                text = text_.format(of_item=self.parent_.tr("of '{name}' notebook").format(name=name))

            elif "{to_item}" in text_:
                text = text_.format(to_item=self.parent_.tr("to '{name}' notebook").format(name=name))

            elif "{the_item}" in text_:
                text = text_.format(the_item=self.parent_.tr("the '{name}' notebook").format(name=name))

        else:
            if "{from_item}" in text_:
                text = text_.format(from_item=self.parent_.tr("from '{name}' document").format(name=name))

            elif "{of_item}" in text_:
                text = text_.format(of_item=self.parent_.tr("of '{name}' document").format(name=name))

            elif "{to_item}" in text_:
                text = text_.format(to_item=self.parent_.tr("to '{name}' document").format(name=name))

            elif "{the_item}" in text_:
                text = text_.format(the_item=self.parent_.tr("the '{name}' document").format(name=name))

        return text.capitalize()

    @Slot(QModelIndex)
    def unmark(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set(None, "completed", name, table):
            index.model().setData(index, ["self", None], ITEM_DATAS["completed"])
            self.parent_.tree_view.setType(index)

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to unmark {the_item}.", index))

    @Slot(QModelIndex)
    def unpin(self, index: QModelIndex, write: bool = True, update: bool = True) -> None:
        if index in self.parent_.parent_.parent_.sidebar.list_view.items:
            name, table = self.get(index)

            if write and not self.parent_.maindb.set("no", "pinned", name, table):
                QMessageBox.critical(
                    self.parent_, self.parent_.tr("Error"), self.tr("Failed to unpin {the_item} from sidebar.", index)
                )
                return

            if update:
                index.model().setData(index, ("self", "no"), ITEM_DATAS["pinned"])

            self.parent_.parent_.parent_.sidebar.list_view.removeItem(index)

            # Unpin the documents that follow the notebook.
            if index.data(ITEM_DATAS["type"]) == "notebook":
                for name_, table_ in self.parent_.maindb.items.copy():
                    if (
                        table_ == name
                        and "notebook" in self.parent_.maindb.items[(name_, table_)].data(ITEM_DATAS["pinned"])[0]
                    ):
                        self.parent_.parent_.parent_.sidebar.list_view.removeItem(
                            self.parent_.maindb.items[(name_, table_)].index()
                        )


class TreeView(QTreeView):
    failed_to_import = Signal(QModelIndex)
    refresh_document = Signal(typing.Any)

    def __init__(self, parent: Selector):
        super().__init__(parent)

        self.parent_ = parent

        self.buttons = [
            PushButton(parent.buttons, lambda: self.filterType(0), self.tr("Notes"), True, True),
            PushButton(parent.buttons, lambda: self.filterType(1), self.tr("To-dos"), True, True),
            PushButton(parent.buttons, lambda: self.filterType(2), self.tr("Diaries"), True, True),
        ]

        self.types = ["note", "todo", "diary"]

        self.model_ = QStandardItemModel(self)

        self.model_.setHorizontalHeaderLabels([self.tr("Name")])

        self.type_filterer = QSortFilterProxyModel(self)
        self.type_filterer.setSourceModel(self.model_)
        self.type_filterer.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.type_filterer.setRecursiveFilteringEnabled(True)
        self.type_filterer.setFilterRole(ITEM_DATAS["type_2"])

        self.normal_filterer = QSortFilterProxyModel(self)
        self.normal_filterer.setSourceModel(self.type_filterer)
        self.normal_filterer.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.normal_filterer.setRecursiveFilteringEnabled(True)
        self.normal_filterer.setFilterRole(ITEM_DATAS["name"])

        self.delegate = ButtonDelegate(self)

        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setItemDelegate(self.delegate)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setModel(self.normal_filterer)

        self.failed_to_import.connect(self.failedToImport)
        self.refresh_document.connect(self.refreshDocument)
        self.delegate.menu_requested.connect(self.openMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def appendAll(self) -> None:
        items = self.parent_.maindb.getAll()

        self.importer = Importer(self)
        self.importer_thread = QThread()
        self.importer.moveToThread(self.importer_thread)
        self.importer_thread.start()
        self.importer.import_all.connect(self.importer.importAll)

        if items != []:
            self.parent_.pages.setCurrentIndex(1)

        for data in items:
            self.appendNotebook(data)

        # Pin pinned items to sidebar after startup.
        for item in self.parent_.maindb.items.values():
            if item.data(ITEM_DATAS["pinned"])[1] == "yes":
                self.parent_.options.pin(item.index(), False, False)

        self.importer.import_all.emit()

    def appendDocument(self, data: list, item: QStandardItem, notebook: str) -> None:
        document = QStandardItem()
        self.parent_.maindb.items[(data[len(data) - 5], notebook)] = document

        document.setData(False, ITEM_DATAS["clicked"])
        document.setData("document", ITEM_DATAS["type"])

        document.setData(self.setCurrentIndex, ITEM_DATAS["setCurrentIndex"])
        document.setData(self.parent_.options.open, ITEM_DATAS["open"])

        document.setData(notebook, ITEM_DATAS["notebook"])
        for i in range(5):
            document.setData(data[len(data) - 1 - i], ITEM_DATAS["backup"] - i)

        for i in range(16):
            document.setData(self.handleSetting(document, i, data[1 + i]), ITEM_DATAS["completed"] + i)

        self.setType(document)

        item.appendRow(document)

    def appendNotebook(self, data: list) -> None:
        notebook = QStandardItem()
        self.parent_.maindb.items[(data[len(data) - 5], "__main__")] = notebook

        notebook.setData(False, ITEM_DATAS["clicked"])
        notebook.setData("notebook", ITEM_DATAS["type"])

        notebook.setData(self.setCurrentIndex, ITEM_DATAS["setCurrentIndex"])
        notebook.setData(self.parent_.options.open, ITEM_DATAS["open"])

        notebook.setData("__main__", ITEM_DATAS["notebook"])
        for i in range(5):
            notebook.setData(data[len(data) - 1 - i], ITEM_DATAS["backup"] - i)

        for i in range(16):
            notebook.setData(self.handleSetting(notebook, i, data[2 + i]), ITEM_DATAS["completed"] + i)

        for data_ in data[0]:
            self.appendDocument(data_, notebook, data[len(data) - 5])

        self.setType(notebook)

        self.model_.appendRow(notebook)

    @Slot(QModelIndex)
    def failedToImport(self, index: QModelIndex) -> None:
        QMessageBox.critical(self, self.tr("Error"), self.parent_.options.tr("{the_item} exported.", index))

    @Slot(int)
    def filterChanged(self, index: int) -> None:
        self.normal_filterer.setFilterRole(ITEM_DATAS["name"] + index)

    @Slot(str)
    def filterNormal(self, text: str) -> None:
        self.normal_filterer.beginResetModel()
        self.normal_filterer.setFilterFixedString(text)
        self.normal_filterer.endResetModel()

    @Slot(int)
    def filterType(self, index: int) -> None:
        if self.buttons[index].isChecked():
            buttons = self.buttons.copy()
            del buttons[index]

            for button in buttons:
                button.setChecked(False)

        self.type_filterer.beginResetModel()
        self.type_filterer.setFilterFixedString(self.types[index] if self.buttons[index].isChecked() else "")
        self.type_filterer.endResetModel()

    def handleSettingViaGlobal(self, number: int) -> str | None:
        """Check whether it follows the default and return the actual setting."""

        if self.parent_.settings.value(f"globals/{SETTINGS_KEYS[number]}") == "default":
            return SETTINGS_DEFAULTS[number]

        else:
            return self.parent_.settings.value(f"globals/{SETTINGS_KEYS[number]}")

    def handleSettingViaNotebook(self, item: QStandardItem, number: int) -> str | None:
        """Check whether it follows the default or global setting and return the actual setting."""

        if (
            self.parent_.maindb.items[(item.data(ITEM_DATAS["notebook"]), "__main__")].data(
                ITEM_DATAS["completed"] + number
            )[0][0]
            == "default"
        ):
            return SETTINGS_DEFAULTS[number]

        else:
            return self.parent_.maindb.items[(item.data(ITEM_DATAS["notebook"]), "__main__")].data(
                ITEM_DATAS["completed"] + number
            )[1]

    def handleSetting(self, item: QStandardItem, number: int, value: str | None) -> tuple[tuple, str | None]:
        """Check whether it follows the default or global setting or notebook and return the type with actual setting."""

        if value == "default":
            return ("default",), SETTINGS_DEFAULTS[number]

        elif value == "global":
            return ("global",), self.handleSettingViaGlobal(number)

        elif value == "notebook":
            if (
                self.parent_.maindb.items[(item.data(ITEM_DATAS["notebook"]), "__main__")].data(
                    ITEM_DATAS["completed"] + number
                )[0][0]
                == "global"
            ):
                return (
                    "notebook",
                    "global",
                ), self.handleSettingViaGlobal(number)

            else:
                return ("notebook",), self.handleSettingViaNotebook(item, number)

        else:
            return ("self",), value

    def mapFromSource(self, index: QModelIndex) -> QModelIndex:
        return self.normal_filterer.mapFromSource(self.type_filterer.mapFromSource(index))

    def mapToSource(self, index: QModelIndex) -> QModelIndex:
        return self.type_filterer.mapToSource(self.normal_filterer.mapToSource(index))

    @Slot(QPoint or QModelIndex)
    def openMenu(self, context_data: QPoint | QModelIndex) -> None:
        index = None

        if isinstance(context_data, QModelIndex):
            index = context_data

            global_pos = self.viewport().mapToGlobal(self.visualRect(index).bottomRight())
            global_pos.setX(global_pos.x() - 23)
            global_pos.setY(global_pos.y() - 46)

        elif isinstance(context_data, QPoint):
            index = self.indexAt(context_data)

            global_pos = self.viewport().mapToGlobal(context_data)

        if not index or not index.isValid():
            return

        index = self.mapToSource(index)

        menu = QMenu()
        menu.addAction(Action(self, lambda: self.parent_.options.createDocument(index), self.tr("Create Document")))
        menu.addAction(Action(self, lambda: self.parent_.options.createNotebook(), self.tr("Create Notebook")))

        menu.addSeparator()
        if index.data(ITEM_DATAS["type"]) == "notebook":
            menu.addAction(
                Action(self, lambda: self.parent_.options.editDescription(index), self.tr("Edit Description"))
            )

        elif index.data(ITEM_DATAS["type"]) == "document":
            menu.addAction(Action(self, lambda: self.parent_.options.open(index, "normal", True), self.tr("Open")))
            menu.addAction(
                Action(self, lambda: self.parent_.options.open(index, "backup", True), self.tr("Show Backup"))
            )
            menu.addAction(Action(self, lambda: self.parent_.options.restoreContent(index), self.tr("Restore Content")))
            menu.addAction(Action(self, lambda: self.parent_.options.clearContent(index), self.tr("Clear Content")))

        menu.addSeparator()
        if index.data(ITEM_DATAS["completed"])[1] == "completed":
            menu.addAction(
                Action(self, lambda: self.parent_.options.markAsUncompleted(index), self.tr("Mark as Uncompleted"))
            )
            menu.addAction(Action(self, lambda: self.parent_.options.unmark(index), self.tr("Unmark")))

        elif index.data(ITEM_DATAS["completed"])[1] == "uncompleted":
            menu.addAction(
                Action(self, lambda: self.parent_.options.markAsCompleted(index), self.tr("Mark as Completed"))
            )
            menu.addAction(Action(self, lambda: self.parent_.options.unmark(index), self.tr("Unmark")))

        else:
            menu.addAction(
                Action(self, lambda: self.parent_.options.markAsCompleted(index), self.tr("Mark as Completed"))
            )
            menu.addAction(
                Action(self, lambda: self.parent_.options.markAsUncompleted(index), self.tr("Mark as Uncompleted"))
            )

        menu.addSeparator()
        if index.data(ITEM_DATAS["locked"])[1] == "enabled":
            menu.addAction(Action(self, lambda: self.parent_.options.removeLock(index), self.tr("Remove Lock")))
        elif index.data(ITEM_DATAS["locked"])[1] == "disabled":
            menu.addAction(Action(self, lambda: self.parent_.options.addLock(index), self.tr("Add Lock")))

        menu.addSeparator()
        if index.data(ITEM_DATAS["pinned"])[1] == "yes":
            menu.addAction(Action(self, lambda: self.parent_.options.unpin(index), self.tr("Unpin from sidebar")))
        elif index.data(ITEM_DATAS["pinned"])[1] == "no":
            menu.addAction(Action(self, lambda: self.parent_.options.pin(index), self.tr("Pin to sidebar")))

        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.parent_.options.export(index), self.tr("Export")))

        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.parent_.options.rename(index), self.tr("Rename")))
        menu.addAction(Action(self, lambda: self.parent_.options.delete(index), self.tr("Delete")))
        if index.data(ITEM_DATAS["type"]) == "notebook":
            menu.addAction(Action(self, lambda: self.parent_.options.reset(index), self.tr("Reset")))

        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.parent_.options.changeAppearance(index), self.tr("Change Appearance")))
        menu.addAction(Action(self, lambda: self.parent_.options.changeSettings(index), self.tr("Change Settings")))

        page = self.parent_.getPageFromIndex(index)

        if index.data(ITEM_DATAS["type"]) == "document" and page is not None:
            menu.addSeparator()
            menu.addAction(Action(self, page.removeDocument, self.tr("Close")))

        menu.exec(global_pos)

    @Slot(typing.Any)
    def refreshDocument(self, page: typing.Any) -> None:
        page.document.refreshContent()

    @Slot(QModelIndex)
    def setCurrentIndex(self, index: QModelIndex) -> None:
        return super().setCurrentIndex(self.mapFromSource(index))

    def setData(self, context_data: QModelIndex | QStandardItem, value: str, role: Qt.ItemDataRole) -> None:
        if isinstance(context_data, QModelIndex):
            context_data.model().setData(context_data, value, role)

        elif isinstance(context_data, QStandardItem):
            context_data.setData(value, role)

    def setType(self, context_data: QModelIndex | QStandardItem) -> None:
        """Set document type by "completed" and "locked" columns."""

        if (
            context_data.data(ITEM_DATAS["completed"])[1] is None
            and context_data.data(ITEM_DATAS["locked"])[1] == "disabled"
        ):
            self.setData(context_data, "note", ITEM_DATAS["type_2"])

        elif (
            context_data.data(ITEM_DATAS["completed"])[1] in ["completed", "uncompleted"]
            and context_data.data(ITEM_DATAS["locked"])[1] == "enabled"
        ):
            self.setData(context_data, "todo diary", ITEM_DATAS["type_2"])

        elif context_data.data(ITEM_DATAS["completed"])[1] in ["completed", "uncompleted"]:
            self.setData(context_data, "todo", ITEM_DATAS["type_2"])

        elif context_data.data(ITEM_DATAS["locked"])[1] == "enabled":
            self.setData(context_data, "diary", ITEM_DATAS["type_2"])


class Importer(QObject):
    import_all = Signal()
    import_file = Signal(str)

    def __init__(self, parent: TreeView) -> None:
        super().__init__()

        self.parent_ = parent

        self.import_file.connect(self.importFile)
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.import_file.emit)

    def importAll(self) -> None:
        for item in self.parent_.parent_.maindb.items.values():
            if item.data(ITEM_DATAS["sync"])[1] is not None:
                sync = item.data(ITEM_DATAS["sync"])[1].removesuffix("_all").removesuffix("_import")
                file = os.path.join(
                    USER_DIRS[item.data(ITEM_DATAS["folder"])[1]],
                    "Nottodbox",
                    item.data(ITEM_DATAS["notebook"]),
                    f"{item.data(ITEM_DATAS['name'])}.{'txt' if sync == 'plain-text' else 'md'}",
                )

                if item.data(ITEM_DATAS["sync"])[1].endswith("_all") or item.data(ITEM_DATAS["sync"])[1].endswith(
                    "_import"
                ):
                    self.watcher.addPath(file)

                    if os.path.isfile(file):
                        db_date = datetime.datetime.strptime(item.data(ITEM_DATAS["modification"]), "%d.%m.%Y %H:%M")
                        file_date = datetime.datetime.fromtimestamp(os.path.getmtime(file))

                        if file_date > db_date:
                            self.importDocument(file, item)

    def importDocument(self, file: str, item: QStandardItem) -> None:
        page = self.parent_.parent_.getPageFromIndex(item.index())

        if (
            page is None
            or page.document.last_content == page.document.getText()
            and QApplication.activeWindow() is None
            and os.path.isfile(file)
        ):
            with open(file) as f:
                input_ = QTextDocument()

                if os.path.splitext(file)[1] == ".md":
                    input_.setMarkdown(f.read())

                elif os.path.splitext(file)[1] == ".txt":
                    input_.setPlainText(f.read())

                if item.data(ITEM_DATAS["format"])[1] == "markdown":
                    content = input_.toMarkdown()

                elif item.data(ITEM_DATAS["format"])[1] == "html":
                    content = input_.toHtml()

                elif item.data(ITEM_DATAS["format"])[1] == "plain-text":
                    content = input_.toPlainText()

                if content != item.data(ITEM_DATAS["content"]):
                    if self.parent_.parent_.maindb.saveDocument(
                        content,
                        item.data(ITEM_DATAS["content"]),
                        False,
                        item.data(ITEM_DATAS["name"]),
                        item.data(ITEM_DATAS["notebook"]),
                    ):
                        item.setData(item.data(ITEM_DATAS["content"]), ITEM_DATAS["backup"])
                        item.setData(content, ITEM_DATAS["content"])

                        page = self.parent_.parent_.getPageFromIndex(item.index())
                        if page is not None:
                            page.document.last_content = content
                            self.parent_.refresh_document.emit(page)

                    else:
                        self.parent_.failed_to_import.emit(item.index())

    def importFile(self, file: str) -> None:
        item = self.parent_.parent_.maindb.items[tuple(reversed(os.path.splitext(file)[0].split("/")[-2:]))]

        if item.data(ITEM_DATAS["sync"])[1].endswith("_all") or item.data(ITEM_DATAS["sync"])[1].endswith("_import"):
            sync = item.data(ITEM_DATAS["sync"])[1].removesuffix("_all").removesuffix("_import")

            if file == os.path.join(
                USER_DIRS[item.data(ITEM_DATAS["folder"])[1]],
                "Nottodbox",
                item.data(ITEM_DATAS["notebook"]),
                f"{item.data(ITEM_DATAS['name'])}.{'txt' if sync == 'plain-text' else 'md'}",
            ):
                self.importDocument(file, item)


class ButtonDelegate(QStyledItemDelegate):
    menu_requested = Signal(QModelIndex)

    dot_size = 4
    dot_padding = 8
    button_size = 24

    def __init__(self, parent: TreeView) -> None:
        super().__init__(parent)

        self.parent_ = parent

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()

        name = index.data(ITEM_DATAS["name"])

        if index.data(ITEM_DATAS["completed"])[1] == "completed":
            name = f"[+] {name}"

        elif index.data(ITEM_DATAS["completed"])[1] == "uncompleted":
            name = f"[-] {name}"

        name_font = QFont(option.font)
        name_font.setWeight(QFont.Weight.Bold)
        name_fontmetrics = QFontMetrics(name_font)
        name_padding = name_fontmetrics.lineSpacing()

        name_rect = QRect(option.rect)
        name_rect.setLeft(name_rect.left() + name_padding)
        name_rect.setTop(name_rect.top() + name_padding)
        name_rect.setRight(option.rect.width())
        name_rect.setHeight(name_fontmetrics.lineSpacing())

        content = index.data(ITEM_DATAS["content"])

        content_rect = QRect(option.rect)
        content_rect.setLeft(content_rect.left() + name_padding)
        content_rect.setTop(name_rect.bottom() + name_padding / 2)
        content_rect.setRight(
            option.rect.width() + (name_padding if index.data(ITEM_DATAS["type"]) == "document" else 0) - 10
        )
        content_rect.setHeight(name_fontmetrics.lineSpacing())

        creation_date = index.data(ITEM_DATAS["creation"])

        creation_rect = QRect(option.rect)
        creation_rect.setLeft(creation_rect.left() + name_padding)
        creation_rect.setTop(content_rect.bottom() + name_padding / 2)
        creation_rect.setRight(
            QFontMetrics(QFont(option.font)).horizontalAdvance(creation_date) + creation_rect.left() + name_padding
        )
        creation_rect.setHeight(name_fontmetrics.lineSpacing())

        modification_date = index.data(ITEM_DATAS["modification"])

        modification_rect = QRect(option.rect)
        modification_rect.setLeft(
            option.rect.width()
            - QFontMetrics(QFont(option.font)).horizontalAdvance(modification_date)
            + (name_padding if index.data(ITEM_DATAS["type"]) == "document" else 0)
        )
        modification_rect.setTop(content_rect.bottom() + name_padding / 2)
        modification_rect.setRight(
            option.rect.width() + (name_padding if index.data(ITEM_DATAS["type"]) == "document" else 0)
        )
        modification_rect.setHeight(name_fontmetrics.lineSpacing())

        painter.save()

        border_rect = QRect(option.rect.marginsRemoved(QMargins(10, 10, 10, 10)))

        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, 10, 10)

        # mouse clicked, mouse hovered and other
        situations = [
            bool(index.data(ITEM_DATAS["clicked"]) and index.data(ITEM_DATAS["type"]) == "document"),
            bool(option.state & QStyle.StateFlag.State_MouseOver),
            True,
        ]

        # default colors of background, foreground and border
        defaults = [
            [option.palette.base().color(), option.palette.text().color(), option.palette.text().color()],
            [option.palette.button().color(), option.palette.text().color(), option.palette.buttonText().color()],
            [option.palette.link().color(), option.palette.text().color(), option.palette.linkVisited().color()],
        ]

        colors = []

        # We must use an inverse loop for the QModelIndex data to match the “situations” variable.
        i = 2

        # A loop from the most specific situation (clicked) to the general situation (other).
        for status in situations:
            if status:
                for j in range(3):
                    if index.data(ITEM_DATAS["bg_normal"] + j * 3 + i)[1] is None:
                        colors.append(defaults[i][j])

                    else:
                        colors.append(QColor(index.data(ITEM_DATAS["bg_normal"] + j * 3 + i)[1]))

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

        painter.drawText(name_rect, name_fontmetrics.elidedText(name, Qt.TextElideMode.ElideRight, name_rect.width()))

        painter.setFont(option.font)

        painter.drawText(
            content_rect,
            QFontMetrics(QFont(option.font)).elidedText(content, Qt.TextElideMode.ElideRight, content_rect.width()),
        )
        painter.drawText(creation_rect, creation_date)
        painter.drawText(modification_rect, modification_date)

        painter.restore()
        painter.save()

        painter.setPen(colors[2])
        painter.setBrush(colors[1])

        button_rect = self.getButtonRect(option)
        center_y = button_rect.center().y()
        center_x = button_rect.center().x()

        painter.drawEllipse(
            center_x - self.dot_size / 2, center_y - self.dot_padding - self.dot_size / 2, self.dot_size, self.dot_size
        )
        painter.drawEllipse(center_x - self.dot_size / 2, center_y - self.dot_size / 2, self.dot_size, self.dot_size)
        painter.drawEllipse(
            center_x - self.dot_size / 2, center_y + self.dot_padding - self.dot_size / 2, self.dot_size, self.dot_size
        )

        painter.restore()

    def editorEvent(
        self, event: QEvent, model: QStandardItemModel, option: QStyleOptionViewItem, index: QModelIndex
    ) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            button_rect = self.getButtonRect(option)

            if event.button() == Qt.MouseButton.LeftButton:
                # Open the menu.
                if button_rect.contains(event.position().toPoint()):
                    self.menu_requested.emit(index)
                    return True

                # Open the document.
                elif index.data(ITEM_DATAS["type"]) == "document":
                    self.parent_.parent_.options.open(self.parent_.mapToSource(index), "normal")

                model.setData(index, not index.data(ITEM_DATAS["clicked"]), ITEM_DATAS["clicked"])

        return super().editorEvent(event, model, option, index)

    def getButtonRect(self, option: QStyleOptionViewItem) -> QRect:
        return QRect(
            option.rect.topRight().x() - self.button_size - 10,
            option.rect.topRight().y(),
            self.button_size,
            option.rect.height(),
        )

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QRect:
        return QSize(option.rect.width(), 108)
