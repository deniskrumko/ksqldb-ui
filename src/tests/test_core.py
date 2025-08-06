import asyncio

from app.core.fastapi import (
    CacheControlledStaticFiles,
    init_fastapi_app,
)
from app.core.render import (
    RENDER_HELPERS,
    register,
)
from app.core.settings import (
    Server,
    Settings,
    get_server,
    get_server_code,
)
from app.core.templates import get_base_context
from app.core.urls import SimpleURL
from app.core.utils import (
    flatten_dict,
    make_list,
)


def test_init_fastapi_app(init_settings):
    app = init_fastapi_app()
    assert "testing" in app.settings.servers


def test_cache_control_header(tmp_path):
    """Should set Cache-Control header on static file response."""
    static_dir = tmp_path
    (static_dir / "foo.txt").write_text("bar")
    app = CacheControlledStaticFiles(directory=static_dir, max_age=123)
    scope = {"type": "http", "path": "/foo.txt", "method": "GET", "headers": []}
    response = asyncio.run(app.get_response("foo.txt", scope))
    assert response.headers["Cache-Control"] == "public, max-age=123"


def test_register_decorator():
    """Should register a function in RENDER_HELPERS."""

    @register
    def foo(x):
        return x + 1

    assert "foo" in RENDER_HELPERS
    assert RENDER_HELPERS["foo"](2) == 3


def test_get_server(fastapi_request, init_settings):
    assert get_server(fastapi_request).code == "testing"


def test_get_server_code(fastapi_request):
    assert get_server_code(fastapi_request) == "testing"


def test_server_display_name():
    """Should return display_name property correctly."""
    s = Server(code="dev", url="http://dev", name="Development")
    assert s.display_name == "Development"

    s2 = Server(code="prod", url="http://prod")
    assert s2.display_name == "Prod"


def test_settings_from_config():
    settings = Settings.from_config(
        {
            "servers": {
                "a": {"url": "expected"},
            },
        },
    )

    assert settings.servers["a"].url == "expected"
    assert settings.http.timeout == 5
    assert settings.history.enabled


def test_settings_default_server_if_default_exists():
    settings = Settings.from_config(
        {
            "servers": {
                "a": {"url": "url1", "default": False},
                "b": {"url": "url2", "default": True},
                "c": {"url": "url2", "default": False},
            },
        },
    )
    assert settings.default_server.code == "b"


def test_settings_default_server_if_default_undefined():
    settings = Settings.from_config(
        {
            "servers": {
                "a": {"url": "url1", "default": False},
                "b": {"url": "url2", "default": False},
                "c": {"url": "url2", "default": False},
            },
        },
    )
    assert settings.default_server.code == "c"  # last one


def test_get_base_context(fastapi_request, init_settings):
    """Should provide all required keys in base context."""
    ctx = get_base_context(fastapi_request)
    assert ctx["current_server"].code == "testing"
    assert not ctx["warning_message"]
    assert ctx["server_query_param"] == "s"
    assert ctx["q"] == "s=testing"


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


def test_make_list_with_list():
    """Should return the same list if input is already a list."""
    assert make_list([1, 2, 3]) == [1, 2, 3]


def test_make_list_with_scalar():
    """Should wrap a scalar value in a list."""
    assert make_list(42) == [42]
    assert make_list("foo") == ["foo"]


def test_flatten_dict_simple():
    """Should flatten a simple nested dictionary."""
    d = {"a": {"b": 1}}
    assert flatten_dict(d) == {"a.b": 1}


def test_flatten_dict_deep():
    """Should flatten a deeply nested dictionary."""
    d = {"a": {"b": {"c": 2}}}
    assert flatten_dict(d) == {"a.b.c": 2}


def test_flatten_dict_with_sep():
    """Should use custom separator when provided."""
    d = {"a": {"b": 1}}
    assert flatten_dict(d, sep="_") == {"a_b": 1}
