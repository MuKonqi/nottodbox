# Nottodbox (pre-alpha)

<p align="center"><img src="./data/io.github.mukonqi.nottodbox.svg" alt="Nottodbox Icon"></img></a></p>
<p align="center"><img src="https://img.shields.io/badge/Edit_notes,_to--dos_and_diaries-376296" alt="Edit notes, to-dos and diaries"></img></p>
<p align="center"><img src="https://img.shields.io/github/downloads/mukonqi/nottodbox/total?label=Downloads" alt="Count of Downloads"></img></p>
<p align="center"><img src="https://img.shields.io/github/v/release/mukonqi/nottodbox?label=Latest Release" alt="Latest Release"></p>


## Features
### Sidebar
- A entry for searching in lists
- A list for open pages (when double-clicked it opens or focuses selected)
- A list for history (when double-clicked it opens or focuses selected)
- Deleting item from history
- Clearing item from history
- Remember's it's status (visible / invisible), area in window (left / right), mode (fixed / floating)

### Home
- A shortcut for keeping today's diary and focusing to it (optional)
- Listing to-dos
- Listing notes

### Notes
- Two labels for showing selected notebook and note
- A entry for searching in list
- Listing notes
- For a notebooks:
    - Creating
    - Setting background color
    - Setting text color
    - Renaming
    - Resetting 
    - Deleting
    - Deleting all
- For a note:
    - Creating
    - Opening
    - Setting background color
    - Setting text color
    - Renaming
    - Showing backup (manuel saves updates backups but auto-saves not)
    - Restoring content via backup (old content will be new backup)
    - Clearing content (old content will be new backup)
    - Deleting

### To-dos
- A entry for searcing in list
- Two labels for showing selected notebook and note
- Listing to-dos
- For a to-do list:
    - Creating
    - Setting background color
    - Setting text color
    - Renaming
    - Resetting
    - Deleting
    - Deleting all
- For a to-do:
    - Creating
    - Changing
    - Editing
    - Deleting

### Diaries
- A label for showing modification information
- A calendar for selecting and highlighting
- A shortcut for coming back to today
- Refreshing today variable
- Opening a diary, if does not keeped yet create a it
- Showing backup (manuel saves updates backups but auto-saves not)
- Restoring content via backup (old content will be new backup)
- Clearing content (old content will be new backup)
- Deleting

### Note and Diary Pages
- Text formatter (plain-text format does not supported):
    - Formatting selected section via cursor or word uncer cursor
    - Format options:
        - Bold
        - Italic
        - Underline
        - Strike through
        - Heading (6 levels)
        - List (4 options)
        - Alignment (3 options) (only for HTML format)
        - Table
        - Link
        - Text color (only for HTML format)
        - Background color (only for HTML format)
- Standart Qt's text edit box with opening links support
- Manuel saving
    - For triggering, user must click the "Save" button or accept the warning question when closing a document.
    - This can change backups except if old diary pages.
- Auto-saving
    - This triggered when the document content's changes.
    - This is disabled and can't be enabled for old diaries.
    - This can't change backups.
- Format options (plain-text, Markdown and HTML)


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
