# Nottodbox-style Color Schemes

## File location
- If you want a color scheme to be added to the program, put the file in [data/color-schemes](/data/color-schemes/).

- If you want a color scheme to only you, put the file in .local/share/nottodbox/color-schemes in your home directory.

## File scheme
> [!TIP]
> You can create color scheme easily with in Nottodbox's appareance settings.

> [!WARNING]
> The file name (not color scheme name!) must end with .json.

> [!WARNING]
> Colors must be in the HEX form (#rrggbb).

> [!WARNING]
> If you are not going to set a color for a color role, you must delete it from the file.

> [!TIP]
> You can go to [Qt's page about color roles](https://doc.qt.io/qt-6/qpalette.html#ColorRole-enum).

```
{
    "name": "",
    "colors": {
        "Window": "",
        "WindowText": "",
        "Base": "",
        "AlternateBase": "",
        "ToolTipBase": "",
        "ToolTipText": "",
        "PlaceholderText": "",
        "Text": "",
        "Button": "",
        "ButtonText": "",
        "BrightText": "",
        "Light": "",
        "Midlight": "",
        "Dark": "",
        "Mid": "",
        "Shadow": "",
        "Highlight": "",
        "Accent": "",
        "HighlightedText": "",
        "Link": "",
        "LinkVisited": ""
    } 
}
```