project (
  'nottodbox'
)


project_id = 'io.github.mukonqi.nottodbox'
project_name = 'nottodbox'


python = import('python')
i18n = import('i18n')
gnome = import('gnome')


python_bin = python.find_installation('python3',
  modules: ['sys', 'argparse', 'gettext', 'getpass', 'os', 'sqlite3', 'datetime', 'configparser', 'json', 'PySide6'])

if not python_bin.found()
  error('Python3 or required Python libraries can not found!')
endif


subdir('nottodbox')
subdir('po')
subdir('share')


install_data(
  join_paths(meson.current_source_dir(), 'LICENSE.txt'),
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox')
)

install_data(
  join_paths(meson.current_source_dir(), 'README.md'),
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox')
)

install_data(
  join_paths(meson.current_source_dir(), 'README.md'),
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'docs', 'nottodbox')
)


gnome.post_install(
  gtk_update_icon_cache: true,
  update_desktop_database: true
)