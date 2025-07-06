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


import logging
import os
import platform
import subprocess
import sys
from datetime import datetime
from PySide6.QtCore import QFile, QLocale, QTranslator, qVersion
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
from .consts import APP_BUILD, APP_VERSION, USER_DIRS, USER_LOGS_DIR
from .mainwindow import MainWindow
from .resources import icons, locale  # noqa: F401


class Application(QApplication):
    def __init__(self, argv: list) -> None:
        super().__init__(argv)
        
        logging.info(f"Nottodbox v{APP_VERSION} (build: {APP_BUILD}) (pid: {os.getpid()})")
        logging.info(f"Operating system: {platform.system()} {platform.release()} ({platform.platform()})")
        logging.info(f"Platform: {QApplication.platformName()}")
        logging.info(f"Python: {platform.python_version()}")
        logging.info(f"Qt: {qVersion()}")
        logging.info(f"Language: {QLocale.system().name()} / {QLocale.system().name().split("_")[0]}")

        self.setApplicationVersion(APP_VERSION)
        self.setApplicationName("nottodbox")
        self.setApplicationDisplayName("Nottodbox")
        self.setDesktopFileName("io.github.mukonqi.nottodbox")
        self.setWindowIcon(QPixmap(":/icons/window"))

        translator = QTranslator(self)
        if translator.load(f":/locale/{QLocale.system().name()}.qm"):
            self.installTranslator(translator)
        else:
            logging.warning(f"Failed to load locale for {QLocale.system().name()}.")
            
            translator = QTranslator(self)
            if translator.load(f":/locale/{QLocale.system().name().split("_")[0]}.qm"):
                self.installTranslator(translator)
            else:
                logging.warning(f"Failed to load locale for {QLocale.system().name().split("_")[0]}.")
            
        if APP_BUILD == "Flatpak":
            for dir in USER_DIRS.values():
                dir = os.path.join(dir, "Nottodbox")
                
                if os.path.isdir(dir):
                    with os.scandir(dir) as entry:
                        if not any(entry):
                            subprocess.run(['flatpak-spawn', '--host', 'rm', '-r', dir])

        self.mainwindow = MainWindow()
        
        
class StreamToLogger:
    def __init__(self, logger, log_level=logging.INFO) -> None:
        self.logger = logger
        self.log_level = log_level

    def write(self, message) -> None:
        message = message.strip()
        if message:
            self.logger.log(self.log_level, message)

    def flush(self):
        pass


def main() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', "%Y-%m-%d %H-%M-%S")

    file_handler = logging.FileHandler(os.path.join(USER_LOGS_DIR, f"{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log"), encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)
    
    application = Application(sys.argv)
    sys.exit(application.exec())