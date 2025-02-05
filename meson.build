project (
  'nottodbox',
  version: '0.0.7',
  license: 'GPL-3.0-or-later'
)


project_id = 'io.github.mukonqi.nottodbox'
project_name = meson.project_name()
project_version = meson.project_version()
project_commit = run_command(find_program('git'), 'rev-parse', '--short', 'HEAD', capture: true, check: true).stdout().replace('\n', '')


python = import('python')
i18n = import('i18n')
gnome = import('gnome')


python_bin = python.find_installation('python3',
  modules: ['sys', 'locale', 'argparse', 'gettext', 'getpass', 'os', 'subprocess', 'sqlite3', 'datetime', 'json', 'PySide6'])

if not python_bin.found()
  error('Python3 or required Python libraries can not found!')
endif


getent = find_program('getent')

if not getent.found()
  error('Getent can not found!')
endif


cut = find_program('cut')

if not cut.found()
  error('Cut can not found!')
endif


subdir('data')
subdir('nottodbox')
subdir('po')


install_data(
  'LICENSE.txt',
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox')
)


install_data(
  'README.md',
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox')
)


gnome.post_install(
  gtk_update_icon_cache: true,
  update_desktop_database: true
)