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
import json
import os
import shutil
import sqlite3

from .consts import ITEM_DATAS, USER_DATABASES_DIR, USER_NOTTODBOX_DIR


def checkVersion(ver1: list, ver2: list) -> bool:
    return bool(
        ver1[0] > ver2[0]
        or ver1[0] == ver2[0]
        and ver1[1] > ver2[1]
        or ver1[0] == ver2[0]
        and ver1[1] == ver2[1]
        and ver1[2] > ver2[2]
        or ver1 == ver2
    )


class MainDB:
    items = {}

    def __init__(self) -> None:
        self.db = sqlite3.connect(f"{USER_DATABASES_DIR}/main.db", check_same_thread=False)
        self.cur = self.db.cursor()

        self.createTable("__main__")

    def addBackup(self, content: str, document: str, notebook: str) -> bool:
        if self.getLocked(document, notebook) != "enabled" or (
            self.getLocked(document, notebook) == "enabled"
            and datetime.datetime.strptime(self.get("creation", document, notebook), "%d.%m.%Y %H:%M:%S").date()
            == datetime.datetime.today().date()
        ):
            if self.getBackups(document, notebook) is not None and self.getBackups(document, notebook) != "":
                backups = json.loads(self.getBackups(document, notebook))
            else:
                backups = {}
            backups[datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")] = content

            self.cur.execute(f"UPDATE '{notebook}' SET backup = ? WHERE name = ?", (json.dumps(backups), document))
            self.db.commit()

            return json.loads(self.getBackups(document, notebook)) == backups

        return True

    def checkIfItExists(self, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"SELECT * FROM '{table}' WHERE name = ?", (name,))

        try:
            self.cur.fetchone()[0]

            if table == "__main__":
                return self.checkIfTheTableExists(name)

            else:
                return self.checkIfItExists(table)

        except TypeError:
            return False

    def checkIfTheBackupExists(self, date: str, document: str, notebook: str) -> bool:
        return date in json.loads(self.getBackups(document, notebook))

    def checkIfTheTableExists(self, name: str = "__main__") -> bool:
        try:
            self.cur.execute(f"SELECT * FROM '{name}'")
            return True

        except sqlite3.OperationalError:
            return False

    def clearContent(self, document: str, notebook: str) -> bool:
        content = self.getContent(document, notebook)

        self.cur.execute(f"UPDATE '{notebook}' SET content = '' WHERE name = ?", (document,))
        self.db.commit()

        if self.getContent(document, notebook) == "" and self.updateModification(document, notebook):
            return self.addBackup(content, document, notebook)

        return False

    def create(
        self, default: str, name: str, table: str = "__main__", date: str | None = None, content: str = ""
    ) -> bool:
        if date is None:
            date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        self.cur.execute(
            f"""
            INSERT INTO '{table}'
            (name, content, creation, modification, completed, locked, autosave, format, sync, folder, pinned, bg_normal, bg_hover, bg_clicked, fg_normal, fg_hover, fg_clicked, bd_normal, bd_hover, bd_clicked)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                content,
                date,
                date,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
                default,
            ),
        )
        self.db.commit()

        return self.checkIfItExists(name, table)

    def createDocument(self, default: str, locked: str, document: str, notebook: str) -> bool:
        date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        if (
            self.create(default, document, notebook, date)
            and self.checkIfItExists(document, notebook)
            and self.set(locked, "locked", document, notebook)
        ):
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
            """
        )
        self.db.commit()

        if name == "__main__" and not self.checkIfTheTableExists(name):
            print("[2] Failed to create main table for main.db")
            exit(2)

        return True

    def createNotebook(self, default: str, locked: str, description: str, name: str) -> bool:
        return (
            self.createTable(name)
            & self.create(default, name, "__main__", None, description)
            & self.set(locked, "locked", name)
        )

    def delete(self, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"DELETE FROM '{table}' WHERE name = ?", (name,))
        self.db.commit()

        if table == "__main__":
            self.cur.execute(f"DROP TABLE IF EXISTS '{name}'")
            self.db.commit()

        if not self.checkIfItExists(name, table):
            if table != "__main__":
                return self.updateModification(table, "__main__")

            else:
                return True

        return False

    def deleteBackup(self, date: str, document: str, notebook: str) -> bool:
        if self.checkIfTheBackupExists(date, document, notebook):
            backups = json.loads(self.getBackups(document, notebook))
            del backups[date]

            return self.set(json.dumps(backups), "backup", document, notebook)

        else:
            return True

    def get(self, column: str, name: str, table: str = "__main__") -> str:
        self.cur.execute(f"SELECT {column} FROM '{table}' WHERE NAME = ?", (name,))

        try:
            fetch = self.cur.fetchone()[0]

        except TypeError:
            fetch = ""

        return fetch

    def getAll(self) -> list:
        items = []

        self.cur.execute("SELECT * FROM __main__")

        for data in self.cur.fetchall():
            self.cur.execute(f"SELECT * FROM '{data[len(data) - 5]}'")

            data = list(data)
            data.insert(0, self.cur.fetchall())

            items.append(data)

        return items

    def getBackups(self, document: str, notebook: str) -> str:
        return self.get("backup", document, notebook)

    def getContent(self, document: str, notebook: str) -> str:
        return self.get("content", document, notebook)

    def getDocument(self, document: str, notebook: str) -> list:
        self.cur.execute(f"SELECT * FROM '{notebook}' WHERE name = ?", (document,))
        return self.cur.fetchone()

    def getLocked(self, document: str, notebook: str) -> bool:
        return self.get("locked", document, notebook) == 0

    def getNotebook(self, name: str) -> list:
        self.cur.execute("SELECT * FROM __main__ WHERE name = ?", (name,))
        data = list(self.cur.fetchall()[0])

        self.cur.execute(f"SELECT * FROM '{name}'")
        data.insert(0, self.cur.fetchall())

        return data

    def rename(self, locked: str, new_name: str, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"UPDATE '{table}' SET locked = ?, name = ? WHERE name = ?", (locked, new_name, name))
        self.db.commit()

        if table == "__main__":
            self.cur.execute(f"ALTER TABLE '{name}' RENAME TO '{new_name}'")
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

    def restoreContent(self, date: str, document: str, notebook: str) -> bool:
        if self.checkIfTheBackupExists(date, document, notebook):
            self.cur.execute(f"SELECT content, backup from '{notebook}' WHERE name = ?", (document,))
            content, backups = self.cur.fetchone()
            backup = json.loads(backups)[date]

            self.cur.execute(f"UPDATE '{notebook}' SET content = ? WHERE name = ?", (backup, document))
            self.db.commit()

            if self.getContent(document, notebook) == backup and self.updateModification(document, notebook):
                return self.addBackup(content, document, notebook)

        return False

    def saveDocument(self, content: str, backup: str, autosave: bool, document: str, notebook: str) -> bool:
        self.cur.execute(f"UPDATE '{notebook}' SET content = ? WHERE name = ?", (content, document))
        self.db.commit()

        if self.getContent(document, notebook) == content and self.updateModification(document, notebook):
            if autosave:
                return True

            else:
                return self.addBackup(backup, document, notebook)

        return False

    def set(self, value: str | None, column: str, name: str, table: str = "__main__") -> bool:
        self.cur.execute(f"UPDATE '{table}' SET {column} = ? WHERE name = ?", (value, name))
        self.db.commit()

        return self.get(column, name, table) == value

    def updateDatabase(self) -> None:
        update = False

        target_version = [int(i) for i in "v0.2.0"[1:].split(".")]

        if os.path.isfile(os.path.join(USER_NOTTODBOX_DIR, "version_old")):
            with open(os.path.join(USER_NOTTODBOX_DIR, "version_old")) as f:
                app_old_version = [int(i) for i in f.read()[1:].split(".")]

                update = not checkVersion(app_old_version, target_version)

        else:
            update = True

        if update:
            shutil.copy2(
                f"{USER_DATABASES_DIR}/main.db",
                f"{USER_DATABASES_DIR}/main.db-{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')}.bak",
            )

            self.cur.execute("UPDATE __main__ SET creation = REPLACE(creation, ?, ?)", ("/", "."))
            self.db.commit()

            self.cur.execute(
                "UPDATE __main__ SET creation = creation || ? WHERE creation LIKE ?", (":00", "__.__.____ __:__")
            )
            self.db.commit()

            self.cur.execute("UPDATE __main__ SET modification = REPLACE(modification, ?, ?)", ("/", "."))
            self.db.commit()

            self.cur.execute(
                "UPDATE __main__ SET modification = modification || ? WHERE modification LIKE ?",
                (":00", "__.__.____ __:__"),
            )
            self.db.commit()

            self.cur.execute(
                "UPDATE __main__ SET sync = sync || ? WHERE sync is NOT NULL AND sync != ? AND sync != ? AND sync != ? AND sync NOT LIKE ? AND sync NOT LIKE ? AND sync NOT LIKE ?",
                ("_export", "", "default", "global", "%_all", "%_export", "%_import"),
            )
            self.db.commit()

            self.cur.execute("SELECT name FROM __main__")

            for table in [fetch[0] for fetch in self.cur.fetchall()]:
                try:
                    datetime.datetime.strptime(table, "%d/%m/%Y")
                    self.cur.execute("UPDATE __main__ SET name = REPLACE(name, ?, ?) WHERE name = ?", ("/", ".", table))
                    self.db.commit()

                except ValueError:
                    pass

                self.cur.execute(f"update '{table}' SET creation = REPLACE(creation, ?, ?)", ("/", "."))
                self.db.commit()

                self.cur.execute(
                    f"UPDATE '{table}' SET creation = creation || ? WHERE creation LIKE ?", (":00", "__.__.____ __:__")
                )
                self.db.commit()

                self.cur.execute(f"update '{table}' SET modification = REPLACE(modification, ?, ?)", ("/", "."))
                self.db.commit()

                self.cur.execute(
                    f"UPDATE '{table}' SET modification = modification || ? WHERE modification LIKE ?",
                    (":00", "__.__.____ __:__"),
                )
                self.db.commit()

                self.cur.execute(
                    f"UPDATE '{table}' SET sync = sync || ? WHERE sync is NOT NULL AND sync != ? AND sync != ? AND sync != ? AND sync != ? AND sync NOT LIKE ? AND sync NOT LIKE ? AND sync NOT LIKE ?",
                    ("_export", "", "default", "global", "notebook", "%_all", "%_export", "%_import"),
                )
                self.db.commit()

                self.cur.execute(f"SELECT name FROM '{table}'")
                for name in [fetch[0] for fetch in self.cur.fetchall()]:
                    try:
                        datetime.datetime.strptime(name, "%d/%m/%Y")
                        self.cur.execute(
                            f"UPDATE '{table}' SET name = REPLACE(name, ?, ?) WHERE name = ?", ("/", ".", name)
                        )
                        self.db.commit()

                    except ValueError:
                        pass

                    if self.get("backup", name, table) is not None and self.get("backup", name, table) != "":
                        try:
                            if "2025" not in json.loads(self.get("backup", name, table)):
                                self.cur.execute(
                                    f"UPDATE '{table}' SET backup = ? WHERE name = ?",
                                    (json.dumps({"2025": self.get("backup", name, table)}), name),
                                )
                                self.db.commit()

                        except (json.JSONDecodeError, TypeError):
                            self.cur.execute(
                                f"UPDATE '{table}' SET backup = ? WHERE name = ?",
                                (json.dumps({"2025": self.get("backup", name, table)}), name),
                            )
                            self.db.commit()

    def updateModification(self, name: str, table: str = "__main__", date: str | None = None) -> bool:
        if date is None:
            date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        successful = True

        if table != "__main__":
            successful = self.set(date, "modification", table)
            self.items[(table, "__main__")].setData(date, ITEM_DATAS["modification"])

        successful = self.set(date, "modification", name, table) & successful

        self.items[(name, table)].setData(date, ITEM_DATAS["modification"])

        return successful
