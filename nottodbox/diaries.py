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


import datetime
from gettext import gettext as _
from PySide6.QtCore import Slot, QDate, QRect, QPoint
from PySide6.QtGui import QMouseEvent, QPainter, QColor
from PySide6.QtWidgets import *
from databases.documents import DBForDocuments
from widgets.dialogs import ColorDialog
from widgets.options import TabWidget, HomePageForDocuments, OptionsForDocuments
from widgets.others import Action, HSeperator, Label, PushButton, VSeperator


class DiariesDB(DBForDocuments):
    file = "diaries.db"
        
    def createChild(self, name: str, table: str = "__main__"):
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
        return super().createChild(
            """
            insert into __main__ 
            (name, content, backup, modification, outdated, autosave, format, highlight) 
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, "", "", date, "no", "global", "global", "global"),
            name, 
            "__main__")
        
    def createMainTable(self) -> bool:
        return super().createMainTable(
            """
            CREATE TABLE IF NOT EXISTS __main__ (
                name TEXT NOT NULL PRIMARY KEY,
                content TEXT,
                backup TEXT,
                modification TEXT NOT NULL,
                outdated TEXT NOT NULL,
                autosave TEXT NOT NULL,
                format TEXT NOT NULL,
                highlight TEXT NOT NULL
                );""")
        
    def getAll(self) -> list:
        self.cur.execute("select name from __main__")
        return self.cur.fetchall()
    
    def getHighlight(self, name: str) -> str:
        return self.getSetting("highlight", name)
    
    def getOutdated(self, name: str) -> str:
        return self.getData("outdated", name)
        
    def getInformations(self, name: str) -> str:
        self.cur.execute("select modification from __main__ where name = ?", (name,))
        return self.cur.fetchone()
        
    def getAllWithHighlights(self) -> list:
        self.cur.execute("select name, highlight from __main__")
        return self.cur.fetchall()
    
    def restoreContent(self, name: str, table: str = "__main__") -> bool:
        call, content = super().restoreContent(name, table)
        
        if call:
            return self.setBackup(content, name)
        
        else:
            return False
    
    def setBackup(self, content: str, name: str, table: str = "__main__") -> bool:
        changed = False
        
        outdated = self.getOutdated(name)
        
        if QDate.fromString(name, "dd/MM/yyyy") != QDate.currentDate():
            if outdated == "no":
                changed = True
                
                self.cur.execute("update __main__ set backup = ?, outdated = ? where name = ?", (content, "yes", name))
                
        else:
            changed = True
            
            self.cur.execute("update __main__ set backup = ?, outdated = ? where name = ?", (content, "no", name))
        
        if changed:
            self.db.commit()
        
            return self.getBackup(name) == content
        
        else:
            return True
        
    def setHighlight(self, value: str, name: str) -> bool:
        return self.setSetting(value, "highlight", name)


diariesdb = DiariesDB()


class DiariesTabWidget(TabWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent, "diaries")
        
        self.home = DiariesHomePage(self)
        
        self.addTab(self.home, _("Home"))
                    
                    
class DiariesHomePage(HomePageForDocuments):
    def __init__(self, parent: DiariesTabWidget):
        super().__init__(parent, "diaries", diariesdb)
        
        self.today = QDate.currentDate()
        
        self.modification = Label(self, "{}: ".format(_("Modification")))
        
        self.calendar = DiariesCalendarWidget(self)
        
        self.comeback_button = PushButton(self, _("Come Back To Today"))
        self.comeback_button.clicked.connect(lambda: self.calendar.setSelectedDate(self.today))  

        self.options = DiariesOptions(self)
        
        self.layout_.addWidget(self.modification, 0, 0, 1, 1)
        self.layout_.addWidget(self.calendar, 1, 0, 1, 1)
        self.layout_.addWidget(self.comeback_button, 2, 0, 1, 1)
        self.layout_.addWidget(VSeperator(self), 0, 2, 3, 1)
        self.layout_.addWidget(self.options, 0, 3, 3, 1)
        
    def appendAll(self):
        for name in diariesdb.getAll():
            name = name[0]
            
            self.shortcuts[(name, "__main__")] = Action(self, name)
            self.shortcuts[(name, "__main__")].triggered.connect(
                lambda state, name = name: self.shortcutEvent(name, "__main__"))
            self.menu.addAction(self.shortcuts[(name, "__main__")])
            
    def refreshSettings(self) -> None:
        self.refreshSettingsForDocuments()
        
        self.parent_.parent_.home.diary.refresh(self.autosave, self.format)
        
    @Slot(str)
    def setSelectedItems(self, name: str, table: str = "__main__") -> None:
        super().setSelectedItems(name, table)
        
        if name != "":
            call = diariesdb.getData("modification", name, table)
            
        else:
            call = None
    
        self.modification.setText("{}: ".format(_("Modification")) + call if call is not None 
                                  else "{}: ".format(_("Modification")))
        
    def shortcutEvent(self, name: str, table: str = "__main__") -> None:
        self.options.open(False, name, table)
        
        
class DiariesOptions(OptionsForDocuments):
    def __init__(self, parent: DiariesHomePage):
        super().__init__(parent, "diaries", diariesdb)
        
        self.set_highlight_button = PushButton(self, _("Set {} Color").format(_("Highlight")))
        self.set_highlight_button.clicked.connect(self.setHighlight)
        
        self.layout_.addWidget(self.open_button)
        self.layout_.addWidget(self.show_backup_button)
        self.layout_.addWidget(self.restore_content_button)
        self.layout_.addWidget(self.clear_content_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.rename_button)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.set_highlight_button)
        
    @Slot(bool, str)
    def open(self, state: bool, name: str = None, table: str = None) -> None:
        if name is None:
            name = self.parent_.name
        
        if table is None:
            table = self.parent_.table
        
        if self.checkIfItExists(name, table, False):
            super().open(False, name, table)
        
        elif self.checkTheName(name, table):
            if diariesdb.createChild(name):
                self.parent_.shortcuts[(name, table)] = Action(self, name)
                self.parent_.shortcuts[(name, table)].triggered.connect(
                    lambda state: self.parent_.shortcutEvent(name, table))
                self.parent_.menu.addAction(self.parent_.shortcuts[(name, table)]) 
                
                super().open(False, name, table)
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to create {item}.")
                                    .format(item = self.localizedChildItem(name)))
        
    @Slot()
    def setHighlight(self) -> None:
        name = self.parent_.name

        if self.checkIfItExists(name):
            highlight = diariesdb.getHighlight(name)
            
            ok, status, qcolor = ColorDialog(self, True, True, 
                QColor(highlight if highlight != "global" and highlight != "default" 
                    else self.parent_.highlight if highlight == "global" else "#376296"),
                _("Select Highlight Color for {item}")
                .format(item = _("{name} dated diary").format(name = name)).title()).getColor()
            
            if ok:
                if status == "new":
                    color = qcolor.name()
                    
                elif status == "global":
                    color = "global"
                    
                elif status == "default":
                    color = "#376296"
                        
                if not diariesdb.setHighlight(color, name):
                    QMessageBox.critical(self, _("Error"), _("Failed to set highlight color for {item}.")
                                        .format(item = _("{name} dated diary").format(name = name)))
        

class DiariesCalendarWidget(QCalendarWidget):
    def __init__(self, parent: DiariesHomePage):
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.setMaximumDate(self.parent_.today)
        self.setStatusTip(_("Double-click on top to opening a diary."))
        self.selectionChanged.connect(
            lambda: self.parent_.setSelectedItems(self.selectedDate().toString("dd/MM/yyyy")))

        self.parent_.setSelectedItems(self.selectedDate().toString("dd/MM/yyyy"))

    def mouseDoubleClickEvent(self, a0: QMouseEvent | None) -> None:
        super().mouseDoubleClickEvent(a0)
        self.parent_.shortcutEvent(self.parent_.name)
    
    def paintCell(self, painter: QPainter | None, rect: QRect, date: QDate | datetime.date) -> None:
        super().paintCell(painter, rect, date)
        
        dates = []
        highlights = {}
        
        for name, highlight in diariesdb.getAllWithHighlights():
            dates.append(QDate.fromString(name, "dd/MM/yyyy"))
            highlights[QDate.fromString(name, "dd/MM/yyyy")] = highlight

        if date in dates:
            if highlights[date] == "global":
                painter.setBrush(QColor(self.parent_.highlight))
                
            elif highlights[date] == "default":
                painter.setBrush(QColor("#376296"))
                
            else:
                painter.setBrush(QColor(highlights[date]))
            
            painter.drawEllipse(rect.topLeft() + QPoint(10, 10), 5, 5)
            
        if date >= self.parent_.today:
            painter.setOpacity(0)