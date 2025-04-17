# SPDX-License-Identifier: GPL-3.0-or-later

# Credit: While making PageHelper class, <https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp> helped me as a referance.

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


from gettext import gettext as _
from PySide6.QtCore import Signal, Slot, Qt, QDate, QObject, QThread
from PySide6.QtGui import QTextCursor, QTextFormat, QTextBlockFormat, QTextCharFormat, QTextListFormat, QTextTableFormat, QTextLength, QTextTable, QDesktopServices, QPalette
from PySide6.QtWidgets import *
from .dialogs import ColorDialog, GetTwoDialog
from .others import Action
            
            
class Page(QWidget):
    def __init__(self, parent: QWidget, module: str,
                 db, mode: str, autosave: str, format: str,
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.name = name
        self.db = db
        self.mode = mode
        self.autosave_ = autosave
        self.format_ = format
        
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
        
        self.call_autosave = self.db.getAutosave(self.name, self.table)

        if self.call_autosave == "global":
            self.autosave = self.autosave_
            
        else:
            self.autosave = self.call_autosave
            
        if self.outdated == "yes":
            self.autosave = "disabled"
            
        self.call_format = self.db.getFormat(self.name, self.table)
        
        if self.call_format == "global":
            self.format = self.format_
            
        else:
            self.format = self.call_format
            
        self.input = PageTextEdit(self)
        self.input.setAcceptRichText(True)
        
        self.helper = PageHelper(self, self.format)
        self.input.cursorPositionChanged.connect(self.helper.updateButtons)
        
        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(self.helper)
        self.layout_.addWidget(self.input)

    def prettyAutosave(self, autosave: str | None = None) -> str:
        if autosave is not None:
            self.autosave_ = autosave
            
        if self.autosave_ == "enabled":
            self.pretty_autosave = _("Enabled").lower()
            
        elif self.autosave_ == "disabled":
            self.pretty_autosave = _("Disabled").lower()
        
        return self.pretty_autosave

    def prettyFormat(self, format: str | None = None) -> str:
        if format is not None:
            self.format_ = format
        
        if self.format_ == "plain-text":
            self.pretty_format = _("Plain-text").lower()
            
        elif self.format_ == "markdown":
            self.pretty_format = "Markdown"
            
        elif self.format_ == "html":
            self.pretty_format = "HTML"
        
        return self.pretty_format
        
    @Slot(int)
    def setAutosave(self, index: int) -> bool:
        self.helper.setAutosave(index)
        
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
        question = QMessageBox.question(self, _("Question"), _("Format changes may corrupt your documents.\nDo you really want to change the format?"))
        
        if question != QMessageBox.StandardButton.Yes:
            return False
        
        self.helper.setFormat(index)
        
        if index == 0:
            value = "global"
        
        elif index == 1:
            value = "html"
        
        elif index == 2:
            value = "markdown"
        
        elif index == 3:
            value = "plain-text"
            
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
                
            self.helper.updateStatus(self.format)
                
            return True
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save new format setting {of_item}.")
                                 .format(of_item = _("of {name} note") if self.module == "notes" else _("of {name} dated diary"))
                                 .format(name = self.name))
            
            return False
            

class BackupPage(Page):
    def __init__(self, parent: QWidget, module: str,
                 db, autosave: str, format: str,
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent, module, db, "backup", autosave, format, name, table)
        
        self.input.setReadOnly(True)
        
        self.helper.button.triggered.connect(self.restoreContent)
            
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


class NormalPage(Page):
    showMessages_ = Signal(bool)
    
    def __init__(self, parent: QWidget, module: str,
                 db, autosave: str, format: str,
                 name: str, table: str = "__main__") -> None:
        super().__init__(parent, module, db, "normal", autosave, format, name, table)
        
        self.connected = False
        
        self.last_content = self.content
        
        self.showMessages_.connect(self.showMessages)
            
        self.saver = PageSaver(self)
        self.saver.saveChild_.connect(self.saver.saveChild)
        
        self.saver_thread = QThread()
        
        self.saver.moveToThread(self.saver_thread)
        
        self.helper.button.triggered.connect(lambda: self.saver.saveChild())
        
        self.save = lambda: self.saver.saveChild_.emit(True)
        
        self.changeAutosaveConnections()
            
    def checkIfTheDiaryExistsIfNotCreateTheDiary(self) -> bool:
        if self.module == "notes":
            return True
        
        elif self.module == "diaries":
            if self.db.checkIfTheChildExists(self.name):
                return True
            
            else:                
                if self.db.createChild(self.name):
                    return True
                
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {name} dated diary for changing settings."))
                    
                    return False
                
    def changeAutosaveConnections(self) -> None:
        if self.autosave == "enabled" and not self.connected:
            self.connectAutosaveConnections()
            
        elif self.autosave == "disabled":
            self.disconnectAutosaveConnections()
                
    def connectAutosaveConnections(self) -> None:
        self.input.textChanged.connect(self.save)
        self.saver_thread.start()
        self.connected = True
    
    def checkIfTheTextChanged(self) -> bool:
        return self.getText() == self.last_content
            
    def disconnectAutosaveConnections(self) -> None:
        if self.connected:
            self.input.textChanged.disconnect(self.save)
        self.saver_thread.quit()
        self.connected = False
                
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
    
    @Slot(bool)
    def showMessages(self, successful: bool) -> None:
        if successful:
            QMessageBox.information(self, _("Successful"), _("{item} saved.")
                                    .format(item = _("{name} note") if self.module == "notes" else _("{name} dated diary"))
                                    .format(name = self.name))
        
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save {item}.")
                                     .format(item = _("{name} note") if self.module == "notes" else _("{name} dated diary"))
                                     .format(name = self.name))
            
    def refresh(self, autosave: str, format: str) -> None:
        self.format_ = format
            
        if self.call_format == "global":
            self.format = format
            self.helper.updateStatus(format)
            
        self.helper.format_actions[0].setText(self.helper.format_actions[0].text().replace(self.pretty_format, self.prettyFormat(format)))
        
        self.autosave_ = autosave
            
        if self.call_autosave == "global":
            self.autosave = autosave
            self.changeAutosaveConnections()
            
        self.helper.autosave_actions[0].setText(self.helper.autosave_actions[0].text().replace(self.pretty_autosave, self.prettyAutosave(autosave)))
            
            
class PageHelper(QToolBar):
    def __init__(self, parent: Page, format: str) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.button = self.addAction(_("Save"))
        self.button.setStatusTip(_("Auto-saves do not change backups and disabled for old diaries."))
        
        self.settings_menu = QMenu(self)
        self.settings_button = QToolButton(self)
        self.settings_button.setText(_("Settings"))
        self.settings_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.settings_button.setMenu(self.settings_menu)

        autosaves = ["global", "enabled", "disabled"]
        self.autosave_menu = self.settings_menu.addMenu(_("Auto-save"))
        self.autosave_actions = [self.autosave_menu.addAction(_("Follow global: {}, (default)").format(self.parent_.prettyAutosave()), lambda: self.parent_.setAutosave(0)),
                                 self.autosave_menu.addAction(_("Enabled"), lambda: self.parent_.setAutosave(1)),
                                 self.autosave_menu.addAction(_("Disabled"), lambda: self.parent_.setAutosave(2))]
        font = self.autosave_actions[0].font()
        font.setUnderline(True)
        self.autosave_actions[0].setFont(font)
        self.setAutosave(autosaves.index(self.parent_.call_autosave))
        
        formats = ["global", "html", "markdown", "plain-text"]
        self.format_menu = self.settings_menu.addMenu(_("Format"))
        self.format_actions = [self.format_menu.addAction(_("Follow global: {}, (default)").format(self.parent_.prettyFormat()), lambda: self.parent_.setFormat(0)),
                               self.format_menu.addAction("HTML", lambda: self.parent_.setFormat(1)),
                               self.format_menu.addAction("Markdown", lambda: self.parent_.setFormat(2)),
                               self.format_menu.addAction(_("Plain-text"), lambda: self.parent_.setFormat(3))]
        font = self.format_actions[0].font()
        font.setUnderline(True)
        self.format_actions[0].setFont(font)
        self.setFormat(formats.index(self.parent_.call_format))
        
        self.settings_action = self.addWidget(self.settings_button)
        
        self.addSeparator()
        
        self.bold_action = Action(self, _("Bold"))
        self.bold_action.triggered.connect(self.setBold)
        self.bold_action.setCheckable(True)
        self.addAction(self.bold_action)
        
        self.italic_action = Action(self, _("Italic"))
        self.italic_action.triggered.connect(self.setItalic)
        self.italic_action.setCheckable(True)
        self.addAction(self.italic_action)
        
        self.underline_action = Action(self, _("Underline"))
        self.underline_action.triggered.connect(self.setUnderline)
        self.underline_action.setCheckable(True)
        self.addAction(self.underline_action)
        
        self.strikethrough_action = Action(self, _("Strike through"))
        self.strikethrough_action.triggered.connect(self.setStrikeThrough)
        self.strikethrough_action.setCheckable(True)
        self.addAction(self.strikethrough_action)

        self.addSeparator()
        
        self.header_menu = QMenu(self)
        self.header_button = QToolButton(self)
        self.header_button.setText(_("Heading"))
        self.header_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.header_button.setMenu(self.header_menu)
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
        self.addWidget(self.header_button)
        
        self.list_menu = QMenu(self)
        self.list_button = QToolButton(self)
        self.list_button.setText(_("List"))
        self.list_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.list_button.setMenu(self.list_menu)
        
        self.list_menu.addAction(
            _("Unordered"), lambda: self.setList(QTextListFormat.Style.ListDisc))
        self.list_menu.addAction(
            _("Ordered with decimal numbers"), lambda: self.setList(QTextListFormat.Style.ListDecimal))
        self.list_menu.addAction(
            _("Ordered with lowercase letters"), lambda: self.setList(QTextListFormat.Style.ListLowerAlpha))
        self.list_menu.addAction(
            _("Ordered with uppercase letters"), lambda: self.setList(QTextListFormat.Style.ListUpperAlpha))
        
        self.alignment_menu = QMenu(self)
        self.alignment_button = QToolButton(self)
        self.alignment_button.setText(_("Alignment"))
        self.alignment_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.alignment_button.setMenu(self.alignment_menu)
        self.alignment_button.setStatusTip(_("Setting alignment is only available in HTML format."))
        self.addWidget(self.list_button)
        
        self.alignment_menu.addAction(_("Left"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignLeft))
        self.alignment_menu.addAction(_("Center"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignCenter))
        self.alignment_menu.addAction(_("Right"), lambda: self.setAlignment(Qt.AlignmentFlag.AlignRight))
        self.alignment_menu.setStatusTip(_("Setting alignment is only available in HTML format."))
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
            for frame in self.parent_.input.document().rootFrame().childFrames():
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
        
    def setAutosave(self, index: int) -> None:
        for button in self.autosave_actions:
            button.setText(button.text().removesuffix(", ({})".format(_("selected"))))
            font = button.font()
            font.setBold(False)
            button.setFont(font)

        self.autosave_actions[index].setText("{}, ({})".format(self.autosave_actions[index].text(), _("selected")))
        font = self.autosave_actions[index].font()
        font.setBold(True)
        self.autosave_actions[index].setFont(font)
        
    def setBackgroundColor(self) -> None:
        ok, status, qcolor = ColorDialog(self, False, True, Qt.GlobalColor.white, _("Select {} Color").format(_("Background"))).getColor()
        
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
        
    def setFormat(self, index: int) -> None:
        for button in self.format_actions:
            button.setText(button.text().removesuffix(", ({})".format(_("selected"))))
            font = button.font()
            font.setBold(False)
            button.setFont(font)

        self.format_actions[index].setText("{}, ({})".format(self.format_actions[index].text(), _("selected")))
        font = self.format_actions[index].font()
        font.setBold(True)
        self.format_actions[index].setFont(font)
        
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
        status, text, url = GetTwoDialog(self, _("Add Link"), "text", _("Link text:"), _("Link URL:"), _("Not required"), _("Required")).getResult()
        
        if status == "ok":
            if url != "" and url != None:
                cur = self.parent_.input.textCursor()
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
        status, rows, columns = GetTwoDialog(self, _("Add Table"), "number", _("Row number:"), _("Column number:"), 1, 1).getResult()
        
        if status == "ok":
            if rows != None and columns != None:
                cur = self.parent_.input.textCursor()
                
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
                
    def updateStatus(self, format: str) -> None:
        if self.parent_.mode == "normal":
            if format == "plain-text":
                actions = self.actions()
                actions.pop(actions.index(self.button))
                actions.pop(actions.index(self.settings_action))
                
                for action in actions:
                    action.setEnabled(False)
                
                self.setStatusTip(_("Text formatter is only available in Markdown and HTML formats.")),
                
            elif format == "markdown":
                for action in self.actions():
                    action.setEnabled(True)
                
                self.alignment_menu.setEnabled(False)
                self.alignment_button.setEnabled(False)
                self.text_color.setEnabled(False)
                self.background_color.setEnabled(False)
                
                self.setStatusTip(_("To close an open formatting, type a word and then click on it."))
                
            elif format == "html":
                for action in self.actions():
                    action.setEnabled(True)
                
                self.alignment_menu.setEnabled(True)
                self.alignment_button.setEnabled(True)
                self.text_color.setEnabled(True)
                self.background_color.setEnabled(True)
                
                self.setStatusTip(_("To close an open formatting, type a word and then click on it."))
                
        elif self.parent_.mode == "backup":
            actions = self.actions()
            actions.pop(actions.index(self.button))
            actions.pop(actions.index(self.settings_action))
            
            for action in actions:
                action.setEnabled(False)
            
            self.setStatusTip(_("Text formatter is not available for backups."))

        
class PageSaver(QObject):
    saveChild_ = Signal(bool)
    
    def __init__(self, parent: NormalPage) -> None:
        super().__init__()
        
        self.parent_ = parent
    
    @Slot(bool)
    def saveChild(self, autosave: bool = False) -> bool:
        if self.parent_.module == "diaries" and not self.parent_.db.checkIfTheChildExists(self.parent_.name, self.parent_.table):
            if self.parent_.db.createChild(self.parent_.name):
                if type(self.parent_.parent_).__name__ == "HomeWidget":
                    self.parent_.parent_.parent_.diaries.home.shortcuts[
                        (self.parent_.name, self.parent_.table)] = Action(self, self.parent_.name)
                    self.parent_.parent_.parent_.diaries.home.shortcuts[(self.parent_.name, self.parent_.table)].triggered.connect(
                        lambda state: self.parent_.parent_.parent_.diaries.home.shortcutEvent(self.parent_.name, self.parent_.table))
                    self.parent_.parent_.parent_.diaries.home.menu.addAction(
                        self.parent_.parent_.parent_.diaries.home.shortcuts[(self.parent_.name, self.parent_.table)])
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to create {item}.")
                                    .format(item = _("{name} note") if self.parent_.module == "notes" else _("{name} dated diary")))
                
                return False
        
        if not autosave or (autosave and self.parent_.autosave == "enabled"):
            if self.parent_.outdated == "yes":
                if autosave:
                    self.parent_.showMessages_.emit(False)
                    
                    return False
                
                question = QMessageBox.question(
                    self.parent_, _("Question"), _("Diaries are unique to the day they are written.\nDo you really want to change the content?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    return

            if self.parent_.db.saveChild(
                self.parent_.getText(), self.parent_.content, autosave, self.parent_.name, self.parent_.table):
                if not autosave:
                    self.parent_.showMessages_.emit(True)
                    
                self.parent_.last_content = self.parent_.getText()
                    
                return True
                
            else:
                self.parent_.showMessages_.emit(False)
                
                return False
            

class PageTextEdit(QTextEdit):
    def __init__(self, parent: Page) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        if self.parent_.format == "plain-text":
            self.setPlainText(self.parent_.content)
            
        elif self.parent_.format == "markdown":
            self.setMarkdown(self.parent_.content)
            
        elif self.parent_.format == "html":
            self.setHtml(self.parent_.content)
    
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