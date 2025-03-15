conf_desktop = configuration_data()

conf_desktop.set('BINDIR', join_paths(get_option('prefix'), get_option('bindir')))


i18n.merge_file(
  input: configure_file(
      input: files(project_id + '.desktop.in.in'),
      output: project_id + '.desktop.in',
      configuration: conf_desktop
  ),
  output: project_id + '.desktop',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  type: 'desktop',
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'applications')
)


i18n.merge_file(
  input: project_id + '.metainfo.xml.in',
  output: project_id + '.metainfo.xml',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'metainfo')
)


install_subdir(
  join_paths(meson.current_source_dir(), 'color-schemes'),
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'nottodbox', 'data')
)


install_subdir(
  join_paths(meson.current_source_dir(), 'icons'),
  install_dir: join_paths(get_option('prefix'), get_option('datadir'))
)


desktop_file_validater = find_program('desktop-file-validate', required: false)

if desktop_file_validater.found()
  test('Validate desktop file...', 
      desktop_file_validater, args: [join_paths(meson.current_build_dir(), project_id + '.desktop')])
endif


metainfo_file_validater = find_program('appstreamcli', required: false)

if metainfo_file_validater.found()
  test('Validate AppStream meta info file...', 
      metainfo_file_validater, args: ['validate', join_paths(meson.current_source_dir(), project_id + '.metainfo.xml')])
endif


run_command(find_program('chmod'), 'a+x', 
  join_paths(meson.current_build_dir(), project_id + '.desktop.in'), 
  check: true)


run_command(find_program('chmod'), 'a+x', 
  join_paths(meson.current_build_dir(), project_id + '.desktop'), 
  check: true)