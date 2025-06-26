pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'musicology' / 'views'

musicology_sources = [
  '__init__.py',
  'home.py'
]

install_data(musicology_sources, install_dir: moduledir)
