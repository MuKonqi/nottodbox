# SPDX-License-Identifier: GPL-3.0-or-later

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


import subprocess
from gettext import gettext as _
from PySide6.QtCore import Slot, QDate, QSettings
from PySide6.QtWidgets import *
from widgets.lists import TreeView
from widgets.others import HSeperator, Label, PushButton
from widgets.pages import NormalPage


USER_NAME_PRETTY = str(subprocess.run("getent passwd $LOGNAME | cut -d: -f5 | cut -d, -f1", shell=True, capture_output=True)
               .stdout).removeprefix("b'").removesuffix("\\n'")

today = QDate.currentDate()


class HomeWidget(QWidget):
    def __init__(self, parent: QMainWindow, todos, notes, diaries):
        super().__init__(parent)
        
        self.layout_ = QVBoxLayout(self)
        
        self.label_welcome = Label(self, _("Welcome {username}!").format(username = USER_NAME_PRETTY))
        font = self.label_welcome.font()
        font.setBold(True)
        font.setPointSize(16)
        self.label_welcome.setFont(font)
        
        self.diary_button = PushButton(self, _("Focus to Diary for Today"))
        self.diary_button.clicked.connect(self.focusToDiary)
        
        self.diary = NormalPage(self, "diaries", diaries.db, diaries.format, diaries.autosave, today.toString("dd.MM.yyyy"))
        
        self.todos_seperator = HSeperator(self)
        
        self.todos_label = Label(self, _("List of To-dos"))
        
        self.todos = TreeView(todos, "todos", todos.db, False, todos.treeview.model_)
        
        self.notes_seperator = HSeperator(self)
        
        self.notes_label = Label(self, _("List of Notes"))
        
        self.notes = TreeView(notes, "home", notes.db, False, notes.treeview.model_)
        
        self.qsettings = QSettings("io.github.mukonqi", "nottodbox")
        
        self.focused_to_diary = self.qsettings.value("home/focused-to-diary")
        
        if self.focused_to_diary is None:
            self.qsettings.setValue("home/focused-to-diary", "false")
            
            self.focused_to_diary = "false"
            
        self.focusToDiary(True)
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.label_welcome)
        self.layout_.addWidget(HSeperator(self))
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
        if inverted and self.focused_to_diary == "true":
            self.focusToDiaryBase(True)
            
        elif inverted and self.focused_to_diary == "false":
            self.focusToDiaryBase(False)
            
        elif not inverted and self.focused_to_diary == "true":
            self.focusToDiaryBase(False)
            
        elif not inverted and self.focused_to_diary == "false":
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
            
            self.focused_to_diary = "true"
            
            self.qsettings.setValue("home/focused-to-diary", "true")
            
        else:
            self.todos_seperator.setVisible(True)
            self.todos_label.setVisible(True)
            self.todos.setVisible(True)
            self.notes_seperator.setVisible(True)
            self.notes_label.setVisible(True)
            self.notes.setVisible(True)
            
            self.diary_button.setText(_("Focus to Diary for Today"))
            
            self.focused_to_diary = "false"
            
            self.qsettings.setValue("home/focused-to-diary", "false")