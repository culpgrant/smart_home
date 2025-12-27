"""Helper functions for working with Pydantic."""

from typing import Any


def normalize_empty_string(value: Any) -> Any:
    """
    Handle empty strings to return None within dict or strings.

    Arguments:
        value: Any

    Returns:
        Normalized string
    """
    if value == "":
        return None
    if isinstance(value, dict):
        return {k: normalize_empty_string(v) for k, v in value.items()}
    return value
