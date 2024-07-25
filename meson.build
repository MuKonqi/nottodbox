project (
    'nottodbox',
    version: '0.1.0',
    license: 'GPL-3.0-or-later'
)

project_id = 'io.github.mukonqi.nottodbox'
project_version = meson.project_version()
project_name = 'Nottodbox'
project_url = 'https://github.com/mukonqi/nottodbox'
project_copyright = 'Copyright (C) 2024 MuKonqi (Muhammed S.)'

python = import('python')
i18n = import('i18n')
gnome = import('gnome')


python_bin = python.find_installation('python3',
    modules: ['sys', 'locale', 'gettext', 'getpass', 'os', 'sqlite3', 'typing', 'datetime', 'PyQt6'])


if not python_bin.found()
    error('Python3 or required modules can not found!')
endif


subdir('data')
subdir('nottodbox')
subdir('po')


gnome.post_install(
    gtk_update_icon_cache: true,
    update_desktop_database: true
)