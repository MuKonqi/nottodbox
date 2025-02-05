# Nottodbox

<p align="center"><img src="./data/io.github.mukonqi.nottodbox.png" alt="Icon of Nottodbox"></img></a></p>
<p align="center"><img src="https://img.shields.io/badge/Organize_notes,_to--dos_and_diaries-376296" alt="Organize notes, to-dos and diaries"></img></p>
<p align="center"><img src="https://img.shields.io/github/downloads/mukonqi/nottodbox/total?label=Downloads" alt="Downloads"></img></p>
<p align="center"><img src="https://img.shields.io/github/v/release/mukonqi/nottodbox?label=Release" alt="Release"></p>


## Features
### Sidebar
> Quickly navigate document pages.
- A entry for searching in lists
- A list for open pages (when double-clicked it opens or focuses selected)
- A list for history (when double-clicked it opens or focuses selected)
- Deleting a item from history
- Clearing history
- Remember's it's status (visible / invisible), area in window (left / right), mode (fixed / floating)

### Home
> See some important things in startup.
- A shortcut for keeping today's diary and focusing to it (optional)
- Listing to-dos
- Listing notes

### Notes
> Take notes.
- Two labels for showing selected notebook and note
- A entry for searching in list
- Listing notes
- When a notebook selected:
    - Creating notebook
    - Creating note
    - Resetting
    - Renaming
    - Resetting 
    - Deleting
    - Deleting all
    - Setting background color
    - Setting text color
- When a note selected:
    - Creating notebook
    - Creating note
    - Opening
    - Showing backup (manuel saves updates backups but auto-saves not)
    - Restoring content via backup (old content will be new backup)
    - Clearing content (old content will be new backup)
    - Renaming
    - Deleting
    - Deleting all
    - Setting background color
    - Setting text color

### To-dos
> Make to-do lists.
- A entry for searcing in list
- Two labels for showing selected notebook and note
- Listing to-dos
- When a to-do list selected:
    - Creating notebook
    - Creating note
    - Resetting
    - Renaming
    - Resetting 
    - Deleting
    - Deleting all
    - Setting background color
    - Setting text color
- When a to-do selected:
    - Creating notebook
    - Creating note
    - Changing status
    - Renaming
    - Resetting 
    - Deleting
    - Deleting all
    - Setting background color
    - Setting text color

### Diaries
> Keep diaries.
- A label for showing modification information
- A calendar for selecting a diary and highlighting it
- A shortcut for coming back to today
- When a diary selected:
    - Opening, if does not created yet create it
    - Showing backup (manuel saves updates backups but auto-saves not)
    - Restoring content via backup (old content will be new backup)
    - Clearing content (old content will be new backup)
    - Renaming
    - Deleting
    - Deleting all
    - Setting highlight color

### Documents
> Easily edit documents in a style.
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
    - For triggering, click the "Save" button or accept the warning question when closing a document.
    - This can change backups except outdated diaries.
- Auto-saving
    - This triggered when the document content's changes.
    - This is disabled and can't be enabled for old diaries.
    - This can't change backups.
- Format options (plain-text, Markdown and HTML)

### Settings
> Change global settings.
- For notes:
    - Setting auto-save
    - Setting format
    - Setting background color
    - Setting foreground color
- For todos:
    - Setting background color
    - Setting foreground color
- For diaries:
    - Setting auto-save
    - Setting format
    - Setting highlight color


### About
> See some informations about Nottodbox.
- The icon and application name
- Version
- Commit
- Link source codes
- Developer
- Copyright notification
- License
- License text


## Installing
TBA


## Building
### Dependencies
- Python3
- The following Python libraries: sys, locale, argparse, gettext, getpass, os, subprocess, sqlite3, datetime, json, PySide6 (they are generally built-in except PySide6)
- Qt
- getent
- cut
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


## Disclaimer
> Nottodbox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

- You can see the license for more details.


## Credit
While making [nottodbox/widgets/pages.py](./nottodbox/widgets/pages.py)'s TextFormatter class, [KDE - Marknote: master/src/documenthandler.cpp](https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp) helped me as a referance.
