"""Itertation Utilities."""

from typing import Any


def chunk_list(items: list[Any], size: int = 100) -> list[list[Any]]:
    """Chunk list into a specific size.

    Args:
        items (list[Any]): List of items
        size (int, optional): Number of items that should be in each list.
            Defaults to 100.

    Returns:
        list[list[Any]]: List of chunked lists
    """
    return [items[i : i + size] for i in range(0, len(items), size)]
