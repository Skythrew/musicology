# home.py
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

from .components.song_card import SongCard

from musicology.data import Artist, Song

@Gtk.Template(resource_path='/io/github/skythrew/musicology/views/home.ui')
class Home(Gtk.Overlay):
    __gtype_name__ = 'Home'

    content = Gtk.Template.Child()
    spinner = Gtk.Template.Child()
    quick_picks_list = Gtk.Template.Child()

    def __init__(self, application, window, **kwargs):
        self.application = application
        self.window = window

        self.data = None
        self.quick_picks = None
        self.quick_picks_model = Gio.ListStore.new(Song)
        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", self.on_factory_setup)
        factory.connect("bind", self.on_factory_bind)

        super().__init__(**kwargs)

        self.quick_picks_list.set_model(Gtk.NoSelection.new(self.quick_picks_model))
        self.quick_picks_list.set_factory(factory)

        GLib.Thread.new(None, self.fetch_data)

    def fetch_data(self):
        self.content.set_visible(False)
        self.spinner.set_visible(True)

        self.data = self.application.YTMusic.get_home()

        for section in self.data:
            if section['title'].lower() == 'quick picks':
                self.quick_picks = section['contents']

        for item in self.quick_picks:
            song = Song(
                id = item['videoId'],
                title=item['title'],
                thumbnail_uri=item['thumbnails'][0]['url'],
                artist=Artist(name=item['artists'][0]['name'], id=item['artists'][0]['id'], thumbnail_uri='')
            )

            GLib.Thread.new(None, song.load_pixbuf)
            self.quick_picks_model.append(song)

        self.content.set_visible(True)
        self.spinner.set_visible(False)

    def on_factory_setup(self, factory, list_item):
        widget = SongCard(self.application, self.window)
        list_item.set_child(widget)

    def on_factory_bind(self, factory, list_item):
        song = list_item.get_item()
        card = list_item.get_child()

        GLib.idle_add(card.set_song, song)
