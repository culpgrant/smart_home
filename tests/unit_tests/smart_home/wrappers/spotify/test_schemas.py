import pytest
from pydantic import ValidationError

from smart_home.wrappers.spotify.schemas import (
    SpotifyBaseModel,
    SpotifyCreatePlaylist,
    SpotifyPlaylist,
    SpotifyUser,
)


class _TestModel(SpotifyBaseModel):
    name: str | None
    count: int | None = None


def test_base_model():
    test = _TestModel(name="", count=1, extra_field="as")
    assert test.name is None
    assert test.count == 1
    assert not hasattr(test, "extra_field")

    # Test Frozen
    with pytest.raises(ValidationError):
        test.name = "changed"
