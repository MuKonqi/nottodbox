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


import getpass
import os
from gettext import gettext as _
from widgets.other import HSeperator, Label
from widgets.pages import NormalPage
from notes import NotesTabWidget, NotesTreeView
from todos import TodosWidget, TodosTreeView
from diaries import diariesdb, setting_autosave, setting_format
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)
    
today = QDate.currentDate()


class HomeScrollArea(QScrollArea):
    def __init__(self, parent: QMainWindow, todos: QTabWidget, notes: QTabWidget):
        super().__init__(parent)
        
        global home_parent
        home_parent = parent
    
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(HomeWidget(self, todos, notes))


class HomeWidget(QWidget):
    def __init__(self, parent: HomeScrollArea, todos: TodosWidget, notes: NotesTabWidget):
        super().__init__(parent)
        
        self.layout_ = QVBoxLayout(self)
        
        self.label_welcome = Label(self, _("Welcome {username}!").format(username = username))
        self.label_welcome.setStyleSheet("font-size: 12pt")
        
        self.label_diary = Label(self, _("Your Diary for {date}").format(date = today.toString("dd.MM.yyyy")))
        self.diary = NormalPage(self, "diaries", today, today.toString("dd.MM.yyyy"), setting_autosave, setting_format, diariesdb)
        
        self.label_todos = Label(self, _("List of Your To-do Lists & To-dos"))
        self.todos = TodosTreeView(todos, "home")
        
        self.label_notes = Label(self, _("List of Your Notebooks & Notes"))
        self.notes = NotesTreeView(notes, "home")
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.label_welcome)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.label_diary)
        self.layout_.addWidget(self.diary)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.label_todos)
        self.layout_.addWidget(self.todos)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.label_notes)
        self.layout_.addWidget(self.notes)