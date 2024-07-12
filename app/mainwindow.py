import sys
import locale
import getpass
import os
import subprocess
from home import Home
from notes import Notes
from todos import Todos
from diaries import Diaries
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import Qt
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


class TabWidget(QTabWidget):
    def __init__(self, parent, targets: list, names: list):
        super().__init__(parent)
        
        self.number = -1
        for target in targets:
            self.number += 1
            self.addTab(target, _(names[self.number]))
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.widget = QWidget(self)
        self.widget.setLayout(QGridLayout(self.widget))

        self.notes = Notes(self)
        self.todos = Todos(self)
        self.diaries = Diaries(self)
        self.home = Home(self, self.todos, self.notes)

        self.tabview = TabWidget(self.widget, 
                                 [self.home, self.notes, self.todos, self.diaries], 
                                 [_("Home"), _("Notes"), _("Todos"), _("Diaries")])
        
        self.statusbar = QStatusBar(self)
        self.setStatusTip(_('Copyright (C) 2024 MuKonqi (Muhammed S.), licensed under GPLv3 or later'))
        
        self.file = self.menuBar().addMenu(_('File'))
        self.file.addAction(_('Quit'), QKeySequence("Ctrl+Q"), lambda: sys.exit(0))
        self.file.addAction(_('New'), QKeySequence("Ctrl+N"), lambda: subprocess.Popen(__file__))
        
        self.setWindowTitle("Nottodbox")
        self.setGeometry(0, 0, 960, 540)
        self.setCentralWidget(self.widget)
        self.setStatusBar(self.statusbar)
        self.widget.layout().addWidget(self.tabview)
        
if __name__ == "__main__":
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    application.exec()