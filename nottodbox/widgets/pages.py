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


import sys
sys.dont_write_bytecode = True


from gettext import gettext as _
from .dialogs import ColorDialog, GetTwoDialog
from PyQt6.QtGui import QTextCursor, QTextFormat, QTextBlockFormat, QTextCharFormat, QTextListFormat, QAction
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import *


class TextFormatter(QToolBar):
    def __init__(self, parent: QWidget, input: QTextEdit, format: str) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.input = input
        self.page = self.parent_.parent()
        
        self.bold_button = QAction(self, text=_("Bold"))
        self.bold_button.triggered.connect(self.setBold)
        self.bold_button.setCheckable(True)
        
        self.italic_button = QAction(self, text=_("Italic"))
        self.italic_button.triggered.connect(self.setItalic)
        self.italic_button.setCheckable(True)
        
        self.underline_button = QAction(self, text=_("Underline"))
        self.underline_button.triggered.connect(self.setUnderline)
        self.underline_button.setCheckable(True)
        
        self.strikethrough_button = QAction(self, text=_("Strike through"))
        self.strikethrough_button.triggered.connect(self.setStrikeThrough)
        self.strikethrough_button.setCheckable(True)
        
        self.fixedspacing_button = QAction(self, text=_("Fixed spacing"))
        self.fixedspacing_button.triggered.connect(self.setFixedSpacing)
        self.fixedspacing_button.setCheckable(True)
        
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
            _("Normal"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignCenter))
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
        self.addAction(self.fixedspacing_button)
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
        self.setStatusTip(_("Text formatter is only available in Markdown and HTML formats."))
        
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
        status, qcolor = ColorDialog(Qt.GlobalColor.white, self, _("Select color")).getColor()
        
        if status == "ok":
            cur = self.input.textCursor()

            chrfmt = cur.charFormat()
            
            if qcolor.isValid():
                chrfmt.setBackground(qcolor)
            else:
                chrfmt.setBackground(QTextCharFormat().background())
                
            self.mergeFormat(cur, chrfmt)
        
    def setBold(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontWeight() == 700:
            chrfmt.setFontWeight(400)
        elif chrfmt.fontWeight() == 400:
            chrfmt.setFontWeight(700)
        
        self.mergeFormat(cur, chrfmt)
        
    def setFixedSpacing(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontFixedPitch():
            chrfmt.setFontFixedPitch(False)
        else:
            chrfmt.setFontFixedPitch(True)
            
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
        
    def setItalic(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontItalic():
            chrfmt.setFontItalic(False)
        else:
            chrfmt.setFontItalic(True)
            
        self.mergeFormat(cur, chrfmt)
        
    def setLink(self) -> None:
        status, text, url = GetTwoDialog(self, "text", _("Add link"), _("Link text:"), _("Link URL:"), _("Not required"), _("Required")).getItems()
        
        if status == "ok":
            if url != "" and url != None:
                cur = self.input.textCursor()
                cur.beginEditBlock()
                
                chrfmt = cur.charFormat()
                chrfmt.setAnchor(True)
                chrfmt.setAnchorHref(url)
                chrfmt.setFontUnderline(True)

                if text == "" or text == None:
                    text = url
                    
                cur.insertText(url, chrfmt)
                cur.endEditBlock()
                    
            else:
                QMessageBox.critical(self, _("Error"), _("The URL is required, it can not be blank."))
        
    def setList(self, style: QTextListFormat.Style) -> None:
        cur = self.input.textCursor()
        cur.insertList(style)
    
    def setStrikeThrough(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontStrikeOut():
            chrfmt.setFontStrikeOut(False)
        else:
            chrfmt.setFontStrikeOut(True)
            
        self.mergeFormat(cur, chrfmt)
        
    def setTable(self) -> None:
        status, row, column = GetTwoDialog(self, "number", _("Add table"), _("Row number:"), _("Column number:"), 1, 1).getItems()
        
        if status == "ok":
            if row != None and column != None:
                cur = self.input.textCursor()
                cur.insertTable(row, column)  

            else:
                QMessageBox.critical(self, _("Error"), _("The row and column numbers are required, they can not be blank."))
                
    def setTextColor(self) -> None:
        status, qcolor = ColorDialog(Qt.GlobalColor.white, self, _("Select color")).getColor()
        
        if status == "ok":
            cur = self.input.textCursor()

            chrfmt = cur.charFormat()
            
            if qcolor.isValid():
                chrfmt.setForeground(qcolor)
            else:
                chrfmt.setForeground(QTextCharFormat().foreground())
                
            self.mergeFormat(cur, chrfmt)
    
    def setUnderline(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontUnderline():
            chrfmt.setFontUnderline(False)
        else:
            chrfmt.setFontUnderline(True)
            
        self.mergeFormat(cur, chrfmt)
    
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
            
        if chrfmt.fontFixedPitch():
            self.fixedspacing_button.setChecked(True)
        else:
            self.fixedspacing_button.setChecked(False)
                
    def updateStatus(self, format: str) -> None:
        if format == "plain-text":
            self.setEnabled(False)
            
        elif format == "markdown":
            self.setEnabled(True)
            self.alignment_menu.setEnabled(False)
            self.alignment_button.setEnabled(False)
            self.text_color.setEnabled(False)
            self.background_color.setEnabled(False)
            
        elif format == "html":
            self.setEnabled(True)
            self.alignment_menu.setEnabled(True)
            self.alignment_button.setEnabled(True)
            self.text_color.setEnabled(True)
            self.background_color.setEnabled(True)


class NormalPage(QWidget):
    def __init__(self, parent: QWidget, module: str, notebook_or_today: str | QDate, name: str, global_autosave: str, global_format: str, database) -> None:
        super().__init__(parent)
        
        self.module = module
        self.name = name
        self.database = database
        self.global_autosave = global_autosave
        self.global_format = global_format
        self.closable = True
        
        if self.module == "notes":
            self.notebook = notebook_or_today
            self.content = self.database.getContent(self.notebook, self.name)
            self.call_autosave = self.database.getAutosave(self.notebook, self.name)
            self.call_format = self.database.getFormat(self.notebook, self.name)
            self.outdated = "no"
            
        elif self.module == "diaries":
            self.today = notebook_or_today
            self.content = self.database.getContent(self.name)
            self.call_autosave = self.database.getAutosave(self.name)
            self.call_format = self.database.getFormat(self.name)
            if QDate().fromString(self.name, "dd.MM.yyyy") == self.today:
                self.outdated = "no"
            else:
                self.outdated = "yes"

        if self.call_autosave == "global":
            self.setting_autosave = self.global_autosave
        else:
            self.setting_autosave = self.call_autosave
        
        if self.call_format == "global":
            self.setting_format = self.global_format
        else:
            self.setting_format = self.call_format
        
        self.input = QTextEdit(self)
        self.input.setAcceptRichText(True)
        
        if self.setting_format == "plain-text":
            self.input.setPlainText(self.content)
            
        elif self.setting_format == "markdown":
            self.input.setMarkdown(self.content)
            
        elif self.setting_format == "html":
            self.input.setHtml(self.content)

        self.formatter = TextFormatter(self, self.input, self.setting_format)
    
        self.input.textChanged.connect(lambda: self.saveDocument(True))
        self.input.cursorPositionChanged.connect(self.formatter.updateButtons)
        
        self.save = QPushButton(self, text=_("Save"))
        self.save.clicked.connect(self.saveDocument)
              
        self.autosave = QComboBox(self)
        self.autosave.addItems([
            _("Auto-save: Follow global ({setting})").format(setting = self.global_autosave),
            _("Auto-save: Enabled"), 
            _("Auto-save: Disabled")])
        
        if self.call_autosave == "global":
            self.autosave.setCurrentIndex(0)
        elif self.call_autosave == "enabled":
            self.autosave.setCurrentIndex(1)
        elif self.call_autosave == "disabled":
            self.autosave.setCurrentIndex(2)
        
        self.autosave.setEditable(False)
        self.autosave.setStatusTip(_("Auto-saves do not change backups."))
        self.autosave.currentIndexChanged.connect(self.setAutoSave)
        
        self.format = QComboBox(self)
        self.format.addItems([
            _("Format: Follow global ({setting})").format(setting = self.global_format),
            _("Format: Plain-text"), 
            _("Format: Markdown"), 
            _("Format: HTML")])
        
        if self.call_format == "global":
            self.format.setCurrentIndex(0)
        elif self.call_format == "plain-text":
            self.format.setCurrentIndex(1)
        elif self.call_format == "markdown":
            self.format.setCurrentIndex(2)
        elif self.call_format == "html":
            self.format.setCurrentIndex(3)
        
        self.format.setEditable(False)
        self.format.setStatusTip(_("Format changes may corrupt the document."))
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.setLayout(QGridLayout(self))
        self.layout().addWidget(self.formatter, 0, 0, 1, 2)
        self.layout().addWidget(self.input, 1, 0, 1, 2)
        self.layout().addWidget(self.save, 2, 0, 1, 2)
        self.layout().addWidget(self.autosave, 3, 0, 1, 1)
        self.layout().addWidget(self.format, 3, 1, 1, 1)
        
        if self.outdated == "yes":
            self.autosave.setEnabled(False)
            self.autosave.setStatusTip(_("Auto-save feature disabled for old diaries."))
            self.setting_autosave = "disabled"
            
    def createDiary(self) -> bool:
        check = self.database.checkIfTheDiaryExists(self.name)
        
        if check:
            return True
        
        else:
            create = self.database.saveDocument(self.name, "", "", False)
            
            if create:
                return True
            
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to create {name} diary for changing settings."))
                return False
                
    def saveDocument(self, autosave: bool = False) -> bool:
        self.closable = False
        
        if self.setting_format == "plain-text":
            text = self.input.toPlainText()
            
        elif self.setting_format == "markdown":
            text = self.input.toMarkdown()
            
        elif self.setting_format == "html":
            text = self.input.toHtml()
        
        if not autosave or (autosave and self.setting_autosave == "enabled"):
            if self.outdated == "yes":
                question = QMessageBox.question(
                    self, _("Question"), _("Diaries are unique to the day they are written.\nSo, are you sure?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    return
            
            if self.module == "notes":
                call = self.database.saveDocument(self.notebook,
                                              self.name,
                                              text,
                                              self.content,
                                              autosave)
            
            elif self.module == "diaries":
                call = self.database.saveDocument(self.name,
                                              text,
                                              self.content,
                                              autosave)

            if call:
                self.closable = True
                
                if not autosave:
                    QMessageBox.information(self, _("Successful"), _("{name} document saved.").format(name = self.name))
                    
                return True
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to save {name} document.").format(name = self.name))
                
                return False
                
    def setAutoSave(self, index: int) -> None:
        if index == 0:
            setting = "global"
        
        elif index == 1:
            setting = "enabled"
        
        elif index == 2:
            setting = "disabled"
        
        if self.module == "notes":
            call = self.database.setAutosave(self.notebook, self.name, setting)
        
        elif self.module == "diaries":
            if self.createDiary():
                call = self.database.setAutosave(self.name, setting)
            else:
                return
        
        if call:
            if setting == "global":
                self.setting_autosave = self.global_autosave
            else:
                self.setting_autosave = setting
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new auto-save setting for {name} document.").format(name = self.name))
            
    def setFormat(self, index: int) -> None:
        if index == 0:
            setting = "global"
        
        elif index == 1:
            setting = "plain-text"
        
        elif index == 2:
            setting = "markdown"
        
        elif index == 3:
            setting = "html"
            
        if self.outdated == "yes":
            question = QMessageBox.question(
                self, _("Question"), _("Diaries are unique to the day they are written.\nSo, are you sure?"))
            
            if question != QMessageBox.StandardButton.Yes:
                return
        
        if self.module == "notes":
            call = self.database.setFormat(self.notebook, self.name, setting)
            
        elif self.module == "diaries":
            if self.createDiary():
                call = self.database.setFormat(self.name, setting)
            else:
                return
        
        if call:
            if setting == "global":
                self.setting_format = self.global_format
            else:
                self.setting_format = setting
                
            self.formatter.updateStatus(self.setting_format)
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new format setting for {name} document.").format(name = self.name))


class BackupPage(QWidget):
    def __init__(self, parent: QWidget, module: str, notebook_or_today: str, name: str, global_format: str, database) -> None:
        super().__init__(parent)
        
        self.module = module
        self.name = name
        self.database = database
        self.global_format = global_format
        self.closable = True
        
        if self.module == "notes":
            self.notebook = notebook_or_today
            self.content = self.database.getBackup(self.notebook, self.name)
            self.call_format = self.database.getFormat(self.notebook, self.name)
            self.outdated = "no"
            
        elif self.module == "diaries":
            self.today = notebook_or_today
            self.content = self.database.getBackup(self.name)
            self.call_format = self.database.getFormat(self.name)
            if QDate().fromString(self.name, "dd.MM.yyyy") == self.today:
                self.outdated = "no"
            else:
                self.outdated = "yes"
        
        self.input = QTextEdit(self)
        
        if self.setting_format == "plain-text":
            self.input.setPlainText(self.content)
            
        elif self.setting_format == "markdown":
            self.input.setMarkdown(self.content)
            
        elif self.setting_format == "html":
            self.input.setHtml(self.content)
        
        self.button = QPushButton(self, text=_("Restore content"))
        self.button.clicked.connect(self.restoreContent)
        
        self.format = QComboBox(self)
        self.format.addItems([
            _("Format: Follow global ({setting})").format(setting = self.global_format),
            _("Format: Plain-text"), 
            _("Format: Markdown"), 
            _("Format: HTML")])
        
        if self.call_format == "global":
            self.format.setCurrentIndex(0)
        elif self.call_format == "plain-text":
            self.format.setCurrentIndex(1)
        elif self.call_format == "markdown":
            self.format.setCurrentIndex(2)
        elif self.call_format == "html":
            self.format.setCurrentIndex(3)
        
        self.format.setEditable(False)
        self.format.setStatusTip(_("Format changes may corrupt the document."))
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.input)
        self.layout().addWidget(self.button)
        self.layout().addWidget(self.format)

    def setFormat(self, index: int) -> None:
        if index == 0:
            setting = "global"
        
        elif index == 1:
            setting = "plain-text"
        
        elif index == 2:
            setting = "markdown"
        
        elif index == 3:
            setting = "html"
            
        if self.outdated == "yes":
            question = QMessageBox.question(
                self, _("Question"), _("Diaries are unique to the day they are written.\nSo, are you sure?"))
            
            if question != QMessageBox.StandardButton.Yes:
                return
        
        if self.module == "notes":
            call = self.database.setFormat(self.notebook, self.name, setting)
        elif self.module == "diaries":
            call = self.database.setFormat(self.name, setting)
        
        if call:
            if setting == "global":
                self.setting_format = self.global_format
            else:
                self.setting_format = setting
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new format setting for {note} document.").format(note = self.name))
            
    def restoreContent(self):
        if self.outdated == "yes":
            question = QMessageBox.question(
                self, _("Question"), _("Diaries are unique to the day they are written.\nSo, are you sure?"))
            
            if question != QMessageBox.StandardButton.Yes:
                return
        
        if self.module == "notes":
            call = self.database.restoreContent(self.notebook, self.name)
        elif self.module == "diaries":
            call = self.database.restoreContent(self.name)
        
        if call:
            QMessageBox.information(self, _("Successful"), _("Backup of {name} document restored.").format(name = self.name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup of {name} document.").format(name = self.name))