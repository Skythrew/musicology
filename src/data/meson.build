pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'musicology' / 'data'

musicology_sources = [
  '__init__.py',
  'artist.py',
  'song.py',
  'constants.py'
]

install_data(musicology_sources, install_dir: moduledir)
