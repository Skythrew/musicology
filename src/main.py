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
from .backend import Player
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

        self.player = Player(self.webview, self.YTMusic)

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

    def change_player_mode(self, _ = None):
        self.player.update_mode()
        GLib.idle_add(self.props.active_window.update_player_mode, self.player.mode)

    def update_player_ui(self):
        while True:
            if self.props.active_window:
                self.player.get_infos(callback = self.on_js_player_ui_return)
                time.sleep(0.3)

    def on_js_player_ui_return(self, player_infos):
        GLib.idle_add(self.props.active_window.set_player_time, player_infos.current_time, player_infos.duration)
        GLib.idle_add(self.props.active_window.set_player_playing, player_infos.status)

        if player_infos.status == 0:
            if self.player.mode == 0 or self.player.mode == 1:
                self.player.next_song()
            else:
                self.player.play_queue()

def main(version):
    """The application's entry point."""
    app = MusicologyApplication()
    return app.run(sys.argv)
