#!@PYTHON3@

# SPDX-License-Identifier: GPL-3.0-or-later

# Nottodbox (io.github.mukonqi.nottodbox)

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
import os
import gettext
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


gettext.bindtextdomain("nottodbox", "@LOCALEDIR@")
gettext.textdomain("nottodbox")


username = getpass.getuser()
userdata = f"/home/{username}/.config/nottodbox/"
if not os.path.isdir(userdata):
    os.mkdir(userdata)


sys.path.insert(1, '@APPDIR@')
from mainwindow import MainWindow


class Application(QApplication):
    def __init__(self, argv: list, index: int = 0) -> None:
        super().__init__(argv)

        with open("@APPDIR@/style.qss") as style_file:
            style = style_file.read()
        
        self.setApplicationVersion("@VERSION@")
        self.setApplicationName("nottodbox")
        self.setApplicationDisplayName("Nottodbox")
        self.setDesktopFileName("@DESKTOPFILE@")
        self.setWindowIcon(QIcon("@ICONFILE_SVG@"))
        self.setStyleSheet(style)
        
        window = MainWindow()
        window.tabwidget.setCurrentIndex(index)
        window.show()

if __name__ == "__main__":
    if len(sys.argv[1:]) >= 1 and 0 <= int(sys.argv[1]) <= 5:
        application = Application(sys.argv, int(sys.argv[1]))
    else:
        application = Application(sys.argv)

    sys.exit(application.exec())