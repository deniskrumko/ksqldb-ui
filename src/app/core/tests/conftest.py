import pytest
from fastapi import Request

from app.core.settings import (
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
def fastapi_request():
    return Request(
        scope={
            "type": "http",
            "query_string": b"s=testing",
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
    )


@pytest.fixture
def init_settings(settings):
    return init_global_settings(settings)
