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
    

from PySide6.QtCore import QByteArray, QSettings, Qt, Slot
from PySide6.QtGui import QCloseEvent, QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import *
from .widgets.controls import VSeperator
from .about import AboutPage
from .home import HomePage
from .resources import icons # noqa: F401
from .settings import SettingsPage
from .sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self, screenshot_mode: bool = False):
        super().__init__()
        
        self.screenshot_mode = screenshot_mode
        
        self.qsettings = QSettings("io.github.mukonqi", "nottodbox")
        
        image = QImage(192, 192, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        
        svg_renderer = QSvgRenderer(":icons/window")
        svg_renderer.render(QPainter(image))
        
        self.show()
        self.setWindowIcon(QIcon.fromTheme("io.github.mukonqi.nottodbox", QIcon(QPixmap.fromImage(image))))
        self.restoreGeometry(QByteArray(self.qsettings.value("mainwindow/geometry")))
        self.restoreState(QByteArray(self.qsettings.value("mainwindow/state")))
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        
        self.setStatusBar(QStatusBar(self))
        self.setStatusTip(self.tr("There may be important information and tips here. Don't forget to look here!"))
        
        self.widget = CentralWidget(self)
        self.setCentralWidget(self.widget)
        
    @Slot(QCloseEvent)
    def closeEvent(self, event: QCloseEvent) -> None:
        self.qsettings.setValue("mainwindow/geometry", self.saveGeometry())
        self.qsettings.setValue("mainwindow/state", self.saveState())
        
        self.widget.home.area.closeAll()
        
        return super().closeEvent(event)


class CentralWidget(QWidget):
    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.sidebar = Sidebar(self)
        self.home = HomePage(self)
        self.settings = SettingsPage(self)
        self.about = AboutPage(self)
        
        self.pages = QStackedWidget(self)
        
        self.old_index = 0
        
        self.pages.addWidget(self.home)
        self.pages.addWidget(self.settings)
        self.pages.addWidget(self.about)
        
        self.layout_ = QHBoxLayout(self)
        self.layout_.addWidget(self.sidebar)
        self.layout_.addWidget(VSeperator(self))
        self.layout_.addWidget(self.pages)
        
    @Slot(bool, int)
    def setCurrentIndex(self, checked: bool, index: int) -> None:
        self.pages.setCurrentIndex(self.old_index if not checked else index)
        
        self.old_index = self.pages.currentIndex()