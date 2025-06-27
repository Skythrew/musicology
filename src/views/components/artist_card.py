import requests

from gi.repository import Adw
from gi.repository import Gtk, GLib, Gio
from gi.repository.GdkPixbuf import Pixbuf

from musicology.data import Artist, Song

@Gtk.Template(resource_path='/io/github/skythrew/musicology/views/components/artist_card.ui')
class ArtistCard(Gtk.Box):
    __gtype_name__ = 'ArtistCard'

    name_label = Gtk.Template.Child('name')
    thumbnail = Gtk.Template.Child('thumbnail')

    def __init__(self, application, **kwargs):
        super().__init__(**kwargs)

        self.application = application

        click_controller = Gtk.GestureClick()

        self.add_controller(click_controller)

        self.artist = None

    def set_artist(self, artist):
        self.artist = artist

        GLib.Thread.new(None, self.load_thumbnail)
        self.name_label.set_label(artist.name)

    def load_thumbnail(self):
        assert self.artist != None

        self.artist.load_pixbuf()

        GLib.idle_add(self.thumbnail.set_pixbuf, self.artist.thumbnail_pixbuf)
