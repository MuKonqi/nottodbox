# Nottodbox

<p align="center">
    <img src="./share/icons/hicolor/96x96/apps/io.github.mukonqi.nottodbox.png" alt="Icon of Nottodbox"></img><br>
    <img src="https://img.shields.io/badge/Organize_notes,_to--dos_and_diaries-376296" alt="Organize notes, to-dos and diaries"></img><br>
    <img src="https://img.shields.io/github/downloads/mukonqi/nottodbox/total?label=Downloads" alt="Downloads"></img>
    <img src="https://img.shields.io/github/v/release/mukonqi/nottodbox?label=Release" alt="Release"><br>
    <a href="https://github.com/mukonqi/nottodbox/releases/latest"><img src="https://docs.appimage.org/_images/download-appimage-banner.svg" alt="Download as an AppImage" /></a>
</p>

## Images
<details>
<summary>Show / Hide</summary>

![Home](/.github/images/home.png)<br>
![Home (Dark)](/.github/images/home-dark.png)<br>
![Notes](/.github/images/notes.png)<br>
![Todos](/.github/images/todos.png)<br>
![Diaries](/.github/images/diaries.png)<br>
![Settings](/.github/images/settings.png)

</details>


## Features
<details>
<summary>Show / Hide</summary>

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
- A welcome text
- A shortcut for keeping today's diary and focusing to it (optional)
- Listing to-dos
- Listing notes

### Notes
> Take notes.
- Two labels for showing selected notebook and note
- A entry for searching in list
- Listing notes
- When a notebook selected:
    - Creating note
    - Creating notebook
    - Resetting
    - Renaming
    - Resetting 
    - Deleting
    - Deleting all
    - Setting background color
    - Setting text color
- When a note selected:
    - Creating note
    - Creating notebook
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
    - Creating to-do
    - Creating to-do list
    - Resetting
    - Renaming
    - Resetting 
    - Deleting
    - Deleting all
    - Setting background color
    - Setting text color
- When a to-do selected:
    - Creating to-do
    - Creating to-do list
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
> Customize Nottodbox.
- Appearance:
    - Setting style
    - Setting color scheme
    - Creating custom color schemes
- Sidebar:
    - Setting alternate row color for lists
- Notes:
    - Setting alternate row color for lists
    - Setting default background color for items
    - Setting default foreground color for item
    - Setting auto-save for documents
    - Setting format for documents
- To-dos:
    - Setting default background color for items
    - Setting default foreground color for items
- Diaries:
    - Setting default highlight color for items
    - Setting auto-save for documents
    - Setting format for documents

### About
> See some informations about Nottodbox.
- The icon and application name
- Version
- Link source codes
- Developer
- Copyright notification
- License
- License text
</details>


## Install with Meson
### Dependencies
- Python3
- PySide6
- git
- meson

### Clone, setup, install
1. ```git clone https://github.com/mukonqi/nottodbox.git```
2. ```meson setup nottodbox/builddir nottodbox```
3. ```meson install -C nottodbox/builddir```


## Run from source
### Dependencies:
- Python3
- PySide6
- git
- msgfmt (generally distributed with gettext or gettext-tools package)

### Clone, OPTIONAL features (translations and shortcut support) set-up , run
1. ```git clone https://github.com/mukonqi/nottodbox.git ; cd nottodbox```
2. ```python3 .github/scripts/translations.py``` (OPTIONAL)
3. ```python3 -m nottodbox```


## Disclaimer
> [!CAUTION] 
> Nottodbox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

> [!TIP]
> You can see the license for more details.


## Credit
- While making [nottodbox/widgets/pages.py](./nottodbox/widgets/pages.py)'s TextFormatter class, [KDE - Marknote: master/src/documenthandler.cpp](https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp) helped me as a referance.

- While making [.github/scripts/build-appimage.yml](.github/scripts/build-appimage.yml)'s script section, [DavidoTek - ProtonUp-Qt: AppImageBuilder.yml](https://github.com/DavidoTek/ProtonUp-Qt/blob/main/AppImageBuilder.yml) helped me as a reference.