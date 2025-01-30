# SPDX-License-Identifier: GPL-3.0-or-later

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


import getpass
import datetime
import sqlite3


username = getpass.getuser()
userdata = f"/home/{username}/.config/io.github.mukonqi/nottodbox/"


class DBBase:
    file = None
    widget = None
    
    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{userdata}{self.file}", check_same_thread=False)
        self.cur = self.db.cursor()
        
        self.createMainTable()
    
    def checkIfItExists(self, name: str, table: str = "__main__") -> bool:
        if self.file != "diaries.db" and table == "__main__":
            return self.checkIfTheParentExists(name)
            
        else:
            return self.checkIfTheChildExists(name, table)
        
    def checkIfTheChildExists(self, name: str, table: str = "__main__") -> bool:
        if table != "__main__":
            if not self.checkIfTheTableExists(table):
                return False
        
        self.cur.execute(f"select * from '{table}' where name = ?", (name,))
        
        try:
            self.cur.fetchone()[0]
            return True
        
        except TypeError:
            return False
        
    def checkIfTheParentExists(self, name: str) -> bool:
        self.cur.execute(f"select * from __main__ where name = ?", (name,))
        
        try:
            self.cur.fetchone()[0]
            return self.checkIfTheTableExists(name)
            
        except TypeError:
            return False
        
    def checkIfTheTableExists(self, table: str = "__main__") -> bool:
        try:
            self.cur.execute(f"select * from '{table}'")
            return True
        
        except sqlite3.OperationalError:
            return False
        
    def createChild(self, sql: str, values: tuple[str], name: str, table: str = "__main__", date: str | None = None) -> bool:
        if not self.checkIfTheChildExists(name, table):
            self.cur.execute(sql, values)
            self.db.commit()
        
            if self.checkIfTheChildExists(name, table):
                if table != "__main__":
                    return self.updateModification(table, "__main__", date)
                
                else:
                    return True
            
            else:
                return False

        else:
            return True
        
    def createMainTable(self, sql: str) -> bool:
        self.cur.execute(sql)
        self.db.commit()
        
        check = self.checkIfTheTableExists()
        
        if not check:
            print(f"[2] Failed to create main table for {self.file}")
            exit(2)
            
        return check
    
    def delete(self, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"delete from '{table}' where name = ?", (name,))
        self.db.commit()
        
        if self.file == "diaries.db" and table == "__main__":
            self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
            self.db.commit()
        
        if not self.checkIfItExists(name, table):
            if table != "__main__":
                return self.updateModification(table, "__main__")
            
            else:
                return True
        
        else:
            return False
        
    def getAll(self) -> dict:
        pass
        
    def getColumn(self, default: str, column: str, name: str, table: str = "__main__") -> str:
        self.cur.execute(f"select {column} from '{table}' where name = ?", (name,))
        
        try:
            fetch = self.cur.fetchone()[0]
            
        except TypeError:
            fetch = default
        
        return fetch
    
    def getData(self, column: str, name: str, table: str = "__main__") -> str:
        return self.getColumn("", column, name, table)
    
    def getSetting(self, column: str, name: str, table: str = "__main__") -> str:
        return self.getColumn("global", column, name, table)
    
    def rename(self, newname: str, name: str, table: str = "__main__") -> bool:  
        self.cur.execute(f"update '{table}' set name = ? where name = ?", (newname, name))
        self.db.commit()
        
        if self.file != "diaries.db" and table == "__main__":
            self.cur.execute(f"ALTER TABLE '{name}' RENAME TO '{newname}'")
            self.db.commit()
        
        if self.checkIfItExists(newname, table):
            if table != "__main__":
                return self.updateModification(table, "__main__")
            
            else:
                return True
        
        else:
            return False
    
    def setColumn(self, default: str, value: str, column: str, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"update '{table}' set {column} = ? where name = ?", (value, name))
        self.db.commit()
        
        return self.getColumn(default, column, name, table) == value
    
    def setData(self, value: str, column: str, name: str, table: str = "__main__") -> bool:
        return self.setColumn("", value, column, name, table)
    
    def setSetting(self, value: str, column: str, name: str, table: str = "__main__") -> bool:
        return self.setColumn("global", value, column, name, table)
    
    def updateModification(self, name: str, table: str = "__main__", date: str | None = None) -> bool:
        if date is None:
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        return self.setData(date, "modification", name, table)