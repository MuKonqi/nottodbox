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

from PySide6.QtCore import (
    QEvent,
    QMargins,
    QModelIndex,
    QPoint,
    QRect,
    QSettings,
    QSize,
    QSortFilterProxyModel,
    Qt,
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
    QTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from .consts import SETTINGS_DEFAULTS, SETTINGS_KEYS, SETTINGS_OPTIONS, SETTINGS_VALUES, USER_DIRS
from .database import MainDB
from .widgets.controls import Action, CalendarWidget, HSeperator, Label, LineEdit, PushButton, VSeperator
from .widgets.dialogs import ChangeAppearance, ChangeSettings, Export, GetDescription, GetName, GetNameAndDescription
from .widgets.documents import BackupView, NormalView


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

    def __init__(self, parent: HomePage)-> None:
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

        self.target = self.pages[0]
        self.target.setAsTarget()


class Page(QWidget):
    document = None

    def __init__(self, parent: Area) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.pager = QStackedWidget(self)

        self.container = QWidget(self.pager)

        self.button = PushButton(self.container, self.setAsTarget, self.tr("Click this button\nto select a document for here"), False, True)
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
        self.pager.setCurrentIndex(1),

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
        self.filter_combobox.addItems([self.tr("By name"), self.tr("By creation date"), self.tr("By modification date"), self.tr("By content / description")])
        self.filter_combobox.currentIndexChanged.connect(self.tree_view.filterChanged)

        self.calendar_widget = CalendarWidget(self)
        self.calendar_widget.selectionChanged.connect(self.selectedDateChanged)

        self.calendar_checkbox = QCheckBox(self)
        self.calendar_checkbox.setText(self.tr("Calendar"))
        try:
            self.calendar_checkbox.checkStateChanged.connect(self.enableCalendar)
        except AttributeError:
            self.calendar_checkbox.stateChanged.connect(self.enableCalendar)
        self.calendar_checkbox.setCheckState(Qt.CheckState.Unchecked if self.settings.value("selector/calendar") == "hidden" else Qt.CheckState.Checked)

        self.create_first_notebook = CreateFirstNotebook(self)

        self.buttons_layout = QHBoxLayout(self.buttons)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget(self)
        self.container_layout = QGridLayout(self.container)

        self.pages = QStackedWidget(self)
        self.pages.addWidget(self.create_first_notebook)
        self.pages.addWidget(self.container)

        for button in self.tree_view.buttons:
            self.buttons_layout.addWidget(button)

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

        self.tree_view.appendAll()

        self.setFixedWidth(330)
        self.enableCalendar(Qt.CheckState.Unchecked if self.settings.value("selector/calendar") == "hidden" else Qt.CheckState.Checked)
        self.setPage()
        self.setVisible(False if self.settings.value("selector/self") == "hidden" else True)
        self.parent_.parent_.sidebar.buttons[-1].setChecked(True if self.settings.value("selector/self") == "hidden" else False)

    @Slot(int or Qt.CheckState)
    def enableCalendar(self, signal: int | Qt.CheckState) -> None:
        if not self.do_not_write:
            self.settings.setValue("selector/calendar", "hidden" if signal == Qt.CheckState.Unchecked or signal == 0 else "visible")

        self.calendar_widget.setVisible(False if signal == Qt.CheckState.Unchecked or signal == 0 else True)

    def setPage(self) -> None:
        if self.tree_view.model_.rowCount() == 0:
            self.do_not_write = True
            self.calendar_checkbox.setCheckState(Qt.CheckState.Checked)
            self.do_not_write = False

            self.pages.setCurrentIndex(0)

        else:
            self.do_not_write = True
            self.calendar_checkbox.setCheckState(Qt.CheckState.Unchecked if self.settings.value("selector/calendar") == "hidden" else Qt.CheckState.Checked)
            self.do_not_write = False

            self.pages.setCurrentIndex(1)

    @Slot()
    def selectedDateChanged(self) -> None:
        if self.pages.currentIndex() == 0:
            self.create_first_notebook.name.setText(self.calendar_widget.selectedDate().toString("dd/MM/yyyy"))

        elif self.pages.currentIndex() == 1:
            self.search_entry.setText(self.calendar_widget.selectedDate().toString("dd/MM/yyyy"))

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
        self.name.setText(self.parent_.calendar_widget.selectedDate().toString("dd/MM/yyyy"))

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
            index.model().setData(index, ["self", "enabled"], Qt.ItemDataRole.UserRole + 21)
            self.parent_.tree_view.setType(index)

            for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
                page.document.refreshSettings()

            QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.tr("Lock added {to_item}.", index))

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to add lock {to_item}.", index))

    @Slot(QModelIndex)
    def changeAppearance(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        ok, values = ChangeAppearance(self.parent_, self.parent_.maindb, index).get()

        if ok:
            successful = True

            for i in range(9):
                if self.parent_.maindb.set(values[i], SETTINGS_KEYS[7 + i], name, table):
                    index.model().setData(index, self.parent_.tree_view.handleSetting(self.parent_.maindb.items[(name, table)], 7 + i, values[i]), Qt.ItemDataRole.UserRole + 27 + i)

                    if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                        for name_, table_ in self.parent_.maindb.items.keys():
                            if table_ == name and "notebook" in self.parent_.maindb.items[(name_, table_)].data(Qt.ItemDataRole.UserRole + 27 + i)[0]:
                                self.parent_.maindb.items[(name_, table_)].setData(self.parent_.tree_view.handleSetting(self.parent_.maindb.items[(name_, table_)], 7 + i, "notebook"), Qt.ItemDataRole.UserRole + 27 + i)

                else:
                    successful = False

            if successful:
                QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.tr("New appearance applied {to_item}.", index))

            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to apply new appearance {to_item}.", index))

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
                    index.model().setData(index, self.parent_.tree_view.handleSetting(self.parent_.maindb.items[(name, table)], i, options[values[i]]), Qt.ItemDataRole.UserRole + 20 + i)

                    for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
                        page.document.refreshSettings()

                    if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                        for name_, table_ in self.parent_.maindb.items.keys():
                            if table_ == name and "notebook" in self.parent_.maindb.items[(name_, table_)].data(Qt.ItemDataRole.UserRole + 20 + i)[0]:
                                self.parent_.maindb.items[(name_, table_)].setData(self.parent_.tree_view.handleSetting(self.parent_.maindb.items[(name_, table_)], i, "notebook"), Qt.ItemDataRole.UserRole + 20 + i)

                                for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == self.parent_.maindb.items[(name_, table_)].index()]:
                                    page.document.refreshSettings()

                    if i == 6:
                        if options[values[i]] == "yes":
                            self.pin(index, False, False)

                        elif options[values[i]] == "no":
                            self.unpin(index, False, False)

                else:
                    successful = False

            if successful:
                QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.tr("New settings applied {to_item}.", index))

            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to apply new settings {to_item}.", index))

    @Slot(QModelIndex)
    def clearContent(self, index: QModelIndex) -> None:
        document = index.data(Qt.ItemDataRole.UserRole + 101)
        notebook = index.data(Qt.ItemDataRole.UserRole + 100)

        if self.parent_.maindb.clearContent(document, notebook):
            index.model().setData(index, "", Qt.ItemDataRole.UserRole + 104)
            index.model().setData(index, self.parent_.maindb.getBackup(document, notebook), Qt.ItemDataRole.UserRole + 105)

            for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
                page.document.refreshContent()

            QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.tr("The content {of_item} cleared.", index))

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to clear the content {of_item}.", index))

    @Slot(QModelIndex)
    def close(self, index: QModelIndex) -> None:
        for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
            if page.document.mode == "normal" and not page.document.last_content == page.document.getText():
                self.question = QMessageBox.question(
                    self.parent_, self.parent_.tr("Question"), self.tr("{the_item} not saved.\nWhat would you like to do?", index),
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Save)

                if self.question == QMessageBox.StandardButton.Save:
                    if not page.document.saver.saveDocument():
                        return

                elif self.question != QMessageBox.StandardButton.Discard:
                    return

            index.model().setData(index, False, Qt.ItemDataRole.UserRole + 1)

            if page.document.mode == "normal":
                page.document.changeAutosaveConnections("disconnect")

            if index in self.parent_.parent_.parent_.sidebar.list_view.items.keys():
                self.parent_.parent_.parent_.sidebar.list_view.items[index].setData(False, Qt.ItemDataRole.UserRole + 1)

    @Slot(QModelIndex)
    def createDocument(self, index: QModelIndex) -> None:
        dialog = GetName(self.parent_, self.parent_.tr("Create Document"), True, "document")
        dialog.set()
        ok, default, document = dialog.get()

        options = SETTINGS_OPTIONS.copy()
        options.append("notebook")

        default = options[default]

        if ok:
            if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                notebook = index.data(Qt.ItemDataRole.UserRole + 101)

            elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                notebook = index.data(Qt.ItemDataRole.UserRole + 100)

            if not self.parent_.maindb.checkIfItExists(document, notebook):
                try:
                    diary = bool(datetime.datetime.strptime(document, "%d/%m/%Y"))

                except ValueError:
                    diary = False

                if document == "":
                    QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                    return

                if self.parent_.maindb.createDocument(default, "enabled" if diary else default, document, notebook):
                    self.parent_.tree_view.appendDocument(self.parent_.maindb.getDocument(document, notebook), self.parent_.maindb.items[(notebook, "__main__")], notebook)

                    if self.parent_.maindb.items[(document, notebook)].data(Qt.ItemDataRole.UserRole + 26)[1] == "yes":
                        self.pin(self.parent_.maindb.items[(document, notebook)].index(), False, False)

                else:
                    QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to create document."))

            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"),
                                     self.parent_.tr("{the_item} is already exists.").format(the_item = self.parent_.tr("the '{name}' document").format(name = document)).capitalize())

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
                    diary = bool(datetime.datetime.strptime(name, "%d/%m/%Y"))

                except ValueError:
                    diary = False

                if name == "":
                    QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                    return

                successful = self.parent_.maindb.createNotebook(default, "enabled" if diary else default, description, name)

                if successful:
                    self.parent_.tree_view.appendNotebook(self.parent_.maindb.getNotebook(name))

                else:
                    QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("Failed to create notebook."))

                self.parent_.setPage()

                return successful

            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"),
                                     self.parent_.tr("{the_item} is already exists.").format(the_item = self.parent_.tr("the '{name}' notebook").format(name = name)).capitalize())
                return False

    @Slot(QModelIndex)
    def delete(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.delete(name, table):
            self.unpin(index, False, False)

            if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                for name_, table_ in self.parent_.maindb.items.copy().keys():
                    if table_ == name:
                        for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == self.parent_.maindb.items[(name_, table_)].index()]:
                            page.removeDocument()

                        self.unpin(self.parent_.maindb.items[(name_, table_)].index(), False, False)

                        del self.parent_.maindb.items[(name_, table_)]

                self.parent_.tree_view.model_.removeRow(index.row())

            elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
                    page.removeDocument()

                self.parent_.maindb.items[(table, "__main__")].removeRow(index.row())

            del self.parent_.maindb.items[(name, table)]

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to delete {the_item}.", index))

        self.parent_.setPage()

    @Slot(QModelIndex)
    def editDescription(self, index: QModelIndex) -> None:
        name = index.data(Qt.ItemDataRole.UserRole + 101)

        dialog = GetDescription(self.parent_, self.parent_.tr("Edit Description"))
        dialog.set()
        ok, description = dialog.get()

        if ok:
            if self.parent_.maindb.set(description, "content", name):
                index.model().setData(index, description, Qt.ItemDataRole.UserRole + 104)

            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to edit description {of_item}.", index))

    @Slot(QModelIndex)
    def export(self, index: QModelIndex, export_: str | None = None) -> None:
        name, table = self.get(index)

        if export_ is None:
            ok, export = Export(self.parent_).get()

        else:
            ok = True
            export = export_

        if ok:
            if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                for name_, table_ in self.parent_.maindb.items.keys():
                    if table_ == name:
                        self.export(self.parent_.tree_view.mapFromSource(self.parent_.maindb.items[(name_, table_)].index()), export)

            elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                os.makedirs(os.path.join(USER_DIRS[index.data(Qt.ItemDataRole.UserRole + 25)[1]], "Nottodbox", table), exist_ok=True)

                input = QTextEdit(index.data(Qt.ItemDataRole.UserRole + 104))

                if index.data(Qt.ItemDataRole.UserRole + 23)[1] == "markdown":
                    content = input.toMarkdown()

                elif index.data(Qt.ItemDataRole.UserRole + 23)[1] == "html":
                    content = input.toHtml()

                elif index.data(Qt.ItemDataRole.UserRole + 23)[1] == "plain-text":
                    content = input.toPlainText()

                input.deleteLater()

                if export == "pdf":
                    writer = QPdfWriter(os.path.join(USER_DIRS[index.data(Qt.ItemDataRole.UserRole + 25)[1]], "Nottodbox", table, f"{name}.pdf"))
                    writer.setTitle(name)

                    document = QTextDocument(content)
                    document.print_(writer)

                elif export == "plain-text" or (export == "format" and index.data(Qt.ItemDataRole.UserRole + 23)[1] == "plain-text"):
                    with open(os.path.join(USER_DIRS[index.data(Qt.ItemDataRole.UserRole + 25)[1]], "Nottodbox", table, f"{name}.txt"), "w+") as f:
                        f.write(content)

                else:
                    export = index.data(Qt.ItemDataRole.UserRole + 23)[1] if export == "format" else export

                    document = QTextDocument(content)

                    writer = QTextDocumentWriter(os.path.join(USER_DIRS[index.data(Qt.ItemDataRole.UserRole + 25)[1]], "Nottodbox", table, f"{name}.{export}"), export.encode("utf-8") if export != "odt" else b"odf")
                    writer.write(document)

            if export_ is None:
                QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.tr("{the_item} exported.", index))

    def get(self, index: QModelIndex) -> tuple[str, str]:
        if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
            return index.data(Qt.ItemDataRole.UserRole + 101), "__main__"

        elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
            return index.data(Qt.ItemDataRole.UserRole + 101), index.data(Qt.ItemDataRole.UserRole + 100)

    @Slot(QModelIndex)
    def markAsCompleted(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set("completed", "completed", name, table):
            index.model().setData(index, ["self", "completed"], Qt.ItemDataRole.UserRole + 20)
            self.parent_.tree_view.setType(index)

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to mark as completed {the_item}.", index))

    @Slot(QModelIndex)
    def markAsUncompleted(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set("uncompleted", "completed", name, table):
            index.model().setData(index, ["self", "uncompleted"], Qt.ItemDataRole.UserRole + 20)
            self.parent_.tree_view.setType(index)

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to mark as uncompleted {the_item}.", index))

    @Slot(QModelIndex, str)
    def open(self, index: QModelIndex, mode: str, make: bool = False) -> None:
        if index not in [page.document.index for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
            if make:
                index.model().setData(index, True, Qt.ItemDataRole.UserRole + 1)

            self.parent_.parent_.area.target.addDocument(NormalView(self.parent_.parent_.area, self.parent_.maindb, index) if mode == "normal" else BackupView(self.parent_.parent_.area, self.parent_.maindb, index))

    @Slot(QModelIndex)
    def pin(self, index: QModelIndex, write: bool = True, update: bool = True) -> None:
        if index not in self.parent_.parent_.parent_.sidebar.list_view.items.keys():
            name, table = self.get(index)

            if write and not self.parent_.maindb.set("yes", "pinned", name, table):
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to pin {the_item} to sidebar.", index))
                return

            if update:
                index.model().setData(index, ("self", "yes"), Qt.ItemDataRole.UserRole + 26)

            self.parent_.parent_.parent_.sidebar.list_view.addItem(index)

            if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                for name_, table_ in self.parent_.maindb.items.copy().keys():
                    if table_ == name and "notebook" in self.parent_.maindb.items[(name_, table_)].data(Qt.ItemDataRole.UserRole + 26)[0]:
                        self.parent_.parent_.parent_.sidebar.list_view.addItem(self.parent_.maindb.items[(name_, table_)].index())

    @Slot(QModelIndex)
    def removeLock(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set("disabled", "locked", name, table):
            index.model().setData(index, ["self", "disabled"], Qt.ItemDataRole.UserRole + 21)
            self.parent_.tree_view.setType(index)

            for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
                page.document.refreshSettings()

            QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.tr("Lock removed {from_item}.", index))

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to remove lock {from_item}.", index))

    @Slot(QModelIndex)
    def rename(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        dialog = GetName(self.parent_, self.parent_.tr("Rename"))
        dialog.set()
        ok, new_name = dialog.get()

        if ok:
            try:
                diary = bool(datetime.datetime.strptime(new_name, "%d/%m/%Y"))

            except ValueError:
                diary = False

            if new_name == "":
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.parent_.tr("A name is required."))
                return

            if not self.parent_.maindb.checkIfItExists(new_name, table):
                if self.parent_.maindb.rename("enabled" if diary else self.parent_.maindb.get("locked", name, table), new_name, name, table):
                    if diary == "enabled":
                        index.model().setData(index, ("self", "enabled"), Qt.ItemDataRole.UserRole + 21)

                    index.model().setData(index, new_name, Qt.ItemDataRole.UserRole + 101)

                    if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                        for name_, table_ in self.parent_.maindb.items.copy().keys():
                            if table_ == name:
                                self.parent_.maindb.items[(name_, table_)].setData(new_name, Qt.ItemDataRole.UserRole + 100)

                                for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == self.parent_.maindb.items[(name_, table_)].index()]:
                                    page.document.refreshNames()

                                    if diary == "enabled":
                                        page.document.refreshSettings()

                                self.parent_.maindb.items[(name_, new_name)] = self.parent_.maindb.items.pop((name_, table_))

                    elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                        for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
                            page.document.refreshNames()

                        if diary == "enabled":
                            page.document.refreshSettings()

                    self.parent_.maindb.items[(new_name, table)] = self.parent_.maindb.items.pop((name, table))

                else:
                    QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to rename {the_item}.", index))

            else:
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("{the_item} is already exists.", index))

    @Slot(QModelIndex)
    def reset(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.reset(name):
            for name_, table_ in self.parent_.maindb.items.copy().keys():
                if table_ == name:
                    for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == self.parent_.maindb.items[(name_, table_)].index()]:
                        page.removeDocument()

                    del self.parent_.maindb.items[(name_, table_)]

            self.parent_.maindb.items[(name, table)].removeRows(0, self.parent_.maindb.items[(name, table)].rowCount())

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to reset {the_item}.", index))

    @Slot(QModelIndex)
    def restoreContent(self, index: QModelIndex) -> None:
        document, notebook = self.get(index)

        if self.parent_.maindb.restoreContent(document, notebook):
            index.model().setData(index, self.parent_.maindb.getContent(document, notebook), Qt.ItemDataRole.UserRole + 104)
            index.model().setData(index, self.parent_.maindb.getBackup(document, notebook), Qt.ItemDataRole.UserRole + 105)

            for page in [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]:
                page.document.refreshContent()

            QMessageBox.information(self.parent_, self.parent_.tr("Successful"), self.tr("The content {of_item} restored.", index))

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to restore content {of_item}.", index))

    def tr(self, text_: str, index: QModelIndex) -> str:
        name, table = self.get(index)

        if table == "__main__":
            if "{from_item}" in text_:
                text = text_.format(from_item = self.parent_.tr("from '{name}' notebook").format(name = name))

            elif "{of_item}" in text_:
                text = text_.format(of_item = self.parent_.tr("of '{name}' notebook").format(name = name))

            elif "{to_item}" in text_:
                text = text_.format(to_item = self.parent_.tr("to '{name}' notebook").format(name = name))

            elif "{the_item}" in text_:
                text = text_.format(the_item = self.parent_.tr("the '{name}' notebook").format(name = name))

        else:
            if "{from_item}" in text_:
                text = text_.format(from_item = self.parent_.tr("from '{name}' document").format(name = name))

            elif "{of_item}" in text_:
                text = text_.format(of_item = self.parent_.tr("of '{name}' document").format(name = name))

            elif "{to_item}" in text_:
                text = text_.format(to_item = self.parent_.tr("to '{name}' document").format(name = name))

            elif "{the_item}" in text_:
                text = text_.format(the_item = self.parent_.tr("the '{name}' document").format(name = name))

        return text.capitalize()

    @Slot(QModelIndex)
    def unmark(self, index: QModelIndex) -> None:
        name, table = self.get(index)

        if self.parent_.maindb.set(None, "completed", name, table):
            index.model().setData(index, ["self", None], Qt.ItemDataRole.UserRole + 20)
            self.parent_.tree_view.setType(index)

        else:
            QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to unmark {the_item}.", index))

    @Slot(QModelIndex)
    def unpin(self, index: QModelIndex, write: bool = True, update: bool = True) -> None:
        if index in self.parent_.parent_.parent_.sidebar.list_view.items.keys():
            name, table = self.get(index)

            if write and not self.parent_.maindb.set("no", "pinned", name, table):
                QMessageBox.critical(self.parent_, self.parent_.tr("Error"), self.tr("Failed to unpin {the_item} from sidebar.", index))
                return

            if update:
                index.model().setData(index, ("self", "no"), Qt.ItemDataRole.UserRole + 26)

            self.parent_.parent_.parent_.sidebar.list_view.removeItem(index)

            if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
                for name_, table_ in self.parent_.maindb.items.copy().keys():
                    if table_ == name and "notebook" in self.parent_.maindb.items[(name_, table_)].data(Qt.ItemDataRole.UserRole + 26)[0]:
                        self.parent_.parent_.parent_.sidebar.list_view.removeItem(self.parent_.maindb.items[(name_, table_)].index())


class TreeView(QTreeView):
    def __init__(self, parent: Selector):
        super().__init__(parent)

        self.parent_ = parent

        self.buttons = [
            PushButton(parent.buttons, lambda: self.filterType(0), self.tr("Notes"), True, True),
            PushButton(parent.buttons, lambda: self.filterType(1), self.tr("To-dos"), True, True),
            PushButton(parent.buttons, lambda: self.filterType(2), self.tr("Diaries"), True, True)
            ]

        self.types = ["note", "todo", "diary"]

        self.model_ = QStandardItemModel(self)

        self.model_.setHorizontalHeaderLabels([self.tr("Name")])

        self.type_filterer = QSortFilterProxyModel(self)
        self.type_filterer.setSourceModel(self.model_)
        self.type_filterer.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.type_filterer.setRecursiveFilteringEnabled(True)
        self.type_filterer.setFilterRole(Qt.ItemDataRole.UserRole + 3)

        self.normal_filterer = QSortFilterProxyModel(self)
        self.normal_filterer.setSourceModel(self.type_filterer)
        self.normal_filterer.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.normal_filterer.setRecursiveFilteringEnabled(True)
        self.normal_filterer.setFilterRole(Qt.ItemDataRole.UserRole + 101)

        self.delegate = ButtonDelegate(self)

        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setItemDelegate(self.delegate)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setModel(self.normal_filterer)

        self.delegate.menu_requested.connect(self.openMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def appendAll(self) -> None:
        items = self.parent_.maindb.getAll()

        if items != []:
            self.parent_.pages.setCurrentIndex(1)

        for data in items:
            self.appendNotebook(data)

        for item in self.parent_.maindb.items.values():
            if item.data(Qt.ItemDataRole.UserRole + 26)[1] == "yes":
                self.parent_.options.pin(item.index(), False, False)

    def appendDocument(self, data: list, item: QStandardItem, notebook: str) -> None:
        document = QStandardItem()
        self.parent_.maindb.items[(data[len(data) - 5], notebook)] = document

        document.setData(False, Qt.ItemDataRole.UserRole + 1)
        document.setData("document", Qt.ItemDataRole.UserRole + 2)

        document.setData(self.setCurrentIndex, Qt.ItemDataRole.UserRole + 10)
        document.setData(self.parent_.options.open, Qt.ItemDataRole.UserRole + 11)

        document.setData(notebook, Qt.ItemDataRole.UserRole + 100)
        for i in range(5):
            document.setData(data[len(data) - 1 - i], Qt.ItemDataRole.UserRole + 105 - i)

        for i in range(16):
            document.setData(self.handleSetting(document, i, data[1 + i]), Qt.ItemDataRole.UserRole + 20 + i)

        self.setType(document)

        item.appendRow(document)

    def appendNotebook(self, data: list) -> None:
        notebook = QStandardItem()
        self.parent_.maindb.items[(data[len(data) - 5], "__main__")] = notebook

        notebook.setData(False, Qt.ItemDataRole.UserRole + 1)
        notebook.setData("notebook", Qt.ItemDataRole.UserRole + 2)

        notebook.setData(self.setCurrentIndex, Qt.ItemDataRole.UserRole + 10)
        notebook.setData(self.parent_.options.open, Qt.ItemDataRole.UserRole + 11)

        for i in range(5):
            notebook.setData(data[len(data) - 1 - i], Qt.ItemDataRole.UserRole + 105 - i)

        for i in range(16):
            notebook.setData(self.handleSetting(notebook, i, data[2 + i]), Qt.ItemDataRole.UserRole + 20 + i)

        for data_ in data[0]:
            self.appendDocument(data_, notebook, data[len(data) - 5])

        self.setType(notebook)

        self.model_.appendRow(notebook)

    @Slot(int)
    def filterChanged(self, index: int) -> None:
        self.normal_filterer.setFilterRole(Qt.ItemDataRole.UserRole + 101 + index)

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
        if self.parent_.settings.value(f"globals/{SETTINGS_KEYS[number]}") == "default":
            return SETTINGS_DEFAULTS[number]

        else:
            return self.parent_.settings.value(f"globals/{SETTINGS_KEYS[number]}")

    def handleSettingViaNotebook(self, item: QStandardItem, number: int) -> str | None:
        if self.parent_.maindb.items[(item.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + number)[0][0] == "default":
            return SETTINGS_DEFAULTS[number]

        else:
            return self.parent_.maindb.items[(item.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + number)[1]

    def handleSetting(self, item: QStandardItem, number: int, value: str | None) -> tuple[tuple, str | None]:
        if value == "default":
            return ("default",), SETTINGS_DEFAULTS[number]

        elif value == "global":
            return ("global",), self.handleSettingViaGlobal(number)

        elif value == "notebook":
            if self.parent_.maindb.items[(item.data(Qt.ItemDataRole.UserRole + 100), "__main__")].data(Qt.ItemDataRole.UserRole + 20 + number)[0][0] == "global":
                return ("notebook", "global",), self.handleSettingViaGlobal(number)

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
        if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
            menu.addAction(Action(self, lambda: self.parent_.options.editDescription(index), self.tr("Edit Description")))

        elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
            menu.addAction(Action(self, lambda: self.parent_.options.open(index, "normal", True), self.tr("Open")))
            menu.addAction(Action(self, lambda: self.parent_.options.open(index, "backup", True), self.tr("Show Backup")))
            menu.addAction(Action(self, lambda: self.parent_.options.restoreContent(index), self.tr("Restore Content")))
            menu.addAction(Action(self, lambda: self.parent_.options.clearContent(index), self.tr("Clear Content")))

        menu.addSeparator()
        if index.data(Qt.ItemDataRole.UserRole + 20)[1] == "completed":
            menu.addAction(Action(self, lambda: self.parent_.options.markAsUncompleted(index), self.tr("Mark as Uncompleted")))
            menu.addAction(Action(self, lambda: self.parent_.options.unmark(index), self.tr("Unmark")))

        elif index.data(Qt.ItemDataRole.UserRole + 20)[1] == "uncompleted":
            menu.addAction(Action(self, lambda: self.parent_.options.markAsCompleted(index), self.tr("Mark as Completed")))
            menu.addAction(Action(self, lambda: self.parent_.options.unmark(index), self.tr("Unmark")))

        else:
            menu.addAction(Action(self, lambda: self.parent_.options.markAsCompleted(index), self.tr("Mark as Completed")))
            menu.addAction(Action(self, lambda: self.parent_.options.markAsUncompleted(index), self.tr("Mark as Uncompleted")))

        menu.addSeparator()
        if index.data(Qt.ItemDataRole.UserRole + 21)[1] == "enabled":
            menu.addAction(Action(self, lambda: self.parent_.options.removeLock(index), self.tr("Remove Lock")))
        elif index.data(Qt.ItemDataRole.UserRole + 21)[1] == "disabled":
            menu.addAction(Action(self, lambda: self.parent_.options.addLock(index), self.tr("Add Lock")))

        menu.addSeparator()
        if index.data(Qt.ItemDataRole.UserRole + 26)[1] == "yes":
            menu.addAction(Action(self, lambda: self.parent_.options.unpin(index), self.tr("Unpin from sidebar")))
        elif index.data(Qt.ItemDataRole.UserRole + 26)[1] == "no":
            menu.addAction(Action(self, lambda: self.parent_.options.pin(index), self.tr("Pin to sidebar")))

        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.parent_.options.export(index), self.tr("Export")))

        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.parent_.options.rename(index), self.tr("Rename")))
        menu.addAction(Action(self, lambda: self.parent_.options.delete(index), self.tr("Delete")))
        if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
            menu.addAction(Action(self, lambda: self.parent_.options.reset(index), self.tr("Reset")))

        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.parent_.options.changeAppearance(index), self.tr("Change Appearance")))
        menu.addAction(Action(self, lambda: self.parent_.options.changeSettings(index), self.tr("Change Settings")))

        pages = [page for page in self.parent_.parent_.area.pages if page.document is not None and page.document.index == index]
        if index.data(Qt.ItemDataRole.UserRole + 2) == "document" and pages != []:
            menu.addSeparator()
            for page in pages:
                menu.addAction(Action(self, lambda: page.removeDocument(), self.tr("Close")))

        menu.exec(global_pos)

    @Slot(QModelIndex)
    def setCurrentIndex(self, index: QModelIndex) -> None:
        return super().setCurrentIndex(self.mapFromSource(index))

    def setData(self, context_data: QModelIndex | QStandardItem, value: str, role: Qt.ItemDataRole) -> None:
        if isinstance(context_data, QModelIndex):
            context_data.model().setData(context_data, value, role)

        elif isinstance(context_data, QStandardItem):
            context_data.setData(value, role)

    def setType(self, context_data: QModelIndex | QStandardItem) -> None:
        if context_data.data(Qt.ItemDataRole.UserRole + 20)[1] is None and context_data.data(Qt.ItemDataRole.UserRole + 21)[1] == "disabled":
            self.setData(context_data, "note", Qt.ItemDataRole.UserRole + 3)

        elif context_data.data(Qt.ItemDataRole.UserRole + 20)[1] in ["completed", "uncompleted"] and context_data.data(Qt.ItemDataRole.UserRole + 21)[1] == "enabled":
            self.setData(context_data, "todo diary", Qt.ItemDataRole.UserRole + 3)

        elif context_data.data(Qt.ItemDataRole.UserRole + 20)[1] in ["completed", "uncompleted"]:
            self.setData(context_data, "todo", Qt.ItemDataRole.UserRole + 3)

        elif context_data.data(Qt.ItemDataRole.UserRole + 21)[1] == "enabled":
            self.setData(context_data, "diary", Qt.ItemDataRole.UserRole + 3)


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

        name = index.data(Qt.ItemDataRole.UserRole + 101)

        if index.data(Qt.ItemDataRole.UserRole + 20)[1] == "completed":
            name = f"[+] {name}"

        elif index.data(Qt.ItemDataRole.UserRole + 20)[1] == "uncompleted":
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

        content = index.data(Qt.ItemDataRole.UserRole + 104)

        content_rect = QRect(option.rect)
        content_rect.setLeft(content_rect.left() + name_padding)
        content_rect.setTop(name_rect.bottom() + name_padding / 2)
        content_rect.setRight(option.rect.width() + (name_padding if index.data(Qt.ItemDataRole.UserRole + 2) == "document" else 0) - 10)
        content_rect.setHeight(name_fontmetrics.lineSpacing())

        creation_date = index.data(Qt.ItemDataRole.UserRole + 102)

        creation_rect = QRect(option.rect)
        creation_rect.setLeft(creation_rect.left() + name_padding)
        creation_rect.setTop(content_rect.bottom() + name_padding / 2)
        creation_rect.setRight(QFontMetrics(QFont(option.font)).horizontalAdvance(creation_date) + creation_rect.left() + name_padding)
        creation_rect.setHeight(name_fontmetrics.lineSpacing())

        modification_date = index.data(Qt.ItemDataRole.UserRole + 103)

        modification_rect = QRect(option.rect)
        modification_rect.setLeft(option.rect.width() - QFontMetrics(QFont(option.font)).horizontalAdvance(modification_date) + (name_padding if index.data(Qt.ItemDataRole.UserRole + 2) == "document" else 0))
        modification_rect.setTop(content_rect.bottom() + name_padding / 2)
        modification_rect.setRight(option.rect.width() + (name_padding if index.data(Qt.ItemDataRole.UserRole + 2) == "document" else 0))
        modification_rect.setHeight(name_fontmetrics.lineSpacing())

        painter.save()

        border_rect = QRect(option.rect.marginsRemoved(QMargins(10, 10, 10, 10)))

        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, 10, 10)

        situations = [
            bool(index.data(Qt.ItemDataRole.UserRole + 1) and index.data(Qt.ItemDataRole.UserRole + 2) == "document"),
            bool(option.state & QStyle.StateFlag.State_MouseOver),
            True
            ]

        defaults = [
            [option.palette.base().color(), option.palette.text().color(), option.palette.text().color()],
            [option.palette.button().color(), option.palette.text().color(), option.palette.buttonText().color()],
            [option.palette.link().color(), option.palette.text().color(), option.palette.linkVisited().color()]
            ]

        colors = []

        i = 2

        for status in situations:
            if status:
                for j in range(3):
                    if index.data(Qt.ItemDataRole.UserRole + 27 + j * 3 + i)[1] is None:
                        colors.append(defaults[i][j])

                    else:
                        colors.append(QColor(index.data(Qt.ItemDataRole.UserRole + 27 + j * 3 + i)[1]))

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

        painter.drawText(content_rect, QFontMetrics(QFont(option.font)).elidedText(content, Qt.TextElideMode.ElideRight, content_rect.width()))
        painter.drawText(creation_rect, creation_date)
        painter.drawText(modification_rect, modification_date)

        painter.restore()
        painter.save()

        painter.setPen(colors[2])
        painter.setBrush(colors[1])

        button_rect = self.getButtonRect(option)
        center_y = button_rect.center().y()
        center_x = button_rect.center().x()

        painter.drawEllipse(center_x - self.dot_size / 2, center_y - self.dot_padding - self.dot_size / 2, self.dot_size, self.dot_size)
        painter.drawEllipse(center_x - self.dot_size / 2, center_y - self.dot_size / 2, self.dot_size, self.dot_size)
        painter.drawEllipse(center_x - self.dot_size / 2, center_y + self.dot_padding - self.dot_size / 2, self.dot_size, self.dot_size)

        painter.restore()

    def editorEvent(self, event: QEvent, model: QStandardItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            button_rect = self.getButtonRect(option)

            if event.button() == Qt.MouseButton.LeftButton:
                if button_rect.contains(event.position().toPoint()):
                    self.menu_requested.emit(index)
                    return True

                elif index.data(Qt.ItemDataRole.UserRole + 2) == "document":
                    self.parent_.parent_.options.open(self.parent_.mapToSource(index), "normal")

                model.setData(index, not index.data(Qt.ItemDataRole.UserRole + 1), Qt.ItemDataRole.UserRole + 1)

        return super().editorEvent(event, model, option, index)

    def getButtonRect(self, option: QStyleOptionViewItem) -> QRect:
        return QRect(option.rect.topRight().x() - self.button_size - 10, option.rect.topRight().y(), self.button_size, option.rect.height())

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QRect:
        return QSize(option.rect.width(), 108)
