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
from notes import NotesTabWidget, NotesListView
from todos import TodosTabWidget, TodolistListView, TodosListView
from diaries import DiariesDiary, diariesdb
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)
    
today = QDate.currentDate()


class HomeScrollArea(QScrollArea):
    """Scrollable area for home page."""
    
    def __init__(self, parent: QMainWindow, todos: QTabWidget, notes: QTabWidget):
        """
        Display a scrollable area for main widget.

        Args:
            parent (QMainWindow): Parent of this widget (main window)
            todos (Todos): Todos widget of parent
            notes (NotesTabWidget): Notes widget of parent
        """

        super().__init__(parent)
        
        global home_parent
        home_parent = parent
    
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(HomeWidget(self, todos, notes))


class HomeWidget(QWidget):
    """Home page main widget.."""
    
    def __init__(self, parent: HomeScrollArea, todos: TodosTabWidget, notes: NotesTabWidget):
        """
        Display a widget for some shortcuts.

        Args:
            parent (HomeScrollArea): Main widget
            todos (Todos): Todos widget of parent
            notes (NotesTabWidget): Notes widget of parent
        """
        
        super().__init__(parent)
        
        self.setLayout(QGridLayout(self))
        
        self.label_welcome = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                             text=_("Welcome {username}!").format(username = username))
        self.label_welcome.setStyleSheet("QLabel{font-size: 12pt;}")
        
        self.label_diary = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter,
                                  text=_("Your Diary for {date}").format(date = today.toString("dd.MM.yyyy")))
        
        self.diary = DiariesDiary(self, today.toString("dd.MM.yyyy"), diariesdb)
        
        # self.label_maintodos = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
        #                           text=_("List of Your Main Todos"))
        
        # self.maintodos = TodolistListView(todos, "main", "home")
        
        # self.label_todolist = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
        #                           text=_("List of Your Todolists"))
        
        # self.todolist = TodosListView(todos, "home")
        # self.todolist.doubleClicked.connect(lambda: home_parent.tabwidget.setCurrentWidget(home_parent.todos))
        
        self.label_notes = QLabel(self, alignment=Qt.AlignmentFlag.AlignCenter, 
                                  text=_("List of Your Notes"))
        
        self.notes = NotesListView(notes, "home")
        self.notes.doubleClicked.connect(lambda: home_parent.tabwidget.setCurrentWidget(home_parent.notes))
        
        self.layout().addWidget(self.label_welcome, 0, 0, 1, 2)
        self.layout().addWidget(self.label_diary, 1, 0, 1, 2)
        self.layout().addWidget(self.diary, 2, 0, 1, 2)
        # self.layout().addWidget(self.label_maintodos, 3, 0, 1, 1)
        # self.layout().addWidget(self.maintodos, 4, 0, 1, 1)
        # self.layout().addWidget(self.label_todolist, 3, 1, 1, 1)
        # self.layout().addWidget(self.todolist, 4, 1, 1, 1)
        self.layout().addWidget(self.label_notes, 5, 0, 1, 2)
        self.layout().addWidget(self.notes, 6, 0, 1, 2)