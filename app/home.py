import sys
import locale
import getpass
import os
import sqlite3
from PyQt6.QtCore import Qt, QStringListModel, QSortFilterProxyModel, QRegularExpression
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


class Home(QLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.setAlignment(align_center)
        self.setText("This page planned for making.\nYou can look other pages at the moment.")
    
       
if __name__ == "__main__":
    application = QApplication(sys.argv)

    window = QMainWindow()
    window.setStatusBar(QStatusBar(window))
    window.setStatusTip(_('Copyright (C) 2024 MuKonqi (Muhammed S.), licensed under GPLv3 or later'))
    window.setGeometry(0, 0, 960, 540)
    window.setWindowTitle("Nottodbox: Home")
    
    widget = QWidget(parent = window)
    widget.setLayout(QGridLayout(widget))
    widget.layout().addWidget(Home(parent = widget))
    
    window.setCentralWidget(widget)
    window.show()

    application.exec()