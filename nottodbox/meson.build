conf_app = configuration_data()

conf_app.set('PYTHON3', python_bin.full_path())
conf_app.set('APP_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox'))
conf_app.set('LOCALE_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
conf_app.set('COLOR-SCHEMES_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox', 'data', 'color-schemes'))

configure_file(
  input: '__init__.py',
  output: 'nottodbox',
  configuration: conf_app,
  install_dir: join_paths(get_option('prefix'), get_option('bindir')),
  install: true
)

configure_file(
  input: 'about.py',
  output: 'about.py',
  configuration: conf_app,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox'),
  install: true
)

configure_file(
  input: 'settings.py',
  output: 'settings.py',
  configuration: conf_app,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox'),
  install: true
)


install_subdir(
  meson.current_source_dir(),
  exclude_directories: ['__pycache__'],
  exclude_files: ['meson.build', 'about.py', 'settings.py'],
  install_dir: join_paths(get_option('prefix'), get_option('datadir'))
)


run_command(find_program('chmod'), 'a+x', 
  join_paths(meson.current_build_dir(), 'nottodbox'), 
  check: true)