# Nottodbox (pre-alpha)

<p align="center"><img src="./data/io.github.mukonqi.nottodbox.svg" alt="Nottodbox Icon"></img></a></p>
<p align="center"><img src="https://img.shields.io/badge/Edit notes, todo lists and diaries-376296" alt="Edit notes, todo lists and diaries"></img></p>
<p align="center"><img src="https://img.shields.io/github/downloads/mukonqi/nottodbox/total?label=Downloads" alt="GitHub Downloads"></img></p>
<p align="center"><img src="https://img.shields.io/github/v/release/mukonqi/nottodbox?label=Latest Release" alt="GitHub Release"></p>


## Features
### Sidebar
- A entry for searching in lists
- A list for showing currently open pages (when double-clicked it opens or focuses selected)
- A list for last opened pages (when double-clicked it opens or focuses selected)
- Deleting item from 2nd list
- Clearing 2nd list

### Home
- A shortcut for keeping today's diary
- Listing todo lists & todos with creation (for both), modification (only todo lists), status (only todo), completion (only todo) informations
- Listing notebooks & notes with creation and modification informations (all of them are for both)

### Notes
- A entry for searching in list
- Two labels for showing selected notebook and note
- Listing notebooks & notes with creation and modification informations (all of them are for both)
- For notebooks:
    - Creating a notebook
    - Renaming a notebook
    - Resetting a notebook
    - Setting background
    - Setting foreground
    - Deleting a notebook
    - Deleting all notebooks
- For notes:
    - Creating a note
    - Opening a note
    - Renaming a note
    - Showing backup (manuel saves updates backups but auto-saves not)
    - Restoring content via backup (old content will be new backup)
    - Clearing content (old content will be new backup)
    - Deleting a note
- Setting auto-save and format settings (plain-text, Markdown or HTML) for global or each note (they can follow global setting)

### Todos
- A entry for searcing in list
- Two labels for showing selected notebook and note
- Listing todo lists & todos with creation (for both), modification (only todo lists), status (only todo), completion (only todo) informations
- For todo lists:
    - Creating a todo list
    - Renaming a todo list
    - Resetting a todo list
    - Setting background
    - Setting foreground
    - Deleting a todo list
    - Deleting all todo lists
- For todos:
    - Creating a todo
    - Changing status
    - Editing a todo
    - Deleting a todo

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
- Setting auto-save and format settings (plain-text, Markdown or HTML) for global or each diary (they can follow global setting)

### Note and diary pages
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
        - Alignment (only for HTML format) (3 options)
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
- Python modules: sys, locale, gettext, getpass, os, sqlite3, datetime, PyQt6 (they are generally built-in except PyQt6)
- git version control system (for downloading this repository)
- meson build system
- ninja build system

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
While making [nottodbox/widgets/pages.py](./nottodbox/widgets/pages.py)'s TextFormatter class, [KDE - Marknote: master/src/documenthandler.cpp](https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp) helped me.
