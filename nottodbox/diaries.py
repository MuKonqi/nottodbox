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

# Credit for TextFormatter class: 
# <https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp>


import sys
sys.dont_write_bytecode = True


import getpass
import sqlite3
import datetime
from settings import settingsdb
from widgets.dialogs import ColorDialog
from widgets.pages import NormalPage, BackupPage
from gettext import gettext as _
from PyQt6.QtGui import QMouseEvent, QPainter, QColor
from PyQt6.QtCore import Qt, QDate, QRect, QPoint
from PyQt6.QtWidgets import *


diaries = {}
actions = {}
today = QDate.currentDate()

username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"

setting_autosave, setting_format, setting_highlight = settingsdb.getModuleSettings("diaries")
if setting_highlight == "default":
    setting_highlight = "#376296"


class DiariesDB:
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}diaries.db")
        self.cur = self.db.cursor()
        self.widgets = {}
    
    def checkIfTheDiaryExists(self, name: str) -> bool:
        self.cur.execute("select * from __main__ where name = ?", (name,))
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
        
    def checkIfTheDiaryBackupExists(self, name: str) -> bool:
        self.cur.execute(f"select backup from __main__ where name = ?", (name,))
        fetch = self.cur.fetchone()[0]
        
        if fetch == None or fetch == "":
            return False
        else:
            return True
        
    def checkIfTheTableExists(self) -> bool:
        try:
            self.cur.execute("select * from __main__")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def clearContent(self, name: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        fetch_before = self.getContent(name)
        
        if QDate.fromString(name, "dd.MM.yyyy") != today:
            self.cur.execute("select outdated from __main__ where name = ?", (name,))
            check_outdated = self.cur.fetchone()[0]

            if check_outdated == "yes":
                self.cur.execute(
                    "update __main__ set content = ?, modification = ?, outdated = ? where name = ?", 
                    ("", date, "yes", name))
                
            elif check_outdated == "no":
                self.cur.execute(
                    "update __main__ set content = ?, backup = ?, modification = ?, outdated = ? where name = ?", 
                    ("", fetch_before, date, "yes", name))

        else:            
            self.cur.execute("update __main__ set content = ?, backup = ?, modification = ?, outdated = ? where name = ?",
                             ("", fetch_before, date, "no", name))
        
        self.db.commit()
        
        fetch_after = self.getContent(name)
        
        if fetch_after == "" or fetch_after == None:
            return True
        else:
            return False
        
    def createTable(self) -> bool:
        self.cur.execute("""
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
        self.db.commit()
        
        return self.checkIfTheTableExists()
    
    def deleteNote(self, name) -> bool:
        self.cur.execute("delete from __main__ where name = ?", (name,))
        self.db.commit()
        
        call = self.checkIfTheDiaryExists(name)
        
        if call:
            return False
        else:
            return True
        
    def getAutosave(self, name: str) -> str:
        self.cur.execute("select autosave from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getBackup(self, name: str) -> str:
        self.cur.execute("select backup from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch

    def getContent(self, name: str) -> str:
        self.cur.execute("select content from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
        
    def getFormat(self, name: str) -> str:
        self.cur.execute("select format from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
    
    def getHighlight(self, name: str) -> str:
        self.cur.execute("select highlight from __main__ where name = ?", (name,))
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = "global"
        return fetch
        
    def getInformations(self, name: str) -> str:
        self.cur.execute("select modification from __main__ where name = ?", (name,))
        return self.cur.fetchone()
        
    def getNames(self) -> list:
        self.cur.execute("select name, highlight from __main__")
        return self.cur.fetchall()
    
    def renameDiary(self, name: str, newname: str) -> bool:
        self.cur.execute("update __main__ set name = ? where name = ?", (newname, name))
        self.db.commit()

        try:
            self.cur.execute("select * from __main__ where name = ?", (newname,))
            self.cur.fetchone()[0]
            return True
            
        except TypeError:
            return False
        
    def recreateTable(self) -> bool:
        self.cur.execute("DROP TABLE IF EXISTS __main__")
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            return False
        else:
            return self.createTable()
    
    def restoreContent(self, name: str) -> tuple:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute("select content, backup from __main__ where name = ?", (name,))
        fetch_before = self.cur.fetchone()
        
        if fetch_before[1] == None or fetch_before[1] == "":
            return "no-backup", False
        
        if QDate.fromString(name, "dd.MM.yyyy") != today:
            self.cur.execute("select outdated from __main__ where name = ?", (name,))
            check_outdated = self.cur.fetchone()[0]

            if check_outdated == "yes":
                self.cur.execute(
                    "update __main__ set content = ?, modification = ?, outdated = ?, where name = ?", 
                    (fetch_before[1], date, "yes", name))
                
            elif check_outdated == "no":
                self.cur.execute(
                    "update __main__ set content = ?, backup = ?, modification = ?, outdated = ?, where name = ?", 
                    (fetch_before[1], fetch_before[0], date, "yes", name))

        else:            
            self.cur.execute(
                "update __main__ set content = ?, backup = ?, modification = ?, outdated = ?, where name = ?", 
                (fetch_before[1], fetch_before[0], date, "no", name))

        self.db.commit()
        
        self.cur.execute("select content, backup from __main__ where name = ?", (name,))
        fetch_after = self.cur.fetchone()
        
        if fetch_before[1] == fetch_after[0]:
            return "successful", True
        else:
            return "failed", False
        
    def saveAll(self) -> bool:
        successful = True
        calls = {}
        
        for name in diaries:
            fetch_format = self.getFormat(name)
            
            if fetch_format == "global":
                fetch_format == setting_format
            
            if fetch_format == "plain-text":
                text = diaries[name].input.toPlainText()
                
            elif fetch_format == "markdown":
                text = diaries[name].input.toMarkdown()
                
            elif fetch_format == "html":
                text = diaries[name].input.toHtml()
            
            calls[name] = self.saveDocument(name,
                                            text, 
                                            diaries[name].content, 
                                            False)
            
            if not calls[name]:
                successful = False
                
        return successful

    def saveDocument(self, name: str, content: str, backup: str, autosave: bool) -> bool:        
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        check = self.checkIfTheDiaryExists(name)
        
        if check:
            if autosave:
                self.cur.execute(
                    "update __main__ set content = ?, modification = ? where name = ?", 
                    (content, date, name))
            
            elif QDate.fromString(name, "dd.MM.yyyy") != today:
                self.cur.execute("select outdated from __main__ where name = ?", (name,))
                check_outdated = self.cur.fetchone()[0]
    
                if check_outdated == "yes":
                    self.cur.execute(
                        "update __main__ set content = ?, modification = ?, outdated = ? where name = ?",
                        (content, date, "yes", name)
                    )
                    
                elif check_outdated == "no":
                    self.cur.execute(
                        "update __main__ set content = ?, backup = ?, modification = ?, outdated = ? where name = ?",
                        (content, backup, date, "yes", name)
                    )
            
            else:
                self.cur.execute(
                    "update __main__ set content = ?, backup = ?, modification = ?, outdated = ? where name = ?",
                    (content, backup, date, "no", name)
                )
            
        else:
            if QDate.fromString(name, "dd.MM.yyyy") == today:
                self.cur.execute(
                    """insert into __main__ (name, content, backup, modification, outdated, autosave, format, highlight) 
                    values (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (name, content, '', date, "no", "global", "global", "global"))
            else:
                self.cur.execute(
                    """insert into __main__ (name, content, backup, modification, outdated, autosave, format, highlight) 
                    values (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (name, content, '', date, "yes", "global", "global", "global"))
        self.db.commit()
                        
        self.cur.execute("select content, modification from __main__ where name = ?", (name,))
        control = self.cur.fetchone()

        if control[0] == content and control[1] == date:             
            return True
        else:
            return False
        
    def setAutosave(self, name: str, setting: str) -> bool:
        if not self.checkIfTheDiaryExists(name):
            return False
        
        self.cur.execute("update __main__ set autosave = ? where name = ?", (setting, name))
        self.db.commit()
        
        call = self.getAutosave(name)
        
        if call == setting:
            return True
        else:
            return False
        
    def setFormat(self, name: str, setting: str) -> bool:
        if not self.checkIfTheDiaryExists(name):
            return False
        
        self.cur.execute("update __main__ set format = ? where name = ?", (setting, name))
        self.db.commit()
        
        call = self.getFormat(name)
        
        if call == setting:
            return True
        else:
            return False
        
    def setHighlight(self, name: str, setting: str) -> bool:
        if not self.checkIfTheDiaryExists(name):
            return False
        
        self.cur.execute("update __main__ set highlight = ? where name = ?", (setting, name))
        self.db.commit()
        
        call = self.getHighlight(name)
        
        if call == setting:
            return True
        else:
            return False


diariesdb = DiariesDB()

create_table = diariesdb.createTable()
if not create_table:
    print("[2] Failed to create table")
    sys.exit(2)


class DiariesTabWidget(QTabWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        
        global diaries_parent
        
        diaries_parent = parent
        self.backups = {}
        
        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self.home))
        
        self.modification = QLabel(self.home, alignment=Qt.AlignmentFlag.AlignCenter, 
                             text=_("Modification: "))
        
        self.calendar = DiariesCalendarWidget(self)
        
        self.comeback = QPushButton(self.home, text=_("Come back to today"))
        self.comeback.clicked.connect(lambda: self.calendar.setSelectedDate(today))

        self.refresh = QPushButton(
            self.home, text=_("Refresh today variable (it is {name})").format(name = today.toString("dd.MM.yyyy")))
        self.refresh.clicked.connect(self.refreshToday)

        self.side = QWidget(self.home)
        self.side.setFixedWidth(180)
        self.side.setLayout(QVBoxLayout(self.side))
        
        self.open_create = QPushButton(self.side, text=_("Open/create"))
        self.open_create.clicked.connect(self.openCreate)

        self.show_backup = QPushButton(self.side, text=_("Show backup"))
        self.show_backup.clicked.connect(self.showBackup)

        self.restore = QPushButton(self.side, text=_("Restore content"))
        self.restore.clicked.connect(self.restoreContent)
        
        self.clear_content = QPushButton(self.side, text=_("Clear content"))
        self.clear_content.clicked.connect(self.clearContent)
        
        self.set_highlight = QPushButton(self.side, text=_("Set highlight"))
        self.set_highlight.clicked.connect(self.setHighlight)
        
        self.delete_diary = QPushButton(self.side, text=_("Delete diary"))
        self.delete_diary.clicked.connect(self.deleteDiary)
        
        self.delete_all = QPushButton(self.side, text=_("Delete all"))
        self.delete_all.clicked.connect(self.deleteAll)
        
        self.side.layout().addWidget(self.open_create)
        self.side.layout().addWidget(self.show_backup)
        self.side.layout().addWidget(self.restore)
        self.side.layout().addWidget(self.clear_content)
        self.side.layout().addWidget(self.set_highlight)
        self.side.layout().addWidget(self.delete_diary)
        self.side.layout().addWidget(self.delete_all)
        self.home.layout().addWidget(self.side, 1, 2, 3, 1)
        self.home.layout().addWidget(self.modification, 0, 0, 1, 1)
        self.home.layout().addWidget(self.calendar, 1, 0, 1, 1)
        self.home.layout().addWidget(self.comeback, 2, 0, 1, 1)
        self.home.layout().addWidget(self.refresh, 3, 0, 1, 1)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        
    def checkIfTheDiaryExists(self, name: str, mode: str = "normal") -> bool:
        call = diariesdb.checkIfTheDiaryExists(name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no diary called {name}.").format(name = name))
        
        return call
    
    def checkIfTheDiaryBackupExist(self, name: str, mode: str = "normal") -> bool:
        call = diariesdb.checkIfTheDiaryBackupExists(name)
        
        if not call and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no backup for {name} diary.").format(name = name))
        
        return call 
    
    def clearContent(self) -> None:
        name = self.calendar.selectedDate().toString("dd.MM.yyyy")
        
        if name == "":
            QMessageBox.critical(self, _("Error"), _("Diary name can not be blank."))
            return        
        
        if not self.checkIfTheDiaryExists(name):
            return
        
        call = diariesdb.clearContent(name)
    
        if call:
            QMessageBox.information(self, _("Successful"), _("Content of {name} diary deleted.").format(name = name))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to clear content of {name} diary.").format(name = name))
         
    def closeTab(self, index: int) -> None:
        if index != self.indexOf(self.home):           
            try:
                if not diaries[self.tabText(index).replace("&", "")].closable:
                    self.question = QMessageBox.question(self, 
                                                         _("Question"),
                                                         _("{name} diary not saved.\nDo you want to directly closing or closing after saving it or cancel?")
                                                         .format(name = self.tabText(index).replace("&", "")),
                                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                                                         QMessageBox.StandardButton.Save)
                    
                    if self.question == QMessageBox.StandardButton.Save:
                        call = diariesdb.saveDocument(self.tabText(index).replace("&", ""),
                                                      diaries[self.tabText(index).replace("&", "")].input.toPlainText(),
                                                      diaries[self.tabText(index).replace("&", "")].content, 
                                                      False)
                        
                        if call:
                            self.closable = True
                        else:
                            QMessageBox.critical(self, _("Error"), _("Failed to save {name} diary.").format(name = self.tabText(index).replace("&", "")))
                    
                    elif self.question != QMessageBox.StandardButton.Yes:
                        return
                
                del diaries[self.tabText(index).replace("&", "")]
                
            except KeyError:
                pass
            
            if not str(self.tabText(index).replace("&", "")).endswith(f' {_("(Backup)")}'):
                diaries_parent.dock.widget().removePage(self.tabText(index).replace("&", ""), self)
            
            self.removeTab(index)
        
    def deleteAll(self) -> None:
        call = diariesdb.recreateTable()
        
        if call:
            self.insertInformations("")
            self.calendar.menu.clear()
            actions.clear()
            
            QMessageBox.information(self, _("Successful"), _("All diaries deleted."))

        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all diaries."))
                       
    def deleteDiary(self) -> None:
        name = self.calendar.selectedDate().toString("dd.MM.yyyy")
        
        if name == "":
            QMessageBox.critical(self, _("Error"), _("Diary name can not be blank."))
            return
        
        if not self.checkIfTheDiaryExists(name):
            return
        
        call = diariesdb.deleteNote(name)
            
        if call:
            self.insertInformations("")
            self.calendar.menu.removeAction(actions[name])
            del actions[name]
            
            QMessageBox.information(self, _("Successful"), _("{name} diary deleted.").format(name = name))
            
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {name} diary.").format(name = name))
        
    def insertInformations(self, name: str) -> None: 
        if name != "":
            call = diariesdb.getInformations(name)
        else:
            call = None
    
        try:
            self.modification.setText(_("Modification: ") + call[0])
        except TypeError:
            self.modification.setText(_("Modification: "))
        
    def openCreate(self) -> None:
        name = self.calendar.selectedDate().toString("dd.MM.yyyy")
        
        if name == "":
            QMessageBox.critical(self, _("Error"), _("Diary name can not be blank."))
            return
        
        call = diariesdb.checkIfTheDiaryExists(name)

        if not call:
            actions[name] = self.calendar.menu.addAction(name, lambda name = name: self.calendar.openCreate(name))
        
        diaries_parent.tabwidget.setCurrentIndex(3)
        
        if name in diaries:
            self.setCurrentWidget(diaries[name])
            
        else:
            diaries_parent.dock.widget().addPage(name, self)

            diaries[name] = NormalPage(self, "diaries", today, name, setting_autosave, setting_format, diariesdb)
            self.addTab(diaries[name], name)
            self.setCurrentWidget(diaries[name])
            
    def refreshSettings(self) -> None:
        global setting_autosave, setting_format, setting_highlight

        setting_autosave, setting_format, setting_highlight = settingsdb.getModuleSettings("diaries")
        if setting_highlight == "default":
            setting_highlight = "#376296"
            
    def refreshToday(self) -> None:
        global today
        
        today = QDate.currentDate()
        
        self.calendar.setMaximumDate(today)
        
        self.refresh.setText(_("Refresh today variable (it is {name})").format(name = today.toString("dd.MM.yyyy")))
            
    def restoreContent(self) -> None:
        name = self.calendar.selectedDate().toString("dd.MM.yyyy")
         
        if name == "":
            QMessageBox.critical(self, _("Error"), _("Diary name can not be blank."))
            return
        
        if not self.checkIfTheDiaryExists(name):
            return
        
        if not self.checkIfTheDiaryBackupExist(name):
            return
        
        if QDate.fromString(name, "dd.MM.yyyy") != today:
            question = QMessageBox.question(self, _("Diaries are unique to the day they are written.\nSo, are you sure?"))

            if question != QMessageBox.StandardButton.Yes:
                return
        
        status, call = diariesdb.restoreContent(name)
        
        if status == "successful" and call:
            QMessageBox.information(self, _("Successful"), _("Backup of {name} diary restored.").format(name = name))
        
        elif status == "no-backup" and not call:
            QMessageBox.critical(self, _("Error"), _("There is no backup for {name} diary.").format(name = name))
            
        elif status == "failed" and not call:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup of {name} diary.").format(name = name))
            
    def setHighlight(self) -> None:
        name = self.calendar.selectedDate().toString("dd.MM.yyyy")
        
        if name == "":
            QMessageBox.critical(self, _("Error"), _("Diary name can not be blank."))
            return

        if not self.checkIfTheDiaryExists(name):
            return
        
        highlight = diariesdb.getHighlight(name)
        
        ok, status, qcolor = ColorDialog(self, True, 
            QColor(highlight if highlight != "global" and highlight != "default" 
                   else setting_highlight if highlight == "global" else "#376296"),
            _("Select Highlight Color for {name} Diary").format(name = name.title())).getColor()
        
        if ok:
            if status == "new":
                color = qcolor.name()
                
            elif status == "global":
                color = "global"
                
            elif status == "default":
                color = "default"
                
            call = diariesdb.setHighlight(name, color)
                    
            if call:
                QMessageBox.information(
                    self, _("Successful"), _("Highlight color setted to {color} for {name} diary.")
                    .format(color = color if (status == "new")
                            else (_("global") if status == "global" else _("default")), name = name))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to set highlight color for {name} diary.").format(name = name))
            
    def showBackup(self) -> None:
        name = self.calendar.selectedDate().toString("dd.MM.yyyy")
        
        if name == "":
            QMessageBox.critical(self, _("Error"), _("Diary name can not be blank."))
            return

        if not self.checkIfTheDiaryExists(name):
            return

        if not self.checkIfTheDiaryBackupExist(name):
            return
        
        diaries_parent.tabwidget.setCurrentIndex(3)

        self.backups[name] = BackupPage(self, "diaries", today, name, setting_format, diariesdb)
        self.addTab(self.backups[name], (name + " " + _("(Backup)")))
        self.setCurrentWidget(self.backups[name])


class DiariesCalendarWidget(QCalendarWidget):
    def __init__(self, parent: DiariesTabWidget):
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.setMaximumDate(today)
        self.setStatusTip(_("Double-click on top to opening a diary."))
        self.clicked.connect(
            lambda: self.parent_.insertInformations(self.selectedDate().toString("dd.MM.yyyy")))

        self.parent_.insertInformations(self.selectedDate().toString("dd.MM.yyyy"))
        
        if not hasattr(self, "menu"):
            self.menu = diaries_parent.menuBar().addMenu(_("Diaries"))
        
        for name, highlight in diariesdb.getNames():
            actions[name] = self.menu.addAction(name, lambda name = name: self.openCreate(name))

    def mouseDoubleClickEvent(self, a0: QMouseEvent | None) -> None:
        super().mouseDoubleClickEvent(a0)
        self.openCreate(self.selectedDate().toString("dd.MM.yyyy"))
        
    def openCreate(self, name: str) -> None:
        if name == "":
            QMessageBox.critical(self, _("Error"), _("Diary name can not be blank."))
            return
        
        call = diariesdb.checkIfTheDiaryExists(name)

        if not call:
            actions[name] = self.menu.addAction(name, lambda name = name: self.calendar.openCreate(name))
        
        diaries_parent.tabwidget.setCurrentIndex(3)
        
        if name in diaries:
            self.parent_.setCurrentWidget(diaries[name])
            
        else:
            diaries_parent.dock.widget().addPage(name, self.parent_)

            diaries[name] = NormalPage(self, "diaries", today, name, setting_autosave, setting_format, diariesdb)
            self.parent_.addTab(diaries[name], name)
            self.parent_.setCurrentWidget(diaries[name])
    
    def paintCell(self, painter: QPainter | None, rect: QRect, date: QDate | datetime.date) -> None:
        super().paintCell(painter, rect, date)
        
        call = diariesdb.getNames()
        dates = []
        highlights = {}
        
        for name, highlight in call:
            dates.append(QDate.fromString(name, "dd.MM.yyyy"))
            highlights[QDate.fromString(name, "dd.MM.yyyy")] = highlight

        if date in dates:
            if highlights[date] == "global":
                painter.setBrush(QColor(setting_highlight))
            elif highlights[date] == "default":
                painter.setBrush(QColor("#376296"))
            else:
                painter.setBrush(QColor(highlights[date]))
            
            painter.drawEllipse(rect.topLeft() + QPoint(10, 10), 5, 5)
            
        if date >= today:
            painter.setOpacity(0)