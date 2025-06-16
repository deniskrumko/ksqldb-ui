import json
from contextlib import suppress
from typing import Any

import httpx

CONTEXT_RESPONSE_KEY = "x_response"
CONTEXT_REQUEST_KEY = "x_request"
VERSION_UNDEFINED = "undefined"


def get_version() -> str | None:
    """Get ksqlDB UI version."""
    with suppress(Exception), open(".version", "r") as f:
        if (version := f.read().strip()) != VERSION_UNDEFINED:
            return version
    return None


def make_list(value: Any) -> list:
    """Convert value to list if not already."""
    return [value] if not isinstance(value, list) else value


class ContextResponse:
    def __init__(self, httpx_response: httpx.Response):
        self.data = []
        self.text = ""

        try:
            self.data = make_list(httpx_response.json())
        except json.decoder.JSONDecodeError:
            self.text = httpx_response.text

        self.code = httpx_response.status_code


class ContextRequest:
    def __init__(self, httpx_request: httpx.Request):
        self.data = httpx_request.content.decode("utf-8")
        self.method = httpx_request.method
        self.url = httpx_request.url


def flatten_dict(data: dict, parent_key: str = "", sep: str = ".") -> dict:
    items = {}
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items
