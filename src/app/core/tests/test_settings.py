from app.core.settings import (
    Server,
    Settings,
    get_server,
    get_server_code,
)


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
