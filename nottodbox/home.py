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


from gettext import gettext as _
from PySide6.QtCore import Slot, QDate, QSettings
from PySide6.QtWidgets import *
from widgets.lists import TreeView
from widgets.others import HSeperator, Label, PushButton
from widgets.pages import NormalPage
from consts import USER_NAME_PRETTY

today = QDate.currentDate()


class HomeWidget(QWidget):
    def __init__(self, parent: QMainWindow, todos, notes, diaries):
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.layout_ = QGridLayout(self)
        
        self.label_welcome = Label(self, _("Welcome {username}!").format(username = USER_NAME_PRETTY))
        font = self.label_welcome.font()
        font.setBold(True)
        font.setPointSize(16)
        self.label_welcome.setFont(font)
        
        self.diary_seperator = HSeperator(self)
        
        self.diary_button = PushButton(self, _("Focus to Diary for Today"))
        self.diary_button.clicked.connect(self.focusToDiary)
        
        self.diary = NormalPage(self, "diaries", diaries.db, diaries.format, diaries.autosave, today.toString("dd/MM/yyyy"))
        self.diary.layout_.default_contents_margins = self.diary.layout_.contentsMargins()
        self.diary.layout_.setContentsMargins(0, 0, 0, 0)
        
        self.todos_seperator = HSeperator(self)
        
        self.todos_label = Label(self, _("List of To-dos"))
        
        self.todos = TreeView(todos, "todos", todos.db, False, todos.treeview.model_)
        
        self.notes_seperator = HSeperator(self)
        
        self.notes_label = Label(self, _("List of Notes"))
        
        self.notes = TreeView(notes, "home", notes.db, False, notes.treeview.model_)
        
        self.qsettings = QSettings("io.github.mukonqi", "nottodbox")
        
        self.focused_to_diary = self.qsettings.value("home/focuses_to_diary")
        
        if self.focused_to_diary is None:
            self.qsettings.setValue("home/focuses_to_diary", "disabled")
            
            self.focused_to_diary = "disabled"
            
        self.focusToDiary(True)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.label_welcome)
        self.layout_.addWidget(self.diary_seperator)
        self.layout_.addWidget(self.diary_button)
        self.layout_.addWidget(self.diary)
        self.layout_.addWidget(self.todos_seperator)
        self.layout_.addWidget(self.todos_label)
        self.layout_.addWidget(self.todos)
        self.layout_.addWidget(self.notes_seperator)
        self.layout_.addWidget(self.notes_label)
        self.layout_.addWidget(self.notes)
    
    @Slot()
    def focusToDiary(self, inverted: bool = False) -> None:        
        if inverted and self.focused_to_diary == "enabled":
            self.focusToDiaryBase(True)
            
        elif inverted and self.focused_to_diary == "disabled":
            self.focusToDiaryBase(False)
            
        elif not inverted and self.focused_to_diary == "enabled":
            self.focusToDiaryBase(False)
            
        elif not inverted and self.focused_to_diary == "disabled":
            self.focusToDiaryBase(True)
        
    def focusToDiaryBase(self, focus: bool) -> None:
        if focus:
            self.todos_seperator.setVisible(False)
            self.todos_label.setVisible(False)
            self.todos.setVisible(False)
            self.notes_seperator.setVisible(False)
            self.notes_label.setVisible(False)
            self.notes.setVisible(False)
            
            self.diary_button.setText(_("Finish Focusing of Diary for Today"))
            
            self.focused_to_diary = "enabled"
            
            self.qsettings.setValue("home/focuses_to_diary", "enabled")
            
        else:
            self.todos_seperator.setVisible(True)
            self.todos_label.setVisible(True)
            self.todos.setVisible(True)
            self.notes_seperator.setVisible(True)
            self.notes_label.setVisible(True)
            self.notes.setVisible(True)
            
            self.diary_button.setText(_("Focus to Diary for Today"))
            
            self.focused_to_diary = "disabled"
            
            self.qsettings.setValue("home/focuses_to_diary", "disabled")