from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from selectolax.parser import HTMLParser

from smart_home.wrappers.base_webscraping import BaseAPI, BaseWebScrapping


@pytest.fixture
def mock_base_webscraping() -> BaseWebScrapping:
    return BaseWebScrapping(base_url="mock_url", timeout=12)


@patch("smart_home.wrappers.base_webscraping.BaseAPI.__init__")
def test_base_webscraping(mock_base_api: MagicMock):

    _ = BaseWebScrapping(base_url="mock_url", timeout=12)
    mock_base_api.assert_called_once_with("mock_url", timeout=12, follow_redirects=True)


async def test_headers(mock_base_webscraping: BaseWebScrapping):
    result = await mock_base_webscraping._headers()  # pyright: ignore[reportPrivateUsage]

    assert result == {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    }


@patch("smart_home.wrappers.base_webscraping.HTMLParser", spec=HTMLParser)
@patch.object(BaseAPI, "get_text")
async def test_get_html(
    mock_get_text: AsyncMock,
    mock_html_parser: MagicMock,
    mock_base_webscraping: BaseWebScrapping,
):
    fake_html = """
        <table class="tablelist-schedule">
        <tr>
            <td><span>Live</span></td>
            <td><a class="ajax" href="/track/111/">Blink-182 - Always</a></td>
        </tr>
        <tr>
            <td><span>10:00</span></td>
            <td><a class="ajax" href="/track/222/">Muse - Starlight</a></td>
        </tr>
        </table>
"""
    mock_get_text.return_value = fake_html
    result = await mock_base_webscraping.get_html(path="asdf")
    mock_get_text.assert_called_once_with(path="asdf")
    mock_html_parser.assert_called_once_with(fake_html)

    assert isinstance(result, HTMLParser)
