import sys
import locale
import getpass
import os
import sqlite3
from diaries import Diary
from notes import NotesListView
from todos import TodolistListView
from PyQt6.QtCore import Qt, QDate, QStringListModel, QSortFilterProxyModel, QRegularExpression
from PyQt6.QtWidgets import *

def _(text): return text
if "tr" in locale.getlocale()[0][0:]:
    language = "tr"
    # translations = gettext.translation("nottodbox", "po", languages=["tr"])
else:
    language = "en"
    # translations = gettext.translation("nottodbox", "po", languages=["en"])
# translations.install()
# _ = translations.gettext

align_center = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)
    
today = QDate.currentDate()

class Widget(QWidget):
    def __init__(self, parent, todos, notes):
        super().__init__(parent)
        
        self.setLayout(QGridLayout(self))
        
        self.welcome = QLabel(self, alignment=align_center,
                             text=_("Welcome {username}!").format(username = username))
        self.welcome.setStyleSheet("QLabel{font-size: 12pt;}")
        
        self.label_diary = QLabel(self, alignment=align_center,
                                  text=_("Your Diary for {date}").format(date = today.toString("dd.MM.yyyy")))
        
        self.diary = Diary(self, today.toString("dd.MM.yyyy"), "today")
        
        self.label_todolist = QLabel(self, alignment=align_center, 
                                  text=_("List of Your Main Todos"))
        
        self.todolist = TodolistListView(todos, "main", "home")
        
        self.label_notes = QLabel(self, alignment=align_center, 
                                  text=_("List of Your Notes"))
        
        self.notes = NotesListView(notes, "home")
        self.notes.doubleClicked.connect(lambda: parent.tabview.setCurrentWidget(parent.notes))
        
        self.layout().addWidget(self.welcome, 0, 0, 1, 2)
        self.layout().addWidget(self.label_diary, 1, 0, 1, 2)
        self.layout().addWidget(self.diary, 2, 0, 1, 2)
        self.layout().addWidget(self.label_todolist, 3, 0, 1, 1)
        self.layout().addWidget(self.todolist, 4, 0, 1, 1)
        self.layout().addWidget(self.label_notes, 5, 0, 1, 2)
        self.layout().addWidget(self.notes, 6, 0, 1, 2)


class Home(QScrollArea):
    def __init__(self, parent, todos, notes):
        super().__init__(parent)
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setAlignment(align_center)
        self.setWidget(Widget(parent, todos, notes))
    
       
if __name__ == "__main__":    
    sys.stderr.write('[2] Error: "home" module do not support working individual')
    sys.exit(2)