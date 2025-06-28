from musicology.backend import Player, PlayerState, PlayerMode
from musicology.data.constants import APP_ID

from gi.repository import GLib
from mpris_server.adapters import PlayState, MprisAdapter
from mpris_server.server import Server
from mpris_server.events import PlayerEventAdapter


class Adapter(MprisAdapter):
	def __init__(self, player: Player):
		super().__init__()
		self.player = player

	def get_desktop_entry(self) -> str:
		return APP_ID

	def get_uri_schemes(self) -> list:
		return []

	def get_mime_types(self) -> list:
		return []

	def can_quit(self) -> bool:
		return False

	def quit(self):
		pass

	def get_current_position(self) -> float:
		return self.player.current_position * 1_000_000

	def next(self):
		GLib.Thread.new(None, self.player.next_song)

	def previous(self):
		GLib.Thread.new(None, self.player.prev_song)

	def pause(self):
		self.player.pause()

	def resume(self):
		self.player.play()

	def stop(self):
	    # TODO: Implement queue clear
		self.player.pause()

	def play(self):
		pass

	def get_playstate(self) -> PlayState:
		if self.player.status == PlayerState.PAUSED:
			return PlayState.PAUSED
		return PlayState.PLAYING

	def seek(self, _time):
	    # TODO: implement seek
		return

	def is_repeating(self) -> bool:
		return self.player.mode == PlayerMode.SONG_LOOP

	def is_playlist(self) -> bool:
		return True

	def set_repeating(self, _val: bool):
		pass

	def set_loop_status(self, _val: str):
		pass

	def get_rate(self) -> float:
		return 1.0

	def set_rate(self, _val: float):
		pass

	def get_shuffle(self) -> bool:
		return False

	def set_shuffle(self, _val: bool):
		pass

	def get_art_url(self, _track):
		return ''

	def get_stream_title(self):
		return ''

	def get_volume(self):
		pass

	def set_volume(self, volume: float):
		pass

	def is_mute(self) -> bool:
		return False

	def can_go_next(self) -> bool:
		return True

	def can_go_previous(self) -> bool:
		return True

	def can_play(self) -> bool:
		return len(self.player.queue) > 0

	def can_pause(self) -> bool:
		return len(self.player.queue) > 0

	def can_seek(self) -> bool:
		return False

	def can_control(self) -> bool:
		return True

	def can_raise(self) -> bool:
		return False

	def set_raise(self, val: bool):
		pass

	def metadata(self) -> dict:
		song = self.player.queue_model.get_selected_item()
		if song:
			duration = self.player.duration
			return {
				'mpris:trackid': '/org/mpris/MediaPlayer2/musicology',
				'mpris:artUrl': song.thumbnail_uri,
				'mpris:length': duration * 1_000_000 if duration > 0 else None,
				'xesam:title': song.title,
				'xesam:artist': [song.artist.name]
			}

		return {'mpris:trackid': '/org/mpris/MediaPlayer2/TrackList/NoTrack'}


def init_mpris(player: object):
	mpris = Server('Musicology', adapter=Adapter(player))
	print(mpris)
	player.mpris_adapter = PlayerEventAdapter(root=mpris.root, player=mpris.player)
	player.mpris_server = mpris
	player.mpris_server.loop()

