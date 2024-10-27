# SPDX-License-Identifier: GPL-3.0-or-later

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
from gettext import gettext as _
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"
    

from sidebar import SidebarWidget
from home import HomeWidget
from notes import NotesTabWidget, notesdb, notes
from todos import TodosWidget
from diaries import DiariesTabWidget, today, diariesdb, diaries
from about import AboutWidget
from settings import SettingsWidget, settingsdb


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.widget = QWidget(self)
        self.layout_ = QVBoxLayout(self.widget)
        
        self.tabwidget = QTabWidget(self.widget)
        self.tabwidget.setUsesScrollButtons(True)
        
        self.menu_sidebar = self.menuBar().addMenu(_("Sidebar"))
        self.menu_sidebar.addAction(_("Show"), lambda: self.dock.setVisible(True))
        self.menu_sidebar.addAction(_("Hide"), lambda: self.dock.setVisible(False))

        self.notes = NotesTabWidget(self)
        self.todos = TodosWidget(self)
        self.diaries = DiariesTabWidget(self)
        self.home = HomeWidget(self, self.todos, self.notes)
        self.settings = SettingsWidget(self, self.notes, self.todos, self.diaries)
        self.about = AboutWidget(self)   

        self.tabwidget.addTab(self.home, _("Home"))
        self.tabwidget.addTab(self.notes, _("Notes"))
        self.tabwidget.addTab(self.todos, _("To-dos"))
        self.tabwidget.addTab(self.diaries, _("Diaries"))
        self.tabwidget.addTab(self.settings, _("Settings"))
        self.tabwidget.addTab(self.about, _("About"))
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        
        self.dock = QDockWidget(self)
        self.dock.setFixedWidth(125)
        self.dock.setStyleSheet("margin: 0px")
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                              QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                              QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                  Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock.setWidget(SidebarWidget(self, self.notes, self.diaries))
        
        self.dock_closed = False
        self.dock_status, self.dock_area, self.dock_mode = settingsdb.getDockSettings()
        if self.dock_area == "left":
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        elif self.dock_area == "right":
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
            
        if self.dock_mode == "floating":
            self.dock.setFloating(True)
        
        if self.dock_status == "disabled":
            self.dock.setVisible(False)
            
        self.widget.setLayout(self.layout_)
        self.layout_.addWidget(self.tabwidget)
        self.dock.dockLocationChanged.connect(self.dockAreaChanged)
        self.dock.topLevelChanged.connect(self.dockModeChanged)
        self.dock.visibilityChanged.connect(self.dockStatusChanged)
            
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        self.setGeometry(0, 0, 1000, 700)
        self.setCentralWidget(self.widget)
        self.setStatusTip(_("There may be important information and tips here. Don't forget to look here!"))

    def closeEvent(self, a0: QCloseEvent | None):        
        pages = self.dock.widget().open_pages.pages
        
        are_there_unsaved_notes = False
        are_there_unsaved_diaries = False
        is_main_diary_unsaved = False
        
        for module, page in pages:
            if module == "notes" and not page.endswith(_(" (Backup)")):
                if not are_there_unsaved_notes and not notes[page].closable:
                    are_there_unsaved_notes = True
                
            elif module == "diaries" and not page.endswith(_(" (Backup)")):
                if not are_there_unsaved_diaries and not diaries[page].closable:
                    are_there_unsaved_diaries = True
                        
        if not self.home.diary.closable:
            is_main_diary_unsaved = True

        if not are_there_unsaved_notes and not are_there_unsaved_diaries and not is_main_diary_unsaved:
            self.dock_closed = True
            return super().closeEvent(a0)
        
        else:
            self.question = QMessageBox.question(self,
                                                 _("Question"),
                                                 _("Some pages are not saved.\nWhat would you like to do?"),
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.SaveAll | QMessageBox.StandardButton.Cancel,
                                                 QMessageBox.StandardButton.SaveAll)
            
            if self.question == QMessageBox.StandardButton.Yes:
                return super().closeEvent(a0)

            elif self.question == QMessageBox.StandardButton.SaveAll:    
                successful = True
                            
                if are_there_unsaved_notes:
                    call_save_all_notes = notesdb.saveAll()
                    
                    if not call_save_all_notes:
                        successful = False
                
                if are_there_unsaved_diaries:
                    call_save_all_diaries = diariesdb.saveAll()
                    
                    if not call_save_all_diaries:
                        successful = False
                    
                if is_main_diary_unsaved:
                    call_save_todays_diary = diariesdb.saveDocument(today.toString("dd.MM.yyyy"),
                                                                    self.home.diary.input.toPlainText(),
                                                                    self.home.diary.content,
                                                                    False)
                    
                    if not call_save_todays_diary:
                        successful = False
                
                if not successful:
                    QMessageBox.critical(self, _("Error"), _("Failed to save some pages."))
                    
                self.dock_closed = True
                        
                return super().closeEvent(a0)
            
            else:
                a0.ignore()
                
    def dockAreaChanged(self, area: Qt.DockWidgetArea) -> None:
        if area == Qt.DockWidgetArea.LeftDockWidgetArea:
            self.dock_area = "left"
        elif area == Qt.DockWidgetArea.RightDockWidgetArea:
            self.dock_area = "right"
            
        call = settingsdb.saveDockSettings(self.dock_status, self.dock_area, self.dock_mode)
        
        if not call:
            QMessageBox.critical(self, _("Error"), _("Can not save new sidebar setting.")) 
    
    def dockModeChanged(self, floating: bool) -> None:
        if floating:
            self.dock_mode = "floating"
        else:
            self.dock_mode = "fixed"
            
        call = settingsdb.saveDockSettings(self.dock_status, self.dock_area, self.dock_mode)
        
        if not call:
            QMessageBox.critical(self, _("Error"), _("Can not save new sidebar setting.")) 
    
    def dockStatusChanged(self, visible: bool) -> None:
        if not self.dock_closed:
            if visible:
                self.dock_status = "enabled"
            else:
                self.dock_status = "disabled"
                        
            call = settingsdb.saveDockSettings(self.dock_status, self.dock_area, self.dock_mode)
            
            if not call:
                QMessageBox.critical(self, _("Error"), _("Can not save new sidebar setting.")) 