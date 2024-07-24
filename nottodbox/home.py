#!/usr/bin/env python3

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


if __name__ == "__main__":
    import sys
    from application import Application
    
    application = Application(sys.argv)
    
    sys.exit(application.exec())

import locale
import gettext
import getpass
import os
from notes import NotesTabWidget, NotesListView
from todos import Todos, TodolistListView, TodosListView
from diaries import DiariesDiary, diariesdb
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import *


if locale.getlocale()[0].startswith("tr"):
    language = "tr"
    translations = gettext.translation("nottodbox", "mo", languages=["tr"], fallback=True)
else:
    language = "en"
    translations = gettext.translation("nottodbox", "mo", languages=["en"], fallback=True)
translations.install()

_ = translations.gettext

align_center = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)
    
today = QDate.currentDate()


class HomeMain(QWidget):
    """The main home widget."""
    
    def __init__(self, parent: QMainWindow, todos: QTabWidget, notes: QTabWidget):
        """
        Create a widget for managing other widgets. 

        Args:
            parent (QMainWindow): Parent of this widget (main window)
            todos (Todos): Todos widget of parent
            notes (NotesTabWidget): Notes widget of parent
        """

        super().__init__(parent)
        
        global home_parent
        home_parent = parent
        
        self.setLayout(QGridLayout(self))
        
        self.label = QLabel(self, alignment=align_center,
                             text=_("Welcome {username}!").format(username = username))
        self.label.setStyleSheet("QLabel{font-size: 12pt;}")
        
        self.left = QScrollArea(self)
        self.left.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.left.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.left.setWidgetResizable(True)
        self.left.setAlignment(align_center)
        self.left.setWidget(HomeLeft(parent, todos, notes))
        
        self.right = QScrollArea(self)
        self.right.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.right.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.right.setWidgetResizable(True)
        self.right.setAlignment(align_center)
        self.right.setWidget(HomeRight(parent))
        self.right.setFixedWidth(144)
        
        self.layout().addWidget(self.label, 0, 0, 1, 2)
        self.layout().addWidget(self.left, 1, 0, 1, 1)
        self.layout().addWidget(self.right, 1, 1, 1, 1)


class HomeLeft(QWidget):
    """A widget for managing items (etc. text-edits, list-views) on the left."""
    
    def __init__(self, parent: HomeMain, todos: Todos, notes: NotesTabWidget):
        """
        Display a widget for shortcut for them:
            - Keeping diary for today
            - Marking as completed/uncompleted todos in main todo list
            - Listing all todo lists except main
            - Listing all notes

        Args:
            parent (HomeMain): Main widget
            todos (Todos): Todos widget of parent
            notes (NotesTabWidget): Notes widget of parent
        """
        
        super().__init__(parent)
        
        self.setLayout(QGridLayout(self))
        
        self.label_diary = QLabel(self, alignment=align_center,
                                  text=_("Your Diary for {date}").format(date = today.toString("dd.MM.yyyy")))
        
        self.diary = DiariesDiary(self, today.toString("dd.MM.yyyy"), diariesdb)
        
        self.label_maintodos = QLabel(self, alignment=align_center, 
                                  text=_("List of Your Main Todos"))
        
        self.maintodos = TodolistListView(todos, "main", "home")
        
        self.label_todolist = QLabel(self, alignment=align_center, 
                                  text=_("List of Your Todolists"))
        
        self.todolist = TodosListView(todos, "home")
        self.todolist.doubleClicked.connect(lambda: home_parent.tabwidget.setCurrentWidget(home_parent.todos))
        
        self.label_notes = QLabel(self, alignment=align_center, 
                                  text=_("List of Your Notes"))
        
        self.notes = NotesListView(notes, "home")
        self.notes.doubleClicked.connect(lambda: home_parent.tabwidget.setCurrentWidget(home_parent.notes))
        
        self.layout().addWidget(self.label_diary, 0, 0, 1, 2)
        self.layout().addWidget(self.diary, 1, 0, 1, 2)
        self.layout().addWidget(self.label_maintodos, 2, 0, 1, 1)
        self.layout().addWidget(self.maintodos, 3, 0, 1, 1)
        self.layout().addWidget(self.label_todolist, 2, 1, 1, 1)
        self.layout().addWidget(self.todolist, 3, 1, 1, 1)
        self.layout().addWidget(self.label_notes, 4, 0, 1, 2)
        self.layout().addWidget(self.notes, 5, 0, 1, 2)
        

class HomeRight(QWidget):
    """A widget for managing items (etc. list-views) on the right."""
    
    def __init__(self, parent: HomeMain):
        """
        Display a widget for list-views.

        Args:
            parent (HomeMain): Main widget
            todos (Todos): Todos widget of parent
            notes (NotesTabWidget): Notes widget of parent
        """
        
        super().__init__(parent)