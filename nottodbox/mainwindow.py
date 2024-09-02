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
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"
    

from sidebar import SidebarWidget
from home import HomeScrollArea
from notes import NotesTabWidget, notesdb, notes
from todos import TodosTabWidget
from diaries import DiariesTabWidget, today, diariesdb, diaries


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.widget = QWidget(self)
        self.widget.setLayout(QVBoxLayout(self.widget))
        
        self.tabwidget = QTabWidget(self)
        self.tabwidget.setUsesScrollButtons(True)
        
        self.widget.layout().addWidget(self.tabwidget)
        
        self.setWindowTitle("Nottodbox")
        self.setCentralWidget(self.widget)
        
        self.menu_sidebar = self.menuBar().addMenu(_("Sidebar"))
        self.menu_sidebar.addAction(_("Show"), self.restoreDockWidget)
        self.menu_sidebar.addAction(_("Close"), lambda: self.removeDockWidget(self.dock))

        self.notes = NotesTabWidget(self)
        self.todos = TodosTabWidget(self)
        self.diaries = DiariesTabWidget(self)
        self.home = HomeScrollArea(self, self.todos, self.notes)

        self.tabwidget.addTab(self.home, _("Home"))
        self.tabwidget.addTab(self.notes, _("Notes"))
        self.tabwidget.addTab(self.todos, _("Todos"))
        self.tabwidget.addTab(self.diaries, _("Diaries"))
        
        self.dock = QDockWidget(self)
        self.dock.setFixedWidth(150)
        self.dock.setStyleSheet("margin: 0px")
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                              QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                              QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dock.setWidget(SidebarWidget(self, self.notes, self.todos, self.diaries))
        
        self.statusbar = QStatusBar(self)
        
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.setStatusBar(self.statusbar)
        self.setStatusTip(_("Copyright (C) 2024 MuKonqi (Muhammed S.), licensed under GPLv3 or later"))

    def restoreDockWidget(self):
        self.dock.show()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

    def closeEvent(self, a0: QCloseEvent | None):
        stringlist = self.dock.widget().model1.stringList()
        
        are_there_unsaved_notes = False
        are_there_unsaved_diaries = False
        is_main_diary_unsaved = False
        
        for page in stringlist:
            if page.startswith(_("Note")) and not page.endswith(_(" (Backup)")):
                length = len(_("Note: "))
                if not are_there_unsaved_notes and not notes[page[length:]].closable:
                    are_there_unsaved_notes = True
                    
                    insert_for_question = _("notes")
                
            elif page.startswith(_("Diary")) and not page.endswith(_(" (Backup)")):
                length = len(_("Diary: "))
                if not are_there_unsaved_diaries and not diaries[page[length:]].closable:
                    are_there_unsaved_diaries = True
                    
                    try:
                        insert_for_question += _(" and diaries")
                    except UnboundLocalError:
                        insert_for_question = _("diaries")
                        
        if not self.home.widget().diary.closable:
            try:
                if not _("diaries") in insert_for_question:
                    insert_for_question += _(" and diaries")
            except UnboundLocalError:
                    insert_for_question = _("diaries")
            finally:
                is_main_diary_unsaved = True
                stringlist = None


        if not are_there_unsaved_notes and not are_there_unsaved_diaries and not is_main_diary_unsaved:
            return super().closeEvent(a0)
        
        else:
            self.question = QMessageBox.question(self,
                                                 _("Question"),
                                                 _("Some {pages} are not saved.\n"
                                                   + "Do you want to directly closing or closing after saving them or cancel?")
                                                 .format(pages = insert_for_question),
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.SaveAll | QMessageBox.StandardButton.Cancel,
                                                 QMessageBox.StandardButton.SaveAll)
            
            if self.question == QMessageBox.StandardButton.Yes:
                return super().closeEvent(a0)

            elif self.question == QMessageBox.StandardButton.SaveAll:                
                if are_there_unsaved_notes:
                    call_notes_save_all = notesdb.saveAll()
                
                if are_there_unsaved_diaries:
                    call_diaries_save_all = diariesdb.saveAll()
                    
                if is_main_diary_unsaved:
                    call_diary_save_one = diariesdb.saveNote(today.toString("dd.MM.yyyy"),
                                                            self.home.widget().diary.input.toPlainText(),
                                                            self.home.widget().diary.content,
                                                            False)
                
                if are_there_unsaved_notes and are_there_unsaved_diaries:
                    if call_notes_save_all and call_diaries_save_all:
                        QMessageBox.information(self, _("Successful"), _("All open notes and open diaries saved."))
                    elif call_notes_save_all and not call_diaries_save_all:
                        QMessageBox.warning(self, _("Warning"), _("All open notes saved but failed to save all open diaries."))
                    elif not call_notes_save_all and call_diaries_save_all:
                        QMessageBox.warning(self, _("Warning"), _("All open diaries saved but failed to save all open notes."))
                    elif not call_notes_save_all and not call_diaries_save_all:
                        QMessageBox.critical(self, _("Error"), _("Failed to save all open notes and open diaries."))
                    
                elif are_there_unsaved_notes: 
                    if call_notes_save_all:
                        QMessageBox.information(self, _("Successful"), _("All open notes saved."))
                    elif not call_notes_save_all:
                        QMessageBox.critical(self, _("Error"), _("Failed to save all open notes."))
                
                elif are_there_unsaved_diaries:
                    if call_diaries_save_all:
                        QMessageBox.information(self, _("Successful"), _("All open diaries saved."))
                    elif not call_diaries_save_all:
                        QMessageBox.critical(self, _("Error"), _("Failed to save all open diaries."))
                        
                elif is_main_diary_unsaved:
                    if call_diary_save_one:
                        QMessageBox.information(self, _("Successful"), _("Diary {date} saved.").format(date = today.toString("dd.MM.yyyy")))
                    elif not call_diary_save_one:
                        QMessageBox.critical(self, _("Error"), _("Failed to save diary {date}.").format(date = today.toString("dd.MM.yyyy")))
                        
                return super().closeEvent(a0)
            
            else:
                a0.ignore()