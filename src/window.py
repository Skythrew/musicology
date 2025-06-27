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

import time

from gi.repository import Adw
from gi.repository import Gtk, GLib

from .views.home import Home, HomeSongCard
from .data.constants import WEBVIEW_HTML
from .views.search import SearchWindow

@Gtk.Template(resource_path='/io/github/skythrew/musicology/window.ui')
class MusicologyWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MusicologyWindow'
    webview_container = Gtk.Template.Child()

    view_stack = Gtk.Template.Child()
    split_view = Gtk.Template.Child()

    sidebar_toggle_btn = Gtk.Template.Child()

    player = Gtk.Template.Child()
    player_title = Gtk.Template.Child()
    player_artist = Gtk.Template.Child()
    player_thumbnail = Gtk.Template.Child()

    # player_duration_label = Gtk.Template.Child('duration_label')
    play_pause_btn = Gtk.Template.Child()
    play_pause_btn_content = Gtk.Template.Child()

    prev_song_btn = Gtk.Template.Child()
    next_song_btn = Gtk.Template.Child()

    player_mode_btn = Gtk.Template.Child()
    player_mode_icon = Gtk.Template.Child()

    search_revealer   = Gtk.Template.Child()
    search_toggle_btn = Gtk.Template.Child()
    search_entry      = Gtk.Template.Child()

    queue_list_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.application = self.get_application()

        self.view_stack.add_titled_with_icon(
            child=Home(application=self.application),
            name='home',
            title=_('Home'),
            icon_name='go-home-symbolic'
        )

        self.search_window = SearchWindow(self.application)
        self.view_stack.add(self.search_window)

        self.split_view.connect('notify::show-sidebar', self.player_show)

        self.sidebar_toggle_btn.connect('clicked', self.toggle_sidebar)

        self.play_pause_btn.connect('clicked', self.get_application().player_toggle)
        self.prev_song_btn.connect('clicked', self.application.prev_song)
        self.next_song_btn.connect('clicked', self.application.next_song)
        self.player_mode_btn.connect('clicked', self.application.change_player_mode)

        self.search_toggle_btn.connect('clicked', self.search_toggle)
        self.search_entry.connect('activate', self.on_search)

        self.webview_container.put(self.get_application().webview, 100, 100)  # offscreen

        self.player_title_scroll_pos = 0

        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", self.on_queue_factory_setup)
        factory.connect("bind", self.on_queue_factory_bind)

        self.queue_model = Gtk.SingleSelection.new(self.get_application().queue)
        self.queue_model.set_can_unselect(False)
        self.queue_model.set_selected(0)

        self.queue_model.connect('notify::selected', self.on_queue_song_selected)

        self.queue_list_view.set_model(self.queue_model)
        self.queue_list_view.set_factory(factory)

    def on_queue_song_selected(self, item, pspec):
        self.application.play_queue()
        self.split_view.set_show_sidebar(False)

    def on_search(self, a1):
        self.view_stack.set_visible_child(self.search_window)
        GLib.Thread.new(None, self.search_window.fetch_data, a1.get_text())

    def search_toggle(self, btn):
        self.search_revealer.set_reveal_child(not self.search_revealer.get_reveal_child())

        if self.search_revealer.get_reveal_child():
            self.search_entry.grab_focus_without_selecting()

    def toggle_sidebar(self, btn):
        sidebar_revealed = self.split_view.get_show_sidebar()

        if sidebar_revealed:
            self.split_view.set_show_sidebar(False)
        else:
            self.player_hide()
            self.split_view.set_show_sidebar(True)

    def player_hide(self):
        self.player.set_reveal_child(False)

    def player_show(self, arg1 = None, arg2 = None):
        if not self.split_view.get_show_sidebar() and len(self.application.queue) != 0:
            self.player.set_reveal_child(True)

    def player_toggle(self):
        self.player.set_reveal_child(not self.player.get_reveal_child())

    def update_current_song(self, song):
        self.player_title.set_label(song.title)
        self.player_artist.set_label(song.artist.name)

        song.connect('notify::thumbnail-pixbuf', self.update_player_thumbnail, song)
        self.player_thumbnail.set_pixbuf(song.thumbnail_pixbuf)
        self.player_show()

    def update_player_thumbnail(self, song, a2, a3):
        self.player_thumbnail.set_pixbuf(song.thumbnail_pixbuf)

    def set_player_time(self, current: int, duration: int):
        return
        current_minutes = current // 60
        current_seconds = current % 60

        duration_minutes = duration // 60
        duration_seconds = duration % 60

        self.player_duration_label.set_label(f'{current_minutes}:{str(current_seconds).zfill(2)}/{duration_minutes}:{str(duration_seconds).zfill(2)}')

    def set_player_playing(self, status):
        if status == 1:
            self.play_pause_btn_content.set_icon_name('media-playback-pause-symbolic')
        else:
            self.play_pause_btn_content.set_icon_name('media-playback-start-symbolic')

    def update_player_mode(self, mode):
        match mode:
            case 0:
                self.player_mode_icon.set_icon_name('media-playlist-consecutive-symbolic')
            case 1:
                self.player_mode_icon.set_icon_name('media-playlist-repeat-symbolic')
            case 2:
                self.player_mode_icon.set_icon_name('media-playlist-repeat-song-symbolic')

    def on_queue_factory_setup(self, factory, list_item):
        widget = HomeSongCard(self.application, clickable = False)
        list_item.set_child(widget)

    def on_queue_factory_bind(self, factory, list_item):
        song = list_item.get_item()
        card = list_item.get_child()

        GLib.idle_add(card.set_song, song)
