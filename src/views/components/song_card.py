# song_card.py
#
# Copyright 2025 Maël GUERIN
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

from gi.repository import Adw
from gi.repository import Gtk, GLib, Gio
from gi.repository.GdkPixbuf import Pixbuf

@Gtk.Template(resource_path='/io/github/skythrew/musicology/views/components/song_card.ui')
class SongCard(Gtk.Box):
    __gtype_name__ = 'SongCard'

    title_label = Gtk.Template.Child('title')
    artist_label = Gtk.Template.Child('artist')
    thumbnail = Gtk.Template.Child('thumbnail')

    def __init__(self, application, window, clickable = True, **kwargs):
        super().__init__(**kwargs)

        self.application = application
        self.window = window

        click_controller = Gtk.GestureClick()
        if clickable:
            click_controller.connect('released', self.load_song)
        else:
            self.remove_css_class('card')

        self.add_controller(click_controller)

        self.song = None

    def set_song(self, song):
        self.song = song

        GLib.Thread.new(None, self.load_thumbnail)
        self.title_label.set_label(song.title)
        self.artist_label.set_label(song.artist.name)

    def load_song(self, a1, a2, a3, a4):
        assert self.song != None

        self.application.player.load_radio_for_song_call(self.song, self.window.update_current_song)

    def load_thumbnail(self):
        assert self.song != None

        self.song.load_pixbuf()

        GLib.idle_add(self.thumbnail.set_pixbuf, self.song.thumbnail_pixbuf)
