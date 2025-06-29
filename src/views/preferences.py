# preferences.py
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

from gi.repository import Adw
from gi.repository import Gtk, GLib

@Gtk.Template(resource_path='/io/github/skythrew/musicology/views/preferences.ui')
class PreferencesDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'PreferencesDialog'

    discord_rpc_row = Gtk.Template.Child()

    def __init__(self, application, **kwargs):
        super().__init__(**kwargs)

        self.application = application

        self.discord_rpc_row.set_active(self.application.settings.get_boolean('discord-rpc'))
        self.discord_rpc_row.connect('notify::active', self._on_discord_rpc_activate)

    def _on_discord_rpc_activate(self, switch, pspec):
        active = switch.get_active()

        self.application.settings.set_boolean('discord-rpc', active)

        if active:
            GLib.Thread.new(None, self.application.init_discord_rpc)
        else:
            self.application.close_discord_rpc()
