import os
import sys
import shutil
import datetime
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "nottodbox"))

from consts import USER_DATABASES_DIR # type: ignore


os.makedirs(USER_DATABASES_DIR, exist_ok=True)

for file in os.listdir(USER_DATABASES_DIR):
    file = os.path.join(USER_DATABASES_DIR, file)
    
    shutil.move(file, f"{file}.bak")
    
    
from notes import NotesDB # type: ignore
from todos import TodosDB # type: ignore
from diaries import DiariesDB # type: ignore


notes = [("My Favorite Games", "Blog"),
         ("About Nottodbox - A Life Changer", "Blog"),
         ("Biology: Hereditary Diseases", "School Projects"),
         ("English: Book Report", "School Homeworks")]

notesdb = NotesDB()

notesdb.createParent("Blog")
notesdb.createParent("School Projects")
notesdb.createParent("School Homeworks")

for name, table in notes:
    notesdb.createChild(name, table)


todosdb = TodosDB()

todosdb.createParent("Nottodbox")
todosdb.createChild("Make a custom tab bar for main window and settings", "Nottodbox")
todosdb.createChild("Make a screenshot helper", "Nottodbox")
todosdb.createChild("Make a page grid helper", "Nottodbox")
todosdb.changeStatus("Make a screenshot helper", "Nottodbox")
todosdb.changeStatus("Make a custom tab bar for main window and settings", "Nottodbox")


diariesdb = DiariesDB()

diariesdb.createChild(datetime.date.today().strftime("%d/%m/%Y"))
diariesdb.saveChild("Hello my dear diary!\nI'm good, because writing diaries can make people happy.\nSee you tomorrow!", "", False, datetime.date.today().strftime("%d/%m/%Y"))


settings = QSettings("io.github.mukonqi", "nottodbox")
geometry = settings.value("mainwindow/geometry")
state = settings.value("mainwindow/state")
settings.setValue("mainwindow/geometry", "")
settings.setValue("mainwindow/state", "")


from mainwindow import MainWindow # type: ignore


application = QApplication(sys.argv)
mainwindow = MainWindow()
list(mainwindow.settings.tabwidget.pages.keys())[0].widget().styles_combobox.setCurrentIndex(list(mainwindow.settings.tabwidget.pages.keys())[0].widget().styles_combobox.findText("Fusion"))
QApplication.setStyle("Fusion")
list(mainwindow.settings.tabwidget.pages.keys())[0].widget().color_schemes_combobox.setCurrentIndex(list(mainwindow.settings.tabwidget.pages.keys())[0].widget().color_schemes_combobox.findText("Nottodbox Light³"))
list(mainwindow.settings.tabwidget.pages.keys())[0].widget().loadPalette()
application.exec()

mainwindow.tabwidget.setCurrentPage(0)
mainwindow.home.todos.expandAll()
mainwindow.home.notes.expandAll()
mainwindow.grab().save(os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "home.png"))

mainwindow.notes.home.treeview.expandAll()
for name, table in notes:
    mainwindow.notes.home.child_options.open(False, name, table)
mainwindow.notes.setCurrentIndex(0)
mainwindow.grab().save(os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "notes.png"))

mainwindow.tabwidget.setCurrentPage(2)
mainwindow.todos.treeview.expandAll()
mainwindow.grab().save(os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "todos.png"))

mainwindow.tabwidget.setCurrentPage(3)
mainwindow.grab().save(os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "diaries.png"))

mainwindow.tabwidget.setCurrentPage(4)
mainwindow.grab().save(os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "settings.png"))


settings.setValue("mainwindow/geometry", geometry)
settings.setValue("mainwindow/state", state)

for file in os.listdir(USER_DATABASES_DIR):
    if file.endswith(".bak"):
        file = os.path.join(USER_DATABASES_DIR, file)
    
        shutil.move(file, file.removesuffix(".bak"))
        

sys.exit(0)