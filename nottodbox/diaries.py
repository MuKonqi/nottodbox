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
import sqlite3
import datetime
from gettext import gettext as _
from PyQt6.QtGui import QMouseEvent, QPainter, QColor
from PyQt6.QtCore import Qt, QDate, QRect, QPoint
from PyQt6.QtWidgets import *


diaries = {}
today = QDate.currentDate()

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


class SettingsDB:
    """The settings database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}settings.db")
        self.cur = self.db.cursor()
    
    def getSettings(self) -> tuple:
        """
        Get required settings. If not any string, create them with default value.

        Returns:
            str: Settings' values
        """
        
        try:
            self.cur.execute(f"select value from settings where setting = 'diaries-autosave'")
            self.setting_autosave = self.cur.fetchone()[0]

        except:
            self.cur.execute(f"insert into settings (setting, value) values ('diaries-autosave', 'true')")
            self.db.commit()
            self.setting_autosave = "true"
        
        try:
            self.cur.execute(f"select value from settings where setting = 'diaries-format'")
            self.setting_format = self.cur.fetchone()[0]

        except:
            self.cur.execute(f"insert into settings (setting, value) values ('diaries-format', 'markdown')")
            self.db.commit()
            self.setting_format = "markdown"
    
        return self.setting_autosave, self.setting_format
    
    def setAutoSave(self, signal: Qt.CheckState | int) -> bool:
        """
        Set auto-save setting for global.

        Args:
            signal (Qt.CheckState | int): QCheckBox's signal.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        global setting_autosave
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            setting_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            setting_autosave = "true"
            
        self.cur.execute(f"update settings set value = '{setting_autosave}' where setting = 'diaries-autosave'")
        self.db.commit()
        
        call = self.getSettings()
        
        if call[0] == setting_autosave:
            return True
        elif call[0] == setting_autosave:
            return False
                
    def setFormat(self, index: int) -> bool:
        """
        Set format setting for global.

        Args:
            index (int): Selected index in QComboBox.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        global setting_format
        
        if index == 0:
            setting_format = "plain-text"
        
        elif index == 1:
            setting_format = "markdown"
        
        elif index == 2:
            setting_format = "html"

        self.cur.execute(f"update settings set value = '{setting_format}' where setting = 'diaries-format'")
        self.db.commit()
        
        call = self.getSettings()
        
        if call[1] == setting_format:
            return True
        elif call[1] == setting_format:
            return False
    

settingsdb = SettingsDB()
setting_autosave, setting_format = settingsdb.getSettings()


class DiariesDB:
    """The diaries database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}diaries.db")
        self.cur = self.db.cursor()
        self.widgets = {}
    
    def checkIfTheDiaryExists(self, date: str) -> bool:
        """
        Check if the diary exists.

        Args:
            date (str): Diary date

        Returns:
            bool: True if the diary exists, if not False
        """
        
        self.cur.execute(f"select * from diaries where date = '{date}'")
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
        
    def checkIfTheTableExists(self) -> bool:
        """
        Check if the table exists.

        Returns:
            bool: True if the table exists, if not False
        """
        
        try:
            self.cur.execute("select * from diaries")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
        """
        If the diaries table not exists, create it.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        sql = """
        CREATE TABLE IF NOT EXISTS diaries (
            date TEXT NOT NULL PRIMARY KEY,
            content TEXT,
            backup TEXT,
            edited TEXT NOT NULL,
            outdated TEXT NOT NULL
        );"""

        self.cur.execute(sql)
        self.db.commit()
        
        return self.checkIfTheTableExists()
    
    def deleteContent(self, date: str) -> bool:
        """Delete content of a diary.

        Args:
            date (str): Diary date

        Returns:
            bool: True if successful, False if not
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        fetch_before = self.getContent(date)
        
        if QDate.fromString(date, "dd.MM.yyyy") != today:
            self.cur.execute(f"select outdated from diaries where date = '{date}'")
            check_outdated = self.cur.fetchone()[0]

            if check_outdated == "yes":
                sql = f"""update diaries set content = '',
                edited = '{date_time}', outdated = 'yes' where date = '{date}'"""
            elif check_outdated == "no":
                sql = f"""update diaries set content = '', backup = '{fetch_before}',
                edited = '{date_time}', outdated = 'yes' where date = '{date}'"""

        else:            
            sql = f"""update diaries set content = '', backup = '{fetch_before}',
            edited = '{date_time}', outdated = 'no' where date = '{date}'"""
        
        self.cur.execute(sql)
        self.db.commit()
        
        fetch_after = self.getContent(date)
        
        if fetch_after == "" or fetch_after == None:
            return True
        else:
            return False
    
    def deleteOne(self, date) -> bool:
        """Delete a diary.

        Args:
            date (str): Diary date

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"delete from diaries where date = '{date}'")
        self.db.commit()
        
        call = self.checkIfTheDiaryExists(date)
        
        if call:
            return False
        else:
            return True
    
    def getBackup(self, date: str) -> str:
        """
        Get backup of a diary.

        Args:
            date (str): Diary date.

        Returns:
            str: Content.
        """
        
        self.cur.execute(f"select backup from diaries where date = '{date}'")
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch

    def getContent(self, date: str) -> str:
        """
        Get content of a diary.

        Args:
            date (str): Diary date.

        Returns:
            str: Content.
        """
        
        self.cur.execute(f"select content from diaries where date = '{date}'")
        try:
            fetch = self.cur.fetchone()[0]
        except TypeError:
            fetch = ""
        return fetch
        
    def getInformations(self, date: str) -> str:
        """
        Get creation and edit dates.

        Args:
            date (str): Diary date

        Returns:
            str: Returns creation and edit dates
        """
        
        self.cur.execute(f"select edited from diaries where date = '{date}'")
        return self.cur.fetchone()
        
    def getNames(self) -> list:
        """Get all diaries' names.

        Returns:
            list: List of all diaries' names.
        """
        
        self.cur.execute("select date from diaries")
        return self.cur.fetchall()
    
    def renameDiary(self, date: str, newname: str) -> bool:
        """
        Rename a diary.

        Args:
            date (str): Old date
            newname (str): New date

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        self.cur.execute(f"update diaries set date = '{newname}' where date = '{date}'")
        self.db.commit()

        try:
            self.cur.execute(f"select * from diaries where date = '{newname}'")
            self.cur.fetchone()[0]
            return True
            
        except TypeError:
            return False
        
    def recreateTable(self) -> bool:
        """Recreates the diaries table.

        Returns:
            bool: True if successful, False if not
        """
        
        self.cur.execute(f"DROP TABLE IF EXISTS diaries")
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            return False
        else:
            return self.createTable()
    
    def restoreContent(self, date: str) -> tuple:
        """
        Restore content of diary.
        
        Args:
            date (str): Diary date
            
        Returns:
            tuple: Status and True if successful, False if unsuccesful
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.cur.execute(f"select content, backup from diaries where date = '{date}'")
        fetch_before = self.cur.fetchone()
        
        if fetch_before[1] == None or fetch_before[1] == "":
            return "no-backup", False
        
        if QDate.fromString(date, "dd.MM.yyyy") != today:
            self.cur.execute(f"select outdated from diaries where date = '{date}'")
            check_outdated = self.cur.fetchone()[0]

            if check_outdated == "yes":
                sql = f"""update diaries set content = '{fetch_before[1]}',
                edited = '{date_time}', outdated = 'yes' where date = '{date}'"""
            elif check_outdated == "no":
                sql = f"""update diaries set content = '{fetch_before[1]}', backup = '{fetch_before[0]}',
                edited = '{date_time}', outdated = 'yes' where date = '{date}'"""

        else:            
            sql = f"""update diaries set content = '{fetch_before[1]}', backup = '{fetch_before[0]}',
            edited = '{date_time}', outdated = 'no' where date = '{date}'"""

        self.cur.execute(sql)
        self.db.commit()
        
        self.cur.execute(f"select content, backup from diaries where date = '{date}'")
        fetch_after = self.cur.fetchone()
        
        if fetch_before[1] == fetch_after[0]:
            return "successful", True
        else:
            return "failed", False
        
    def saveAll(self) -> bool:
        """
        Save all diaries.
        If there is such a diary, create it.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        successful = True
        calls = {}
        
        for date in diaries:
            calls[date] = self.saveOne(date,
                                       diaries[date].input.toPlainText(), 
                                       diaries[date].content, 
                                       False)
            
            if calls[date] == False:
                successful = False
                
        return successful

    def saveOne(self, date: str, content: str, backup: str, autosave: bool) -> bool:        
        """
        Save a diary.
        If there is such a diary, create it.
        
        Args:
            date (str): Diary date
            content (str): Content of diary
            backup (str): Backup of diary
            autosave (bool): True if the caller is "auto-save", false if it is not
            
        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        check = self.checkIfTheDiaryExists(date)
        
        if check:
            if autosave:
                sql = f"""update diaries set content = '{content}',
                edited = '{date_time}' where date = '{date}'"""
            
            elif QDate.fromString(date, "dd.MM.yyyy") != today:
                self.cur.execute(f"select outdated from diaries where date = '{date}'")
                check_outdated = self.cur.fetchone()[0]
    
                if check_outdated == "yes":
                    sql = f"""update diaries set content = '{content}',
                    edited = '{date_time}', outdated = 'yes' where date = '{date}'"""
                elif check_outdated == "no":
                    sql = f"""update diaries set content = '{content}', backup = '{backup}',
                    edited = '{date_time}', outdated = 'yes' where date = '{date}'"""
            
            else: 
                sql = f"""update diaries set content = '{content}', backup = '{backup}',
                edited = '{date_time}', outdated = 'no' where date = '{date}'"""
            
            self.cur.execute(sql)
            self.db.commit()
            
        else:
            sql = f"""insert into diaries (date, content, backup, edited, outdated) 
                    values ('{date}', '{content}', '', '{date_time}', 'no')"""

            self.cur.execute(sql)
            self.db.commit()
                        
        self.cur.execute(f"select content, edited from diaries where date = '{date}'")
        control = self.cur.fetchone()

        if control[0] == content and control[1] == date_time:             
            return True
        else:
            return False


diariesdb = DiariesDB()

create_table = diariesdb.createTable()
if not create_table:
    print("[2] Failed to create table")
    sys.exit(2)


class DiariesTabWidget(QTabWidget):
    """The "Diaries" tab widget class."""
    
    def __init__(self, parent: QMainWindow) -> None:
        """Init and then set.

        Args:
            parent (QMainWindow): Main window.
        """
        
        super().__init__(parent)
        
        global diaries_parent
        
        diaries_parent = parent
        self.backups = {}
        
        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self.home))
        
        self.edited = QLabel(self.home, alignment=Qt.AlignmentFlag.AlignCenter, 
                             text=_("Edited: "))
        
        self.calendar = DiariesCalendarWidget(self)
        
        self.comeback_button = QPushButton(self.home, text=_("Come back to today"))
        self.comeback_button.clicked.connect(lambda: self.calendar.setSelectedDate(today))

        self.update_button = QPushButton(self.home,
                                            text=_("Update today variable (it is {date})").format(date = today.toString("dd.MM.yyyy")))
        self.update_button.clicked.connect(self.updateToday)

        self.side = QWidget(self.home)
        self.side.setFixedWidth(150)
        self.side.setLayout(QVBoxLayout(self.side))
        
        self.open_create_button = QPushButton(self.side, text=_("Open/create diary"))
        self.open_create_button.clicked.connect(
            lambda: self.openCreate(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.show_backup_button = QPushButton(self.side, text=_("Show backup"))
        self.show_backup_button.clicked.connect(
            lambda: self.showBackup(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.restore_button = QPushButton(self.side, text=_("Restore content"))
        self.restore_button.clicked.connect(
            lambda: self.restoreContent(self.calendar.selectedDate().toString("dd.MM.yyyy")))
        
        self.delete_content_button = QPushButton(self.side, text=_("Delete content"))
        self.delete_content_button.clicked.connect(
            lambda: self.deleteContent(self.calendar.selectedDate().toString("dd.MM.yyyy")))
        
        self.delete_diary_button = QPushButton(self.side, text=_("Delete diary"))
        self.delete_diary_button.clicked.connect(
            lambda: self.deleteDiary(self.calendar.selectedDate().toString("dd.MM.yyyy")))
        
        self.delete_all_button = QPushButton(self.side, text=_("Delete all diaries"))
        self.delete_all_button.clicked.connect(
            self.deleteAll)
        
        self.format = QComboBox(self)
        self.format.addItems([_("Format: Plain text"), _("Format: Markdown"), _("Format: HTML")])
        self.format.setEditable(False)
        if setting_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif setting_format == "markdown":
            self.format.setCurrentIndex(1)
        elif setting_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)        
        
        self.autosave = QCheckBox(self, text=_("Enable auto-save"))
        if setting_autosave == "true":
            self.autosave.setChecked(True)
        self.autosave.setStatusTip(_("Auto-saves do not change backups."))
        try:
            self.autosave.checkStateChanged.connect(self.setAutoSave)
        except:
            self.autosave.stateChanged.connect(self.setAutoSave)
        
        self.side.layout().addWidget(self.open_create_button)
        self.side.layout().addWidget(self.show_backup_button)
        self.side.layout().addWidget(self.restore_button)
        self.side.layout().addWidget(self.delete_content_button)
        self.side.layout().addWidget(self.delete_diary_button)
        self.side.layout().addWidget(self.delete_all_button)
        self.side.layout().addWidget(self.format)
        self.side.layout().addWidget(self.autosave)
        self.home.layout().addWidget(self.side, 1, 2, 2, 1)
        self.home.layout().addWidget(self.edited, 0, 0, 1, 2)
        self.home.layout().addWidget(self.calendar, 1, 0, 1, 2)
        self.home.layout().addWidget(self.comeback_button, 2, 0, 1, 1)
        self.home.layout().addWidget(self.update_button, 2, 1, 1, 1)
        
        self.addTab(self.home, _("Home"))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        
    def checkIfTheDiaryExists(self, date: str, mode: str = "normal") -> None:
        """
        Check if the diary exists.

        Args:
            date (str): Diary date
            mode (str, optional): Inverted mode for deleting etc. Defaults to "normal".
        """
        
        call = diariesdb.checkIfTheDiaryExists(date)
        
        if call == False and mode == "normal":
            QMessageBox.critical(self, _("Error"), _("There is no diary called {date}.").format(date = date))
        
        return call
         
    def closeTab(self, index: int) -> None:
        """
        Close a tab.

        Args:
            index (int): Index of tab
        """
        
        if index != self.indexOf(self.home):           
            try:
                if not diaries[self.tabText(index).replace("&", "")].closable:
                    self.question = QMessageBox.question(self, 
                                                         _("Question"),
                                                         _("{date} diary not saved.\nDo you want to directly closing or closing after saving it or cancel?")
                                                         .format(date = self.tabText(index).replace("&", "")),
                                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                                                         QMessageBox.StandardButton.Save)
                    
                    if self.question == QMessageBox.StandardButton.Save:
                        call = diariesdb.saveOne(self.tabText(index).replace("&", ""),
                                                 diaries[self.tabText(index).replace("&", "")].input.toPlainText(),
                                                 diaries[self.tabText(index).replace("&", "")].content, 
                                                 False)
                        
                        if call:
                            self.closable = True
                        else:
                            QMessageBox.critical(self, _("Error"), _("Failed to save {date} diary.").format(date = self.tabText(index).replace("&", "")))
                    
                    elif self.question != QMessageBox.StandardButton.Yes:
                        return
                
                del diaries[self.tabText(index).replace("&", "")]
                
            except KeyError:
                pass
            
            diaries_parent.dock.widget().removePage(self.tabText(index).replace("&", ""), self)
            self.removeTab(index)
        
    def deleteAll(self) -> None:
        """Delete all diaries."""
        
        call = diariesdb.recreateTable()
        
        self.insertInformations("")
    
        if call:
            QMessageBox.information(self, _("Successful"), _("All diaries deleted."))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete all diaries."))
        
    def deleteContent(self, date: str) -> None:
        """
        Delete content of a diary.

        Args:
            date (str): Diary date
        """
        
        if date == "" or date == None:
            QMessageBox.critical(self, _("Error"), _("Diary date can not be blank."))
            return        
        
        if self.checkIfTheDiaryExists(date) == False:
            return
        
        call = diariesdb.deleteContent(date)
    
        if call:
            QMessageBox.information(self, _("Successful"), _("Content of {date} diary deleted.").format(date = date))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete content of {date} diary.").format(date = date))
                       
    def deleteDiary(self, date: str) -> None:
        """
        Delete a diary.

        Args:
            date (str): Diary date
        """
        
        if date == "" or date == None:
            QMessageBox.critical(self, _("Error"), _("Diary date can not be blank."))
            return
        
        if self.checkIfTheDiaryExists(date) == False:
            return
        
        call = diariesdb.deleteOne(date)

        self.insertInformations("")
            
        if call:
            QMessageBox.information(self, _("Successful"), _("{date} diary deleted.").format(date = date))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to delete {date} diary.").format(date = date))
        
    def insertInformations(self, date: str) -> None:
        """Insert edit date.

        Args:
            date (str): Diary date.
        """
        
        if date != "":
            call = diariesdb.getInformations(date)
        else:
            call = None
    
        try:
            self.edited.setText(_("Edited: ") + call[0])
        except TypeError:
            self.edited.setText(_("Edited: "))
        
    def openCreate(self, date: str) -> None:
        """Open or create a diary.

        Args:
            date (str): Diary date
        """
        
        if date == "" or date == None:
            QMessageBox.critical(self, _("Error"), _("Diary date can not be blank."))
            return
        
        call = diariesdb.checkIfTheDiaryExists(date)

        if QDate().fromString(date, "dd.MM.yyyy") != today and not call:
            QMessageBox.critical(self, _("Error"), _("You can not create a diary for past."))
            return
        
        diaries_parent.tabwidget.setCurrentIndex(3)
        
        if date in diaries:
            self.setCurrentWidget(diaries[date])
            
        else:
            diaries_parent.dock.widget().addPage(date, self)

            diaries[date] = DiariesDiary(self, date, diariesdb)
            self.addTab(diaries[date], date)
            self.setCurrentWidget(diaries[date])
            
    def restoreContent(self, date: str) -> None:
        """Restore content of a diary.

        Args:
            date (str): Diary date
        """
        
        if date == "" or date == None:
            QMessageBox.critical(self, _("Error"), _("Diary date can not be blank."))
            return
        
        if self.checkIfTheDiaryExists(date) == False:
            return
        
        if QDate.fromString(date, "dd.MM.yyyy") != today:
            question = QMessageBox.question(self, 
                                            _("Question"),
                                            _("Diaries are special for that day, editing an old diary can take away the meaning of the diary."
                                            +"\nSo, are you sure you want to restoring content of it?"))

            if question != QMessageBox.StandardButton.Yes:
                return
        
        status, call = diariesdb.restoreContent(date)
        
        if status == "successful" and call:
            QMessageBox.information(self, _("Successful"), _("Backup of {date} diary restored.").format(date = date))
        
        elif status == "no-backup" and not call:
            QMessageBox.critical(self, _("Error"), _("There is no backup for {date} diary.").format(date = date))
            
        elif status == "failed" and not call:
            QMessageBox.critical(self, _("Error"), _("Failed to restore backup of {date} diary.").format(date = date))
            
    def setAutoSave(self, signal: Qt.CheckState | int) -> None:
        """
        Set auto-save setting for global.

        Args:
            signal (Qt.CheckState | int): QCheckBox's signal.
        """
        
        global setting_autosave
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            setting_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            setting_autosave = "true"
            
        call = settingsdb.setAutoSave(signal)
        
        if call == False:
            QMessageBox.critical(self, _("Erorr"), _("Failed to set auto-save setting."))
                
    def setFormat(self, index: int) -> None:
        """
        Set format setting for global.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        global setting_format
        
        if index == 0:
            setting_format = "plain-text"
        
        elif index == 1:
            setting_format = "markdown"
        
        elif index == 2:
            setting_format = "html"
            
        call = settingsdb.setFormat(index)
        
        if call == False:
            QMessageBox.critical(self, _("Erorr"), _("Failed to set format setting."))
            
    def showBackup(self, date: str) -> None:
        """
        Show backup of a diary.

        Args:
            date (str): Diary date
        """
        
        if date == "" or date == None:
            QMessageBox.critical(self, _("Error"), _("Diary date can not be blank."))
            return

        if self.checkIfTheDiaryExists(date) == False:
            return
        
        diaries_parent.tabwidget.setCurrentIndex(3)
        diaries_parent.dock.widget().addPage(date + " " + _("(Backup)"), self)

        self.backups[date] = DiariesBackup(self, date)
        self.addTab(self.backups[date], (date + " " + _("(Backup)")))
        self.setCurrentWidget(self.backups[date])
        
    def updateToday(self):
        """Update "today" variable."""
        
        global today
        
        today = QDate.currentDate()
        
        self.update_button.setText(_("Update today variable (it is {date})").format(date = today.toString("dd.MM.yyyy")))


class DiariesDiary(QWidget):
    """A page for diaries."""
    def __init__(self, parent: DiariesTabWidget | QWidget, date: str, database: DiariesDB) -> None:
        """Init and then set page.
        
        Args:
            parent (DiariesTabWidget | QWidget): "Diaries" tab widget in main window or home page
            date (str): Diary date
            database (DiariesDB): Database class
        """
        
        super().__init__(parent)
        
        self.parent_ = parent
        self.date = date
        self.database = database
        self.content = self.database.getContent(date)
        self.setting_autosave = setting_autosave
        self.setting_format = setting_format
        self.closable = True
        
        self.setLayout(QGridLayout(self))
        self.setStatusTip(_("Auto-saves do not change backups."))
        
        self.autosave = QCheckBox(self)
        if QDate().fromString(self.date, "dd.MM.yyyy") == today:
            self.autosave.setText(_("Enable auto-save for this time"))
            if setting_autosave == "true":
                self.autosave.setChecked(True)
            try:
                self.autosave.checkStateChanged.connect(self.setAutoSave)
            except:
                self.autosave.stateChanged.connect(self.setAutoSave)
        else:
            self.autosave.setText(_("Auto-saves disabled for old diaries"))
            self.autosave.setDisabled(True)
            
            self.setting_autosave = "false"
        
        self.input = QTextEdit(self)
        self.input.setPlainText(self.content)
        self.input.textChanged.connect(
            lambda: self.updateOutput(self.input.toPlainText()))
        self.input.textChanged.connect(lambda: self.saveDiary(True))
        
        self.format = QComboBox(self)
        self.format.addItems([_("Format for this time: Plain text"), 
                               _("Format for this time: Markdown"), 
                               _("Format for this time: HTML")])
        self.format.setEditable(False)
        if self.setting_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif self.setting_format == "markdown":
            self.format.setCurrentIndex(1)
        elif self.setting_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.updateOutput(self.content)
        
        self.button = QPushButton(self, text=_("Save"))
        self.button.clicked.connect(self.saveDiary)
        
        self.layout().addWidget(self.autosave, 0, 0, 1, 1)
        self.layout().addWidget(self.input, 1, 0, 1, 1)
        self.layout().addWidget(self.format, 0, 1, 1, 1)
        self.layout().addWidget(self.output, 1, 1, 1, 1)
        self.layout().addWidget(self.button, 2, 0, 1, 2)
        
    def saveDiary(self, autosave: bool = False) -> None:
        """Save a diary.

        Args:
            autosave (bool, optional): _description_. Defaults to False.
        """
        
        self.closable = False
        
        if not autosave or (autosave and self.setting_autosave == "true"):
            if QDate.fromString(self.date, "dd.MM.yyyy") != today:
                question = QMessageBox.question(self, 
                                                _("Question"),
                                                _("Diaries are special for that day, editing an old diary can take away the meaning of the diary."
                                                +"\nSo, are you sure you want to save it?"))

                if question != QMessageBox.StandardButton.Yes:
                    return
            
            call = self.database.saveOne(self.date,
                                         self.input.toPlainText(),
                                         self.content, 
                                         autosave)

            if call:
                self.closable = True
                
                if not autosave:
                    QMessageBox.information(self, _("Successful"), _("Diary {date} saved.").format(date = self.date))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to save {date} diary.").format(date = self.date))
                
    def setAutoSave(self, signal: Qt.CheckState | int) -> None:
        """Set auto-save setting for only this page.

        Args:
            signal (Qt.CheckState | int): QCheckBox's signal.
        """
        
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.setting_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            self.setting_autosave = "true"

    def setFormat(self, index: int) -> None:
        """Set format setting for only this page.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        if index == 0:
            self.setting_format = "plain-text"
        
        elif index == 1:
            self.setting_format = "markdown"
        
        elif index == 2:
            self.setting_format = "html"
            
        self.updateOutput(self.input.toPlainText())
            
    def updateOutput(self, text: str) -> None:
        """Update output when input's text changed or format changed.

        Args:
            text (str): Content
        """
        
        if self.setting_format == "plain-text":
            self.output.setPlainText(text)
        
        elif self.setting_format == "markdown":
            self.output.setMarkdown(text)
        
        elif self.setting_format == "html":
            self.output.setHtml(text)
            

class DiariesBackup(QWidget):
    """A page for diaries' backups."""
    
    def __init__(self, parent: DiariesTabWidget, date: str) -> None:
        """Init and then set page.
        
        Args:
            parent (DiariesTabWidget): "Diaries" tab widget in main window
            date (str): Diary date
        """        
        
        super().__init__(parent)
        
        self.backup = diariesdb.getBackup(date)
        
        self.setting_format = setting_format
        
        self.setLayout(QVBoxLayout(self))
        self.setStatusTip(_("Auto-saves do not change backups."))
            
        self.format = QComboBox(self)
        self.format.addItems([_("Format for this time: Plain text"), 
                               _("Format for this time: Markdown"), 
                               _("Format for this time: HTML")])
        self.format.setEditable(False)
        if self.setting_format == "plain-text":
            self.format.setCurrentIndex(0)
        elif self.setting_format == "markdown":
            self.format.setCurrentIndex(1)
        elif self.setting_format == "html":
            self.format.setCurrentIndex(2)
        self.format.currentIndexChanged.connect(self.setFormat)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.updateOutput(self.backup)
        
        self.button = QPushButton(self, text=_("Restore content"))
        self.button.clicked.connect(lambda: parent.restoreContent(date))
        
        self.layout().addWidget(self.format)
        self.layout().addWidget(self.output)
        self.layout().addWidget(self.button)

    def setFormat(self, index: int) -> None:
        """Set format setting for only this page.

        Args:
            index (int): Selected index in QComboBox.
        """
        
        if index == 0:
            self.setting_format = "plain-text"
        
        elif index == 1:
            self.setting_format = "markdown"
        
        elif index == 2:
            self.setting_format = "html"
            
        self.updateOutput(self.backup)
            
    def updateOutput(self, text: str) -> None:
        """Update output when format changed.

        Args:
            text (str): Content
        """
        
        if self.setting_format == "plain-text":
            self.output.setPlainText(text)
        
        elif self.setting_format == "markdown":
            self.output.setMarkdown(text)
        
        elif self.setting_format == "html":
            self.output.setHtml(text)


class DiariesCalendarWidget(QCalendarWidget):
    """The calendar widget."""
    
    def __init__(self, parent: DiariesTabWidget):
        """Init and set calendar widget.

        Args:
            parent (DiariesTabWidget): "Diaries" tab widget in main window
        """
        
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.setMaximumDate(today)
        self.setStatusTip(_("Double-click on top to opening a diary."))
        self.clicked.connect(
            lambda: self.parent_.insertInformations(self.selectedDate().toString("dd.MM.yyyy")))

        self.parent_.insertInformations(self.selectedDate().toString("dd.MM.yyyy"))
        
        self.setMenu(diariesdb.getNames())
        
    def setMenu(self, call: list):
        """
        Set diaries menu

        Args:
            call (list): diariesdb.getNames function
        """
        
        if not hasattr(self, "menu"):
            self.menu = diaries_parent.menuBar().addMenu(_("Diaries"))
        self.menu.clear()
        
        for name in call:
            self.menu.addAction(name[0], lambda name = name: self.parent_.openCreate(name[0]))
    
    def paintCell(self, painter: QPainter | None, rect: QRect, date: QDate | datetime.date) -> None:
        """
        Override of QCalendarWidget's paintCell function.

        Args:
            painter (QPainter | None): Painter
            rect (QRect): Rect
            date (QDate | datetime.date): Date
        """
        
        super().paintCell(painter, rect, date)
        
        call = diariesdb.getNames()
        dates = []
        
        for name in call:
            dates.append(QDate.fromString(name[0], "dd.MM.yyyy"))
            self.menu.addAction(name[0], lambda name = name: self.parent_.openCreate(name[0]))

        if date in dates:
            painter.setBrush(QColor(55, 98, 150, 255))
            painter.drawEllipse(rect.topLeft() + QPoint(10, 10), 5, 5)
            
        if date >= today:
            painter.setOpacity(0)
            
        self.setMenu(call)
    
    def mouseDoubleClickEvent(self, a0: QMouseEvent | None) -> None:
        """Override of QCalendarWidget's mouseDoubleClickEvent function.

        Args:
            a0 (QMouseEvent | None): Mouse event
        """
        
        super().mouseDoubleClickEvent(a0)
        self.parent_.openCreate(self.selectedDate().toString("dd.MM.yyyy"))