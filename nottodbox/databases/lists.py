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


import datetime
from .advanced import DBAdvanced


class DBForLists(DBAdvanced):
    def createParent(self, sql: list[str], values: tuple[str], name: str) -> bool:
        self.cur.execute(sql[0], values)
        self.db.commit()
        
        self.cur.execute(sql[1])
        self.db.commit()
        
        return self.checkIfTheParentExists(name)
    
    def deleteAll(self) -> bool:
        successful = True
        
        self.cur.execute("select name from __main__")
        lists = self.cur.fetchall()
        
        for item in lists:
            item = item[0]
            
            if not self.delete(item):
                successful = False
        
        if successful:
            self.cur.execute("DROP TABLE IF EXISTS __main__")
            self.db.commit()
            
            if not self.checkIfTheTableExists("__main__"):
                return self.createMainTable()
            
            else:
                return False

        else:
            return False
        
    def getAll(self) -> dict:
        childs = {}
        
        self.cur.execute("select name from __main__")
            
        for table in self.cur.fetchall():
            table = table[0]
            
            childs[table] = []
            
            self.cur.execute(f"select name from '{table}'")
            
            for name in self.cur.fetchall():
                childs[table].append(name) 
                
        return childs
        
    def getBackground(self, name: str, table: str = "__main__") -> str:
        return super().getSetting("background", name, table)        
    
    def getForeground(self, name: str, table: str = "__main__") -> str:
        return super().getSetting("foreground", name, table)
    
    def getModification(self, name: str, table: str = "__main__") -> str:
        return super().getData("modification", name, table)
    
    def resetParent(self, name: str) -> bool:
        self.cur.execute("delete from __main__ where name = ?", (name,))
        self.db.commit()
        
        self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
        self.db.commit()
        
        if not self.checkIfTheParentExists(name):
            return self.createParent(name)
        
        else:
            return False
        
    def setBackground(self, value: str, name: str, table: str = "__main__") -> bool:
        return super().setSetting(value, "background", name, table)
    
    def setForeground(self, value: str, name: str, table: str = "__main__") -> bool:
        return super().setSetting(value, "foreground", name, table)
    
    def updateModification(self, name: str, table: str = "__main__", date: str | None = None) -> bool:
        if date is None:
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
        successful = True
        calls = []
        
        calls.append(super().updateModification(name, table, date))
        
        if not calls[0]:
            successful = False
        
        if table != "__main__":
            calls.append(super().updateModification(table, "__main__", date))
            
            if not calls[1]:
                successful = False
        
        return successful