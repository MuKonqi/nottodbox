# SPDX-License-Identifier: GPL-3.0-or-later

# Credit: While making TextFormatter class, <https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp> helped me as a referance.

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
from PySide6.QtCore import Signal, Slot, Qt, QDate, QObject, QThread
from PySide6.QtGui import QTextCursor, QTextFormat, QTextBlockFormat, QTextCharFormat, QTextListFormat, QTextTableFormat, QTextLength, QTextTable, QDesktopServices, QPalette
from PySide6.QtWidgets import *
from .dialogs import ColorDialog, GetTwoDialog
from .others import PushButton, Action
            
            
class BasePage(QWidget):
    def __init__(self, parent: QWidget, module: str,
                 db, mode: str, format: str, autosave: str,
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent)
        
        self.module = module
        self.name = name
        self.db = db
        self.mode = mode
        self.format_ = format
        self.autosave_ = autosave
        
        self.closable = True
        
        self.layout_ = QGridLayout(self)
        
        self.today = QDate.currentDate()
        
        if self.module == "notes":
            self.table = table
            
            self.outdated = "no"
            
        elif self.module == "diaries":
            self.table = "__main__"
            
            self.outdated = self.db.getOutdated(name)
                    
        if self.mode == "normal":
            self.content = self.db.getContent(self.name, self.table)
        
        elif self.mode == "backup":
            self.content = self.db.getBackup(self.name, self.table)
            
        self.call_format = self.db.getFormat(self.name, self.table)
        
        if self.call_format == "global":
            self.format = self.format_
            
        else:
            self.format = self.call_format
            
        self.call_autosave = self.db.getAutosave(self.name, self.table)

        if self.call_autosave == "global":
            self.autosave = self.autosave_
            
        else:
            self.autosave = self.call_autosave
        
        self.input = TextEdit(self)
        self.input.setAcceptRichText(True)
        
        if self.format == "plain-text":
            self.input.setPlainText(self.content)
            
        elif self.format == "markdown":
            self.input.setMarkdown(self.content)
            
        elif self.format == "html":
            self.input.setHtml(self.content)
        
        self.format_combobox = QComboBox(self)
        self.format_combobox.addItems([
            "{} {}".format(_("Format:"), _("Follow global ({setting})").format(setting = self.prettyFormat())),
            "{} {}".format(_("Format:"), _("Plain-text")),
            "{} {}".format(_("Format:"), "Markdown"),
            "{} {}".format(_("Format:"), "HTML")])
        
        if self.call_format == "global":
            self.format_combobox.setCurrentIndex(0)
        elif self.call_format == "plain-text":
            self.format_combobox.setCurrentIndex(1)
        elif self.call_format == "markdown":
            self.format_combobox.setCurrentIndex(2)
        elif self.call_format == "html":
            self.format_combobox.setCurrentIndex(3)
        
        self.format_combobox.setEditable(False)
        self.format_combobox.setStatusTip(_("Format changes may corrupt the content."))
        self.format_combobox.currentIndexChanged.connect(self.setFormat)
        
        self.autosave_combobox = QComboBox(self)
        self.autosave_combobox.addItems([
            "{} {}".format(_("Auto-save:"), _("Follow global ({setting})").format(setting = self.prettyAutosave())),
            "{} {}".format(_("Auto-save:"), _("Enabled")),
            "{} {}".format(_("Auto-save:"), _("Disabled"))])
        
        if self.call_autosave == "global":
            self.autosave_combobox.setCurrentIndex(0)
        elif self.call_autosave == "enabled":
            self.autosave_combobox.setCurrentIndex(1)
        elif self.call_autosave == "disabled":
            self.autosave_combobox.setCurrentIndex(2)
        
        self.autosave_combobox.setEditable(False)
        self.autosave_combobox.setStatusTip(_("Auto-saves do not change backups."))
        self.autosave_combobox.currentIndexChanged.connect(self.setAutosave)
        
        if self.outdated == "yes":
            self.autosave_combobox.setEnabled(False)
            self.autosave_combobox.setStatusTip(_("Auto-save feature disabled for old diaries."))
            self.autosave = "disabled"
            
        self.button = PushButton(self)
            
        self.formatter = TextFormatter(self, self.format)
        
        self.input.cursorPositionChanged.connect(self.formatter.updateButtons)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.formatter, 0, 0, 1, 2)
        self.layout_.addWidget(self.input, 1, 0, 1, 2)
        self.layout_.addWidget(self.button, 2, 0, 1, 2)
        self.layout_.addWidget(self.format_combobox, 3, 0, 1, 1)
        self.layout_.addWidget(self.autosave_combobox, 3, 1, 1, 1)
        
    def prettyAutosave(self, global_autosave_: str | None = None) -> str:
        if global_autosave_ is None:
            global_autosave = self.autosave_
            
        else:
            global_autosave = global_autosave_
            
        if global_autosave == "enabled":
            return _("Enabled").lower()
            
        elif global_autosave == "disabled":
            return _("Disabled").lower()

    def prettyFormat(self, global_format_: str | None = None) -> str:
        if global_format_ is None:
            global_format = self.format_
            
        else:
            global_format = global_format_
        
        if global_format == "plain-text":
            return _("Plain-text").lower()
            
        elif global_format == "markdown":
            return "Markdown"
            
        elif global_format == "html":
            return "HTML"
        
    @Slot(int)
    def setAutosave(self, index: int) -> bool:
        if index == 0:
            value = "global"
        
        elif index == 1:
            value = "enabled"
        
        elif index == 2:
            value = "disabled"
        
        if self.db.setAutosave(value, self.name, self.table):
            if value == "global":
                self.autosave = self.autosave_
                
            else:
                self.autosave = value
                
                return True
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new auto-save setting {of_item}.")
                                 .format(of_item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary"))
                                 .format(name = self.name))
            
            return False
            
    @Slot(int)
    def setFormat(self, index: int) -> bool:
        if index == 0:
            value = "global"
        
        elif index == 1:
            value = "plain-text"
        
        elif index == 2:
            value = "markdown"
        
        elif index == 3:
            value = "html"
            
        if self.outdated == "yes":
            question = QMessageBox.question(
                self, _("Question"), _("Diaries are unique to the day they are written.\nDo you really want to change the content?"))
            
            if question != QMessageBox.StandardButton.Yes:
                return
        
        if self.db.setFormat(value, self.name, self.table):
            if value == "global":
                self.format = self.format_
                
            else:
                self.format = value
                
            self.formatter.updateStatus(self.format)
                
            return True
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new format setting {of_item}.")
                                 .format(of_item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary"))
                                 .format(name = self.name))
            
            return False
            

class BackupPage(BasePage):
    def __init__(self, parent: QWidget, module: str,
                 db, format: str, autosave: str,
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent, module, db, "backup", format, autosave, name, table)
        
        self.input.setReadOnly(True)
        
        self.button.setText(_("Restore Content"))
        self.button.clicked.connect(self.restoreContent)
            
    @Slot()
    def restoreContent(self) -> None:
        if self.outdated == "yes":
            question = QMessageBox.question(
                self, _("Question"), _("Diaries are unique to the day they are written.\nDo you really want to change the content?"))
            
            if question != QMessageBox.StandardButton.Yes:
                return
        
        if self.db.restoreContent(self.name, self.table):
            QMessageBox.information(self, _("Successful"), _("Backup {of_item} restored.")
                                    .format(of_item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary"))
                                    .format(name = self.name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup {of_item}.")
                                 .format(of_item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary"))
                                 .format(name = self.name))
            
    @Slot(int)
    def setAutosave(self, index: int) -> bool:
        return super().setAutosave(index)[0]


class NormalPage(BasePage):
    def __init__(self, parent: QWidget, module: str,
                 db, format: str, autosave: str,
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent, module, db, "normal", format, autosave, name, table)
            
        self.saver = Saver(self)
        self.saver.started.connect(self.saver.saveChild)
        
        self.saver_thread = QThread()
        
        self.saver.moveToThread(self.saver_thread)

        self.input.textChanged.connect(self.makeCanNotClosable)
        
        self.button.setText(_("Save"))
        self.button.clicked.connect(lambda: self.saver.saveChild())
        
        self.save = lambda: self.saver.started.emit(True)
        
        self.changeAutosaveConnections()
            
    def checkIfTheDiaryExistsIfNotCreateTheDiary(self) -> bool:
        if self.module == "notes":
            return True
        
        elif self.module == "diaries":
            if self.db.checkIfTheChildExists(self.name):
                return True
            
            else:
                create = self.db.createChild(self.name)
                
                if create:
                    return True
                
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} dated diary for changing settings."))
                    
                    return False
                
    def changeAutosaveConnections(self) -> None:    
        if self.autosave == "enabled":
            self.connectAutosaveConnections()
            
        elif self.autosave == "disabled":
            self.disconnectAutosaveConnections()
                
    def connectAutosaveConnections(self) -> None:
        self.saver_thread.start()
        self.connected = True
        self.input.textChanged.connect(self.save)
            
    def disconnectAutosaveConnections(self) -> None:
        self.saver_thread.quit()
        self.connected = False
        if self.connected:
            self.input.textChanged.disconnect(self.save)
                
    def getText(self) -> str:
        if self.format == "plain-text":
            return self.input.toPlainText()
            
        elif self.format == "markdown":
            return self.input.toMarkdown()
            
        elif self.format == "html":
            return self.input.toHtml()
        
    def makeBackup(self) -> bool:
        if self.db.setBackup(self.getText(), self.name):
            return True
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to set backup {of_item}.")
                                 .format(item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary")))
                
            return False
        
    @Slot()
    def makeCanNotClosable(self) -> None:
        self.closable = False
    
    @Slot(int)
    def setAutosave(self, index: int) -> bool:
        if not self.checkIfTheDiaryExistsIfNotCreateTheDiary():
            return False
        
        if super().setAutosave(index):
            self.changeAutosaveConnections()
            
            return True    
            
        else:
            return False
        
    @Slot(int)
    def setFormat(self, index: int) -> bool:        
        return self.checkIfTheDiaryExistsIfNotCreateTheDiary() and super().setFormat(index)
        
        
class Saver(QObject):
    started = Signal(bool)
    
    def __init__(self, parent: NormalPage) -> None:
        super().__init__()
        
        self.parent_ = parent
    
    @Slot(bool)
    def saveChild(self, autosave: bool = False) -> bool | None:
        if self.parent_.outdated == "":
            if not self.parent_.db.createChild(self.parent_.name):
                QMessageBox.critical(self.parent_, _("Error"), _("Failed to create {item}.")
                                    .format(item = _("{name} note") if self.parent_.module == "notes" else _("{name} dated diary")))
                
                return False
        
        if not autosave or (autosave and self.parent_.autosave == "enabled"):
            if self.parent_.outdated == "yes":
                question = QMessageBox.question(
                    self.parent_, _("Question"), _("Diaries are unique to the day they are written.\nDo you really want to change the content?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    return
            
            call = self.parent_.db.saveChild(self.parent_.getText(),
                                             self.parent_.content,
                                             autosave,
                                             self.parent_.name,
                                             self.parent_.table)

            if call:
                self.parent_.closable = True
                
                if not autosave:
                    QMessageBox.information(self.parent_, _("Successful"), _("{item} saved.")
                                            .format(item = _("{name} note") if self.parent_.module == "notes" else _("{name} dated diary"))
                                            .format(name = self.parent_.name))
                    
                return True
                
            else:
                QMessageBox.critical(self.parent_, _("Error"), _("Failed to save {item}.")
                                     .format(item = _("{name} note") if self.parent_.module == "notes" else _("{name} dated diary"))
                                     .format(name = self.parent_.name))
                
                return False
            

class TextEdit(QTextEdit):
    def mousePressEvent(self, e):
        self.anchor = self.anchorAt(e.pos())
        
        if self.anchor:
            QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)
            
        super().mousePressEvent(e)
            
    def mouseReleaseEvent(self, e):
        if self.anchor:
            QDesktopServices.openUrl(self.anchor)
            QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
            self.anchor = None
            
        super().mouseReleaseEvent(e)


class TextFormatter(QToolBar):
    def __init__(self, parent: BasePage, format: str) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.input = self.parent_.input
        self.page = self.parent_.parent()
        
        self.bold_button = Action(self, _("Bold"))
        self.bold_button.triggered.connect(self.setBold)
        self.bold_button.setCheckable(True)
        
        self.italic_button = Action(self, _("Italic"))
        self.italic_button.triggered.connect(self.setItalic)
        self.italic_button.setCheckable(True)
        
        self.underline_button = Action(self, _("Underline"))
        self.underline_button.triggered.connect(self.setUnderline)
        self.underline_button.setCheckable(True)
        
        self.strikethrough_button = Action(self, _("Strike through"))
        self.strikethrough_button.triggered.connect(self.setStrikeThrough)
        self.strikethrough_button.setCheckable(True)
        
        self.header_menu = QMenu(self)
        self.header_menu.addAction(
            _("Paragraph text"), lambda: self.setHeadingLevel(0))
        self.header_menu.addAction(
            _("Biggest header"), lambda: self.setHeadingLevel(1))
        self.header_menu.addAction(
            _("Bigger header"), lambda: self.setHeadingLevel(2))
        self.header_menu.addAction(
            _("Big header"), lambda: self.setHeadingLevel(3))
        self.header_menu.addAction(
            _("Small header"), lambda: self.setHeadingLevel(4))
        self.header_menu.addAction(
            _("Smaller header"), lambda: self.setHeadingLevel(5))
        self.header_menu.addAction(
            _("Smallest header"), lambda: self.setHeadingLevel(6))
        
        self.header_button = QToolButton(self)
        self.header_button.setText(_("Heading"))
        self.header_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.header_button.setMenu(self.header_menu)
        
        self.list_menu = QMenu(self)
        self.list_menu.addAction(
            _("Unordered"), lambda: self.setList(QTextListFormat.Style.ListDisc))
        self.list_menu.addAction(
            _("Ordered with decimal numbers"), lambda: self.setList(QTextListFormat.Style.ListDecimal))
        self.list_menu.addAction(
            _("Ordered with lowercase letters"), lambda: self.setList(QTextListFormat.Style.ListLowerAlpha))
        self.list_menu.addAction(
            _("Ordered with uppercase letters"), lambda: self.setList(QTextListFormat.Style.ListUpperAlpha))
        
        self.list_button = QToolButton(self)
        self.list_button.setText(_("List"))
        self.list_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.list_button.setMenu(self.list_menu)
        
        self.alignment_menu = QMenu(self)
        self.alignment_menu.addAction(
            _("Left"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignLeft))
        self.alignment_menu.addAction(
            _("Center"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignCenter))
        self.alignment_menu.addAction(
            _("Right"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignRight))
        self.alignment_menu.setStatusTip(_("Setting alignment is only available in HTML format."))
        
        self.alignment_button = QToolButton(self)
        self.alignment_button.setText(_("Alignment"))
        self.alignment_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.alignment_button.setMenu(self.alignment_menu)
        self.alignment_button.setStatusTip(_("Setting alignment is only available in HTML format."))
        
        self.addAction(self.bold_button)
        self.addAction(self.italic_button)
        self.addAction(self.underline_button)
        self.addAction(self.strikethrough_button)
        self.addSeparator()
        
        self.addWidget(self.header_button)
        self.addWidget(self.list_button)
        self.addWidget(self.alignment_button)
        self.addSeparator()
        
        self.addAction(_("Table"), self.setTable)
        self.addAction(_("Link"), self.setLink)
        
        self.text_color = self.addAction(_("Text color"), self.setTextColor)
        self.text_color.setStatusTip(_("Setting text color is only available in HTML format."))
        
        self.background_color = self.addAction(_("Background color"), self.setBackgroundColor)
        self.background_color.setStatusTip(_("Setting background color is only available in HTML format."))
        
        self.updateStatus(format)
        
        self.fixTable()
        
    def fixTable(self, element: QTextTable = None) -> None:
        if type(element) == QTextTable:
            self.fixTableBase(element)
        
        else:
            for frame in self.input.document().rootFrame().childFrames():
                if type(frame) == QTextTable:
                    self.fixTableBase(frame)
        
    def fixTableBase(self, table: QTextTable) -> None:
        table_format = QTextTableFormat()
        table_format.setBorder(1)
        
        constraints = []
        
        for i in range(0, table.columns()):
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
        
    def mergeFormat(self, cur: QTextCursor, format: QTextCharFormat) -> None:
        if not cur.hasSelection():
            cur.select(QTextCursor.SelectionType.WordUnderCursor)
            
        cur.mergeCharFormat(format)
    
    def setAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        blkfmt = QTextBlockFormat()
        blkfmt.setAlignment(alignment)
        
        cur = self.input.textCursor()
        cur.mergeBlockFormat(blkfmt)
        
    def setBackgroundColor(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, True, Qt.GlobalColor.white, _("Select {} Color").format(_("Background"))).getColor()
        
        if ok:
            if status == "new":
                color = qcolor
                
            elif status == "default":
                color = QTextCharFormat().background()
            
            cur = self.input.textCursor()

            chrfmt = cur.charFormat()
            
            chrfmt.setBackground(color)
                
            self.mergeFormat(cur, chrfmt)
        
    @Slot()
    def setBold(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontWeight() == 700:
            chrfmt.setFontWeight(400)
        elif chrfmt.fontWeight() == 400:
            chrfmt.setFontWeight(700)
        
        self.mergeFormat(cur, chrfmt)
        
    def setHeadingLevel(self, level: int) -> None:
        cur = self.input.textCursor()
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
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontItalic():
            chrfmt.setFontItalic(False)
        else:
            chrfmt.setFontItalic(True)
            
        self.mergeFormat(cur, chrfmt)
        
    def setLink(self) -> None:
        status, text, url = GetTwoDialog(self, _("Add Link"), "text", _("Link text:"), _("Link URL:"), _("Not required"), _("Required")).getResult()
        
        if status == "ok":
            if url != "" and url != None:
                cur = self.input.textCursor()
                cur.beginEditBlock()
                
                chrfmt = cur.charFormat()
                chrfmt.setAnchor(True)
                chrfmt.setAnchorHref(url)
                chrfmt.setForeground(QApplication.palette().color(QPalette.ColorRole.Link))

                if text == "" or text == None:
                    text = url
                    
                cur.insertText(text, chrfmt)
                cur.endEditBlock()
                    
            else:
                QMessageBox.critical(self, _("Error"), _("The URL is required, it can not be blank."))
        
    def setList(self, style: QTextListFormat.Style) -> None:
        cur = self.input.textCursor()
        cur.insertList(style)
    
    @Slot()
    def setStrikeThrough(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontStrikeOut():
            chrfmt.setFontStrikeOut(False)
        else:
            chrfmt.setFontStrikeOut(True)
            
        self.mergeFormat(cur, chrfmt)
                
    def setTable(self) -> None:
        status, rows, columns = GetTwoDialog(self, _("Add Table"), "number", _("Row number:"), _("Column number:"), 1, 1).getResult()
        
        if status == "ok":
            if rows != None and columns != None:
                cur = self.input.textCursor()
                
                self.fixTable(cur.insertTable(rows, columns))
                
            else:
                QMessageBox.critical(self, _("Error"), _("The row and column numbers are required, they can not be blank."))
                
    def setTextColor(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, True, Qt.GlobalColor.white, _("Select {} Color").format(_("Text"))).getColor()
        
        if ok:
            if status == "new":
                color = qcolor
                
            elif status == "default":
                color = QTextCharFormat().foreground()
            
            cur = self.input.textCursor()

            chrfmt = cur.charFormat()
            
            chrfmt.setForeground(color)
                
            self.mergeFormat(cur, chrfmt)
    
    @Slot()
    def setUnderline(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontUnderline():
            chrfmt.setFontUnderline(False)
        else:
            chrfmt.setFontUnderline(True)
            
        self.mergeFormat(cur, chrfmt)
    
    @Slot()
    def updateButtons(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontWeight() == 700:
            self.bold_button.setChecked(True)
        elif chrfmt.fontWeight() == 400: 
            self.bold_button.setChecked(False)
            
        if chrfmt.fontItalic():
            self.italic_button.setChecked(True)  
        else:
            self.italic_button.setChecked(False)
            
        if chrfmt.fontUnderline():
            self.underline_button.setChecked(True)
        else:
            self.underline_button.setChecked(False)
            
        if chrfmt.fontStrikeOut():
            self.strikethrough_button.setChecked(True)
        else:
            self.strikethrough_button.setChecked(False)
                
    def updateStatus(self, format: str) -> None:
        if self.parent_.mode == "normal":
            if format == "plain-text":
                self.setEnabled(False)
                self.setStatusTip(_("Text formatter is only available in Markdown and HTML formats.")),
                
            elif format == "markdown":
                self.setEnabled(True)
                self.alignment_menu.setEnabled(False)
                self.alignment_button.setEnabled(False)
                self.text_color.setEnabled(False)
                self.background_color.setEnabled(False)
                self.setStatusTip(_("To close an open formatting, type a word and then click on it."))
                
            elif format == "html":
                self.setEnabled(True)
                self.alignment_menu.setEnabled(True)
                self.alignment_button.setEnabled(True)
                self.text_color.setEnabled(True)
                self.background_color.setEnabled(True)
                self.setStatusTip(_("To close an open formatting, type a word and then click on it."))
                
        elif self.parent_.mode == "backup":
            self.setEnabled(False)
            self.setStatusTip(_("Text formatter is not available for backups."))