"""Spotify Wrapper Async."""

import asyncio
import base64
import os
import time
from collections.abc import AsyncIterator
from functools import cached_property
from typing import Any, Literal
from urllib import parse

from smart_home.utils.logging import get_logger
from smart_home.wrappers.base_api_wrapper import BaseAPI
from smart_home.wrappers.spotify import schemas

DEFAULT_SCOPES = ["playlist-modify-public"]
log = get_logger()


class SpotifyAuth(BaseAPI):
    """
    Authentication for Spotify.

    Args:
        BaseAPI (BaseAPI): SubClass to BaseAPI
    """

    def __init__(
        self,
        client_id: str,
        scope: list[str] | None = None,
        redirect_uri: str = "http://127.0.0.1:8080/callback",
        base_url: str = "https://accounts.spotify.com",
    ) -> None:
        """
        Init class for Auth Spotify.

        Args:
            client_id (str): App client id registered with Spotify
            scope (list[str] | None, optional): Scope of permissions given.
                Defaults to None.
            redirect_uri (str, optional): Redirect uri has to match what is regerested
                with Spotify. Defaults to "http://127.0.0.1:8080/callback".
            base_url (str, optional): Base URL for auth calls. Defaults to "https://accounts.spotify.com".
        """
        super().__init__(base_url)
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.base_url = base_url
        self.access_token: str = ""
        self.access_token_expires_at: float = 0
        if scope is None:
            self.scope = DEFAULT_SCOPES.copy()

    @cached_property
    def refresh_token(self) -> str:
        """
        Long term refresh token stored in environment variables.

        Returns:
            str: Refresh Token
        """
        return str(os.environ["SPOTIFY_REFRESH_TOKEN"])

    @cached_property
    def client_secret(self) -> str:
        """
        Permanent Spotify Client Secret from Spotify.

        Returns:
            str: Client Secret
        """
        log.info("--- RUNNING REAL DATA_SOURCE ---")
        return str(os.environ["SPOTIFY_CLIENT_SECRET"])

    async def _headers(self) -> dict[str, str]:
        """
        Default Headers.

        Returns:
            dict[str, str]: Default Headers.
        """
        return {}

    async def _authorization_call(
        self, code: str, grant_type: Literal["authorization_code", "refresh_token"]
    ) -> dict[Any, Any]:
        """
        Call to get an auth code or auth token.

        Args:
            code (str): Authorization Code or Refresh Token
            grant_type (Literal["authorization_code", "refresh_token"]):
                What type of token to get

        Returns:
            dict[Any, Any]: Result of API call
        """
        log.info(f"Requesting {grant_type} authentication code")
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        data = {
            "grant_type": grant_type,
            "redirect_uri": self.redirect_uri,
        }
        if grant_type == "authorization_code":
            data["code"] = code
        elif grant_type == "refresh_token":
            data["refresh_token"] = code
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        return await self.post("api/token", data=data, headers=headers)

    async def _refresh_access_token(self) -> str:
        """
        Gets access token and caches the values with automated refreshing when expires.

        Raises:
            ValueError: Unable to get the token.

        Returns:
            str: Access token to use in API calls.
        """
        data = await self._authorization_call(
            code=self.refresh_token, grant_type="refresh_token"
        )
        access_token = data.get("access_token")
        access_token_expires_in = data.get("expires_in")

        if not access_token or not access_token_expires_in:
            raise ValueError(
                "Unable to get the access token or when the token expires. "
                f"Data recieved from api call: {data}"
            )
        self.access_token = access_token
        self.access_token_expires_at = time.time() + access_token_expires_in
        return self.access_token

    @property
    def _is_token_expired(self) -> bool:
        """
        Is the access token expired.

        Returns:
            bool: True/False
        """
        return time.time() >= self.access_token_expires_at

    async def get_access_token(self) -> str:
        """
        Gets the current access token, requests a new one if expired or initial.

        Returns:
            str: Access Token
        """
        if not self.access_token or self._is_token_expired:
            log.info("Requesting access token")
            return await self._refresh_access_token()
        return self.access_token

    async def _auth_headers(self) -> dict[str, str]:
        """
        Headers that have Auth information.

        Returns:
            dict[str, str]: Headers
        """
        token = await self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def _build_auth_url(self) -> str:
        """
        One time url that must be invoked by a human to give access.
        Gives the autorization code for the user.

        Returns:
            str: url to be accessed
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scope),
        }
        return f"{self.base_url}/authorize?{parse.urlencode(params)}"


class SpotifyWrapper(BaseAPI):
    """Async Spotify Wrapper with methods to interact with Spotifys API.

    Args:
        BaseAPI (BaseAPI): BaseAPI
    """

    def __init__(
        self,
        base_url: str = "https://api.spotify.com/v1",
        client_id: str = "bc4c1fd27f3e463f8c2e5b4c65466f73",
    ) -> None:
        """Init.

        Args:
            base_url (str, optional): Base URL for API. Defaults to "https://api.spotify.com/v1".
            client_id (str, optional): Spotify API Client ID.
                Defaults to "bc4c1fd27f3e463f8c2e5b4c65466f73".
        """
        self.client_id = client_id
        self.auth = SpotifyAuth(client_id=self.client_id)

        # Internal state (caching)
        self._current_user: schemas.SpotifyUser | None = None
        self._user_lock = asyncio.Lock()
        super().__init__(base_url)

    async def _headers(self) -> dict[str, str]:
        """Create Headers for API call.

        Returns:
            dict[str, str]: API call headers
        """
        token = await self.auth.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    async def get_current_user(self) -> schemas.SpotifyUser:
        """Get the current user that is authenticating.

        Returns:
            schemas.SpotifyUser: Spotify User Pydantic model
        """
        # Lock to handle concurrent requests safely
        async with self._user_lock:
            if not self._current_user:
                log.info("Calling API to get current user")
                data = await self.get("me")
                self._current_user = schemas.SpotifyUser.model_validate(data)
        return self._current_user

    async def create_playlist(
        self, playlist: schemas.SpotifyCreatePlaylist
    ) -> schemas.SpotifyPlaylist:
        """Create a playlist within Spotify.

        Does not create a playlist if one already exists with the same name

        Args:
            playlist (schemas.SpotifyCreatePlaylist): _description_

        Returns:
            schemas.SpotifyPlaylist: _description_
        """
        log.info(f"Attempting to create playlist {playlist.name}")
        existing_playlist = await self.find_playlist_by_name(name=playlist.name)
        if existing_playlist:
            log.info(
                f"Playlist with name {playlist.name} already exists, not creating."
            )
            return existing_playlist
        new_playlist = await self.post("me/playlists", json=playlist.model_dump())
        return schemas.SpotifyPlaylist.model_validate(new_playlist)

    async def iter_playlists(self) -> AsyncIterator[schemas.SpotifyPlaylist]:
        """Iterate through all the playlist tied to a user.

        Yields:
            Iterator[AsyncIterator[schemas.SpotifyPlaylist]]: Pydantic Playlist
        """
        log.info("Getting all playlists on the user")
        url = "me/playlists"
        while url:
            data = await self.get(url)
            for item in data["items"]:
                yield schemas.SpotifyPlaylist.model_validate(item)
            url = data["next"]

    async def find_playlist_by_name(self, name: str) -> schemas.SpotifyPlaylist | None:
        """Find a playlist by name.

        Leverages the iterator to return once playlist is found immediately.
        There can be duplicate playlists on a user, this does not handle for that.

        Args:
            name (str): Playlist name

        Returns:
            schemas.SpotifyPlaylist | None: Spotify Playlist
        """
        async for playlist in self.iter_playlists():
            if playlist.name.lower() == name.lower():
                return playlist
        return None
