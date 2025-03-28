#!@PYTHON3@

# SPDX-License-Identifier: GPL-3.0-or-later

# Nottodbox (io.github.mukonqi.nottodbox)

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


import sys
import argparse
import os
import gettext
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


sys.path.insert(1, "@APP_DIR@" if os.path.isdir("@APP_DIR@") else os.path.dirname(__file__))

from consts import APP_ID, APP_VERSION, DESKTOP_FILE, ICON_FILE, LOCALE_DIR, USER_DESKTOP_FILE, USER_DESKTOP_FILE_FOUND  # type: ignore


gettext.bindtextdomain("nottodbox", LOCALE_DIR)
gettext.textdomain("nottodbox")

_ = gettext.gettext

def __(message: str) -> str:
    return _(message).lower()


class CustomFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix = None):
        if prefix is None:
            prefix = _("usage: ")
        
        return super().add_usage(usage, actions, groups, prefix)

parser = argparse.ArgumentParser(prog="nottodbox", add_help=False, formatter_class=CustomFormatter)
parser._positionals.title = _("positional arguments")
parser._optionals.title = _("optional arguments")
group = parser.add_mutually_exclusive_group()

parser.add_argument("-h", "--help", help=_("show this help message"), action="help", default=argparse.SUPPRESS)
parser.add_argument("-v", "--version", help=_("show the version"), action="version", version=APP_VERSION)
group.add_argument("-i", "--index", help=_("set the page to be opened via number"), default=1,
                   choices=[1, 2, 3, 4, 5], type=int)
group.add_argument("-p", "--page", help=_("set the page to be opened via name"), default=_("home"), 
                   choices=[__("Home"), __("Notes"), __("To-Dos"), __("Diaries"), __("Settings")], type=str)

args = parser.parse_args()


from mainwindow import MainWindow

class Application(QApplication):
    def __init__(self, argv: list) -> None:
        super().__init__(argv)

        self.setApplicationVersion(APP_VERSION)
        self.setApplicationName("nottodbox")
        self.setApplicationDisplayName("Nottodbox")
        self.setDesktopFileName(USER_DESKTOP_FILE if USER_DESKTOP_FILE_FOUND else DESKTOP_FILE)
        self.setWindowIcon(QIcon.fromTheme(APP_ID, QIcon(ICON_FILE)))
        
        window = MainWindow()
        
        if args.index:
            window.tabwidget.setCurrentPage(args.index - 1)
        
        elif args.page:
            if args.page == _("Home"):
                window.tabwidget.setCurrentPage(0)
            
            elif args.page == __("Notes"):
                window.tabwidget.setCurrentPage(1)
                
            elif args.page == __("To-Dos"):
                window.tabwidget.setCurrentPage(2)
                
            elif args.page == __("Diaries"):
                window.tabwidget.setCurrentPage(3)
                
            elif args.page == __("Settings"):
                window.tabwidget.setCurrentPage(4)
                

application = Application(sys.argv)

sys.exit(application.exec())