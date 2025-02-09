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
from PySide6.QtCore import Slot, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import *
from settings import settings
from .dialogs import ColorDialog, GetDateDialog
from .lists import TreeView
from .others import Action, HSeperator, Label, VSeperator, PushButton
from .pages import NormalPage, BackupPage


class TabWidget(QTabWidget):
    def __init__(self, parent: QMainWindow, module: str) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        
        self.backups = {}
        self.pages = {}
        
        self.current_index = 0
        self.last_closed = None
        
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.setUsesScrollButtons(True)
        
        self.tabCloseRequested.connect(self.closeTab)
        self.currentChanged.connect(self.tabChanged)
        
    @Slot(int)
    def closeTab(self, index: int) -> None:
        if hasattr(self, "home"):
            if index != self.indexOf(self.home):           
                page = self.tabText(index).replace("&", "")
                
                if not page.endswith(_(" (Backup)")):
                    if self.module == "notes":
                        name, table = str(page).split(" @ ")
                    
                    elif self.module == "diaries":
                        name = page
                        table = "__main__"
                    
                    if not self.pages[(name, table)].closable:
                        self.question = QMessageBox.question(self, 
                                                            _("Question"),
                                                            _("{item} not saved.\nWhat would you like to do?")
                                                            .format(item = _("{name} note" if self.module == "notes" else "{name} diary").format(name = name)),
                                                            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                                                            QMessageBox.StandardButton.Save)
                        
                        if self.question == QMessageBox.StandardButton.Save:
                            if not self.pages[(name, table)].saver.saveChild():
                                return
                        
                        elif self.question != QMessageBox.StandardButton.Discard:
                            return
                        
                    if self.module == "diaries" and QDate.fromString(name, "dd.MM.yyyy") != QDate.currentDate():
                        if not self.pages[(name, table)].makeBackup():
                            return
                        
                    self.last_closed = self.pages[(name, table)]
                    
                    del self.pages[(name, table)]
                    
                    if not hasattr(self, "closable"):
                        self.closable = True
                    
                    if not str(page).endswith(_(" (Backup)")):
                        if self.module == "notes":
                            self.parent_.dock.widget().open_pages.deletePage(self.module, f"{name} @ {table}")
                            
                        elif self.module == "diaries":
                            self.parent_.dock.widget().open_pages.deletePage(self.module, name)
                                            
                self.removeTab(index)
                
    @Slot(int)
    def tabChanged(self, index: int) -> None:
        if index != self.current_index:
            old_widget = self.widget(self.current_index)
            
            if old_widget is None:
                old_widget = self.last_closed
            
            if old_widget != self.home and old_widget.mode == "normal":
                old_widget.disconnectAutosaveConnections()
                
            new_widget = self.widget(index)
            
            if new_widget != self.home and new_widget.mode == "normal":
                new_widget.changeAutosaveConnections()
            
            self.current_index = index
            

class HomePage(QWidget):
    def __init__(self, parent: TabWidget | QMainWindow, module: str, db):
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.db = db
        
        self.name = ""
        self.table = ""
        
        if module == "notes":
            self.menu = self.parent_.parent_.menuBar().addMenu(_("Notes"))
        
        elif module == "todos":
            self.menu = self.parent_.menuBar().addMenu(_("To-Dos"))
            
        elif module == "diaries":
            self.menu = self.parent_.parent_.menuBar().addMenu(_("Diaries"))
            
        self.shortcuts = {}
        
        self.layout_ = QGridLayout(self)
        self.setLayout(self.layout_)
        self.appendAll()
        
        self.refreshSettingsBase()
        
    def appendAll(self) -> None:
        pass
        
    def refreshSettingsBase(self) -> None:
        self.autosave, self.background, self.foreground, self.format, self.highlight = settings.get(self.module)
        
    def returnPretty(self, name: str, table: str) -> str:
        if self.module == "notes":
            return f"{name} @ {table}"
        
        elif self.module == "todos":
            status = self.db.getStatus(name, table)
            
            if status == "completed":
                return f"[+] {name} @ {table}"
            elif status == "uncompleted":
                return f"[-] {name} @ {table}"

        elif self.module == "diaries":
            return name
    
    @Slot(str, str)
    def setSelectedItem(self, name: str, table: str = "__main__") -> None:
        self.table = table
        self.name = name
        
    @Slot(str, str)
    def shortcutEvent(self, name: str, table: str = "__main__") -> None:
        pass
    
    
class HomePageForDocuments(HomePage):    
    def refreshSettingsForDocuments(self) -> None:
        self.refreshSettingsBase()
        
        for page in list(self.parent_.pages.values()):
            if page.call_format == "global":
                page.format = self.format
                page.formatter.updateStatus(self.format)
                
            page.format_combobox.setItemText(0, "{} {}".format(_("Format:"), _("Follow global ({setting})")
                                                               .format(setting = page.prettyFormat(self.format))))
            
            if page.call_autosave == "global":
                page.autosave = self.autosave
                
                page.changeAutosaveConnections()
                
            page.autosave_combobox.setItemText(0, "{} {}".format(_("Auto-save:"), _("Follow global ({setting})")
                                                                 .format(setting = page.prettyAutosave(self.autosave))))
        
        
class HomePageForLists(HomePage):
    def __init__(self, parent: TabWidget, module: str, db) -> None:
        super().__init__(parent, module, db)
        
        db.widget = self
        
        self.child_counts = {}
        self.child_items = {}
        self.table_counts = {}
        self.table_items = {}
        
        self.selecteds = QWidget(self)
        self.selecteds_layout = QHBoxLayout(self.selecteds)
        
        self.parent_selected = Label(self.selecteds, "{}: ".format(self.localizedParent().title()))
        self.child_selected = Label(self.selecteds, "{}: ".format(self.localizedChild().title()))
        
        self.treeview = TreeView(self, self.module, db)
        
        self.entry = QLineEdit(self)
        self.entry.setClearButtonEnabled(True)
        self.entry.setPlaceholderText(_("Search..."))
        self.entry.textEdited.connect(self.treeview.setFilter)
        
        self.none_options = NoneOptions(self, self.module, self.db)
        
        self.child_options = QWidget
        
        self.parent_options = ParentOptions(self, self.module, self.db)
        self.parent_options.setVisible(False)
        
        self.current_widget = self.none_options
        
        self.selecteds.setLayout(self.selecteds_layout)
        self.selecteds_layout.addWidget(self.parent_selected)
        self.selecteds_layout.addWidget(self.child_selected)
        
        self.layout_.addWidget(self.selecteds, 0, 0, 1, 3)
        self.layout_.addWidget(HSeperator(self), 1, 0, 1, 3)
        self.layout_.addWidget(self.entry, 2, 0, 1, 1)
        self.layout_.addWidget(HSeperator(self), 3, 0, 1, 1)
        self.layout_.addWidget(self.treeview, 4, 0, 1, 1)
        self.layout_.addWidget(VSeperator(self), 2, 1, 3, 1)
        self.layout_.addWidget(self.none_options, 2, 2, 3, 1)
        
    def appendAll(self):
        all = self.db.getAll()
        
        for table in all:
            for name in all[table]:
                name = name[0]
                
                self.shortcuts[(name, table)] = Action(self, self.returnPretty(name, table))
                self.shortcuts[(name, table)].triggered.connect(
                    lambda state, name = name: self.shortcutEvent(name, table))
                self.menu.addAction(self.shortcuts[(name, table)])
        
    def localizedChild(self) -> str:
        if self.module == "notes":
            return _("note")
        
        elif self.module == "todos":
            return _("to-do")
        
    def localizedParent(self) -> str:
        if self.module == "notes":
            return _("notebook")
        
        elif self.module == "todos":
            return _("to-do list")
        
    def refreshSettingsForLists(self) -> None:
        self.refreshSettingsBase()
        
        self.treeview.deleteAll()
        self.treeview.setIndex("", "")
        self.treeview.appendAll()
        
    @Slot(str, str)
    def setOptionWidget(self, name: str = "", table: str = "") -> None:
        super().setSelectedItem(name, table)
        
        if table == "__main__":
            table = name
            name = ""

        self.none_options.setVisible(False)
        self.parent_options.setVisible(False)
        self.child_options.setVisible(False)
        
        if self.table == "":
            self.none_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.none_options)
            
            self.current_widget = self.none_options
            
        elif self.table != "" and self.name == "":
            self.parent_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.parent_options)
            
            self.current_widget = self.parent_options
            
        elif self.table != "" and self.name != "":
            self.child_options.setVisible(True)
            self.layout_.replaceWidget(self.current_widget, self.child_options)
            
            self.current_widget = self.child_options
            
        self.parent_selected.setText("{}: ".format(self.localizedParent().title()) + table)
        self.child_selected.setText("{}: ".format(self.localizedChild().title()) + name)
    
    
class Options(QWidget):
    def __init__(self, parent: HomePage | HomePageForLists, module: str, db) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        self.module = module
        self.db = db
        
        self.layout_ = QVBoxLayout(self)
        self.setLayout(self.layout_)
        self.setFixedWidth(200)
        
        self.rename_button = PushButton(self, _("Rename"))
        self.rename_button.clicked.connect(self.rename)
        
        self.delete_button = PushButton(self, _("Delete"))
        self.delete_button.clicked.connect(self.delete)
        
        self.delete_all_button = PushButton(self, _("Delete All"))
        self.delete_all_button.clicked.connect(self.deleteAll)
        
    def autoGet(self) -> tuple[str, str]:
        if self.parent_.name == "":
            return self.parent_.table, "__main__"
            
        else:
            return self.parent_.name, self.parent_.table
    
    def checkIfItExists(self, name: str, table: str = "__main__", messages: bool = True) -> bool:
        if self.checkTheName(name, table, messages):
            call = self.db.checkIfItExists(name, table)
                
            if not call and messages:
                QMessageBox.critical(self, _("Error"), _("There is no {item}.")
                                    .format(item = self.localizedItem(name, table)))
                
            return call
    
    def checkTheName(self, name: str, table: str = "__main__", messages: bool = True) -> bool:
        if "'" in name or "@" in name:
            if messages:
                QMessageBox.critical(self, _("Error"), _("The name can not contain these characters: ' and @"))
            
            return False
        
        elif "__main__" == name and "__main__" == table:
            if messages:
                QMessageBox.critical(self, _("Error"), _("The name can not be to __main__."))
            
            return False
        
        else:
            return True
        
    @Slot()
    def delete(self) -> tuple[bool, str, str]:
        name, table = self.autoGet()
        
        if self.checkIfItExists(name, table):
            question = QMessageBox.question(self, _("Question"), _("Do you really want to delete the {item}?")
                                            .format(item = self.localizedTheItem(name, table)))
            
            if question == QMessageBox.StandardButton.Yes:
                if self.db.delete(name, table):
                    self.parent_.setSelectedItem("", table)
                    
                    if table == "__main__" and self.module != "diaries":
                        for child, parent in self.parent_.shortcuts.copy().keys():
                            if parent == name:
                                self.parent_.menu.removeAction(self.parent_.shortcuts[(child, parent)])
                                del self.parent_.shortcuts[(child, parent)]
                            
                    else:
                        self.parent_.menu.removeAction(self.parent_.shortcuts[(name, table)])
                        del self.parent_.shortcuts[(name, table)]
                                            
                    return True, name, table
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to delete {item}.")
                                        .format(item = self.localizedItem(name, table)))
                    
        return False, "", ""
        
    @Slot()
    def deleteAll(self) -> bool:
        question = QMessageBox.question(self, _("Question"), _("Do you really want to delete all {the_items}?")
                                        .format(the_items = self.localizedModuleTheItems()))
        
        if question == QMessageBox.StandardButton.Yes:
            if self.db.deleteAll():
                self.parent_.setSelectedItem("", "")
                
                self.parent_.menu.clear()
                self.parent_.shortcuts.clear()
                
                return True

            else:
                QMessageBox.critical(self, _("Error"), _("Failed to delete all {items}.")
                                     .format(items = self.localizedModuleItems()))
                
                return False
            
    def localizedChild(self) -> str:
        if self.module == "notes":
            return _("note")
        
        elif self.module == "diary":
            return _("diary")
        
        elif self.module == "todos":
            return _("to-do")
            
    def localizedChildItem(self, name: str) -> str:
        if self.module == "notes":
            return _("{name} note").format(name = name)

        elif self.module == "diaries":
            return _("{name} dated diary").format(name = name)
        
        elif self.module == "todos":
            return _("{name} to-do").format(name = name)
        
    def localizedChildOfItem(self, name: str) -> str:
        if self.module == "notes":
            return _("of {name} note").format(name = name)

        elif self.module == "diaries":
            return _("of {name} dated diary").format(name = name)
        
        elif self.module == "todos":
            return _("of {name} to-do").format(name = name)
        
    def localizedChildTheItem(self, name: str) -> str:
        if self.module == "notes":
            return _("the {name} note").format(name = name)
        
        elif self.module == "diaries":
            return _("the {name} dated diary").format(name = name)
        
        elif self.module == "todos":
            return _("the {name} to-do").format(name = name)
        
    def localizedModuleItems(self) -> str:
        if self.module == "notes":
            return _("Notes").lower()
        
        elif self.module == "diaries":
            return _("Diaries").lower()
        
        elif self.module == "todos":
            return _("To-Dos").lower()
        
    def localizedModuleTheItems(self) -> str:
        if self.module == "notes":
            return _("the notes")
        
        elif self.module == "diaries":
            return _("the diaries")
        
        elif self.module == "todos":
            return _("the to-dos")
    
    def localizedItem(self, name: str, table: str = "__main__") -> str:
        if table == "__main__" and self.module != "diaries":
            return self.localizedParentItem(name)
        
        else:
            return self.localizedChildItem(name)
        
    def localizedTheItem(self, name: str, table: str = "__main__") -> str:
        if table == "__main__" and self.module != "diaries":
            return self.localizedParentTheItem(name)
        
        else:
            return self.localizedChildTheItem(name)
        
    def localizedParent(self) -> str:
        if self.module == "notes":
            return _("notebook")
        
        elif self.module == "todos":
            return _("to-do list")
        
    def localizedParentItem(self, name: str) -> str:
        if self.module == "notes":
            return _("{name} notebook").format(name = name)
        
        elif self.module == "todos":
            return _("{name} to-do list").format(name = name)
        
    def localizedParentTheItem(self, name: str) -> str:
        if self.module == "notes":
            return _("the {name} notebook").format(name = name)
        
        elif self.module == "todos":
            return _("the {name} to-do list").format(name = name)
        
    @Slot()
    def rename(self) -> tuple[bool, str, str, str]:
        name, table = self.autoGet()
        
        if self.checkIfItExists(name, table):
            if self.module == "diaries":
                question = QMessageBox.question(
                    self, _("Question"), _("Diaries are unique to the day they are written.\nDo you really want to rename the diary?"))

                if question != QMessageBox.StandardButton.Yes:
                    return
                
                newname, topwindow = GetDateDialog(self, 
                                                   _("Rename {the_item}").format(the_item = self.localizedTheItem(name, table)).title(), 
                                                   _("Please select a new date for {the_item}.").format(the_item = self.localizedTheItem(name, table)),
                                                   name).getResult()
                
            else:
                newname, topwindow = QInputDialog.getText(self,
                                                _("Rename {the_item}").format(the_item = self.localizedTheItem(name, table)).title(), 
                                                _("Please enter a new name for {the_item}.").format(the_item = self.localizedTheItem(name, table)))
            
            if topwindow and newname != "":
                if self.checkTheName(newname) and not self.checkIfItExists(newname, table, False):
                    if self.db.rename(newname, name, table):
                        self.parent_.setSelectedItem(newname, table)
                        
                        if table == "__main__" and self.module != "diaries":
                            for child, parent in self.parent_.shortcuts.copy().keys():
                                if parent == name:
                                    self.parent_.shortcuts[(child, parent)].setText(self.parent_.returnPretty(child, newname))
                                    self.parent_.shortcuts[(child, parent)].triggered.disconnect()
                                    self.parent_.shortcuts[(child, parent)].triggered.connect(
                                        lambda state, child = child: self.parent_.shortcutEvent(child, newname))
                                    self.parent_.shortcuts[(child, newname)] = self.parent_.shortcuts.pop((child, parent))
                                    
                        else:
                            self.parent_.shortcuts[(name, table)].setText(self.parent_.returnPretty(newname, table))
                            self.parent_.shortcuts[(name, table)].triggered.disconnect()
                            self.parent_.shortcuts[(name, table)].triggered.connect(
                                lambda state: self.parent_.shortcutEvent(newname, table))
                            self.parent_.shortcuts[(newname, table)] = self.parent_.shortcuts.pop((name, table))
                            
                        return True, newname, name, table
        
                    else:
                        QMessageBox.critical(self, _("Error"), _("Failed to rename {item}.")
                                            .format(item = self.localizedItem(name, table)))
                
                else:
                    QMessageBox.critical(self, _("Error"), _("Already existing {newitem}, renaming {the_item} cancalled.")
                                        .format(newitem = self.localizedItem(newname, table), 
                                                the_item = self.localizedTheItem(name, table)))
                
        return False, "", "", ""
                

class OptionsForDocuments(Options):
    def __init__(self, parent: HomePage | HomePage, module: str, db):
        super().__init__(parent, module, db)
        
        self.open_button = PushButton(self, _("Open"))
        self.open_button.clicked.connect(self.open)
        
        self.show_backup_button = PushButton(self, _("Show Backup"))
        self.show_backup_button.clicked.connect(self.showBackup)

        self.restore_content_button = PushButton(self, _("Restore Content"))
        self.restore_content_button.clicked.connect(self.restoreContent)
        
        self.clear_content_button = PushButton(self, _("Clear Content"))
        self.clear_content_button.clicked.connect(self.clearContent)
    
    def checkIfBackupExists(self, name: str, table: str) -> bool:  
        call = self.db.checkIfTheChildBackupExists(name, table)
        
        if not call:
            QMessageBox.critical(self, _("Error"), _("There is no backup for {item}.")
                                 .format(item = self.localizedChildItem(name)))
        
        return call
    
    @Slot()
    def clearContent(self) -> None:
        name = self.parent_.name
        table = self.parent_.table
        
        if self.checkIfItExists(name, table):
            question = QMessageBox.question(self, _("Question"), _("Do you really want to clear the content {of_item}?")
                                            .format(of_item = self.localizedChildOfItem(name)))
            
            if question == QMessageBox.StandardButton.Yes:
                if self.db.clearContent(name, table):
                    QMessageBox.information(self, _("Successful"), _("Content {of_item} cleared.")
                                            .format(of_item = self.localizedChildOfItem(name)))
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to clear content {of_item}.")
                                        .format(of_item = self.localizedChildOfItem(name)))
        
    @Slot(bool, str)
    def open(self, state: bool, name: str = None, table: str = None) -> None:
        if name is None:
            name = self.parent_.name
        
        if table is None:
            table = self.parent_.table
        
        if self.checkIfItExists(name, table):
            if (name, table) in self.parent_.parent_.pages.keys():
                self.parent_.parent_.setCurrentWidget(self.parent_.parent_.pages[(name, table)])
                
            else:            
                self.parent_.parent_.pages[(name, table)] = NormalPage(self, self.module, 
                                                                       self.db, self.parent_.format, self.parent_.autosave, 
                                                                       name, table)
                self.parent_.parent_.addTab(self.parent_.parent_.pages[(name, table)], 
                                            self.parent_.returnPretty(name, table))
                self.parent_.parent_.setCurrentWidget(self.parent_.parent_.pages[(name, table)])
                self.parent_.parent_.parent_.dock.widget().open_pages.appendPage(self.module, self.parent_.returnPretty(name, table))
                
            self.parent_.parent_.parent_.tabwidget.setCurrentWidget(self.parent_.parent_)
            
    @Slot()
    def restoreContent(self) -> None:
        name = self.parent_.name
        table = self.parent_.table
        
        if self.checkIfBackupExists(name, table):
            if self.db.restoreContent(name, table):
                QMessageBox.information(self, _("Successful"), _("Backup {of_item} restored.")
                                        .format(of_item = self.localizedChildOfItem(name)))
                
            else:
                QMessageBox.critical(self, _("Error"), _("Failed to restore backup {of_item}.")
                                    .format(of_item = self.localizedChildOfItem(name)))
            
    @Slot()
    def showBackup(self) -> None:
        name = self.parent_.name
        table = self.parent_.table
        
        if self.checkIfBackupExists(name, table):
            self.parent_.parent_.backups[(name, table)] = BackupPage(self, self.module, 
                                                                     self.db, self.parent_.format, self.parent_.autosave,
                                                                     name, table)
            self.parent_.parent_.addTab(self.parent_.parent_.backups[(name, table)], 
                                        self.parent_.returnPretty(name, table) + _(" (Backup)"))
            self.parent_.parent_.setCurrentWidget(self.parent_.parent_.backups[(name, table)])
            
            self.parent_.parent_.parent_.tabwidget.setCurrentWidget(self.parent_.parent_)
                    
    
class OptionsForLists(Options):
    def __init__(self, parent: HomePage | HomePageForLists, module: str, db):
        super().__init__(parent, module, db)
        
        self.create_child_button = PushButton(self, _("Create {}")
                                             .format(self.localizedChild().title()))
        self.create_child_button.clicked.connect(self.createChild)
        
        self.create_parent_button = PushButton(self, _("Create {}")
                                                 .format(self.localizedParent().title()))
        self.create_parent_button.clicked.connect(self.createParent)
        
        self.set_background_button = PushButton(self, _("Set {} Color").format(_("Background")))
        self.set_background_button.clicked.connect(self.setBackground)
        
        self.set_foreground_button = PushButton(self, _("Set {} Color").format(_("Text")))
        self.set_foreground_button.clicked.connect(self.setForeground)
    
    @Slot()
    def createChild(self) -> None:
        table = self.parent_.table
        
        if self.checkIfItExists(table):
            name, topwindow = QInputDialog.getText(self, 
                                                _("Create {}").format(self.localizedChild().title()), 
                                                _("Please enter a name for creating a {}.").format(self.localizedChild()))
            
            if not self.checkTheName(name, table):
                return
            
            elif topwindow and name != "":
                if self.checkIfItExists(name, table, False):
                    QMessageBox.critical(self, _("Error"), _("{item} already created.")
                                        .format(item = self.localizedChildItem(name)))
            
                else:
                    if self.db.createChild(name, table):
                        self.parent_.shortcuts[(name, table)] = Action(self, self.parent_.returnPretty(name, table))
                        self.parent_.shortcuts[(name, table)].triggered.connect(
                            lambda state: self.parent_.shortcutEvent(name, table))
                        self.parent_.menu.addAction(self.parent_.shortcuts[(name, table)]) 
                        
                        self.parent_.treeview.appendChild(name, table)
                        self.parent_.treeview.setIndex(name, table)
                        
                    else:
                        QMessageBox.critical(self, _("Error"), _("Failed to create {item}.")
                                            .format(item = self.localizedChildItem(name)))
    
    @Slot()
    def createParent(self) -> None:
        name, topwindow = QInputDialog.getText(self, 
                                               _("Create {}").format(self.localizedParent().title()), 
                                               _("Please enter a name for creating a {}.").format(self.localizedParent()))
        
        if not self.parent_.parent_options.checkTheName(name):
            return
        
        elif topwindow and name != "":
            if self.checkIfItExists(name, "__main__", False):
                QMessageBox.critical(self, _("Error"), _("{item} already created.")
                                     .format(item = self.localizedParentItem(name)))
        
            else:
                if self.db.createParent(name):
                    self.parent_.treeview.appendParent(name)
                    self.parent_.treeview.setIndex("", name)
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to create {item}.")
                                         .format(item = self.localizedParentItem(name)))
                    
    @Slot()
    def delete(self) -> None:
        call, name, table = super().delete()
        
        if call:
            if table == "__main__":
                self.parent_.treeview.deleteParent(name)
                self.parent_.treeview.setIndex("", "")
            else:
                self.parent_.treeview.deleteChild(name, table)
                self.parent_.treeview.setIndex("", table)
            
    @Slot()
    def deleteAll(self) -> None:
        if super().deleteAll():
            self.parent_.treeview.deleteAll()
            self.parent_.treeview.setIndex("", "")
    
    @Slot()
    def rename(self) -> None:
        call, newname, name, table = super().rename()
        
        if call:
            self.parent_.treeview.updateItem(newname, name, table)
            if table == "__main__":
                self.parent_.treeview.setIndex("", newname)
            else:
                self.parent_.treeview.setIndex(newname, "")
                    
    @Slot()
    def setBackground(self) -> None:
        name, table = self.autoGet()
        
        if self.checkIfItExists(name, table):
            background = self.db.getBackground(name)
            
            ok, status, qcolor = ColorDialog(self, True, True,
                QColor(background if background != "global" and background != "default"
                       else self.parent_.background if background == "global" and self.parent_.background != "default"
                       else ("#FFFFFF")),
                _("Select Background Color for {item}")
                .format(item = self.localizedItem(name, table)).title()).getColor()
            
            if ok:
                if status == "new":
                    color = qcolor.name()
                    
                elif status == "global":
                    color = "global"
                    
                elif status == "default":
                    color = "default"
                
                if self.db.setBackground(color, name, table):
                    self.parent_.treeview.updateBackground(color, name, table)
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to set background color for {item}.")
                                        .format(item = self.localizedItem(name, table)))
                    
    @Slot()
    def setForeground(self) -> None:
        name, table = self.autoGet()
        
        if self.checkIfItExists(name, table):
            foreground = self.db.getForeground(name)
            
            ok, status, qcolor = ColorDialog(self, True, True,
                QColor(foreground if foreground != "global" and foreground != "default"
                       else self.parent_.foreground if foreground == "global" and self.parent_.foreground != "default"
                       else ("#FFFFFF")),
                _("Select Text Color for {item}")
                .format(item = self.localizedItem(name, table)).title()).getColor()
            
            if ok:
                if status == "new":
                    color = qcolor.name()
                    
                elif status == "global":
                    color = "global"
                    
                elif status == "default":
                    color = "default"
                
                if self.db.setForeground(color, name, table):
                    self.parent_.treeview.updateForeground(color, name, table)
                    
                else:
                    QMessageBox.critical(self, _("Error"), _("Failed to set text color for {item}.")
                                        .format(item = self.localizedItem(name, table)))
                    

class NoneOptions(OptionsForLists):
    def __init__(self, parent: HomePageForLists, module: str, db) -> None:
        super().__init__(parent, module, db)
        
        self.delete_button.setVisible(False)
        self.rename_button.setVisible(False)
        self.create_child_button.setVisible(False)
        self.set_background_button.setVisible(False)
        self.set_foreground_button.setVisible(False)
        
        self.warning_label = Label(self, _("You can select\na {}\nor a {}\non the left.")
                                   .format(self.localizedParent(), self.localizedChild()))
        self.warning_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.layout_.addWidget(self.warning_label)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.create_parent_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)


class ParentOptions(OptionsForLists):
    def __init__(self, parent: HomePageForLists, module: str, db) -> None:
        super().__init__(parent, module, db)
        
        self.reset_button = PushButton(self, _("Reset"))
        self.reset_button.clicked.connect(self.reset)
        
        self.layout_.addWidget(self.create_child_button)
        self.layout_.addWidget(self.create_parent_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.reset_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.rename_button)
        self.layout_.addWidget(self.delete_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.delete_all_button)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.set_background_button)
        self.layout_.addWidget(self.set_foreground_button)
    
    @Slot()
    def reset(self) -> None:
        name = self.parent_.table
        
        if self.checkIfItExists(name):
            question = QMessageBox.question(self, _("Question"), _("Do you really want to reset the {item}?")
                                            .format(item = self.localizedParentTheItem(name)))
            
            if question == QMessageBox.StandardButton.Yes:
                if self.checkIfItExists(name):
                    if self.db.resetParent(name):
                        self.parent_.setSelectedItem("", name)
                        
                        for child, parent in self.parent_.shortcuts.copy().keys():
                            if parent == name:
                                self.parent_.menu.removeAction(self.parent_.shortcuts[(child, parent)])
                                del self.parent_.shortcuts[(child, parent)]
                        
                        self.parent_.treeview.deleteParent(name)
                        self.parent_.treeview.appendParent(name)
                        self.parent_.treeview.setIndex("", name)
                        
                    else:
                        QMessageBox.critical(self, _("Error"), _("Failed to reset {item}.")
                                            .format(item = self.localizedParentItem(name)))