import requests

from .artist import Artist
from gi.repository import GObject, Gio
from gi.repository.GdkPixbuf import Pixbuf

class Song(GObject.Object):
    id = GObject.Property(type=str)
    title = GObject.Property(type=str)
    thumbnail_uri = GObject.Property(type=str)
    thumbnail_pixbuf = GObject.Property(type=Pixbuf)
    artist = GObject.Property(type=Artist)

    def __init__(self, id, title, artist, thumbnail_uri):
        super().__init__()
        self.id = id
        self.title = title
        self.artist = artist
        self.thumbnail_uri = thumbnail_uri

    def set_pixbuf(self, pixbuf):
        self.thumbnail_pixbuf = pixbuf

    def load_pixbuf(self):
        request = requests.get(self.thumbnail_uri)

        input_stream = Gio.MemoryInputStream.new_from_data(request.content, None)

        pixbuf = Pixbuf.new_from_stream(input_stream, None)
        self.set_pixbuf(pixbuf)
        self.notify('thumbnail-pixbuf')
