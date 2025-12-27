from typing import Any

import pytest

from smart_home.wrappers.pydantic import pydantic


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("asdf", "asdf"),
        ("", None),
        ({"a": "asdf", "b": ""}, {"a": "asdf", "b": None})
    ],
)
def test_normalize_empty_string(value: Any, expected: Any):
    assert pydantic.normalize_empty_string(value) == expected
