# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024 MuKonqi (Muhammed S.)

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
from PySide6.QtCore import Slot, Qt, QDate
from PySide6.QtGui import QTextCursor, QTextFormat, QTextBlockFormat, QTextCharFormat, QTextListFormat, QDesktopServices, QPalette
from PySide6.QtWidgets import *
from databases.base import DBBase
from .dialogs import ColorDialog, GetTwoDialog
from .others import PushButton, Action


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
    def __init__(self, parent: QWidget, input: TextEdit, format: str) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.input = input
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
        ok, status, qcolor = ColorDialog(self, False, Qt.GlobalColor.white, _("Select Background Color")).getColor()
        
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
        status, row, column = GetTwoDialog(self, _("Add Table"), "number", _("Row number:"), _("Column number:"), 1, 1).getResult()
        
        if status == "ok":
            if row != None and column != None:
                cur = self.input.textCursor()
                cur.insertTable(row, column)  

            else:
                QMessageBox.critical(self, _("Error"), _("The row and column numbers are required, they can not be blank."))
                
    def setTextColor(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, Qt.GlobalColor.white, _("Select Text Color")).getColor()
        
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
            
            
class BasePage(QWidget):
    def __init__(self, parent: QWidget, module: str,
                 db: DBBase, caller: str, format: str,
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent)
        
        self.module = module
        self.name = name
        self.db = db
        self.format_ = format
        
        self.closable = True
        
        self.layout_ = QGridLayout(self)
        
        self.today = QDate.currentDate()
        
        if self.module == "notes":
            self.table = table
            
            self.outdated = "no"
            
        elif self.module == "diaries":
            self.table = "__main__"
            
            self.outdated = self.db.getOutdated(name)
                    
        if caller == "normal":
            self.content = self.db.getContent(self.name, self.table)
        
        elif caller == "backup":
            self.content = self.db.getBackup(self.name, self.table)
            
        call_format = self.db.getFormat(self.name, self.table)
            
        if self.format_ == "plain-text":
            pretty_format = _("Plain-text").lower()
            
        elif self.format_ == "markdown":
            pretty_format = "Markdown"
            
        elif self.format_ == "html":
            pretty_format = "HTML"
        
        if call_format == "global":
            self.format = self.format_
            
        else:
            self.format = call_format
        
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
            "{} {}".format(_("Format:"), _("Follow global ({setting})").format(setting = pretty_format)),
            "{} {}".format(_("Format:"), _("Plain-text")),
            "{} {}".format(_("Format:"), "Markdown"),
            "{} {}".format(_("Format:"), "HTML")])
        
        if call_format == "global":
            self.format_combobox.setCurrentIndex(0)
        elif call_format == "plain-text":
            self.format_combobox.setCurrentIndex(1)
        elif call_format == "markdown":
            self.format_combobox.setCurrentIndex(2)
        elif call_format == "html":
            self.format_combobox.setCurrentIndex(3)
        
        self.format_combobox.setEditable(False)
        self.format_combobox.setStatusTip(_("Format changes may corrupt the content."))
        self.format_combobox.currentIndexChanged.connect(self.setFormat)
        
        self.setLayout(self.layout_)
            
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
        
        call = self.db.setFormat(value, self.name, self.table)
        
        if call:
            if value == "global":
                self.format = self.format_
                
            else:
                self.format = value
                
            return True
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new format setting {of_item}.")
                                 .format(of_item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary"))
                                 .format(name = self.name))
            
            return False
        

class BackupPage(BasePage):
    def __init__(self, parent: QWidget, module: str, 
                 db: DBBase, format: str, 
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent, module, db, "backup", format, name, table)
        
        self.button = PushButton(self, _("Restore Content"))
        self.button.clicked.connect(self.restoreContent)
        
        self.layout_.addWidget(self.input)
        self.layout_.addWidget(self.button)
        self.layout_.addWidget(self.format_combobox)
            
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


class NormalPage(BasePage):
    def __init__(self, parent: QWidget, module: str,
                 db: DBBase, format: str, autosave: str,
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent, module, db, "normal", format, name, table)
        
        self.autosave_ = autosave
        
        call_autosave = self.db.getAutosave(self.name, self.table)
                
        if self.autosave_ == "enabled":
            pretty_autosave = _("Enabled").lower()
            
        elif self.autosave_ == "disabled":
            pretty_autosave = _("Disabled").lower()

        if call_autosave == "global":
            self.autosave = self.autosave_
            
        else:
            self.autosave = call_autosave

        self.formatter = TextFormatter(self, self.input, self.format)
    
        self.input.textChanged.connect(lambda: self.saveChild(True))
        self.input.cursorPositionChanged.connect(self.formatter.updateButtons)
        
        self.button = PushButton(self, _("Save"))
        self.button.clicked.connect(self.saveChild)
              
        self.autosave_combobox = QComboBox(self)
        self.autosave_combobox.addItems([
            "{} {}".format(_("Auto-save:"), _("Follow global ({setting})").format(setting = pretty_autosave)),
            "{} {}".format(_("Auto-save:"), _("Enabled")),
            "{} {}".format(_("Auto-save:"), _("Disabled"))])
        
        if call_autosave == "global":
            self.autosave_combobox.setCurrentIndex(0)
        elif call_autosave == "enabled":
            self.autosave_combobox.setCurrentIndex(1)
        elif call_autosave == "disabled":
            self.autosave_combobox.setCurrentIndex(2)
        
        self.autosave_combobox.setEditable(False)
        self.autosave_combobox.setStatusTip(_("Auto-saves do not change backups."))
        self.autosave_combobox.currentIndexChanged.connect(self.setAutoSave)
        
        if self.outdated == "yes":
            self.autosave_combobox.setEnabled(False)
            self.autosave_combobox.setStatusTip(_("Auto-save feature disabled for old diaries."))
            self.autosave = "disabled"
        
        self.layout_.addWidget(self.formatter, 0, 0, 1, 2)
        self.layout_.addWidget(self.input, 1, 0, 1, 2)
        self.layout_.addWidget(self.button, 2, 0, 1, 2)
        self.layout_.addWidget(self.format_combobox, 3, 0, 1, 1)
        self.layout_.addWidget(self.autosave_combobox, 3, 1, 1, 1)
            
    def checkIfTheDiaryExistsIfNotCreateTheDiary(self) -> bool:
        if self.module == "notes":
            return True
        
        elif self.module == "diaries":
            check = self.db.checkIfTheChildExists(self.name)
            
            if check:
                return True
            
            else:
                create = self.db.createChild("", self.name)
                
                if create:
                    return True
                
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} dated diary for changing settings."))
                    return False
                
    @Slot(bool)
    def saveChild(self, autosave: bool = False) -> bool:
        self.closable = False
            
        if self.outdated == "":
            if not self.db.createChild(self.name):
                QMessageBox.critical(self, _("Error"), _("Failed to create {item}.")
                                    .format(item = _("{name} note") if self.module == "notes" else _("{name} dated diary")))
                
                return False
        
        if not autosave or (autosave and self.autosave == "enabled"):
            if self.outdated == "yes":
                question = QMessageBox.question(
                    self, _("Question"), _("Diaries are unique to the day they are written.\nDo you really want to change the content?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    return
            
            call = self.db.saveChild(self.getText(),
                                     self.content,
                                     autosave,
                                     self.name,
                                     self.table)

            if call:
                self.closable = True
                
                if not autosave:
                    QMessageBox.information(self, _("Successful"), _("{item} saved.")
                                            .format(item = _("{name} note") if self.module == "notes" else _("{name} dated diary"))
                                            .format(name = self.name))
                    
                return True
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to save {item}.")
                                     .format(item = _("{name} note") if self.module == "notes" else _("{name} dated diary"))
                                     .format(name = self.name))
                
                return False
    
    @Slot(int)
    def setAutoSave(self, index: int) -> None:
        if index == 0:
            value = "global"
        
        elif index == 1:
            value = "enabled"
        
        elif index == 2:
            value = "disabled"
        
        if not self.checkIfTheDiaryExistsIfNotCreateTheDiary():
            return
        
        if self.db.setAutosave(value, self.name, self.table):
            if value == "global":
                self.autosave = self.autosave_
                
            else:
                self.autosave = value
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new auto-save setting {of_item}.")
                                 .format(of_item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary"))
                                 .format(name = self.name))
            
    def setBackup(self) -> bool:
        if self.db.setBackup(self.getText(), self.name):
            return True
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to set backup {of_item}.")
                                 .format(item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary")))
                
            return False
            
    @Slot(int)
    def setFormat(self, index: int) -> None:
        if not self.checkIfTheDiaryExistsIfNotCreateTheDiary():
            return
        
        if super().setFormat(index):
            self.formatter.updateStatus(self.format)
            
    def getText(self) -> str:
        if self.format == "plain-text":
            return self.input.toPlainText()
            
        elif self.format == "markdown":
            return self.input.toMarkdown()
            
        elif self.format == "html":
            return self.input.toHtml()