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
from widgets.pages import NormalPage
from notes import NotesTabWidget, NotesTreeView
from todos import TodosTabWidget, TodosTreeView
from diaries import diariesdb, setting_autosave, setting_format
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import *


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
    def __init__(self, parent: HomeScrollArea, todos: TodosTabWidget, notes: NotesTabWidget):
        super().__init__(parent)
        
        self.setLayout(QVBoxLayout(self))
        
        self.label_welcome = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                             text=_("Welcome {username}!").format(username = username))
        self.label_welcome.setStyleSheet("font-size: 12pt")
        
        self.label_diary = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                                  text=_("Your Diary for {date}").format(date = today.toString("dd.MM.yyyy")))
        
        self.diary = NormalPage(self, "diaries", today, today.toString("dd.MM.yyyy"), setting_autosave, setting_format, diariesdb)
        
        self.label_todos = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
                                  text=_("List of Your Todo Lists & Todos"))
        
        self.todos = TodosTreeView(todos, "home")
        
        self.label_notes = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
                                  text=_("List of Your Notes"))
        
        self.notes = NotesTreeView(notes, "home")
        
        self.layout().addWidget(self.label_welcome)
        self.layout().addWidget(self.label_diary)
        self.layout().addWidget(self.diary)
        self.layout().addWidget(self.label_todos)
        self.layout().addWidget(self.todos)
        self.layout().addWidget(self.label_notes)
        self.layout().addWidget(self.notes)