# window.py
#
# Copyright 2025 Maël
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from gi.repository import Adw
from gi.repository import Gtk, GLib, Gio
from gi.repository.GdkPixbuf import Pixbuf

from .home import HomeSongCard
from .components import ArtistCard
from musicology.data import Artist, Song

@Gtk.Template(resource_path='/io/github/skythrew/musicology/views/search.ui')
class SearchWindow(Gtk.Overlay):
    __gtype_name__ = 'SearchWindow'

    content = Gtk.Template.Child()
    results_content = Gtk.Template.Child()
    spinner = Gtk.Template.Child()
    no_results = Gtk.Template.Child()

    top_result_box = Gtk.Template.Child()

    songs_list_view = Gtk.Template.Child()
    artists_list_view = Gtk.Template.Child()

    def __init__(self, application, window, **kwargs):
        self.application = application
        self.window = window

        self.top_result = None
        self.top_result_widget = None

        self.songs_list_model = Gio.ListStore.new(Song)
        self.artists_list_model = Gio.ListStore.new(Artist)

        songs_factory = Gtk.SignalListItemFactory.new()
        songs_factory.connect("setup", self.on_songs_factory_setup)
        songs_factory.connect("bind", self.on_songs_factory_bind)

        artists_factory = Gtk.SignalListItemFactory.new()
        artists_factory.connect("setup", self.on_artists_factory_setup)
        artists_factory.connect("bind", self.on_artists_factory_bind)

        super().__init__(**kwargs)

        self.songs_list_view.set_model(Gtk.NoSelection.new(self.songs_list_model))
        self.songs_list_view.set_factory(songs_factory)

        self.artists_list_view.set_model(Gtk.NoSelection.new(self.artists_list_model))
        self.artists_list_view.set_factory(artists_factory)

    def __build_song_from_result(self, result):
        return Song(
            id = result['videoId'],
            title = result['title'],
            artist = Artist(
                name = result['artists'][0]['name'],
                id = result['artists'][0]['id'],
                thumbnail_uri = ''
            ),
            thumbnail_uri = result['thumbnails'][0]['url']
        )

    def __build_artist_from_result(self, result):
        return Artist(
            id = result['browseId'],
            name = result['artist'],
            thumbnail_uri = result['thumbnails'][0]['url']
        )

    def __build_artist_from_top_result(self, result):
        return Artist(
            id = result['artists'][0]['id'],
            name = result['artists'][0]['name'],
            thumbnail_uri = result['thumbnails'][0]['url']
        )

    def __add_artist_top_result(self, result):
        GLib.idle_add(self.top_result_box.remove, self.top_result_widget)

        self.top_result = self.__build_artist_from_top_result(result)

        card = ArtistCard(self.application)
        self.top_result_widget = card
        card.set_artist(self.top_result)
        GLib.idle_add(self.top_result_box.append, card)

    def __add_song_top_result(self, result):
        GLib.idle_add(self.top_result_box.remove, self.top_result_widget)

        self.top_result = self.__build_song_from_result(result)

        card = HomeSongCard(self.application, self.window)
        self.top_result_widget = card
        card.set_song(self.top_result)
        GLib.idle_add(self.top_result_box.append, card)

    def fetch_data(self, search):
        GLib.idle_add(self.content.set_visible, False)
        GLib.idle_add(self.spinner.set_visible, True)

        self.songs_list_model.remove_all()
        self.artists_list_model.remove_all()

        results = self.application.YTMusic.search(search)

        if len(results) > 0:
            match results[0]['resultType']:
                case 'artist':
                    self.__add_artist_top_result(results[0])
                case 'song':
                    self.__add_song_top_result(results[0])
                case _:
                    top = [el for el in results if (el['resultType'] == 'artist') or (el['resultType'] == 'song')][0]

                    match top['resultType']:
                        case 'artist':
                            self.top_result = None
                        case 'song':
                            self.__add_song_top_result(top)

            for result in results[1:]:
                match result['resultType']:
                    case 'song':
                        self.songs_list_model.append(self.__build_song_from_result(result))
                    case 'artist':
                        self.artists_list_model.append(self.__build_artist_from_result(result))
        else:
            GLib.idle_add(self.no_results.set_visible, True)
            GLib.idle_add(self.results_content.set_visible, False)

        if len(results) > 0:
            GLib.idle_add(self.no_results.set_visible, False)
            GLib.idle_add(self.results_content.set_visible, True)

        GLib.idle_add(self.content.set_visible, True)
        GLib.idle_add(self.spinner.set_visible, False)

    def on_songs_factory_setup(self, factory, list_item):
        widget = HomeSongCard(self.application, window = self.window)
        list_item.set_child(widget)

    def on_songs_factory_bind(self, factory, list_item):
        song = list_item.get_item()
        card = list_item.get_child()

        GLib.idle_add(card.set_song, song)

    def on_artists_factory_setup(self, factory, list_item):
        widget = ArtistCard(self.application)
        list_item.set_child(widget)

    def on_artists_factory_bind(self, factory, list_item):
        artist = list_item.get_item()
        card = list_item.get_child()

        GLib.idle_add(card.set_artist, artist)
