from smart_home.wrappers.online_radio_box.schemas import Song


def test_song():
    result = Song(artist="Abc", title="Wer")
    result2 = Song(artist="AbC", title="WeR")

    assert result.artist == "abc"
    assert result.title == "wer"
    assert result == result2
