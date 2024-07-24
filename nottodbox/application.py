#!/usr/bin/env python3

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


import getpass
import os
import sys
from typing import List
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from mainwindow import MainWindow


username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)
    

class Application(QApplication):
    """The main QApplication class."""
    
    def __init__(self, argv: List[str], index: int = 0) -> None:
        """Init and set main application.

        Args:
            argv (List[str]): Mostly sys.argv
            index (int): Wanted index in tab widget. Defaults to 0.
        """
        
        super().__init__(argv)
        
        self.setApplicationName("nottodbox")
        self.setApplicationDisplayName("Nottodbox")
        # self.setWindowIcon(QIcon(""))
        
        window = MainWindow()
        window.tabwidget.setCurrentIndex(index)
        window.show()

if __name__ == "__main__":
    application = Application(sys.argv)

    sys.exit(application.exec())