from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from selectolax.parser import HTMLParser

from smart_home.wrappers.online_radio_box.online_radio_box import (
    BaseWebScrapping,
    OnlineRadioBox,
)
from smart_home.wrappers.online_radio_box.online_radio_box_schemas import Song


@pytest.fixture
def mock_radio_box() -> OnlineRadioBox:
    return OnlineRadioBox(radio_station="mock")


async def fake_parse_song_gen(
    self: OnlineRadioBox,
    day_offset: int,
) -> AsyncGenerator[Song]:
    for song in [
        Song(artist="artist", title="title"),
        Song(artist="artist", title="title"),
    ]:
        yield song


@patch(
    "smart_home.wrappers.online_radio_box.online_radio_box.BaseWebScrapping.__init__"
)
def test_init(mock_base: MagicMock):
    OnlineRadioBox(radio_station="mock")
    mock_base.assert_called_once_with(
        base_url="https://onlineradiobox.com/us/mock/playlist",
        timeout=10,
    )


@patch.object(BaseWebScrapping, "get_html")
async def test__parse_song_table(
    mock_get_html: AsyncMock, mock_radio_box: OnlineRadioBox
):
    html = """
    <html>
      <body>
        <table class="tablelist-schedule">
          <tr>
            <td class="track_history_item">
              <a class="ajax">Warren Zevon - Lawyers, Guns and Money</a>
            </td>
            <td class="track_history_item">
              <a class="zzzz">Nonparsableclass</a>
            </td>
            <td class="track_history_item">
              <a class="ajax">Artist; Title</a>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    parser = HTMLParser(html)
    mock_get_html.return_value = parser

    results = [song async for song in mock_radio_box._parse_song_table(2)]  # pyright: ignore[reportPrivateUsage]

    assert len(results) == 1
    assert isinstance(results[0], Song)
    assert results[0].artist == "warren zevon"
    assert results[0].title == "lawyers, guns and money"
    mock_get_html.assert_called_once_with(path="2")


@patch.object(OnlineRadioBox, "_parse_song_table", new=fake_parse_song_gen)
async def test_get_songs_day(mock_radio_box: OnlineRadioBox):
    result = await mock_radio_box.get_songs_day(4)

    assert len(result) == 1
    assert result == {Song(artist="artist", title="title")}


@patch.object(OnlineRadioBox, "get_songs_day")
async def test_get_all_songs_previous_7_days(
    mock_get_songs_day: AsyncMock, mock_radio_box: OnlineRadioBox
):
    songs_return = [
        {Song(artist="artist", title="title")},
        {Song(artist="artist1", title="title1")},
        {Song(artist="artist", title="title")},
        {Song(artist="artist", title="title")},
        {Song(artist="artist", title="title")},
        {Song(artist="artist", title="title")},
        {Song(artist="artist2", title="title2")},
    ]
    mock_get_songs_day.side_effect = songs_return

    result = await mock_radio_box.get_all_songs_previous_7_days()

    assert result == {
        Song(artist="artist", title="title"),
        Song(artist="artist1", title="title1"),
        Song(artist="artist2", title="title2"),
    }
    assert mock_get_songs_day.call_count == 7
