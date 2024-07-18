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


import sys
import locale
import gettext
import getpass
import os
import subprocess
import sqlite3
from PyQt6.QtGui import QCloseEvent, QKeySequence
from PyQt6.QtCore import Qt
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
    

with sqlite3.connect(f"{userdata}settings.db", timeout=5.0) as db_settings:
    cur_settings = db_settings.cursor()
    
    sql_settings = """
    CREATE TABLE IF NOT EXISTS settings (
        setting TEXT NOT NULL PRIMARY KEY,
        value TEXT NOT NULL
    );"""
    cur_settings.execute(sql_settings)
    
    db_settings.commit()
    

from sidebar import SidebarListView
from home import HomeScrollableArea
from notes import NotesTabWidget
from todos import Todos
from diaries import DiariesTabWidget


class TabWidget(QTabWidget):
    """Main tab widget.
    
    Methods:
        __init__: Display a tab widget then add tabs.
    """ 
     
    def __init__(self, parent: QMainWindow, targets: list, names: list):
        """Display a tab widget then add tabs.

        Args:
            parent (QMainWindow): Parent of tabwidget.
            targets (list): Widgets of tabs to add.
            names (list): Names of tabs to add.
            
        Attributes:
            number (int) = For range
        """
        
        super().__init__(parent)
        
        self.number = -1
        for target in targets:
            self.number += 1
            self.addTab(target, _(names[self.number]))


class MainWindow(QMainWindow):
    """Main window.
    
    Methods:
        __init__: Display a main window.
        restoreDockWidget: Restore dock widget (sidebar)
        closeEvent: Close main window (if there are open pages ask question)
    """
    
    def __init__(self):
        """Display a main window."""
        
        super().__init__()
        
        self.widget = QWidget(self)
        self.widget.setLayout(QGridLayout(self.widget))

        self.notes = NotesTabWidget(self)
        self.todos = Todos(self)
        self.diaries = DiariesTabWidget(self)
        self.home = HomeScrollableArea(self, self.todos, self.notes)

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
        self.dock.setWidget(SidebarListView(self, self.notes, self.todos, self.diaries))
        
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
        """Restore dock widget (sidebar)"""
        
        self.dock.show()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

    def closeEvent(self, a0: QCloseEvent | None):
        """Close main window (if there are open pages ask question)

        Args:
            a0 (QCloseEvent | None): Qt close event

        Returns:
            super().closeEvent(a0): Close window
            None: Do not close window
        """
        
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