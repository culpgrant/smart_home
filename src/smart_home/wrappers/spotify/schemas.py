"""Pydantic models for Spotify."""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from smart_home.wrappers.pydantic.pydantic import normalize_empty_string


class SpotifyBaseModel(BaseModel):
    """Base Model for all Spotify Data Attributes."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def _normalize_empty_strings(cls, data: Any) -> Any:
        """
        Normalize empty strings.

        Arguments:
            data: Any - Data to normalize

        Returns:
            Normalized data
        """
        return normalize_empty_string(data)


class SpotifyUser(SpotifyBaseModel):
    """Spotify User Data Model."""
    id: str = Field(description="The Spotify user ID")
    display_name: str | None = Field(description="User Name displayed in the app")
    external_urls: dict[str, str] | None = Field(
        description="dictionary of urls to the user profile", default=None
    )
    followers: dict[str, Any] | None = Field(
        description="number of followers and href", default=None
    )
    href: str | None = Field(description="api url of the user", default=None)
    images: list[dict[str, Any]] | None = Field(
        description="list of the images and urls to them", default=None
    )


class SpotifyPlaylist(SpotifyBaseModel):
    """Spotify Playlist Model, returning data from Spotify."""
    id: str = Field(description="Paylist ID")
    name: str = Field(description="Name of the playlist")
    href: str = Field(description="API URL to playlist")
    description: str | None = Field(description="Playlist description", default=None)
    collaborative: bool = Field(
        description="If the playlist can be added to by other people"
    )
    external_urls: dict[str, str] = Field(description="Spotify url for the playlist")
    owner: SpotifyUser = Field(description="Who owns the playlist")
    # primary_color: #TODO: Need to do this
    public: bool = Field(description="Is the profile public to other users to see")
    snapshot_id: str = Field(description="Not sure what this is referring to")
    tracks: dict[str, Any] = Field(
        description="Shows total tracks and a link to the tracks"
    )
    type: str = Field(description="type is playlist")
    uri: str = Field(description="Internal api id for the playlist")
    images: list[dict[str, Any]] | None = Field(
        description="information on the images stored for the playlist cover",
        default=None,
    )


class SpotifyCreatePlaylist(SpotifyBaseModel):
    """Spotify Playlist Model to create playlists."""
    name: str = Field(description="Name for the playlist")
    description: str = Field(
        description="Description to give the playlist",
        default="Created through Spotify Wrapper",
    )
    public: bool = Field(
        description="If playlist should be on public users profile", default=True
    )
    collaborative: bool = Field(
        description="Allow other people to edit playlist", default=False
    )
