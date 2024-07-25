conf_app = configuration_data()

conf_app.set('PYTHON3', python_bin.full_path())
conf_app.set('VERSION', project_version)
conf_app.set('APPDIR', join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox'))
conf_app.set('LOCALEDIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))


configure_file(
    input: 'nottodbox.in',
    output: 'nottodbox',
    configuration: conf_app,
    install_dir: join_paths(get_option('prefix'), get_option('bindir')),
    install: true
)


install_subdir(
    meson.current_source_dir(),
    exclude_directories: ['__pycache__'],
    exclude_files: ['nottodbox.in', 'meson.build'],
    install_dir: join_paths(get_option('prefix'), get_option('datadir'))
)