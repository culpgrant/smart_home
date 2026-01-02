"""Online Radio Box Website Handler."""

import asyncio
from collections.abc import AsyncIterator

from smart_home.wrappers.base_webscraping import BaseWebScrapping
from smart_home.wrappers.online_radio_box.online_radio_box_schemas import Song


class OnlineRadioBox(BaseWebScrapping):
    """Wrapper for Online Radio Box Website."""

    def __init__(self, radio_station: str, timeout: float = 10) -> None:
        """
        Init method.

        Args:
            radio_station (str): Radio Station to webscrape.
            timeout (float, optional): Timeout in seconds. Defaults to 10.
        """
        super().__init__(
            base_url=f"https://onlineradiobox.com/us/{radio_station}/playlist",
            timeout=timeout,
        )

    async def _parse_song_table(self, day_offset: int) -> AsyncIterator[Song]:
        """
        Parse the song table and yield Song pydantic class.

        Args:
            day_offset (int): Day offset (0-6) to get the previous days plays.

        Yields:
            Iterator[AsyncIterator[Song]]: Pydantic Song instance.
        """
        web_page = await self.get_html(path=f"{day_offset}")
        for node in web_page.css("table.tablelist-schedule tr"):
            link = node.css_first("td.track_history_item a.ajax")
            if not link:
                continue

            text = link.text(strip=True)  # "Artist - Song"

            if " - " in text:
                artist, title = text.split(" - ", 1)
            else:
                continue

            yield Song(artist=artist, title=title)

    async def get_songs_day(self, day_offset: int) -> set[Song]:
        """Get a set of all the songs played for 1 day.

        Args:
            day_offset (int): Day offset to retrieve

        Returns:
            set[Song]: Set of Songs
        """
        songs: set[Song] = set()
        async for song in self._parse_song_table(day_offset):
            songs.add(song)
        return songs

    async def get_all_songs_previous_7_days(self) -> set[Song]:
        """Get all unique songs played in previous 7 days.

        Returns:
            set[Song]: Set of Songs
        """
        all_songs: list[set[Song]] = await asyncio.gather(
            *(self.get_songs_day(n) for n in range(7))
        )
        # Flatten all sets into one
        return set[Song]().union(*all_songs)
