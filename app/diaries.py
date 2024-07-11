import sys
import locale
import getpass
import os
import sqlite3
import datetime
from PyQt6.QtCore import Qt, QDate
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

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"
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
            name TEXT NOT NULL PRIMARY KEY,
            content TEXT,
            backup TEXT,
            created TEXT NOT NULL,
            edited TEXT
        );"""
        diaries_cur = diaries_db.cursor()
        diaries_cur.execute(diaries_sql)
        diaries_db.commit()
db_start()


class Diary(QWidget):
    def __init__(self, parent, name, mode):
        super().__init__()

        self.mode = mode
        self.fetch_autosave = fetch_autosave
        self.fetch_outmode = fetch_outmode

        self.setParent(parent)
        self.setLayout(QGridLayout(self))

        self.autosave = QCheckBox(parent = self)
        if self.mode == "today":
            self.autosave.setText(_('Enable auto-save for this time'))
            if fetch_autosave == "true":
                self.autosave.setChecked(True)
            try:
                self.autosave.checkStateChanged.connect(self.set_autosave)
            except:
                self.autosave.stateChanged.connect(self.set_autosave)

        else:
            self.autosave.setText(_("Auto-saves disabled for old diaries"))
            self.autosave.setDisabled(True)

        self.input = QTextEdit(parent = self)

        self.outmode = QComboBox(parent = self)
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

        self.output = QTextEdit(parent = self)
        self.output.setReadOnly(True)

        self.input.textChanged.connect(
            lambda: self.refresh(self.input.toPlainText()))

        if self.mode == "today":
            self.input.textChanged.connect(lambda: self.save(name,
                                                            self.input.toPlainText(),
                                                            datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                                            "auto"))

        self.button = QPushButton(parent = self, text = _('Save'))
        self.button.clicked.connect(lambda: self.save(name,
                                                      self.input.toPlainText(),
                                                      datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

        self.layout().addWidget(self.autosave, 0, 0, 1, 1)
        self.layout().addWidget(self.input, 1, 0, 1, 1)
        self.layout().addWidget(self.outmode, 0, 1, 1, 1)
        self.layout().addWidget(self.output, 1, 1, 1, 1)
        self.layout().addWidget(self.button, 2, 0, 1, 2)

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_open:
            self.cur_open = self.db_open.cursor()

            self.cur_open.execute(f"select content, backup from diaries where name = '{name}'")

            try:
                self.fetch_open = self.cur_open.fetchone()
                self.fetch_content = self.fetch_open[0]
                if self.mode == "today":
                    self.fetch_backup = self.fetch_content
                else:
                    self.fetch_backup = self.fetch_open[1]
                self.input.setPlainText(self.fetch_content)
                self.refresh(self.fetch_content)
            except TypeError:
                self.fetch_backup = ""

    def set_autosave(self, signal):
        if signal == Qt.CheckState.Unchecked or signal == 0:
            self.fetch_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            self.fetch_autosave = "true"

    def set_outmode(self, index):
        if index == 0:
            self.fetch_outmode = "plain-text"

        elif index == 1:
            self.fetch_outmode = "markdown"

        elif index == 2:
            self.fetch_outmode = "html"

        self.refresh(self.input.toPlainText())

    def refresh(self, text):
        if self.fetch_outmode == "plain-text":
            self.output.setPlainText(text)

        elif self.fetch_outmode == "markdown":
            self.output.setMarkdown(text)

        elif self.fetch_outmode == "html":
            self.output.setHtml(text)

    def save(self, name, content, date, mode = "manuel"):
        if mode == "manuel":
            if self.mode == "old":
                self.question_save = QMessageBox.question(self, _("Question"),
                                                          _("Diaries are special for that day, editing an old diary can take away the meaning of the diary."
                                                            +"\nSo, are you sure you want to save it?"))

                if self.question_save != QMessageBox.StandardButton.Yes:
                    return

            try:
                with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save1:
                    self.cur_save1 = self.db_save1.cursor()
                    self.cur_save1.execute(f"select content from diaries where name = '{name}'")
                    self.fetch_save1 = self.cur_save1.fetchone()[0]
                
                with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save2:
                    self.sql_save2 = f"""update diaries set content = '{content}', backup = '{self.fetch_backup}',
                    edited = '{date}' where name = '{name}'"""
                    self.cur_save2 = self.db_save2.cursor()
                    self.cur_save2.execute(self.sql_save2)
                    self.db_save2.commit()

            except TypeError:
                with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save3:
                    self.sql_save3 = f"""insert into diaries (name, content, backup, created, edited)
                    values ('{name}', '{content}', '', '{date}', '{date}')"""
                    self.cur_save3 = self.db_save3.cursor()
                    self.cur_save3.execute(self.sql_save3)
                    self.db_save3.commit()

            with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save4:
                self.cur_save4 = self.db_save4.cursor()
                self.cur_save4.execute(f"select content from diaries where name = '{name}'")
                self.fetch_save4 = self.cur_save4.fetchone()[0]

            if self.fetch_save4 == content:
                QMessageBox.information(self, _('Successful'), _('Diary in {name} saved.').format(name = name))
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to save diary in {name}.').format(name = name))

        elif mode == "auto" and self.fetch_autosave == "true":
            try:
                with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_save1:
                    self.cur_save1 = self.db_save1.cursor()
                    self.cur_save1.execute(f"select content from diaries where name = '{name}'")
                    self.fetch_save1 = self.cur_save1.fetchone()[0]

                with sqlite3.connect(f"{userdata}diaries.db", timeout=1.0) as self.db_save2:
                    self.sql_save2 = f"""update diaries set content = '{content}',
                    edited = '{date}' where name = '{name}'"""
                    self.cur_save2 = self.db_save2.cursor()
                    self.cur_save2.execute(self.sql_save2)
                    self.db_save2.commit()

            except TypeError:
                with sqlite3.connect(f"{userdata}diaries.db", timeout=1.0) as self.db_save3:
                    self.sql_save3 = f"""insert into diaries (name, content, backup, created, edited)
                    values ('{name}', '{content}', '', '{date}', '{date}')"""
                    self.cur_save3 = self.db_save3.cursor()
                    self.cur_save3.execute(self.sql_save3)
                    self.db_save3.commit()


class Backup(QWidget):
    def __init__(self, parent, name):
        super().__init__()

        self.fetch_outmode = fetch_outmode

        self.setParent(parent)
        self.setLayout(QVBoxLayout(self))

        self.outmode = QComboBox(parent = self)
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

        self.output = QTextEdit(parent = self)
        self.output.setReadOnly(True)

        self.layout().addWidget(self.outmode)
        self.layout().addWidget(self.output)

        try:
            with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_showb:
                self.cur_showb = self.db_showb.cursor()
                self.cur_showb.execute(f"select backup from diaries where name = '{name}'")
                self.fetch_showb = self.cur_showb.fetchone()[0]
                self.refresh(self.fetch_showb)
        except TypeError:
            pass

    def set_outmode(self, index):
        if index == 0:
            self.fetch_outmode = "plain-text"

        elif index == 1:
            self.fetch_outmode = "markdown"

        elif index == 2:
            self.fetch_outmode = "html"

        self.refresh(self.fetch_showb)

    def refresh(self, text):
        if self.fetch_outmode == "plain-text":
            self.output.setPlainText(text)

        elif self.fetch_outmode == "markdown":
            self.output.setMarkdown(text)

        elif self.fetch_outmode == "html":
            self.output.setHtml(text)


class Diaries(QTabWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global fetch_autosave, fetch_outmode

        with sqlite3.connect(f"{userdata}settings.db", timeout=5.0) as self.db_init:
            self.cur_init = self.db_init.cursor()

            try:
                self.cur_init.execute(f"select value from settings where setting = 'diaries-autosave'")
                fetch_autosave = self.cur_init.fetchone()[0]

            except:
                self.cur_init.execute(f"insert into settings (setting, value) values ('diaries-autosave', 'true')")
                self.db_init.commit()
                fetch_autosave = "true"

            try:
                self.cur_init.execute(f"select value from settings where setting = 'diaries-outmode'")
                fetch_outmode = self.cur_init.fetchone()[0]

            except:
                self.cur_init.execute(f"insert into settings (setting, value) values ('diaries-outmode', 'markdown')")
                self.db_init.commit()
                fetch_outmode = "markdown"

        self.setStatusTip(_('Fun fact: Auto-saves and editing/restoring contents for old diaries does not change backups.'))

        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self.home))

        self.created = QLabel(parent = self.home, alignment = align_center,
                              text = _('Created:'))
        self.edited = QLabel(parent = self.home, alignment = align_center,
                             text = _('Edited:'))

        self.calendar = QCalendarWidget(self.home)
        self.calendar.setMaximumDate(today)
        self.calendar.clicked.connect(self.insert)

        self.comeback_button = QPushButton(parent = self.home, text = _('Come back to current day'))
        self.comeback_button.clicked.connect(self.comeback)

        self.updateday_button = QPushButton(parent = self.home,
                                            text = _('Update current day (day is {date} at the moment)').format(date = today.toString("dd.MM.yyyy")))
        self.updateday_button.clicked.connect(self.updateday)

        self.side = QWidget(self.home)
        self.side.setFixedWidth(144)
        self.side.setLayout(QVBoxLayout(self.side))

        self.open_button = QPushButton(parent = self.side, text = _('Open/create diary'))
        self.open_button.clicked.connect(lambda: self.open(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.show_backup_button = QPushButton(parent = self.side, text = _('Show backup'))
        self.show_backup_button.clicked.connect(lambda: self.show_backup(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.restore_button = QPushButton(parent = self.side, text = _('Restore content'))
        self.restore_button.clicked.connect(lambda: self.restore(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.delete_content_button = QPushButton(parent = self.side, text = _('Delete content'))
        self.delete_content_button.clicked.connect(lambda: self.delete_content(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.delete_diary_button = QPushButton(parent = self.side, text = _('Delete diary'))
        self.delete_diary_button.clicked.connect(lambda: self.delete_diary(self.calendar.selectedDate().toString("dd.MM.yyyy")))

        self.delete_all_button = QPushButton(parent = self.side, text = _('Delete all diaries'))
        self.delete_all_button.clicked.connect(self.delete_all)

        self.outmode = QComboBox(parent = self)
        self.outmode.addItems([_("Out: Plain text"), _("Out: Markdown"), _("Out: HTML")])
        self.outmode.setEditable(False)
        if fetch_outmode == "plain-text":
            self.outmode.setCurrentIndex(0)
        elif fetch_outmode == "markdown":
            self.outmode.setCurrentIndex(1)
        elif fetch_outmode == "html":
            self.outmode.setCurrentIndex(2)
        self.outmode.currentIndexChanged.connect(self.set_outmode)

        self.autosave = QCheckBox(parent = self, text = _('Enable auto-save'))
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
        self.home.layout().addWidget(self.created, 0, 0, 1, 1)
        self.home.layout().addWidget(self.edited, 0, 1, 1, 1)
        self.home.layout().addWidget(self.calendar, 1, 0, 1, 2)
        self.home.layout().addWidget(self.comeback_button, 2, 0, 1, 1)
        self.home.layout().addWidget(self.updateday_button, 2, 1, 1, 1)

        self.addTab(self.home, _('Home'))
        self.setTabsClosable(True)
        self.setMovable(True)

        self.tabCloseRequested.connect(self.close)

    def close(self, index):
        if index != self.indexOf(self.home):
            try:
                del diaries[self.tabText(index).replace("&", "")]
            except KeyError:
                pass
            finally:
                self.removeTab(index)

    def set_autosave(self, signal):
        global fetch_autosave

        if signal == Qt.CheckState.Unchecked or signal == 0:
            fetch_autosave = "false"

        elif signal == Qt.CheckState.Checked or signal == 2:
            fetch_autosave = "true"

        with sqlite3.connect(f"{userdata}settings.db", timeout=5.0) as self.db_autosave:
            self.cur_autosave = self.db_autosave.cursor()
            self.cur_autosave.execute(f"update settings set value = '{fetch_autosave}' where setting = 'diaries-autosave'")
            self.db_autosave.commit()

    def set_outmode(self, index):
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

    def comeback(self):
        self.calendar.setSelectedDate(today)

    def updateday(self):
        global today
        today = QDate.currentDate()

        self.updateday_button.setText(_('Update current day (day is {date} at the moment)').format(date = today.toString("dd.MM.yyyy")))

    def insert(self, name):
        name = name.toString("dd.MM.yyyy")

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_insert:
            self.cur_insert = self.db_insert.cursor()
            self.cur_insert.execute(f"select created, edited from diaries where name = '{name[0]}'")
            self.fetch_insert = self.cur_insert.fetchone()

        try:
            self.created.setText(f"{_('Created')}: {self.fetch_insert[0]}")
            self.edited.setText(f"{_('Edited')}: {self.fetch_insert[1]}")
        except TypeError:
            pass

    def control(self, name, mode = "normal"):
        try:
            with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_control:
                self.cur_control = self.db_control.cursor()
                self.cur_control.execute(f"select * from diaries where name = '{name}'")
                self.fetch_control = self.cur_control.fetchone()[0]
            return True
        except TypeError:
            if mode == "normal":
                QMessageBox.critical(self, _('Error'), _('There is no diary in {name}.').format(name = name))
            return False

    def open(self, name):
        if name in diaries:
            self.setCurrentWidget(diaries[name])

        else:
            if name == today.toString("dd.MM.yyyy"):
                diaries[name] = Diary(self, name, "today")
            elif self.control(name) == True:
                diaries[name] = Diary(self, name, "old")
            else:
                return

            self.addTab(diaries[name], name)
            self.setCurrentWidget(diaries[name])

    def show_backup(self, name):
        if self.control(name) == False:
            return

        backups[name] = Backup(self, name)
        self.addTab(backups[name], (name + " " + _("(Backup)")))
        self.setCurrentWidget(backups[name])

    def restore(self, name):
        if self.control(name) == False:
            return

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_loadb1:
            self.cur_loadb1 = self.db_loadb1.cursor()
            self.cur_loadb1.execute(f"select content, backup from diaries where name = '{name}'")
            self.fetch_loadb1 = self.cur_loadb1.fetchone()

        if self.fetch_loadb1[1] == None or self.fetch_loadb1[1] == "":
            QMessageBox.critical(self, _('Error'), _('There is no backup for diary in {name}.').format(name = name))
            return
        
        if name != today.toString("dd.MM.yyyy"):
            self.question_restore = QMessageBox.question(self, _("Question"),
                                                        _("Diaries are special for that day, restoring content an old diary can take away the meaning of the diary."
                                                        +"\nSo, are you sure you want to restore content?"))

            if self.question_restore != QMessageBox.StandardButton.Yes:
                return

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_loadb2:
            if name == today.toString("dd.MM.yyyy"):
                self.sql_loadb2 = f"""update diaries set content = '{self.fetch_loadb1[1]}',
                backup = '{self.fetch_loadb1[0]}' where name = '{name}'"""
            else:
                self.sql_loadb2 = f"update diaries set content = '{self.fetch_loadb1[1]}' where name = '{name}'"
            self.cur_loadb2 = self.db_loadb2.cursor()
            self.cur_loadb2.execute(self.sql_loadb2)
            self.db_loadb2.commit()

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_loadb3:
            self.cur_loadb3 = self.db_loadb3.cursor()
            self.cur_loadb3.execute(f"select content, backup from diaries where name = '{name}'")
            self.fetch_loadb3 = self.cur_loadb3.fetchone()

        if self.fetch_loadb1[1] == self.fetch_loadb3[0]:
            QMessageBox.information(self, _('Successful'), _('Diary in {name} restored.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to restore diary in {name}.').format(name = name))

    def delete_content(self, name):
        if self.control(name) == False:
            return

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_delete1:
            self.cur_delete1 = self.db_delete1.cursor()
            self.cur_delete1.execute(f"select content from diaries where name = '{name}'")
            self.fetch_delete1 = self.cur_delete1.fetchone()[0]

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_delete2:
            self.cur_delete2 = self.db_delete2.cursor()
            self.cur_delete2.execute(
                f"update diaries set content = '', backup = '{self.fetch_delete1}' where name = '{name}'")
            self.db_delete2.commit()

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_delete3:
            self.cur_delete3 = self.db_delete3.cursor()
            self.cur_delete3.execute(f"select content from diaries where name = '{name}'")
            self.fetch_delete3 = self.cur_delete3.fetchone()[0]

        if self.fetch_delete3 != None:
            QMessageBox.information(self, _('Successful'), _('Content of diary in {name} deleted.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete content of diary in {name}.').format(name = name))

    def delete_diary(self, name):
        if self.control(name) == False:
            return

        with sqlite3.connect(f"{userdata}diaries.db", timeout=5.0) as self.db_remove1:
            self.cur_remove1 = self.db_remove1.cursor()
            self.cur_remove1.execute(f"delete from diaries where name = '{name}'")
            self.db_remove1.commit()

        if self.control(name, "inverted") == False:
            QMessageBox.information(self, _('Successful'), _('Diary in {name} deleted.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete diary in {name}.').format(name = name))

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