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

# Credit: <https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp>

import sys
sys.dont_write_bytecode = True


from gettext import gettext as _
from .dialog import GetTwoItem
from PyQt6.QtGui import QTextCursor, QTextFormat, QTextBlockFormat, QTextCharFormat, QTextListFormat, QAction
from PyQt6.QtCore import Qt
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
        
        self.strikeout_button = QAction(self, text=_("Strike out"))
        self.strikeout_button.triggered.connect(self.setStrikeOut)
        self.strikeout_button.setCheckable(True)
        
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
        self.addAction(self.strikeout_button)
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
        self.background_color = self.addAction(_("Background color"), self.setBackground)
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
        
    def setBackground(self) -> None:
        color = QColorDialog.getColor(Qt.GlobalColor.white, self, _("Set background color"))
        
        if color.isValid():
            cur = self.input.textCursor()

            chrfmt = cur.charFormat()
            chrfmt.setBackground(color)
            
            self.mergeFormat(cur, chrfmt)
            
        else:
            QMessageBox.critical(self, _("Error"), _("The color is invalid."))
        
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
    
    def setTextColor(self) -> None:
        color = QColorDialog.getColor(Qt.GlobalColor.white, self, _("Set text color"))
        
        if color.isValid():
            cur = self.input.textCursor()

            chrfmt = cur.charFormat()
            chrfmt.setForeground(color)
            
            self.mergeFormat(cur, chrfmt)
            
        else:
            QMessageBox.critical(self, _("Error"), _("The color is invalid."))
        
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
        text, url = GetTwoItem(self, "text", _("Add link"), _("Link text:"), _("Link URL:"), _("Not required"), _("Required")).getItems()
        
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
    
    def setStrikeOut(self) -> None:
        cur = self.input.textCursor()
        chrfmt = cur.charFormat()
        
        if chrfmt.fontStrikeOut():
            chrfmt.setFontStrikeOut(False)
        else:
            chrfmt.setFontStrikeOut(True)
            
        self.mergeFormat(cur, chrfmt)
        
    def setTable(self) -> None:
        row, column = GetTwoItem(self, "number", _("Add table"), _("Row number:"), _("Column:"), 1, 1).getItems()
        
        if row != None and column != None:
            cur = self.input.textCursor()
            cur.insertTable(row, column)  

        else:
            QMessageBox.critical(self, _("Error"), _("The row and column numbers are required, they can not be blank."))
    
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
            self.strikeout_button.setChecked(True)
        else:
            self.strikeout_button.setChecked(False)
            
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