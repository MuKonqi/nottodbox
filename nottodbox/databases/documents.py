# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024-2025MuKonqi (Muhammed S.)

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
from .base import DBBase


username = getpass.getuser()
userdata = f"/home/{username}/.config/io.github.mukonqi/nottodbox/"


class DBForDocuments(DBBase):        
    def checkIfTheChildBackupExists(self, name: str, table: str = "__main__") -> bool:
        if self.checkIfTheChildExists(name, table):
            self.cur.execute(f"select backup from '{table}' where name = ?", (name,))
            fetch = self.cur.fetchone()[0]
            
            if fetch == None or fetch == "":
                return False
            
            else:
                return True
            
        else:
            return False
        
    def clearContent(self, name: str, table: str = "__main__") -> bool:
        content = self.getContent(name, table)
            
        self.cur.execute(f"update '{table}' set content = '' where name = ?", (name,))
        self.db.commit()
        
        if self.getContent(name, table) == "":
            if self.updateModification(name, table):
                return self.setBackup(content, name, table)
            
            else:
                return False
            
        else:
            return False
    
    def getAutosave(self, name: str, table: str = "__main__") -> str:
        return super().getSetting("autosave", name, table)
    
    def getBackup(self, name: str, table: str = "__main__") -> str:
        return super().getData("backup", name, table)
    
    def getContent(self, name: str, table: str = "__main__") -> str:
        return super().getData("content", name, table)
    
    def getFormat(self, name: str, table: str = "__main__") -> str:
        return super().getSetting("format", name, table)
    
    def getNewContent(self, default_format: str, page, name: str, table: str = "__main__") -> str:
        format = self.getFormat(name, table)
            
        if format == "global":
            format = default_format
        
        if format == "plain-text":
            return page.input.toPlainText()
            
        elif format == "markdown":
            return page.input.toMarkdown()
            
        elif format == "html":
            return page.input.toHtml()
    
    def restoreContent(self, name: str, table: str = "__main__") -> tuple[bool, str]:
        self.cur.execute(f"select content, backup from '{table}' where name = ?", (name,))
        content, backup = self.cur.fetchone()
        
        self.cur.execute(f"update '{table}' set content = ? where name = ?", (backup, name))
        self.db.commit()
        
        if self.getContent(name, table) == backup:
            return self.updateModification(name, table), content
        
        else:
            return False, content
        
    def saveAll(self, default_format: str, pages: dict) -> bool:
        successful = True
        calls = {}
        
        for name, table in pages:
            format = self.getFormat(name, table)
                
            if format == "global":
                format = default_format
            
            if format == "plain-text":
                text = pages[(name, table)].input.toPlainText()
                
            elif format == "markdown":
                text = pages[(name, table)].input.toMarkdown()
                
            elif format == "html":
                text = pages[(name, table)].input.toHtml()
            
            calls[(name, table)] = self.saveChild(text, 
                                                  pages[(name, table)].content, 
                                                  False, 
                                                  name,
                                                  table)
            
            if not calls[(name, table)]:
                successful = False
                
        return successful
    
    def saveChild(self, content: str, backup: str, autosave: bool, name: str, table: str = "__main__") -> bool:        
        if self.checkIfTheChildExists(name, table):
            self.cur.execute(f"update '{table}' set content = ? where name = ?", (content, name))
            self.db.commit()
        
            if self.getContent(name, table) == content:
                if self.updateModification(name, table):
                    if autosave:
                        return True
                    
                    else:
                        return self.setBackup(backup, name, table)
                    
                else:
                    return False    
            
            else:
                return False
        
        else:
            return False
        
    def setAutosave(self, value: str, name: str, table: str = "__main__") -> bool:
        return super().setSetting(value, "autosave", name, table)
    
    def setBackup(self, content: str, name: str, table: str = "__main__") -> bool:
        pass
    
    def setFormat(self, value: str, name: str, table: str = "__main__") -> bool:
        return super().setSetting(value, "format", name, table)