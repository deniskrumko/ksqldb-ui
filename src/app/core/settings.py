import tomllib
from os import getenv
from typing import Optional

from fastapi import Request

from .urls import SimpleURL

SETTINGS: Optional[dict] = None
SERVER_QUERY_PARAM: str = 's'


def get_settings() -> dict:
    global SETTINGS

    if SETTINGS is not None:
        return SETTINGS

    app_config = getenv('APP_CONFIG')
    if not app_config:
        raise ValueError('APP_CONFIG env var is not set')

    with open(app_config, "rb") as f:
        data = tomllib.load(f)

    SETTINGS = data
    return data


def get_server_options(request: Request) -> dict:
    server_name = get_server_name(request)
    if not server_name:
        raise ValueError('Server name is not set')

    settings = get_settings()
    if server_name not in settings['servers']:
        raise ValueError(f'Server "{server_name}" is not found to config file')

    return dict(settings['servers'][server_name])


def get_server_name(request: Request) -> str | None:
    return request.query_params.get(SERVER_QUERY_PARAM)


def get_server_url(request: Request) -> SimpleURL:
    params = get_server_options(request)
    return SimpleURL(params['url'])
