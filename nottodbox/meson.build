conf_app = configuration_data()

conf_app.set('PYTHON3', python_bin.full_path())
conf_app.set('VERSION', project_version)
conf_app.set('COMMIT', project_commit)
conf_app.set('APPDIR', join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox'))
conf_app.set('LOCALEDIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
conf_app.set('DESKTOPFILE', join_paths(get_option('prefix'), get_option('datadir'), 'applications') + '/' + project_id + '.desktop')
conf_app.set('ICONFILE', join_paths(get_option('prefix'), get_option('datadir'), 'icons/hicolor/scalable/apps') + '/' + project_id + '.svg')


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

install_subdir(
  meson.current_source_dir(),
  exclude_directories: ['__pycache__'],
  exclude_files: ['meson.build', 'about.py'],
  install_dir: join_paths(get_option('prefix'), get_option('datadir'))
)


run_command(find_program('chmod'), 'a+x', 
  join_paths(meson.current_build_dir(), 'nottodbox'), 
  check: true)