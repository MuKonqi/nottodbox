app_config = configuration_data()

app_config.set('PYTHON3', python_bin.full_path())
app_config.set('APP_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox'))
app_config.set('DATA_DIR', join_paths(get_option('prefix'), get_option('datadir')))
app_config.set('LOCALE_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
app_config.set('MODE', 'meson')
app_config.set('COLOR-SCHEMES_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox', 'data', 'color-schemes'))

configure_file(
  input: '__init__.py',
  output: 'nottodbox',
  configuration: app_config,
  install_dir: join_paths(get_option('prefix'), get_option('bindir')),
  install: true
)

configure_file(
  input: 'consts.py',
  output: 'consts.py',
  configuration: app_config,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox'),
  install: true
)

configure_file(
  input: 'settings.py',
  output: 'settings.py',
  configuration: app_config,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox'),
  install: true
)


install_subdir(
  meson.current_source_dir(),
  exclude_directories: ['__pycache__', 'databases/__pycache__', 'widgets/__pycache__', 'locale'],
  exclude_files: ['meson.build', 'consts.py', 'settings.py'],
  install_dir: join_paths(get_option('prefix'), get_option('datadir'))
)


run_command(find_program('chmod'), 'a+x', 
  join_paths(meson.current_build_dir(), 'nottodbox'), 
  check: true)