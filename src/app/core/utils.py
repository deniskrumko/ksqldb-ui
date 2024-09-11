import json
from typing import Any

import httpx

CONTEXT_RESPONSE_KEY = 'x_response'
CONTEXT_REQUEST_KEY = 'x_request'


def make_list(value: Any) -> list:
    """Convert value to list if not already."""
    return [value] if not isinstance(value, list) else value


class ContextResponse:
    def __init__(self, httpx_response: httpx.Response):
        self.data = []
        self.text = ''

        try:
            self.data = make_list(httpx_response.json())
        except json.decoder.JSONDecodeError:
            self.text = httpx_response.text

        self.code = httpx_response.status_code


class ContextRequest:
    def __init__(self, httpx_request: httpx.Request):
        self.data = httpx_request.content.decode('utf-8')
        self.method = httpx_request.method
        self.url = httpx_request.url
