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
import getpass
import argparse
import os
import gettext
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


gettext.bindtextdomain("nottodbox", "@LOCALE_DIR@" if os.path.isdir("@LOCALE_DIR@") else f"{os.path.dirname(__file__)}/locale")
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
parser.add_argument("-v", "--version", help=_("show the version"), action="version", version="v0.0.8-3")
group.add_argument("-i", "--index", help=_("set the page to be opened via number"), default=1,
                   choices=[1, 2, 3, 4, 5, 6], type=int)
group.add_argument("-p", "--page", help=_("set the page to be opened via name"), default=_("home"), 
                   choices=[__("Home"), __("Notes"), __("To-Dos"), __("Diaries"), __("Settings"), __("About")], type=str)

args = parser.parse_args()


APP_ID = "io.github.mukonqi.nottodbox"
USER_DATA = f"/home/{getpass.getuser()}/.local/share/nottodbox"
os.makedirs(USER_DATA, exist_ok=True)   


sys.path.insert(1, "@APP_DIR@" if os.path.isdir("@APP_DIR@") else os.path.dirname(__file__))


from mainwindow import MainWindow


class Application(QApplication):
    def __init__(self, argv: list) -> None:
        super().__init__(argv)

        self.setApplicationVersion("v0.0.8-3")
        self.setApplicationName("nottodbox")
        self.setApplicationDisplayName("Nottodbox")
        self.setDesktopFileName(os.path.join(self.getBaseDir(), "applications", f"{APP_ID}.desktop"))
        self.setWindowIcon(QIcon.fromTheme(APP_ID, 
                                           QIcon(os.path.join(self.getBaseDir(), "icons", "hicolor", "96x96", "apps", f"{APP_ID}.png"))))
        
        window = MainWindow()
        
        if args.index:
            window.tabwidget.tabbar.setCurrentIndex(args.index - 1)
        
        elif args.page:
            if args.page == _("Home"):
                window.tabwidget.tabbar.setCurrentIndex(0)
            
            elif args.page == __("Notes"):
                window.tabwidget.tabbar.setCurrentIndex(1)
                
            elif args.page == __("To-Dos"):
                window.tabwidget.tabbar.setCurrentIndex(2)
                
            elif args.page == __("Diaries"):
                window.tabwidget.tabbar.setCurrentIndex(3)
                
            elif args.page == __("Settings"):
                window.tabwidget.tabbar.setCurrentIndex(4)
                
            elif args.page == __("About"):
                window.tabwidget.tabbar.setCurrentIndex(5)
                
    def getBaseDir(self) -> str:
        if os.path.dirname(os.path.dirname(__file__)) == "site-packages":
            return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "share")
        
        else:
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), "share")
                

application = Application(sys.argv)

sys.exit(application.exec())