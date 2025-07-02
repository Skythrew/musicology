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

from .views.home import Home
from .views.components import SongCard
from .views.help_overlay import HelpOverlay
from .data.constants import WEBVIEW_HTML
from .views.search import SearchWindow
from .backend import PlayerState, PlayerMode

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

    player_progress = Gtk.Template.Child()
    play_pause_btn = Gtk.Template.Child()
    play_pause_btn_content = Gtk.Template.Child()

    prev_song_btn = Gtk.Template.Child()
    next_song_btn = Gtk.Template.Child()

    player_mode_btn = Gtk.Template.Child()
    player_mode_icon = Gtk.Template.Child()

    search_revealer   = Gtk.Template.Child()
    search_toggle_btn = Gtk.Template.Child()
    search_entry      = Gtk.Template.Child()

    current_position_label = Gtk.Template.Child()
    remaining_time_label = Gtk.Template.Child()

    queue_list_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.application = self.get_application()

        self.set_help_overlay(HelpOverlay())

        self.view_stack.add_titled_with_icon(
            child=Home(application=self.application, window = self),
            name='home',
            title=_('Home'),
            icon_name='go-home-symbolic'
        )

        self.connect('close-request', self.__on_close)

        self.search_window = SearchWindow(self.application, self)
        self.view_stack.add(self.search_window)

        self.split_view.connect('notify::show-sidebar', self.player_show)

        self.sidebar_toggle_btn.connect('clicked', self.toggle_sidebar)

        self.play_pause_btn.connect('clicked', self.on_play_pause_btn_clicked)
        self.prev_song_btn.connect('clicked', self.on_prev_btn_clicked)
        self.next_song_btn.connect('clicked', self.on_next_btn_clicked)
        self.player_mode_btn.connect('clicked', self.application.change_player_mode)

        self.search_toggle_btn.connect('clicked', self.search_toggle)
        self.search_entry.connect('activate', self.on_search)

        self.webview_container.put(self.application.webview, 100, 100)  # offscreen

        self.player_title_scroll_pos = 0

        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", self.on_queue_factory_setup)
        factory.connect("bind", self.on_queue_factory_bind)

        self.application.player.queue_model.connect('notify::n-items', self.on_queue_size_change)
        self.application.player.queue_model.connect('notify::selected', self.on_queue_song_selected)

        self.queue_list_view.set_model(self.application.player.queue_model)
        self.queue_list_view.set_factory(factory)

    def __on_close(self, _):
        self.close()

    def on_queue_song_selected(self, item, pspec):
        self.application.player.play_queue()
        self.update_current_song(item.get_selected_item())
        self.split_view.set_show_sidebar(False)

    def on_queue_size_change(self, queue, pspec):
        if queue.get_property('n-items') > 0:
            self.sidebar_toggle_btn.set_sensitive(True)
        else:
            self.sidebar_toggle_btn.set_sensitive(False)

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

    def on_play_pause_btn_clicked(self, btn):
        self.application.player.toggle()

    def on_next_btn_clicked(self, btn):
        self.application.player.next_song()

    def on_prev_btn_clicked(self, btn):
        self.application.player.prev_song()

    def player_hide(self):
        self.player.set_reveal_child(False)

    def player_show(self, arg1 = None, arg2 = None):
        if not self.split_view.get_show_sidebar() and len(self.application.player.queue) != 0:
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
        current_minutes = current // 60
        current_seconds = current % 60

        duration_minutes = duration // 60
        duration_seconds = duration % 60

        remaining_minutes = (duration - current) // 60
        remaining_seconds = (duration - current) % 60

        self.player_progress.set_min_value(0)
        self.player_progress.set_max_value(duration)

        self.player_progress.set_value(current)

        self.current_position_label.set_label(f'+ {current_minutes}:{str(current_seconds).zfill(2)}')
        self.remaining_time_label.set_label(f'- {remaining_minutes}:{str(remaining_seconds).zfill(2)}')

    def set_player_playing(self, status):
        if status == PlayerState.PLAYING:
            self.play_pause_btn_content.set_icon_name('media-playback-pause-symbolic')
        else:
            self.play_pause_btn_content.set_icon_name('media-playback-start-symbolic')

    def update_player_mode(self, mode):
        match mode:
            case PlayerMode.CONSECUTIVE:
                self.player_mode_icon.set_icon_name('media-playlist-consecutive-symbolic')
            case PlayerMode.QUEUE_LOOP:
                self.player_mode_icon.set_icon_name('media-playlist-repeat-symbolic')
            case PlayerMode.SONG_LOOP:
                self.player_mode_icon.set_icon_name('media-playlist-repeat-song-symbolic')

    def on_queue_factory_setup(self, factory, list_item):
        widget = SongCard(self.application, window = self, clickable = False)
        list_item.set_child(widget)

    def on_queue_factory_bind(self, factory, list_item):
        song = list_item.get_item()
        card = list_item.get_child()

        GLib.idle_add(card.set_song, song)
