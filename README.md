# Nottodbox (pre-alpha)

<p align="center"><img src="./data/io.github.mukonqi.nottodbox.svg" alt="Nottodbox Icon"></img></a></p>
<p align="center"><img src="https://img.shields.io/badge/Edit notes, todo lists and diaries-376296" alt="Edit notes, todo lists and diaries"></img></p>
<p align="center"><img src="https://img.shields.io/github/downloads/mukonqi/nottodbox/total?label=Downloads" alt="GitHub Downloads"></img></p>
<p align="center"><img src="https://img.shields.io/github/v/release/mukonqi/nottodbox?label=Latest Release" alt="GitHub Release"></p>


## Features
TBA


## Building
### Dependencies
- Python3
- Python modules: sys, locale, gettext, getpass, os, sqlite3, datetime, PyQt6 (they are generally built-in except PyQt6)
- git version control system (for downloading this repository)
- meson build system
- ninja build system

### Commands
- Note: Do not forget to install dependencies.
```
    git clone https://github.com/mukonqi/nottodbox.git
    meson setup . builddir
    ninja -C builddir
    ninja -C builddir install
```


## Installing
TBA


## Contributing
### For devoloping
TBA

### For translating
TBA


## Disclaimer
Nottodbox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 

without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

- Note: You can see the license for more details.

## Credit
While making [nottodbox/widgets/pages.py](./nottodbox/widgets/pages.py)'s TextFormatter class, [KDE - Marknote: master/src/documenthandler.cpp](https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp) helped me.