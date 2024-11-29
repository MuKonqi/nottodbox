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
    

import getpass
from gettext import gettext as _
from PySide6.QtCore import Qt, QSettings, QByteArray
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import *
from sidebar import SidebarWidget
from home import HomeWidget
from notes import NotesTabWidget, notesdb
from todos import TodosHomePage
from diaries import DiariesTabWidget, diariesdb
from about import AboutWidget
from settings import SettingsWidget


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        self.setGeometry(0, 0, 1000, 700)
        
        self.qsettings = QSettings("io.github.mukonqi", "nottodbox")
        
        self.widget = QWidget(self)
        self.layout_ = QVBoxLayout(self.widget)
        
        self.tabwidget = QTabWidget(self.widget)
        self.tabwidget.setUsesScrollButtons(True)
        
        self.menu_sidebar = self.menuBar().addMenu(_("Sidebar"))
        self.menu_sidebar.addAction(_("Show"), lambda: self.dock.setVisible(True))
        self.menu_sidebar.addAction(_("Hide"), lambda: self.dock.setVisible(False))

        self.notes = NotesTabWidget(self)
        self.todos = TodosHomePage(self)
        self.diaries = DiariesTabWidget(self)
        self.about = AboutWidget(self)
        self.home = HomeWidget(self, self.todos, self.notes.home, self.diaries.home.format, self.diaries.home.autosave)
        self.settings = SettingsWidget(self, self.notes.home, self.todos, self.diaries.home)

        self.tabwidget.addTab(self.home, _("Home"))
        self.tabwidget.addTab(self.notes, _("Notes"))
        self.tabwidget.addTab(self.todos, _("To-dos"))
        self.tabwidget.addTab(self.diaries, _("Diaries"))
        self.tabwidget.addTab(self.settings, _("Settings"))
        self.tabwidget.addTab(self.about, _("About"))
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.setStatusTip(_("There may be important information and tips here. Don't forget to look here!"))
        
        self.dock = QDockWidget(self)
        self.dock.setObjectName("DockWidget")
        self.dock.setFixedWidth(125)
        self.dock.setStyleSheet("margin: 0px")
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                              QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                              QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                  Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock.setWidget(SidebarWidget(self, self.notes, self.diaries))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
            
        self.widget.setLayout(self.layout_)
        self.layout_.addWidget(self.tabwidget)
        self.setCentralWidget(self.widget)
    
        self.show()
        self.restoreGeometry(QByteArray(self.qsettings.value("geometry")))
        self.restoreState(QByteArray(self.qsettings.value("state")))

    def closeEvent(self, a0: QCloseEvent | None):                
        pages = self.dock.widget().open_pages.pages
        
        are_there_unsaved_notes = False
        are_there_unsaved_diaries = False
        is_main_diary_unsaved = False
        
        for module, page in pages:
            if module == "notes" and not page.endswith(_(" (Backup)")):
                name, table = str(page).split(" @ ")
                
                if not are_there_unsaved_notes and not self.notes.pages[(name, table)].closable:
                    are_there_unsaved_notes = True
                
            elif module == "diaries" and not page.endswith(_(" (Backup)")):
                name = page
                
                if not are_there_unsaved_diaries and not self.diaries.pages[(name, "__main__")].closable:
                    are_there_unsaved_diaries = True
                        
        if not self.home.diary.closable:
            is_main_diary_unsaved = True

        if not are_there_unsaved_notes and not are_there_unsaved_diaries and not is_main_diary_unsaved:  
            self.qsettings.setValue("geometry", self.saveGeometry())
            self.qsettings.setValue("state", self.saveState())
            
            return super().closeEvent(a0)
        
        else:
            self.question = QMessageBox.question(self,
                                                 _("Question"),
                                                 _("Some pages are not saved.\nWhat would you like to do?"),
                                                 QMessageBox.StandardButton.SaveAll | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                                                 QMessageBox.StandardButton.SaveAll)

            if self.question == QMessageBox.StandardButton.SaveAll:    
                successful = True
                            
                if are_there_unsaved_notes:
                    messages = True
                    
                    call_save_all_notes = notesdb.saveAll(self.notes.home.format, self.notes.pages)
                    
                    if not call_save_all_notes:
                        successful = False
                
                if are_there_unsaved_diaries:
                    messages = True
                    
                    call_save_all_diaries = diariesdb.saveAll(self.diaries.home.format, self.diaries.pages)
                    
                    if not call_save_all_diaries:
                        successful = False
                    
                if is_main_diary_unsaved:
                    messages = False
                    
                    call_save_todays_diary = self.home.diary.saveChild(False)
                    
                    if not call_save_todays_diary:
                        successful = False
                
                if successful and messages:
                    QMessageBox.information(self, _("Successful"), _("All pages saved."))
                    
                elif not successful:
                    if messages:
                        QMessageBox.critical(self, _("Error"), _("Failed to save some pages."))
                        
                    return a0.ignore()
                
                self.qsettings.setValue("geometry", self.saveGeometry())
                self.qsettings.setValue("state", self.saveState())
                        
                return super().closeEvent(a0)
            
            elif self.question == QMessageBox.StandardButton.Discard:
                return super().closeEvent(a0)
            
            else:
                a0.ignore()