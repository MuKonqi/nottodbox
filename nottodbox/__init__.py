#!@PYTHON3@

# SPDX-License-Identifier: GPL-3.0-or-later

# Nottodbox (io.github.mukonqi.nottodbox)

# Copyright (C) 2024-2025 Mukonqi (Muhammed S.)

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


gettext.bindtextdomain("nottodbox", "@LOCALEDIR@")
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
parser.add_argument("-v", "--version", help=_("show the version"), action="version", version="@VERSION@")
group.add_argument("-i", "--index", help=_("set the page to be opened via number"), default=0,
                   choices=[1, 2, 3, 4, 5, 6], type=int)
group.add_argument("-p", "--page", help=_("set the page to be opened via name"), default=_("home"), 
                   choices=[__("Home"), __("Notes"), __("To-Dos"), __("Diaries"), __("Settings"), __("About")], type=str)

args = parser.parse_args()


username = getpass.getuser()
userdata = f"/home/{username}/.config/io.github.mukonqi/nottodbox"
if not os.path.isdir(userdata):
    os.makedirs(userdata)   


sys.path.insert(1, '@APPDIR@')
from mainwindow import MainWindow


class Application(QApplication):
    def __init__(self, argv: list) -> None:
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
        
        if args.index:
            window.tabwidget.setCurrentIndex(args.index - 1)
        
        elif args.page:
            if args.page == _("Home"):
                window.tabwidget.setCurrentIndex(0)
            
            elif args.page == __("Notes"):
                window.tabwidget.setCurrentIndex(1)
                
            elif args.page == __("To-Dos"):
                window.tabwidget.setCurrentIndex(2)
                
            elif args.page == __("Diaries"):
                window.tabwidget.setCurrentIndex(3)
                
            elif args.page == __("Settings"):
                window.tabwidget.setCurrentIndex(4)
                
            elif args.page == __("About"):
                window.tabwidget.setCurrentIndex(5)

if __name__ == "__main__":
    application = Application(sys.argv)

    sys.exit(application.exec())