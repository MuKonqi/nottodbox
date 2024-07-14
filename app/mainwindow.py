import sys
import locale
import getpass
import os
import subprocess
from sidebar import Sidebar
from home import Home
from notes import Notes
from todos import Todos
from diaries import Diaries
from PyQt6.QtGui import QCloseEvent, QKeySequence
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
    def __init__(self, parent: QTabWidget | QWidget, targets: list, names: list):
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
        
        self.dock = QDockWidget(self)
        self.dock.setTitleBarWidget(QLabel(self.dock, alignment=align_center, text=_("List of Opened Pages")))
        self.dock.titleBarWidget().setStyleSheet("QLabel{margin: 10px 0px;}")
        self.dock.setFixedWidth(144)
        self.dock.setStyleSheet("QDockWidget{margin: 0px;}")
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                              QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                              QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dock.setWidget(Sidebar(self, self.notes, self.todos, self.diaries))
        
        self.statusbar = QStatusBar(self)
        
        self.menu_file = self.menuBar().addMenu(_('File'))
        self.menu_file.addAction(_('Quit'), QKeySequence("Ctrl+Q"), lambda: sys.exit(0))
        self.menu_file.addAction(_('New'), QKeySequence("Ctrl+N"), lambda: subprocess.Popen(__file__))
        
        self.menu_sidebar = self.menuBar().addMenu(_('Sidebar'))
        self.menu_sidebar.addAction(_('Show'), self.restoreDockWidget)
        self.menu_sidebar.addAction(_('Close'), lambda: self.removeDockWidget(self.dock))
        
        self.setWindowTitle("Nottodbox")
        self.setGeometry(0, 0, 960, 540)
        self.setCentralWidget(self.widget)
        self.setStatusBar(self.statusbar)
        self.setStatusTip(_('Copyright (C) 2024 MuKonqi (Muhammed S.), licensed under GPLv3 or later'))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.widget.layout().addWidget(self.tabview)

    def restoreDockWidget(self):
        self.dock.show()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

    def closeEvent(self, a0: QCloseEvent | None):
        if self.dock.widget().model().stringList() == []:
            return super().closeEvent(a0)
        
        else:
            self.question = QMessageBox.question(self, _("Warning"), _("Some pages are still open.\nAre you sure to exit?"))
            
            if self.question == QMessageBox.StandardButton.Yes:
                return super().closeEvent(a0)
            else:
                a0.ignore()

        
if __name__ == "__main__":
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    application.exec()