# Nottodbox

<p align="center">
    <img src="./share/icons/hicolor/96x96/apps/io.github.mukonqi.nottodbox.png" alt="Icon of Nottodbox"></img><br>
    <img src="https://img.shields.io/badge/Organize_notes,_to--dos_and_diaries-376296" alt="Organize notes, to-dos and diaries"></img><br>
    <img src="https://img.shields.io/github/downloads/mukonqi/nottodbox/total?label=Downloads" alt="Downloads"></img>
    <img src="https://img.shields.io/github/v/release/mukonqi/nottodbox?label=Release" alt="Release"><br>
</p>

<p>Nottodbox allows you to create and organize notes, to-dos, and diaries with rich text support in popular formats.</p>
<p>In today&#39;s fast-paced world, we often have multiple tasks to handle simultaneously. That&#39;s why you can open multiple documents at once in the desired row x column layout.</p>
<p>You can change the style and color scheme of the application to make it feel more like home.</p>
<p>All customization options for documents/notebooks:</p>
<ul>
    <li>You can mark a to-do as completed or uncompleted.</li>
    <li>You can add a content lock to a document to turn it into a diary. This prevents the backup from being changed.</li>
    <li>Documents are automatically saved unless you are editing a outdated diary and have disabled this feature. Additionally, a backup of the old content is always retained. Furthermore, auto-saves do not overwrite backups, meaning your manual changes remain intact.</li>
    <li>Documents can be in three formats: Markdown, HTML, and plain-text.</li>
    <li>Documents can be exported in multiple formats to your 'Documents' or 'Desktop' folder if you enable this feature. This allows you to edit them in other applications as well.</li>
    <li>You can pin your favorite documents/notebooks to the sidebar for easy access.</li>
    <li>You can change the background, text, and border colors of the document/notebook in three different states: normal, hover, and click</li>
</ul>
<p>And here&#39;s the most important part! All documents are associated with a notebook, and all options can follow it. All documents/notebooks can use the default settings or follow the global settings. With them, you can to customize so many things with ease.</p>

## Images
<details>
<summary>Show / Hide</summary>

![Appearance when using 'Nottodbox Light' color scheme](.github/images/light.png)
![Appearance when using 'Nottodbox Dark' color scheme](.github/images/dark.png)
</details>

## Using
<!-- ### Installing from Flatpak / Flathub (recommended for Linux users)
> [!WARNING]
> [Set up Flatpak](https://flatpak.org/setup/)

- `flatpak install io.github.mukonqi.nottodbox` -->

### Installing from GitHub releases (recommended for Windows and macOS users)
- [Download for Linux](https://github.com/MuKonqi/nottodbox/releases/download/latest/nottodbox)
- [Download for macOS](https://github.com/MuKonqi/nottodbox/releases/download/latest/nottodbox-mac)
- [Download for Windows](https://github.com/MuKonqi/nottodbox/releases/download/latest/nottodbox.exe)

<!-- ### Installing from PyPI
> [!WARNING] 
> Dependencies: Python (3.10 and higher) and pip

- `pip install nottodbox` -->

### Building a Flatpak
> [!WARNING]
> [Set up Flatpak](https://flatpak.org/setup/)

- Build: `git clone https://github.com/mukonqi/nottodbox.git ; cd nottodbox ; flatpak-builder --user --force-clean --install-deps-from flathub --install --sandbox .flatpak-builder/app io.github.mukonqi.nottodbox.yaml`
- Run: `flatpak run --branch=master --arch=x86_64 --command=nottodbox io.github.mukonqi.nottodbox`

### Building via pip
> [!WARNING] 
> Dependencies: Python (3.10 and higher), pip and git
> [!CAUTION] 
> Build command tested on bash.

- Build: `git clone https://github.com/mukonqi/nottodbox.git ; cd nottodbox ; pip install .`
- Run: `nottodbox`

### Building via PyInstaller
> [!WARNING] 
> Dependencies: Python (3.10 and higher), PySide6, PyInstaller and git

> [!CAUTION] 
> Build command tested on bash.

- Build: `git clone https://github.com/mukonqi/nottodbox.git ; cd nottodbox ; pyinstaller --add-data 'nottodbox/color-schemes/:nottodbox/color-schemes' --add-data 'nottodbox/LICENSE.txt:nottodbox' -F -n nottodbox nottodbox/__main__.py`
- Now you can find the executable in dist/nottodbox(.exe).

## Running from source
> [!WARNING] 
> Dependencies: Python (3.10 and higher), PySide6 and git

> [!CAUTION] 
> Run command tested on bash.

- `git clone https://github.com/mukonqi/nottodbox.git ; cd nottodbox ; python3 -m nottodbox`

## Disclaimer
> [!CAUTION] 
> Nottodbox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

> [!TIP]
> You can see the license for more details.

## Credit
- While making [nottodbox/scripts/widgets/documents.py](./nottodbox/scripts/widgets/documents.py)'s DocumentHelper class, [KDE - Marknote: master/src/documenthandler.cpp](https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp) helped me as a referance.