import sys
import locale
import getpass
import os
import sqlite3
import datetime
from PyQt6.QtGui import QMouseEvent, QPainter, QColor
from PyQt6.QtCore import Qt, QDate, QRect, QPoint
from PyQt6.QtWidgets import *

def _(text): return text
if "tr" in locale.getlocale()[0][0:]:
    language = "tr"
    # translations = gettext.translation("nottodbox", "po", languages=["tr"])
else:
    language = "en"
    # translations = gettext.translation("nottodbox", "po", languages=["en"])
# translations.install()
# _ = translations.gettext

align_center = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter

userdate = getpass.getuser()
userdata = f"/home/{userdate}/.local/share/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)

diaries = {}
backups = {}
today = QDate.currentDate()

def db_start():
    with sqlite3.connect(f"{userdata}settings.db", timeout=5.0) as settings_db:
        settings_sql = """
        CREATE TABLE IF NOT EXISTS settings (
            setting TEXT NOT NULL PRIMARY KEY,
            value TEXT NOT NULL
        );"""
        settings_cur = settings_db.cursor()
        settings_cur.execute(settings_sql)
        settings_db.commit()

    with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as diaries_db:
        diaries_sql = """
        CREATE TABLE IF NOT EXISTS diaries (
            date TEXT NOT NULL PRIMARY KEY,
            content TEXT,
            backup TEXT,
            edited TEXT NOT NULL
        );"""
        diaries_cur = diaries_db.cursor()
        diaries_cur.execute(diaries_sql)
        diaries_db.commit()
db_start()

with sqlite3.connect(f"{userdata}settings.db", timeout=5.0) as db_init:
    cur_init = db_init.cursor()

    try:
        cur_init.execute(f"select value from settings where setting = 'diaries-autosave'")
        fetch_autosave = cur_init.fetchone()[0]

    except:
        cur_init.execute(f"insert into settings (setting, value) values ('diaries-autosave', 'true')")
        db_init.commit()
        fetch_autosave = "true"

    try:
        cur_init.execute(f"select value from settings where setting = 'diaries-outmode'")
        fetch_outmode = cur_init.fetchone()[0]

    except:
        cur_init.execute(f"insert into settings (setting, value) values ('diaries-outmode', 'markdown')")
        db_init.commit()
        fetch_outmode = "markdown"


class Diary(QWidget):
    def __init__(self, parent: QTabWidget | QWidget, date: str, mode: str):
        super().__init__(parent)

        self._mode = mode
        self.fetch_autosave = fetch_autosave
        self.fetch_outmode = fetch_outmode

        self.setLayout(QGridLayout(self))

        self.autosave = QCheckBox(self)
        if self._mode == "today":
            self.autosave.setText(_('Enable auto-save for this page'))
            if fetch_autosave == "true":
                self.autosave.setChecked(True)
            try:
                self.autosave.checkStateChanged.connect(self.set_autosave)
            except:
                self.autosave.stateChanged.connect(self.set_autosave)

        else:
            self.autosave.setText(_("Auto-saves disabled for old diaries"))
            self.autosave.setDisabled(True)

        self.input = QTextEdit(self)

        self.outmode = QComboBox(self)
        self.outmode.addItems([_("Out mode for this page: Plain text"),
                               _("Out mode for this page: Markdown"),
                               _("Out mode for this page: HTML")])
        self.outmode.setEditable(False)
        if self.fetch_outmode == "plain-text":
            self.outmode.setCurrentIndex(0)
        elif self.fetch_outmode == "markdown":
            self.outmode.setCurrentIndex(1)
        elif self.fetch_outmode == "html":
            self.outmode.setCurrentIndex(2)
        self.outmode.currentIndexChanged.connect(self.set_outmode)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)

        self.input.textChanged.connect(
            lambda: self.refresh(self.input.toPlainText()))

        if self._mode == "today":
            self.input.textChanged.connect(lambda: self.save(date,
                                                            self.input.toPlainText(),
                                                            datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                                            "auto"))

        self.button = QPushButton(self, text=_('Save'))
        self.button.clicked.connect(lambda: self.save(date,
                                                      self.input.toPlainText(),
                                                      datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

        self.layout().addWidget(self.autosave, 0, 0, 1, 1)
        self.layout().addWidget(self.input, 1, 0, 1, 1)
        self.layout().addWidget(self.outmode, 0, 1, 1, 1)
        self.layout().addWidget(self.output, 1, 1, 1, 1)
        self.layout().addWidget(self.button, 2, 0, 1, 2)

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_open:
            self.cur_open = self.db_open.cursor()

            self.cur_open.execute(f"select content, backup from diaries where date = '{date}'")

            try:
                self.fetch_open = self.cur_open.fetchone()
                self.fetch_content = self.fetch_open[0]
                if self._mode == "today":
                    self.fetch_backup = self.fetch_content
                else:
                    self.fetch_backup = self.fetch_open[1]
                self.input.setPlainText(self.fetch_content)
                self.refresh(self.fetch_content)
            except TypeError:
                self.fetch_backup = ""

    def set_autosave(self, signal: Qt.CheckState | int):
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.fetch_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            self.fetch_autosave = "true"

    def set_outmode(self, index: int):
        if index == 0:
            self.fetch_outmode = "plain-text"

        elif index == 1:
            self.fetch_outmode = "markdown"

        elif index == 2:
            self.fetch_outmode = "html"

        self.refresh(self.input.toPlainText())

    def refresh(self, text: str):
        if self.fetch_outmode == "plain-text":
            self.output.setPlainText(text)

        elif self.fetch_outmode == "markdown":
            self.output.setMarkdown(text)

        elif self.fetch_outmode == "html":
            self.output.setHtml(text)

    def save(self, date: str, content: str, edited: str, mode: str = "manuel"):
        if mode == "manuel":
            if self._mode == "old":
                self.question_save = QMessageBox.question(self, _("Question"),
                                                          _("Diaries are special for that day, editing an old diary can take away the meaning of the diary."
                                                            +"\nSo, are you sure you want to save it?"))

                if self.question_save != QMessageBox.StandardButton.Yes:
                    return

            try:
                with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save1:
                    self.cur_save1 = self.db_save1.cursor()
                    self.cur_save1.execute(f"select content from diaries where date = '{date}'")
                    self.fetch_save1 = self.cur_save1.fetchone()[0]
                
                with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save2:
                    self.sql_save2 = f"""update diaries set content = '{content}', backup = '{self.fetch_backup}',
                    edited = '{edited}' where date = '{date}'"""
                    self.cur_save2 = self.db_save2.cursor()
                    self.cur_save2.execute(self.sql_save2)
                    self.db_save2.commit()

            except TypeError:
                with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save3:
                    self.sql_save3 = f"""insert into diaries (date, content, backup, edited)
                    values ('{date}', '{content}', '', '{edited}'')"""
                    self.cur_save3 = self.db_save3.cursor()
                    self.cur_save3.execute(self.sql_save3)
                    self.db_save3.commit()

            with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save4:
                self.cur_save4 = self.db_save4.cursor()
                self.cur_save4.execute(f"select content from diaries where date = '{date}'")
                self.fetch_save4 = self.cur_save4.fetchone()[0]

            if self.fetch_save4 == content:
                QMessageBox.information(self, _('Successful'), _('Diary for {date} saved.').format(date = date))
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to save diary for {date}.').format(date = date))

        elif mode == "auto" and self.fetch_autosave == "true":
            try:
                with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save1:
                    self.cur_save1 = self.db_save1.cursor()
                    self.cur_save1.execute(f"select content from diaries where date = '{date}'")
                    self.fetch_save1 = self.cur_save1.fetchone()[0]

                with sqlite3.connect(f"{userdata}diaries.db", timeout=1.0) as self.db_save2:
                    self.sql_save2 = f"""update diaries set content = '{content}',
                    edited = '{edited}' where date = '{date}'"""
                    self.cur_save2 = self.db_save2.cursor()
                    self.cur_save2.execute(self.sql_save2)
                    self.db_save2.commit()

            except TypeError:
                with sqlite3.connect(f"{userdata}diaries.db", timeout=1.0) as self.db_save3:
                    self.sql_save3 = f"""insert into diaries (date, content, backup, edited)
                    values ('{date}', '{content}', '', '{edited}')"""
                    self.cur_save3 = self.db_save3.cursor()
                    self.cur_save3.execute(self.sql_save3)
                    self.db_save3.commit()


class Backup(QWidget):
    def __init__(self, parent: QTabWidget | QWidget, date: str):
        super().__init__(parent)

        self.fetch_outmode = fetch_outmode

        self.setLayout(QVBoxLayout(self))

        self.outmode = QComboBox(self)
        self.outmode.addItems([_("Out mode for this page: Plain text"),
                               _("Out mode for this page: Markdown"),
                               _("Out mode for this page: HTML")])
        self.outmode.setEditable(False)
        if self.fetch_outmode == "plain-text":
            self.outmode.setCurrentIndex(0)
        elif self.fetch_outmode == "markdown":
            self.outmode.setCurrentIndex(1)
        elif self.fetch_outmode == "html":
            self.outmode.setCurrentIndex(2)
        self.outmode.currentIndexChanged.connect(self.set_outmode)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        
        self.button = QPushButton(self, text=_('Restore content'))
        self.button.clicked.connect(lambda: Diaries.restore(self, date, "page"))

        self.layout().addWidget(self.outmode)
        self.layout().addWidget(self.output)
        self.layout().addWidget(self.button)

        try:
            with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_showb:
                self.cur_showb = self.db_showb.cursor()
                self.cur_showb.execute(f"select backup from diaries where date = '{date}'")
                self.fetch_showb = self.cur_showb.fetchone()[0]
                self.refresh(self.fetch_showb)
        except TypeError:
            pass

    def set_outmode(self, index: int):
        if index == 0:
            self.fetch_outmode = "plain-text"

        elif index == 1:
            self.fetch_outmode = "markdown"

        elif index == 2:
            self.fetch_outmode = "html"

        self.refresh(self.fetch_showb)

    def refresh(self, text: str):
        if self.fetch_outmode == "plain-text":
            self.output.setPlainText(text)

        elif self.fetch_outmode == "markdown":
            self.output.setMarkdown(text)

        elif self.fetch_outmode == "html":
            self.output.setHtml(text)
            
            
class Calendar(QCalendarWidget):
    def __init__(self, parent: QTabWidget | QWidget):
        super().__init__(parent)
        
        self._parent = parent
        
        self.setMaximumDate(today)
        self.clicked.connect(lambda: Diaries.insert(parent, self.selectedDate()))
        Diaries.insert(parent, self.selectedDate())
    
    def paintCell(self, painter: QPainter | None, rect: QRect, date: QDate | datetime.date):
        super().paintCell(painter, rect, date)
    
        self.list = []
        
        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_refresh:
            self.cur_refresh = self.db_refresh.cursor()
            self.cur_refresh.execute("select date from diaries")
            self.fetch_refresh = self.cur_refresh.fetchall()
        
        for i in range(0, len(self.fetch_refresh)):
            self.list.append(QDate.fromString(self.fetch_refresh[i][0], "dd.MM.yyyy"))

        if date in self.list:
            painter.setBrush(QColor(55, 98, 150, 255))
            painter.drawEllipse(rect.topLeft() + QPoint(10, 10), 5, 5)
            
        if date >= today:
            painter.setOpacity(0)
    
    def mouseDoubleClickEvent(self, a0: QMouseEvent | None):
        super().mouseDoubleClickEvent(a0)
        Diaries.open(self._parent, self.selectedDate().toString("dd.MM.yyyy"))


class Diaries(QTabWidget):
    def __init__(self, parent: QMainWindow | QWidget):
        super().__init__(parent)

        self.setStatusTip(_('Fun fact: Auto-saves and editing/restoring contents for old diaries does not change backups.'))

        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self.home))

        self.edited = QLabel(self.home, alignment=align_center,
                             text=_('Edited:'))

        self.calendar = Calendar(self)

        self.comeback_button = QPushButton(self.home, text=_('Come back to today'))
        self.comeback_button.clicked.connect(lambda: self.calendar.setSelectedDate(today))

        self.refresh_button = QPushButton(self.home,
                                            text=_('Refresh today variable (it is {date})').format(date = today.toString("dd.MM.yyyy")))
        self.refresh_button.clicked.connect(self.refresh)

        self.side = QWidget(self.home)
        self.side.setFixedWidth(144)
        self.side.setLayout(QVBoxLayout(self.side))

        self.open_button = QPushButton(self.side, text=_('Open/create diary'))
        self.open_button.clicked.connect(lambda: self.open(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.show_backup_button = QPushButton(self.side, text=_('Show backup'))
        self.show_backup_button.clicked.connect(lambda: self.show_backup(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.restore_button = QPushButton(self.side, text=_('Restore content'))
        self.restore_button.clicked.connect(lambda: self.restore(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.delete_content_button = QPushButton(self.side, text=_('Delete content'))
        self.delete_content_button.clicked.connect(lambda: self.delete_content(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.delete_diary_button = QPushButton(self.side, text=_('Delete diary'))
        self.delete_diary_button.clicked.connect(lambda: self.delete_diary(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.delete_all_button = QPushButton(self.side, text=_('Delete all diaries'))
        self.delete_all_button.clicked.connect(self.delete_all)

        self.outmode = QComboBox(self)
        self.outmode.addItems([_("Out: Plain text"), _("Out: Markdown"), _("Out: HTML")])
        self.outmode.setEditable(False)
        if fetch_outmode == "plain-text":
            self.outmode.setCurrentIndex(0)
        elif fetch_outmode == "markdown":
            self.outmode.setCurrentIndex(1)
        elif fetch_outmode == "html":
            self.outmode.setCurrentIndex(2)
        self.outmode.currentIndexChanged.connect(self.set_outmode)

        self.autosave = QCheckBox(self, text=_('Enable auto-save'))
        if fetch_autosave == "true":
            self.autosave.setChecked(True)
        try:
            self.autosave.checkStateChanged.connect(self.set_autosave)
        except:
            self.autosave.stateChanged.connect(self.set_autosave)

        self.side.layout().addWidget(self.open_button)
        self.side.layout().addWidget(self.show_backup_button)
        self.side.layout().addWidget(self.restore_button)
        self.side.layout().addWidget(self.delete_content_button)
        self.side.layout().addWidget(self.delete_diary_button)
        self.side.layout().addWidget(self.delete_all_button)
        self.side.layout().addWidget(self.outmode)
        self.side.layout().addWidget(self.autosave)
        self.home.layout().addWidget(self.side, 1, 2, 2, 1)
        self.home.layout().addWidget(self.edited, 0, 0, 1, 2)
        self.home.layout().addWidget(self.calendar, 1, 0, 1, 2)
        self.home.layout().addWidget(self.comeback_button, 2, 0, 1, 1)
        self.home.layout().addWidget(self.refresh_button, 2, 1, 1, 1)

        self.addTab(self.home, _('Home'))
        self.setTabsClosable(True)
        self.setMovable(True)

        self.tabCloseRequested.connect(self.close)

    def close(self, index: int):
        if index != self.indexOf(self.home):
            try:
                del diaries[self.tabText(index).replace("&", "")]
            except KeyError:
                pass
            finally:
                self.removeTab(index)

    def set_autosave(self, signal: Qt.CheckState | int):
        global fetch_autosave

        if signal == Qt.CheckState.Unchecked or signal == 0:
            fetch_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            fetch_autosave = "true"

        with sqlite3.connect(f"{userdata}settings.db", timeout=5.0) as self.db_autosave:
            self.cur_autosave = self.db_autosave.cursor()
            self.cur_autosave.execute(f"update settings set value = '{fetch_autosave}' where setting = 'diaries-autosave'")
            self.db_autosave.commit()

    def set_outmode(self, index: int):
        global fetch_outmode

        if index == 0:
            fetch_outmode = "plain-text"

        elif index == 1:
            fetch_outmode = "markdown"

        elif index == 2:
            fetch_outmode = "html"

        with sqlite3.connect(f"{userdata}settings.db", timeout=5.0) as self.db_outmode:
            self.cur_outmode = self.db_outmode.cursor()
            self.cur_outmode.execute(f"update settings set value = '{fetch_outmode}' where setting = 'diaries-outmode'")
            self.db_outmode.commit()

    def refresh(self):
        global today
        today = QDate.currentDate()

        self.refresh_button.setText(_('refresh today information (it is {date})').format(date = today.toString("dd.MM.yyyy")))
        
    def insert(self, date: QDate):
        date = date.toString("dd.MM.yyyy")
        
        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_insert:
            self.cur_insert = self.db_insert.cursor()
            self.cur_insert.execute(f"select edited from diaries where date = '{date}'")
            self.fetch_insert = self.cur_insert.fetchone()

        try:
            self.edited.setText(f"{_('Edited')}: {self.fetch_insert[0]}")
        except TypeError:
            self.edited.setText(f"{_('Edited')}:")

    def control(self, date: str, mode: str = "normal"):
        try:
            with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_control:
                self.cur_control = self.db_control.cursor()
                self.cur_control.execute(f"select * from diaries where date = '{date}'")
                self.fetch_control = self.cur_control.fetchone()[0]
            return True
        except TypeError:
            if mode == "normal":
                QMessageBox.critical(self, _('Error'), _('There is no diary for {date}.').format(date = date))
            return False

    def open(self, date: str):
        if date in diaries:
            self.setCurrentWidget(diaries[date])

        else:
            if date == today.toString("dd.MM.yyyy"):
                diaries[date] = Diary(self, date, "today")
            elif self.control(date) == True:
                diaries[date] = Diary(self, date, "old")
            else:
                return

            self.addTab(diaries[date], date)
            self.setCurrentWidget(diaries[date])

    def show_backup(self, date: str):
        if self.control(date) == False:
            return

        backups[date] = Backup(self, date)
        self.addTab(backups[date], (date + " " + _("(Backup)")))
        self.setCurrentWidget(backups[date])

    def restore(self, date: str, caller: str = "home"):
        if caller == "home" and self.control(date) == False:
            return

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_restore1:
            self.cur_restore1 = self.db_restore1.cursor()
            self.cur_restore1.execute(f"select content, backup from diaries where date = '{date}'")
            self.fetch_restore1 = self.cur_restore1.fetchone()

        if self.fetch_restore1[1] == None or self.fetch_restore1[1] == "":
            QMessageBox.critical(self, _('Error'), _('There is no backup for diary for {date}.').format(date = date))
            return
        
        if date != today.toString("dd.MM.yyyy"):
            self.question_restore = QMessageBox.question(self, _("Question"),
                                                        _("Diaries are special for that day, restoring content an old diary can take away the meaning of the diary."
                                                        +"\nSo, are you sure you want to restore content?"))

            if self.question_restore != QMessageBox.StandardButton.Yes:
                return

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_restore2:
            if date == today.toString("dd.MM.yyyy"):
                self.sql_restore2 = f"""update diaries set content = '{self.fetch_restore1[1]}',
                backup = '{self.fetch_restore1[0]}' where date = '{date}'"""
            else:
                self.sql_restore2 = f"update diaries set content = '{self.fetch_restore1[1]}' where date = '{date}'"
            self.cur_restore2 = self.db_restore2.cursor()
            self.cur_restore2.execute(self.sql_restore2)
            self.db_restore2.commit()

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_restore3:
            self.cur_restore3 = self.db_restore3.cursor()
            self.cur_restore3.execute(f"select content, backup from diaries where date = '{date}'")
            self.fetch_restore3 = self.cur_restore3.fetchone()

        if self.fetch_restore1[1] == self.fetch_restore3[0]:
            QMessageBox.information(self, _('Successful'), _('Diary for {date} restored.').format(date = date))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to restore diary for {date}.').format(date = date))

    def delete_content(self, date: str):
        if self.control(date) == False:
            return
        
        if date != today.toString("dd.MM.yyyy"):
            self.question_restore = QMessageBox.question(self, _("Question"),
                                                        _("Diaries are special for that day, restoring content an old diary can take away the meaning of the diary."
                                                        +"\nSo, are you sure you want to restore content?"))

            if self.question_restore != QMessageBox.StandardButton.Yes:
                return

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_delete1:
            self.cur_delete1 = self.db_delete1.cursor()
            self.cur_delete1.execute(f"select content from diaries where date = '{date}'")
            self.fetch_delete1 = self.cur_delete1.fetchone()[0]

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_delete2:
            self.cur_delete2 = self.db_delete2.cursor()
            if date == today.toString("dd.MM.yyyy"):
                self.cur_delete2.execute(
                    f"update diaries set content = '', backup = '{self.fetch_delete1}' where date = '{date}'")
            else:
                self.cur_delete2.execute(f"update diaries set content = '' where date = '{date}'")
            self.db_delete2.commit()

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_delete3:
            self.cur_delete3 = self.db_delete3.cursor()
            self.cur_delete3.execute(f"select content from diaries where date = '{date}'")
            self.fetch_delete3 = self.cur_delete3.fetchone()[0]

        if self.fetch_delete3 != None:
            QMessageBox.information(self, _('Successful'), _('Content of diary for {date} deleted.').format(date = date))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete content of diary for {date}.').format(date = date))

    def delete_diary(self, date: str):
        if self.control(date) == False:
            return

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_remove1:
            self.cur_remove1 = self.db_remove1.cursor()
            self.cur_remove1.execute(f"delete from diaries where date = '{date}'")
            self.db_remove1.commit()

        if self.control(date, "inverted") == False:
            QMessageBox.information(self, _('Successful'), _('Diary for {date} deleted.').format(date = date))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete diary for {date}.').format(date = date))

    def delete_all(self):
        try:
            os.remove(f"{userdata}diaries.db")
        except:
            QMessageBox.critical(self, _('Error'), _('Failed to delete all diaries.'))
            return

        if not os.path.isfile(f"{userdata}diaries.db"):
            db_start()

            QMessageBox.information(self, _('Successful'), _('All diaries deleted.'))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete all diaries.'))


if __name__ == "__main__":
    application = QApplication(sys.argv)

    window = QMainWindow()
    window.setStatusBar(QStatusBar(window))
    window.setStatusTip(_('Copyright (C) 2024 MuKonqi (Muhammed S.), licensed under GPLv3 or later'))
    window.setGeometry(0, 0, 960, 540)
    window.setWindowTitle("Nottodbox: Diaries")

    widget = QWidget(parent = window)
    widget.setLayout(QGridLayout(widget))
    widget.layout().addWidget(Diaries(parent = widget))

    window.setCentralWidget(widget)
    window.show()

    application.exec()