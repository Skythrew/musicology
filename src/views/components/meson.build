pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'musicology' / 'views' / 'components'

musicology_sources = [
  '__init__.py',
  'artist_card.py',
  'song_card.py'
]

install_data(musicology_sources, install_dir: moduledir)
