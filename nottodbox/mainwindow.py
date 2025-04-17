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
from widgets.tabwidget import TabWidget
from sidebar import SidebarWidget
from home import HomeWidget
from notes import NotesTabWidget, notesdb
from todos import TodosHomePage
from diaries import DiariesTabWidget, diariesdb
from settings import SettingsWidget


class MainWindow(QMainWindow):
    def __init__(self, screenshot_mode: bool = False):
        super().__init__()
        
        self.screenshot_mode = screenshot_mode
        
        self.qsettings = QSettings("io.github.mukonqi", "nottodbox")
        
        self.tabbar = QDockWidget(self)
        self.tabbar.setObjectName("TabBar")
        self.tabbar.setFixedHeight(self.tabbar.height() * 2.3)
        self.tabbar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.tabbar.setAllowedAreas(Qt.DockWidgetArea.TopDockWidgetArea)
        self.tabbar.setTitleBarWidget(QWidget(self.tabbar))
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.tabbar)
        
        self.dock = QDockWidget(self)
        self.dock.setObjectName("Dock")
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                              QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                              QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                  Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        
        self.show()
        self.restoreGeometry(QByteArray(self.qsettings.value("mainwindow/geometry")))
        self.restoreState(QByteArray(self.qsettings.value("mainwindow/state")))
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        
        self.tabwidget = TabWidget(self)
        
        self.menu_sidebar = self.menuBar().addMenu(_("Sidebar"))
        self.menu_sidebar.addAction(_("Show / Hide"), lambda: self.dock.setVisible(True if not self.dock.isVisible() else False))
        
        self.notes = NotesTabWidget(self)
        self.todos = TodosHomePage(self)
        self.diaries = DiariesTabWidget(self)
        self.home = HomeWidget(self, self.todos, self.notes.home, self.diaries.home)
        self.sidebar = SidebarWidget(self, self.notes, self.diaries)
        self.settings = SettingsWidget(self, self.sidebar, self.notes.home, self.todos, self.diaries.home)
        
        self.tabwidget.addPage(_("Home"), self.home, False)
        self.tabwidget.addPage(_("Notes"), self.notes, True)
        self.tabwidget.addPage(_("To-dos"), self.todos)
        self.tabwidget.addPage(_("Diaries"), self.diaries)
        self.tabwidget.addPage(_("Settings"), self.settings, True)
        self.tabwidget.finished()
        
        self.setStatusBar(QStatusBar(self))
        self.setStatusTip(_("There may be important information and tips here. Don't forget to look here!"))
        
        self.dock.setWidget(self.sidebar)
        self.tabbar.setWidget(self.tabwidget.tabbars_widget)
        self.setCentralWidget(self.tabwidget)
        
        self.sidebar.setFixedWidth(self.width() / (len(self.tabwidget.tabs) + len(self.tabwidget.tabbars) - 1) + 10)
        self.settings.tabwidget.tabbars_widget.setFixedWidth(self.width() / (len(self.tabwidget.tabs) + len(self.tabwidget.tabbars) - 1) + 3)

    @Slot(QCloseEvent)
    def closeEvent(self, a0: QCloseEvent):
        if self.screenshot_mode:
            return super().closeEvent(a0)
        
        are_there_unsaved_notes = False
        are_there_unsaved_diaries = False
        is_main_diary_unsaved = False
        closing_confirmed = False
        
        for module, page in self.sidebar.open_pages.pages:
            if module == "notes" and not page.endswith(_(" (Backup)")):
                name, table = str(page).split(" @ ")
                
                if not are_there_unsaved_notes and not self.notes.pages[(name, table)].checkIfTheTextChanged():
                    are_there_unsaved_notes = True
                
            elif module == "diaries" and not page.endswith(_(" (Backup)")):
                name = page
                
                if not are_there_unsaved_diaries and not self.diaries.pages[(name, "__main__")].checkIfTheTextChanged():
                    are_there_unsaved_diaries = True
                        
        if not self.home.diary.checkIfTheTextChanged():
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
            for module, page in self.sidebar.open_pages.pages:
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
            
            
class TabWidget(TabWidget):
    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent, Qt.AlignmentFlag.AlignTop)
        
        self.currentChanged.connect(self.pageChanged)
        
        self.tabbars_layout.setContentsMargins(10, 10, 10, 10)
        
    @Slot(int)
    def pageChanged(self, index: int) -> None:
        if index != self.current_index:
            old_widget = self.widget(self.current_index)
            
            if old_widget == self.parent_.home:
                self.parent_.home.diary.disconnectAutosaveConnections()

            elif ((old_widget == self.parent_.diaries or old_widget == self.parent_.notes) and
                old_widget.currentWidget() != old_widget.home and old_widget.currentWidget().mode == "normal"):
                old_widget.currentWidget().disconnectAutosaveConnections()
                
            new_widget = self.widget(index)
            
            today = (self.parent_.diaries.home.today.toString("dd/MM/yyyy"), "__main__")
            
            if new_widget == self.parent_.home:
                self.parent_.home.diary.changeAutosaveConnections()
                
                if today in self.parent_.diaries.pages or self.parent_.diaries.todays_diary_closed:
                    if today in self.parent_.diaries.pages:
                        self.parent_.diaries.pages[today].removeWidget(self.parent_.diaries.pages[today].widget(0))
                        
                    self.parent_.home.diary_seperator.setVisible(True)
                    self.parent_.home.diary_button.setVisible(True)
                    self.parent_.home.diary.layout_.setContentsMargins(0, 0, 0, 0)
                    self.parent_.home.layout_.addWidget(self.parent_.home.diary, 3, 0, 1, 1)
                    self.parent_.home.diary.setVisible(True)
                    
                    self.parent_.diaries.todays_diary_closed = False

            elif ((new_widget == self.parent_.diaries or new_widget == self.parent_.notes) and
                new_widget.currentWidget() != new_widget.home and new_widget.currentWidget().mode == "normal"):
                new_widget.currentWidget().changeAutosaveConnections()
                
                if today in self.parent_.diaries.pages:
                    self.parent_.home.diary_seperator.setVisible(False)
                    self.parent_.home.diary_button.setVisible(False)
                    self.parent_.home.diary.layout_.setContentsMargins(self.parent_.home.diary.layout_.default_contents_margins)
                    self.parent_.diaries.pages[(self.parent_.diaries.home.today.toString("dd/MM/yyyy"), "__main__")].addWidget(self.parent_.home.diary)
            
            self.current_index = index