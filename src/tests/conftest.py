import pytest
from fastapi import Request

from app.core.settings import (
    GlobalSettings,
    HistorySettings,
    HTTPSettings,
    Server,
    Settings,
    init_settings as init_global_settings,
)


@pytest.fixture
def sample_url():
    """Fixture for a sample URL string."""
    return "http://example.com"


@pytest.fixture
def app(settings):
    class MockApp:
        def __init__(self, settings):
            self.settings = settings

    return MockApp(settings)


@pytest.fixture
def fastapi_request(app):
    return Request(
        scope={
            "type": "http",
            "query_string": b"s=testing",
            "app": app,
            "test": True,
        },
    )


@pytest.fixture
def settings():
    return Settings(
        servers={
            "testing": Server(
                code="testing",
                url="http://testing",
            ),
        },
        http=HTTPSettings(),
        history=HistorySettings(),
        global_settings=GlobalSettings(),
    )


@pytest.fixture
def init_settings(settings):
    return init_global_settings(settings)
