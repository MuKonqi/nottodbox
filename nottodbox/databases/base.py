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


import getpass
import os
import sqlite3


USER_DATABASES = f"/home/{getpass.getuser()}/.local/share/io.github.mukonqi/nottodbox/databases"
if not os.path.isdir(USER_DATABASES):
    os.makedirs(USER_DATABASES)


class DBBase:
    file = None
    widget = None
    
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{USER_DATABASES}/{self.file}", check_same_thread=False)
        self.cur = self.db.cursor()
        
        self.createMainTable()
        
    def checkIfTheTableExists(self, table: str = "__main__") -> bool:
        try:
            self.cur.execute(f"select * from '{table}'")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createMainTable(self, sql: str) -> bool:
        self.cur.execute(sql)
        self.db.commit()
        
        check = self.checkIfTheTableExists()
        
        if not check:
            print(f"[2] Failed to create main table for {self.file}")
            exit(2)
            
        return check
        
    def deleteAll(self) -> bool:
        self.cur.execute("DROP TABLE IF EXISTS __main__")
        self.db.commit()
        
        if self.checkIfTheTableExists():
            return False
        
        else:
            return self.createMainTable()