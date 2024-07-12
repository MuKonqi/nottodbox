import sys
import locale
import getpass
import os
import sqlite3
import datetime
from PyQt6.QtCore import Qt, QStringListModel, QSortFilterProxyModel, QRegularExpression
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

notes =  {}
backups = {}


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

    with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as notes_db:
        notes_sql = """
        CREATE TABLE IF NOT EXISTS notes (
            name TEXT NOT NULL PRIMARY KEY,
            content TEXT,
            backup TEXT, 
            created TEXT NOT NULL,
            edited TEXT
        );"""
        notes_cur = notes_db.cursor()
        notes_cur.execute(notes_sql)
        notes_db.commit()
db_start()


class Note(QWidget):
    def __init__(self, parent, name):
        super().__init__(parent)
        
        self.fetch_autosave = fetch_autosave
        self.fetch_outmode = fetch_outmode
        
        self.setLayout(QGridLayout(self))
        
        self.autosave = QCheckBox(parent = self, text = _('Enable auto-save for this time'))
        if fetch_autosave == "true":
            self.autosave.setChecked(True)
        try:
            self.autosave.checkStateChanged.connect(self.set_autosave)
        except:
            self.autosave.stateChanged.connect(self.set_autosave)
        
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
            
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_open:
            self.cur_open = self.db_open.cursor()
            self.cur_open.execute(f"select content from notes where name = '{name}'")
            
            try:
                self.fetch_open = self.cur_open.fetchone()[0]
                self.input.setPlainText(self.fetch_open)
                self.refresh(self.fetch_open)
            except TypeError:
                self.fetch_open = ""
    
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
            try:   
                with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_save1:
                    self.cur_save1 = self.db_save1.cursor()
                    self.cur_save1.execute(f"select content from notes where name = '{name}'")
                    self.fetch_save1 = self.cur_save1.fetchone()[0]
                
                with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_save2:
                    self.sql_save2 = f"""update notes set content = '{content}', backup = '{self.fetch_open}',
                    edited = '{date}' where name = '{name}'"""
                    self.cur_save2 = self.db_save2.cursor()
                    self.cur_save2.execute(self.sql_save2)
                    self.db_save2.commit()

            except TypeError:
                with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_save3:
                    self.sql_save3 = f"""insert into notes (name, content, backup, created, edited) 
                    values ('{name}', '{content}', '', '{date}', '{date}')"""
                    self.cur_save3 = self.db_save3.cursor()
                    self.cur_save3.execute(self.sql_save3)
                    self.db_save3.commit()
                    
            Notes.refresh(self)
        
            with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_save4:
                self.cur_save4 = self.db_save4.cursor()
                self.cur_save4.execute(f"select content from notes where name = '{name}'")
                self.fetch_save4 = self.cur_save4.fetchone()[0]

            if self.fetch_save4 == content:
                QMessageBox.information(self, _('Successful'), _('{name} note saved.').format(name = name))
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to save {name} note.').format(name = name))

        elif mode == "auto" and self.fetch_autosave == "true":
            try:
                with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_save1:
                    self.cur_save1 = self.db_save1.cursor()
                    self.cur_save1.execute(f"select content from notes where name = '{name}'")
                    self.fetch_save1 = self.cur_save1.fetchone()[0]
                
                with sqlite3.connect(f"{userdata}notes.db", timeout=1.0) as self.db_save2:
                    self.sql_save2 = f"""update notes set content = '{content}',
                    edited = '{date}' where name = '{name}'"""
                    self.cur_save2 = self.db_save2.cursor()
                    self.cur_save2.execute(self.sql_save2)
                    self.db_save2.commit()
            
            except TypeError:    
                with sqlite3.connect(f"{userdata}notes.db", timeout=1.0) as self.db_save3:
                    self.sql_save3 = f"""insert into notes (name, content, backup, created, edited) 
                    values ('{name}', '{content}', '', '{date}', '{date}')"""
                    self.cur_save3 = self.db_save3.cursor()
                    self.cur_save3.execute(self.sql_save3)
                    self.db_save3.commit()
                    
                Notes.refresh(self)
            

class Backup(QWidget):
    def __init__(self, parent, name):
        super().__init__(parent)
        
        self.fetch_outmode = fetch_outmode
        
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
        
        self.button = QPushButton(parent = self, text = _('Restore content'))
        self.button.clicked.connect(lambda: Notes.restore(self, name, "page"))
        
        self.layout().addWidget(self.outmode)
        self.layout().addWidget(self.output)
        self.layout().addWidget(self.button)

        try:
            with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_showb:
                self.cur_showb = self.db_showb.cursor()
                self.cur_showb.execute(f"select backup from notes where name = '{name}'")
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


class Notes(QTabWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global notes_model, fetch_autosave, fetch_outmode
        
        with sqlite3.connect(f"{userdata}settings.db", timeout=5.0) as self.db_init:
            self.cur_init = self.db_init.cursor()

            try:
                self.cur_init.execute(f"select value from settings where setting = 'notes-autosave'")
                fetch_autosave = self.cur_init.fetchone()[0]

            except:
                self.cur_init.execute(f"insert into settings (setting, value) values ('notes-autosave', 'true')")
                self.db_init.commit()
                fetch_autosave = "true"
                
            try:
                self.cur_init.execute(f"select value from settings where setting = 'notes-outmode'")
                fetch_outmode = self.cur_init.fetchone()[0]

            except:
                self.cur_init.execute(f"insert into settings (setting, value) values ('notes-outmode', 'markdown')")
                self.db_init.commit()
                fetch_outmode = "markdown"
        
        self.setStatusTip(_('Fun fact: Auto-saves does not change backups.'))
        
        self.home = QWidget(self)
        self.home.setLayout(QGridLayout(self.home))
        
        self.entry = QLineEdit(self.home)
        self.entry.setPlaceholderText("Type anything for search or a note name others")
        self.entry.textChanged.connect(
            lambda: self.proxy.setFilterRegularExpression(QRegularExpression
                                                          (self.entry.text(), QRegularExpression.PatternOption.CaseInsensitiveOption)))
        
        self.created = QLabel(parent = self.home, alignment = align_center, 
                              text = _('Created:'))
        self.edited = QLabel(parent = self.home, alignment = align_center, 
                             text = _('Edited:'))
        
        self.listview = QListView(self.home)
        self.listview.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listview.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        notes_model = QStringListModel(self)
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(notes_model)
        
        self.listview.setModel(self.proxy)

        self.listview.selectionModel().selectionChanged.connect(
            lambda: self.insert(self.proxy.itemData(self.listview.currentIndex())))

        self.side = QWidget(self.home)
        self.side.setFixedWidth(144)
        self.side.setLayout(QVBoxLayout(self.side))
        
        self.open_button = QPushButton(parent = self.side, text = _('Open/create note'))
        self.open_button.clicked.connect(lambda: self.open(self.entry.text()))
        
        self.rename_button = QPushButton(parent = self.side, text = _('Rename note'))
        self.rename_button.clicked.connect(lambda: self.rename(self.entry.text()))

        self.show_backup_button = QPushButton(parent = self.side, text = _('Show backup'))
        self.show_backup_button.clicked.connect(lambda: self.show_backup(self.entry.text()))

        self.restore_button = QPushButton(parent = self.side, text = _('Restore content'))
        self.restore_button.clicked.connect(lambda: self.restore(self.entry.text()))
        
        self.delete_content_button = QPushButton(parent = self.side, text = _('Delete content'))
        self.delete_content_button.clicked.connect(lambda: self.delete_content(self.entry.text()))
        
        self.delete_note_button = QPushButton(parent = self.side, text = _('Delete note'))
        self.delete_note_button.clicked.connect(lambda: self.delete_note(self.entry.text()))
        
        self.delete_all_button = QPushButton(parent = self.side, text = _('Delete all notes'))
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
        self.side.layout().addWidget(self.rename_button)
        self.side.layout().addWidget(self.show_backup_button)
        self.side.layout().addWidget(self.restore_button)
        self.side.layout().addWidget(self.delete_content_button)
        self.side.layout().addWidget(self.delete_note_button)
        self.side.layout().addWidget(self.delete_all_button)
        self.side.layout().addWidget(self.outmode)
        self.side.layout().addWidget(self.autosave)
        self.home.layout().addWidget(self.side, 1, 2, 2, 1)
        self.home.layout().addWidget(self.entry, 0, 0, 1, 3)
        self.home.layout().addWidget(self.created, 1, 0, 1, 1)
        self.home.layout().addWidget(self.edited, 1, 1, 1, 1)
        self.home.layout().addWidget(self.listview, 2, 0, 1, 2)
        
        self.addTab(self.home, _('Home'))
        self.setTabsClosable(True)
        self.setMovable(True)
        
        self.refresh()
        
        self.tabCloseRequested.connect(self.close)
         
    def close(self, index):
        if index != self.indexOf(self.home):
            try:
                del notes[self.tabText(index).replace("&", "")]
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
            self.cur_autosave.execute(f"update settings set value = '{fetch_autosave}' where setting = 'notes-autosave'")
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
            self.cur_outmode.execute(f"update settings set value = '{fetch_outmode}' where setting = 'notes-outmode'")
            self.db_outmode.commit()
    
    def refresh(self):
        global notes_model, notes_list
        
        notes_list = []
        
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_refresh:
            self.cur_refresh = self.db_refresh.cursor()
            self.cur_refresh.execute("select name from notes")
            self.fetch_refresh = self.cur_refresh.fetchall()
        
        for i in range(0, len(self.fetch_refresh)):
            notes_list.append(self.fetch_refresh[i][0])

        notes_model.setStringList(notes_list)
        
    def insert(self, name):
        if name != {}:
            with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_insert:
                self.cur_insert = self.db_insert.cursor()
                self.cur_insert.execute(f"select name, created, edited from notes where name = '{name[0]}'")
                self.fetch_insert = self.cur_insert.fetchone()
            
            try:
                self.entry.setText(self.fetch_insert[0])
                self.created.setText(f"{_('Created')}: {self.fetch_insert[1]}")
                self.edited.setText(f"{_('Edited')}: {self.fetch_insert[2]}")
            except TypeError:
                self.created.setText(f"{_('Created')}:")
                self.edited.setText(f"{_('Edited')}:")
        
    def control(self, name, mode = "normal"):
        try:
            with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_control:
                self.cur_control = self.db_control.cursor()
                self.cur_control.execute(f"select * from notes where name = '{name}'")
                self.fetch_control = self.cur_control.fetchone()[0]
            return True
        except TypeError:
            if mode == "normal":
                QMessageBox.critical(self, _('Error'), _('There is no note called {name}.').format(name = name))
            return False
        
    def open(self, name):
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return        
        
        if name in notes:
            self.setCurrentWidget(notes[name])
            
        else:
            notes[name] = Note(self, name)
            self.addTab(notes[name], name)
            self.setCurrentWidget(notes[name])
    
    def rename(self, name):
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return        
        
        if self.control(name) == False:
            return
        
        self.newname, self.topwindow = QInputDialog.getText(self, 
                                                             _("Rename {name} Note").format(name = name), 
                                                             _("Please enter a new name for {name} below.").format(name = name))
        
        if self.newname != "" and self.newname != None and self.topwindow == True:
            with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_rename1:
                self.sql_rename1 = f"update notes set name = '{self.newname}' where name = '{name}'"
                self.cur_rename1 = self.db_rename1.cursor()
                self.cur_rename1.execute(self.sql_rename1)
                self.db_rename1.commit()
            
            self.refresh()

            try:
                with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_rename2:
                    self.cur_rename2 = self.db_rename2.cursor()
                    self.cur_rename2.execute(f"select * from notes where name = '{self.newname}'")
                    self.fetch_rename2 = self.cur_rename2.fetchone()[0]
                    
                self.entry.setText(self.newname)    
                
                QMessageBox.information(self, _('Successful'), 
                                        _('{name} note renamed as {newname}.').format(name = name, newname = self.newname))
                
            except TypeError:
                QMessageBox.critical(self, _('Error'), _('Failed to rename {name} note.').format(name = name))
                
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to rename {name} note.').format(name = name))
    
    def show_backup(self, name):
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return

        if self.control(name) == False:
            return
        
        backups[name] = Backup(self, name)
        self.addTab(backups[name], (name + " " + _("(Backup)")))
        self.setCurrentWidget(backups[name])
    
    def restore(self, name, caller = "home"):
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return
        
        if caller == "home" and self.control(name) == False:
            return
        
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_restore1:
            self.cur_restore1 = self.db_restore1.cursor()
            self.cur_restore1.execute(f"select content, backup from notes where name = '{name}'")
            self.fetch_restore1 = self.cur_restore1.fetchone()
            
        if self.fetch_restore1[1] == None or self.fetch_restore1[1] == "":
            QMessageBox.critical(self, _('Error'), _('There is no backup for {name} note.').format(name = name))
            return
                        
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_restore2:
            self.sql_restore2 = f"""update notes set content = '{self.fetch_restore1[1]}', 
            backup = '{self.fetch_restore1[0]}' where name = '{name}'"""
            self.cur_restore2 = self.db_restore2.cursor()
            self.cur_restore2.execute(self.sql_restore2)
            self.db_restore2.commit()
            
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_restore3:
            self.cur_restore3 = self.db_restore3.cursor()
            self.cur_restore3.execute(f"select content, backup from notes where name = '{name}'")
            self.fetch_restore3 = self.cur_restore3.fetchone()
            
        if self.fetch_restore1[1] == self.fetch_restore3[0]:
            QMessageBox.information(self, _('Successful'), _('{name} note restored.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to restore {name} note.').format(name = name))
            
    def delete_content(self, name):
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return        
        
        if self.control(name) == False:
            return
        
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_delete1:
            self.cur_delete1 = self.db_delete1.cursor()
            self.cur_delete1.execute(f"select content from notes where name = '{name}'")
            self.fetch_delete1 = self.cur_delete1.fetchone()[0]
        
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_delete2:
            self.cur_delete2 = self.db_delete2.cursor()
            self.cur_delete2.execute(
                f"update notes set content = '', backup = '{self.fetch_delete1}' where name = '{name}'")
            self.db_delete2.commit()
        
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_delete3:
            self.cur_delete3 = self.db_delete3.cursor()
            self.cur_delete3.execute(f"select content from notes where name = '{name}'")
            self.fetch_delete3 = self.cur_delete3.fetchone()[0]
    
        if self.fetch_delete3 != None:
            QMessageBox.information(self, _('Successful'), _('Content of {name} note deleted.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete content of {name} note.').format(name = name))
                       
    def delete_note(self, name):
        if name == "" or name == None:
            QMessageBox.critical(self, _('Error'), _('Note name can not be blank.'))
            return
        
        if self.control(name) == False:
            return
        
        with sqlite3.connect(f"{userdata}notes.db", timeout=5.0) as self.db_remove1:
            self.cur_remove1 = self.db_remove1.cursor()
            self.cur_remove1.execute(f"delete from notes where name = '{name}'")
            self.db_remove1.commit()
            
        self.refresh()
        self.entry.setText("")
            
        if self.control(name, "inverted") == False:
            QMessageBox.information(self, _('Successful'), _('{name} note deleted.').format(name = name))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete {name} note.').format(name = name))
            
    def delete_all(self):
        try:
            os.remove(f"{userdata}notes.db")
        except:
            QMessageBox.critical(self, _('Error'), _('Failed to delete all notes.'))
            return
    
        if not os.path.isfile(f"{userdata}notes.db"):
            db_start()
            self.refresh()
            self.entry.setText("")
            
            QMessageBox.information(self, _('Successful'), _('All notes deleted.'))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete all notes.'))
            
            
if __name__ == "__main__":
    application = QApplication(sys.argv)

    window = QMainWindow()
    window.setStatusBar(QStatusBar(window))
    window.setStatusTip(_('Copyright (C) 2024 MuKonqi (Muhammed S.), licensed under GPLv3 or later'))
    window.setGeometry(0, 0, 960, 540)
    window.setWindowTitle("Nottodbox: Notes")
    
    widget = QWidget(parent = window)
    widget.setLayout(QGridLayout(widget))
    widget.layout().addWidget(Notes(parent = widget))
    
    window.setCentralWidget(widget)
    window.show()

    application.exec()