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


import getpass
import subprocess
from gettext import gettext as _
from PySide6.QtCore import Slot, QDate
from PySide6.QtWidgets import *
from widgets.other import HSeperator, Label, PushButton
from widgets.pages import NormalPage
from diaries import diariesdb, setting_autosave, setting_format
from todos import TodosWidget, TodosTreeView
from notes import NotesTabWidget, NotesTreeView


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"
username = str(subprocess.run("getent passwd $LOGNAME | cut -d: -f5 | cut -d, -f1", shell=True, capture_output=True)
               .stdout).removeprefix("b'").removesuffix("\\n'")
    
today = QDate.currentDate()


class HomeWidget(QWidget):
    def __init__(self, parent: QMainWindow, todos: TodosWidget, notes: NotesTabWidget):
        super().__init__(parent)
        
        self.focused_to_diary = False
        
        self.layout_ = QVBoxLayout(self)
        
        self.label_welcome = Label(self, _("Welcome {username}!").format(username = username))
        self.label_welcome.setStyleSheet("font-size: 16pt; font-weight: 900;")
        
        self.diary_button = PushButton(self, _("Focus to Diary for Today"))
        self.diary_button.clicked.connect(self.focusToDiary)
        
        self.diary = NormalPage(self, "diaries", today, today.toString("dd.MM.yyyy"), setting_autosave, setting_format, diariesdb)
        
        self.todos_seperator = HSeperator(self)
        
        self.todos_label = Label(self, _("List of To-dos"))
        
        self.todos = TodosTreeView(todos, "home", todos.treeview.model_)
        
        self.notes_seperator = HSeperator(self)
        
        self.notes_label = Label(self, _("List of Notes"))
        
        self.notes = NotesTreeView(notes, "home", notes.treeview.model_)
        
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
    def focusToDiary(self) -> None:
        if self.focused_to_diary:
            self.todos_seperator.setVisible(True)
            self.todos_label.setVisible(True)
            self.todos.setVisible(True)
            self.notes_seperator.setVisible(True)
            self.notes_label.setVisible(True)
            self.notes.setVisible(True)
            
            self.diary_button.setText(_("Focus to Diary for Today"))
            
            self.focused_to_diary = False
            
        else:
            self.todos_seperator.setVisible(False)
            self.todos_label.setVisible(False)
            self.todos.setVisible(False)
            self.notes_seperator.setVisible(False)
            self.notes_label.setVisible(False)
            self.notes.setVisible(False)
            
            self.diary_button.setText(_("Finish Focusing of Diary for Today"))
            
            self.focused_to_diary = True