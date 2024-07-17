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
    from mainwindow import MainWindow
    from PyQt6.QtWidgets import QApplication
    
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.tabview.setCurrentIndex(0)

    sys.exit(application.exec())


import locale
import gettext
import getpass
import os
from notes import NotesListView
from todos import TodolistListView, TodosListView
from diaries import Diary, diariesdb
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import *


if locale.getlocale()[0].startswith("tr"):
    language = "tr"
    translations = gettext.translation("nottodbox", "po", languages=["tr"], fallback=True)
else:
    language = "en"
    translations = gettext.translation("nottodbox", "po", languages=["en"], fallback=True)
translations.install()

_ = translations.gettext

align_center = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)
    
today = QDate.currentDate()


class Widget(QWidget):
    def __init__(self, parent: QMainWindow, todos: QTabWidget, notes: QTabWidget):
        """
        Display a widget for shortcut for them:
            - Keeping diary for today
            - Marking as completed/uncompleted todos in main todo list
            - Listing all todo lists except main
            - Listing all notes

        Args:
            parent (QMainWindow): Parent of this widget (main window)
            todos (QTabWidget): Todos widget of parent
            notes (QTabWidget): Notes widget of parent
        """
        
        super().__init__(parent)
        
        self.setLayout(QGridLayout(self))
        
        self.welcome = QLabel(self, alignment=align_center,
                             text=_("Welcome {username}!").format(username = username))
        self.welcome.setStyleSheet("QLabel{font-size: 12pt;}")
        
        self.label_diary = QLabel(self, alignment=align_center,
                                  text=_("Your Diary for {date}").format(date = today.toString("dd.MM.yyyy")))
        
        self.diary = Diary(self, today.toString("dd.MM.yyyy"), diariesdb)
        
        self.label_maintodos = QLabel(self, alignment=align_center, 
                                  text=_("List of Your Main Todos"))
        
        self.maintodos = TodolistListView(todos, "main", "home")
        
        self.label_todolist = QLabel(self, alignment=align_center, 
                                  text=_("List of Your Todolists"))
        
        self.todolist = TodosListView(todos, "home")
        self.todolist.doubleClicked.connect(lambda: parent.tabview.setCurrentWidget(parent.todos))
        
        self.label_notes = QLabel(self, alignment=align_center, 
                                  text=_("List of Your Notes"))
        
        self.notes = NotesListView(notes, "home")
        self.notes.doubleClicked.connect(lambda: parent.tabview.setCurrentWidget(parent.notes))
        
        self.layout().addWidget(self.welcome, 0, 0, 1, 2)
        self.layout().addWidget(self.label_diary, 1, 0, 1, 2)
        self.layout().addWidget(self.diary, 2, 0, 1, 2)
        self.layout().addWidget(self.label_maintodos, 3, 0, 1, 1)
        self.layout().addWidget(self.maintodos, 4, 0, 1, 1)
        self.layout().addWidget(self.label_todolist, 3, 1, 1, 1)
        self.layout().addWidget(self.todolist, 4, 1, 1, 1)
        self.layout().addWidget(self.label_notes, 5, 0, 1, 2)
        self.layout().addWidget(self.notes, 6, 0, 1, 2)


class Home(QScrollArea):
    def __init__(self, parent: QMainWindow, todos: QTabWidget, notes: QTabWidget):
        """
        Display a scrollable area for "Widget" class.

        Args:
            parent (QMainWindow): Parent of this widget (main window)
            todos (QTabWidget): Todos widget of parent
            notes (QTabWidget): Notes widget of parent
        """        
        
        super().__init__(parent)
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setAlignment(align_center)
        self.setWidget(Widget(parent, todos, notes))