from gi.repository import GObject

class Artist(GObject.Object):
    name = GObject.Property(type=str)
    id = GObject.Property(type=str)

    def __init__(self, name, id):
        super().__init__()
        self.name = name
        self.id   = id
