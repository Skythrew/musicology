from dataclasses import dataclass
from gi.repository import Gio, Gtk, GLib
from musicology.data import Song, Artist

@dataclass
class PlayerInfos:
    current_time: int
    duration: int
    status: int

class PlayerMode:
    CONSECUTIVE = 0
    QUEUE_LOOP = 1
    SONG_LOOP = 2

class PlayerState:
    UNSTARTED = -1
    ENDED = 0
    PLAYING = 1
    PAUSED = 2
    BUFFERING = 3
    VIDEO_CUED = 5

class Player:
    def __init__(self, webview, YTMusic):
        self.webview = webview
        self.YTMusic = YTMusic

        self.queue = Gio.ListStore.new(Song)

        self.queue_model = Gtk.SingleSelection.new(self.queue)
        self.queue_model.set_can_unselect(False)
        self.queue_model.set_selected(0)

        self.current_position = 0
        self.duration = 0

        self.status = PlayerState.UNSTARTED

        # PLAYER MODES: 0 (consecutive) / 1 (queue loop) / 2 (song loop)
        self.mode = PlayerMode.CONSECUTIVE

    def load_radio_for_song_call(self, song, callback):
        GLib.Thread.new(None, self.load_radio_for_song, song, callback)

    def load_radio_for_song(self, song, callback):
        res = self.YTMusic.get_watch_playlist(videoId = song.id, radio = True)
        GLib.idle_add(self.load_queue, res, song, callback)

    def load_queue(self, res, first_song = None, callback = None):
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

        if callback != None:
            callback(self.queue[0])

    def play_queue(self):
        self.play_song(self.queue[self.queue_model.get_selected()])

    def prev_song(self):
        if self.queue_model.get_selected() > 0:
            self.queue_model.set_selected(self.queue_model.get_selected() - 1)

    def next_song(self):
        if self.queue_model.get_selected() < len(self.queue) - 1:
            self.queue_model.set_selected(self.queue_model.get_selected() + 1)
        elif self.mode == PlayerMode.QUEUE_LOOP:
            self.queue_model.set_selected(0)

    def update_mode(self):
        self.mode = (self.mode + 1) % 3

    def get_infos(self, callback):
        script = f'getPlayerInfos();'
        self.webview.evaluate_javascript(
            script,
            -1,
            cancellable=None,
            source_uri=None,
            callback=self.on_infos_return,
            user_data=callback
        )

    def on_infos_return(self, webview, result, callback):
        try:
            js_value = webview.evaluate_javascript_finish(result)
        except GLib.Error as e:
            print("JavaScript evaluation error:", e)
            return

        res = js_value.to_string().split(',')

        if res[0] == '':
            return

        current_time = round(float(res[0]))
        self.current_position = current_time
        duration = round(float(res[1]))
        self.duration = duration
        status = int(res[2])

        self.status = status

        callback(PlayerInfos(current_time = current_time, duration = duration, status = status))

    def toggle(self):
        if self.status == PlayerState.PAUSED:
            self.play()
        elif self.status == PlayerState.PLAYING:
            self.pause()

        self.mpris_adapter.on_playpause()

    def play(self):
        self.webview.evaluate_javascript(
            'player.playVideo();',
            -1,
            cancellable=None,
            source_uri=None,
            callback=None,
            user_data=None
        )

        self.status = PlayerState.PLAYING

        self.mpris_adapter.on_playpause()

    def pause(self):
        self.webview.evaluate_javascript(
            'player.pauseVideo();',
            -1,
            cancellable=None,
            source_uri=None,
            callback=None,
            user_data=None
        )

        self.status = PlayerState.PAUSED

        self.mpris_adapter.on_playpause()

    def stop(self):
        self.webview.evaluate_javascript(
            'player.stopVideo();',
            -1,
            cancellable=None,
            source_uri=None,
            callback=self.on_js_done,
            user_data=None
        )

        self.status = PlayerState.UNSTARTED

    def play_song(self, song):
        self.mpris_server.unpublish()
        self.mpris_server.publish()
        self.mpris_adapter.emit_all()
        self.mpris_adapter.on_playback()

        self.webview.evaluate_javascript(
            "navigator.mediaSession.setActionHandler('play', null);",
            -1,
            cancellable=None,
            source_uri=None,
            callback=self.on_js_done,
            user_data=None
        )

        self.webview.evaluate_javascript(
            "navigator.mediaSession.setActionHandler('pause', null);",
            -1,
            cancellable=None,
            source_uri=None,
            callback=self.on_js_done,
            user_data=None
        )

        script = f'loadSingleSong("{song.id}")'
        self.webview.evaluate_javascript(
            script,
            -1,
            cancellable=None,
            source_uri=None,
            callback=self.on_js_done,
            user_data=None
        )

    def on_js_done(self, webview, result, user_data):
        try:
            js_value = webview.evaluate_javascript_finish(result)
        except GLib.Error as e:
            print("JavaScript evaluation error:", e)
            return
