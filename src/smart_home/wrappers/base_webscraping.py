"""Base Webscrapping Class for helper methods to webscrape."""

from selectolax.parser import HTMLParser

from smart_home.wrappers.base_api_wrapper import BaseAPI


class BaseWebScrapping(BaseAPI):
    """Base Web Scrapping Class."""

    def __init__(self, base_url: str, *, timeout: float = 10) -> None:
        """
        Init method.

        Args:
            base_url (str): base url to webscrape
            timeout (float, optional): timeout in seconds. Defaults to 10.
        """
        super().__init__(base_url, timeout=timeout, follow_redirects=True)

    async def _headers(self) -> dict[str, str]:
        """
        Headers to simulate a webrowser.

        Returns:
            dict[str, str]: Headers
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        }

    async def get_html(self, path: str) -> HTMLParser:
        """Get HTML Parser for an HTML Path.

        Args:
            path (str): HTML Path

        Returns:
            HTMLParser: Selectolax HTML Parser
        """
        html_text = await self.get_text(path=path)
        return HTMLParser(html_text)
