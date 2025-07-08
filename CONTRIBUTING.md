# Contributing to Nottodbox
Thank you for your interest in contributing to Nottodbox!

## How to Contribute
> [!CAUTION]
> You should not use <> in file name. I'll use them here because I wanted to highlight that they need to change.

### Report bugs

If it is related to the nottodbox/ folder, i.e., directly related to the application code, please use the “Bug Report” template.

### Request features

Please use the "Feature Request" template.

### Submit code changes
Respect code style:
  - Linter: Ruff
  - Formatter: Ruff
  - Naming: MyClass, myFunction, my_variable, MY_CONST and use `self` for the first argument of class.

### Translations

Nottodbox uses two different systems for localization depending on the type of content:

- **QTranslator** for the main application's UI translations (necessary).
- **gettext** for `.desktop` and `.metainfo` files (optional, this is only related with Linux).

#### 1. Translating the Application (QTranslator)

- The UI strings in the app are translated using Qt's QTranslator system.
- Translation files are `.ts` files located in the `locates/` directory.
- To contribute translations or updates:
  1. If you add a new language:
    1. Run ```pyside6-lupdate nottodbox/scripts/*.py nottodbox/scripts/*/*.py -no-obsolete -source-language en_US -target-language <languagecode_COUNTRYCODE> -ts locale/<languagecode_COUNTRYCODE>.ts``` (do not forget change languagecode_COUNTRYCODE (example: tr_TR))
  2. Use Qt Linguist (`linguist`) to open and edit `.ts` files.
  3. Submit updated file in your pull request.

#### 2. Translating `.desktop` and `.metainfo` Files (gettext)
- The `.desktop` and `.metainfo` files use GNU gettext for localization.
- Translation files are `.po` files located in the `po/` directory.
- To contribute:
  1. If you add a new language: 
    1. Run ```xgettext share/applications/io.github.mukonqi.nottodbox.desktop.in share/metainfo/io.github.mukonqi.nottodbox.appdata.xml.in -o po/template.pot```.
    2. Copy `po/template.pot` file and paste as `po/<languagecode_COUNTRYCODE>.po` (do not forget change languagecode_COUNTRYCODE (example: tr_TR))
  1. Edit the relevant `.po` files using a gettext editor such as Poedit.
  2. Submit updated file with your pull request.

### Color Schemes

Nottodbox supports two color scheme format:
  - KDE's .colors format: Detailed and very popular (just look to [KDE Store | Plasma Color Schemes](https://store.kde.org/browse?cat=112&ord=latest))
  - Nottodbox's .json format: Simple and preferred way for Nottodbox

- To contribute:
  1. Prepare the file:
    - Use Nottodbox's appareance settings.
    - By-hand:
      1. Create `nottodbox/color-schemes/<name>.json` file.
      2. Copy-paste this: 
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
      3. And edit file according to this:
        - Colors must be in the HEX form (#rrggbb).
        - If you are not going to set a color for a color role, you must delete it from the file.
        - You learn meaning of these color roles in [Qt's page](https://doc.qt.io/qt-6/qpalette.html#ColorRole-enum).
  2. Submit the new file.

## License

By contributing to Nottodbox, you agree that your contributions will be licensed under the project's [GPL-3.0-or-later](https://github.com/MuKonqi/nottodbox/blob/main/LICENSE.txt) license.

---
Thank you for helping improve Nottodbox!