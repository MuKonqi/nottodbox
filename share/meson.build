desktop_config = configuration_data()
desktop_config.set('BIN_DIR', join_paths(get_option('prefix'), get_option('bindir')))

i18n.merge_file(
  input: configure_file(
      input: files(join_paths('applications', project_id + '.desktop.in.in')),
      output: project_id + '.desktop.in',
      configuration: desktop_config
  ),
  output: project_id + '.desktop',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  type: 'desktop',
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'applications')
)

desktop_file_validater = find_program('desktop-file-validate', required: false)

if desktop_file_validater.found()
  test('Validate desktop file...', 
      desktop_file_validater, args: [join_paths(meson.current_build_dir(), project_id + '.desktop')])
endif

run_command(find_program('chmod'), 'a+x', 
  join_paths(meson.current_build_dir(), project_id + '.desktop.in'), 
  check: true)


i18n.merge_file(
  input: join_paths('metainfo', project_id + '.appdata.xml.in'),
  output: project_id + '.appdata.xml',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'metainfo')
)

metainfo_file_validater = find_program('appstreamcli', required: false)

if metainfo_file_validater.found()
  test('Validate AppStream meta info file...', 
      metainfo_file_validater, args: ['validate', join_paths(meson.current_build_dir(), project_id + '.appdata.xml')])
endif


install_subdir(
  join_paths(meson.current_source_dir(), 'icons'),
  install_dir: join_paths(get_option('prefix'), get_option('datadir'))
)