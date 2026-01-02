"""Job Class that runs every sunday to update the Q101 Spotify Playlist."""

import asyncio
from functools import cached_property

# TODO: Base Job class for email confirmation/home assisant notification and timing
from smart_home.utils.logging import get_logger
from smart_home.wrappers.online_radio_box.online_radio_box import OnlineRadioBox
from smart_home.wrappers.online_radio_box.online_radio_box_schemas import Song
from smart_home.wrappers.spotify.spotify import SpotifyWrapper
from smart_home.wrappers.spotify.spotify_schemas import (
    SpotifyCreatePlaylist,
    SpotifyPlaylist,
)

log = get_logger()

DEFAULT_SONGS = {
    Song(artist="warren zevon", title="lawyers, guns, and money"),
    Song(artist="the band", title="atlantic city"),
}


class Q101ToSpotify:
    """Q101 to Spotify Playlist Job."""

    def __init__(self, radio_station: str = "wkqx") -> None:
        """Init method.

        Args:
            radio_station (str, optional): Radio station. Defaults to "wkqx".
        """
        self.radio_station = radio_station

    @cached_property
    def wkqx_wrapper(self) -> OnlineRadioBox:
        """WKQX wrapper.

        Returns:
            OnlineRadioBox: OnlineRadioBox wrapper
        """
        return OnlineRadioBox(radio_station=self.radio_station)

    @cached_property
    def spotify_wrapper(self) -> SpotifyWrapper:
        """Spotify Wrapper.

        Returns:
            SpotifyWrapper: Spotify wrapper
        """
        return SpotifyWrapper()

    async def create_spotify_playlist(self) -> SpotifyPlaylist:
        """Create 101.1 Spotify Playlist.

        Returns:
            SpotifyPlaylist: Q101 Spotify Playlist.
        """
        playlist = SpotifyCreatePlaylist(
            name="101.1 WKQX Chicago",
            description=(
                "Replica of what 101.1 WKQX Chicago has played in the last week. "
                "Updates every Sunday. https://github.com/culpgrant/smart_home"
            ),
        )
        return await self.spotify_wrapper.create_playlist(playlist)

    async def run(self) -> None:
        """Main method to invoke.

        Webscrape all 7 days of previous plays.
        Create the playlist
        Search spotify for all the tracks
        Clear existing playlists tracks
        Add new tracks to playlist

        Returns:
            None: None
        """
        log.info("Getting previous 7 days of WKQX")
        log.info("Creating/Ensuring Spotify Playlist is created.")
        radio_songs, spotify_playlist = await asyncio.gather(
            self.wkqx_wrapper.get_all_songs_previous_7_days(),
            self.create_spotify_playlist(),
        )

        radio_songs = radio_songs.union(DEFAULT_SONGS)

        log.info(f"Got {len(radio_songs)} songs from Online Radio Box")

        # TODO: This needs multiprocessing
        # Add all songs to a set, to make 1 request to add songs to playlist
        spotify_song_uris: set[str] = set()
        for radio_song in radio_songs:
            spotify_song = await self.spotify_wrapper.search_track(
                title=radio_song.title, artist=radio_song.artist
            )
            if not spotify_song:
                continue
            spotify_song_uris.add(spotify_song.uri)

        log.info("Clearing out existing songs on playlist")
        await self.spotify_wrapper.clear_playlist_tracks(
            playlist_id=spotify_playlist.id
        )

        await self.spotify_wrapper.add_song_to_playlist(
            playlist_id=spotify_playlist.id, track_uri=list(spotify_song_uris)
        )
        return None


if __name__ == "__main__":
    asyncio.run(Q101ToSpotify().run())
