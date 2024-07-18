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


if __name__ == "__main__":
    import sys
    from mainwindow import MainWindow
    from PyQt6.QtWidgets import QApplication
    
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.tabview.setCurrentIndex(0)

    sys.exit(application.exec())


import locale
import gettext
import getpass
import os
from PyQt6.QtCore import Qt, QStringListModel
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


class SidebarListView(QListView):
    """List for open pages."""
    
    def __init__(self, parent: QMainWindow, notes: QTabWidget, todos: QTabWidget, diaries: QTabWidget):
        """
        Display a list for open pages.

        Args:
            parent (QMainWindow): Parent of this widget (main window)
            notes (QTabWidget): Notes widget of parent
            todos (QTabWidget): Todos widget of parent
            diaries (QTabWidget): Diaries widget of parent
        """
        
        super().__init__(parent)
        
        global sidebar_parent, sidebar_model, sidebar_notes, sidebar_todos, sidebar_diaries, sidebar_items
        
        sidebar_parent = parent
        sidebar_notes = notes
        sidebar_todos = todos
        sidebar_diaries = diaries
        
        sidebar_items = {}
        
        sidebar_model = QStringListModel(self)
        
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setModel(sidebar_model)
        
        self.doubleClicked.connect(lambda: self.go(sidebar_model.itemData(self.currentIndex())[0]))
        
    def go(self, key: str):
        """
        Go directly to the selected page.

        Args:
            key (str): Type and name of selected page
        """
        
        if sidebar_items[key] == sidebar_notes:
            length = len(_("Note"))
            
            if key.endswith(_(" (Backup)")):
                sidebar_notes.setCurrentWidget(sidebar_notes.backups[key[(length + 2):].replace(_(" (Backup)"), "")])

            else:
                sidebar_notes.setCurrentWidget(sidebar_notes.notes[key[(length + 2):]])
                
        elif sidebar_items[key] == sidebar_todos:
            length = len(_("Todo list"))
            
            sidebar_todos.setCurrentWidget(sidebar_todos.todolists[key[(length + 2):]])

        elif sidebar_items[key] == sidebar_diaries:
            length = len(_("Diary for"))
            
            if key.endswith(_(" (Backup)")):
                sidebar_diaries.setCurrentWidget(sidebar_diaries.backups[key[(length + 2):].replace(_(" (Backup)"), "")])

            else:
                sidebar_diaries.setCurrentWidget(sidebar_diaries.diaries[key[(length + 2):]])
        
        sidebar_parent.tabview.setCurrentWidget(sidebar_items[key])
        
    def add(text: str, target: QTabWidget):
        """
        Add the open page to list.

        Args:
            text (str): Name of page
            target (QTabWidget): Parent widget of page
        """
        
        stringlist = sidebar_model.stringList()

        if target == sidebar_notes:
            stringlist.append(_("Note: {name}").format(name = text))
            sidebar_items[_("Note: {name}").format(name = text)] = target
            
        elif target == sidebar_todos:
            stringlist.append(_("Todo list: {todolist}").format(todolist = text))
            sidebar_items[_("Todo list: {todolist}").format(todolist = text)] = target
            
        elif target == sidebar_diaries:
            stringlist.append(_("Diary for: {date}").format(date = text))
            sidebar_items[_("Diary for: {date}").format(date = text)] = target
        
        sidebar_model.setStringList(stringlist)
    
    def remove(text: str, target: QTabWidget):
        """
        Remove the open (after calling this should be closed) page from list.

        Args:
            text (str): Name of page
            target (QTabWidget): Parent widget of page
        """
        
        stringlist = sidebar_model.stringList()

        if target == sidebar_notes:
            stringlist.remove(_("Note: {name}").format(name = text))
            try:
                del sidebar_items[_("Note: {name}").format(name = text)]
            except KeyError:
                pass
            
        elif target == sidebar_todos:
            stringlist.remove(_("Todo list: {todolist}").format(todolist = text))
            del sidebar_items[_("Todo list: {todolist}").format(todolist = text)]
            
        elif target == sidebar_diaries:
            stringlist.remove(_("Diary for: {date}").format(date = text))
            try:
                del sidebar_items[_("Diary for: {date}").format(date = text)]
            except KeyError:
                pass
        
        sidebar_model.setStringList(stringlist)