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


if __name__ == "__main__":
    import sys
    from application import Application
    
    application = Application(sys.argv, 4)
    
    sys.exit(application.exec())


import locale
import gettext
import getpass
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


if locale.getlocale()[0].startswith("tr"):
    language = "tr"
    translations = gettext.translation("nottodbox", "mo", languages=["tr"], fallback=True)
else:
    language = "en"
    translations = gettext.translation("nottodbox", "mo", languages=["en"], fallback=True)
translations.install()

_ = translations.gettext

align_center = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter

username = getpass.getuser()
userdata = f"/home/{username}/.local/share/nottodbox/"


defaults = {
    "autosave": "true",
    "format": "markdown",
    "space": "2",
}

settings = {
    "notes-autosave": "",
    "notes-format": "",
    "diaries-autosave": "",
    "diaries-format": "",
    "diaries-space": ""
}

print(settings[1])

class SettingsDB:
    """The settings database pool."""
    
    def __init__(self) -> None:
        """Connect database and then set cursor."""
        
        self.db = sqlite3.connect(f"{userdata}settings.db")
        self.cur = self.db.cursor()
        
    def checkIfTheTableExists(self) -> bool:
        """
        Check if the table exists.

        Returns:
            bool: True if the table exists, if not False
        """
        
        try:
            self.cur.execute("select * from settings")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createTable(self) -> bool:
        """
        If the settings table not exists, create it.

        Returns:
            bool: True if successful, False if unsuccesful
        """
        
        sql = """
        CREATE TABLE IF NOT EXISTS settings (
            setting TEXT NOT NULL PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
        
        self.cur.execute(sql)
        self.db.commit()
        
        call = self.checkIfTheTableExists()
        
        if call:
            self.getAllSettings()
        
        return call
    
    def getAllSettings(self) -> None:
        """Get all settings' values."""

        for setting, value in settings.items():
                setting.replace("-", " ")
                self.getSetting(setting.split()[0], setting.split(1))
    
    def getSetting(self, module: str, setting: str) -> str:
        """
        Get the setting's value. If not any value, create them with default value.

        Args:
            module (str): The module
            setting (str): The setting

        Returns:
            str: Setting's value
        """
        
        global settings
        
        settings[f"{module}-{setting}"]
               
        try:
            self.cur.execute(f"select value from settings where setting = '{module}-{setting}'")
            return self.cur.fetchone()[0]

        except:
            self.cur.execute(f"insert into settings (setting, value) values ('{module}-{setting}', '{defaults[setting]}')")
            self.db.commit()
            return defaults[setting]
        
    def updateSetting(self, module: str, setting: str, value: str) -> bool:
        """
        Update the setting.

        Args:
            module (str): The module
            setting (str): The setting
            value (str): New value

        Returns:
            bool: True if successful, False if not
        """
            
        self.cur.execute(f"update settings set value = '{value}' where setting = '{module}-{setting}'")
        self.db.commit()
        
        call = self.getSetting(module, setting)
        
        if call[0] == value:
            global settings
            settings[f"module-setting"] = value

            return True

        elif call[0] == value:
            return False

settingsdb = SettingsDB()

create_table = settingsdb.createTable()
if create_table:
    table = True
else:
    table = False