# Nottodbox

<p align="center">
    <img src="./share/icons/hicolor/96x96/apps/io.github.mukonqi.nottodbox.png" alt="Icon of Nottodbox"></img><br>
    <img src="https://img.shields.io/badge/Organize_notes,_to--dos_and_diaries-376296" alt="Organize notes, to-dos and diaries"></img><br>
    <img src="https://img.shields.io/github/downloads/mukonqi/nottodbox/total?label=Downloads" alt="Downloads"></img>
    <img src="https://img.shields.io/github/v/release/mukonqi/nottodbox?label=Release" alt="Release"><br>
    <a href="https://github.com/mukonqi/nottodbox/releases/latest"><img src="https://docs.appimage.org/_images/download-appimage-banner.svg" alt="Download as an AppImage" /></a>
</p>

Nottodbox allows you to create and organize notes, to-dos, and diaries with rich text support in popular formats.

- In today's fast-paced world, we often have multiple tasks to handle simultaneously. That's why you can open multiple documents at once in the desired row x column layout. 

- You can change the style and color scheme of the app to make it feel more like home.

- All customization options for documents/notebooks:
    - You can mark a to-do as completed once it's finished.
    - You can add a content lock to a document to turn it into a diary. This prevents the backup from being modified after that point.
	- Documents are automatically saved unless you are editing a outdated diary and have disabled this feature. Additionally, a backup of the old content is always retained. Furthermore, auto-saves do not overwrite backups, meaning your manual changes remain intact.
    - Documents can be in three formats: Markdown, HTML, and plain text.
	- Documents can be exported in multiple formats to your Documents or Desktop folder by default if you enable this feature. This allows you to edit them in other applications as well.
    - You can pin your favorite documents/notebooks to the sidebar for easy access.
    
	- You can change the background, text, and border colors of the document/notebook in three different states (normal, hover, and click) at the location of your choice.

	And here's the most important part! All documents are associated with a notebook, and all options can follow it. All documents/notebooks can use the default settings or follow the global settings. With them, you can to customize so many things with ease.

## Images
<details>
<summary>Show / Hide</summary>

![Appearance when using 'Nottodbox Light' color scheme](.github/images/light.png)
![Appearance when using 'Nottodbox Dark' color scheme](.github/images/dark.png)
</details>


## Run from source
### Dependencies:
- Python3
- PySide6
- git

### Clone and run
1. ```git clone https://github.com/mukonqi/nottodbox.git```
2. ```python3 nottodbox/nottodbox/__init__.py```


## Disclaimer
> [!CAUTION] 
> Nottodbox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

> [!TIP]
> You can see the license for more details.


## Credit
- While making [nottodbox/widgets/documents.py](./nottodbox/widgets/documents.py)'s DocumentHelper class, [KDE - Marknote: master/src/documenthandler.cpp](https://invent.kde.org/office/marknote/-/blob/master/src/documenthandler.cpp) helped me as a referance.