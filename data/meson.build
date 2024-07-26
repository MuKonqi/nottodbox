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


install_data(
    project_id + '.svg',
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'icons/hicolor/scalable/apps')
)


desktop_file_validater = find_program('desktop-file-validate', required: false)

if desktop_file_validater.found()
    test('Validate desktop file...', 
        desktop_file_validater, args: [join_paths(meson.current_build_dir(), project_id + '.desktop')])
endif


run_command(find_program('chmod'), 'a+x', 
    join_paths(meson.current_build_dir(), project_id + '.desktop'), 
    check: true)