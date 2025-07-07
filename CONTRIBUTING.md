# Contributing to Nottodbox
Thank you for your interest in contributing to Nottodbox!

## How to Contribute
### Bugs reporting

### Feature request

### Submit code changes

### Translations
Nottodbox uses two different systems for localization depending on the type of content:

- **QTranslator** for the main application UI translations.
- **gettext** for `.desktop` and `.metainfo` files.

#### 1. Translating the Application (QTranslator)

- The UI strings in the app are translated using Qt's QTranslator system.
- Translation files are `.ts` files located in the `locates/` directory.
- To contribute translations or updates:
  - If you add a new language:
    - Run ```pyside6-lupdate nottodbox/scripts/*.py nottodbox/scripts/*/*.py -no-obsolete -source-language en_US -target-language languagecode_COUNTRYCODE -ts locale/languagecode_COUNTRYCODE.ts``` (do not forget change languagecode_COUNTRYCODE (example: tr_TR))
  - Use Qt Linguist (`linguist`) to open and edit `.ts` files.
  - Submit both updated `.ts` file in your pull request.

#### 2. Translating `.desktop` and `.metainfo` Files (gettext)
> ![CAUTION]
> If you a non-Linux user, you can skip this section. It may be hard. Because Nottodbox `.desktop` and `.metainfo` are only related with Linux.

- The `.desktop` and `.metainfo` files use GNU gettext for localization.
- Translation files are `.po` files located in the `po/` directory.
- To contribute:
  - If you add a new language: 
    - Run ```xgettext share/applications/io.github.mukonqi.nottodbox.desktop.in share/metainfo/io.github.mukonqi.nottodbox.appdata.xml.in -o po/template.pot```.
    - Copy `po/template.pot` file and paste as `po/languagecode_COUNTRYCODE.po` (do not forget change languagecode_COUNTRYCODE (example: tr_TR))
  - Edit the relevant `.po` files using a gettext editor such as Poedit.
  - Submit updated `.po` file with your pull request.

## Code Style
- Nottodbox uses Ruff for linting but does not uses any formatting tool for now.

## License
By contributing to Nottodbox, you agree that your contributions will be licensed under the project's [GPL-3.0 License](https://github.com/MuKonqi/nottodbox/blob/main/LICENSE.txt).

---
Thank you for helping improve Nottodbox!