# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024-2025 MuKonqi (Muhammed S.)

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
    

from PySide6.QtCore import Qt, QSettings, QByteArray, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import *
from sidebar import Sidebar
from centralwidget import CentralWidget


class MainWindow(QMainWindow):
    def __init__(self, screenshot_mode: bool = False):
        super().__init__()
        
        self.screenshot_mode = screenshot_mode
        
        self.qsettings = QSettings("io.github.mukonqi", "nottodbox")
        
        self.dock = QDockWidget(self)
        self.dock.setObjectName("Dock")
        self.dock.setFixedWidth(50)
        self.dock.setTitleBarWidget(QWidget())
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        
        self.show()
        self.restoreGeometry(QByteArray(self.qsettings.value("mainwindow/geometry")))
        self.restoreState(QByteArray(self.qsettings.value("mainwindow/state")))
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        
        self.setStatusBar(QStatusBar(self))
        self.setStatusTip(self.tr("There may be important information and tips here. Don't forget to look here!"))
        
        self.dock.setWidget(Sidebar(self, self.dock))
        self.setCentralWidget(CentralWidget(self))
        
    @Slot(QCloseEvent)
    def closeEvent(self, a0: QCloseEvent):
        self.qsettings.setValue("mainwindow/geometry", self.saveGeometry())
        self.qsettings.setValue("mainwindow/state", self.saveState())