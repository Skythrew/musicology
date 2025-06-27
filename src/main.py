# main.py
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

import sys, time
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')

from gi.repository import Gtk, Gio, Adw, WebKit, GLib
from ytmusicapi import YTMusic
from .data.constants import WEBVIEW_HTML
from .data import Song, Artist
from .window import MusicologyWindow


class MusicologyApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='io.github.skythrew.musicology',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/io/github/skythrew/musicology')

        self.YTMusic = YTMusic()

        self.webview = WebKit.WebView()
        self.webview.load_html(WEBVIEW_HTML, "http://localhost")

        self.queue = Gio.ListStore.new(Song)

        self.status = None

        # PLAYER MODES: 0 (consecutive) / 1 (queue loop) / 2 (song loop)
        self.player_mode = 0

        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

        GLib.Thread.new(None, self.update_player_ui)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = MusicologyWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name='musicology',
                                application_icon='io.github.skythrew.musicology',
                                developer_name='Maël GUERIN',
                                version='0.1.0',
                                developers=['Maël GUERIN'],
                                copyright='© 2025 Maël GUERIN')
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_('translator-credits'))
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def load_radio_for_song_call(self, song):
        GLib.Thread.new(None, self.load_radio_for_song, song)

    def load_radio_for_song(self, song):
        res = self.YTMusic.get_watch_playlist(videoId = song.id, radio = True)
        GLib.idle_add(self.load_queue, res, song)

    def load_queue(self, res, first_song = None):
        self.queue.remove_all()

        if first_song != None:
            self.queue.append(first_song)
        else:
            item = res['tracks'][0]
            self.queue.append(Song(
                id = item['videoId'],
                title = item['title'],
                artist = Artist(id = item['artists'][0]['id'], name=item['artists'][0]['name'], thumbnail_uri = ''),
                thumbnail_uri = item['thumbnail'][0]['url']
            ))

        for song in [Song(
            id = item['videoId'],
            title = item['title'],
            artist = Artist(id = item['artists'][0]['id'], name=item['artists'][0]['name'], thumbnail_uri = ''),
            thumbnail_uri = item['thumbnail'][0]['url']
        ) for item in res['tracks'][1:]]:
            self.queue.append(song)

        GLib.idle_add(self.props.active_window.sidebar_toggle_btn.set_sensitive, True)

    def play_queue(self):
        self.play_song(self.queue[self.props.active_window.queue_model.get_selected()])

    def prev_song(self, btn = None):
        if self.props.active_window.queue_model.get_selected() > 0:
            self.props.active_window.queue_model.set_selected(self.props.active_window.queue_model.get_selected() - 1)

    def next_song(self, btn = None):
        if self.props.active_window.queue_model.get_selected() < len(self.queue) - 1:
            self.props.active_window.queue_model.set_selected(self.props.active_window.queue_model.get_selected() + 1)
        elif self.player_mode == 1:
            self.props.active_window.queue_model.set_selected(0)

    def play_song(self, song):
        GLib.idle_add(self.props.active_window.update_current_song, song)
        script = f'loadSingleSong("{song.id}")'
        self.webview.evaluate_javascript(
            script,
            -1,
            cancellable=None,
            source_uri=None,
            callback=self.on_js_done,
            user_data=None
        )

    def change_player_mode(self, _ = None):
        self.player_mode = (self.player_mode + 1) % 3
        GLib.idle_add(self.props.active_window.update_player_mode, self.player_mode)

    def update_player_ui(self):
        while True:
            if self.props.active_window:
                script = f'getPlayerInfos();'
                self.webview.evaluate_javascript(
                    script,
                    -1,
                    cancellable=None,
                    source_uri=None,
                    callback=self.on_js_player_ui_return,
                    user_data=None
                )
                time.sleep(0.3)

    def on_js_player_ui_return(self, webview, result, user_data):
        try:
            js_value = webview.evaluate_javascript_finish(result)
        except GLib.Error as e:
            print("JavaScript evaluation error:", e)
            return

        res = js_value.to_string().split(',')

        if res[0] == '':
            return
        current_time = round(float(res[0]))
        duration = round(float(res[1]))
        status = int(res[2])

        self.status = status

        GLib.idle_add(self.props.active_window.set_player_time, current_time, duration)
        GLib.idle_add(self.props.active_window.set_player_playing, status)

        if self.status == 0:
            if self.player_mode == 0 or self.player_mode == 1:
                self.next_song()
            else:
                self.play_queue()

    def on_js_done(self, webview, result, user_data):
        try:
            js_value = webview.evaluate_javascript_finish(result)
        except GLib.Error as e:
            print("JavaScript evaluation error:", e)
            return

    def player_toggle(self, arg):
        if self.status == 2:
            self.webview.evaluate_javascript(
                    'player.playVideo();',
                    -1,
                    cancellable=None,
                    source_uri=None,
                    callback=None,
                    user_data=None
                )
        elif self.status == 1:
            self.webview.evaluate_javascript(
                    'player.pauseVideo();',
                    -1,
                    cancellable=None,
                    source_uri=None,
                    callback=None,
                    user_data=None
                )

def main(version):
    """The application's entry point."""
    app = MusicologyApplication()
    return app.run(sys.argv)
