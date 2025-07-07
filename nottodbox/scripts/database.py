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


import datetime
import sqlite3

from PySide6.QtCore import Qt

from .consts import USER_DATABASES_DIR


class MainDB:
    items = {}

    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{USER_DATABASES_DIR}/main.db", check_same_thread=False)
        self.cur = self.db.cursor()

        self.createTable("__main__")

    def checkIfItExists(self, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"select * from '{table}' where name = ?", (name,))

        try:
            self.cur.fetchone()[0]

            if table == "__main__":
                return self.checkIfTheTableExists(name)

            else:
                return self.checkIfItExists(table)

        except TypeError:
            return False

    def checkIfTheTableExists(self, name: str = "__main__") -> bool:
        try:
            self.cur.execute(f"select * from '{name}'")
            return True

        except sqlite3.OperationalError:
            return False

    def clearContent(self, document: str, notebook: str) -> bool:
        content = self.getContent(document, notebook)

        self.cur.execute(f"update '{notebook}' set content = '' where name = ?", (document,))
        self.db.commit()

        if self.getContent(document, notebook) == "" and self.updateModification(document, notebook):
            return self.setBackup(content, document, notebook)

        return False

    def create(self, default: str, name: str, table: str = "__main__", date: str | None = None, content: str = "") -> bool:
        if date is None:
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        self.cur.execute(
            f"""
            INSERT INTO '{table}'
            (name, content, creation, modification, completed, locked, autosave, format, sync, folder, pinned, bg_normal, bg_hover, bg_clicked, fg_normal, fg_hover, fg_clicked, bd_normal, bd_hover, bd_clicked)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, content, date, date, default, default, default, default, default, default, default, default, default, default, default, default, default, default, default, default)
        )
        self.db.commit()

        return self.checkIfItExists(name, table)

    def createDocument(self, default: str, locked: str, document: str, notebook: str) -> bool:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        if self.create(default, document, notebook, date) and self.checkIfItExists(document, notebook) and self.set(locked, "locked", document, notebook):
            return self.updateModification(notebook, "__main__", date)

        return False

    def createTable(self, name: str = "__main__") -> bool:
        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS '{name}' (
                id INTEGER PRIMARY KEY,
                completed TEXT,
                locked TEXT NOT NULL,
                autosave TEXT NOT NULL,
                format TEXT NOT NULL,
                sync TEXT,
                folder TEXT NOT NULL,
                pinned TEXT NOT NULL,
                bg_normal TEXT NOT NULL,
                bg_hover TEXT NOT NULL,
                bg_clicked TEXT NOT NULL,
                fg_normal TEXT NOT NULL,
                fg_hover TEXT NOT NULL,
                fg_clicked TEXT NOT NULL,
                bd_normal TEXT NOT NULL,
                bd_hover TEXT NOT NULL,
                bd_clicked TEXT NOT NULL,
                name TEXT NOT NULL UNIQUE,
                creation TEXT NOT NULL,
                modification TEXT NOT NULL,
                content TEXT,
                backup TEXT
            );
            """)
        self.db.commit()

        if name == "__main__" and not self.checkIfTheTableExists(name):
            print("[2] Failed to create main table for main.db")
            exit(2)

        return True

    def createNotebook(self, default: str, locked: str, description: str, name: str) -> bool:
        return self.createTable(name) & self.create(default, name, "__main__", None, description) & self.set(locked, "locked", name)

    def delete(self, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"delete from '{table}' where name = ?", (name,))
        self.db.commit()

        if table == "__main__":
            self.cur.execute(f"drop table if exists '{name}'")
            self.db.commit()

        if not self.checkIfItExists(name, table):
            if table != "__main__":
                return self.updateModification(table, "__main__")

            else:
                return True

        return False

    def get(self, column: str, name: str, table: str = "__main__") -> str:
        self.cur.execute(f"select {column} from '{table}' where name = ?", (name,))

        try:
            fetch = self.cur.fetchone()[0]

        except TypeError:
            fetch = ""

        return fetch

    def getAll(self) -> list:
        items = []

        self.cur.execute("select * from __main__")

        for data in self.cur.fetchall():
            self.cur.execute(f"select * from '{data[len(data) - 5]}'")

            data = list(data)
            data.insert(0, self.cur.fetchall())

            items.append(data)

        return items

    def getBackup(self, document: str, notebook: str) -> str:
        return self.get("backup", document, notebook)

    def getContent(self, document: str, notebook: str) -> str:
        return self.get("content", document, notebook)

    def getDocument(self, document: str, notebook: str) -> list:
        self.cur.execute(f"select * from '{notebook}' where name = ?", (document,))
        return self.cur.fetchone()

    def getLocked(self, document: str, notebook: str) -> bool:
        return self.get("locked", document, notebook) == 0

    def getNotebook(self, name: str) -> list:
        self.cur.execute("select * from __main__ where name = ?", (name,))
        data = list(self.cur.fetchall()[0])

        self.cur.execute(f"select * from '{name}'")
        data.insert(0, self.cur.fetchall())

        return data

    def rename(self, locked: str, new_name: str, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"update '{table}' set locked = ?, name = ? where name = ?", (locked, new_name, name))
        self.db.commit()

        if table == "__main__":
            self.cur.execute(f"alter table '{name}' rename to '{new_name}'")
            self.db.commit()

        if self.checkIfItExists(new_name, table):
            if table != "__main__":
                return self.updateModification(table, "__main__")

            else:
                return True

        return False

    def reset(self, name: str) -> bool:
        self.cur.execute(f"delete from '{name}'")
        self.db.commit()

        return self.getNotebook(name)[0] == []

    def restoreContent(self, document: str, notebook: str) -> bool:
        self.cur.execute(f"select content, backup from '{notebook}' where name = ?", (document,))
        content, backup = self.cur.fetchone()

        self.cur.execute(f"update '{notebook}' set content = ? where name = ?", (backup, document))
        self.db.commit()

        if self.getContent(document, notebook) == backup and self.updateModification(document, notebook):
            return self.setBackup(content, document, notebook)

        return False

    def saveDocument(self, content: str, backup: str, autosave: bool, document: str, notebook: str) -> bool:
        self.cur.execute(f"update '{notebook}' set content = ? where name = ?", (content, document))
        self.db.commit()

        if self.getContent(document, notebook) == content and self.updateModification(document, notebook):
            if autosave:
                return True

            else:
                return self.setBackup(backup, document, notebook)

        return False

    def set(self, value: str | None, column: str, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"update '{table}' set {column} = ? where name = ?", (value, name))
        self.db.commit()

        return self.get(column, name, table) == value

    def setBackup(self, content: str, document: str, notebook: str) -> bool:
        if self.getLocked(document, notebook) != "enabled" or (self.getLocked(document, notebook) == "enabled" and datetime.datetime.strptime(self.get("creation", document, notebook), "%d/%m/%Y %H:%M").date() == datetime.datetime.today().date()):
            self.cur.execute(f"update '{notebook}' set backup = ? where name = ?", (content, document))
            self.db.commit()

            return self.getBackup(document, notebook) == content

        else:
            return True

    def updateModification(self, name: str, table: str = "__main__", date: str | None = None) -> bool:
        if date is None:
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        successful = True

        if table != "__main__":
            successful = self.set(date, "modification", table)
            self.items[(table, "__main__")].setData(date, Qt.ItemDataRole.UserRole + 103)

        successful = self.set(date, "modification", name, table) & successful

        self.items[(name, table)].setData(date, Qt.ItemDataRole.UserRole + 103)

        return successful
