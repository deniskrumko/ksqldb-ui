from app.core.urls import SimpleURL


def test_simpleurl():
    url = SimpleURL("http://example.com/")
    assert url / "path/" / "/file" / "1/" == SimpleURL("http://example.com/path/file/1")


def test_simpleurl_string_representation():
    u = SimpleURL("http://example.com/")
    assert str(u) == "http://example.com/"


def test_simpleurl_eq(sample_url):
    """Test equality comparison for SimpleURL."""
    url = SimpleURL(sample_url)
    assert url == sample_url
    assert url == SimpleURL(sample_url)
