"""Online Radio Box - Schemas."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from smart_home.wrappers.pydantic import to_lower


class Song(BaseModel):
    """
    Song Schema to hold information about a song.

    Args:
        BaseModel (BaseModel): Pydantic Base Model
    """

    artist: Annotated[str, BeforeValidator(to_lower)] = Field(..., min_length=1)
    title: Annotated[str, BeforeValidator(to_lower)] = Field(..., min_length=1)

    def __hash__(self) -> int:
        """Custom Hash function to help with deduplicating.

        Returns:
            int: Hash of Artist and Title
        """
        return hash((self.artist, self.title))

    def __eq__(self, other: object) -> bool:
        """Custom Equal function to help with deduplicating.

        Args:
            other (Song): Incoming Song object

        Returns:
            bool: If it already exists
        """
        return self.__hash__() == other.__hash__()
