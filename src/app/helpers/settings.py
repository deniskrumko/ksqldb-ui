import tomllib
from os import getenv
from typing import Optional

from fastapi import Request

from .urls import SimpleURL

SETTINGS: Optional[dict] = None


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


def get_server_params(request: Request) -> dict:
    server = request.query_params['s']
    settings = get_settings()

    if server not in settings['servers']:
        raise ValueError(f'Server "{server}" is not found to config file')

    return dict(settings['servers'][server])


def get_server(request: Request) -> SimpleURL:
    params = get_server_params(request)
    return SimpleURL(params['url'])
