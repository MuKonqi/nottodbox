import sys
import locale
import getpass
import os
from PyQt6.QtCore import Qt, QStringListModel
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

class Sidebar(QListView):
    def __init__(
        self, 
        parent: QMainWindow | QWidget, 
        notes: QTabWidget | QWidget, 
        todos: QTabWidget | QWidget,
        diaries: QTabWidget | QWidget):
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
        if sidebar_items[key] == sidebar_notes:
            length = len(_("Note"))
            
            if key.endswith(_(" (Backup)")):
                sidebar_notes.setCurrentWidget(sidebar_notes.backups[key[(length + 2):].replace(_(" (Backup)"), "")])

            else:
                sidebar_notes.setCurrentWidget(sidebar_notes.notes[key[(length + 2):]])
                
        elif sidebar_items[key] == sidebar_todos:
            length = len(_("Todolist"))
            
            sidebar_todos.setCurrentWidget(sidebar_todos.todolists[key[(length + 2):]])

        elif sidebar_items[key] == sidebar_diaries:
            length = len(_("Diary for"))
            
            if key.endswith(_(" (Backup)")):
                sidebar_diaries.setCurrentWidget(sidebar_diaries.backups[key[(length + 2):].replace(_(" (Backup)"), "")])

            else:
                sidebar_diaries.setCurrentWidget(sidebar_diaries.diaries[key[(length + 2):]])
        
        sidebar_parent.tabview.setCurrentWidget(sidebar_items[key])
        
    def add(text: str, target: QTabWidget | QWidget):
        stringlist = sidebar_model.stringList()

        if target == sidebar_notes:
            stringlist.append(_("Note: {name}").format(name = text))
            sidebar_items[_("Note: {name}").format(name = text)] = target
            
        elif target == sidebar_todos:
            stringlist.append(_("Todolist: {todolist}").format(todolist = text))
            sidebar_items[_("Todolist: {todolist} todolist").format(todolist = text)] = target
            
        elif target == sidebar_diaries:
            stringlist.append(_("Diary for: {date}").format(date = text))
            sidebar_items[_("Diary for: {date}").format(date = text)] = target
        
        sidebar_model.setStringList(stringlist)
    
    def remove(text: str, target: QTabWidget | QWidget):
        stringlist = sidebar_model.stringList()

        if target == sidebar_notes:
            stringlist.remove(_("Note: {name}").format(name = text))
            try:
                del sidebar_items[_("Note: {name}").format(name = text)]
            except KeyError:
                pass
            
        elif target == sidebar_todos:
            stringlist.remove(_("Todolist: {todolist}").format(todolist = text))
            del sidebar_items[_("Todolist: {todolist} todolist").format(todolist = text)]
            
        elif target == sidebar_diaries:
            stringlist.remove(_("Diary for: {date}").format(date = text))
            try:
                del sidebar_items[_("Diary for: {date}").format(date = text)]
            except KeyError:
                pass
        
        sidebar_model.setStringList(stringlist)

       
if __name__ == "__main__":    
    from mainwindow import MainWindow
    
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    application.exec()