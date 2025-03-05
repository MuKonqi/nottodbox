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
    

from gettext import gettext as _
from PySide6.QtCore import Slot, Qt, QSettings, QByteArray
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import *
from sidebar import SidebarWidget
from home import HomeWidget
from notes import NotesTabWidget, notesdb
from todos import TodosHomePage
from diaries import DiariesTabWidget, diariesdb
from about import AboutWidget
from settings import SettingsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.qsettings = QSettings("io.github.mukonqi", "nottodbox")
        
        self.tabwidget = TabWidget(self)
        
        self.menu_sidebar = self.menuBar().addMenu(_("Sidebar"))
        self.menu_sidebar.addAction(_("Show"), lambda: self.dock.setVisible(True))
        self.menu_sidebar.addAction(_("Hide"), lambda: self.dock.setVisible(False))
        
        self.dock = QDockWidget(self)
        self.dock.setObjectName("DockWidget")
        self.dock.setFixedWidth(150)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                              QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                              QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                  Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.about = AboutWidget(self)
        self.notes = NotesTabWidget(self)
        self.todos = TodosHomePage(self)
        self.diaries = DiariesTabWidget(self)
        self.home = HomeWidget(self, self.todos, self.notes.home, self.diaries.home)
        self.sidebar = SidebarWidget(self, self.notes, self.diaries)
        self.settings = SettingsWidget(self, self.sidebar, self.notes.home, self.todos, self.diaries.home)

        self.tabwidget.load()
        
        self.dock.setWidget(self.sidebar)
    
        self.show()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.setCentralWidget(self.tabwidget)
        self.setStatusBar(QStatusBar(self))
        self.setStatusTip(_("There may be important information and tips here. Don't forget to look here!"))
        self.restoreGeometry(QByteArray(self.qsettings.value("mainwindow/geometry")))
        self.restoreState(QByteArray(self.qsettings.value("mainwindow/state")))
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)

    @Slot(QCloseEvent)
    def closeEvent(self, a0: QCloseEvent):                
        pages = self.dock.widget().open_pages.pages
        
        are_there_unsaved_notes = False
        are_there_unsaved_diaries = False
        is_main_diary_unsaved = False
        closing_confirmed = False
        
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
            self.qsettings.setValue("mainwindow/geometry", self.saveGeometry())
            self.qsettings.setValue("mainwindow/state", self.saveState())
            
            closing_confirmed = True
        
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
                    
                    call_save_todays_diary = self.home.diary.saver.saveChild(False)
                    
                    if not call_save_todays_diary:
                        successful = False
                
                if successful and messages:
                    QMessageBox.information(self, _("Successful"), _("All pages saved."))
                    
                elif not successful:
                    if messages:
                        QMessageBox.critical(self, _("Error"), _("Failed to save some pages."))
                        
                    return a0.ignore()
                
                self.qsettings.setValue("mainwindow/geometry", self.saveGeometry())
                self.qsettings.setValue("mainwindow/state", self.saveState())
                        
                closing_confirmed = True
            
            elif self.question == QMessageBox.StandardButton.Discard:
                closing_confirmed = True
                
        if closing_confirmed:
            for module, page in pages:
                if module == "notes" and not page.endswith(_(" (Backup)")):
                    name, table = str(page).split(" @ ")
                    
                    self.notes.pages[(name, table)].saver_thread.quit()
                    
                elif module == "diaries" and not page.endswith(_(" (Backup)")):
                    name = page
                    
                    self.diaries.pages[(name, "__main__")].saver_thread.quit()
                    
            self.home.diary.saver_thread.quit()
            
            return super().closeEvent(a0)
        
        else:
            a0.ignore()
            
            
class TabWidget(QWidget):
    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.current_index = 0
        
        self.layout_ = QVBoxLayout(self)
        
        self.tabbar = QTabBar(self)
        self.tabbar.setUsesScrollButtons(True)
        self.tabbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabbar.currentChanged.connect(self.tabChanged)
        
        self.container = QStackedWidget(self)
        
    def load(self) -> None:
        self.pages = [self.parent_.home, 
                      self.parent_.notes, self.parent_.todos, self.parent_.diaries, 
                      self.parent_.settings, self.parent_.about]
        
        for page in self.pages:
            self.container.addWidget(page)
            
        self.tabbar.addTab(_("Home"))
        self.tabbar.addTab(_("Notes"))
        self.tabbar.addTab(_("To-dos"))
        self.tabbar.addTab(_("Diaries"))
        self.tabbar.addTab(_("Settings"))
        self.tabbar.addTab(_("About"))
        
        self.setLayout(self.layout_)
        self.layout_.addWidget(self.tabbar)
        self.layout_.addWidget(self.container)
        
    @Slot(int)
    def tabChanged(self, index: int) -> None:
        self.container.setCurrentIndex(index)
        
        if index != self.current_index:
            old_widget = self.container.widget(self.current_index)
            
            if old_widget == self.parent_.home:
                self.parent_.home.diary.disconnectAutosaveConnections()

            elif ((old_widget == self.parent_.diaries or old_widget == self.parent_.notes) and
                old_widget.currentWidget() != old_widget.home and old_widget.currentWidget().mode == "normal"):
                old_widget.currentWidget().disconnectAutosaveConnections()
                
            new_widget = self.container.widget(index)
            
            if new_widget == self.parent_.home:
                self.parent_.home.diary.changeAutosaveConnections()

            elif ((new_widget == self.parent_.diaries or new_widget == self.parent_.notes) and
                new_widget.currentWidget() != new_widget.home and new_widget.currentWidget().mode == "normal"):
                new_widget.currentWidget().changeAutosaveConnections()
            
            self.current_index = index
            
    def setCurrentWidget(self, widget: QWidget) -> None:
        self.tabbar.setCurrentIndex(self.container.indexOf(widget))