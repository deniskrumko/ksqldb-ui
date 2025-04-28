from app.core.urls import SimpleURL


def test_simpleurl():
    url = SimpleURL("http://example.com/")
    assert url / "path/" / "/file" / "1/" == SimpleURL("http://example.com/path/file/1")


def test_simpleurl_string_representation():
    u = SimpleURL("http://example.com/")
    assert str(u) == "http://example.com/"
