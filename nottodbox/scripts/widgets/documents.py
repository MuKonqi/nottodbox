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
import os

from PySide6.QtCore import QDate, QModelIndex, QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import (
    QDesktopServices,
    QMouseEvent,
    QPalette,
    QPdfWriter,
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
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QTextEdit, QToolBar, QToolButton, QVBoxLayout, QWidget

from ..consts import USER_DIRS
from .controls import Action, HSeperator, Label
from .dialogs import GetColor, GetTwoNumber


class Document(QWidget):
    def __init__(self, parent: QWidget, db, index: QModelIndex, mode: str) -> None:
        super().__init__(parent)

        self.parent_ = parent

        self.settings = {}

        self.db = db
        self.index = index
        self.mode = mode

        self.creation = index.data(Qt.ItemDataRole.UserRole + 102)

        self.today = QDate.currentDate()

        self.label = Label(self)

        self.input = TextEdit(self)
        self.input.setAcceptRichText(True)

        self.helper = DocumentHelper(self)
        self.input.cursorPositionChanged.connect(self.helper.updateButtons)

        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(self.label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.helper)
        self.layout_.addWidget(self.input)

        self.handleSettings()
        self.refreshContent()
        self.refreshNames()

    def handleGlobal(self, setting: str) -> str:
        if self.settings[(setting, "global")] is None:
            return self.settings[(setting, "default")]

        else:
            return self.settings[(setting, "global")]

    def handleNotebook(self, setting: str) -> None:
        if self.settings[(setting, "notebook")] is None:
            return self.settings[(setting, "default")]

        elif self.settings[(setting, "notebook")] == "global":
            return self.handleGlobal(setting)

        else:
            return self.settings[(setting, "notebook")]

    def handleSettings(self) -> None:
        self.settings["autosave"] = self.index.data(Qt.ItemDataRole.UserRole + 22)[1]
        self.settings["folder"] = self.index.data(Qt.ItemDataRole.UserRole + 25)[1]
        self.settings["format"] = self.index.data(Qt.ItemDataRole.UserRole + 23)[1]
        self.settings["locked"] = self.index.data(Qt.ItemDataRole.UserRole + 21)[1]
        self.settings["sync"] = self.index.data(Qt.ItemDataRole.UserRole + 24)[1]

        self.helper.updateStatus(self.settings["format"])

    def refreshContent(self) -> None:
        self.content = (
            self.index.data(Qt.ItemDataRole.UserRole + 104)
            if self.mode == "normal"
            else self.index.data(Qt.ItemDataRole.UserRole + 105)
        )

        if self.settings["format"] == "plain-text":
            self.input.setPlainText(self.content)

        elif self.settings["format"] == "markdown":
            self.input.setMarkdown(self.content)

        elif self.settings["format"] == "html":
            self.input.setHtml(self.content)

    def refreshNames(self) -> None:
        self.document = self.index.data(Qt.ItemDataRole.UserRole + 101)
        self.notebook = self.index.data(Qt.ItemDataRole.UserRole + 100)

        self.label.setText(self.document)
        self.input.setDocumentTitle(self.document)


class BackupView(Document):
    def __init__(self, parent: QWidget, db, index: QModelIndex) -> None:
        super().__init__(parent, db, index, "backup")

        self.input.setReadOnly(True)

        self.helper.button.triggered.connect(self.restoreContent)

    @Slot()
    def restoreContent(self) -> None:
        if (
            self.settings["locked"] == "enabled"
            and datetime.datetime.strptime(self.creation, "%d/%m/%Y %H:%M").date() != datetime.datetime.today().date()
        ):
            question = QMessageBox.question(
                self,
                self.tr("Question"),
                self.tr("Diaries are unique to the day they are written.\nDo you really want to change the content?"),
            )

            if question != QMessageBox.StandardButton.Yes:
                return

        if self.db.restoreContent(self.document, self.notebook):
            self.index.model().setData(
                self.index, self.db.getContent(self.document, self.notebook), Qt.ItemDataRole.UserRole + 104
            )
            self.index.model().setData(
                self.index, self.db.getBackup(self.document, self.notebook), Qt.ItemDataRole.UserRole + 105
            )

            QMessageBox.information(self, self.tr("Successful"), self.tr("Content restored."))

        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to restore content."))

    def refreshSettings(self) -> None:
        self.handleSettings()


class NormalView(Document):
    show_messages = Signal(bool)

    def __init__(self, parent: QWidget, db, index: QModelIndex) -> None:
        super().__init__(parent, db, index, "normal")

        self.connected = False

        self.last_content = self.content

        self.show_messages.connect(self.showMessages)

        self.saver = DocumentSaver(self)
        self.saver.save_document.connect(self.saver.saveDocument)

        self.saver_thread = QThread()

        self.saver.moveToThread(self.saver_thread)

        self.helper.button.triggered.connect(lambda: self.saver.saveDocument())

        self.save = lambda: self.saver.save_document.emit(True)

        self.changeAutosaveConnections()

    def changeAutosaveConnections(self, event: str | None = None) -> None:
        if (
            self.settings["locked"] == "disabled"
            or datetime.datetime.strptime(self.creation, "%d/%m/%Y %H:%M").date() == datetime.datetime.today().date()
        ) and ((self.settings["autosave"] == "enabled" and not self.connected) or event == "connect"):
            self.input.textChanged.connect(self.save)
            self.saver_thread.start()
            self.connected = True

        elif (
            self.settings["autosave"] == "disabled"
            or event == "disconnect"
            or (
                self.settings["locked"] == "enabled"
                and datetime.datetime.strptime(self.creation, "%d/%m/%Y %H:%M").date()
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

    @Slot(bool)
    def showMessages(self, successful: bool) -> None:
        if successful:
            QMessageBox.information(self, self.tr("Successful"), self.tr("Document saved."))

        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to save document."))

    def refreshSettings(self) -> None:
        self.handleSettings()

        self.changeAutosaveConnections()


class DocumentHelper(QToolBar):
    def __init__(self, parent: BackupView | NormalView) -> None:
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

    def __init__(self, parent: NormalView) -> None:
        super().__init__()

        self.parent_ = parent

    @Slot(bool)
    def saveDocument(self, autosave: bool = False) -> bool:
        if not autosave or (autosave and self.parent_.settings["autosave"] == "enabled"):
            if (
                self.parent_.settings["locked"] == "enabled"
                and datetime.datetime.strptime(self.parent_.creation, "%d/%m/%Y %H:%M").date()
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

                if self.parent_.settings["sync"] is not None:
                    os.makedirs(
                        os.path.join(USER_DIRS[self.parent_.settings["folder"]], "Nottodbox", self.parent_.notebook),
                        exist_ok=True,
                    )

                    if self.parent_.settings["sync"] is not None:
                        if self.parent_.settings["sync"] == "pdf":
                            writer = QPdfWriter(
                                os.path.join(
                                    USER_DIRS[self.parent_.settings["folder"]],
                                    "Nottodbox",
                                    self.parent_.notebook,
                                    f"{self.parent_.document}.pdf",
                                )
                            )
                            writer.setTitle(self.parent_.document)

                            document = QTextDocument(self.parent_.getText())
                            document.print_(writer)

                        elif self.parent_.settings["sync"] == "plain-text" or (
                            self.parent_.settings["sync"] == "format"
                            and self.parent_.settings["format"] == "plain-text"
                        ):
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
                            export = (
                                self.parent_.settings["format"]
                                if self.parent_.settings["sync"] == "format"
                                else self.parent_.settings["sync"]
                            )

                            document = QTextDocument(self.parent_.getText())

                            writer = QTextDocumentWriter(
                                os.path.join(
                                    USER_DIRS[self.parent_.settings["folder"]],
                                    "Nottodbox",
                                    self.parent_.notebook,
                                    f"{self.parent_.document}.{export}",
                                ),
                                export.encode("utf-8") if export != "odt" else b"odf",
                            )
                            writer.write(document)

                self.parent_.index.model().setData(
                    self.parent_.index, self.parent_.getText(), Qt.ItemDataRole.UserRole + 104
                )

                if not autosave:
                    self.parent_.index.model().setData(
                        self.parent_.index,
                        self.parent_.db.getBackup(self.parent_.document, self.parent_.notebook),
                        Qt.ItemDataRole.UserRole + 105,
                    )

                    self.parent_.show_messages.emit(True)

                return True

            else:
                self.parent_.show_messages.emit(False)

                return False


class TextEdit(QTextEdit):
    def __init__(self, parent: BackupView | NormalView) -> None:
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
