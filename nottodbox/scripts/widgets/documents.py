# SPDX-License-Identifier: GPL-3.0-or-later

# Credit: While making DocumentHelper class, <https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp> helped me as a referance.

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


import datetime
import json
import os

from PySide6.QtCore import (
    QDate,
    QEvent,
    QMargins,
    QModelIndex,
    QObject,
    QRect,
    QSize,
    QSortFilterProxyModel,
    Qt,
    QThread,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QDesktopServices,
    QFont,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPalette,
    QPdfWriter,
    QPen,
    QStandardItem,
    QStandardItemModel,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextDocumentWriter,
    QTextFormat,
    QTextLength,
    QTextListFormat,
    QTextTable,
    QTextTableFormat,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QListView,
    QMenu,
    QMessageBox,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionButton,
    QStyleOptionViewItem,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..consts import ITEM_DATAS, USER_DIRS
from .controls import Action, HSeperator, Label, LineEdit, PushButton
from .dialogs import GetColor, GetTwoNumber


class BackupView(QWidget):
    def __init__(self, parent: QWidget, container: QWidget, db, index: QModelIndex) -> None:
        super().__init__(parent)

        self.parent_ = parent
        self.container = container
        self.db = db
        self.index = index

        self.format = index.data(ITEM_DATAS["format"])[1]
        self.mode = "backup"

        self.header = QWidget(self)

        self.mode_label = Label(self.header, self.tr("Backup:"))
        self.mode_label.setFixedWidth(75)

        self.label = Label(self.header)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)

        self.close_button = PushButton(self.header, self.container.removeDocument, self.tr("Close"))
        self.close_button.setFixedWidth(75)

        self.listview = BackupListView(self)

        self.content_entry = LineEdit(self, self.tr("Filter by content..."))
        self.content_entry.textChanged.connect(self.listview.filterContent)

        self.creation_entry = LineEdit(self, self.tr("Filter by date..."))
        self.creation_entry.textChanged.connect(self.listview.filterDate)

        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.addWidget(self.mode_label)
        self.header_layout.addWidget(self.label)
        self.header_layout.addWidget(self.close_button)

        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(self.header)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.content_entry)
        self.layout_.addWidget(self.creation_entry)
        self.layout_.addWidget(self.listview)

        self.refreshContent()
        self.refreshNames()

    def refreshContent(self) -> None:
        self.listview.deleteAll()
        self.listview.appendAll()

    def refreshNames(self) -> None:
        self.document = self.index.data(ITEM_DATAS["name"])
        self.notebook = self.index.data(ITEM_DATAS["notebook"])

        self.label.setText(self.document)


class BackupListView(QListView):
    def __init__(self, parent: BackupView) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.items = {}

        self.model_ = QStandardItemModel(self)

        self.content_filterer = QSortFilterProxyModel(self)
        self.content_filterer.setSourceModel(self.model_)
        self.content_filterer.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.content_filterer.setRecursiveFilteringEnabled(True)
        self.content_filterer.setFilterRole(ITEM_DATAS["content"])

        self.date_filterer = QSortFilterProxyModel(self)
        self.date_filterer.setSourceModel(self.content_filterer)
        self.date_filterer.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.date_filterer.setRecursiveFilteringEnabled(True)
        self.date_filterer.setFilterRole(ITEM_DATAS["name"])

        self.delegate = BackupDelegate(self)
        self.delegate.clicked.connect(self.delegateClicked)

        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setItemDelegate(self.delegate)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setModel(self.date_filterer)
        self.setUniformItemSizes(False)

    def appendAll(self) -> None:
        backups = json.loads(self.parent_.index.data(ITEM_DATAS["backup"]))

        for date, content in backups.items():
            self.appendItem(date, content)

    def appendItem(self, date: str, content: str) -> None:
        self.items[date] = QStandardItem()

        self.items[date].setData(content, ITEM_DATAS["content"])
        self.items[date].setData(date, ITEM_DATAS["name"])

        self.model_.appendRow(self.items[date])

    def deleteAll(self) -> None:
        for date in self.items.copy():
            self.deleteItem(date)

    def deleteItem(self, date: str) -> None:
        self.model_.removeRow(self.items[date].row())

        del self.items[date]

    @Slot(QModelIndex, str)
    def delegateClicked(self, index: QModelIndex, operation: str) -> None:
        if operation == "restore":
            if self.parent_.db.restoreContent(
                index.data(ITEM_DATAS["name"]), self.parent_.document, self.parent_.notebook
            ):
                self.parent_.index.model().setData(
                    self.parent_.index,
                    self.parent_.db.getBackups(self.parent_.document, self.parent_.notebook),
                    ITEM_DATAS["backup"],
                )
                self.parent_.index.model().setData(
                    self.parent_.index,
                    self.parent_.db.getContent(self.parent_.document, self.parent_.notebook),
                    ITEM_DATAS["content"],
                )

                QMessageBox.information(
                    self,
                    self.tr("Successful"),
                    self.tr("The backup '{}' '{of_item}' restored.").format(
                        index.data(ITEM_DATAS["name"]),
                        of_item=self.tr("the {name} document").format(name=self.parent_.document),
                    ),
                )

                self.parent_.refreshContent()

            else:
                QMessageBox.critical(
                    self,
                    self.tr("Error"),
                    self.tr("Failed to restore '{}' backup of '{of_item}'.").format(
                        index.data(ITEM_DATAS["name"]),
                        of_item=self.tr("the {name} document").format(name=self.parent_.document),
                    ),
                )

        if operation == "delete":
            if self.parent_.db.deleteBackup(
                index.data(ITEM_DATAS["name"]), self.parent_.document, self.parent_.notebook
            ):
                self.parent_.index.model().setData(
                    self.parent_.index,
                    self.parent_.db.getBackups(self.parent_.document, self.parent_.notebook),
                    ITEM_DATAS["backup"],
                )

                QMessageBox.information(
                    self,
                    self.tr("Successful"),
                    self.tr("The '{}' backup '{of_item}' deleted.").format(
                        index.data(ITEM_DATAS["name"]),
                        of_item=self.tr("the {name} document").format(name=self.parent_.document),
                    ),
                )

                self.deleteItem(index.data(ITEM_DATAS["name"]))

            else:
                QMessageBox.critical(
                    self,
                    self.tr("Error"),
                    self.tr("Failed to delete '{}' backup of '{of_item}'.").format(
                        index.data(ITEM_DATAS["name"]),
                        of_item=self.tr("the {name} document").format(name=self.parent_.document),
                    ),
                )

    @Slot(str)
    def filterContent(self, text: str) -> None:
        self.content_filterer.beginResetModel()
        self.content_filterer.setFilterFixedString(text)
        self.content_filterer.endResetModel()

    @Slot(str)
    def filterDate(self, text: str) -> None:
        self.date_filterer.beginResetModel()
        self.date_filterer.setFilterFixedString(text)
        self.date_filterer.endResetModel()


class BackupDelegate(QStyledItemDelegate):
    clicked = Signal(QModelIndex, str)

    def __init__(self, parent: BackupListView) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.hovered_index = QModelIndex()
        self.hovered_button = None

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()

        name_font = QFont(option.font)
        name_font.setWeight(QFont.Weight.Bold)

        style = QApplication.style()

        option_restore = QStyleOptionButton()
        option_restore.rect = self.getButtonRects(option.rect)[0]
        option_restore.text = self.tr("Restore")
        option_restore.state = QStyle.State(QStyle.StateFlag.State_Enabled)
        if self.hovered_index == index and self.hovered_button == "restore":
            option_restore.state |= QStyle.StateFlag.State_MouseOver

        option_delete = QStyleOptionButton()
        option_delete.rect = self.getButtonRects(option.rect)[1]
        option_delete.text = self.tr("Delete")
        option_delete.state = QStyle.State(QStyle.StateFlag.State_Enabled)
        if self.hovered_index == index and self.hovered_button == "delete":
            option_delete.state |= QStyle.StateFlag.State_MouseOver

        text_document = QTextDocument()
        documentSetContent(index.data(ITEM_DATAS["content"]), self.parent_.parent_.format, text_document)

        border_rect = QRect(option.rect.marginsRemoved(QMargins(10, 10, 10, 10)))
        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, 10, 10)

        colors = [option.palette.base().color(), option.palette.text().color(), option.palette.text().color()]
        border_pen = QPen(colors[2], 5)

        painter.setPen(border_pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawPath(border_path)
        painter.fillPath(border_path, colors[0])

        painter.setPen(colors[1])
        painter.setFont(name_font)
        painter.drawText(
            QRect(option.rect.left() + 15, option.rect.top() + 10, option.rect.width() - 160, 40),
            self.tr("Date: {}").format(index.data(ITEM_DATAS["name"])),
            Qt.AlignmentFlag.AlignVCenter,
        )

        painter.restore()
        painter.save()

        style.drawControl(QStyle.ControlElement.CE_PushButton, option_restore, painter)
        style.drawControl(QStyle.ControlElement.CE_PushButton, option_delete, painter)

        text_document.setTextWidth(option.rect.adjusted(10, 50, -10, -10).width())
        painter.translate(option.rect.adjusted(10, 50, -10, -10).topLeft())
        text_document.drawContents(painter)

        painter.restore()

    def editorEvent(
        self, event: QEvent, model: QStandardItemModel, option: QStyleOptionViewItem, index: QModelIndex
    ) -> bool:
        restore_rect, delete_rect = self.getButtonRects(option.rect)
        pos = event.position().toPoint()

        if event.type() == QEvent.Type.MouseMove:
            new_hover_button = None
            if restore_rect.contains(pos):
                new_hover_button = "restore"
            elif delete_rect.contains(pos):
                new_hover_button = "delete"

            if self.hovered_button != new_hover_button or self.hovered_index != index:
                self.hovered_button = new_hover_button
                self.hovered_index = index
                self.parent_.update(index)
            return True

        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if restore_rect.contains(pos):
                self.clicked.emit(index, "restore")
                return True

            elif delete_rect.contains(pos):
                self.clicked.emit(index, "delete")
                return True

        return super().editorEvent(event, model, option, index)

    def getButtonRects(self, rect: QRect) -> tuple[QRect, QRect]:
        return QRect(rect.right() - 140 + QStyle.PM_DefaultFrameWidth / 2, rect.top() + 15, 60, 30), QRect(
            rect.right() - 75 + QStyle.PM_DefaultFrameWidth / 2, rect.top() + 15, 60, 30
        )

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        text_document = QTextDocument()
        text_document.setTextWidth(option.rect.adjusted(10, 50, -10, -10).width())
        documentSetContent(index.data(ITEM_DATAS["content"]), self.parent_.parent_.format, text_document)

        return QSize(option.rect.width(), text_document.size().height() + 60)


class DocumentView(QWidget):
    show_messages = Signal(bool)

    def __init__(self, parent: QWidget, container: QWidget, db, index: QModelIndex) -> None:
        super().__init__(parent)

        self.parent_ = parent
        self.container = container
        self.db = db
        self.index = index

        self.settings = {}
        self.connected = False
        self.mode = "normal"

        self.creation = index.data(ITEM_DATAS["creation"])

        self.today = QDate.currentDate()

        self.show_messages.connect(self.showMessages)

        self.saver_thread = QThread()

        self.saver = DocumentSaver(self)
        self.saver.save_document.connect(self.saver.saveDocument)
        self.saver.moveToThread(self.saver_thread)

        self.save = lambda: self.saver.save_document.emit(True)

        self.header = QWidget(self)

        self.mode_label = Label(self.header, self.tr("Document:"))
        self.mode_label.setFixedWidth(75)

        self.label = Label(self.header)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)

        self.close_button = PushButton(self.header, self.container.removeDocument, self.tr("Close"))
        self.close_button.setFixedWidth(75)

        self.input = DocumentTextEdit(self)
        self.input.setAcceptRichText(True)

        self.helper = DocumentHelper(self)
        self.helper.button.triggered.connect(lambda: self.saver.saveDocument())
        self.input.cursorPositionChanged.connect(self.helper.updateButtons)

        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.addWidget(self.mode_label)
        self.header_layout.addWidget(self.label)
        self.header_layout.addWidget(self.close_button)

        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(self.header)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.helper)
        self.layout_.addWidget(self.input)

        self.setSettings()
        self.setContent()
        self.refreshNames()
        self.changeAutosaveConnections()

        self.last_content = self.content

    def changeAutosaveConnections(self, event: str | None = None) -> None:
        if (
            self.settings["locked"] == "disabled"
            or datetime.datetime.strptime(self.creation, "%d.%m.%Y %H:%M:%S").date() == datetime.datetime.today().date()
        ) and ((self.settings["autosave"] == "enabled" and not self.connected) or event == "connect"):
            self.input.textChanged.connect(self.save)
            self.saver_thread.start()
            self.connected = True

        elif (
            self.settings["autosave"] == "disabled"
            or event == "disconnect"
            or (
                self.settings["locked"] == "enabled"
                and datetime.datetime.strptime(self.creation, "%d.%m.%Y %H:%M:%S").date()
                != datetime.datetime.today().date()
            )
        ):
            if self.connected:
                self.input.textChanged.disconnect(self.save)
            self.saver_thread.quit()
            self.connected = False

    def getText(self, format_: str | None = None) -> str:
        if format_ is None:
            format_ = self.settings["format"]

        if format_ == "plain-text":
            return self.input.toPlainText()

        elif format_ == "markdown":
            return self.input.toMarkdown()

        elif format_ == "html":
            return self.input.toHtml()

    def refreshContent(self) -> None:
        self.changeAutosaveConnections("disconnect")
        self.setContent()
        self.changeAutosaveConnections()

    def refreshSettings(self) -> None:
        self.setSettings()
        self.changeAutosaveConnections()

    def refreshNames(self) -> None:
        self.document = self.index.data(ITEM_DATAS["name"])
        self.notebook = self.index.data(ITEM_DATAS["notebook"])

        self.label.setText(self.document)
        self.input.setDocumentTitle(self.document)

    def setContent(self) -> None:
        self.content = self.index.data(ITEM_DATAS["content"])

        documentSetContent(self.content, self.settings["format"], self.input)

    def setSettings(self) -> None:
        """Get settings from QModelIndex's datas."""

        self.settings["autosave"] = self.index.data(ITEM_DATAS["autosave"])[1]
        self.settings["folder"] = self.index.data(ITEM_DATAS["folder"])[1]
        self.settings["format"] = self.index.data(ITEM_DATAS["format"])[1]
        self.settings["locked"] = self.index.data(ITEM_DATAS["locked"])[1]
        self.settings["sync"] = self.index.data(ITEM_DATAS["sync"])[1]

        # Update TextFormatter's status.
        self.helper.updateStatus(self.settings["format"])

    @Slot(bool)
    def showMessages(self, successful: bool) -> None:
        if successful:
            QMessageBox.information(self, self.tr("Successful"), self.tr("Document saved."))

        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to save document."))


class DocumentHelper(QToolBar):
    def __init__(self, parent: DocumentView) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.button = self.addAction(self.tr("Save") if self.parent_.mode == "normal" else self.tr("Restore Content"))
        self.button.setStatusTip(self.tr("Auto-saves do not change backups and disabled for outdated diaries."))

        self.bold_action = Action(self, self.setBold, self.tr("Bold"))
        self.bold_action.setCheckable(True)
        self.addAction(self.bold_action)

        self.italic_action = Action(self, self.setItalic, self.tr("Italic"))
        self.italic_action.setCheckable(True)
        self.addAction(self.italic_action)

        self.underline_action = Action(self, self.setUnderline, self.tr("Underline"))
        self.underline_action.setCheckable(True)
        self.addAction(self.underline_action)

        self.strikethrough_action = Action(self, self.setStrikeThrough, self.tr("Strike through"))
        self.strikethrough_action.setCheckable(True)
        self.addAction(self.strikethrough_action)

        self.addSeparator()

        self.header_menu = QMenu(self)
        self.header_button = QToolButton(self)
        self.header_button.setText(self.tr("Heading"))
        self.header_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.header_button.setMenu(self.header_menu)
        self.header_menu.addAction(self.tr("Basic text"), lambda: self.setHeadingLevel(0))
        self.header_menu.addAction(self.tr("Title"), lambda: self.setHeadingLevel(1))
        self.header_menu.addAction(self.tr("Subtitle"), lambda: self.setHeadingLevel(2))
        self.header_menu.addAction(self.tr("Section"), lambda: self.setHeadingLevel(3))
        self.header_menu.addAction(self.tr("Subsection"), lambda: self.setHeadingLevel(4))
        self.header_menu.addAction(self.tr("Paragraph"), lambda: self.setHeadingLevel(5))
        self.header_menu.addAction(self.tr("Subparagraph"), lambda: self.setHeadingLevel(6))
        self.addWidget(self.header_button)

        self.list_menu = QMenu(self)
        self.list_button = QToolButton(self)
        self.list_button.setText(self.tr("List"))
        self.list_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.list_button.setMenu(self.list_menu)

        self.list_menu.addAction(self.tr("Unordered"), lambda: self.setList(QTextListFormat.Style.ListDisc))
        self.list_menu.addAction(
            self.tr("Ordered with decimal numbers"), lambda: self.setList(QTextListFormat.Style.ListDecimal)
        )
        self.list_menu.addAction(
            self.tr("Ordered with lowercase letters"), lambda: self.setList(QTextListFormat.Style.ListLowerAlpha)
        )
        self.list_menu.addAction(
            self.tr("Ordered with uppercase letters"), lambda: self.setList(QTextListFormat.Style.ListUpperAlpha)
        )

        self.alignment_menu = QMenu(self)
        self.alignment_button = QToolButton(self)
        self.alignment_button.setText(self.tr("Alignment"))
        self.alignment_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.alignment_button.setMenu(self.alignment_menu)
        self.alignment_button.setStatusTip(self.tr("Setting alignment is only available in HTML format."))
        self.addWidget(self.list_button)

        self.alignment_menu.addAction(self.tr("Left"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignLeft))
        self.alignment_menu.addAction(self.tr("Center"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignCenter))
        self.alignment_menu.addAction(self.tr("Right"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignRight))
        self.alignment_menu.setStatusTip(self.tr("Setting alignment is only available in HTML format."))
        self.addWidget(self.alignment_button)

        self.addSeparator()

        self.addAction(self.tr("Table"), self.setTable)

        self.addAction(self.tr("Link"), self.setLink)

        self.text_color = self.addAction(self.tr("Text color"), self.setTextColor)
        self.text_color.setStatusTip(self.tr("Setting text color is only available in HTML format."))

        self.background_color = self.addAction(self.tr("Background color"), self.setBackgroundColor)
        self.background_color.setStatusTip(self.tr("Setting background color is only available in HTML format."))

        self.fixTable()

    def fixTable(self, element: QTextTable = None) -> None:
        if isinstance(element, QTextTable):
            self.fixTableBase(element)

        else:
            for frame in self.parent_.input.document().rootFrame().childFrames():
                if isinstance(frame, QTextTable):
                    self.fixTableBase(frame)

    def fixTableBase(self, table: QTextTable) -> None:
        table_format = QTextTableFormat()
        table_format.setBorder(1)

        constraints = []

        for i in range(0, table.columns()):  # noqa: B007
            constraints.append(QTextLength(QTextLength.Type.PercentageLength, 100 / table.columns()))

        table_format.setColumnWidthConstraints(constraints)
        table_format.setCellSpacing(0)
        table_format.setCellPadding(2.5)
        table_format.setBorder(5)

        for row in range(0, table.rows()):
            for column in range(0, table.columns()):
                cell = table.cellAt(row, column)

                if cell.isValid():
                    cell.firstCursorPosition().insertText("|")

        table.setFormat(table_format)

    def mergeFormat(self, cur: QTextCursor, format_: QTextCharFormat) -> None:
        if not cur.hasSelection():
            cur.select(QTextCursor.SelectionType.WordUnderCursor)

        cur.mergeCharFormat(format_)

    def setBackgroundColor(self) -> None:
        ok, status, qcolor = GetColor(
            self, True, False, False, Qt.GlobalColor.white, self.tr("Select {} Color").format(self.tr("Background"))
        ).getColor()

        if ok:
            if status == "new":
                color = qcolor

            elif status == "default":
                color = QTextCharFormat().background()

            cur = self.parent_.input.textCursor()

            chrfmt = cur.charFormat()

            chrfmt.setBackground(color)

            self.mergeFormat(cur, chrfmt)

    @Slot()
    def setBold(self) -> None:
        cur = self.parent_.input.textCursor()
        chrfmt = cur.charFormat()

        if chrfmt.fontWeight() == 700:
            chrfmt.setFontWeight(400)
        elif chrfmt.fontWeight() == 400:
            chrfmt.setFontWeight(700)

        self.mergeFormat(cur, chrfmt)

    def setHeadingLevel(self, level: int) -> None:
        cur = self.parent_.input.textCursor()
        cur.beginEditBlock()

        blkfmt = QTextBlockFormat()
        blkfmt.setHeadingLevel(level)
        cur.mergeBlockFormat(blkfmt)

        chrfmt = QTextCharFormat()
        chrfmt.setFontWeight(400 if level == 0 else 700)
        chrfmt.setProperty(QTextFormat.Property.FontSizeAdjustment, 5 - level if level > 0 else 0)

        sel_cur = cur

        if sel_cur.hasSelection():
            top = sel_cur
            top.setPosition(min(top.anchor(), top.position()))
            top.movePosition(QTextCursor.MoveOperation.StartOfBlock)

            bottom = sel_cur
            bottom.setPosition(max(bottom.anchor(), bottom.position()))
            bottom.movePosition(QTextCursor.MoveOperation.EndOfBlock)

            sel_cur.setPosition(top.position(), QTextCursor.MoveMode.MoveAnchor)
            sel_cur.setPosition(bottom.position(), QTextCursor.MoveMode.KeepAnchor)

        else:
            sel_cur.select(QTextCursor.SelectionType.BlockUnderCursor)

        sel_cur.mergeCharFormat(chrfmt)

        cur.mergeBlockCharFormat(chrfmt)
        cur.endEditBlock()

    @Slot()
    def setItalic(self) -> None:
        cur = self.parent_.input.textCursor()
        chrfmt = cur.charFormat()

        if chrfmt.fontItalic():
            chrfmt.setFontItalic(False)
        else:
            chrfmt.setFontItalic(True)

        self.mergeFormat(cur, chrfmt)

    def setLink(self) -> None:
        status, text, url = GetTwoNumber(
            self,
            self.tr("Add Link"),
            "text",
            self.tr("Link text:"),
            self.tr("Link URL:"),
            self.tr("Not required"),
            self.tr("Required"),
        ).getResult()

        if status == "ok":
            if url != "" and url is not None:
                cur = self.parent_.input.textCursor()
                cur.beginEditBlock()

                chrfmt = cur.charFormat()
                chrfmt.setAnchor(True)
                chrfmt.setAnchorHref(url)
                chrfmt.setForeground(QApplication.palette().color(QPalette.ColorRole.Link))

                if text == "" or text is None:
                    text = url

                cur.insertText(text, chrfmt)
                cur.endEditBlock()

            else:
                QMessageBox.critical(self, self.tr("Error"), self.tr("The URL is required, it can not be blank."))

    def setList(self, style: QTextListFormat.Style) -> None:
        cur = self.parent_.input.textCursor()
        cur.insertList(style)

    @Slot()
    def setStrikeThrough(self) -> None:
        cur = self.parent_.input.textCursor()
        chrfmt = cur.charFormat()

        if chrfmt.fontStrikeOut():
            chrfmt.setFontStrikeOut(False)
        else:
            chrfmt.setFontStrikeOut(True)

        self.mergeFormat(cur, chrfmt)

    def setTable(self) -> None:
        status, rows, columns = GetTwoNumber(
            self, self.tr("Add Table"), "number", self.tr("Row number:"), self.tr("Column number:"), 1, 1
        ).getResult()

        if status == "ok":
            if rows is not None and columns is not None:
                cur = self.parent_.input.textCursor()

                self.fixTable(cur.insertTable(rows, columns))

            else:
                QMessageBox.critical(
                    self, self.tr("Error"), self.tr("The row and column numbers are required, they can not be blank.")
                )

    def setTextColor(self) -> None:
        ok, status, qcolor = GetColor(
            self, True, False, False, Qt.GlobalColor.white, self.tr("Select {} Color").format(self.tr("Text"))
        ).getColor()

        if ok:
            if status == "new":
                color = qcolor

            elif status == "default":
                color = QTextCharFormat().foreground()

            cur = self.parent_.input.textCursor()

            chrfmt = cur.charFormat()

            chrfmt.setForeground(color)

            self.mergeFormat(cur, chrfmt)

    @Slot()
    def setUnderline(self) -> None:
        cur = self.parent_.input.textCursor()
        chrfmt = cur.charFormat()

        if chrfmt.fontUnderline():
            chrfmt.setFontUnderline(False)
        else:
            chrfmt.setFontUnderline(True)

        self.mergeFormat(cur, chrfmt)

    @Slot()
    def updateButtons(self) -> None:
        cur = self.parent_.input.textCursor()
        chrfmt = cur.charFormat()

        if chrfmt.fontWeight() == 700:
            self.bold_action.setChecked(True)
        elif chrfmt.fontWeight() == 400:
            self.bold_action.setChecked(False)

        if chrfmt.fontItalic():
            self.italic_action.setChecked(True)
        else:
            self.italic_action.setChecked(False)

        if chrfmt.fontUnderline():
            self.underline_action.setChecked(True)
        else:
            self.underline_action.setChecked(False)

        if chrfmt.fontStrikeOut():
            self.strikethrough_action.setChecked(True)
        else:
            self.strikethrough_action.setChecked(False)

    def updateStatus(self, format_: str) -> None:
        if self.parent_.mode == "normal":
            if format_ == "plain-text":
                actions = self.actions()
                actions.pop(actions.index(self.button))

                for action in actions:
                    action.setEnabled(False)

                (self.setStatusTip(self.tr("Text formatter is only available in Markdown and HTML formats.")),)

            elif format_ == "markdown":
                for action in self.actions():
                    action.setEnabled(True)

                self.alignment_menu.setEnabled(False)
                self.alignment_button.setEnabled(False)
                self.text_color.setEnabled(False)
                self.background_color.setEnabled(False)

            elif format_ == "html":
                for action in self.actions():
                    action.setEnabled(True)

                self.alignment_menu.setEnabled(True)
                self.alignment_button.setEnabled(True)
                self.text_color.setEnabled(True)
                self.background_color.setEnabled(True)

        elif self.parent_.mode == "backup":
            actions = self.actions()
            actions.pop(actions.index(self.button))

            for action in actions:
                action.setEnabled(False)

            self.setStatusTip(self.tr("Text formatter is not available for backups."))


class DocumentSaver(QObject):
    save_document = Signal(bool)

    def __init__(self, parent: DocumentView) -> None:
        super().__init__()

        self.parent_ = parent

    @Slot(bool)
    def saveDocument(self, autosave: bool = False) -> bool:
        if not autosave or (autosave and self.parent_.settings["autosave"] == "enabled"):
            if (
                self.parent_.settings["locked"] == "enabled"
                and datetime.datetime.strptime(self.parent_.creation, "%d.%m.%Y %H:%M:%S").date()
                != datetime.datetime.today().date()
            ):
                if autosave:
                    self.parent_.show_messages.emit(False)

                    return False

                question = QMessageBox.question(
                    self.parent_,
                    self.tr("Question"),
                    self.tr(
                        "Diaries are unique to the day they are written.\nDo you really want to change the content?"
                    ),
                )

                if question != QMessageBox.StandardButton.Yes:
                    return

            if self.parent_.db.saveDocument(
                self.parent_.getText(), self.parent_.content, autosave, self.parent_.document, self.parent_.notebook
            ):
                self.parent_.last_content = self.parent_.getText()

                if self.parent_.settings["sync"] is not None and (
                    self.parent_.settings["sync"].endswith("_all") or self.parent_.settings["sync"].endswith("_export")
                ):
                    os.makedirs(
                        os.path.join(USER_DIRS[self.parent_.settings["folder"]], "Nottodbox", self.parent_.notebook),
                        exist_ok=True,
                    )

                    sync = self.parent_.settings["sync"].removesuffix("_all").removesuffix("_export")
                    export = self.parent_.settings["format"] if sync == "format" else sync

                    if sync == "pdf":
                        writer = QPdfWriter(
                            os.path.join(
                                USER_DIRS[self.parent_.settings["folder"]],
                                "Nottodbox",
                                self.parent_.notebook,
                                f"{self.parent_.document}.pdf",
                            )
                        )
                        writer.setTitle(self.parent_.document)

                        self.parent_.input.document().print_(writer)

                    elif export == "plain-text":
                        with open(
                            os.path.join(
                                USER_DIRS[self.parent_.settings["folder"]],
                                "Nottodbox",
                                self.parent_.notebook,
                                f"{self.parent_.document}.txt",
                            ),
                            "w+",
                        ) as f:
                            f.write(self.parent_.input.toPlainText())

                    else:
                        export = self.parent_.settings["format"] if sync == "format" else sync

                        writer = QTextDocumentWriter(
                            os.path.join(
                                USER_DIRS[self.parent_.settings["folder"]],
                                "Nottodbox",
                                self.parent_.notebook,
                                f"{self.parent_.document}.{export}",
                            ),
                            export.encode("utf-8") if export != "odt" else b"odf",
                        )
                        writer.write(self.parent_.input.document())

                self.parent_.index.model().setData(self.parent_.index, self.parent_.getText(), ITEM_DATAS["content"])

                if not autosave:
                    self.parent_.index.model().setData(
                        self.parent_.index,
                        self.parent_.db.getBackups(self.parent_.document, self.parent_.notebook),
                        ITEM_DATAS["backup"],
                    )

                    self.parent_.show_messages.emit(True)

                return True

            else:
                self.parent_.show_messages.emit(False)

                return False


class DocumentTextEdit(QTextEdit):
    def __init__(self, parent: DocumentView) -> None:
        super().__init__(parent)

        self.parent_ = parent

    def mousePressEvent(self, event: QMouseEvent):
        self.anchor = self.anchorAt(event.pos())

        if self.anchor:
            QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if hasattr(self, "anchor") and self.anchor:
            QDesktopServices.openUrl(self.anchor)
            QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
            self.anchor = None

        super().mouseReleaseEvent(event)


def documentSetContent(content_: str, format_: str, input_: QTextDocument | QTextEdit) -> None:
    if format_ == "plain-text":
        input_.setPlainText(content_)

    elif format_ == "markdown":
        input_.setMarkdown(content_)

    elif format_ == "html":
        input_.setHtml(content_)
