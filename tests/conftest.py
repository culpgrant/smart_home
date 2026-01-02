import pytest

from smart_home.wrappers.spotify.spotify_schemas import (
    SpotifyPlaylist,
    SpotifyTrack,
    SpotifyUser,
)


@pytest.fixture
def fake_playlist() -> SpotifyPlaylist:
    return SpotifyPlaylist(
        id="asdlfkjhwe",
        name="fake playlist",
        description="pytest",
        href="url",
        collaborative=False,
        external_urls={"href": "url"},
        owner=SpotifyUser(
            id="asdf65",
            display_name="asd",
            external_urls=None,
            followers=None,
            href=None,
            images=None,
        ),
        public=False,
        snapshot_id="adsfads",
        tracks={"total_tracks": 456},
        type="playlist",
        uri="asdfas",
    )


@pytest.fixture
def fake_track() -> SpotifyTrack:
    return SpotifyTrack(
        id="asdfjasdfklj",
        name="spotify_track",
        uri="Spotify:Track:asdfjasdfklj",
        disc_number=3,
        duration_ms=96876,
        explicit=False,
        href="https:link",
        is_playable=True,
        popularity=45,
        type="track",
        track_number=4,
        is_local=True,
    )
