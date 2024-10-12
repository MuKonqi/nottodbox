# Nottodbox (pre-alpha)

<p align="center"><img src="./data/io.github.mukonqi.nottodbox.svg" alt="Nottodbox Icon"></img></a></p>
<p align="center"><img src="https://img.shields.io/badge/Edit notes, to-do lists and diaries-376296" alt="Edit notes, to-do lists and diaries"></img></p>
<p align="center"><img src="https://img.shields.io/github/downloads/mukonqi/nottodbox/total?label=Downloads" alt="GitHub Downloads"></img></p>
<p align="center"><img src="https://img.shields.io/github/v/release/mukonqi/nottodbox?label=Latest Release" alt="GitHub Release"></p>


## Features
### Sidebar
- A entry for searching in lists
- A list for showing currently open pages (when double-clicked it opens or focuses selected)
- A list for last opened pages (when double-clicked it opens or focuses selected)
- Deleting item from 2nd list
- Clearing 2nd list
- Remember's it's status (visible / invisible), area in window (left / right), mode (fixed / floating)

### Home
- A shortcut for keeping today's diary
- Listing to-do lists & to-dos with creation (for both), modification (only to-do lists), status (only to-do), completion (only to-do) informations
- Listing notebooks & notes with creation and modification informations (all of them are for both)

### Notes
- Two labels for showing selected notebook and note
- A entry for searching in list
- Listing notebooks & notes with creation and modification informations (all of them are for both)
- For notebooks:
    - Creating a notebook
    - Setting background color
    - Setting text color
    - Renaming a notebook
    - Resetting a notebook
    - Deleting a notebook
    - Deleting all notebooks
- For notes:
    - Creating a note
    - Opening a note
    - Setting background color
    - Setting text color
    - Renaming a note
    - Showing backup (manuel saves updates backups but auto-saves not)
    - Restoring content via backup (old content will be new backup)
    - Clearing content (old content will be new backup)
    - Deleting a note

### To-dos
- A entry for searcing in list
- Two labels for showing selected notebook and note
- Listing to-do lists & to-dos with creation (for both), modification (only to-do lists), status (only to-do), completion (only to-do) informations
- For to-do lists:
    - Creating a to-do list
    - Setting background color
    - Setting text color
    - Renaming a to-do list
    - Resetting a to-do list
    - Deleting a to-do list
    - Deleting all to-do lists
- For to-dos:
    - Creating a to-do
    - Changing status
    - Editing a to-do
    - Deleting a to-do

### Diaries
- A label for showing modification information
- A calendar for selecting diaries
- A shortcut for coming back to today
- Refreshing today variable
- Opening a diary, if does not keeped yet create a it
- Showing backup (manuel saves updates backups but auto-saves not)
- Restoring content via backup (old content will be new backup)
- Clearing content (old content will be new backup)
- Deleting a diary

### Note and Diary's Pages
- Text formatter (plain-text format does not supported):
    - Formatting selected section via cursor
    - Formatting word under cursor
    - Format options:
        - Bold
        - Italic
        - Underline
        - Strike through
        - Fixed spacing
        - Heading (6 levels)
        - List (4 options)
        - Alignment (3 options) (only for HTML format)
        - Table
        - Link
        - Text color (only for HTML format)
        - Background color (only for HTML format)
- Standart Qt's text edit box
- Manuel saving
- Options for setting auto-save and format settings


## Building
### Dependencies
- Python3
- Python modules: sys, locale, gettext, getpass, os, sqlite3, datetime, webbrowser, PySide6 (they are generally built-in except PySide6)
- Qt
- git
- meson
- ninja

### Commands
- Note: Do not forget to install dependencies.
```
    git clone https://github.com/mukonqi/nottodbox.git
    cd nottodbox
    meson setup . builddir
    ninja -C builddir
    ninja -C builddir install
```


## Installing
TBA


## Disclaimer
> Nottodbox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

- You can see the license for more details.

## Credit
While making [nottodbox/widgets/pages.py](./nottodbox/widgets/pages.py)'s TextFormatter class, [KDE - Marknote: master/src/documenthandler.cpp](https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp) helped me as a referance.
