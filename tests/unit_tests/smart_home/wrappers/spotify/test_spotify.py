from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from smart_home.wrappers.spotify.spotify import BaseAPI, SpotifyAuth, SpotifyWrapper
from smart_home.wrappers.spotify.spotify_schemas import (
    SpotifyCreatePlaylist,
    SpotifyPlaylist,
    SpotifyTrack,
    SpotifyUser,
)


@pytest.fixture
def fake_auth_wrapper() -> SpotifyAuth:
    return SpotifyAuth(client_id="fake_client_id")


@patch.dict("os.environ", {"SPOTIFY_REFRESH_TOKEN": "fake_token"})
def test_auth_refresh_token(fake_auth_wrapper: SpotifyAuth):
    result = fake_auth_wrapper.refresh_token
    assert result == "fake_token"


@patch.dict("os.environ", {"SPOTIFY_CLIENT_SECRET": "fake_token"})
def test_auth_client_secret(fake_auth_wrapper: SpotifyAuth):
    result = fake_auth_wrapper.client_secret
    assert result == "fake_token"


async def test_headers(fake_auth_wrapper: SpotifyAuth):
    result = await fake_auth_wrapper._headers()  # pyright: ignore[reportPrivateUsage]
    assert result == {}


@patch(
    "smart_home.wrappers.spotify.spotify.SpotifyAuth.client_secret",
    new_callable=PropertyMock,
)
@patch.object(BaseAPI, "post", new_callable=AsyncMock)
async def test_auth_authorization_call_authorization_code(
    mock_base_api: PropertyMock,
    mock_client_secret: AsyncMock,
):
    # Setup Mocks
    mock_client_secret.return_value = "mock_client_secret"
    mock_base_api.return_value = {"code": "fake_return_code"}

    # Cant use fixture because of mocks
    fake_wrapper = SpotifyAuth(client_id="asd")
    result = await fake_wrapper._authorization_call(  # pyright: ignore[reportPrivateUsage]
        code="fake_code",
        grant_type="authorization_code",
    )
    data = {
        "grant_type": "authorization_code",
        "redirect_uri": "http://127.0.0.1:8080/callback",
        "code": "fake_code",
    }
    headers = {
        "Authorization": "Basic YXNkOm1vY2tfY2xpZW50X3NlY3JldA==",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    mock_base_api.assert_called_once_with("api/token", data=data, headers=headers)
    assert result == {"code": "fake_return_code"}


@patch(
    "smart_home.wrappers.spotify.spotify.SpotifyAuth.client_secret",
    new_callable=PropertyMock,
)
@patch.object(BaseAPI, "post", new_callable=AsyncMock)
async def test_auth_authorization_call_refresh_token(
    mock_base_api: PropertyMock,
    mock_client_secret: AsyncMock,
):
    # Setup Mocks
    mock_client_secret.return_value = "mock_client_secret"
    mock_base_api.return_value = {"code": "fake_return_code"}

    # Cant use fixture because of mocks
    fake_wrapper = SpotifyAuth(client_id="asd")
    result = await fake_wrapper._authorization_call(  # pyright: ignore[reportPrivateUsage]
        code="fake_code",
        grant_type="refresh_token",
    )
    data = {
        "grant_type": "refresh_token",
        "redirect_uri": "http://127.0.0.1:8080/callback",
        "refresh_token": "fake_code",
    }
    headers = {
        "Authorization": "Basic YXNkOm1vY2tfY2xpZW50X3NlY3JldA==",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    mock_base_api.assert_called_once_with("api/token", data=data, headers=headers)
    assert result == {"code": "fake_return_code"}


@patch.dict("os.environ", {"SPOTIFY_REFRESH_TOKEN": "fake_token"})
@patch("smart_home.wrappers.spotify.spotify.time.time")
@patch.object(SpotifyAuth, "_authorization_call", new_callable=AsyncMock)
async def test__refresh_access_token_success(
    mock_authorization_call: AsyncMock, mock_time: MagicMock
):
    mock_authorization_call.return_value = {
        "access_token": "mock_value",
        "expires_in": 3600,
    }
    mock_time.return_value = 100
    # Cant use fixture because of mocks
    fake_wrapper = SpotifyAuth(client_id="asd")
    await fake_wrapper._refresh_access_token()  # pyright: ignore[reportPrivateUsage]

    # Test the instance attributes are updated
    assert fake_wrapper.access_token == "mock_value"
    assert fake_wrapper.access_token_expires_at == 3700


@patch.dict("os.environ", {"SPOTIFY_REFRESH_TOKEN": "fake_token"})
@patch.object(SpotifyAuth, "_authorization_call", new_callable=AsyncMock)
async def test__refresh_access_token_failed(mock_authorization_call: AsyncMock):
    mock_authorization_call.return_value = {"unexpected_return": "unexpected_return"}
    # Cant use fixture because of mocks
    fake_wrapper = SpotifyAuth(client_id="asd")
    with pytest.raises(ValueError, match="Unable to get the access") as exc:
        await fake_wrapper._refresh_access_token()  # pyright: ignore[reportPrivateUsage]

    assert "Unable to get the access token or when the token expires." in str(exc.value)

    # Test the instance attributes are updated
    assert fake_wrapper.access_token == ""
    assert fake_wrapper.access_token_expires_at == 0


@patch("smart_home.wrappers.spotify.spotify.time.time")
def test_is_token_expired_false(mock_time: MagicMock, fake_auth_wrapper: SpotifyAuth):
    mock_time.return_value = 90
    fake_auth_wrapper.access_token_expires_at = 100

    result = fake_auth_wrapper._is_token_expired  # pyright: ignore[reportPrivateUsage]
    assert result is False


@patch("smart_home.wrappers.spotify.spotify.time.time")
def test_is_token_expired_true(mock_time: MagicMock, fake_auth_wrapper: SpotifyAuth):
    mock_time.return_value = 190
    fake_auth_wrapper.access_token_expires_at = 100

    result = fake_auth_wrapper._is_token_expired  # pyright: ignore[reportPrivateUsage]
    assert result is True


@patch.object(SpotifyAuth, "_refresh_access_token", new_callable=AsyncMock)
async def test_get_access_token_requests(
    mock_refresh_token: AsyncMock, fake_auth_wrapper: SpotifyAuth
):
    mock_refresh_token.return_value = "mock_token"

    result = await fake_auth_wrapper.get_access_token()

    assert result == "mock_token"
    mock_refresh_token.assert_called_once()


@patch.object(SpotifyAuth, "_is_token_expired", new_callable=PropertyMock)
@patch.object(SpotifyAuth, "_refresh_access_token", new_callable=AsyncMock)
async def test_get_access_token_cache(
    mock_refresh_token: AsyncMock,
    mock_token_expired: PropertyMock,
    fake_auth_wrapper: SpotifyAuth,
):
    mock_token_expired.return_value = False
    fake_auth_wrapper.access_token = "mock_token"

    result = await fake_auth_wrapper.get_access_token()

    assert result == "mock_token"
    mock_refresh_token.assert_not_called()


@patch.object(SpotifyAuth, "get_access_token", new_callable=AsyncMock)
async def test_auth_headers(
    mock_get_access_token: AsyncMock, fake_auth_wrapper: SpotifyAuth
):
    mock_get_access_token.return_value = "Mock Token"
    # fake_wrapper = SpotifyAuth(client_id="asd")

    result = await fake_auth_wrapper._auth_headers()  # pyright: ignore[reportPrivateUsage]
    assert result == {"Authorization": "Bearer Mock Token"}


def test_build_auth_url(fake_auth_wrapper: SpotifyAuth):
    result = fake_auth_wrapper._build_auth_url()  # pyright: ignore[reportPrivateUsage]
    assert (
        result
        == "https://accounts.spotify.com/authorize?client_id=fake_client_id&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080%2Fcallback&scope=playlist-modify-public"
    )


@pytest.fixture
def fake_wrapper() -> SpotifyWrapper:
    return SpotifyWrapper(client_id="fake_id")


@pytest.fixture
def fake_user() -> SpotifyUser:
    return SpotifyUser.model_construct(id="test_id", display_name="test name")


@pytest.fixture
def fake_create_playlist() -> SpotifyCreatePlaylist:
    return SpotifyCreatePlaylist.model_construct(
        name="fake playlist", description="pytest"
    )


@pytest.fixture
def fake_playlist() -> SpotifyPlaylist:
    return SpotifyPlaylist.model_construct(
        id="asdlfkjhwe",
        name="fake playlist",
        description="pytest",
        href="url",
        collaborative=False,
        external_urls={"href": "url"},
        owner=SpotifyUser.model_construct(
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


# TODO: Remove all pydantic.model_construct


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


async def fake_empty_gen(self: SpotifyWrapper) -> AsyncGenerator[None]:
    if False:
        yield


async def fake_match_gen(
    self: SpotifyWrapper,
) -> AsyncGenerator[SpotifyPlaylist]:
    yield SpotifyPlaylist.model_construct(
        id="asdlfkjhwe",
        name="fake playlist",
        description="pytest",
        href="url",
        collaborative=False,
        external_urls={"href": "url"},
        owner=SpotifyUser.model_construct(
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


@patch("smart_home.wrappers.spotify.spotify.BaseAPI.__init__")
@patch("smart_home.wrappers.spotify.spotify.SpotifyAuth")
def test_wrapper_init(mock_spotify_auth: MagicMock, mock_base_api: MagicMock):
    result = SpotifyWrapper(client_id="fake_id")

    assert result.client_id == "fake_id"
    mock_spotify_auth.assert_called_once_with(client_id="fake_id")
    mock_base_api.assert_called_once_with("https://api.spotify.com/v1")


@patch.object(SpotifyAuth, "get_access_token")
async def test_wrapper_headers(mock_token: MagicMock, fake_wrapper: SpotifyWrapper):
    mock_token.return_value = "fake_token"
    result = await fake_wrapper._headers()  # pyright: ignore[reportPrivateUsage]
    mock_token.assert_called_once_with()
    assert result == {
        "Authorization": "Bearer fake_token",
        "Accept": "application/json",
    }


@patch.object(BaseAPI, "get")
async def test_get_current_user_first(
    mock_get: AsyncMock, fake_wrapper: SpotifyWrapper, fake_user: SpotifyUser
):
    assert fake_wrapper._current_user is None  # pyright: ignore[reportPrivateUsage]
    mock_get.return_value = fake_user
    result = await fake_wrapper.get_current_user()
    assert isinstance(result, SpotifyUser)
    assert result == fake_user
    assert fake_wrapper._current_user == fake_user  # pyright: ignore[reportPrivateUsage]
    mock_get.assert_called_once_with("me")


@patch.object(BaseAPI, "get")
async def test_get_current_user_cache(
    mock_get: AsyncMock, fake_wrapper: SpotifyWrapper, fake_user: SpotifyUser
):
    fake_wrapper._current_user = fake_user  # pyright: ignore[reportPrivateUsage]

    result = await fake_wrapper.get_current_user()

    assert isinstance(result, SpotifyUser)
    assert result == fake_user
    assert fake_wrapper._current_user == fake_user  # pyright: ignore[reportPrivateUsage]
    mock_get.assert_not_called()


@patch.object(BaseAPI, "post")
@patch.object(SpotifyWrapper, "find_playlist_by_name")
async def test_create_playlist_create(
    mock_find_playlist: AsyncMock,
    mock_post: AsyncMock,
    fake_wrapper: SpotifyWrapper,
    fake_create_playlist: SpotifyCreatePlaylist,
    fake_playlist: SpotifyPlaylist,
):
    mock_find_playlist.return_value = None
    fake_playlist_data = fake_playlist.model_dump_json()

    mock_post.return_value = fake_playlist

    result = await fake_wrapper.create_playlist(fake_create_playlist)

    assert result == SpotifyPlaylist.model_validate_json(fake_playlist_data)
    mock_post.assert_called_once_with(
        "me/playlists", json=fake_create_playlist.model_dump()
    )


@patch.object(BaseAPI, "post")
@patch.object(SpotifyWrapper, "find_playlist_by_name")
async def test_create_playlist_exists(
    mock_find_playlist: AsyncMock,
    mock_post: AsyncMock,
    fake_wrapper: SpotifyWrapper,
    fake_create_playlist: SpotifyCreatePlaylist,
    fake_playlist: SpotifyPlaylist,
):
    mock_find_playlist.return_value = fake_playlist

    result = await fake_wrapper.create_playlist(fake_create_playlist)

    assert result == fake_playlist
    mock_post.assert_not_called()


@patch.object(BaseAPI, "get")
async def test_iter_playlists_single_page(
    mock_get: AsyncMock, fake_wrapper: SpotifyWrapper, fake_playlist: SpotifyPlaylist
):
    mock_get.return_value = {
        "items": [
            fake_playlist,
            fake_playlist,
        ],
        "next": None,
    }
    playlists = [playlist async for playlist in fake_wrapper.iter_playlists()]

    assert len(playlists) == 2
    mock_get.assert_called_once_with("me/playlists")


@patch.object(BaseAPI, "get")
async def test_iter_playlists_multi_page(
    mock_get: AsyncMock, fake_wrapper: SpotifyWrapper, fake_playlist: SpotifyPlaylist
):
    page1: dict[str, Any] = {
        "items": [
            fake_playlist,
            fake_playlist,
        ],
        "next": "https://api.spotify.com/v1/me/playlists?offset=2",
    }
    page2: dict[str, Any] = {
        "items": [
            fake_playlist,
        ],
        "next": None,
    }
    mock_get.side_effect = [page1, page2]
    playlists = [playlist async for playlist in fake_wrapper.iter_playlists()]

    assert len(playlists) == 3
    assert mock_get.call_count == 2
    assert mock_get.call_args_list[0].args[0] == "me/playlists"
    assert (
        mock_get.call_args_list[1].args[0]
        == "https://api.spotify.com/v1/me/playlists?offset=2"
    )


@patch.object(SpotifyWrapper, "iter_playlists", new=fake_match_gen)
async def test_find_playlist_by_name(
    fake_wrapper: SpotifyWrapper, fake_playlist: SpotifyPlaylist
):

    result = await fake_wrapper.find_playlist_by_name(name="fAKe playlist")

    assert result == fake_playlist


@patch.object(SpotifyWrapper, "iter_playlists", new=fake_match_gen)
async def test_find_playlist_by_name_not_found(fake_wrapper: SpotifyWrapper):

    result = await fake_wrapper.find_playlist_by_name(name="fake_playlist")

    assert result is None


@patch.object(BaseAPI, "get")
async def test_search_track(
    mock_get: AsyncMock, fake_track: SpotifyTrack, fake_wrapper: SpotifyWrapper
):
    fake_track_data = fake_track.model_dump()
    mock_get.return_value = {
        "tracks": {
            "href": "https://api.spotify.com/v1/search?offset=0&limit=1&query=track%3ALawyers%2C%20Guns%20and%20Money%20artist%3AWarren%20and%20Zevon&type=track&market=US",
            "limit": 1,
            "next": "https://api.spotify.com/v1/search?offset=1&limit=1&query=track%3ALawyers%2C%20Guns%20and%20Money%20artist%3AWarren%20and%20Zevon&type=track&market=US",
            "offset": 0,
            "previous": None,
            "total": 17,
            "items": [fake_track_data],
        }
    }
    result = await fake_wrapper.search_track(title="song title", artist="song artist")

    mock_get.assert_called_once_with(
        "search",
        params={
            "q": "track:song title artist:song artist",
            "type": "track",
            "market": "US",
            "limit": 1,
            "offset": 0,
        },
    )
    assert result == fake_track


@patch.object(BaseAPI, "get")
async def test_search_track_no_results(
    mock_get: AsyncMock, fake_wrapper: SpotifyWrapper
):
    mock_get.return_value = {
        "tracks": {
            "href": "https://api.spotify.com/v1/search?offset=0&limit=1&query=track%3ALawyers%2C%20Guns%20and%20Money%20artist%3AWarren%20and%20Zevon&type=track&market=US",
            "limit": 1,
            "next": "https://api.spotify.com/v1/search?offset=1&limit=1&query=track%3ALawyers%2C%20Guns%20and%20Money%20artist%3AWarren%20and%20Zevon&type=track&market=US",
            "offset": 0,
            "previous": None,
            "total": 17,
            "items": [],
        }
    }
    result = await fake_wrapper.search_track(title="song title", artist="song artist")

    mock_get.assert_called_once_with(
        "search",
        params={
            "q": "track:song title artist:song artist",
            "type": "track",
            "market": "US",
            "limit": 1,
            "offset": 0,
        },
    )
    assert result is None


@patch("smart_home.wrappers.spotify.spotify.chunk_list")
@patch.object(BaseAPI, "post")
async def test_add_song_to_playlist(
    mock_post: AsyncMock, mock_chunk_list: MagicMock, fake_wrapper: SpotifyWrapper
):
    mock_chunk_list.return_value = [
        ["track_1", "track_2"],
        ["track_3", "track_4"],
        ["track_5", "track_6"],
    ]
    mock_post.side_effect = [
        {"snapshot_id": "abc"},
        {"snapshot_id": "abc1"},
        {"snapshot_id": "abc2"},
    ]

    result = await fake_wrapper.add_song_to_playlist(
        playlist_id="asda", track_uri=["fake_tracks"]
    )

    assert result == [
        {"snapshot_id": "abc"},
        {"snapshot_id": "abc1"},
        {"snapshot_id": "abc2"},
    ]
    mock_chunk_list.assert_called_once_with(["fake_tracks"], size=100)
    assert mock_post.call_count == 3
    mock_post.assert_called_with(
        path="playlists/asda/tracks",
        json={
            "uris": ["track_5", "track_6"],
        },
    )


@patch.object(BaseAPI, "post")
async def test_add_song_to_playlist_one_song(
    mock_post: AsyncMock, fake_wrapper: SpotifyWrapper
):
    mock_post.return_value = {"snapshot_id": "abc"}

    result = await fake_wrapper.add_song_to_playlist(
        playlist_id="asda", track_uri="fake_track"
    )

    assert result == [
        {"snapshot_id": "abc"},
    ]
    assert mock_post.call_count == 1
    mock_post.assert_called_with(
        path="playlists/asda/tracks",
        json={
            "uris": ["fake_track"],
        },
    )


@patch.object(BaseAPI, "put")
async def test_clear_playlist_tracks(mock_put: AsyncMock, fake_wrapper: SpotifyWrapper):
    mock_put.return_value = {"snapshot_id": "abc"}

    result = await fake_wrapper.clear_playlist_tracks(playlist_id="asdfas")

    assert result == {"snapshot_id": "abc"}
    mock_put.assert_called_once_with(path="playlists/asdfas/tracks", json={"uris": []})
