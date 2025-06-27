pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'musicology' / 'backend'

musicology_sources = [
  '__init__.py',
  'player.py'
]

install_data(musicology_sources, install_dir: moduledir)
