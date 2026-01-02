from unittest.mock import AsyncMock

import pytest

from smart_home.jobs.q101_spotify import Q101ToSpotify
from smart_home.wrappers.online_radio_box.online_radio_box_schemas import Song
from smart_home.wrappers.spotify.spotify_schemas import (
    SpotifyCreatePlaylist,
    SpotifyPlaylist,
    SpotifyTrack,
)


@pytest.fixture
def mock_job_class() -> Q101ToSpotify:
    return Q101ToSpotify()


async def test_create_spotify_playlist(
    fake_playlist: SpotifyPlaylist,
    mock_job_class: Q101ToSpotify,
):
    mock_job_class.spotify_wrapper.create_playlist = AsyncMock(
        return_value=fake_playlist
    )
    result = await mock_job_class.create_spotify_playlist()

    mock_job_class.spotify_wrapper.create_playlist.assert_called_once_with(
        SpotifyCreatePlaylist(
            name="101.1 WKQX Chicago",
            description=(
                "Replica of what 101.1 WKQX Chicago has played in the last week. "
                "Updates every Sunday. https://github.com/culpgrant/smart_home"
            ),
        )
    )
    assert result == fake_playlist


async def test_run(
    fake_playlist: SpotifyPlaylist,
    fake_track: SpotifyTrack,
    mock_job_class: Q101ToSpotify,
):
    fake_songs = {Song(artist="mock_artist", title="mock_title")}
    mock_job_class.wkqx_wrapper.get_all_songs_previous_7_days = AsyncMock(
        return_value=fake_songs
    )
    mock_job_class.create_spotify_playlist = AsyncMock(return_value=fake_playlist)
    mock_job_class.spotify_wrapper.search_track = AsyncMock(
        side_effect=[fake_track, fake_track, fake_track]
    )
    mock_job_class.spotify_wrapper.clear_playlist_tracks = AsyncMock(
        return_value={"snapshot_id": "asd"}
    )
    mock_job_class.spotify_wrapper.add_song_to_playlist = AsyncMock(
        return_value=[{"snapshot_id": "asd"}]
    )

    result = await mock_job_class.run()

    mock_job_class.wkqx_wrapper.get_all_songs_previous_7_days.assert_called_once()
    mock_job_class.create_spotify_playlist.assert_called_once()
    mock_job_class.spotify_wrapper.clear_playlist_tracks.assert_called_once_with(
        playlist_id="asdlfkjhwe"
    )
    mock_job_class.spotify_wrapper.add_song_to_playlist.assert_called_once_with(
        playlist_id="asdlfkjhwe", track_uri=["Spotify:Track:asdfjasdfklj"]
    )

    assert result is None
