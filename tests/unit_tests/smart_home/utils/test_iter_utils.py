from smart_home.utils import iter_utils


def test_chunk_list():
    original_list = [0, 1, 2, 3, 4, 5, 6]
    result = iter_utils.chunk_list(items=original_list, size=3)

    assert result == [[0, 1, 2], [3, 4, 5], [6]]
