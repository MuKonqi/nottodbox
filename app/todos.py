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

todolists = {}

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
        
    with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as db:
        sql1 = """
        CREATE TABLE IF NOT EXISTS todos (
            name TEXT NOT NULL PRIMARY KEY,
            created TEXT NOT NULL
        );"""
        sql2 = """
        CREATE TABLE IF NOT EXISTS main (
            todo TEXT NOT NULL PRIMARY KEY,
            status TEXT NOT NULL,
            started TEXT NOT NULL,
            completed TEXT
        );"""
        cur = db.cursor()
        cur.execute(sql1)
        cur.execute(sql2)
        db.commit()
db_start()


class Todolist(QWidget):
    def __init__(self, parent, todolist = "main"):
        super().__init__(parent)
        
        self.todolist = todolist
        
        self.setLayout(QGridLayout(self))
        
        self.started = QLabel(parent = self, alignment = align_center, 
                              text = _('Started:'))
        self.completed = QLabel(parent = self, alignment = align_center, 
                                text = _("Completed:"))
        
        self.listview = QListView(self)
        self.listview.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listview.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.model = QStringListModel(self)
        
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        
        self.listview.setModel(self.proxy)
        self.listview.selectionModel().selectionChanged.connect(
            lambda: self.insert(self.proxy.itemData(self.listview.currentIndex())))
        
        self.entry = QLineEdit(parent = self)
        self.entry.setPlaceholderText(_("Type anything/a todo"))
        self.entry.textChanged.connect(
            lambda: self.proxy.setFilterRegularExpression(QRegularExpression
                                                          (self.entry.text(), QRegularExpression.PatternOption.CaseInsensitiveOption)))
        
        self.comp_button = QPushButton(parent = self, text = _("Mark as completed"))
        self.comp_button.clicked.connect(lambda: self.comp(self.entry.text(), 
                                                           datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
        self.uncomp_button = QPushButton(parent = self, text = _("Mark as uncompleted"))
        self.uncomp_button.clicked.connect(lambda: self.uncomp(self.entry.text(), 
                                                               datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
        self.add_button = QPushButton(parent = self, text = _("Add"))
        self.add_button.clicked.connect(lambda: self.add(self.entry.text(),
                                                         datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
        self.edit_button = QPushButton(parent = self, text = _("Edit"))
        self.edit_button.clicked.connect(lambda: self.edit(self.entry.text()))
        
        self.delete_button = QPushButton(parent = self, text = _("Delete"))
        self.delete_button.clicked.connect(lambda: self.delete(self.entry.text()))
        
        self.delete_all_button = QPushButton(parent = self, text = _("Delete All"))
        self.delete_all_button.clicked.connect(self.delete_all)
        
        self.layout().addWidget(self.started, 0, 0, 1, 1)
        self.layout().addWidget(self.completed, 0, 1, 1, 1)
        self.layout().addWidget(self.listview, 1, 0, 1, 2)
        self.layout().addWidget(self.entry, 2, 0, 1, 2)
        self.layout().addWidget(self.comp_button, 3, 0, 1, 1)
        self.layout().addWidget(self.uncomp_button, 3, 1, 1, 1)
        self.layout().addWidget(self.add_button, 4, 0, 1, 1)
        self.layout().addWidget(self.edit_button, 4, 1, 1, 1)
        self.layout().addWidget(self.delete_button, 5, 0, 1, 1)
        self.layout().addWidget(self.delete_all_button, 5, 1, 1, 1)
        
        self.refresh()
        
    def refresh(self):
        self.list = []
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_refresh:
            self.cur_refresh = self.db_refresh.cursor()
            self.cur_refresh.execute(f"select * from {self.todolist}")
            self.fetch_refresh = self.cur_refresh.fetchall()
        
        for i in range(0, len(self.fetch_refresh)):
            if self.fetch_refresh[i][1] == "completed":
                self.list.append(f"[+] {self.fetch_refresh[i][0]}")
                
            elif self.fetch_refresh[i][1] == "uncompleted":
                self.list.append(f"[-] {self.fetch_refresh[i][0]}")

        self.model.setStringList(self.list)
        
    def insert(self, todo):
        if todo != {}:
            if todo[0].startswith("[-]") == True:
                todo = todo[0].replace("[-] ", "")
            elif todo[0].startswith("[+]") == True:
                todo = todo[0].replace("[+] ", "")
            
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_insert:
                self.cur_insert = self.db_insert.cursor()
                self.cur_insert.execute(f"select todo, started, completed from {self.todolist} where todo = '{todo}'")
                self.fetch_insert = self.cur_insert.fetchone()
            
            try:
                self.entry.setText(self.fetch_insert[0])
                self.started.setText(f"{_('Started')}: {self.fetch_insert[1]}")
                self.completed.setText(f"{_('Completed')}: {self.fetch_insert[2]}")
            except TypeError:
                self.started.setText(f"{_('Started')}:")
                self.completed.setText(f"{_('Completed')}:")
        
    def control(self, todo, mode = "normal"):
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_control:
                self.cur_control = self.db_control.cursor()
                self.cur_control.execute(f"select * from {self.todolist} where todo = '{todo}'")
                self.fetch_control = self.cur_control.fetchone()[0]
            return True
        except TypeError:
            if mode == "normal":
                QMessageBox.critical(self, _('Error'), _('There is no todo in {todolist} list called {todo}.').format(todolist = self.todolist, todo = todo))
            return False
    
    def comp(self, todo, date):
        if self.control(todo) == False:
            return
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_comp1:
            self.cur_comp1 = self.db_comp1.cursor()
            self.cur_comp1.execute(f"update {self.todolist} set status = 'completed', completed = '{date}' where todo = '{todo}'")
            self.db_comp1.commit()
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_comp2:
            self.cur_comp2 = self.db_comp2.cursor()
            self.cur_comp2.execute(f"select status from {self.todolist} where todo = '{todo}'")
            self.fetch_comp2 = self.cur_comp2.fetchone()[0]
        
        self.refresh()
        
        if self.fetch_comp2 == "completed":
            QMessageBox.information(self, _("Successful"), _("{todo} in {todolist} marked as completed.").format(todo = todo, todolist = self.todolist))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to mark {todo} in {todolist} as completed.").format(todo = todo, todolist = self.todolist))
    
    def uncomp(self, todo):
        if self.control(todo) == False:
            return
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_uncomp1:
            self.cur_uncomp1 = self.db_uncomp1.cursor()
            self.cur_uncomp1.execute(f"update {self.todolist} set status = 'uncompleted', completed = NULL where todo = '{todo}'")
            self.db_uncomp1.commit()
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_uncomp2:
            self.cur_uncomp2 = self.db_uncomp2.cursor()
            self.cur_uncomp2.execute(f"select status from {self.todolist} where todo = '{todo}'")
            self.fetch_uncomp2 = self.cur_uncomp2.fetchone()[0]
            
        self.refresh()
        
        if self.fetch_uncomp2 == "uncompleted":
            QMessageBox.information(self, _("Successful"), _("{todo} in {todolist} marked as uncompleted.").format(todo = todo, todolist = self.todolist))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to mark {todo} in {todolist} as uncompleted.").format(todo = todo, todolist = self.todolist))
    
    def add(self, todo, date):
        if todo == "" or todo == None:
            QMessageBox.critical(self, _('Error'), _('Todo can not be blank.'))
            return           
        
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_add1:
                self.sql_add1 = f"""insert into {self.todolist} (todo, status, started) 
                values ('{todo}', 'uncompleted', '{date}')"""
                self.cur_add1 = self.db_add1.cursor()
                self.cur_add1.execute(self.sql_add1)
                self.db_add1.commit()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, _('Error'), _('{todo} todo already added to {todolist}.').format(todo = todo, todolist = self.todolist))
            return
                
        self.refresh()
    
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_add2:
            self.cur_add2 = self.db_add2.cursor()
            self.cur_add2.execute(f"select todo, status, started from {self.todolist} where todo = '{todo}'")
            self.fetch_add2 = self.cur_add2.fetchone()

        self.if_add = self.fetch_add2[0] == todo and self.fetch_add2[1] == "uncompleted"
        
        if self.if_add == True and self.fetch_add2[2] == date:
            QMessageBox.information(self, _('Successful'), _('{todo} added to {todolist}.').format(todo = todo, todolist = self.todolist))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to add {todo} to {todolist}.').format(todo = todo, todolist = self.todolist))
    
    def edit(self, todo):
        if todo == "" or todo == None:
            QMessageBox.critical(self, _('Error'), _('Todo can not be blank.'))
            return        
        
        if self.control(todo) == False:
            return
        
        self.newtodo, self.topwindow = QInputDialog.getText(self, 
                                                             _("Edit {todo} todo in {todolist}").format(todo = todo, todolist = self.todolist), 
                                                             _("Please enter a todo for {todo} in {todolist} below.").format(todo = todo, todolist = self.todolist))
        
        if self.newtodo != "" and self.newtodo != None and self.topwindow == True:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_edit1:
                self.sql_edit1 = f"update {self.todolist} set todo = '{self.newtodo}' where todo = '{todo}'"
                self.cur_edit1 = self.db_edit1.cursor()
                self.cur_edit1.execute(self.sql_edit1)
                self.db_edit1.commit()
            
            self.refresh()
            self.entry.setText(self.newtodo)

            try:
                with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_edit2:
                    self.cur_edit2 = self.db_edit2.cursor()
                    self.cur_edit2.execute(f"select * from {self.todolist} where todo = '{self.newtodo}'")
                    self.fetch_edit2 = self.cur_edit2.fetchone()[0]
                
                self.entry.setText(self.newtodo)
                
                QMessageBox.information(self, _('Successful'),
                                        _('{todo} todo in {todolist} edited as {newtodo}.')
                                        .format(todo = todo, todolist = self.todolist, newtodo = self.newtodo))
                
            except TypeError:
                QMessageBox.critical(self, _('Error'), _('Failed to edit {todo} todo in {todolist}.').format(todo = todo, todolist = self.todolist))
                
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to edit {todo} todo in {todolist}.').format(todo = todo, todolist = self.todolist))
    
    def delete(self, todo):
        if todo == "" or todo == None:
            QMessageBox.critical(self, _('Error'), _('Todo can not be blank.'))
            return
        
        if self.control(todo) == False:
            return
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_remove1:
            self.cur_remove1 = self.db_remove1.cursor()
            self.cur_remove1.execute(f"delete from {self.todolist} where todo = '{todo}'")
            self.db_remove1.commit()
            
        self.refresh()
        self.entry.setText("")
            
        if self.control(todo, "inverted") == False:
            QMessageBox.information(self, _('Successful'), _('{todo} todo in {todolist} deleted.').format(todo = todo, todolist = self.todolist))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete {todo} todo in {todolist}.').format(todo = todo, todolist = self.todolist))
    
    def delete_all(self):
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all1:
            self.cur_delete_all1 = self.db_delete_all1.cursor()
            self.cur_delete_all1.execute(f"select todo from {self.todolist}")
            self.fetch_delete_all1 = self.cur_delete_all1.fetchall()
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all2:
            self.cur_delete_all2 = self.db_delete_all2.cursor()
            
            for todolist in self.fetch_delete_all1:
                self.cur_delete_all2.execute(f"delete from '{self.todolist}' where todo = '{todolist[0]}'")
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all3:
            self.cur_delete_all3 = self.db_delete_all3.cursor()
            self.cur_delete_all3.execute(f"select * from {self.todolist}")
            self.fetch_delete_all3 = self.cur_delete_all3.fetchall()
        
        self.refresh()
        
        if self.fetch_delete_all3 == []:
            QMessageBox.information(self, _('Successful'), _('All todos in {todolist} deleted.').format(todolist = self.todolist))
        else:
            QMessageBox.critical(self, _('Error'), _('Failed to delete all todos in {todolist}.').format(todolist = self.todolist))

class Todos(QTabWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.setStatusTip("Tips: For search, just type in entries.")
        
        self.home = QWidget(self)
        self.home.setLayout(QHBoxLayout(self.home))
        
        self.side = QWidget(self.home)
        self.side.setFixedWidth(288)
        self.side.setLayout(QGridLayout(self.side))
        
        self.created = QLabel(parent = self.side, alignment = align_center, 
                              text = _('Created:'))
        
        self.listview = QListView(self.side)
        self.listview.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listview.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.listview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.model = QStringListModel(self)
        
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        
        self.listview.setModel(self.proxy)
        self.listview.selectionModel().selectionChanged.connect(
            lambda: self.insert(self.proxy.itemData(self.listview.currentIndex())))
        
        self.entry = QLineEdit(parent = self.side)
        self.entry.setPlaceholderText(_('Type anything/a list name'))
        self.entry.textChanged.connect(
            lambda: self.proxy.setFilterRegularExpression(QRegularExpression
                                                          (self.entry.text(), QRegularExpression.PatternOption.CaseInsensitiveOption)))
        
        self.open_button = QPushButton(parent = self.side, text = _("Open"))
        self.open_button.clicked.connect(lambda: self.open(self.entry.text()))
        
        self.add_button = QPushButton(parent = self.side, text = _("Add"))
        self.add_button.clicked.connect(lambda: self.add(self.entry.text(),
                                                         datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
        self.rename_button = QPushButton(parent = self.side, text = _("Rename"))
        self.rename_button.clicked.connect(lambda: self.rename(self.entry.text()))
        
        self.delete_button = QPushButton(parent = self.side, text = _("Delete"))
        self.delete_button.clicked.connect(lambda: self.delete(self.entry.text()))
        
        self.delete_all_button = QPushButton(parent = self.side, text = _("Delete All"))
        self.delete_all_button.clicked.connect(self.delete_all)

        self.home.layout().addWidget(Todolist(self, "main"))
        self.side.layout().addWidget(self.created, 0, 0, 1, 2)
        self.side.layout().addWidget(self.listview, 1, 0, 1, 2)
        self.side.layout().addWidget(self.entry, 2, 0, 1, 2)
        self.side.layout().addWidget(self.open_button, 3, 0, 1, 2)
        self.side.layout().addWidget(self.add_button, 4, 0, 1, 1)
        self.side.layout().addWidget(self.rename_button, 4, 1, 1, 1)
        self.side.layout().addWidget(self.delete_button, 5, 0, 1, 1)
        self.side.layout().addWidget(self.delete_all_button, 5, 1, 1, 1)
        self.home.layout().addWidget(self.side)
        
        self.addTab(self.home, _('Home'))
        self.setTabsClosable(True)
        self.setMovable(True)
        
        self.refresh()
        
        self.tabCloseRequested.connect(self.close)
         
    def close(self, index):
        if index != self.indexOf(self.home):
            try:
                del todolists[self.tabText(index).replace("&", "")]
            finally:
                self.removeTab(index)
    
    def refresh(self):
        self.list = []
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_refresh:
            self.cur_refresh = self.db_refresh.cursor()
            self.cur_refresh.execute("select name from todos")
            self.fetch_refresh = self.cur_refresh.fetchall()
        
        for i in range(0, len(self.fetch_refresh)):
            self.list.append(self.fetch_refresh[i][0])

        self.model.setStringList(self.list)
    
    def insert(self, todolist):
        if todolist != {}:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_insert:
                self.cur_insert = self.db_insert.cursor()
                self.cur_insert.execute(f"select name, created from todos where name = '{todolist[0]}'")
                self.fetch_insert = self.cur_insert.fetchone()
            
            try:
                self.entry.setText(self.fetch_insert[0])
                self.created.setText(f"{_('Created')}: {self.fetch_insert[1]}")
            except TypeError:
                self.created.setText(f"{_('Created')}:")
        
    def control(self, todolist, mode = "normal"):
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5.0) as self.db_control:
                self.cur_control = self.db_control.cursor()
                self.cur_control.execute(f"select * from '{todolist}'")
                self.fetch_control = self.cur_control.fetchone()[0]
            return True
        except TypeError:
            if mode == "normal":
                QMessageBox.critical(self, _('Error'), _('There is no todo list called {todolist}.').format(todolist = todolist))
            return False
    
    def open(self, todolist):
        if todolist == "main" or todolist == "" or todolist == None:
            QMessageBox.critical(self, _('Error'), _('Todo list name can not be blank or main.'))
            return
        
        if todolist not in self.list:
            QMessageBox.critical(self, _('Error'), _('There is no todolist called {todolist}.').format(todolist = todolist))
            return
        
        if todolist in todolists:
            self.setCurrentWidget(todolists[todolist])
            
        else:
            todolists[todolist] = Todolist(self, todolist)
            self.addTab(todolists[todolist], todolist)
            self.setCurrentWidget(todolists[todolist])
    
    def add(self, todolist, date):
        if todolist == "main" or todolist == "" or todolist == None:
            QMessageBox.critical(self, _('Error'), _('Todo list name can not be blank or main.'))
            return 
        
        try:
            with sqlite3.connect(f"{userdata}todos.db") as self.db_add1:
                self.sql_add1 = f"""
                CREATE TABLE {todolist} (
                    todo TEXT NOT NULL PRIMARY KEY,
                    status TEXT NOT NULL,
                    started TEXT NOT NULL,
                    completed TEXT
                );"""
                self.cur_add1 = self.db_add1.cursor()
                self.cur_add1.execute(self.sql_add1)
                self.cur_add1.execute(f"insert into todos (name, created) values ('{todolist}', '{date}')")
                self.db_add1.commit()
                
        except sqlite3.OperationalError:
            QMessageBox.critical(self, _('Error'), _('{todolist} list already exist.').format(todolist = todolist))
            return
        
        self.refresh()
        
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5) as self.db_add2:
                self.cur_add2 = self.db_add2.cursor()
                self.cur_add2.execute(f"select * from '{todolist}'")
                self.cur_add2.fetchall()
                self.cur_add2.execute(f"select name, created from todos where name = '{todolist}'")
                self.fetch_add2 = self.cur_add2.fetchone()
            
            if todolist in self.fetch_add2 and date in self.fetch_add2:
                QMessageBox.information(self, _('Successful'), _('{todolist} list added.').format(todolist = todolist))
                
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to add {todolist} list.').format(todolist = todolist))
        
        except sqlite3.OperationalError:
            QMessageBox.critical(self, _('Error'), _('Failed to add {todolist} list.').format(todolist = todolist))

    def rename(self, todolist):
        if todolist == "main" or todolist == "" or todolist == None:
            QMessageBox.critical(self, _('Error'), _('Todo list name can not be blank or main.'))
            return
        self.newname, self.topwindow = QInputDialog.getText(self, 
                                                             _("Rename {todolist} List").format(todolist = todolist), 
                                                             _("Please enter a new name for {todolist} list below.").format(todolist = todolist))
        
        try:
            with sqlite3.connect(f"{userdata}todos.db") as self.db_rename1:
                self.cur_rename1 = self.db_rename1.cursor()
                self.cur_rename1.execute(f"ALTER TABLE {todolist} RENAME TO {self.newname}")
                self.cur_rename1.execute(f"update todos set name = '{self.newname}' where name = '{todolist}'")
                self.db_rename1.commit()
        except sqlite3.OperationalError:
            QMessageBox.critical(self, _('Error'), _('There is no list called {todolist}.').format(todolist = todolist))
            return
        
        self.refresh()
        
        try:
            with sqlite3.connect(f"{userdata}todos.db", timeout=5) as self.db_rename2:
                self.cur_rename2 = self.db_rename2.cursor()
                self.cur_rename2.execute(f"select * from '{self.newname}'")
                self.cur_rename2.fetchall()
                self.cur_rename2.execute(f"select name from todos")
                self.fetch_rename2 = self.cur_rename2.fetchone()
                
            self.entry.setText(self.newname)
                
            if self.newname in self.fetch_rename2:
                QMessageBox.information(self, _('Successful'), _('{todolist} list renamed as {newname}.').format(todolist = todolist, newname = self.newname))
        
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to rename {todolist} list.').format(todolist = todolist))
        
        except sqlite3.OperationalError:
            QMessageBox.critical(self, _('Error'), _('Failed to rename {todolist} list.').format(todolist = todolist))
    
    def delete(self, todolist):
        if todolist == "main" or todolist == "" or todolist == None:
            QMessageBox.critical(self, _('Error'), _('Todo list name can not be blank or main.'))
            return
        
        try:
            with sqlite3.connect(f"{userdata}todos.db") as self.db_delete1:
                self.cur_delete1 = self.db_delete1.cursor()
                self.cur_delete1.execute(f"DROP TABLE {todolist}")
                self.cur_delete1.execute(f"delete from todos where name = '{todolist}'")
                self.db_delete1.commit()
                
        except sqlite3.OperationalError:
            QMessageBox.critical(self, _('Error'), _('There is no list called {todolist}.').format(todolist = todolist))
            return
        
        self.refresh()
        self.entry.setText("")
        
        with sqlite3.connect(f"{userdata}todos.db", timeout=5) as self.db_delete2:
            self.cur_delete2 = self.db_delete2.cursor()
            
            try:
                self.cur_delete2.execute(f"select * from '{todolist}'")
                self.cur_delete2.fetchall()
            
            except sqlite3.OperationalError:
                self.cur_delete2.execute(f"select name from todos")
                self.fetch_delete2 = self.cur_delete2.fetchall()
                    
                if todolist not in self.fetch_delete2:
                    db_start()
                    QMessageBox.information(self, _('Successful'), _('{todolist} list deleted.').format(todolist = todolist))
            
            else:
                QMessageBox.critical(self, _('Error'), _('Failed to delete {todolist} list.').format(todolist = todolist))
    
    def delete_all(self):
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all1:
            self.cur_delete_all1 = self.db_delete_all1.cursor()
            self.cur_delete_all1.execute(f"select name from todos")
            self.fetch_delete_all1 = self.cur_delete_all1.fetchall()
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all2:
            self.cur_delete_all2 = self.db_delete_all2.cursor()
            self.cur_delete_all2.execute("DROP TABLE todos")
            
            for todolist in self.fetch_delete_all1:
                self.cur_delete_all2.execute(f"DROP TABLE {todolist[0]}")
        
        with sqlite3.connect(f"{userdata}todos.db") as self.db_delete_all3:
            self.cur_delete_all3 = self.db_delete_all3.cursor()
            
            try:
                for todolist in self.fetch_delete_all1:
                    self.cur_delete_all3.execute(f"select * from {todolist[0]}")
                self.cur_delete_all3.fetchall()
                
            except sqlite3.OperationalError:
                try:
                    self.cur_delete_all3.execute(f"select name from todos'")
                    self.cur_delete_all3.fetchall()

                except sqlite3.OperationalError:
                    db_start()
                    self.refresh()
                    
                    QMessageBox.information(self, _('Successful'), _('All todolists deleted.'))

            else:
                QMessageBox.critical(self, _('Error'), _('Failed to delete all todolists.')) 
    
    
if __name__ == "__main__":
    application = QApplication(sys.argv)

    window = QMainWindow()
    window.setStatusBar(QStatusBar(window))
    window.setStatusTip(_('Copyright (C) 2024 MuKonqi (Muhammed S.), licensed under GPLv3 or later'))
    window.setGeometry(0, 0, 960, 540)
    window.setWindowTitle("Nottodbox: Todos")
    
    widget = QWidget(parent = window)
    widget.setLayout(QVBoxLayout(widget))
    widget.layout().addWidget(Todos(parent = widget))
    
    window.setCentralWidget(widget)
    window.show()

    application.exec()