from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from smart_home.wrappers.spotify.schemas import (
    SpotifyCreatePlaylist,
    SpotifyPlaylist,
    SpotifyUser,
)
from smart_home.wrappers.spotify.spotify import BaseAPI, SpotifyAuth, SpotifyWrapper


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
