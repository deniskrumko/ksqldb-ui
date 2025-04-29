import tomllib
from functools import lru_cache
from os import getenv
from typing import (
    Any,
    Optional,
)

from fastapi import Request

from .urls import SimpleURL

SETTINGS: Optional[dict] = None
SERVER_QUERY_PARAM: str = "s"


def get_settings() -> dict:
    """Get settings from config.toml file."""
    global SETTINGS

    if SETTINGS is not None:
        return SETTINGS

    app_config = getenv("APP_CONFIG")
    if not app_config:
        raise ValueError("APP_CONFIG env var is not set")

    with open(app_config, "rb") as f:
        data = tomllib.load(f)

    SETTINGS = data
    return data


@lru_cache(maxsize=100)
def get_setting(name: str, default_value: Any | None = None) -> Any:
    """Get nested setting value using dot notation (e.g. 'name.subname')."""
    settings = get_settings()
    current: Any = settings

    for part in name.split("."):
        if not isinstance(current, dict):
            return default_value

        current = current.get(part)
        if current is None:
            return default_value

    return current


def get_server_options(request: Request) -> dict:
    """Get current server from request."""
    server_name = get_server(request)
    if not server_name:
        raise ValueError("Server name is not set")

    settings = get_settings()
    if server_name not in settings["servers"]:
        raise ValueError(f'Server "{server_name}" is not found to config file')

    return dict(settings["servers"][server_name])


def get_server(request: Request) -> str | None:
    """Get current server name from request."""
    return request.query_params.get(SERVER_QUERY_PARAM)


def get_server_url(request: Request, default_options: Optional[dict] = None) -> SimpleURL:
    """Get current server url from request."""
    params = default_options or get_server_options(request)
    return SimpleURL(params["url"])


def get_server_display_name(request: Request, default_options: Optional[dict] = None) -> SimpleURL:
    """Get current server display name from request."""
    params = default_options or get_server_options(request)
    return SimpleURL(params.get("name", get_server(request)))
