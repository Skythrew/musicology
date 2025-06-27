import requests

from gi.repository import Gio, GObject
from gi.repository.GdkPixbuf import Pixbuf

class Artist(GObject.Object):
    name = GObject.Property(type=str)
    id = GObject.Property(type=str)
    thumbnail_uri = GObject.Property(type=str)
    thumbnail_pixbuf = GObject.Property(type=Pixbuf)

    def __init__(self, name, id, thumbnail_uri):
        super().__init__()
        self.name = name
        self.id   = id
        self.thumbnail_uri = thumbnail_uri

    def load_pixbuf(self):
        request = requests.get(self.thumbnail_uri)

        input_stream = Gio.MemoryInputStream.new_from_data(request.content, None)

        pixbuf = Pixbuf.new_from_stream(input_stream, None)
        self.thumbnail_pixbuf = pixbuf

